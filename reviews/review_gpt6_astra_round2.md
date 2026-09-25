**The revision fixes most substantive numerical errors, but I would not leave the current report public unchanged.** The headline accuracy comparisons and AMBIGUOUS verdicts survive scrutiny. Remaining problems concern an incorrect cascade explanation, incomplete reproduction fixes, and unsupported explanatory language—not a collapse of the results.

I ran both analysis scripts, independently recomputed the main comparisons, verified the preregistration hash, and checked all three dataset URLs. I executed the figure code with its final save intercepted to preserve your no-modification requirement. I did not run paid model calls or training. The report’s Git working tree remains clean.

**Verification of all ten erratum items**

References below are to the current `report/README.md`.

| Item | Result |
|---|---|
| **1. Cascade framing** | **Partial—major.** All three sensitivity rows reproduce: `(0.220, 0.485, +0.265)`, `(0.490, 0.730, +0.240)`, `(1.000, 0.730, −0.270)`. The explanation at lines 93–96 is false; see finding 1. |
| **2. Calibration language** | **Fixed.** AUROC is correctly distinguished from calibration. B1’s paired AUROC-difference CI reproduces as **[−0.187, +0.008]**. My B0 paired bootstrap also includes zero, approximately **[−0.021, +0.137]**, supporting the cautious “neither direction is established.” |
| **3. Cascade mechanism** | **Fixed for this claim.** Lines 115–118 explicitly mark the explanation as a hypothesis. The global repair/harm counts are correct: **9/0 for Jev; 26/2 for nano**. |
| **4. B0 escalation rates** | **Fixed.** Under B1’s rule, Jev escalates **27/208 = 0.129808**, achieving **180/208 = 0.865385**; nano escalates **92/208 = 0.442308**, achieving **0.875**. |
| **5. Encoder versus frontier** | **Fixed.** Paired advantage is **12/208 = 5.769pp**; full-300 advantage is **23/300 = 7.667pp**. The reported paired CI **[+2.4, +9.6]pp** reproduces with a fresh seed-0 bootstrap. |
| **6. Cross-fit check** | **Fixed.** Rates **0.225/0.435**, accuracies **0.900/0.895**, and failure to reach **0.905** all reproduce and are disclosed. |
| **7. Cost/recomputability** | **Partial—minor.** The unsupported Jev-versus-LLM cost comparison is removed. But lines 228–229 still incorrectly say all table numbers except LLM costs come from `results/*.jsonl`; the serial latency table comes from **`results/latency_serial.json`**. |
| **8. B0 missingness/verdict** | **Numerically fixed; audit incomplete.** Retained/omitted Terra accuracies are **0.875/0.804348**. B0 is indeed **AMBIGUOUS**. The completion/stopping history remains unavailable, and the supplied retry workflow has problems described below. |
| **9. Arbitrary 5pp rule** | **Fixed conceptually; new minor CI inconsistency.** Actual intervals replace the rule, but the revised encoder-versus-Jev endpoint does not match the supplied analysis script. |
| **10. Structured output/reproduction** | **Partial—major.** “JSON-prompted, regex-parsed” is correct, and analysis of the published files now works. Analysis of newly generated results remains silently misdirected. |

**Remaining findings**

1. **[Major; newly introduced] Exact parity is reachable—the report incorrectly says otherwise.**

   [README lines 93–96](../README.md:93) say confidence-1.0 items “can never be escalated” and Jev-first cascades “cannot reach exact Terra parity at any threshold.”

   Both [PREREG_B1 lines 24–25](../prereg/PREREG_B1.md:24) and `analyze_b1.py:18` explicitly include **t = 1.01**. At that threshold, every item is escalated, and accuracy is **0.915**, exactly Terra’s accuracy.

   The correct explanation is:

   > No threshold retaining any Jev answers achieves exact parity on this sample. At t = 1.0, escalation is 0.490 and accuracy is 0.910; at t = 1.01, escalation is 1.000 and accuracy is 0.915.

   The **102 confidence-1.0 items and six errors are correct**, but only **one of those six errors is repairable by Terra**. This is a threshold jump, not an unreachable accuracy ceiling. The sensitivity table itself is correct.

2. **[Major; introduced by the path fix] Reruns silently analyze the old published results.**

   Runners write to:

   - `code/results_b0.jsonl` — `run_b0.py:8`
   - `code/results_b1.jsonl` — `run_b1.py:11`

   But `analyze_b0.py:3`, `analyze_b1.py:4`, and `make_figure.py:5` preferentially select **`results/results_*.jsonl`**, which already exist in the published repository.

   Thus following the rerun instructions and then running the analyses produces the original report again, regardless of the new outputs. There is no input-path argument to override this. Erratum item 10’s “Both fixed” is premature.

   **What does work:** from the published repository root (`report/` here), both analysis commands run successfully. The figure code resolves its inputs and output directory correctly. All three download URLs returned HTTP 200 with the expected dataset sizes.

3. **[Major; remaining reproducibility defect] B0’s supplied retry/resume code does not implement the described treatment of failures.**

   `run_b0.py:21–33` writes exhausted failures with `correct=False`. On restart, lines 11–13 mark **every existing row as done**, including failures. `analyze_b0.py:19–20` retains those false values because they are not missing.

   The apparent cleanup helper, `finish_jev.sh:8–16`, still references nonexistent **`pilot/results_b0.jsonl`** and **`pilot/run_b0.py`** within the published layout.

   Therefore the supplied workflow cannot reproduce “failures were retried, never scored as wrong” without undocumented intervention. **This does not invalidate the published scores:** their 1,108 B0 rows contain no such failure records.

   Similarly, B1’s analyzer drops final Jev `error` rows (`analyze_b1.py:6`), whereas preregistration line 20 says final failures count as wrong with confidence zero. This discrepancy does not affect the published complete B1 sample.

4. **[Minor; newly introduced] The encoder-versus-Jev CI disagrees with the supplied script.**

   [README line 55](../README.md:55) now reports **+10.1pp [+5.3, +15.4]**. Running `analyze_b0.py` produces:

   ```text
   paired acc diff encoder-jev: +0.101 [+0.053,+0.149]
   ```

   The README interval reproduces when the bootstrap RNG is **reset to seed 0 for that comparison**. The script instead continues a shared RNG after earlier calculations. Both are plausible Monte Carlo intervals, but the published deterministic computation and text disagree. The previous **+14.9pp** endpoint matched the script.

5. **[Major; remaining overclaim] The encoder’s causal explanation is still asserted without testing it.**

   [README lines 126–128](../README.md:126) say learning dataset conventions **“is” a contributing factor**, and a zero-shot model has **“no way”** to infer them.

   The experiment measures an accuracy difference; it does not identify its cause. A label example does not establish how much of the advantage comes from conventions, and the impossibility claim is unsupported. Use “a possible contributor” and “may be ambiguous from label names alone.”

   The surrounding recommendation to **test a supervised baseline when comparable labeled data exists** is appropriately limited and can stay.

6. **[Minor; new latency wording] The ~2× observation holds, but “matched” and “no repeat-latency measurement” need precision.**

   The Summary compares Jev’s **200-item** median, **0.43s**, with nano’s **30-item serial** median, **0.923635s**. On the same 30 items, Jev’s median is **0.422950s**, giving approximately **2.18×**. Thus the numerical conclusion survives.

   However, line 151’s claim about concurrency rests on different-time measurements, and the table compares 30 serial items against 200 concurrent items. It is descriptive evidence, not an isolated causal estimate of concurrency’s effect.

   Line 158’s “no repeat-latency … measurement” also conflicts with the explicitly repeated 30 LLM items. Say there was no systematic repeated-run latency study.

7. **[Minor] Some preregistration and reproduction claims remain incomplete.**

   - `PREREG_B0.md:12` says an ambiguous result will not motivate expansion, yet B1 followed an ambiguous B0. This deviation is absent from README’s “full disclosure” list.
   - README line 60 describes B1 as testing superior error ranking. B1’s actual primary hypothesis concerns **escalation at the accuracy target**; AUROC is secondary.
   - The B1 SHA-256 digest matches exactly, but `shasum -a 256 -c prereg/PREREG_B1.sha256` fails: its filename is **`pilot/PREREG_B1.md`**, and the additional timestamp line is malformed for checksum verification.
   - The analysis commands do not emit all revised supporting quantities: notably accuracy-difference CIs for B1, encoder-versus-Terra CI, and margin sensitivity. They are independently recoverable, but the revision’s verification calculation is not supplied.
   - `analyze_b1.py` prints B1’s verdict only; `analyze_b0.py` prints ingredients rather than a B0 verdict. README line 212’s plural “verdicts” is inaccurate.

**What is still missing before stronger trust or deployment claims**

- **[Major for auditability] B0 completion provenance:** retained IDs exist, but failed-attempt history, cleanup actions, and the stopping decision are needed to assess selection. Pairing does not guarantee that relative advantages generalize beyond the retained subset.
- **[Minor for reproducibility] Frozen inputs and environment:** pin dataset revisions/checksums, encoder revision, and package versions. The supplied URLs track mutable branches.
- **[Minor for preregistration provenance] Independently timestamped registration evidence:** the matching hash verifies content integrity, not that the document existed before model calls.
- **[Major only for a deployment-savings claim] A frozen threshold evaluated on independent data at the required accuracy.** The current cross-fit result does not establish this; the revised report now admits that correctly.

**Final verdict:** **Not safe entirely as written; a targeted correction is still needed.** The principal descriptive results are sound: B1 **+7.5pp** accuracy over nano, approximately **2× lower successful-call latency**, B0 encoder **+5.8pp** over Terra, and **no established cascade advantage**. Those claims can remain. Correct the unreachable-parity explanation, rerun-analysis routing, remaining causal assertion, and smaller inconsistencies before treating the erratum as complete.
