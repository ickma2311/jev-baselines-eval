"""Pilot B0: Jev vs nano vs Terra on Banking77 (n=300). Resumable: appends to pilot/results_b0.jsonl."""
import sys, os, json, threading
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(__file__))
from common import *
from litai import LLM

OUT = os.path.join(os.path.dirname(__file__), "results_b0.jsonl")
df, labels = load_sample(300)
done = set()
if os.path.exists(OUT):
    for line in open(OUT):
        r = json.loads(line)
        if not r.get("error"): done.add((r["method"], r["i"]))   # failures are retried on the next run
lock = threading.Lock()
key = vercel_key()
MODELS = {"nano": "openai/gpt-5.4-nano-2026-03-17", "terra": "openai/gpt-5.6-terra"}

def run(method, i):
    if (method, i) in done: return
    text, y = df.text[i], df.category[i]
    for attempt in range(8):
        try:
            if method == "jev":
                r = jev_classify(text, labels, key)
            else:
                r = llm_classify(LLM(model=MODELS[method], billing="ickma2311-org/inference", max_retries=2), text, labels)
            break
        except Exception as e:
            r = {"pred": None, "conf": None, "latency": None, "error": str(e)[:200]}
            time.sleep(min(60, 2 ** attempt))
    r.update(method=method, i=int(i), gold=y, correct=(r.get("pred") == y))
    with lock:
        with open(OUT, "a") as f: f.write(json.dumps(r) + "\n")

for method, workers in [("jev", 1), ("nano", 6), ("terra", 6)]:
    with ThreadPoolExecutor(workers) as ex:
        list(ex.map(lambda i: run(method, i), range(len(df))))
    print(method, "done", flush=True)
