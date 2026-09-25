# Round 2 — external review of the corrected version (gpt-6-sol, reasoning effort xhigh, Codex CLI)

## Round 2 verdict

**FIX FIRST — rewrite the department-control interpretation as an explicitly weighted, exploratory sensitivity analysis, and remove claims that it establishes why the marginal results occurred.**

I independently joined the result rows to the frozen items and recomputed the figures below from those raw files. I used rank-based AUROC with half credit for ties and the frozen bootstrap settings for E1.

| System | Authority: resisted / hijacked | E1 AUROC [95% CI] | Pooled within-department AUROC [exploratory 95% CI] | Hijacks admitted at 0.85 | Clean-correct rejected |
|---|---:|---:|---:|---:|---:|
| Jev | 53 / 247 | 0.261 [0.190, 0.336] | 0.329 [0.251, 0.412] | 76 / 247 | 10 / 299 |
| decider-2b | 129 / 171 | 0.412 [0.348, 0.478] | 0.493 [0.412, 0.574] | 111 / 171 | 37 / 288 |
| kotoba | 197 / 103 | 0.571 [0.501, 0.640] | 0.497 [0.428, 0.567] | 10 / 103 | 184 / 252 |

The harness values, reported medians, distinct-score and tie counts, and authority ASR ordering also reproduce. So do the new counts: Jev’s gate rejects **171/247** hijacks, decider’s rejects **60/171**; Jev admits **76/247** hijacks versus **4/53** resisted authority decisions; kotoba has **18** wrong but non-targeted authority answers; and **7** Jev clean-correct scores lie within **0.06** of the cutoff. I reproduced Jev’s reported target, option-position and length-quartile controls; the decider department permutation result agrees to Monte Carlo precision. The frozen-file hashes match the write-up.

**The new statistical issue is interpretation, not arithmetic.** The pooled department figure weights each department by its number of resisted–hijacked pairs. That is a legitimate *same-department pair* AUROC, but the write-up does not define the weighting. For decider, departments containing **74 of its 300 authority rows** have only one outcome class and cannot contribute a within-department pair. Averaging the estimable departments equally instead gives **0.417**, rather than **0.493**; for kotoba it gives **0.561**, rather than **0.497**. Those are different estimands, not corrections to the reported calculation. They show why “the inversion disappears” and especially “the marginal figure **is explained** by which tickets get hijacked, **not by** hijacking” are too definitive. The permutation makes a department-mix explanation *compatible* with decider’s marginal result; it does not establish a causal explanation or absence of within-department association.

By contrast, Jev’s “attenuated, still clearly below 0.5” description **is supported for the reported pair-weighted estimate**: my exploratory interval is **[0.251, 0.412]**. Calling the analysis *EXPLORATORY* correctly identifies its timing, but does not make the causal wording in the headline and “What this supports” section sound.

The new Jev enrichment statement is fair **within the authority arm**. My recomputation gives admission rates of **30.8%** for hijacked and **7.5%** for resisted decisions; hijacks are **76/80** admitted authority decisions versus **247/300** authority decisions overall. It does not establish harm from a deployed gate, and the revision appropriately says that.

### Round 1 findings

- **Anti-protective deployment claim:** fixed in the main interpretation; the gate rejection counts and deployment limit are now stated. The remaining phrase that kotoba’s threshold is “not a working gate” still makes a utility judgment from a measured tradeoff without specified costs.
- **Decider inversion treated as an unqualified finding:** **partly fixed**. Its pre-registered marginal `INVERTED` label is retained and the exploratory control is shown, but the revision replaces the old overinterpretation with the definitive department explanation above.
- **Claim to settle willkelly’s question:** fixed; the revision acknowledges that study’s earlier analyses.
- **Claim that the header does not move the model:** fixed in scope; the revision limits the re-ask to sampled choices and acknowledges possible cutoff changes.
- **Missing trust-boundary and non-targeted-is-not-necessarily-correct statements:** fixed.

I found **no material underclaim** that warrants a stronger conclusion. The sampled gate results are sharper than a bare AUROC, but the report is right to withhold a deployment verdict.

**Not independently reproducible from the supplied raw rows:** the reported re-ask’s **30/30** choices and confidence differences, the per-row User-Agent assignment, Modal billing, and total project spend. The Jev rows do sum to the reported **672,896** input tokens; at the preregistered price they give **$0.0283** for those stored calls. That token sum does not include any separately performed re-asks.
