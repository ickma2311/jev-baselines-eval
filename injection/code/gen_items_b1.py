"""Freeze the B1 item set: base indices 50-349, disjoint from B0's 0-49.

Same upstream generator, same seed, same four arms as B0 (PREREG_B1.md section 5).
The generator is index-addressable, so generating 350 and dropping the first 50
yields exactly the indices B0 did not use. Indices above 199 were never run
upstream either, so most of this set is fresh to everyone.

    python code/gen_items_b1.py
"""

import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "vendor" / "jev-evaluation"))
sys.path.insert(0, str(ROOT / "code"))

from jeveval import config  # noqa: E402
from jeveval.generators import adversarial  # noqa: E402

from gen_items_b0 import ARMS, QUESTION_TYPE, UPSTREAM_COMMIT, check  # noqa: E402

START = 50          # B0 used 0-49
COUNT = 300         # -> 50..349
OUT_DIR = ROOT / "data"


def build():
    seed = config.seed_for("E9", "injection")
    records = []
    for arm in ARMS:
        instances = adversarial.generate(
            difficulty={"technique": arm, "question_type": QUESTION_TYPE},
            seed=seed,
            count=START + COUNT,
        )[START:]
        for inst in instances:
            question = inst.questions[adversarial.KEY_CHOICE]
            records.append(
                {
                    "item_id": f"{arm}/{inst.index:03d}",
                    "arm": arm,
                    "base_index": inst.index,
                    "seed": seed,
                    "upstream_commit": UPSTREAM_COMMIT,
                    "state": inst.state,
                    "question": question["question"],
                    "options": question["options"],
                    "true_department": inst.meta["true_department"],
                    "injection_target": inst.meta["injection_target"],
                }
            )
    return records, seed


def main():
    records, seed = build()

    indices = {r["base_index"] for r in records}
    assert indices == set(range(START, START + COUNT)), "wrong index range"

    # The B0 set must not leak into the confirmatory set.
    b0 = ROOT / "data" / "items_b0.jsonl"
    if b0.exists():
        b0_indices = {json.loads(line)["base_index"] for line in b0.open()}
        overlap = indices & b0_indices
        assert not overlap, f"B1 overlaps B0 on {sorted(overlap)[:5]}"

    check(records, indices)  # the same pre-registered invariants B0 enforced

    path = OUT_DIR / "items_b1.jsonl"
    payload = "".join(
        json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in records
    )
    path.write_text(payload, encoding="utf-8")
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    (OUT_DIR / "items_b1.sha256").write_text(f"{digest}  items_b1.jsonl\n")

    print(f"seed (E9/injection) = {seed}")
    print(f"{len(records)} items = {len(ARMS)} arms x {COUNT}, base indices "
          f"{START}..{START + COUNT - 1}")
    print(f"disjoint from B0: yes")
    print(f"wrote {path}")
    print(f"sha256 {digest}")


if __name__ == "__main__":
    main()
