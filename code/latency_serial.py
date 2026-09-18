"""Matched-condition latency: nano/Terra run SERIALLY (as Jev was), same 30 CLINC items."""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(__file__))
import run_b1 as b, common
from litai import LLM
out = []
for name, m in [("nano", "openai/gpt-5.4-nano-2026-03-17"), ("terra", "openai/gpt-5.6-terra")]:
    llm = LLM(model=m, billing="ickma2311-org/inference", max_retries=2)
    for i in range(30):
        r = common.llm_classify(llm, b.items[i][0], b.labels)
        out.append({"method": name, "i": i, "latency": r["latency"], "mode": "serial"})
        print(name, i, round(r["latency"], 2), flush=True)
json.dump(out, open(os.path.join(os.path.dirname(__file__), "latency_serial.json"), "w"))
