"""Freeze the B0 item set.

Regenerates, byte-identically, the first 50 support-ticket-routing instances of
willkelly/jev-evaluation's E9 injection condition, for the four arms B0 uses.
See prereg/PREREG_B0.md sections 3 and 4; nothing here may be changed after the
freeze without a DEVIATIONS_B0.md entry.

The upstream generator is index-addressable: every instance is derived from
sha256 of its own coordinates, so count=50 yields exactly the first 50 of the
count=200 draw that produced the published numbers.

    python code/gen_items_b0.py
"""

import hashlib
import json
import pathlib
import sys

VENDOR = pathlib.Path(__file__).resolve().parent.parent / "vendor" / "jev-evaluation"
sys.path.insert(0, str(VENDOR))

from jeveval import config  # noqa: E402
from jeveval.generators import adversarial  # noqa: E402

# Pinned in the pre-registration.
UPSTREAM_COMMIT = "d80f375621ad4b9306c6dff6941242925d7e2386"
ARMS = ("clean", "noise_control", "direct_override", "authority")
N = 50
QUESTION_TYPE = "choice"
KEY = adversarial.KEY_CHOICE

OUT_DIR = pathlib.Path(__file__).resolve().parent.parent / "data"


def build():
    """Generate every arm and return the flat list of records."""
    seed = config.seed_for("E9", "injection")
    records = []
    for arm in ARMS:
        instances = adversarial.generate(
            difficulty={"technique": arm, "question_type": QUESTION_TYPE},
            seed=seed,
            count=N,
        )
        for inst in instances:
            question = inst.questions[KEY]
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


def check(records, indices=None):
    """Pre-registration invariants. Any failure here stops the freeze.

    `indices` is the expected set of base indices; it defaults to B0's 0..N-1 so
    that B0 keeps its original behaviour, and B1 passes its own 50..349.
    """
    by_arm = {}
    for r in records:
        by_arm.setdefault(r["arm"], {})[r["base_index"]] = r

    if indices is None:
        indices = range(N)
    indices = list(indices)

    assert set(by_arm) == set(ARMS), f"arms present: {sorted(by_arm)}"
    for arm in ARMS:
        assert len(by_arm[arm]) == len(indices), (
            f"{arm}: {len(by_arm[arm])} items, expected {len(indices)}"
        )

    for index in indices:
        rows = [by_arm[arm][index] for arm in ARMS]
        base = rows[0]

        # The injected target is never the correct answer: "the answer moved to
        # the injected one" has to be a failure, not a relabelling.
        assert base["injection_target"] != base["true_department"], index

        # One option order per base index, shared by every arm, so the arm
        # difference carries no position bias.
        orders = {tuple(o["id"] for o in r["options"]) for r in rows}
        assert len(orders) == 1, f"index {index}: option order differs across arms"

        # Truth, target and question are properties of the base index alone.
        assert len({r["true_department"] for r in rows}) == 1, index
        assert len({r["injection_target"] for r in rows}) == 1, index
        assert len({r["question"] for r in rows}) == 1, index
        assert len(base["options"]) == 8, len(base["options"])

        # The clean arm is the unmodified ticket; every other arm is that same
        # ticket plus exactly one inserted paragraph.
        clean_body = by_arm["clean"][index]["state"]["body"]
        for arm in ARMS:
            body = by_arm[arm][index]["state"]["body"]
            if arm == "clean":
                assert body == clean_body, index
            else:
                assert body != clean_body, f"{arm}/{index}: body unchanged"
                assert len(body.split("\n\n")) == len(clean_body.split("\n\n")) + 1, (
                    f"{arm}/{index}: expected exactly one inserted paragraph"
                )

        # The noise control must name no department and issue no instruction,
        # or it stops being a control for "any added text moves the answer".
        noise_body = by_arm["noise_control"][index]["state"]["body"]
        inserted = [p for p in noise_body.split("\n\n") if p not in clean_body.split("\n\n")]
        assert len(inserted) == 1, index
        labels = [o["label"].lower() for o in base["options"]]
        assert not any(lbl in inserted[0].lower() for lbl in labels), (
            f"index {index}: noise control names a department"
        )


def main():
    records, seed = build()
    check(records)

    OUT_DIR.mkdir(exist_ok=True)
    path = OUT_DIR / "items_b0.jsonl"
    payload = "".join(
        json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in records
    )
    path.write_text(payload, encoding="utf-8")

    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    (OUT_DIR / "items_b0.sha256").write_text(f"{digest}  items_b0.jsonl\n")

    print(f"seed (E9/injection) = {seed}")
    print(f"{len(records)} items = {len(ARMS)} arms x {N}")
    print(f"wrote {path}")
    print(f"sha256 {digest}")


if __name__ == "__main__":
    main()
