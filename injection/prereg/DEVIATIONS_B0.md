# B0 deviations from PREREG_B0.md

Append-only. The pre-registration itself (sha256 `b49e012e…`, tag `prereg-b0`) is not edited.

## D1 — GPU changed from T4 to L4 (2026-09-22, before any B0 result existed)

**Pre-registered**: "两个复现都在 Modal 的单张 T4（16GB）上跑" [both replicas run on a single T4 (16 GB) on Modal] (section 4), budget table priced at T4.

**Changed to**: a single Modal L4 (24 GB).

**Why**: `decider-ai`'s own loader defaults to `torch.bfloat16` on CUDA
(`decider/infer.py`: `dtype = torch.float16 if mps else torch.bfloat16`). T4 is sm75 and has no
bfloat16 support. Honouring the T4 would have meant forcing fp16, i.e. running the model at a
precision its README does not specify — which conflicts with section 4's requirement that each system
is called through the interface its own README recommends. Changing the hardware keeps the model's
own default; changing the dtype would not.

**Effect on the endpoint**: none. The primary endpoint is a difference in decision rates between arms
on the same hardware; no latency claim is made in B0.

**Effect on the budget**: L4 is $0.80/h against T4's $0.59/h. At the estimated 0.3 GPU-h this moves
the estimate from about $0.28 to about $0.32, and the upper bound from $0.91 to about $1.12. Both
remain inside the $5 project cap and are drawn from Modal's free credit ($4.73 of $30 used this month
as of 2026-09-22), so real payment stays $0.

## Implementation notes (not deviations, recorded for the record)

- `Decider()` takes a path and has no `revision` argument, so the pinned revision
  `fa996cea58e1c1d8d1ab4d7124154f303b017f95` is materialized with
  `huggingface_hub.snapshot_download(repo, revision=...)` and the resulting directory is passed in.
  The pin is therefore still enforced. `OpenJev.from_pretrained` accepts `revision` directly.
- kotoba's config sets `max_state_tokens = 256`. The injected paragraph sits near the end of each
  ticket, so silent truncation would delete the treatment and produce a spurious zero lift. Every
  kotoba row records `state_tokens` and `state_truncated`; if any item truncates, that is reported
  rather than averaged over.
- The two replicas cannot share a Python environment (`decider-ai` requires `transformers>=5`,
  `typed-decisions` requires `>=4.56,<5`), so each runs in its own image. `typed-decisions` also
  requires Python >= 3.12.

## Implementation note — torch is not pinned by us

The first working image pinned `torch==2.5.1`. decider then failed at inference with
`torch._dynamo.exc.InternalTorchDynamoError` inside `transformers/utils/import_utils.py`
(`torch.compiler.is_exporting()`), an API that torch 2.5.1 does not have but transformers 5.x calls
from a compiled region. Both packages declare their own torch requirement (`decider-ai`: `torch`;
`typed-decisions`: `torch>=2.4`), so the pin was removed and each image now resolves the stack its
own package asks for. This keeps each replica on the dependency set its maintainers specify, which is
what section 4 of the pre-registration requires.
