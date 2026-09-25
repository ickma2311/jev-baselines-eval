"""Run the B0 item set against Jev (the harness-validation arm).

Uses the upstream project's own wire encoder so the request body is byte-for-byte
the shape that produced willkelly's published numbers. If we built the body
ourselves and got a detail wrong, the section 4.1 check would be comparing our
harness against their harness rather than validating ours.

Resumable: already-answered items are skipped, so an interrupted run costs
nothing to restart.

    python code/run_jev_b0.py            # all 200 items
    python code/run_jev_b0.py --limit 2  # smoke: 2 calls, ~$0.00003
"""

import argparse
import json
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "vendor" / "jev-evaluation"))
sys.path.insert(0, str(ROOT / "code"))

from jeveval import wire  # noqa: E402

from jev_client import ask  # noqa: E402

KEY = "q_route"
MODEL = "jev-latest"
RESULTS = ROOT / "results"


def load_items():
    path = ROOT / "data" / "items_b0.jsonl"
    return [json.loads(line) for line in path.open()]


def build_questions(item):
    """The neutral question dict the upstream wire encoder expects."""
    return {KEY: {"type": "choice", "question": item["question"], "options": item["options"]}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None, help="only the first N items")
    ap.add_argument("--dry-run", action="store_true", help="print one body, call nothing")
    ap.add_argument("--item-ids", nargs="+", help="only these item_ids, e.g. clean/000")
    ap.add_argument("--out", default="b0_jev.jsonl", help="results filename")
    args = ap.parse_args()

    items = load_items()
    if args.item_ids:
        wanted = set(args.item_ids)
        items = [i for i in items if i["item_id"] in wanted]
    if args.limit:
        items = items[: args.limit]

    if args.dry_run:
        body = wire.build_request(state=items[0]["state"], questions=build_questions(items[0]), model=MODEL)
        print(json.dumps(body, indent=2, ensure_ascii=False)[:1200])
        return 0

    RESULTS.mkdir(exist_ok=True)
    out_path = RESULTS / args.out
    done = set()
    if out_path.exists():
        for line in out_path.open():
            done.add(json.loads(line)["item_id"])

    todo = [i for i in items if i["item_id"] not in done]
    print(f"[progress] {len(done)} done, {len(todo)} to go", flush=True)

    started = time.time()
    with out_path.open("a") as fh:
        for n, item in enumerate(todo, 1):
            questions = build_questions(item)
            body = wire.build_request(state=item["state"], questions=questions, model=MODEL)
            resp, secs = ask(body["state"], body["questions"], model=MODEL)
            answer = resp["answers"][KEY]
            fh.write(json.dumps({
                "item_id": item["item_id"],
                "arm": item["arm"],
                "base_index": item["base_index"],
                "system": "jev",
                "model_version": resp.get("model"),
                "predicted": answer["choice"],
                "confidence": answer.get("confidence"),
                "probabilities": answer.get("probabilities"),
                "true_department": item["true_department"],
                "injection_target": item["injection_target"],
                "latency_s": round(secs, 3),
                "usage": resp.get("usage"),
            }, ensure_ascii=False) + "\n")
            fh.flush()
            if n % 10 == 0 or n == len(todo):
                rate = (time.time() - started) / n
                print(f"[progress] {n}/{len(todo)}  {rate:.2f}s/item  "
                      f"eta {rate * (len(todo) - n):.0f}s", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
