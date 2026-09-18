"""Isolate per-call overhead from payload size and from network, for both provider paths."""
import sys, os, time, json, urllib.request, statistics as st
sys.path.insert(0, os.path.dirname(__file__))
import run_b1 as b, common
from litai import LLM
key = common.vercel_key(); N = 10
def rep(f, n=N):
    xs = []
    for k in range(n):
        for attempt in range(7):
            try:
                t = time.time(); f(); xs.append(time.time() - t); break
            except Exception:
                time.sleep(min(60, 2 ** attempt))
        print(".", end="", flush=True)
    return xs
def jev_min():
    body = {"state": "ok", "questions": {"q": {"type": "boolean", "instructions": "Is this fine?"}}}
    req = urllib.request.Request(common.JEV_URL, data=json.dumps(body).encode(), method="POST", headers={
        "Authorization": f"Bearer {key}", "Content-Type": "application/json", "ai-gateway-protocol-version": "0.0.1",
        "ai-gateway-auth-method": "api-key", "ai-evaluation-model-specification-version": "4", "ai-model-id": "typesafe-ai/jev"})
    urllib.request.urlopen(req, timeout=60).read()
llm = LLM(model="openai/gpt-5.4-nano-2026-03-17", billing="ickma2311-org/inference", max_retries=2)
out = {}
for name, f in [("jev_minimal", jev_min), ("jev_real_151labels", lambda: b.jev_once(b.items[0][0], key)),
                ("nano_minimal", lambda: llm.chat("Reply with exactly: ok", max_tokens=2000)),
                ("nano_real_151labels", lambda: common.llm_classify(llm, b.items[0][0], b.labels))]:
    xs = rep(f); out[name] = xs
    print(f"\n{name}: median {st.median(xs):.3f}s  min {min(xs):.3f}  max {max(xs):.3f}  n={len(xs)}", flush=True)
json.dump(out, open(os.path.join(os.path.dirname(__file__), "latency_breakdown.json"), "w"))
