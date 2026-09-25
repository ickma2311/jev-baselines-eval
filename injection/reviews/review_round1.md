# Round 1 — external review of the first version (gpt-6-sol, reasoning effort xhigh, Codex CLI)

## 1. Independent recomputation

I joined each raw result row to the frozen item by arm and base index, then calculated E1 with a Mann–Whitney rank statistic, counting ties as half. I independently drew the preregistered stratified bootstrap intervals using the frozen seed and resample count. The three result files have complete, unique rows; their item metadata matches the frozen items. The Jev harness bounds and kotoba truncation check also pass on the raw rows.

| System | Not targeted / targeted | E1 AUROC | 95% CI |
|---|---:|---:|---:|
| Jev | 53 / 247 | **0.261** | **[0.190, 0.336]** |
| decider-2b | 129 / 171 | **0.412** | **[0.348, 0.478]** |
| kotoba | 197 / 103 | **0.571** | **[0.501, 0.640]** |

These match the write-up to its reported precision. All counts and estimates in this review are my recomputations from the [Jev rows](../results/b1_jev.jsonl), [decider rows](../results/b1_decider_2b.jsonl), [kotoba rows](../results/b1_kotoba_deberta.jsonl), and [frozen items](../data/items_b1.jsonl), unless explicitly identified as a claim in a document.

## 2. Strongest artifact case

**The marginal E1 result is real, but decider’s causal-sounding interpretation is fragile.** E1 groups items by the model’s own choice and scores that same choice’s confidence. That definition does not mathematically force inversion; it also cannot show that *being hijacked caused* higher confidence. Department-specific choice and confidence behavior can create the marginal association.

I recomputed exploratory AUCs using only comparisons within the same item characteristic. The “clean counterpart” column instead scores the paired item’s clean-arm confidence, with higher scores favoring items that later resisted.

| System | Same gold department, with exploratory CI | Same target | Same target position | Same ticket-length quartile | Clean counterpart |
|---|---:|---:|---:|---:|---:|
| Jev | **0.329 [0.251, 0.412]** | 0.263 | 0.257 | 0.248 | 0.575 |
| decider-2b | **0.493 [0.412, 0.574]** | 0.395 | 0.400 | 0.403 | 0.779 |
| kotoba | **0.497 [0.428, 0.567]** | 0.679 | 0.554 | 0.574 | 0.810 |

For decider, gold department is the sharpest alternative explanation: all 37 billing-gold items resisted, while all 37 sales-gold items were targeted. A permutation that preserves each gold department’s class counts and confidence scores, but removes any within-department association, yields a marginal AUC centered at **0.426** with a **[0.382, 0.469]** permutation range. The observed **0.412** fits that explanation. This does **not** invalidate its preregistered marginal `INVERTED` label; it does undermine “more confident *precisely because* hijacked.”

Jev is different. Its inversion persists within gold departments, targets, option positions, and length groups. A simple “the model is confident on easy items” account also fails for both systems: on the paired *clean* items, confidence favors those that later resist, especially for decider. The exploratory controls therefore give a strong artifact case against **decider’s interpretation**, not against Jev’s observed within-arm ranking. They do not establish Jev’s mechanism.

## 3. Sentences to fix

- “[A] confidence gate does not protect against the authority framing, and for two of them it is anti-protective” in [RESULTS_B1.md](../results/history/RESULTS_B1.v1.md:51) exceeds E1 and conflicts with [D5/D11](../prereg/DEVIATIONS_B1.md:48), which explicitly withhold a deployed-gate verdict. At the frozen threshold, the gate **rejected 171/247 Jev and 60/171 decider targeted decisions**. A supported replacement is: “On these authority-arm items, higher confidence ranks targeted decisions above non-targeted decisions for Jev and, marginally, decider; the operating-point counts describe one hypothetical threshold and do not establish deployment utility.”

- “This also settles, for Jev, the question willkelly’s study left open” ([line 56](../results/history/RESULTS_B1.v1.md:56)) is unfair. [Will Kelly’s study](https://github.com/willkelly/jev-evaluation) already discussed both confidence under successful versus failed authority attacks **and** an operating gate. B1 adds a preregistered within-authority rank statistic on new items; it does not supersede that study’s operational finding.

- “The header does not move the model” ([line 83](../results/history/RESULTS_B1.v1.md:83)) is stronger than the reported re-ask supports. Say: “The reported clean-item re-ask found unchanged choices in its sampled items; equivalence of confidence scores and cross-arm gate rates remains unestablished.” The re-ask records are not in the supplied raw files, so I could not independently verify its reported result.

The report also needs the exact trust-boundary statement promised by D6. D9 requires explaining that “not targeted” need not mean correct: **18 kotoba authority rows** are wrong in another direction. Those omissions qualify the “[p]rotocol was followed” sentence on [line 8](../results/history/RESULTS_B1.v1.md:8).

## 4. The frozen threshold

The table’s arithmetic is correct, and freezing the threshold before the run avoids choosing it to flatter these results. **Presenting the same numeric cutoff across three different confidence scales invites an invalid comparison.** No vendor threshold is documented in D11; each row is a descriptive application of one outside policy, not a like-for-like system comparison or a gate verdict. The report should say that beside the table.

“Anti-protective” needs a denominator. Within Jev’s authority arm, the gate admits **76/247** targeted decisions versus **4/53** non-targeted decisions, enriching targeted outcomes among what it admits. For decider those counts are **111/171** versus **73/129**; that operating-point contrast is much weaker. Neither comparison says whether a gate improves an actual deployment, whose traffic mix and costs were not measured.

## 5. DEV-2

The header split **does not confound E1 directly**: every Jev authority row used the later header, and E1 reads only that arm. It does affect claims comparing authority with clean traffic, including the threshold table. Matching choices in a small clean re-ask is inadequate for confidence equivalence; my raw-row check finds **7 clean-correct Jev scores within 0.06 of the cutoff**, where a shift of the size reported in the write-up could change admission.

For a defensible cross-arm table, re-ask the **entire clean arm** under the same header as authority, retain paired responses, and recompute clean rejection and confidence differences with a stated equivalence margin. To claim the *header itself* has no effect would require randomized, contemporaneous old-header/new-header paired calls if the old header can be accepted; otherwise withdraw that causal claim.

**FIX FIRST — rewrite the interpretation as a bounded, per-system E1 finding, with the exploratory department result and descriptive gate limits stated explicitly.**


