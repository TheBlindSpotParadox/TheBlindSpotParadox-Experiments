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

`Delta_e_c = inf{Delta_e : q05(S_max) >= lambda}` is the opposite reading of the same curve: the
smallest magnitude at which the envelope becomes viable at a given threshold. It is reported on the
grid and by linear interpolation between the two bracketing points, with a seed-level bootstrap
interval. On the canonical grid the crossing at lambda = 15 falls in the gap between 0.0854 and
0.1409 and the grid answer is coarse; the refinement sweep (`s6_runner.py refine`) fills it.

Usage:  s6_recompute_cusum_delta001.py [data|data_refine|smoke]     (default: data)

The Lindley recursion is evaluated in closed form, `S_t = M_t - min_{k<=t} M_k` with `M` the running
sum of the excess, which is exact and vectorised; the explicit recursion is run once at startup on a
random walk to certify the identity rather than trust it.
"""
import json
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
CRITICAL_LAMBDA = ssot.S6_AUDIT_LAMBDAS[0]     # 15, the threshold Delta_e_c is defined against
BOOTSTRAP_SEED = 12345
N_BOOTSTRAP = 10_000


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


def delta_e_c(mags, q05, threshold=CRITICAL_LAMBDA):
    """(grid inf, linear interpolation) of inf{Delta_e : q05(S_max) >= threshold}.

    The grid value is the smallest magnitude whose q05 already reaches the threshold -- the literal
    infimum over the sampled set. The interpolated value reads the crossing between that point and
    its predecessor, and is NaN when the predecessor is missing or the pair does not bracket the
    threshold, because interpolating a non-crossing is invention. Both are NaN when no magnitude
    reaches the threshold."""
    mags, q05 = np.asarray(mags, dtype=np.float64), np.asarray(q05, dtype=np.float64)
    hit = np.flatnonzero(q05 >= threshold)
    if hit.size == 0:
        return np.nan, np.nan
    i = int(hit[0])
    grid = float(mags[i])
    if i == 0 or not (q05[i - 1] < threshold <= q05[i]):
        return grid, np.nan
    w = (threshold - q05[i - 1]) / (q05[i] - q05[i - 1])
    return grid, float(mags[i - 1] + w * (mags[i] - mags[i - 1]))


def bootstrap_delta_e_c(by_delta, threshold=CRITICAL_LAMBDA, seed=BOOTSTRAP_SEED,
                        n_boot=N_BOOTSTRAP):
    """Seed-level bootstrap of Delta_e_c, each magnitude's block resampled independently."""
    mags = sorted(by_delta)
    rng = np.random.default_rng(seed)
    q05 = np.empty((n_boot, len(mags)))
    for j, de in enumerate(mags):
        v = by_delta[de]
        q05[:, j] = np.quantile(v[rng.integers(0, v.size, size=(n_boot, v.size))], 0.05, axis=1)
    reps = np.array([delta_e_c(mags, row, threshold) for row in q05])
    point = delta_e_c(mags, [np.quantile(by_delta[de], 0.05) for de in mags], threshold)

    def summary(estimate, col):
        ok = col[np.isfinite(col)]
        return {"estimate": None if np.isnan(estimate) else round(float(estimate), 6),
                "ci_lo_2p5": round(float(np.quantile(ok, 0.025)), 5) if ok.size else None,
                "ci_hi_97p5": round(float(np.quantile(ok, 0.975)), 5) if ok.size else None,
                "fraction_no_crossing": round(float(np.mean(~np.isfinite(col))), 5)}

    return {"threshold": float(threshold),
            "grid": summary(point[0], reps[:, 0]),
            "interpolated": summary(point[1], reps[:, 1]),
            "n_bootstrap": int(n_boot), "bootstrap_seed": int(seed),
            "magnitudes": [round(m, 6) for m in mags],
            "q05_per_magnitude": [round(float(np.quantile(by_delta[de], 0.05)), 4) for de in mags],
            "scheme": "seed-level, block resampled per magnitude"}


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


def main(which="data"):
    _check_lindley()
    base = RESULTS_DIR / which
    root = base / "traces.parquet"
    if not root.exists():
        raise SystemExit(f"[FATAL] {root} absent -- run s6_runner.py first")
    parts = sorted(root.iterdir())
    suffix = "" if which == "data" else f"_{which}"

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
    out_all = out_dir / f"cusum_delta001_quantiles_all_arms{suffix}.csv"
    table.to_csv(out_all, index=False)
    ref = table[table.arm == REFERENCE_ARM].drop(columns=["arm"]).reset_index(drop=True)
    # The single-arm file predates this script's extension to three arms and is exactly the 'full'
    # slice of the table above. It is rewritten here so nothing on disk goes stale, not duplicated
    # for its own sake.
    out_ref = out_dir / f"cusum_delta001_quantiles{suffix}.csv"
    ref.assign(arm=REFERENCE_ARM).to_csv(out_ref, index=False)

    # p_0 recomputed here must agree with the e_pre the campaign wrote, or one of the two is wrong.
    runs = pq.read_table(base / "runs.parquet").to_pandas()
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
    # On a wide grid, report the four declared landmarks by nearest match. On a narrow one -- the
    # refinement sweep spans 0.05 in Delta_e -- every landmark collapses onto the same one or two
    # points, so the whole grid is printed instead of four copies of its endpoints.
    targets = KEY_DELTA_E if grid.size > 8 else grid.tolist()
    for target in targets:
        de = float(grid[np.argmin(np.abs(grid - target))])
        sub = table[np.isclose(table.delta_e, de)]
        print(f"\n  Delta_e = {de:.6f}  (requested {target})")
        print("    " + sub[["arm"] + show].to_string(index=False).replace("\n", "\n    "))

    print("\n--- global spread of the S_max median over the grid ---")
    for arm in [a for a in (REFERENCE_ARM, "frozen") if (table.arm == a).any()]:
        m = table.loc[table.arm == arm, ["delta_e", "s_max_median"]]
        lo, hi = m.s_max_median.min(), m.s_max_median.max()
        print(f"  {arm:8s} min {lo:8.3f} at Delta_e = {m.loc[m.s_max_median.idxmin(), 'delta_e']:.6f}"
              f" | max {hi:8.3f} at Delta_e = {m.loc[m.s_max_median.idxmax(), 'delta_e']:.6f}"
              f" | spread max/min = {hi / lo:6.2f}x")

    by_delta = {float(de): per_arm[REFERENCE_ARM][0] for de, per_arm in res
                if REFERENCE_ARM in per_arm}
    dec = bootstrap_delta_e_c(by_delta)
    out_json = out_dir / f"delta_e_c{suffix}.json"
    out_json.write_text(json.dumps({"source": str(base.relative_to(ssot.ROOT_DIR)),
                                    "arm": REFERENCE_ARM, "delta_p": AUDIT_DELTA_P,
                                    "window": int(T_HORIZON), "delta_e_c": dec},
                                   indent=2, sort_keys=True, default=float) + "\n", encoding="utf-8")

    print(f"\nDelta_e_c = inf{{Delta_e : q05(S_max) >= {dec['threshold']:g}}}, arm "
          f"'{REFERENCE_ARM}', {dec['n_bootstrap']} bootstrap draws, seed {dec['bootstrap_seed']}")
    print(f"  q05 per magnitude: "
          + ", ".join(f"{m:.4f}:{q:.2f}" for m, q in zip(dec["magnitudes"], dec["q05_per_magnitude"])))
    for kind in ("grid", "interpolated"):
        d = dec[kind]
        est = "none" if d["estimate"] is None else f"{d['estimate']:.5f}"
        lo = "n/a" if d["ci_lo_2p5"] is None else f"{d['ci_lo_2p5']:.5f}"
        hi = "n/a" if d["ci_hi_97p5"] is None else f"{d['ci_hi_97p5']:.5f}"
        print(f"  {kind:13s} estimate {est}  CI95 [{lo}, {hi}]  "
              f"replicates with no crossing: {d['fraction_no_crossing']:.4f}")

    env = ref[ref.delta_e >= ENVELOPE_FLOOR]
    print(f"\nlambda_op(0.05) = min_Delta_e q05(S_max), arm '{REFERENCE_ARM}'")
    print(f"  full grid [{ref.delta_e.min():.4f}, {ref.delta_e.max():.4f}] = {ref.s_max_q05.min():.3f}"
          f"  at Delta_e = {ref.loc[ref.s_max_q05.idxmin(), 'delta_e']}")
    if env.empty:
        print(f"  envelope  [{ENVELOPE_FLOOR:.2f}, ...] : no magnitude on this grid reaches the floor")
    else:
        print(f"  envelope  [{ENVELOPE_FLOOR:.2f}, {ref.delta_e.max():.4f}] = {env.s_max_q05.min():.3f}"
              f"  at Delta_e = {env.loc[env.s_max_q05.idxmin(), 'delta_e']}")
    print(f"[INFO] wrote {out_all.relative_to(ssot.ROOT_DIR)} ({len(table)} rows)")
    print(f"[INFO] wrote {out_ref.relative_to(ssot.ROOT_DIR)} ({len(ref)} rows)")
    print(f"[INFO] wrote {out_json.relative_to(ssot.ROOT_DIR)}")
    return table


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data")
