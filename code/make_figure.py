import json, os, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
_here = os.path.dirname(os.path.abspath(__file__))
RES = lambda n: next(p for p in [os.path.join(_here, "..", "results", n), os.path.join(_here, n), os.path.join("pilot", n)] if os.path.exists(p))
FIGDIR = os.path.join(_here, "..", "figures") if os.path.isdir(os.path.join(_here, "..", "figures")) else "report/figures"

def load(p):
    d = pd.DataFrame([json.loads(l) for l in open(p)])
    if "error" in d: d = d[d.error.isna()]
    d = d.drop_duplicates(["method", "i"], keep="last")
    W = d.pivot(index="i", columns="method", values="correct").astype(float)
    C = d.pivot(index="i", columns="method", values="conf").astype(float).fillna(0.0)
    W = W.dropna(); return W, C.loc[W.index]

def curve(first, W, C):
    pts = []
    for t in np.unique(np.concatenate([C[first].values, [0.0, 1.01]])):
        esc = C[first] < t
        pts.append((esc.mean(), np.where(esc, W["terra"], W[first]).mean()))
    p = pd.DataFrame(pts, columns=["rate", "acc"]).sort_values("rate")
    return p.groupby("rate").acc.max().reset_index()

fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
for ax, (name, path, extra) in zip(axes, [("B0: Banking77 (n=208, 77 labels)", RES("results_b0.jsonl"), True),
                                          ("B1: CLINC150 zero-shot (n=200, 151 labels)", RES("results_b1.jsonl"), False)]):
    W, C = load(path)
    for f, col in [("jev", "#c0392b"), ("nano", "#2c7fb8")]:
        c = curve(f, W, C); ax.plot(c.rate, c.acc, "-o", ms=3, color=col, label=f"{f} → terra cascade")
    ax.axhline(W.terra.mean(), ls="--", c="gray", lw=1, label=f"terra alone ({W.terra.mean():.3f})")
    if extra and "encoder" in W:
        ax.axhline(W.encoder.mean(), ls=":", c="green", lw=1.5, label=f"supervised encoder ({W.encoder.mean():.3f})")
    ax.set_title(name, fontsize=10); ax.set_xlabel("fraction of items escalated to Terra"); ax.set_ylabel("accuracy")
    ax.legend(fontsize=8); ax.grid(alpha=.3)
plt.tight_layout(); plt.savefig(os.path.join(FIGDIR, "cascade_curves.png"), dpi=160)
print("wrote", os.path.join(FIGDIR, "cascade_curves.png"))
