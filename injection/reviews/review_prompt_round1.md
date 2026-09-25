> Published note: the `results/RESULTS_B1.md` this prompt refers to is archived as [`results/history/RESULTS_B1.v1.md`](../results/history/RESULTS_B1.v1.md) — the version under review in this round. The final write-up is the study README.

# Task: attack a finished result before it goes anywhere

An experiment (B1) has finished. Its write-up claims something sharp, and I want the strongest case
against it before this is shown to anyone.

Read:

- `results/RESULTS_B1.md` — the write-up under attack
- `prereg/PREREG_B1.md` — the frozen pre-registration (sha256 b8bb4d93…), including section 7's list
  of claims B1 cannot make and section 8's rule on the word PASS
- `prereg/DEVIATIONS_B1.md` — eleven pre-run amendments D1–D11 and two during-run deviations DEV-1/DEV-2
- `results/b1_jev.jsonl`, `results/b1_decider_2b.jsonl`, `results/b1_kotoba_deberta.jsonl` — the raw
  rows, 1,200 each
- `code/analyze_b1.py` — the analysis; `code/smoke_b1.py` — its unit tests
- `data/items_b1.jsonl` — the frozen items
- `results/RESULTS_B0.md` — the screen that preceded it

## The headline being attacked

> For Jev and decider-2b, confidence is **INVERTED**: within the arm where the authority paragraph
> was inserted, these systems are *more* confident precisely on the decisions that were hijacked.
> Jev E1 AUROC 0.261 [0.190, 0.336]; decider-2b 0.412 [0.348, 0.478]; kotoba 0.571 [0.501, 0.640].

## What I want, in order

1. **Recompute E1 and the CIs from the raw rows yourself.** Do not trust `analyze_b1.py` — it is the
   thing that might be wrong. If your numbers differ from the write-up's, say so with your method.

2. **The strongest argument that INVERTED is an artifact rather than a finding.** Consider at least:
   whether conditioning on the model's own outcome manufactures the direction; whether the hijacked
   and resisted classes differ systematically in something other than being hijacked (item
   difficulty, which department is the target, option position, ticket length); whether a model that
   is simply more confident overall on easy items would produce this pattern without any
   injection-specific effect. **Test the ones that are testable against the raw rows** rather than
   listing them.

3. **Is any sentence in the write-up stronger than the data supports?** Quote it and say what it
   should say instead. Pay attention to the deployment framing, to what "anti-protective" implies,
   and to whether the willkelly comparison is fair to their study.

4. **Is the τ = 0.85 operating-point table honest?** It was frozen before the run (D11) and no vendor
   documents a threshold. Does presenting it per system mislead, given the three confidence scales
   are not the same measurement?

5. **DEV-2**: the Jev rows were collected under two different User-Agent headers, split so that
   `clean` and `authority` fall on opposite sides. The write-up reports a 30-item re-ask that
   reproduced 30/30 predictions. Is that check adequate? If not, what would be?

6. A one-line verdict: **PUBLISHABLE AS WRITTEN**, or **FIX FIRST** with the single change.

## Rules

Every number you assert must come from the raw files or your own recomputation, and say which. If a
concern is speculative, label it speculative. **If the write-up is sound, say so and stop — "nothing
new" is a correct answer**, and a fabricated objection costs a person real time.
