import json, os, numpy as np, pandas as pd
P = os.path.join(os.path.dirname(__file__), "results_b0.jsonl")
d = pd.DataFrame([json.loads(l) for l in open(P)]).drop_duplicates(["method", "i"], keep="last")
rng = np.random.default_rng(0)

def ci(x):
    x = np.asarray(x, float); b = [rng.choice(x, len(x)).mean() for _ in range(2000)]
    return x.mean(), np.percentile(b, 2.5), np.percentile(b, 97.5)

def auroc(conf, correct):
    c = pd.DataFrame({"c": conf, "y": correct}).dropna()
    pos, neg = c[c.y].c.values, c[~c.y].c.values
    if len(pos) == 0 or len(neg) == 0: return float("nan")
    return (np.mean([(p > neg).mean() + 0.5 * (p == neg).mean() for p in pos]))

W = d.pivot(index="i", columns="method", values="correct").astype(float)
FULL = W.copy()
if "jev" in W and W.jev.notna().sum() < len(W):   # paired comparison on items Jev completed
    W = W[W.jev.notna()]
    print(f"NOTE: restricted to {len(W)} items with valid Jev results (paired subset)")
C = d.pivot(index="i", columns="method", values="conf").astype(float).loc[W.index]
L = d.pivot(index="i", columns="method", values="latency").astype(float).loc[W.index]
print(f"n per method: {d.groupby('method').size().to_dict()}  errors: {d.get('error', pd.Series()).notna().groupby(d.method).sum().to_dict()}")
print("\nmethod  acc [95% CI]           med_lat  p95_lat  AUROC(conf)")
for m in ["jev", "nano", "terra", "encoder"]:
    if m not in W: continue
    a, lo, hi = ci(W[m].fillna(0))
    print(f"{m:6s}  {a:.3f} [{lo:.3f},{hi:.3f}]   {L[m].median():6.2f}s  {L[m].quantile(.95):6.2f}s  {auroc(C[m], W[m]==1):.3f}")
if "jev" in W: print(f"jev mean cost/call: ${d[d.method=='jev'].cost.mean():.6f}")

def cascade(first):
    rows = []
    for t in np.round(np.arange(0, 1.001, 0.05), 2):
        esc = (C[first] < t) | C[first].isna()
        acc = np.where(esc, W["terra"].fillna(0), W[first].fillna(0)).mean()
        rows.append((t, esc.mean(), acc))
    return pd.DataFrame(rows, columns=["t", "terra_rate", "acc"])

if all(m in W for m in ["jev", "nano", "terra"]):
    print("\nCascade curves (escalate to Terra when first-stage conf < t)")
    cj, cn = cascade("jev"), cascade("nano")
    parts = [cj.add_prefix("jev_"), cn[["terra_rate", "acc"]].add_prefix("nano_")]
    if "encoder" in W: ce = cascade("encoder"); parts.append(ce[["terra_rate", "acc"]].add_prefix("enc_"))
    print(pd.concat(parts, axis=1).to_string(index=False))
    best = lambda c: c[c.terra_rate <= 0.5].acc.max()
    print(f"\nbest acc @ terra_rate<=50%: jev→terra {best(cj):.3f}   nano→terra {best(cn):.3f}" + (f"   enc→terra {best(ce):.3f}" if "encoder" in W else "") + f"   terra alone {W['terra'].fillna(0).mean():.3f}")
    print(f"oracle upper bound (any of jev/terra right): {((W.jev==1)|(W.terra==1)).mean():.3f}")
    print(f"error overlap: P(terra wrong | jev wrong) = {(W.terra[W.jev==0]==0).mean():.3f}   P(terra wrong) = {(W.terra==0).mean():.3f}")

print("\nfull-300 accuracy (non-Jev):", {m: round(FULL[m].mean(), 3) for m in ["nano", "terra", "encoder"] if m in FULL})
diff = lambda a, b: ci(W[a] - W[b])
for a, b in [("nano", "jev"), ("terra", "jev"), ("encoder", "jev")]:
    m, lo, hi = diff(a, b); print(f"paired acc diff {a}-{b}: {m:+.3f} [{lo:+.3f},{hi:+.3f}]")
