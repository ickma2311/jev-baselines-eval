"""Run the frozen B1 item set against the two open replicas, on Modal.

Two entry points, deliberately separate so the first thing we pay for is small:

    modal run code/modal_replicas_b0.py::probe   # loads both models, 2 items each
    modal run code/modal_replicas_b0.py::run     # the full 200 items per model

Per PREREG_B0.md section 4, each system is called through the interface its own
README recommends, and a replica that cannot express an 8-way choice natively is
recorded NOT-APPLICABLE rather than driven through an interface we invented.

  decider-2b  exposes `system_one(state, questions)`, which takes the same state
              dict and criteria object we send Jev, so it is used as-is.
  kotoba      exposes `decide(text, questions)` and takes a plain string, not a
              state dict. The ticket is therefore serialized to text by
              `state_to_text` below. That serialization is identical across all
              four arms, so it cannot affect the arm contrast that the primary
              endpoint measures; it is recorded in every output row.

Every function sets a timeout so a hung load cannot bill indefinitely.
"""

import json
import pathlib

import modal

APP = modal.App("open-jev-b1")
ROOT = pathlib.Path(__file__).resolve().parent.parent

KOTOBA_REPO = "com-kotobalabs/open-jev-deberta-v3-large"
KOTOBA_REV = "19bf9a64815add579fbf6c907bef584d9277a8e4"
DECIDER_REPO = "Mapika/decider-2b"
DECIDER_REV = "fa996cea58e1c1d8d1ab4d7124154f303b017f95"

# The two replicas cannot share an environment: decider-ai requires
# transformers>=5 while typed-decisions requires >=4.56,<5. pip cannot resolve
# both, so each replica gets its own image on top of a shared base, and neither
# transformers version is pinned by us — each package resolves its own.
# torch is deliberately NOT pinned or pre-installed here. Both packages declare
# their own torch requirement (decider-ai: "torch"; typed-decisions: "torch>=2.4")
# and pinning torch==2.5.1 broke decider at inference: transformers 5.x calls
# torch.compiler.is_exporting() inside a compiled region, which 2.5.1 lacks.
# Letting each package resolve its own stack is both faithful and correct.
base = (
    # typed-decisions declares requires-python >= 3.12; 3.11 fails to install.
    modal.Image.debian_slim(python_version="3.12")
    # Both replicas ship as GitHub repos rather than PyPI packages, and
    # debian_slim has no git.
    .apt_install("git")
)

# add_local_file must be the last step of each image: Modal refuses a build
# step after it, and keeping it last means a change to the item set does not
# rebuild the torch layer.
ITEMS = ("/items_b1.jsonl", ROOT / "data" / "items_b1.jsonl")
decider_image = (
    base.pip_install("git+https://github.com/Mapika/decider")
    .add_local_file(ITEMS[1], ITEMS[0])
)
kotoba_image = (
    base.pip_install("git+https://github.com/kotoba-lang/typed-decisions")
    .add_local_file(ITEMS[1], ITEMS[0])
)

# Weights are cached between runs so a re-run does not re-download 4.4 GB.
cache = modal.Volume.from_name("open-jev-hf-cache", create_if_missing=True)
# L4, not T4: decider defaults to bfloat16 on CUDA and T4 (sm75) has no bfloat16.
# Forcing fp16 would mean running the model at a precision its README does not
# specify, so the GPU is changed instead of the model's own default. Logged in
# prereg/DEVIATIONS_B0.md.
GPU = "L4"
TIMEOUT = 30 * 60


def state_to_text(state):
    """Deterministic plain-text rendering of a ticket state.

    Only used for replicas whose native interface takes a string. Identical
    across arms by construction: the only thing that differs between arms is
    the body, which is what the experiment varies.
    """
    sender = state.get("from", {})
    return (
        f"From: {sender.get('name', '')} <{sender.get('email', '')}>\n"
        f"Received: {state.get('received', '')}\n"
        f"Channel: {state.get('channel', '')}\n"
        f"Subject: {state.get('subject', '')}\n\n"
        f"{state.get('body', '')}"
    )


def load_items(limit_per_arm=None):
    items = [json.loads(line) for line in open("/items_b1.jsonl")]
    if limit_per_arm:
        seen = {}
        kept = []
        for it in items:
            n = seen.get(it["arm"], 0)
            if n < limit_per_arm:
                kept.append(it)
                seen[it["arm"]] = n + 1
        return kept
    return items


def _row(item, system, predicted, probabilities, confidence, extra=None):
    row = {
        "item_id": item["item_id"],
        "arm": item["arm"],
        "base_index": item["base_index"],
        "system": system,
        "predicted": predicted,
        "confidence": confidence,
        "probabilities": probabilities,
        "true_department": item["true_department"],
        "injection_target": item["injection_target"],
    }
    if extra:
        row.update(extra)
    return row


@APP.function(image=decider_image, gpu=GPU, volumes={"/cache": cache}, timeout=TIMEOUT)
def run_decider(limit_per_arm=None):
    """decider-2b through its own Jev-shaped `system_one` interface."""
    import os
    import time

    os.environ["HF_HOME"] = "/cache/hf"
    from decider.infer import Decider
    from huggingface_hub import snapshot_download

    # Decider() takes a path, not a revision, so the pinned revision is
    # materialized first and the local directory is handed over.
    path = snapshot_download(DECIDER_REPO, revision=DECIDER_REV)
    t0 = time.time()
    d = Decider(path)
    print(f"[progress] decider loaded in {time.time() - t0:.1f}s", flush=True)

    items = load_items(limit_per_arm)
    rows = []
    started = time.time()
    for n, item in enumerate(items, 1):
        questions = {
            "q_route": {
                "type": "choice",
                "instructions": item["question"],
                "criteria": {o["id"]: o["label"] for o in item["options"]},
            }
        }
        call_started = time.time()
        resp = d.system_one(item["state"], questions)
        answer = resp["answers"]["q_route"]
        rows.append(_row(
            item, "decider_2b", answer["choice"], answer.get("probabilities"),
            answer.get("confidence"),
            {"model_version": resp.get("model"),
             "latency_s": round(time.time() - call_started, 3),
             "interface": "system_one(state, questions)"},
        ))
        if n % 20 == 0 or n == len(items):
            rate = (time.time() - started) / n
            print(f"[progress] decider {n}/{len(items)} {rate:.2f}s/item "
                  f"eta {rate * (len(items) - n):.0f}s", flush=True)
    cache.commit()
    return rows


@APP.function(image=kotoba_image, gpu=GPU, volumes={"/cache": cache}, timeout=TIMEOUT)
def run_kotoba(limit_per_arm=None):
    """kotoba's encoder through its own `decide(text, questions)` interface."""
    import os
    import time

    os.environ["HF_HOME"] = "/cache/hf"
    from typed_decisions.open_jev import OpenJev

    t0 = time.time()
    m = OpenJev.from_pretrained(KOTOBA_REPO, revision=KOTOBA_REV)
    max_state_tokens = m.config.get("max_state_tokens", 256)
    print(f"[progress] kotoba loaded in {time.time() - t0:.1f}s, "
          f"max_state_tokens={max_state_tokens}", flush=True)

    items = load_items(limit_per_arm)
    rows = []
    started = time.time()
    for n, item in enumerate(items, 1):
        # This interface takes option labels, not ids; map the answer back.
        label_to_id = {o["label"]: o["id"] for o in item["options"]}
        labels = [o["label"] for o in item["options"]]
        call_started = time.time()
        text = state_to_text(item["state"])
        # The injected paragraph sits near the end of the ticket, so silent
        # truncation would delete the treatment and show a spurious zero lift.
        # Measure it per item instead of trusting the length estimate.
        n_tokens = len(m.tok(text, add_special_tokens=False)["input_ids"])
        truncated = n_tokens > max_state_tokens
        out = m.decide(
            text,
            [{"type": "choice", "instructions": item["question"], "options": labels}],
        )[0]
        probs = {label_to_id.get(k, k): v for k, v in (out.get("probabilities") or {}).items()}
        rows.append(_row(
            item, "kotoba_deberta", label_to_id.get(out["choice"], out["choice"]),
            probs, out.get("confidence"),
            {"latency_s": round(time.time() - call_started, 3),
             "state_tokens": n_tokens,
             "state_truncated": truncated,
             "interface": "decide(text, questions); state rendered by state_to_text"},
        ))
        if n % 20 == 0 or n == len(items):
            rate = (time.time() - started) / n
            print(f"[progress] kotoba {n}/{len(items)} {rate:.2f}s/item "
                  f"eta {rate * (len(items) - n):.0f}s", flush=True)
    n_trunc = sum(1 for r in rows if r["state_truncated"])
    print(f"[progress] kotoba truncated {n_trunc}/{len(rows)} states", flush=True)
    cache.commit()
    return rows


def _write(name, rows):
    out = ROOT / "results" / f"b1_{name}.jsonl"
    out.parent.mkdir(exist_ok=True)
    with out.open("w") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"wrote {out} ({len(rows)} rows)")


@APP.local_entrypoint()
def probe():
    """Cheapest possible first contact: both models, 2 items per arm."""
    for name, fn in (("decider_2b", run_decider), ("kotoba_deberta", run_kotoba)):
        rows = fn.remote(limit_per_arm=2)
        print(f"\n{name}: {len(rows)} rows")
        for r in rows:
            print(f"  {r['item_id']:<18} pred={r['predicted']:<14} "
                  f"truth={r['true_department']:<10} target={r['injection_target']:<8} "
                  f"conf={r['confidence']}")
        _write(f"probe_{name}", rows)


@APP.local_entrypoint()
def run():
    """The full frozen set: 200 items per model."""
    for name, fn in (("decider_2b", run_decider), ("kotoba_deberta", run_kotoba)):
        rows = fn.remote()
        _write(name, rows)
