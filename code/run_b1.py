"""Pilot B1 (see PREREG_B1.md): Jev vs nano vs Terra on CLINC150 zero-shot (n=200, seed 1).
Usage: python3 run_b1.py llm   -> nano + terra (parallel)
       python3 run_b1.py jev   -> Jev serially, retry with backoff until every item succeeds
Appends to results_b1.jsonl; resumable (skips (method, i) already present without error)."""
import sys, os, json, random, time, threading, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(__file__))
from common import ROOT, vercel_key, JEV_URL, llm_classify, LLM_PROMPT
import common

OUT = os.path.join(os.path.dirname(__file__), "results_b1.jsonl")
d = json.load(open(os.path.join(ROOT, "data/clinc150_full.json")))
pool = d["test"] + d["oos_test"]
items = random.Random(1).sample(pool, 200)
labels = sorted({l for _, l in d["test"]}) + ["oos"]
assert len(labels) == 151

common.LLM_PROMPT = LLM_PROMPT.replace("bank customer message", "virtual assistant user request").replace(
    "Allowed labels: {labels}", "Allowed labels: {labels}\n(use \"oos\" if the request matches none of the other labels)")

def crit(l):
    return "out of scope: the request does not match any other intent" if l == "oos" else l.replace("_", " ")

def jev_once(text, key):
    body = {"state": f"Virtual assistant user request: {text}",
            "questions": {"intent": {"type": "choice", "instructions": "Which intent best describes the user's request?",
                                     "criteria": {l: crit(l) for l in labels}}}}
    req = urllib.request.Request(JEV_URL, data=json.dumps(body).encode(), method="POST", headers={
        "Authorization": f"Bearer {key}", "Content-Type": "application/json",
        "ai-gateway-protocol-version": "0.0.1", "ai-gateway-auth-method": "api-key",
        "ai-evaluation-model-specification-version": "4", "ai-model-id": "typesafe-ai/jev"})
    t = time.time()
    with urllib.request.urlopen(req, timeout=60) as r:
        res = json.load(r)
    dt = time.time() - t
    a = res["answers"]["intent"]; pm = res.get("providerMetadata", {})
    return {"pred": a["choice"], "conf": pm.get("typesafe", {}).get("confidence", {}).get("intent"),
            "latency": dt, "cost": float(pm.get("gateway", {}).get("cost", "nan"))}

def done_set():
    s = set()
    if os.path.exists(OUT):
        for line in open(OUT):
            r = json.loads(line)
            if not r.get("error"): s.add((r["method"], r["i"]))
    return s

lock = threading.Lock()
def write(r):
    with lock, open(OUT, "a") as f: f.write(json.dumps(r) + "\n")

def run_llm():
    from litai import LLM
    models = {"nano": "openai/gpt-5.4-nano-2026-03-17", "terra": "openai/gpt-5.6-terra"}
    done = done_set()
    def one(method, i):
        if (method, i) in done: return
        text, y = items[i]
        r = None
        for attempt in range(3):
            try:
                r = llm_classify(LLM(model=models[method], billing="ickma2311-org/inference", max_retries=2), text, labels); break
            except Exception as e:
                r = {"pred": None, "conf": None, "latency": None, "call_failed": str(e)[:200]}; time.sleep(2 ** attempt)
        r.update(method=method, i=i, gold=y, correct=(r.get("pred") == y))
        write(r)
    for m in models:
        with ThreadPoolExecutor(6) as ex: list(ex.map(lambda i: one(m, i), range(len(items))))
        print(m, "done", flush=True)

def run_jev():
    key = vercel_key(); done = done_set()
    for i, (text, y) in enumerate(items):
        if ("jev", i) in done: continue
        attempt = 0
        while True:
            try:
                r = jev_once(text, key); break
            except urllib.error.HTTPError as e:
                if e.code != 429 and attempt >= 5:
                    r = {"pred": None, "conf": None, "latency": None, "error": f"HTTP {e.code}"}; break
            except Exception as e:
                if attempt >= 5:
                    r = {"pred": None, "conf": None, "latency": None, "error": str(e)[:200]}; break
            time.sleep(min(60, 2 ** min(attempt, 6))); attempt += 1
        r.update(method="jev", i=i, gold=y, correct=(r.get("pred") == y), attempts=attempt + 1)
        write(r)
        print(time.strftime("%H:%M:%S"), "jev", i, "attempts", attempt + 1, flush=True)

if __name__ == "__main__":
    {"llm": run_llm, "jev": run_jev}[sys.argv[1]]()
