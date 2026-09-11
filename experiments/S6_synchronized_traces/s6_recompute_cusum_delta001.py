"""Post-hoc audit: re-accumulate the external CUSUM on the committed traces at delta_P = 0.01.

Run on the three arms that share a trajectory -- 'full', 'no_swap' and 'frozen'. 'static' is excluded
on purpose: it is a different model class with a six-fold capacity deficit (docs/theory/
S6_causal_evidence.md section 8, divergence 5), so its evidence ceiling is not comparable with the
other three. The three retained arms differ only by which replacements were allowed to fire, which
is what makes the ceilings a decomposition rather than a comparison.

The campaign writes `a_refl` at `DELTA_P = 0.005`, the registry tolerance. The manuscript text
states 0.01, and `docs/theory/transfer_S1.md` open item 2 records the factor of two as unresolved --
"Factor 2 on theta*, three orders of magnitude on ARL_0 at lambda = 50". This script settles the
empirical half of that question without re-running a single simulation: the traces carry the raw
per-step error, so the accumulation is a pure function of committed data.

Definition. On the `full` arm, with p_0 calibrated on the 1000 pre-drift steps of the same run,

    S_t = max(0, S_{t-1} + e_t - p_0_hat - delta_P),   S_{-1} = 0,   t in [tau*, tau* + T_h)

and `S_max = max_t S_t` is the evidence ceiling: a monitor of threshold lambda fires on that run iff
`S_max >= lambda`. Reported per magnitude and per arm: median, q05 and q95 of `S_max`, and the
crossing rate at each audited lambda. `min_{Delta e} q05(S_max)` on the 'full' arm is the operational
threshold lambda_op(0.05) -- the largest threshold that still detects 95 % of runs at every magnitude
on the grid.

The Lindley recursion is evaluated in closed form, `S_t = M_t - min_{k<=t} M_k` with `M` the running
sum of the excess, which is exact and vectorised; the explicit recursion is run once at startup on a
random walk to certify the identity rather than trust it.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.dataset as ds
import pyarrow.parquet as pq
from joblib import Parallel, delayed

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from config import experiment_ssot as ssot  # noqa: E402

RESULTS_DIR = ssot.RESULTS_DIR / "S6_synchronized_traces"
AUDIT_DELTA_P = ssot.S6_AUDIT_DELTA_P
AUDIT_LAMBDAS = ssot.S6_AUDIT_LAMBDAS
WARMUP = ssot.S6_WARMUP_WINDOW
T_HORIZON = ssot.S6_T_HORIZON
ARMS = [a for a in ssot.S6_ARM_NAMES if a != "static"]   # full, no_swap, frozen -- one trajectory
REFERENCE_ARM = "full"
ENVELOPE_FLOOR = 0.20                          # R8's declared envelope floor for the lambda minimum
KEY_DELTA_E = [0.028, 0.194, 0.327, 0.498]     # grid floor, signal peak, transfer_S1 point, ceiling


def s_max(excess):
    """max_t of the reflected CUSUM fed `excess`. Lindley: S_t = M_t - min_{0<=k<=t} M_k, M_0 = 0."""
    m = np.concatenate(([0.0], np.cumsum(excess)))
    return float(np.max(m - np.minimum.accumulate(m)))


def _check_lindley():
    rng = np.random.default_rng(0)
    x = rng.normal(size=500) - 0.1
    s = peak = 0.0
    for v in x:
        s = max(0.0, s + v)
        peak = max(peak, s)
    assert abs(peak - s_max(x)) < 1e-12, (peak, s_max(x))


def partition(part, delta_p=AUDIT_DELTA_P, warmup=WARMUP, horizon=T_HORIZON):
    """{arm: (S_max per seed, p_0_hat per seed)} plus delta_e, for one magnitude partition.

    p_0 is calibrated per (arm, seed) on that trajectory's own pre-drift window. The three arms share
    their pre-drift history by construction -- they are forks of one run taken after the drift -- so
    the three estimates coincide, and the agreement check at the end of `main` uses that."""
    delta_e = float(Path(part).name.split("=", 1)[1])
    df = ds.dataset(str(part), format="parquet").to_table(
        columns=["arm", "seed", "t_rel", "err"],
        filter=ds.field("arm").isin(ARMS) & (ds.field("t_rel") >= -warmup)
        & (ds.field("t_rel") < horizon)).to_pandas().sort_values(["arm", "seed", "t_rel"])

    out = {}
    for arm, g_arm in df.groupby("arm", sort=False):
        peaks, p0 = [], []
        for _, g in g_arm.groupby("seed", sort=True):
            err = g["err"].to_numpy(dtype=np.float64)
            t_rel = g["t_rel"].to_numpy()
            p0_hat = float(err[t_rel < 0].mean())
            peaks.append(s_max(err[t_rel >= 0] - p0_hat - delta_p))
            p0.append(p0_hat)
        out[arm] = (np.asarray(peaks), np.asarray(p0))
    return delta_e, out


def main():
    _check_lindley()
    root = RESULTS_DIR / "data" / "traces.parquet"
    if not root.exists():
        raise SystemExit(f"[FATAL] {root} absent -- run s6_runner.py full first")
    parts = sorted(root.iterdir())

    res = Parallel(n_jobs=-1)(delayed(partition)(p) for p in parts)
    rows = [{
        "arm": arm, "delta_e": round(de, 6), "n": int(peaks.size),
        "p0_hat_median": round(float(np.median(p0)), 6),
        "s_max_median": round(float(np.median(peaks)), 3),
        "s_max_q05": round(float(np.quantile(peaks, 0.05)), 3),
        "s_max_q95": round(float(np.quantile(peaks, 0.95)), 3),
        **{f"cross_rate_lambda{lam:g}": round(float(np.mean(peaks >= lam)), 3)
           for lam in AUDIT_LAMBDAS},
        "delta_p": AUDIT_DELTA_P, "window": int(T_HORIZON),
    } for de, per_arm in res for arm, (peaks, p0) in per_arm.items()]

    table = pd.DataFrame.from_records(rows)
    table["arm"] = pd.Categorical(table["arm"], categories=ARMS, ordered=True)
    table = table.sort_values(["arm", "delta_e"], ignore_index=True)

    out_dir = RESULTS_DIR / "tables"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_all = out_dir / "cusum_delta001_quantiles_all_arms.csv"
    table.to_csv(out_all, index=False)
    ref = table[table.arm == REFERENCE_ARM].drop(columns=["arm"]).reset_index(drop=True)
    # The single-arm file predates this script's extension to three arms and is exactly the 'full'
    # slice of the table above. It is rewritten here so nothing on disk goes stale, not duplicated
    # for its own sake.
    out_ref = out_dir / "cusum_delta001_quantiles.csv"
    ref.assign(arm=REFERENCE_ARM).to_csv(out_ref, index=False)

    # p_0 recomputed here must agree with the e_pre the campaign wrote, or one of the two is wrong.
    runs = pq.read_table(RESULTS_DIR / "data" / "runs.parquet").to_pandas()
    campaign = runs[runs.arm.isin(ARMS)].groupby(["arm", "delta_e"])["e_pre"].median()
    audit = table.set_index([table.arm.astype(str), "delta_e"])["p0_hat_median"]
    drift = float((campaign.sort_index() - audit.sort_index()).abs().max())

    show = [c for c in table.columns if c.startswith(("s_max", "cross_rate"))]
    print(f"=== S6 CUSUM audit at delta_P = {AUDIT_DELTA_P} "
          f"(registry DELTA_P = {ssot.DELTA_P}) ===")
    print(f"arms {ARMS}, {int(table.n.sum())} runs, window [tau*, tau* + {T_HORIZON}), "
          f"p_0 on the {WARMUP} pre-drift steps")
    print(f"p_0 agreement with the campaign's e_pre column: max |diff| = {drift:.2e}")

    print(f"\n--- comparative summary at the key magnitudes "
          f"(lambda = {', '.join(f'{x:g}' for x in AUDIT_LAMBDAS)}) ---")
    grid = np.array(sorted(table.delta_e.unique()))
    for target in KEY_DELTA_E:
        de = float(grid[np.argmin(np.abs(grid - target))])
        sub = table[np.isclose(table.delta_e, de)]
        print(f"\n  Delta_e = {de:.6f}  (requested {target})")
        print("    " + sub[["arm"] + show].to_string(index=False).replace("\n", "\n    "))

    print("\n--- global spread of the S_max median over the grid ---")
    for arm in (REFERENCE_ARM, "frozen"):
        m = table.loc[table.arm == arm, ["delta_e", "s_max_median"]]
        lo, hi = m.s_max_median.min(), m.s_max_median.max()
        print(f"  {arm:8s} min {lo:8.3f} at Delta_e = {m.loc[m.s_max_median.idxmin(), 'delta_e']:.6f}"
              f" | max {hi:8.3f} at Delta_e = {m.loc[m.s_max_median.idxmax(), 'delta_e']:.6f}"
              f" | spread max/min = {hi / lo:6.2f}x")

    env = ref[ref.delta_e >= ENVELOPE_FLOOR]
    print(f"\nlambda_op(0.05) = min_Delta_e q05(S_max), arm '{REFERENCE_ARM}'")
    print(f"  full grid [{ref.delta_e.min():.4f}, {ref.delta_e.max():.4f}] = {ref.s_max_q05.min():.3f}"
          f"  at Delta_e = {ref.loc[ref.s_max_q05.idxmin(), 'delta_e']}")
    print(f"  envelope  [{ENVELOPE_FLOOR:.2f}, {ref.delta_e.max():.4f}] = {env.s_max_q05.min():.3f}"
          f"  at Delta_e = {env.loc[env.s_max_q05.idxmin(), 'delta_e']}")
    print(f"[INFO] wrote {out_all.relative_to(ssot.ROOT_DIR)} ({len(table)} rows)")
    print(f"[INFO] wrote {out_ref.relative_to(ssot.ROOT_DIR)} ({len(ref)} rows)")
    return table


if __name__ == "__main__":
    main()
