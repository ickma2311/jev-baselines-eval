import json, os, sys, numpy as np, pandas as pd
_here = os.path.dirname(os.path.abspath(__file__))
P = sys.argv[1] if len(sys.argv) > 1 else next(   # pass a path to analyze your own rerun
    p for p in [os.path.join(_here, "..", "results", "results_b0.jsonl"), os.path.join(_here, "results_b0.jsonl")] if os.path.exists(p))
print(f"input: {P}")
d = pd.DataFrame([json.loads(l) for l in open(P)]).drop_duplicates(["method", "i"], keep="last")
rng = np.random.default_rng(0)

def ci(x, seed=0):                      # fresh RNG per comparison -> deterministic, order-independent
    r = np.random.default_rng(seed)
    x = np.asarray(x, float); b = [r.choice(x, len(x)).mean() for _ in range(2000)]
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

print("\n=== extra paired CIs quoted in the report ===")
for a, b in [("encoder", "terra"), ("encoder", "jev"), ("terra", "jev"), ("nano", "jev")]:
    if a in W and b in W:
        m, lo, hi = ci(W[a] - W[b]); print(f"  {a}-{b}: {100*m:+.2f}pp [{100*lo:+.2f}, {100*hi:+.2f}]")
print("\n=== B0 preregistered verdict (PREREG_B0.md) ===")
k1 = (W.nano.mean() - W.jev.mean() >= -0.03) and (L.nano.median() <= 2 * L.jev.median())
bj = cascade("jev"); bn = cascade("nano"); best = lambda c: c[c.terra_rate <= 0.5].acc.max()
k2 = (best(bj) - best(bn)) < 0.02
go = (best(bj) >= W.terra.mean() - 0.01) and (best(bj) - best(bn) >= 0.02)
print(f"  K1 (nano within 3pp AND latency <=2x): {k1}  [acc diff {100*(W.nano.mean()-W.jev.mean()):+.1f}pp, latency {L.nano.median()/L.jev.median():.2f}x]")
print(f"  K2 (jev cascade not >2pp over nano cascade): {k2}  [{100*(best(bj)-best(bn)):+.1f}pp]")
print(f"  VERDICT: {'KILL' if (k1 and k2) else ('GO' if go else 'AMBIGUOUS')}")
