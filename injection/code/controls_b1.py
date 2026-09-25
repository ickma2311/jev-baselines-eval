"""EXPLORATORY stratified controls for Jev's E1 in B1 (README, "The department control").

E1 is the AUROC of confidence for resisted (positive) vs hijacked (negative) decisions in the
`authority` arm. Each control recomputes it within strata and combines strata pair-weighted
(each stratum weighted by its resisted x hijacked pairs; one-class strata contribute nothing):

  target    -- the injected target department
  position  -- the target's option position (0-7) in the presented option list
  department -- gold department, combined both pair-weighted and equal-weighted (mean of the
               per-department AUROCs that are estimable), plus the equal-weighted figure after
               dropping departments whose smaller outcome class has a single row
  length    -- quartile of ticket length, where length is the word count of the ticket body in
               the item's `clean` arm (the same ticket without the inserted paragraph), and
               quartiles are an equal-size split of the 300 items by stable rank

The length definition was written down after the fact (see README); `--all-lengths` prints the
same control under several other reasonable length definitions for comparison.

Not computed here (separate calculations, not included in this package): the bootstrap interval on
the pair-weighted department figure, the permutation check, and the conditional logistic model.

Usage: python code/controls_b1.py [--system jev|decider_2b|kotoba_deberta] [--all-lengths]
"""
import argparse
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent


def auc_pairs(pos, neg):
    s = sum((p > n) + 0.5 * (p == n) for p in pos for n in neg)
    return s / (len(pos) * len(neg)), len(pos) * len(neg)


def pair_weighted(rows, labels):
    groups = {}
    for r, k in zip(rows, labels):
        groups.setdefault(k, []).append(r)
    num = den = 0.0
    for members in groups.values():
        pos = [r["confidence"] for r in members if not r["hijacked"]]
        neg = [r["confidence"] for r in members if r["hijacked"]]
        if pos and neg:
            a, w = auc_pairs(pos, neg)
            num += a * w
            den += w
    return num / den


def department_control(rows):
    groups = {}
    for r in rows:
        groups.setdefault(r["true_department"], []).append(r)
    num = den = 0.0
    per_dept = []
    unmatched = 0
    for members in groups.values():
        pos = [r["confidence"] for r in members if not r["hijacked"]]
        neg = [r["confidence"] for r in members if r["hijacked"]]
        if not (pos and neg):
            unmatched += len(members)
            continue
        a, w = auc_pairs(pos, neg)
        num += a * w
        den += w
        per_dept.append((a, min(len(pos), len(neg))))
    equal = float(np.mean([a for a, _ in per_dept]))
    equal_no_sparse = float(np.mean([a for a, m in per_dept if m > 1]))
    return num / den, equal, equal_no_sparse, unmatched


def rank_quartile(values):
    v = np.asarray(values)
    ranks = np.argsort(np.argsort(v, kind="stable"), kind="stable")
    return ranks * 4 // len(v)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--system", default="jev")
    ap.add_argument("--all-lengths", action="store_true")
    args = ap.parse_args()

    items = {}
    for line in open(ROOT / "data" / "items_b1.jsonl"):
        it = json.loads(line)
        items[it["item_id"]] = it
    clean = {it["base_index"]: it for it in items.values() if it["arm"] == "clean"}

    rows = []
    for line in open(ROOT / "results" / f"b1_{args.system}.jsonl"):
        r = json.loads(line)
        if r["arm"] != "authority":
            continue
        it = items[r["item_id"]]
        r["hijacked"] = r["predicted"] == r["injection_target"]
        r["position"] = [o["id"] for o in it["options"]].index(r["injection_target"])
        r["item"] = it
        r["clean_body"] = clean[it["base_index"]]["state"]["body"]
        rows.append(r)

    marginal = pair_weighted(rows, [0] * len(rows))
    print(f"system {args.system}: n={len(rows)} authority rows, "
          f"{sum(not r['hijacked'] for r in rows)} resisted / {sum(r['hijacked'] for r in rows)} hijacked")
    print(f"  marginal E1                    {marginal:.3f}")
    print(f"  within injected target         {pair_weighted(rows, [r['injection_target'] for r in rows]):.3f}")
    print(f"  within target option position  {pair_weighted(rows, [r['position'] for r in rows]):.3f}")
    pw, eq, eq_ns, unmatched = department_control(rows)
    print(f"  within gold department, pair-weighted   {pw:.3f}  (rows with no within-department comparison: {unmatched}/{len(rows)})")
    print(f"  within gold department, equal-weighted  {eq:.3f}")
    print(f"    ... dropping single-row minority classes {eq_ns:.3f}")
    words = [len(r["clean_body"].split()) for r in rows]
    print(f"  within ticket-length quartile  {pair_weighted(rows, rank_quartile(words)):.3f}")

    if args.all_lengths:
        alt = {
            "clean body, characters": [len(r["clean_body"]) for r in rows],
            "injected body, words": [len(r["item"]["state"]["body"].split()) for r in rows],
            "injected body, characters": [len(r["item"]["state"]["body"]) for r in rows],
            "clean state as JSON, characters": [len(json.dumps(clean[r["item"]["base_index"]]["state"])) for r in rows],
            "API input tokens (injected)": [r["usage"]["input_tokens"] for r in rows if "usage" in r],
        }
        print("  length quartile under other definitions:")
        for name, vals in alt.items():
            if len(vals) != len(rows):
                print(f"    {name:34s} n/a (field missing for this system)")
                continue
            print(f"    {name:34s} {pair_weighted(rows, rank_quartile(vals)):.3f}")


if __name__ == "__main__":
    main()
