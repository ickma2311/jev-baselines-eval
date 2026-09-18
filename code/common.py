import os, re, json, time, subprocess, urllib.request
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def vercel_key():
    k = os.environ.get("VERCEL_AI_API")
    if not k:
        out = subprocess.run(["zsh", "-c", "source ~/.zshrc >/dev/null 2>&1; printf %s \"$VERCEL_AI_API\""], capture_output=True, text=True)
        k = out.stdout.strip()
    return k

def load_sample(n=300, seed=0):
    df = pd.read_csv(os.path.join(ROOT, "data/banking77_test.csv"))
    labels = sorted(df.category.unique())
    return df.sample(n=n, random_state=seed).reset_index(drop=True), labels

def human(label):
    return label.replace("_", " ")

JEV_URL = "https://ai-gateway.vercel.sh/v4/ai/evaluation-model"

def jev_classify(text, labels, key):
    body = {"state": f"Bank customer message: {text}",
            "questions": {"intent": {"type": "choice",
                                     "instructions": "Which intent best describes the customer's message?",
                                     "criteria": {l: human(l) for l in labels}}}}
    req = urllib.request.Request(JEV_URL, data=json.dumps(body).encode(), method="POST", headers={
        "Authorization": f"Bearer {key}", "Content-Type": "application/json",
        "ai-gateway-protocol-version": "0.0.1", "ai-gateway-auth-method": "api-key",
        "ai-evaluation-model-specification-version": "4", "ai-model-id": "typesafe-ai/jev"})
    t = time.time()
    with urllib.request.urlopen(req, timeout=60) as r:
        d = json.load(r)
    dt = time.time() - t
    a = d["answers"]["intent"]
    conf = d.get("providerMetadata", {}).get("typesafe", {}).get("confidence", {}).get("intent")
    cost = float(d.get("providerMetadata", {}).get("gateway", {}).get("cost", "nan"))
    return {"pred": a["choice"], "p_top": max(a["probabilities"].values()), "conf": conf, "latency": dt, "cost": cost,
            "in_tok": d.get("usage", {}).get("inputTokens")}

LLM_PROMPT = """Classify the bank customer message into exactly one intent label.
Allowed labels: {labels}

Message: {text}

Return JSON only: {{"label": "<one allowed label>", "confidence": <probability 0-1 that your label is correct>}}"""

def llm_classify(llm, text, labels):
    t = time.time()
    out = llm.chat(LLM_PROMPT.format(labels=", ".join(labels), text=text), max_tokens=2000)
    dt = time.time() - t
    m = re.search(r"\{.*\}", out, re.S)
    try:
        j = json.loads(m.group(0)); pred, conf = j.get("label"), float(j.get("confidence"))
    except Exception:
        pred, conf = None, None
    return {"pred": pred, "conf": conf, "latency": dt, "raw": out[:200]}
