"""Envelope statistics of stream S6: is the operating point a knife edge, and is argmax stable?

Three questions, all answered on committed artifacts. No simulation, no new dependency.

1. `lambda_op_bootstrap`. The operational threshold `lambda_op(0.05) = min_{Delta_e in E} q05(S_max)`
   is a MINIMUM of QUANTILES over a grid: both operations are order statistics, so the point estimate
   carries no standard error of its own and a value of 15.2 against a candidate threshold of 15 says
   nothing until it is resampled. Seed-level bootstrap, blocks per magnitude, 10 000 replicates.

   The specification reads "block per magnitude", which is implemented as the primary estimate:
   each magnitude's 100 seeds are resampled independently. That breaks the seed pairing across
   magnitudes, and the pairing is real -- every magnitude reuses the same seed pool, so runs sharing
   a seed share their entire pre-drift trajectory and their `e_pre`. The paired variant is therefore
   computed alongside under `paired_across_magnitudes`, resampling the seed INDEX once per replicate
   and reading every magnitude at those seeds. The two bracket the answer; the decision rules should
   be read against the primary and checked against the secondary.

2. `crossing_counts`. Integer counts, not rates: at `lambda = 50` on the envelope the events are so
   rare that a rate of 0.01 is one run, and an interval computed as if it were a proportion of a
   large sample would be nonsense. Fisher's exact test of homogeneity on the 2 x C table decides
   whether the magnitudes may be pooled at all; the Clopper-Pearson interval on the aggregate is
   emitted ONLY if that test fails to reject, because pooling a heterogeneous table is how a
   structural effect gets averaged into a comfortable number.

   Fisher for a 2 x C table is not in scipy (which stops at 2 x 2), so it is enumerated exactly here:
   with column totals `n_j` and `k` successes overall, `P(T) = prod C(n_j, t_j) / C(N, k)` and the
   p-value is the total probability of every table at most as probable as the observed one. The
   enumeration is exact in integer arithmetic and is refused rather than approximated when the
   configuration count exceeds the cap.

3. `horizon_stability`. `tau_erase = argmax_t A_unrefl(t)` is the Phase-1 surrogate the report leans
   on once `tau_err(delta_P)` is shown to be inestimable. An argmax over a window is only meaningful
   if it does not migrate with the window: the diagnostic is the relative movement of the attained
   maximum `A_swap` between horizons, and the fraction of runs whose argmax sits in the terminal
   10 % of its window -- the signature of a maximum that has not yet occurred.

   Computed at the registry `DELTA_P = 0.005` and on the window `[tau_swap^(1/M), tau_swap^(1/M)+T_h)`
   so it is the published `tau_erase` column that is being audited, not a variant of it. The
   recomputation at `T_h = 2500` is checked against that column.

Output: results/S6_synchronized_traces/tables/envelope_stats.json
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.dataset as ds
import pyarrow.parquet as pq
from joblib import Parallel, delayed
from scipy.stats import binomtest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from config import experiment_ssot as ssot  # noqa: E402

RESULTS_DIR = ssot.RESULTS_DIR / "S6_synchronized_traces"
AUDIT_DELTA_P = ssot.S6_AUDIT_DELTA_P          # 0.01, manuscript tolerance (items 1 and 2)
REGISTRY_DELTA_P = ssot.DELTA_P                # 0.005, the tolerance A_unrefl was written at (item 3)
AUDIT_LAMBDAS = ssot.S6_AUDIT_LAMBDAS          # 15, 50
WARMUP = ssot.S6_WARMUP_WINDOW
T_HORIZON = ssot.S6_T_HORIZON                  # 2500
TRACE_POST = ssot.S6_TRACE_POST                # 4000, the hard ceiling on any horizon below
ARMS = [a for a in ssot.S6_ARM_NAMES if a != "static"]
REFERENCE_ARM = "full"

BOOTSTRAP_SEED = 12345
N_BOOTSTRAP = 10_000
ENVELOPES = {"0.20_0.50": (0.20, 0.50), "0.20_0.40": (0.20, 0.40)}
DECISION_LAMBDA = 15.0
HORIZONS = [1250, 2500, 5000]
TERMINAL_FRACTION = 0.10
FISHER_MAX_CONFIGS = 2_000_000


def s_max(excess):
    """max_t of the reflected CUSUM. Lindley: S_t = M_t - min_{0<=k<=t} M_k, M_0 = 0."""
    m = np.concatenate(([0.0], np.cumsum(excess)))
    return float(np.max(m - np.minimum.accumulate(m)))


# ══════════════════════════════════════════════════════════════════════════════
# extraction
# ══════════════════════════════════════════════════════════════════════════════
def partition_stats(part, tau_swap, warmup=WARMUP, horizon=T_HORIZON):
    """(delta_e, S_max rows, horizon-stability rows) for one magnitude partition.

    `tau_swap` is {seed: tau_swap^(1/M)} for the reference arm at this magnitude."""
    delta_e = float(Path(part).name.split("=", 1)[1])
    df = ds.dataset(str(part), format="parquet").to_table(
        columns=["arm", "seed", "t_rel", "err", "a_unrefl"],
        filter=ds.field("arm").isin(ARMS) & (ds.field("t_rel") >= -warmup)
        & (ds.field("t_rel") < TRACE_POST)).to_pandas().sort_values(["arm", "seed", "t_rel"])

    peaks, stability = [], []
    for (arm, seed), g in df.groupby(["arm", "seed"], sort=True):
        err = g["err"].to_numpy(dtype=np.float64)
        t_rel = g["t_rel"].to_numpy()
        post = t_rel >= 0
        p0_hat = float(err[~post].mean())
        window = post & (t_rel < horizon)
        peaks.append({"arm": arm, "seed": int(seed), "delta_e": delta_e,
                      "p0_hat": p0_hat,
                      "s_max": s_max(err[window] - p0_hat - AUDIT_DELTA_P)})

        if arm != REFERENCE_ARM:
            continue
        a_unrefl = g["a_unrefl"].to_numpy(dtype=np.float64)[post]   # already at REGISTRY_DELTA_P
        lo = tau_swap.get(int(seed), np.nan)
        row = {"seed": int(seed), "delta_e": delta_e, "tau_swap": lo}
        if np.isfinite(lo):
            lo = int(lo)
            for t_h in HORIZONS:
                hi = min(lo + t_h, a_unrefl.size)
                if hi - lo < 2:
                    continue
                seg = a_unrefl[lo:hi]
                arg = int(np.argmax(seg))
                row[f"a_swap_{t_h}"] = float(seg[arg])
                row[f"tau_erase_{t_h}"] = float(lo + arg)
                row[f"terminal_{t_h}"] = bool(arg >= (1 - TERMINAL_FRACTION) * (hi - lo - 1))
                row[f"width_{t_h}"] = int(hi - lo)
        stability.append(row)
    return delta_e, peaks, stability


# ══════════════════════════════════════════════════════════════════════════════
# 1. bootstrap of lambda_op
# ══════════════════════════════════════════════════════════════════════════════
def bootstrap_lambda_op(by_delta, rng, n_boot=N_BOOTSTRAP):
    """(estimate, replicates) for min_Delta_e q05(S_max), blocks resampled per magnitude."""
    mags = sorted(by_delta)
    q05 = np.empty((n_boot, len(mags)))
    for j, de in enumerate(mags):
        s = by_delta[de]
        idx = rng.integers(0, s.size, size=(n_boot, s.size))
        q05[:, j] = np.quantile(s[idx], 0.05, axis=1)
    estimate = float(min(np.quantile(by_delta[de], 0.05) for de in mags))
    return estimate, q05.min(axis=1)


def bootstrap_lambda_op_paired(by_delta, rng, n_boot=N_BOOTSTRAP):
    """Same statistic, resampling the seed index once per replicate across every magnitude."""
    mags = sorted(by_delta)
    mat = np.stack([by_delta[de] for de in mags], axis=1)        # seeds x magnitudes
    idx = rng.integers(0, mat.shape[0], size=(n_boot, mat.shape[0]))
    q05 = np.quantile(mat[idx], 0.05, axis=1)                    # n_boot x magnitudes
    return q05.min(axis=1)


def summarise(estimate, reps, threshold=DECISION_LAMBDA):
    return {"estimate": round(float(estimate), 4),
            "ci_lo_2p5": round(float(np.quantile(reps, 0.025)), 4),
            "ci_hi_97p5": round(float(np.quantile(reps, 0.975)), 4),
            "fraction_below_15": round(float(np.mean(reps < threshold)), 5),
            "n_bootstrap": int(reps.size)}


# ══════════════════════════════════════════════════════════════════════════════
# 2. exact Fisher on a 2 x C table, and Clopper-Pearson
# ══════════════════════════════════════════════════════════════════════════════
def _compositions(k, caps):
    if len(caps) == 1:
        if k <= caps[0]:
            yield (k,)
        return
    for t in range(min(k, caps[0]) + 1):
        for rest in _compositions(k - t, caps[1:]):
            yield (t,) + rest


def fisher_exact_2xc(successes, totals, max_configs=FISHER_MAX_CONFIGS):
    """Exact Fisher test of homogeneity on a 2 x C table, by integer enumeration.

    P(T) = prod_j C(n_j, t_j) / C(N, k); the p-value is the total probability of every table with the
    same margins that is at most as probable as the observed one. Returns `None` for the p-value when
    the configuration count exceeds the cap, rather than substituting an approximation."""
    successes, totals = list(map(int, successes)), list(map(int, totals))
    k, n_total = sum(successes), sum(totals)
    n_configs = math.comb(k + len(totals) - 1, len(totals) - 1)
    if k == 0:
        return {"p_value": 1.0, "method": "degenerate (no success in the table)",
                "n_successes": 0, "n_total": n_total, "n_configurations": 1}
    if n_configs > max_configs:
        return {"p_value": None, "method": f"refused: {n_configs} configurations exceeds the cap",
                "n_successes": k, "n_total": n_total, "n_configurations": int(n_configs)}
    obs = math.prod(math.comb(n, t) for n, t in zip(totals, successes))
    num = enumerated = 0
    for comp in _compositions(k, totals):
        w = math.prod(math.comb(n, t) for n, t in zip(totals, comp))
        enumerated += 1
        if w <= obs:
            num += w
    return {"p_value": float(num / math.comb(n_total, k)), "method": "exact enumeration",
            "n_successes": k, "n_total": n_total, "n_configurations": int(enumerated)}


def clopper_pearson(k, n, confidence=0.95):
    ci = binomtest(int(k), int(n)).proportion_ci(confidence_level=confidence, method="exact")
    return {"k": int(k), "n": int(n), "point": round(k / n, 6),
            "ci_lo": round(float(ci.low), 6), "ci_hi": round(float(ci.high), 6),
            "confidence_level": confidence, "method": "Clopper-Pearson exact"}


# ══════════════════════════════════════════════════════════════════════════════
def main():
    base = RESULTS_DIR / "data"
    runs = pq.read_table(base / "runs.parquet").to_pandas()
    parts = sorted((base / "traces.parquet").iterdir())
    tau_by_de = {de: dict(zip(g.seed, g.tau_swap_q010))
                 for de, g in runs[runs.arm == REFERENCE_ARM].groupby("delta_e")}
    grid = np.array(sorted(tau_by_de))

    def tau_for(part):
        de = float(Path(part).name.split("=", 1)[1])
        return tau_by_de[float(grid[np.argmin(np.abs(grid - de))])]

    res = Parallel(n_jobs=-1)(delayed(partition_stats)(p, tau_for(p)) for p in parts)
    peaks = pd.DataFrame([r for _, rows, _ in res for r in rows])
    stab = pd.DataFrame([r for _, _, rows in res for r in rows])

    ref = peaks[peaks.arm == REFERENCE_ARM]
    by_delta = {float(de): g.s_max.to_numpy() for de, g in ref.groupby("delta_e")}

    # --- 1. bootstrap ---------------------------------------------------------------------------
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    boot = {}
    for name, (lo, hi) in ENVELOPES.items():
        sub = {de: v for de, v in by_delta.items() if lo <= de <= hi}
        estimate, reps = bootstrap_lambda_op(sub, rng)
        paired = bootstrap_lambda_op_paired(sub, np.random.default_rng(BOOTSTRAP_SEED))
        boot[name] = {"envelope": [lo, hi], "n_magnitudes": len(sub),
                      "magnitudes": sorted(round(d, 6) for d in sub),
                      **summarise(estimate, reps),
                      "paired_across_magnitudes": summarise(estimate, paired)}

    # --- 2. crossing counts ---------------------------------------------------------------------
    counts = (peaks.assign(**{f"cross{lam:g}": peaks.s_max >= lam for lam in AUDIT_LAMBDAS})
              .groupby(["arm", "delta_e"], observed=True)
              .agg(n=("s_max", "size"),
                   **{f"n_cross_lambda{lam:g}": (f"cross{lam:g}", "sum") for lam in AUDIT_LAMBDAS})
              .reset_index().sort_values(["arm", "delta_e"]))
    counts[[f"n_cross_lambda{lam:g}" for lam in AUDIT_LAMBDAS]] = \
        counts[[f"n_cross_lambda{lam:g}" for lam in AUDIT_LAMBDAS]].astype(int)

    env_lo, env_hi = ENVELOPES["0.20_0.50"]
    env = counts[(counts.arm == REFERENCE_ARM) & (counts.delta_e >= env_lo)
                 & (counts.delta_e <= env_hi)].sort_values("delta_e")
    fisher = fisher_exact_2xc(env.n_cross_lambda50, env.n)
    homogeneity = {"table_shape": [2, int(len(env))], "arm": REFERENCE_ARM, "lambda": 50.0,
                   "per_magnitude_successes": env.n_cross_lambda50.tolist(),
                   "per_magnitude_totals": env.n.tolist(), "fisher_exact": fisher}
    if fisher["p_value"] is not None and fisher["p_value"] >= 0.05:
        homogeneity["pooled_clopper_pearson"] = clopper_pearson(
            int(env.n_cross_lambda50.sum()), int(env.n.sum()))
        homogeneity["pooling_justified"] = True
    else:
        homogeneity["pooled_clopper_pearson"] = None
        homogeneity["pooling_justified"] = False
        homogeneity["note"] = ("homogeneity rejected at 5 % (or untestable): the aggregate interval "
                               "is withheld because pooling a heterogeneous table would average a "
                               "structural effect away")

    # --- 3. horizon stability -------------------------------------------------------------------
    published = runs[runs.arm == REFERENCE_ARM].set_index(["delta_e", "seed"])["tau_erase"]
    recomputed = stab.set_index(["delta_e", "seed"])[f"tau_erase_{T_HORIZON}"]
    joined = pd.concat([published.rename("published"), recomputed.rename("recomputed")], axis=1).dropna()
    cross_check = {"n": int(len(joined)),
                   "max_abs_diff": float((joined.published - joined.recomputed).abs().max()),
                   "identical": bool((joined.published == joined.recomputed).all())}

    rows = []
    for de, g in stab.groupby("delta_e"):
        entry = {"delta_e": round(float(de), 6), "n": int(len(g))}
        for a, b in ((1250, 2500), (2500, 5000), (1250, 5000)):
            ca, cb = f"a_swap_{a}", f"a_swap_{b}"
            if ca in g and cb in g:
                ok = g[ca].notna() & g[cb].notna() & (g[ca].abs() > 1e-12)
                rel = ((g.loc[ok, cb] - g.loc[ok, ca]) / g.loc[ok, ca].abs()).abs()
                entry[f"median_rel_change_a_swap_{a}_to_{b}"] = round(float(rel.median()), 6)
                # The median run does not move at all, so the median alone hides the minority whose
                # maximum had not yet occurred. The tail is reported next to it, not instead of it.
                entry[f"mean_rel_change_a_swap_{a}_to_{b}"] = round(float(rel.mean()), 6)
                entry[f"q90_rel_change_a_swap_{a}_to_{b}"] = round(float(rel.quantile(0.90)), 6)
                entry[f"fraction_rel_change_above_10pct_{a}_to_{b}"] = round(float((rel > 0.10).mean()), 4)
                entry[f"rel_change_of_median_a_swap_{a}_to_{b}"] = round(
                    float(abs(g[cb].median() - g[ca].median()) / abs(g[ca].median())), 6)
        for t_h in HORIZONS:
            col = f"terminal_{t_h}"
            if col in g:
                entry[f"fraction_argmax_in_terminal_10pct_T{t_h}"] = round(float(g[col].mean()), 4)
                entry[f"median_a_swap_T{t_h}"] = round(float(g[f"a_swap_{t_h}"].median()), 3)
                entry[f"median_width_T{t_h}"] = int(g[f"width_{t_h}"].median())
        rows.append(entry)
    key = "median_rel_change_a_swap_1250_to_5000"
    decision_values = [r[key] for r in rows if key in r]

    payload = {
        "source": str(base.relative_to(ssot.ROOT_DIR)),
        "config": {"audit_delta_p": AUDIT_DELTA_P, "registry_delta_p": REGISTRY_DELTA_P,
                   "t_horizon": int(T_HORIZON), "trace_post_ceiling": int(TRACE_POST),
                   "warmup": int(WARMUP), "arms": ARMS, "reference_arm": REFERENCE_ARM,
                   "bootstrap_seed": BOOTSTRAP_SEED, "n_bootstrap": N_BOOTSTRAP,
                   "lambdas": AUDIT_LAMBDAS, "horizons": HORIZONS,
                   "horizon_5000_truncated_to": int(TRACE_POST)},
        "lambda_op_bootstrap": boot,
        "crossing_counts": {"per_arm_per_magnitude": counts.to_dict(orient="records"),
                            "envelope_homogeneity": homogeneity},
        "horizon_stability": {"delta_p": REGISTRY_DELTA_P,
                              "window": "[tau_swap^(1/M), tau_swap^(1/M) + T_h)",
                              "cross_check_vs_published_tau_erase": cross_check,
                              "per_magnitude": rows,
                              "median_over_grid_rel_change_1250_to_5000":
                                  round(float(np.median(decision_values)), 6) if decision_values else None,
                              "max_over_grid_rel_change_1250_to_5000":
                                  round(float(np.max(decision_values)), 6) if decision_values else None},
    }
    out = RESULTS_DIR / "tables" / "envelope_stats.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True, default=float) + "\n",
                   encoding="utf-8")

    # --- console --------------------------------------------------------------------------------
    print(f"=== S6 envelope statistics === delta_P = {AUDIT_DELTA_P} (items 1-2), "
          f"{REGISTRY_DELTA_P} (item 3), T_h = {T_HORIZON}, bootstrap seed {BOOTSTRAP_SEED}")

    print("\n[1] lambda_op(0.05) = min_Delta_e q05(S_max), seed bootstrap, "
          f"{N_BOOTSTRAP} replicates")
    for name, b in boot.items():
        p = b["paired_across_magnitudes"]
        print(f"  envelope {name} ({b['n_magnitudes']} magnitudes)")
        print(f"    block per magnitude : estimate {b['estimate']:7.3f}  "
              f"CI95 [{b['ci_lo_2p5']:7.3f}, {b['ci_hi_97p5']:7.3f}]  "
              f"P(< {DECISION_LAMBDA:g}) = {b['fraction_below_15']:.4f}")
        print(f"    paired across mags  : estimate {p['estimate']:7.3f}  "
              f"CI95 [{p['ci_lo_2p5']:7.3f}, {p['ci_hi_97p5']:7.3f}]  "
              f"P(< {DECISION_LAMBDA:g}) = {p['fraction_below_15']:.4f}")

    print(f"\n[2] crossing counts, envelope [{env_lo:.2f}, {env_hi:.2f}], arm "
          f"'{REFERENCE_ARM}', lambda = 50")
    print(f"  successes per magnitude: {homogeneity['per_magnitude_successes']}")
    print(f"  total {fisher['n_successes']} / {fisher['n_total']}  |  "
          f"Fisher exact 2 x {len(env)}: p = {fisher['p_value']}  ({fisher['method']}, "
          f"{fisher['n_configurations']} configurations)")
    cp = homogeneity["pooled_clopper_pearson"]
    if cp:
        print(f"  homogeneity not rejected -> pooled Clopper-Pearson: {cp['k']}/{cp['n']} = "
              f"{cp['point']:.5f}, CI95 [{cp['ci_lo']:.5f}, {cp['ci_hi']:.5f}]")
    else:
        print(f"  {homogeneity['note']}")
    wide = counts.pivot(index="delta_e", columns="arm", values="n_cross_lambda50")
    print("  n_cross(lambda=50) by arm:\n" + wide[ARMS].to_string())

    print(f"\n[3] horizon stability of tau_erase = argmax A_unrefl "
          f"(cross-check vs published column: identical = {cross_check['identical']}, "
          f"max |diff| = {cross_check['max_abs_diff']:.0f})")
    cols = ["delta_e", "median_rel_change_a_swap_1250_to_5000",
            "q90_rel_change_a_swap_1250_to_5000", "fraction_rel_change_above_10pct_1250_to_5000",
            "fraction_argmax_in_terminal_10pct_T1250", "fraction_argmax_in_terminal_10pct_T2500",
            "fraction_argmax_in_terminal_10pct_T5000", "median_a_swap_T1250",
            "median_a_swap_T2500", "median_a_swap_T5000"]
    df = pd.DataFrame(rows)
    print(df[[c for c in cols if c in df]].to_string(index=False))
    hs = payload["horizon_stability"]
    tail = [r.get("fraction_rel_change_above_10pct_1250_to_5000", 0.0) for r in rows]
    print(f"  median over the grid of the 1250 -> 5000 relative change: "
          f"{hs['median_over_grid_rel_change_1250_to_5000']:.4f}"
          f"  (max of the per-magnitude medians {hs['max_over_grid_rel_change_1250_to_5000']:.4f})")
    print(f"  fraction of runs moving more than 10 %: max over the grid "
          f"{max(tail):.4f} at Delta_e = {rows[int(np.argmax(tail))]['delta_e']}")
    print(f"\n[INFO] wrote {out.relative_to(ssot.ROOT_DIR)}")
    return payload


if __name__ == "__main__":
    main()
