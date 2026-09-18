# Jev vs. the right baselines: a pre-registered independent evaluation

Independent evaluation of [TypeSafe's Jev](https://www.typesafe.ai/) (System One typed-decision model) on
**intent classification and confidence-gated cascades**, run on 2026-09-18, two days after Jev's public launch.

Not affiliated with TypeSafe. No vendor involvement, no free credits; API costs (~$1 total) paid by the author.

## Why another Jev eval

Several independent evals appeared within 48h of launch
([4esv/jev-eval](https://github.com/4esv/jev-eval), [themsquared/jev-benchmark](https://github.com/themsquared/jev-benchmark),
[classmethod](https://dev.classmethod.jp/en/articles/jev-for-llm-model-routing/)). They mostly compare Jev against a
*frontier* LLM. This report adds three things:

1. **Baselines Jev actually has to beat**, not just frontier models:
   a **nano-class LLM** (`gpt-5.4-nano`, ~0.9s, structured output) and a **supervised encoder**
   (frozen `bge-small-en-v1.5` + logistic regression, 10k training examples, 9ms, free, runs on a laptop).
2. **Pre-registration.** Kill/go criteria were written before looking at results; the second experiment's
   pre-registration is hash-pinned (`prereg/PREREG_B1.sha256`). Both experiments are reported with their
   pre-registered verdicts, including the one that failed to confirm my own hypothesis.
3. **A cascade metric that reflects how you would actually deploy this**: at equal accuracy, what fraction of
   traffic still has to reach the expensive model?

**Headline: on these tasks Jev is a good zero-shot classifier that is ~2x faster than a nano-class LLM — not
40–200x — and its confidence is not better calibrated than an LLM's. Where labeled data exists, a 9ms
supervised classifier beats everything, including the frontier model.**

## Results

### B0 — Banking77 (77 labels, paired n=208)

| method | accuracy [95% CI] | median / p95 latency | conf. AUROC |
|---|---|---|---|
| Jev | 0.832 [0.779, 0.880] | 0.44 / 0.71 s | 0.853 |
| gpt-5.4-nano | 0.793 [0.736, 0.851] | 0.85 / 1.52 s | 0.795 |
| GPT-5.6 Terra | 0.875 [0.827, 0.918] | 1.51 / 5.57 s | 0.808 |
| supervised encoder | **0.933** [0.899, 0.966] | **0.01** / 0.10 s | 0.899 |

Paired differences vs Jev: Terra +4.3pp [−0.5, +9.1], nano −3.8pp [−8.7, +1.0], encoder **+10.1pp [+5.3, +14.9]**.

### B1 — CLINC150 zero-shot (150 intents + `oos`, n=200)

| method | accuracy | median / p95 latency | conf. AUROC | `oos` recall |
|---|---|---|---|---|
| Jev | 0.870 | 0.43 / 0.74 s | **0.734** | 0.714 |
| gpt-5.4-nano | 0.795 | 0.88 / 1.50 s | **0.816** | 0.486 |
| GPT-5.6 Terra | 0.915 | 1.20 / 2.46 s | 0.670 | 0.800 |

### Cascades: escalate to Terra when the first stage is unsure

![cascade curves](figures/cascade_curves.png)

To reach Terra's own accuracy (within 1pp), the fraction of items that must be escalated to Terra:

| first stage | B1 escalation rate | B1 cross-fit rate | B0 escalation rate |
|---|---|---|---|
| Jev | **0.220** | 0.225 | 0.255 |
| gpt-5.4-nano | 0.485 | 0.435 | 0.442 |

Jev-first cascades reach frontier accuracy while sending roughly **half as much traffic** to the frontier model
as nano-first cascades. B1's pre-registered primary metric was this gap, Δ = R_nano − R_jev:
**Δ = +0.265, 95% CI [−0.530, +0.595] → pre-registered verdict: AMBIGUOUS** (point estimate passes the +0.10
threshold, but the interval includes 0). R is a min-over-thresholds statistic and is unstable under bootstrap;
the pre-registered cross-fit check (pick the threshold on one half, evaluate on the other) gives a consistent
Δ = +0.210. Treat the direction as suggestive, not established.

### The mechanism hypothesis failed

B0 suggested Jev's confidence separates right from wrong answers better than an LLM's (AUROC 0.853 vs 0.795).
B1 **reverses** it: Jev 0.734 vs nano 0.816 (paired diff −0.082, 95% CI [−0.187, +0.008]).

So the escalation savings above are **not** explained by better calibration. They come from Jev's higher
standalone zero-shot accuracy (0.870 vs 0.795) — fewer items need help in the first place. The B0 calibration
signal did not replicate and is best read as post-hoc noise. This also contradicts my own pre-registered
hypothesis H1, which is recorded as **unsupported**.

## What this means in practice

- **If you have labeled data**, train a small encoder. 0.933 accuracy, 9ms, no per-call cost, no vendor. It beat
  the frontier LLM by 8pp here, mostly because it learns the dataset's own labeling conventions
  (e.g. Banking77 files "Google Pay top-up failed" under `apple_pay_or_google_pay`, not `top_up_failed`) —
  conventions no zero-shot model can guess.
- **If you have no labeled data**, Jev is a reasonable zero-shot router: better accuracy and ~2x lower latency
  than a nano-class LLM at a fraction of the cost, and it is markedly better at `oos` ("none of these") than
  nano (0.714 vs 0.486).
- **Do not route on Jev's confidence assuming it is better calibrated than an LLM's.** On CLINC150 it was worse.
- **The vendor's 40–200x speed claim does not survive a nano-class baseline**: measured 0.43s vs 0.88s.

## Methods

- **Jev** via Vercel AI Gateway (`typesafe-ai/jev`, `POST /v4/ai/evaluation-model`), single `choice` question with
  one criterion per label; confidence from `providerMetadata.typesafe.confidence`. Measured cost
  $0.000071/call (77 labels) and $0.000106/call (151 labels).
- **LLMs** (`openai/gpt-5.4-nano-2026-03-17`, `openai/gpt-5.6-terra`) via Lightning AI, same prompt for both:
  all labels listed, JSON-only reply with a label and a self-reported confidence in [0,1].
  Lightning does not expose logprobs for these models, so **LLM confidence is verbalized**, which may understate
  what LLM calibration can do. Treat the AUROC comparison as "Jev vs verbalized LLM confidence".
- **Supervised encoder**: frozen `BAAI/bge-small-en-v1.5` CLS embeddings + scikit-learn logistic regression
  (C=10) trained on the full Banking77 train split (10,003 examples), on an M4 Max via MPS. B0 only — B1 is
  deliberately zero-shot, so no supervised baseline there.
- **Datasets**: Banking77 test split (CC-BY 4.0) and CLINC150 `data_full.json` test + oos_test (CC-BY-SA 3.0),
  both fetched from the authors' repos. Sampling seeds fixed (`seed=0` for B0, `Random(1)` for B1).
- **Latency** is wall-clock per API call from a single machine in the US west coast, Jev serially, LLMs at
  concurrency 6. It includes network time and is not a datacenter-local measurement.

## Deviations from pre-registration (full disclosure)

1. **B0 n reduced from 300 to 208.** Jev on the Vercel free tier is rate-limited to ~1 request/minute;
   finishing 300 would have taken hours. All methods are compared on the same 208 items (paired). Rate-limit
   failures are content-independent, and failed items were retried, never scored as wrong.
2. **The supervised encoder baseline was added after B0's pre-registration** was written.
3. **"Escalation rate at matched accuracy" was added post-hoc in B0.** It became B1's pre-registered primary
   metric precisely because it was post-hoc in B0.
4. B1 had no failures: 200/200 for all three methods.

## Limitations

- Small samples: 208 and 200 items. Differences under ~5pp are noise here.
- Both tasks are single-node intent classification. **Nothing here measures end-to-end agent workflows**, where
  a wrong routing decision propagates downstream and where decision latency may be a small share of total
  latency. That remains the open question.
- Jev is in early access and versioned; these numbers describe 2026-09-18 behavior via Vercel's gateway.
- One run per item; no repeat-determinism measurement (see 4esv/jev-eval for that).
- Prompts were not tuned per model; a prompt-tuned nano could close some of the accuracy gap.
- Verbalized LLM confidence (see Methods) is a ceiling caveat on the calibration comparison.

## Reproducing

```bash
pip install pandas numpy scikit-learn torch transformers matplotlib litai
export VERCEL_AI_API=...        # Vercel AI Gateway key (Jev)
# LLMs go through Lightning AI: litai reads ~/.lightning/credentials.json; set billing to your teamspace

python code/run_b0.py                                   # Jev + nano + Terra on Banking77
OMP_NUM_THREADS=1 python code/encoder_baseline.py       # supervised baseline (OMP flag avoids a macOS segfault)
python code/run_b1.py llm && python code/run_b1.py jev  # CLINC150 zero-shot
python code/analyze_b0.py && python code/analyze_b1.py  # verdicts exactly as pre-registered
python code/make_figure.py
```

Raw per-item results (prediction, confidence, latency, cost) are in `results/*.jsonl` — every number in this
report is recomputable from them.

## License

Code and report: MIT. Datasets keep their original licenses (see Methods).
