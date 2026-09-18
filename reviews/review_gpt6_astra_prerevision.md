## Bottom line

**The report needs a public correction, not just additional caveats.** The disclosed measurements are useful, but the headline and practical recommendations materially exceed them.

The most serious problems are:

- **AUROC is repeatedly misrepresented as calibration.**
- **The cross-fit results omit the accuracies that undermine the claimed matched-accuracy confirmation.**
- **The report misstates what its pre-registered H1 actually was.**
- **The primary result is AMBIGUOUS, yet the prominent narrative presents cascade savings as established.**
- **“Beat the frontier LLM by 8pp” is an arithmetic error: the reported difference is 5.8pp.**

This review is based on the supplied report, pre-registration, and analyzer output—not an audit of the raw predictions or code.

## 1. Factual and statistical errors

### 1.1 The report did not measure calibration

AUROC measures how well a confidence score **ranks correct answers above incorrect answers**. It does not measure whether a stated confidence of 0.8 corresponds to approximately 80% correctness.

A monotone transformation can radically change calibration without changing AUROC at all.

Consequently, these statements are unsupported:

> “its confidence is not better calibrated than an LLM’s”

> “not explained by better calibration”

> “On CLINC150 it was worse.”

The measured outcome is **correctness discrimination using the available confidence scores**, not calibration. Even for that outcome, Jev–nano’s B1 interval, **[−0.187, +0.008]**, includes zero. The result favors nano descriptively; it does not establish population-level inferiority at the reported confidence level.

**Required correction:** Replace “calibration” with the precise measured property throughout. To discuss calibration, first establish what Jev’s confidence purports to mean, then report reliability plots and appropriate probability-scoring metrics with uncertainty.

### 1.2 The README misidentifies the pre-registered hypothesis

The pre-registration’s H1 is:

> Jev-first routing requires fewer large-model calls than nano-first routing to achieve the same accuracy.

It is **not**:

> Jev’s confidence is better calibrated, or better at separating correct from incorrect answers.

AUROC is explicitly secondary.

The README’s placement of “my own pre-registered hypothesis H1 … unsupported” under **“The mechanism hypothesis failed”** therefore rewrites the pre-registration. H1 was unconfirmed because the primary cascade result was ambiguous. The confidence mechanism was not the registered primary hypothesis, and its failure was not established either.

**Required correction:** Separate:
1. The registered cascade hypothesis: **unconfirmed**.
2. The confidence-discrimination observation: mixed across datasets, with uncertain B1 difference.
3. The proposed mechanism: not established by this analysis.

### 1.3 The cross-fit result does not confirm matched-accuracy savings

The README reports cross-fit escalation rates while omitting the associated accuracies:

| Cross-fit cascade | Escalation | Accuracy | Difference from Terra |
|---|---:|---:|---:|
| Jev → Terra | 0.225 | 0.900 | −1.5pp |
| nano → Terra | 0.435 | 0.895 | −2.0pp |

The specified target is **0.905**. **Neither cross-fit cascade reaches it.**

Thus, “a consistent Δ = +0.210” means that the selected policies have different held-out escalation rates. It does **not** mean that a 21pp reduction at matched accuracy survived held-out evaluation.

The misses are small—one and two items below the pooled target—but that does not justify silently treating the constraint as satisfied. With this sample, constraint satisfaction is itself uncertain.

Cross-fitting is a sensible response to threshold-selection optimism. The problem is the interpretation, not the idea. It needs:

- Held-out accuracy and escalation reported together.
- Paired uncertainty relative to Terra.
- An explicit rule for policies that miss the accuracy target.
- A clear distinction between evaluating a selected policy and estimating an optimal matched-accuracy frontier.

**The omitted cross-fit accuracies should be restored prominently.**

### 1.4 The primary result cannot sustain the prominent cascade claim

The registered result is:

\[
\Delta=0.265,\qquad 95\%\ \mathrm{CI}=[-0.530,\;0.595].
\]

Under the reported procedure, the interval accommodates both a very large nano advantage and a very large Jev advantage. The correct registered verdict is **AMBIGUOUS**.

Yet the preceding sentence says:

> “Jev-first cascades reach frontier accuracy while sending roughly half as much traffic…”

That is defensible only as a description of **thresholds selected and evaluated on these same samples**. It is not an established deployment result.

“Treat the direction as suggestive” is useful, but does not undo the more prominent assertion.

Also, “equal accuracy” is inaccurate terminology: the criterion permits **one percentage point below** the observed Terra accuracy. Say “within 1pp of observed Terra accuracy.”

### 1.5 The instability of \(R\) is substantive, not a nuisance to explain away

The metric takes the smallest escalation rate among thresholds satisfying an empirical accuracy constraint. Several features make this fragile:

- At \(n=200\), one item changes accuracy by **0.5pp**; the entire tolerance is two items.
- Accuracy need not increase monotonically with escalation: Terra can overwrite a correct first-stage answer with an incorrect one.
- A tiny change in the sampled errors can eliminate an early qualifying threshold and make \(R\) jump to a much higher escalation rate.
- Confidence ties and the number of available thresholds can differ substantially between models.
- The target accuracy is itself estimated from the same sample.

Recomputing Terra’s accuracy and both policies in each paired bootstrap replicate is appropriate. But a percentile bootstrap for this discontinuous, selected statistic does **not automatically have reliable 95% coverage**. Its validity needs investigation rather than an assumption.

Conversely, saying the statistic is unstable does not authorize substituting the point estimate or cross-fit traffic gap for the inconclusive inference.

The pre-registration’s claim that selection optimism is “symmetric” is also too strong. **Applying the same procedure is not evidence of equal bias.** Different confidence granularity, curve shapes, and error patterns can produce different selection optimism.

A better confirmatory endpoint would evaluate thresholds fixed on separate calibration data, with held-out accuracy non-inferiority and escalation savings reported jointly.

### 1.6 The proposed explanation for cascade savings is not demonstrated

> “They come from Jev’s higher standalone zero-shot accuracy…”

Higher initial accuracy reduces the number of net corrections needed. It is a plausible contributor, not an identified explanation.

For any escalated set \(S\), the accuracy gain is determined by:

\[
\frac{
\#(\text{first stage wrong, Terra right in }S)
-
\#(\text{first stage right, Terra wrong in }S)
}{n}.
\]

Therefore, savings depend on:

- Initial accuracy.
- Which errors Terra can fix.
- Which correct answers Terra would spoil.
- Whether confidence selects the beneficial cases.

Lower correctness AUROC does not isolate the contribution of baseline accuracy, and global AUROC may not reflect ranking quality near the operating threshold.

The report should show error overlap, random-routing controls, and oracle-routing bounds before assigning the mechanism.

### 1.7 There is a straightforward arithmetic error

> “It beat the frontier LLM by 8pp here”

The reported accuracies are 0.933 and 0.875:

\[
0.933-0.875=0.058.
\]

That is **5.8 percentage points**, not 8.

Moreover, the report supplies the encoder–Jev paired interval, not the encoder–Terra paired interval. The higher encoder point estimate is clear; a statistical superiority claim over Terra requires the direct paired comparison.

### 1.8 Small samples support some conclusions, not a blanket “noise” rule

> “Differences under ~5pp are noise here.”

This is statistically wrong as a general statement. Paired uncertainty depends on **discordant outcomes**, not just total sample size or the size of the accuracy difference.

What these results support:

- **B0 encoder versus Jev:** substantial positive difference under the reported interval.
- **B0 Jev versus nano:** uncertain; the paired interval includes zero.
- **B1 Jev versus nano accuracy:** a 7.5pp observed difference, but the paired interval is missing. Marginal accuracies alone do not determine it.
- **B1 confidence discrimination:** inconclusive difference under the reported interval.
- **B1 cascade savings:** inconclusive primary result.

At 150 intents plus OOS, 200 examples also provide very limited evidence about individual intents or deployment robustness.

The OOS result is **25/35 versus 17/35**, with Terra at **28/35**. “Markedly better” should be restricted to the observed sample until the paired comparison and uncertainty are shown.

### 1.9 Secondary-result multiplicity needs honest handling

The one registered primary endpoint is a strength. There is no need to retroactively penalize it simply because descriptive secondary outcomes exist.

But the report then promotes selected findings across datasets, models, accuracy, AUROC, OOS recall, latency, and cascades into strong conclusions. Those secondary intervals are not a simultaneous confidence guarantee.

Keep them exploratory, or define a limited confirmatory family and use appropriate inference. Do not rescue an ambiguous primary result with whichever secondary endpoint looks strongest.

## 2. Confounds and fairness

### Verbalized confidence versus logprobs

This does **not invalidate a comparison of the actual deployed interfaces**. If these are the scores users receive, their routing utility is worth measuring.

It does invalidate generalization from that comparison to “LLM confidence” broadly. Neither verbalized confidence nor token logprobs are automatically calibrated correctness probabilities.

Calling verbalized confidence a “ceiling caveat” is misleading. It is an **interface and elicitation limitation**, not a demonstrated bound. Logprobs could improve or worsen the relevant metric, and multi-token label probabilities require careful construction.

### Untuned prompts

Using the same prompt for two LLMs standardizes an input; it does not establish equal optimization or best attainable performance. Jev’s typed-choice interface is itself a specialized task interface.

The current result is a comparison of **these implementations**, not model capability in general. Test a small, predetermined set of reasonable prompts and schema-enforced outputs using separate development data.

The introduction’s “structured output” also needs clarification: asking for JSON is not necessarily constrained decoding.

### Serial Jev versus concurrency-six LLM latency

The observed median ratios are approximately **1.9× and 2.0×**. That arithmetic is fine.

The experimental comparison is not controlled:

- Concurrency can affect queueing, client contention, and provider throttling.
- Gateways, backend load, and service tiers differ.
- Network time is included.
- Per-call latency is not throughput or inference-only compute time.

Concurrency six does not mechanically multiply latency by six, and its effect cannot be determined from these summaries. But it prevents attributing the ratio cleanly to model speed.

The reported Jev free-tier limit also matters operationally: fast individual calls do not imply high sustainable throughput.

**Safe wording:** “About 2× lower median observed API latency under these different calling configurations.”

The vendor’s 40–200× claim cannot be declared refuted without specifying and matching its comparator, workload, and latency definition.

### Rate-limit-induced B0 subsample

Pairing all models on the same retained items is good.

However, “rate-limit failures are content-independent” is an assertion requiring support. Explain:

- How the 208 items were retained from the planned 300.
- Whether item order was randomized.
- Whether every item in that retained subset completed.
- Whether inclusion or stopping depended on observed outcomes.

If this was an outcome-independent prefix of a randomized order, the main issue is reduced precision, not necessarily bias. Do not allege bias without evidence—but do not declare it absent without documenting the selection process.

### One run per item

One call per independently sampled item can be a reasonable estimate of one-shot deployment performance. Repeats are not automatically more valuable than more independent items.

But this design cannot characterize run-to-run prediction variability, confidence stability, temporal API variation, or stable threshold behavior. Those limitations matter especially for a confidence-gated cascade.

### The supervised encoder

This is a **legitimate and useful labeled-data baseline**, not an unfair comparison merely because it used the official training split. That is standard supervised evaluation.

It is not a zero-shot peer. Its advantage is conditional on having **10,003 relevant labeled examples**, which is much stronger than “having labeled data.”

The general recommendation needs qualification:

- A small labeled set may not reproduce this result.
- Training, labeling, maintenance, and local inference are not free.
- M4 Max timing is hardware-specific.
- Domain shift may change the comparison.
- The explanation that it wins “mostly” by learning labeling conventions is unsupported by a single example.
- “Conventions no zero-shot model can guess” is an unjustified absolute.

Keep the baseline; narrow the conclusion.

## 3. Headline and practical overclaims

The headline bundles three differently supported propositions:

1. **Good zero-shot classifier:** reasonable as a qualified description of the observed task results.
2. **2× faster, not 40–200×:** only the first part describes these measured configurations; the vendor-wide rebuttal is unsupported.
3. **Not better calibrated:** not measured.

The practical section further adds “a fraction of the cost” without reporting nano’s per-call costs alongside Jev’s. It also omits total cascade cost, including first-stage calls and escalations.

A defensible replacement headline would be:

> **On two small intent-classification samples, Jev had higher observed accuracy than nano and about half its median API latency under the tested configurations. Cascade savings remain inconclusive. A supervised encoder had the highest Banking77 accuracy.**

## 4. Analyses and baselines a skeptic should demand first

In priority order:

1. **Honest held-out cascade evaluation.** Publish selected thresholds, held-out accuracy differences from Terra, escalation rates, and uncertainty together. Treat accuracy non-inferiority as a requirement, not an implied property.
2. **Paired accuracy and OOS comparisons.** Include encoder–Terra, B1 Jev–nano, and OOS discordance tables.
3. **Error-overlap and routing controls.** Random escalation at matched budgets, oracle escalation bounds, and the counts of beneficial versus harmful Terra overrides.
4. **Fuller evaluation samples.** More independent examples and OOS coverage; size the study around the intended accuracy margin and routing improvement.
5. **Actual calibration analysis**, if retaining any calibration claim, plus explicit confidence semantics.
6. **Matched latency experiments.** Equal concurrency, interleaved measurements, retries and waiting time, throughput, hardware, and complete cost accounting.
7. **Cheap practical baselines.** TF–IDF/character n-gram linear models and supervised learning curves on Banking77; reasonable untuned or development-selected prompt alternatives for nano.

Not all are prerequisites for publishing a pilot. They are prerequisites for the broader practical conclusions currently attached to it.

## 5. What is good and should remain

- The **AMBIGUOUS** primary verdict is disclosed rather than suppressed.
- B1 separates a B0 exploratory observation from a later registered test.
- Paired comparisons and paired resampling are appropriate.
- Recomputing the shared Terra target inside bootstrap replicates preserves an important dependence.
- Nano and supervised baselines are much more informative than frontier-only comparisons.
- The report discloses interfaces, confidence sources, sample reductions, prompt limitations, and single-run evaluation.
- Cross-fitting was a good planned check, even though its result is overstated.
- Publishing raw per-item results and analysis scripts makes meaningful correction possible.
- The explicit exclusion of end-to-end agent claims is appropriate.

## The three most important fixes

1. **Correct the public narrative immediately.** Remove calibration claims, accurately identify H1, label cascade savings unconfirmed, change 8pp to 5.8pp, and scope latency and labeled-data recommendations.
2. **Restore the complete cross-fit result and repair cascade inference.** Show that both held-out policies missed the empirical target. Stop presenting traffic-only agreement as confirmation of matched-accuracy savings.
3. **Run a larger, independently calibrated evaluation with controlled operational comparisons.** Freeze thresholds before final testing; report paired accuracy/non-inferiority, routing savings, OOS uncertainty, latency, and costs.

## Public-report verdict

**Not safe to leave public as written. A dated correction is warranted.**

The underlying pilot is worth keeping public. The problem is not that \(n=200\) makes every observation worthless. The problem is that the report transforms an explicitly inconclusive primary result into confident practical advice, labels discrimination as calibration, and omits the part of its cross-fit output that matters most to the claim being checked.
