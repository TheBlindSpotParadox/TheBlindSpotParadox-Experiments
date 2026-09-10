"""Post-hoc audit: re-accumulate the external CUSUM on the committed traces at delta_P = 0.01.

The campaign writes `a_refl` at `DELTA_P = 0.005`, the registry tolerance. The manuscript text
states 0.01, and `docs/theory/transfer_S1.md` open item 2 records the factor of two as unresolved --
"Factor 2 on theta*, three orders of magnitude on ARL_0 at lambda = 50". This script settles the
empirical half of that question without re-running a single simulation: the traces carry the raw
per-step error, so the accumulation is a pure function of committed data.

Definition. On the `full` arm, with p_0 calibrated on the 1000 pre-drift steps of the same run,

    S_t = max(0, S_{t-1} + e_t - p_0_hat - delta_P),   S_{-1} = 0,   t in [tau*, tau* + T_h)

and `S_max = max_t S_t` is the evidence ceiling: a monitor of threshold lambda fires on that run iff
`S_max >= lambda`. Reported per magnitude: median, q05 and q95 of `S_max`, and the crossing rate at
each audited lambda. `min_{Delta e} q05(S_max)` is the operational threshold lambda_op(0.05) -- the
largest threshold that still detects 95 % of runs at every magnitude on the grid.

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
ARM = "full"
ENVELOPE_FLOOR = 0.20                          # R8's declared envelope floor for the lambda minimum


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
    """(delta_e, S_max per seed, p_0_hat per seed) for one magnitude partition."""
    delta_e = float(Path(part).name.split("=", 1)[1])
    df = ds.dataset(str(part), format="parquet").to_table(
        columns=["arm", "seed", "t_rel", "err"],
        filter=(ds.field("arm") == ARM) & (ds.field("t_rel") >= -warmup)
        & (ds.field("t_rel") < horizon)).to_pandas().sort_values(["seed", "t_rel"])

    peaks, p0 = [], []
    for _, g in df.groupby("seed", sort=True):
        err = g["err"].to_numpy(dtype=np.float64)
        t_rel = g["t_rel"].to_numpy()
        p0_hat = float(err[t_rel < 0].mean())
        peaks.append(s_max(err[t_rel >= 0] - p0_hat - delta_p))
        p0.append(p0_hat)
    return delta_e, np.asarray(peaks), np.asarray(p0)


def main():
    _check_lindley()
    root = RESULTS_DIR / "data" / "traces.parquet"
    if not root.exists():
        raise SystemExit(f"[FATAL] {root} absent -- run s6_runner.py full first")
    parts = sorted(root.iterdir())

    res = sorted(Parallel(n_jobs=-1)(delayed(partition)(p) for p in parts))
    rows = [{
        "delta_e": round(de, 6), "n": int(peaks.size),
        "p0_hat_median": round(float(np.median(p0)), 6),
        "s_max_median": round(float(np.median(peaks)), 3),
        "s_max_q05": round(float(np.quantile(peaks, 0.05)), 3),
        "s_max_q95": round(float(np.quantile(peaks, 0.95)), 3),
        **{f"cross_rate_lambda{lam:g}": round(float(np.mean(peaks >= lam)), 3)
           for lam in AUDIT_LAMBDAS},
        "delta_p": AUDIT_DELTA_P, "window": int(T_HORIZON), "arm": ARM,
    } for de, peaks, p0 in res]
    table = pd.DataFrame.from_records(rows)

    out = RESULTS_DIR / "tables" / "cusum_delta001_quantiles.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(out, index=False)

    # p_0 recomputed here must agree with the e_pre the campaign wrote, or one of the two is wrong.
    runs = pq.read_table(RESULTS_DIR / "data" / "runs.parquet").to_pandas()
    ref = runs[runs.arm == ARM].groupby("delta_e")["e_pre"].median().to_numpy()
    drift = float(np.abs(np.sort(ref) - table.p0_hat_median.to_numpy()).max())

    env = table[table.delta_e >= ENVELOPE_FLOOR]
    print(f"=== S6 CUSUM audit at delta_P = {AUDIT_DELTA_P} "
          f"(registry DELTA_P = {ssot.DELTA_P}) ===")
    print(f"arm '{ARM}', {int(table.n.sum())} runs, window [tau*, tau* + {T_HORIZON}), "
          f"p_0 on the {WARMUP} pre-drift steps")
    print(table.drop(columns=["delta_p", "window", "arm"]).to_string(index=False))
    print(f"\np_0 agreement with the campaign's e_pre column: max |diff| = {drift:.2e}")
    print(f"lambda_op(0.05) = min_Delta_e q05(S_max)")
    print(f"  full grid [{table.delta_e.min():.4f}, {table.delta_e.max():.4f}] = "
          f"{table.s_max_q05.min():.3f}  at Delta_e = {table.loc[table.s_max_q05.idxmin(), 'delta_e']}")
    print(f"  envelope  [{ENVELOPE_FLOOR:.2f}, {table.delta_e.max():.4f}] = "
          f"{env.s_max_q05.min():.3f}  at Delta_e = {env.loc[env.s_max_q05.idxmin(), 'delta_e']}")
    for lam in AUDIT_LAMBDAS:
        col = f"cross_rate_lambda{lam:g}"
        print(f"  crossing rate at lambda = {lam:g}: min {table[col].min():.3f}, "
              f"max {table[col].max():.3f}, envelope min {env[col].min():.3f}")
    print(f"[INFO] wrote {out.relative_to(ssot.ROOT_DIR)}")
    return table


if __name__ == "__main__":
    main()
