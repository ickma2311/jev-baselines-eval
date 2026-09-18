**An edit/erratum is needed.** The core B1 numbers reproduce, but the public narrative overstates them, the cross-fit presentation omits failed accuracy targets, and two reported comparisons are numerically wrong.

I reviewed the requested files and recomputed from both JSONL files without modifying anything. The B1 preregistration is at `report/prereg/PREREG_B1.md`; its contents and the published result files match their pilot copies.

1. **[Blocking] The cross-fit check does not validate savings at the stated accuracy target.**  
   [README lines 53–65](/Users/chaoma/projects/research/jev_workflow/report/README.md:53) place cross-fit escalation rates under “reach Terra’s own accuracy (within 1pp)” and invoke their consistency as reassurance. But the analysis produces:

   | Policy | Escalation | Held-out accuracy | Required accuracy |
   |---|---:|---:|---:|
   | Jev → Terra | 22.5% | **90.0%** | 90.5% |
   | nano → Terra | 43.5% | **89.5%** | 90.5% |

   **Neither meets the target.** Cross-fitting appropriately separates threshold selection from evaluation, but the resulting rate difference is not a validated difference in minimum escalation *at matched target accuracy*. Reporting the rates without these accuracies materially misleads readers.

2. **[Blocking] The headline claims calibration results that were never measured.**  
   [Lines 24–26, 69–75 and 86](/Users/chaoma/projects/research/jev_workflow/report/README.md:24) turn confidence AUROC into “better calibrated,” “not better calibrated,” and “was worse.” AUROC measures discrimination between correct and incorrect answers. It does not measure whether confidence 0.9 means approximately 90% correctness; monotonic transformations can preserve AUROC while radically changing calibration.

   Furthermore, the reported AUROC-difference interval **[−0.187, +0.008] includes zero**. It establishes neither inferiority nor equivalence. The defensible statement is: “Jev had lower observed correctness-ranking AUROC than nano’s verbalized confidence on B1; the paired interval included zero.” Verbalized confidence is a legitimate operational baseline, but it does not represent all LLM confidence methods. Logprobs would not automatically solve calibration either.

3. **[Major] The narrative misidentifies the preregistered hypothesis and overrules the AMBIGUOUS verdict.**  
   [B1 preregistration lines 4–5](/Users/chaoma/projects/research/jev_workflow/report/prereg/PREREG_B1.md:4) define H1 as **lower escalation at matched accuracy**, not superior calibration. Thus “The mechanism hypothesis failed” and “This also contradicts my own pre-registered hypothesis H1” ([README lines 67–75](/Users/chaoma/projects/research/jev_workflow/report/README.md:67)) are inaccurate.

   The primary result is **Δ = 26.5pp, interval −53.0 to +59.5pp, AMBIGUOUS**. That is consistent with substantial advantage or disadvantage. “Jev-first cascades reach frontier accuracy while sending roughly half as much traffic” should be explicitly an **in-sample, threshold-selected observation**, not the main affirmative conclusion with uncertainty appended afterward.

4. **[Major] The instability of \(R\) is substantive, not a bootstrap nuisance readers should discount.**  
   [Lines 62–65](/Users/chaoma/projects/research/jev_workflow/report/README.md:62) acknowledge instability but immediately emphasize the favorable cross-fit direction. My recomputation shows:

   - In the specified 2,000 bootstrap samples, **Jev’s \(R=1\) in 7.6%**; nano’s never does.
   - Jev assigns confidence **1.0 to 102/200 items**, including six errors. This creates a large indivisible threshold jump.
   - Requiring **exact Terra accuracy**, instead of allowing a 1pp shortfall, gives **\(R_\text{Jev}=1.00\), \(R_\text{nano}=0.73\), Δ = −0.27**.
   - Allowing a 0.5pp shortfall gives **0.49 versus 0.73**.

   The preregistered 1pp margin must remain primary, but these results make “at equal accuracy” ([line 21](/Users/chaoma/projects/research/jev_workflow/report/README.md:21)) particularly misleading. The percentile interval is reproducible; its nominal coverage for this discontinuous, threshold-selected statistic is not established merely by preregistration.

5. **[Major] B0’s Jev escalation number uses the wrong accuracy criterion.**  
   [Lines 53–58](/Users/chaoma/projects/research/jev_workflow/report/README.md:53) report **0.255** under the “within 1pp” criterion. Terra’s B0 accuracy is 182/208, so the target is approximately **0.865**.

   Applying B1’s threshold rule gives Jev **27/208 = 0.1298** escalation at threshold **0.64**, with accuracy **180/208 = 0.8654**. Even the coarser B0 analysis grid reaches the target at **0.2019**, not 0.255. The reported 0.255 achieves exact Terra accuracy on that coarse grid. The table mixes criteria.

6. **[Major] “The encoder beat the frontier LLM by 8pp here” is wrong on the reported paired sample.**  
   [Lines 79–80](/Users/chaoma/projects/research/jev_workflow/report/README.md:79): **0.9327 − 0.8750 = 5.77pp**, not 8pp. Approximately 8pp comes from the full 300-item comparison, whose Terra accuracy is different.

   The encoder result remains strong: my paired bootstrap gives approximately **+2.4 to +9.6pp** versus Terra. Correct the arithmetic and identify the sample consistently.

7. **[Major] The proposed causal explanation for cascade savings is untested.**  
   [Lines 72–74](/Users/chaoma/projects/research/jev_workflow/report/README.md:72) say savings “come from” higher standalone accuracy and dismiss B0’s confidence signal as “post-hoc noise.” Neither follows from the analyses.

   Routing value depends on which errors Terra can repair and which correct answers escalation can spoil—not merely first-stage accuracy or correctness AUROC. In B1:

   - Jev/Terra: **9 repairable errors, 0 harmful substitutions**.
   - nano/Terra: **26 repairable errors, 2 harmful substitutions**.

   These observed error relationships matter. A mechanism claim needs random-routing controls, error-overlap analysis, and ranking by potential escalation benefit. A nonsignificant reversal does not establish that the original observation was noise.

8. **[Major] The latency ratios describe two unequal serving configurations, not isolated model speed.**  
   [Lines 83–87 and 103–104](/Users/chaoma/projects/research/jev_workflow/report/README.md:83): Jev runs serially through Vercel; LLMs run at concurrency six through Lightning. Concurrency can affect queueing and contention, but these records do not establish its direction or magnitude. The approximately 2× ratio is a valid descriptive ratio of recorded successful-call medians; it is not a controlled speed comparison.

   Moreover, B1 has **45 Jev items requiring multiple attempts**, including **38 requiring 11 attempts**. Recorded latency excludes failed attempts and backoff ([runner lines 73–86](/Users/chaoma/projects/research/jev_workflow/pilot/run_b1.py:73)). Thus successful-call latency must be separated from completion latency and throughput. The categorical vendor-speed rebuttal also needs the vendor claim’s actual comparison conditions.

9. **[Major] The practical cost recommendation is unsupported by the published records.**  
   [Lines 83–85](/Users/chaoma/projects/research/jev_workflow/report/README.md:83) say Jev costs “a fraction” of nano. Both result files record Jev costs, but **no nano or Terra per-call costs**. Consequently, [lines 141–142](/Users/chaoma/projects/research/jev_workflow/report/README.md:141)—“every number … is recomputable”—are too broad.

   Report token usage, pricing basis and actual LLM costs before making the comparison. For cascades, compute total cost including every first-stage call; reduced Terra traffic alone is insufficient.

10. **[Major] B0’s missingness is disclosed, but its claimed harmlessness is not demonstrated.**  
    [Lines 108–110](/Users/chaoma/projects/research/jev_workflow/report/README.md:108) assert failures are content-independent. Pairing prevents comparing methods on different retained items; it does not prove the retained sample represents the intended 300.

    Terra scores **87.5% on retained items versus 80.4% on omitted items**. That does not prove selection bias, but it shows subset choice materially changes reported performance. The completion process, stopping decision and failed-attempt history need an audit. Also, contrary to [lines 18–20](/Users/chaoma/projects/research/jev_workflow/report/README.md:18), both preregistered verdicts are not explicitly reported: applying B0’s rules yields **AMBIGUOUS** too.

11. **[Major] Sample-size uncertainty is handled inconsistently; secondary findings become recommendations.**  
    [Line 118](/Users/chaoma/projects/research/jev_workflow/report/README.md:118), “Differences under ~5pp are noise,” is statistically indefensible. Precision depends on paired disagreements and subgroup sizes, not a universal percentage-point cutoff.

    B1’s accuracy advantage is reasonably supported **for this sample and configuration**: Jev − nano = **7.5pp**, paired bootstrap approximately **[3.0, 12.5]pp**. Conversely, the “markedly better” OOS claim uses only **35 examples: 25 versus 17 correct**. Its paired exact test is approximately **p = 0.039 before multiplicity adjustment**. Numerous models, endpoints and datasets are discussed; secondary comparisons should remain exploratory. One run per item also leaves generation variability unmeasured.

12. **[Major] The encoder is a useful baseline, but the recommendation exceeds the experiment.**  
    [Lines 79–82 and 98–100](/Users/chaoma/projects/research/jev_workflow/report/README.md:79): training on Banking77’s separate training split is **not itself leakage**. It is a legitimate deployment alternative when comparable labeled data exists. It is nevertheless a different information regime: **10,003 labeled examples versus zero task-training examples**.

    One experiment does not justify “If you have labeled data, train a small encoder” across tasks, label budgets and distribution shifts. “Mostly because” it learns conventions is an untested explanation; “no zero-shot model can guess” is an absolute claim without support. Keep the result, state the training budget, and add learning curves before generalizing.

13. **[Minor] “Structured output” overstates the implemented LLM constraint, and prompt robustness is missing.**  
    [Line 16](/Users/chaoma/projects/research/jev_workflow/report/README.md:16) says structured output, but [the implementation](/Users/chaoma/projects/research/jev_workflow/pilot/common.py:49) requests JSON in text and parses it with a regex; it does not supply a schema-constrained output setting. Call it “JSON-prompted output.”

    Untuned prompts do not invalidate this comparison. They limit it to these prompts and interfaces. Before broader capability claims, test equivalent label descriptions and a small, equal-budget prompt comparison selected on separate development data.

14. **[Major] The published reproduction instructions do not match the published directory layout.**  
    [Lines 129–142](/Users/chaoma/projects/research/jev_workflow/report/README.md:129) invoke `code/…`, but analysis scripts load results beside themselves while published files are in `results/`. The figure script hardcodes `pilot/results_*.jsonl`; runners require a `data/` directory absent from `report/`. A reader cannot reproduce the report from the published bundle using these commands as written.

**What is good and should stay:** the paired comparisons, released per-item outputs, inexpensive nano baseline, supervised encoder alternative, separate-dataset follow-up, explicit AMBIGUOUS category, and disclosure of confidence source and execution conditions. Most central table values reproduce. The study is useful as a small, transparent evaluation; its weaknesses do not erase those observations.

**The three most important fixes, in order:**

1. **Correct the public claims immediately:** remove calibration and causal assertions; lead with the AMBIGUOUS primary outcome; disclose cross-fit accuracies; fix B0 escalation and the encoder’s 8pp claim.
2. **Make the cascade evidence decision-relevant:** show accuracy alongside every rate, threshold/margin sensitivity and confidence ties. For confirmation, select thresholds on separate data and evaluate a frozen policy against the accuracy constraint; include random-routing and error-overlap controls.
3. **Repair operational comparisons and reproducibility:** matched-concurrency timing with retries reported separately, measured LLM/cascade costs, an auditable B0 completion history, and working published analysis paths.

**Verdict:** **The headline claims are not safe to leave public as written. An explicit correction is warranted.** A defensible replacement is:

> In two small intent-classification samples, Jev had higher observed accuracy and lower recorded successful-call latency than the tested nano configuration. B1 did not establish lower escalation at matched accuracy. A supervised encoder achieved the highest accuracy on Banking77.
