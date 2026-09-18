"""Rule out client-side overhead: compare the outer llm.chat() duration against the
actual HTTP span(s) it performs (urllib3 level), per the reviewer's requested check."""
import sys, os, json, time, statistics as st
sys.path.insert(0, os.path.dirname(__file__))
import run_b1 as b, common
import urllib3
from litai import LLM

spans = []
_orig = urllib3.poolmanager.PoolManager.urlopen
def patched(self, method, url, *a, **kw):
    t = time.perf_counter(); r = _orig(self, method, url, *a, **kw)
    try: _ = r.data                      # force full body read inside the span
    except Exception: pass
    spans.append({"method": method, "url": str(url)[:60], "status": getattr(r, "status", None),
                  "dt": time.perf_counter() - t})
    return r
urllib3.poolmanager.PoolManager.urlopen = patched

llm = LLM(model="openai/gpt-5.4-nano-2026-03-17", billing="ickma2311-org/inference", max_retries=2)
t = time.perf_counter(); llm.chat("Reply with exactly: ok", max_tokens=2000); warm = time.perf_counter() - t
print(f"warm-up call (init included): {warm:.3f}s, http spans {len(spans)}", flush=True)

rows = []
for i in range(12):
    spans.clear()
    t = time.perf_counter(); common.llm_classify(llm, b.items[i][0], b.labels); outer = time.perf_counter() - t
    http = sum(s["dt"] for s in spans)
    rows.append({"i": i, "outer": outer, "http_sum": http, "n_http": len(spans),
                 "statuses": [s["status"] for s in spans], "overhead": outer - http})
    print(f"  item {i}: outer {outer:.3f}s  http {http:.3f}s  ({len(spans)} req)  client overhead {outer-http:+.3f}s", flush=True)
med = lambda k: st.median([r[k] for r in rows])
print(f"\nMEDIAN outer {med('outer'):.3f}s | http {med('http_sum'):.3f}s | client overhead {med('overhead'):+.3f}s | requests/call {med('n_http')}")
json.dump({"warmup_s": warm, "rows": rows}, open(os.path.join(os.path.dirname(__file__), "latency_instrument.json"), "w"), indent=1)
