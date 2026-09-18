"""Analysis exactly as specified in PREREG_B1.md."""
import json, os, numpy as np, pandas as pd
_here = os.path.dirname(os.path.abspath(__file__))
P = next(p for p in [os.path.join(_here, "..", "results", "results_b1.jsonl"), os.path.join(_here, "results_b1.jsonl")] if os.path.exists(p))
d = pd.DataFrame([json.loads(l) for l in open(P)])
if "error" in d: d = d[d.error.isna()]                       # Jev rate-limit failures are retried, never scored
d = d.drop_duplicates(["method", "i"], keep="last")
W = d.pivot(index="i", columns="method", values="correct").astype(float)
C = d.pivot(index="i", columns="method", values="conf").astype(float).fillna(0.0)   # failed/unparsed -> conf 0
L = d.pivot(index="i", columns="method", values="latency").astype(float)
G = d.pivot(index="i", columns="method", values="gold")
W = W.dropna(); C = C.loc[W.index]; L = L.loc[W.index]
n = len(W); print(f"n (items with all 3 methods) = {n}")

def min_rate(first, w, c):
    """Smallest Terra-call rate s.t. cascade acc >= A_T - 0.01 (R=1 if unreachable)."""
    target = w["terra"].mean() - 0.01
    ts = np.unique(np.concatenate([c[first], [0.0, 1.01]]))
    best = 1.0
    for t in ts:
        esc = c[first] < t
        acc = np.where(esc, w["terra"], w[first]).mean()
        if acc >= target - 1e-12: best = min(best, esc.mean())
    return best

def delta(w, c):
    return min_rate("nano", w, c) - min_rate("jev", w, c)

def auroc(conf, correct):
    pos, neg = conf[correct == 1], conf[correct == 0]
    if len(pos) == 0 or len(neg) == 0: return np.nan
    return np.mean([(p > neg).mean() + 0.5 * (p == neg).mean() for p in pos])

w, c = W.reset_index(drop=True), C.reset_index(drop=True)
R_j, R_n = min_rate("jev", w, c), min_rate("nano", w, c)
D = R_n - R_j
rng = np.random.default_rng(0)
boot, boot_auc = [], {"jev-nano": [], "jev-terra": []}
for _ in range(2000):
    idx = rng.integers(0, n, n); wb, cb = w.iloc[idx].reset_index(drop=True), c.iloc[idx].reset_index(drop=True)
    boot.append(delta(wb, cb))
    a = {m: auroc(cb[m].values, wb[m].values) for m in ["jev", "nano", "terra"]}
    boot_auc["jev-nano"].append(a["jev"] - a["nano"]); boot_auc["jev-terra"].append(a["jev"] - a["terra"])
lo, hi = np.percentile(boot, [2.5, 97.5])

print("\n=== PRIMARY (preregistered) ===")
print(f"A_T (Terra alone) = {w.terra.mean():.3f}; target = {w.terra.mean()-0.01:.3f}")
print(f"R_jev = {R_j:.3f}   R_nano = {R_n:.3f}   Δ = R_nano − R_jev = {D:+.3f}  95% CI [{lo:+.3f}, {hi:+.3f}]")
verdict = "GO" if (D >= 0.10 and lo > 0) else ("KILL" if (D <= 0 or hi < 0.05) else "AMBIGUOUS")
print("VERDICT:", verdict)

print("\n=== SECONDARY (report only) ===")
for m in ["jev", "nano", "terra"]:
    print(f"{m:6s} acc {w[m].mean():.3f}  med_lat {L[m].median():.2f}s  p95 {L[m].quantile(.95):.2f}s  AUROC {auroc(c[m].values, w[m].values):.3f}")
for k, v in boot_auc.items():
    v = np.array(v)[~np.isnan(v)]
    print(f"AUROC diff {k}: point {np.mean(v):+.3f}  95% CI [{np.percentile(v,2.5):+.3f}, {np.percentile(v,97.5):+.3f}]")
# cross-fit Δ: choose t on one half, evaluate on the other
half = np.random.default_rng(2).permutation(n); A, B = half[: n // 2], half[n // 2:]
def pick_t(first, w, c):
    target = w["terra"].mean() - 0.01; best = (1.0, 1.01)
    for t in np.unique(np.concatenate([c[first], [0.0, 1.01]])):
        esc = c[first] < t
        if np.where(esc, w["terra"], w[first]).mean() >= target - 1e-12: best = min(best, (esc.mean(), t))
    return best[1]
def evalt(first, t, w, c):
    esc = c[first] < t; return esc.mean(), np.where(esc, w["terra"], w[first]).mean()
cf = {}
for f in ["jev", "nano"]:
    r1 = evalt(f, pick_t(f, w.iloc[A], c.iloc[A]), w.iloc[B], c.iloc[B]); r2 = evalt(f, pick_t(f, w.iloc[B], c.iloc[B]), w.iloc[A], c.iloc[A])
    cf[f] = ((r1[0] + r2[0]) / 2, (r1[1] + r2[1]) / 2)
    print(f"cross-fit {f}→terra: terra_rate {cf[f][0]:.3f}  acc {cf[f][1]:.3f}")
print(f"cross-fit Δ (rate) = {cf['nano'][0]-cf['jev'][0]:+.3f}   (acc jev−nano cascade {cf['jev'][1]-cf['nano'][1]:+.3f})")
jc = d[d.method == "jev"].cost.mean() if "cost" in d else float("nan")
print(f"Jev mean cost/call ${jc:.6f}")
oos = G.loc[W.index, "terra"] == "oos"
print("oos recall:", {m: round(W.loc[oos.values, m].mean(), 3) for m in ["jev", "nano", "terra"]}, f"(n_oos={int(oos.sum())})")
