# Run with: OMP_NUM_THREADS=1 KMP_DUPLICATE_LIB_OK=TRUE (torch+sklearn OpenMP segfault on macOS otherwise)
"""Supervised baseline: frozen bge-small embeddings + logistic regression, trained on Banking77 train.
Scores the same n=300 test sample as B0 and appends rows with method='encoder' to results_b0.jsonl."""
import os, sys, json, time, numpy as np, pandas as pd, torch
from transformers import AutoTokenizer, AutoModel
from sklearn.linear_model import LogisticRegression
sys.path.insert(0, os.path.dirname(__file__))
from common import load_sample, ROOT

dev = "mps" if torch.backends.mps.is_available() else "cpu"
name = "BAAI/bge-small-en-v1.5"
tok, mdl = AutoTokenizer.from_pretrained(name), AutoModel.from_pretrained(name).to(dev).eval()

@torch.no_grad()
def embed(texts, bs=128):
    out = []
    for i in range(0, len(texts), bs):
        b = tok(texts[i:i+bs], padding=True, truncation=True, max_length=64, return_tensors="pt").to(dev)
        h = mdl(**b).last_hidden_state[:, 0]
        out.append(torch.nn.functional.normalize(h, dim=-1).cpu().numpy())
    return np.vstack(out)

tr = pd.read_csv(os.path.join(ROOT, "data/banking77_train.csv"))
te, labels = load_sample(300)
t0 = time.time(); Xtr = embed(tr.text.tolist()); print(f"embedded {len(tr)} train in {time.time()-t0:.1f}s")
clf = LogisticRegression(C=10, max_iter=3000).fit(Xtr, tr.category)

rows = []
for i, (text, y) in enumerate(zip(te.text, te.category)):
    t = time.time(); p = clf.predict_proba(embed([text]))[0]; dt = time.time() - t   # per-item latency, batch=1
    k = int(p.argmax())
    rows.append(dict(method="encoder", i=i, gold=y, pred=clf.classes_[k], conf=float(p[k]), latency=dt, correct=clf.classes_[k] == y))
out = os.path.join(os.path.dirname(__file__), "results_b0.jsonl")
kept = [l for l in open(out) if json.loads(l)["method"] != "encoder"]
open(out, "w").write("".join(kept) + "".join(json.dumps(r) + "\n" for r in rows))
print("encoder acc", np.mean([r["correct"] for r in rows]), "median latency", np.median([r["latency"] for r in rows]))
