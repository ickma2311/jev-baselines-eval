**Reframe it.** The ~2.2× ratio is a useful observation about the tested API paths, but it does not establish a model-speed advantage. I verified the medians: **0.42295 s for Jev and 0.92363 s for nano; ratio 2.184**. No files were modified.

**1. What the number supports—and what A/B establish**

It supports: **the recorded median call duration was approximately 54% shorter for the Jev configuration on these 30 items**, under the respective clients, providers, and measurement conditions. This is a ratio of medians, not a typical paired speedup or a prediction for another deployment.

Drop claims that:

- Jev’s **model computation** is 2.2× faster or more efficient.
- The ratio generalizes across providers, locations, load, or workloads.
- These observations establish that serving overhead dominates.
- This comparison disproves the vendor’s speed claims under different conditions.

A narrows the explanation, but “network is <10%” is too strong: **47–65 ms of handshake alone is about 11–15% of 423 ms**. More importantly, curl measures the client-facing connection; it does not isolate gateway-to-backend transit or internal routing. Similar handshake timings make external connection establishment an unlikely explanation for the roughly **501 ms gap**, assuming the probes represent the actual requests.

B establishes **no detectable positive payload-size effect in this tiny sample**. It is consistent with a large latency floor, but does not identify its source or quantify its share:

- Queueing, dynamic batching, routing, or warm/cold state could mask a payload effect.
- Prompt caching could reduce the effective difference in computation.
- Model computation itself can have a substantial floor; short-input prefill need not scale proportionally with token count.
- Generating a short answer can contribute relatively fixed latency.
- Client initialization, extra requests, retries, or response processing could contribute.

Also, the tests change task/output requirements alongside input size—boolean versus choice, and “ok” versus classification JSON. They are useful probes, not isolated input-length experiments. **The larger requests being faster at n=3 is not evidence that larger inputs reduce latency.**

**2. Keep it with this framing**

I would accept:

> On the same 30 CLINC150 items, collected in separate serial runs, the recorded median call duration was 0.423 s for Jev through Vercel using urllib and 0.924 s for nano through Lightning using litai—a 2.18× ratio of medians. This compares the tested client-and-service configurations, not isolated model inference speed. Jev timing excludes failed attempts and backoff; nano timing wraps the SDK call and may include internal retries. The result does not establish throughput or a provider-independent speed advantage.

Replace the README’s **“the ratio is the point”** assertion: the ratio is also configuration-specific. Apply that qualification to the summary and practical takeaway, not just the limitations.

**No new measurement is required to retain this explicitly historical, descriptive statement.** Before retaining a prominent “lower per-call latency” deployment claim, I would require one small instrumentation check: verify comparable timing boundaries and identify SDK initialization, ancillary requests, and retries. More repetitions alone will not resolve those issues.

**3. The biggest actionable confound: what happens inside `llm.chat`**

The code reveals concrete asymmetries:

- [Jev’s timer](/Users/chaoma/projects/research/jev_workflow/report/code/run_b1.py:24) starts after request construction and includes reading/parsing the response. Its retry loop is outside that timer.
- [Nano’s timer](/Users/chaoma/projects/research/jev_workflow/report/code/common.py:49) includes prompt formatting and everything inside `llm.chat`, but excludes the final classification JSON parsing.
- [The serial script](/Users/chaoma/projects/research/jev_workflow/report/code/latency_serial.py:7) creates one reusable client per model with `max_retries=2`. Internal retries are therefore potentially inside the recorded duration; Lightning documents this [retry behavior](https://lightning.ai/docs/litai/features/fallback-retry).
- The currently installed litai implementation loads its backend in a background thread and waits for initialization inside `chat`. Thus, constructing the object outside the timer does **not** guarantee initialization is excluded. This is a first-call concern, not sufficient by itself to explain the median gap. The historical installed version is not pinned here.

**Streaming is not an evident mismatch:** Jev reads the complete response, and the current litai default is `stream=False`. Both measure completion, not time to first token. Switching nano to first-token timing would answer a different question; routing requires a usable decision.

The cheapest useful test is:

1. Warm one reusable nano client, recording initialization separately.
2. Instrument roughly **10–20 real classification calls** with `perf_counter`: outer `chat` duration, each HTTP request’s duration through full body consumption, request count, status, and retries. Record timings without credentials.
3. Compare outer duration with the full set of HTTP spans. Milliseconds of residual overhead cannot explain a ~501 ms gap; hundreds of milliseconds warrant investigation.
4. If substantial overhead appears, alternate SDK calls with raw HTTP calls to **the exact same Lightning endpoint**, matching payload, authentication/billing route, output limits, streaming mode, and connection reuse. Do not substitute another provider.

That test separates client-side contribution from remote-path time cheaply. Even if client overhead is negligible, the remaining gap still combines provider serving behavior and model execution; **it does not become an isolated model benchmark**.
