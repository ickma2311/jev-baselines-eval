# Round 3 — external review after the round-2 fix (gpt-6-sol, reasoning effort xhigh, Codex CLI)

All figures below are **my independent recomputations** from the three [raw result files](../results/b1_jev.jsonl) ([decider](../results/b1_decider_2b.jsonl), [kotoba](../results/b1_kotoba_deberta.jsonl)) joined to the [frozen items](../data/items_b1.jsonl). I did not use `analyze_b1.py` to calculate them.

| System | Pair-weighted | Equal-weighted | Rows with no within-department comparison |
|---|---:|---:|---:|
| Jev | **0.329** | **0.228** | 0 / 300 |
| decider-2b | **0.493** | **0.417** | **74 / 300** |
| kotoba | **0.497** | **0.561** | 0 / 300 |

I also reproduced Jev’s exploratory pair-weighted interval **[0.251, 0.412]** using 5,000 bootstrap resamples within each department and outcome class.

**The two-weighting presentation is sound, but its conclusion needs one wording fix.** Equal weighting is a coherent description of a uniformly chosen *estimable* department. For decider, that means only six departments; the same 74 rows are absent from **both** within-department estimates. It is not an estimate covering all 300 rows. My additional equal-weighted bootstrap intervals exclude 0.5 for decider **[0.348, 0.483]** and kotoba **[0.501, 0.623]**, but these exploratory results depend on the chosen weighting and sparse departments. Kotoba’s equal estimate falls from **0.561 to 0.498** if its department with just one hijacked row is omitted. Calling the overall department-adjusted reading *inconclusive* is therefore appropriate, not an underclaim.

As a third check, my department-stratified conditional logistic fit gives hijack odds ratios per 0.1 higher confidence of **1.58 [1.23, 2.06]** for Jev, **0.98 [0.79, 1.21]** for decider, and **1.17 [0.99, 1.39]** for kotoba. It supports Jev’s within-department association but requires a common-slope assumption and cannot recover decider’s single-class departments. A Mantel–Haenszel analysis would require choosing a confidence cutoff. Neither supplies a design-free answer that changes the cautious conclusion.

**Jev’s surviving claim is at the right strength** in the main interpretation: an inverse confidence ranking within this authority arm, persisting under the reported exploratory controls, without a causal mechanism or deployment verdict. I found no further numerical defect. One stale sentence remains: [lines 42–44](../results/history/RESULTS_B1.v3.md:42) say department mix *explains* decider’s and kotoba’s marginal results “not by hijacking,” contradicting the later, correct “compatible with” caveat. The [section heading](../results/history/RESULTS_B1.v3.md:62) also implies decider fails every department control, though its equal-weighted estimate remains inverted.

**FIX FIRST — replace that department-control framing with: Jev’s inversion is robust to both reported weightings; decider’s and kotoba’s adjusted readings depend on the weighting, so department mix remains a possible explanation. Then stop the review cycle.**


