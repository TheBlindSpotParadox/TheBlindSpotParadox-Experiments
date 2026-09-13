"""Causal reading of the erasure (failles F6 / F7 and the Hydra question).

Three measurements on the campaign artifacts.

1. Segmented regression of A_unrefl(t). The proof budget accumulates while the ensemble error stays
   above the monitor's tolerance and decreases once it falls back under it, so A_unrefl(t) is a
   two-slope curve and its knot is the physical instant at which adaptation takes over. The knot is
   fitted, not assumed: a continuous piecewise-linear model A(t) = b0 + b1 t + b2 (t - b)^+ is
   least-squares fitted for every candidate knot on a fixed grid and the SSE minimiser is kept. The
   knot is then compared to tau_swap^(1/M). If the first swap is the cause of the erasure, the two
   coincide; if it is only its first symptom, they do not.

2. Counterfactual contrast, at the seed level. 'full' and 'no_swap' share one stream, one history
   and one fork; they differ by the replacements suppressed after the first. A paired SIGN test on
   (A_full - A_no_swap) and on the erasure times is therefore a within-pair test with no
   distributional assumption -- the right instrument here, because A is bounded below and skewed.

3. Erasure share. 'frozen' is the branch that never adapts again, so A_frozen is the evidence an
   external monitor would have received had adaptation stopped at the fork. Since all three arms
   fork AFTER the first replacement and therefore carry it identically, the decomposition separates
   the two mechanisms that act after the fork, not the first swap:

       E_total = A_frozen - A_full        post-fork erasure: incremental learning AND later swaps
       E_learn = A_frozen - A_no_swap     incremental learning alone, no tree ever replaced again
       share_learn = E_learn / E_total    the remainder is the Hydra's marginal contribution

   Shares are computed per (Delta_e, seed) and aggregated as medians: the ratio is unstable wherever
   E_total is near zero, so a mean over runs would be dominated by those runs alone.

4. Exact decomposition on the tau*-anchored reference. Measurement 3 cannot attribute anything to
   the first replacement, because all three of its arms carry it. Stream S8 adds two arms forked at
   tau* itself -- 'no_swap_ab_initio' and 'frozen_ab_initio' -- and the four-term identity closes
   with no residue. `decomposition_ab_initio` evaluates it and renders decision rules D1 and D2 of
   `docs/prompts/s8-decision-rules.md`. On a corpus without those arms it returns NOT PRODUCED,
   which is why this module reads the S6 and the S8 campaigns with the same code.

Output: <base>/s6_causal.json, `base` defaulting to results/S6_synchronized_traces/data/
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.dataset as ds
import pyarrow.parquet as pq
from joblib import Parallel, delayed
from scipy.stats import binomtest

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import s6_defs as defs  # noqa: E402
import s6_writer as writer  # noqa: E402
from config import experiment_ssot as ssot  # noqa: E402

T_HORIZON = ssot.S6_T_HORIZON
RESULTS_DIR = ssot.RESULTS_DIR / "S6_synchronized_traces"
KNOT_STEP = 5                                   # candidate knots every 5 steps
KNOT_MARGIN = 20                                # no knot inside the first/last 20 steps


def fit_knot(a_unrefl, step=KNOT_STEP, margin=KNOT_MARGIN):
    """(knot, slope_before, slope_after, r2) of the best continuous one-knot linear fit."""
    n = a_unrefl.size
    if n < 4 * margin:
        return np.nan, np.nan, np.nan, np.nan
    t = np.arange(n, dtype=np.float64)
    base = np.column_stack([np.ones(n), t])
    best = (np.inf, np.nan, None)
    for b in range(margin, n - margin, step):
        x = np.column_stack([base, np.clip(t - b, 0.0, None)])
        coef, res, *_ = np.linalg.lstsq(x, a_unrefl, rcond=None)
        sse = float(res[0]) if res.size else float(((x @ coef - a_unrefl) ** 2).sum())
        if sse < best[0]:
            best = (sse, b, coef)
    sse, b, coef = best
    tss = float(((a_unrefl - a_unrefl.mean()) ** 2).sum())
    return float(b), float(coef[1]), float(coef[1] + coef[2]), float(1 - sse / tss) if tss else np.nan


def _partition_stats(part, e_pre_by_seed, horizon=T_HORIZON, delta=ssot.DELTA_P):
    """One pass over a magnitude partition: knots on 'full', common-window budgets on every arm.

    `a_pos_common` is the positive-part budget of def:budget evaluated over the SAME window for all
    four arms, [tau*, tau* + T_h). The `a_fw` column in runs.parquet integrates each arm up to its
    OWN tau_erase, which is censored on 'frozen' -- that arm never settles, by construction. A
    contrast between arms integrated over different intervals is not a contrast, so the decomposition
    is read here and not from `a_fw`."""
    tbl = ds.dataset(str(part), format="parquet").to_table(
        columns=["arm", "seed", "t_rel", "err", "a_unrefl"],
        filter=(ds.field("t_rel") >= 0) & (ds.field("t_rel") < horizon))
    df = tbl.to_pandas().sort_values(["arm", "seed", "t_rel"])

    knots, budgets = [], []
    for (arm, seed), g in df.groupby(["arm", "seed"], sort=True):
        e_pre = e_pre_by_seed.get((arm, int(seed)), np.nan)
        err = g["err"].to_numpy(dtype=np.float64)
        # Positive part on the SMOOTHED rate, per def:budget. On the raw indicator the clip is
        # inert and the sum degenerates into 0.945 x the error count (see s6_defs.budget_framework).
        smooth = defs.rolling_mean(err, ssot.S6_ERR_WINDOW)
        excess = smooth[np.isfinite(smooth)] - e_pre - delta
        budgets.append({"arm": arm, "seed": int(seed),
                        "a_pos_common": float(np.clip(excess, 0.0, None).sum()),
                        "a_signed_common": float((err - e_pre - delta).sum())})
        if arm == "full":
            knot, s_before, s_after, r2 = fit_knot(g["a_unrefl"].to_numpy())
            knots.append({"seed": int(seed), "knot": knot, "slope_before": s_before,
                          "slope_after": s_after, "r2": r2})
    return knots, budgets


def partition_stats(traces_root, runs, n_jobs=-1):
    """(knots DataFrame on 'full', budgets DataFrame on every arm), keyed by (delta_e, seed)."""
    parts = sorted(Path(traces_root).iterdir())
    e_pre = {de: {(a, s): e for a, s, e in
                  g[["arm", "seed", "e_pre"]].itertuples(index=False)}
             for de, g in runs.groupby("delta_e")}
    lookup = [e_pre[min(e_pre, key=lambda d: abs(d - float(p.name.split("=", 1)[1])))] for p in parts]
    res = Parallel(n_jobs=n_jobs)(delayed(_partition_stats)(p, m) for p, m in zip(parts, lookup))
    k_rows, b_rows = [], []
    for p, (knots, budgets) in zip(parts, res):
        de = float(p.name.split("=", 1)[1])
        k_rows += [{**r, "delta_e": de} for r in knots]
        b_rows += [{**r, "delta_e": de} for r in budgets]
    return pd.DataFrame(k_rows), pd.DataFrame(b_rows)


def sign_test(diff):
    """Paired sign test on a difference vector; ties are dropped, as the test requires."""
    d = np.asarray(diff, dtype=np.float64)
    d = d[np.isfinite(d) & (d != 0.0)]
    if d.size == 0:
        return {"n": 0, "n_positive": 0, "p_value": np.nan, "median_diff": np.nan}
    n_pos = int((d > 0).sum())
    return {"n": int(d.size), "n_positive": n_pos,
            "p_value": float(binomtest(n_pos, d.size, 0.5).pvalue),
            "median_diff": float(np.median(d))}


def contrasts(runs, col):
    """Paired 'full' vs 'no_swap' contrast on `col`, pooled and per magnitude."""
    wide = runs.pivot_table(index=["delta_e", "seed"], columns="arm", values=col)
    if not {"full", "no_swap"} <= set(wide.columns):
        return {"pooled": sign_test([]), "per_delta_e": []}
    d = (wide["full"] - wide["no_swap"]).dropna()
    per = [{"delta_e": float(de), **sign_test(g.to_numpy())}
           for de, g in d.groupby(level="delta_e")]
    return {"pooled": sign_test(d.to_numpy()), "per_delta_e": per}


def erasure_share(runs, col="a_fw"):
    """Median share of the post-fork erasure imputable to INCREMENTAL LEARNING, per magnitude
    and pooled.

    The quantity is not what an earlier revision of this function claimed. All three arms fork at
    tau_swap^(1/M), AFTER the learn_one that produced the first replacement, so all three carry that
    replacement identically. No difference between them can therefore be attributed to it: the first
    swap is common to the factual arm and to both counterfactuals, and this decomposition cannot
    isolate it.

    What the three arms do separate is everything that happens AFTER the fork:

        e_total = A_frozen - A_full       post-fork erasure: incremental learning AND later swaps
        e_learn = A_frozen - A_no_swap    incremental learning alone -- 'no_swap' keeps learning with
                                          both detector paths inert, so no tree is ever replaced again
        e_total - e_learn                 the marginal contribution of the later replacements, i.e.
                                          the Hydra

    `median_share_learn` is therefore the fraction of the post-fork erasure done by the ensemble
    simply continuing to fit the new concept with the trees it already has. Isolating the first swap
    would need a fourth arm forked BEFORE it fires, which this campaign does not simulate."""
    wide = runs.pivot_table(index=["delta_e", "seed"], columns="arm", values=col)
    need = {"full", "no_swap", "frozen"}
    if not need <= set(wide.columns):
        return {"pooled": None, "per_delta_e": []}
    e_total = wide["frozen"] - wide["full"]
    e_learn = wide["frozen"] - wide["no_swap"]
    ok = np.isfinite(e_total) & np.isfinite(e_learn) & (e_total > 0)
    share = (e_learn[ok] / e_total[ok]).clip(-1.0, 2.0)
    per = [{"delta_e": float(de), "n": int(g.size), "median_share_learn": float(np.median(g)),
            "q25": float(np.quantile(g, 0.25)), "q75": float(np.quantile(g, 0.75))}
           for de, g in share.groupby(level="delta_e") if g.size]
    return {"pooled": {"n": int(share.size), "median_share_learn": float(np.median(share)),
                       "q25": float(np.quantile(share, 0.25)),
                       "q75": float(np.quantile(share, 0.75)),
                       "median_e_total": float(np.median(e_total[ok])),
                       "median_e_learn": float(np.median(e_learn[ok])),
                       "n_dropped_non_positive_e_total": int((~ok).sum())},
            "per_delta_e": per}


def bootstrap_median_ci(values, seeds, seed=ssot.S8_BOOTSTRAP_SEED, n_boot=ssot.S8_N_BOOTSTRAP,
                        level=ssot.S8_CI_LEVEL):
    """Seed-PAIRED bootstrap CI of the median of `values`.

    Every magnitude reuses the same seed pool, so two cells sharing a seed share their whole
    pre-drift trajectory and their e_pre. Resampling the (delta_e, seed) cells independently would
    treat those as 20 independent observations. The seed INDEX is resampled once per replicate and
    every magnitude is read at those seeds, which is the scheme `s6_envelope_stats` already uses for
    lambda_op."""
    v = np.asarray(values, dtype=np.float64)
    s = np.asarray(seeds)
    ok = np.isfinite(v)
    v, s = v[ok], s[ok]
    if v.size == 0:
        return {"n": 0, "median": np.nan, "lo": np.nan, "hi": np.nan, "n_boot": 0}
    pool = np.unique(s)
    by_seed = [np.flatnonzero(s == u) for u in pool]
    rng = np.random.default_rng(np.random.SeedSequence(seed))
    reps = np.empty(n_boot, dtype=np.float64)
    for b in range(n_boot):
        pick = rng.integers(0, pool.size, pool.size)
        reps[b] = np.median(v[np.concatenate([by_seed[i] for i in pick])])
    alpha = (1.0 - level) / 2.0
    return {"n": int(v.size), "n_seeds": int(pool.size), "median": float(np.median(v)),
            "lo": float(np.quantile(reps, alpha)), "hi": float(np.quantile(reps, 1 - alpha)),
            "n_boot": int(n_boot), "level": float(level)}


def decomposition_ab_initio(runs, col="a_pos_common"):
    """Exact four-term erasure decomposition anchored on the tau*-forked reference (stream S8).

    `erasure_share` above is anchored on tau_swap^(1/M), which every S6 arm shares, so its E_learn
    CONTAINS the first replacement and `\\LearnShare` cannot be read as learning alone. With the two
    ab initio arms the reference becomes tau*, an exogenous instant, and the decomposition closes:

        E_total      = A_frozen_abinit - A_full          all post-tau* adaptation
        E_learn_pure = A_frozen_abinit - A_abinit        learning alone, no tree ever replaced
        E_swap_first = A_abinit        - A_no_swap       the FIRST replacement, isolated
        E_swap_rest  = A_no_swap       - A_full          every later replacement
        E_total = E_learn_pure + E_swap_first + E_swap_rest      identically, by telescoping

    Decision rules D1 and D2 of `docs/prompts/s8-decision-rules.md` are evaluated here and their
    verdicts are written into the payload, not left to the reader."""
    wide = runs.pivot_table(index=["delta_e", "seed"], columns="arm", values=col)
    need = {"full", "no_swap", "frozen_ab_initio", "no_swap_ab_initio"}
    if not need <= set(wide.columns):
        return {"status": "NOT PRODUCED", "missing_arms": sorted(need - set(wide.columns)),
                "column": col}

    terms = pd.DataFrame({
        "e_total": wide["frozen_ab_initio"] - wide["full"],
        "e_learn_pure": wide["frozen_ab_initio"] - wide["no_swap_ab_initio"],
        "e_swap_first": wide["no_swap_ab_initio"] - wide["no_swap"],
        "e_swap_rest": wide["no_swap"] - wide["full"],
        "d_swap_all": wide["no_swap_ab_initio"] - wide["full"],
    })
    residual = (terms.e_total
                - (terms.e_learn_pure + terms.e_swap_first + terms.e_swap_rest)).abs().max()

    ok = np.isfinite(terms.e_total) & (terms.e_total > 0)
    for c in ("e_learn_pure", "e_swap_first", "e_swap_rest", "d_swap_all"):
        ok &= np.isfinite(terms[c])
    sub = terms[ok]
    shares = pd.DataFrame({c.replace("e_", "share_").replace("d_", "share_"):
                           sub[c] / sub.e_total
                           for c in ("e_learn_pure", "e_swap_first", "e_swap_rest", "d_swap_all")})

    seeds = sub.index.get_level_values("seed").to_numpy()
    ci = {name: bootstrap_median_ci(shares[name].to_numpy(), seeds) for name in shares.columns}
    sign_all = sign_test(sub.d_swap_all.to_numpy())
    band_lo, band_hi = ssot.S8_INERT_BAND
    inert = (band_lo <= ci["share_swap_all"]["lo"] and ci["share_swap_all"]["hi"] <= band_hi
             and not (sign_all["p_value"] < ssot.S8_SIGN_TEST_ALPHA))

    per = [{"delta_e": float(de), "n": int(len(g)),
            **{f"median_{c}": float(np.median(g[c])) for c in sub.columns},
            **{f"median_{c}": float(np.median(shares.loc[g.index, c])) for c in shares.columns}}
           for de, g in sub.groupby(level="delta_e")]

    return {
        "status": "PRODUCED", "column": col,
        "n_cells": int(len(sub)), "n_dropped_non_positive_e_total": int((~ok).sum()),
        "additivity_residual_max": float(residual),
        "median_terms": {c: float(np.median(sub[c])) for c in sub.columns},
        "share_ci": ci,
        "sign_test_a_abinit_minus_a_full": sign_all,
        "D1_inert_band": [float(band_lo), float(band_hi)],
        "D1_sign_test_alpha": float(ssot.S8_SIGN_TEST_ALPHA),
        "D1_verdict": "INERT" if inert else "NOT INERT",
        "D2_verdict": ("MEASURED" if ci["share_swap_first"]["lo"] > 0.0
                       else "NOT SEPARABLE"),
        "learn_share_restated": ci["share_learn_pure"],
        "per_delta_e": per,
    }


def erasure_estimability(traces_root, runs, de, window=ssot.S6_ERR_WINDOW, delta=ssot.DELTA_P):
    """Is tau_err(delta_P) estimable at all on this stream?

    def:times reads tau_erase off a threshold p_0 + delta_P. The error is observed through a trailing
    mean of `window` steps, whose standard error at p_0 = 0.05 is sqrt(p(1-p)/W). If delta_P is not
    several of those standard errors, the "last crossing" is the last time NOISE pushed the window
    over the line, and the statistic reports the horizon rather than the erasure.

    The control is the pre-drift window itself: 1000 steps with no drift in them. A physically
    meaningful erasure time is ~0 there. Whatever the statistic returns on that stretch is what it
    returns on noise alone."""
    part = Path(traces_root) / f"delta_e={ssot.S6_PARQUET_PARTITION_FMT.format(de)}"
    tbl = ds.dataset(str(part), format="parquet").to_table(
        columns=["arm", "seed", "t_rel", "err"], filter=ds.field("arm") == "full")
    df = tbl.to_pandas().sort_values(["seed", "t_rel"])
    e_pre = runs[(runs.arm == "full") & np.isclose(runs.delta_e, de)].set_index("seed")["e_pre"]

    null = []
    for seed, g in df.groupby("seed"):
        pre = g.loc[g.t_rel < 0, "err"].to_numpy(dtype=np.float64)
        null.append(defs.tau_err_framework(pre, float(e_pre.loc[seed]), delta,
                                           window=window, horizon=pre.size))
    null = np.asarray(null, dtype=np.float64)
    horizon = int((df.t_rel < 0).sum() / max(df.seed.nunique(), 1))
    # p_0 is measured, not the 0.05 transfer_S1 computes its numerical results at: the canonical
    # stream settles near 0.024, and the standard error of the smoothed rate scales with it.
    p0 = float(np.median(e_pre))
    se = float(np.sqrt(p0 * (1 - p0) / window))
    return {"window": int(window), "delta_p": float(delta), "p0_measured": p0,
            "rolling_mean_se": se, "delta_p_in_se_units": float(delta / se),
            "window_required_for_3_se": int(np.ceil(9 * p0 * (1 - p0) / delta ** 2)),
            "null_horizon": horizon, "null_n": int(null.size),
            "null_censored_rate": float(np.mean(~np.isfinite(null))),
            "null_median_tau_err": float(np.nanmedian(null)),
            "null_mean_tau_err": float(np.nanmean(null)),
            "null_mean_as_fraction_of_horizon": float(np.nanmean(null) / horizon) if horizon else np.nan,
            "estimable": bool(delta / se >= 3.0)}


def kappa_gate(runs, target=ssot.S6_KAPPA_DELTA_E_TARGET):
    """The S6 blocking gate of docs/theory/transfer_S1.md, evaluated on the campaign.

    transfer_S1 fixes W* = 95 as the largest exploitable transient that still preserves the
    lambda = 50 starvation certificate, and derives kappa* = W* / (first-swap statistic):
    1.73 on the mean (54.8 steps) and 3.18 on the q05 (30 steps). The measured kappa replaces W* by
    the transient actually observed. `kappa > kappa*` falsifies the certificate as that document
    states it.

    Both bases are reported, together with the mean first swap itself -- transfer_S1 asserts 54.8
    steps at this operating point, and whether the campaign reproduces that number decides whether a
    kappa mismatch is about the erasure time or about the swap time."""
    de = min(runs.delta_e.unique(), key=lambda d: abs(d - target))
    g = runs[(runs.arm == "full") & np.isclose(runs.delta_e, de)]
    swap = g.tau_swap_q010.to_numpy(dtype=np.float64)
    erase = g.tau_erase_fw.to_numpy(dtype=np.float64)
    ok_s, ok_e = np.isfinite(swap), np.isfinite(erase)
    mean_swap = float(np.mean(swap[ok_s])) if ok_s.any() else np.nan
    q05_swap = float(np.quantile(swap[ok_s], 0.05)) if ok_s.any() else np.nan
    mean_erase = float(np.mean(erase[ok_e])) if ok_e.any() else np.nan
    per_run = g.kappa.to_numpy(dtype=np.float64)
    per_run = per_run[np.isfinite(per_run)]
    k_mean = mean_erase / mean_swap if mean_swap else np.nan
    k_q05 = mean_erase / q05_swap if q05_swap else np.nan

    # Same ratio on the two ESTIMABLE erasure surrogates, so the gate has an answer even when
    # tau_err(delta_P) does not. Direction, not value, is what carries across definitions.
    surrogates = {}
    for name, col in (("argmax_A_unrefl", "tau_erase"),
                      ("tau_err_rho010", f"tau_err_rho{int(round(ssot.S6_RHO_GRID[-1] * 100)):03d}")):
        v = g[col].to_numpy(dtype=np.float64)
        v = v[np.isfinite(v)]
        m = float(np.mean(v)) if v.size else np.nan
        surrogates[name] = {
            "column": col, "n": int(v.size), "mean": m,
            "censoring_rate": float(1 - v.size / max(len(g), 1)),
            "kappa_mean_basis": m / mean_swap if mean_swap else np.nan,
            "kappa_q05_basis": m / q05_swap if q05_swap else np.nan,
            "verdict_mean_basis": "FALSIFIED" if (mean_swap and m / mean_swap > ssot.S6_KAPPA_STAR_MEAN)
            else "HELD"}
    return {
        "erasure_surrogates": surrogates,
        "delta_e_target": float(target), "delta_e_used": float(de), "n": int(len(g)),
        "n_censored_erase": int((~ok_e).sum()), "n_censored_swap": int((~ok_s).sum()),
        "mean_tau_swap_1m": mean_swap, "q05_tau_swap_1m": q05_swap,
        "transfer_S1_mean_tau_swap": 54.8, "transfer_S1_q05_tau_swap": 30.0,
        "transfer_S1_W_star": float(ssot.S6_W_STAR),
        "mean_tau_erase": mean_erase,
        "kappa_mean_basis": k_mean, "kappa_star_mean": float(ssot.S6_KAPPA_STAR_MEAN),
        "kappa_q05_basis": k_q05, "kappa_star_q05": float(ssot.S6_KAPPA_STAR_Q05),
        "median_per_run_kappa": float(np.median(per_run)) if per_run.size else np.nan,
        "fraction_runs_above_kappa_star_mean": float(np.mean(per_run > ssot.S6_KAPPA_STAR_MEAN))
        if per_run.size else np.nan,
        "verdict_mean_basis": "FALSIFIED" if k_mean > ssot.S6_KAPPA_STAR_MEAN else "HELD",
        "verdict_q05_basis": "FALSIFIED" if k_q05 > ssot.S6_KAPPA_STAR_Q05 else "HELD",
    }


def main(which="data", base=None, out_name="s6_causal.json"):
    """`base` overrides the S6 corpus directory so a foreign campaign carrying the same schema --
    stream S8's ab initio campaign -- is read by this module rather than by a fork of it."""
    base = Path(base) if base is not None else RESULTS_DIR / which
    runs = pq.read_table(base / "runs.parquet").to_pandas()
    knots, budgets = partition_stats(base / "traces.parquet", runs)
    runs = runs.merge(budgets, on=["delta_e", "arm", "seed"], how="left")

    full = runs[runs.arm == "full"][["delta_e", "seed", "tau_swap_q010", "tau_erase_fw", "delta_e_emp"]]
    merged = knots.merge(full, on=["delta_e", "seed"], how="inner")
    merged["knot_minus_tau_swap"] = merged["knot"] - merged["tau_swap_q010"]
    merged["knot_over_tau_swap"] = merged["knot"] / merged["tau_swap_q010"].replace(0, np.nan)

    ok = np.isfinite(merged["knot_minus_tau_swap"])
    knot_summary = {
        "n": int(ok.sum()),
        "median_knot": float(merged.loc[ok, "knot"].median()),
        "median_tau_swap": float(merged.loc[ok, "tau_swap_q010"].median()),
        "median_knot_minus_tau_swap": float(merged.loc[ok, "knot_minus_tau_swap"].median()),
        "median_knot_over_tau_swap": float(merged.loc[ok, "knot_over_tau_swap"].median()),
        "median_r2": float(merged.loc[ok, "r2"].median()),
        "median_slope_before": float(merged.loc[ok, "slope_before"].median()),
        "median_slope_after": float(merged.loc[ok, "slope_after"].median()),
        "sign_test_knot_after_first_swap": sign_test(merged.loc[ok, "knot_minus_tau_swap"]),
        "per_delta_e": [{"delta_e": float(de), "n": int(g.knot.notna().sum()),
                         "median_knot": float(g.knot.median()),
                         "median_tau_swap": float(g.tau_swap_q010.median()),
                         "median_ratio": float(g.knot_over_tau_swap.median()),
                         "median_r2": float(g.r2.median())}
                        for de, g in merged.groupby("delta_e")],
    }

    payload = {
        "source": str(base.relative_to(ssot.ROOT_DIR)),
        "n_runs": int(len(runs)), "horizon": float(T_HORIZON),
        "knot_grid": {"step": KNOT_STEP, "margin": KNOT_MARGIN},
        "segmented_regression": knot_summary,
        "contrast_full_minus_no_swap": {
            c: contrasts(runs, c)
            for c in ("a_pos_common", "a_signed_common", "a_fw", "a", "tau_erase_fw", "tau_erase")},
        "erasure_share_post_fork": {c: erasure_share(runs, c)
                                     for c in ("a_pos_common", "a_signed_common", "a")},
        "decomposition_ab_initio": {c: decomposition_ab_initio(runs, c)
                                    for c in ("a_pos_common", "a_signed_common", "a")},
        "kappa_gate_transfer_S1": {
            **kappa_gate(runs),
            "estimability": erasure_estimability(
                base / "traces.parquet", runs,
                min(runs.delta_e.unique(), key=lambda d: abs(d - ssot.S6_KAPPA_DELTA_E_TARGET)))},
    }
    out = base / out_name
    out.write_text(json.dumps(payload, indent=2, sort_keys=True, default=float) + "\n",
                   encoding="utf-8")

    k = knot_summary
    print(f"=== S6 causal ({payload['source']}) === {payload['n_runs']} run records")
    print(f"\n[1] Segmented regression of A_unrefl(t), arm 'full', n={k['n']}")
    print(f"    median knot            = {k['median_knot']:.1f}")
    print(f"    median tau_swap^(1/M)  = {k['median_tau_swap']:.1f}")
    print(f"    median knot / tau_swap = {k['median_knot_over_tau_swap']:.2f}   "
          f"(median difference {k['median_knot_minus_tau_swap']:+.1f} steps)")
    print(f"    median R^2 = {k['median_r2']:.4f} | slopes {k['median_slope_before']:+.4f} -> "
          f"{k['median_slope_after']:+.4f}")
    st = k["sign_test_knot_after_first_swap"]
    print(f"    sign test knot > tau_swap: {st['n_positive']}/{st['n']}  p = {st['p_value']:.3e}")

    print("\n[2] Paired contrast 'full' - 'no_swap' (sign test, seed level)")
    for col, res in payload["contrast_full_minus_no_swap"].items():
        p = res["pooled"]
        print(f"    {col:16s} n={p['n']:5d}  positive={p['n_positive']:5d}  "
              f"median diff={p['median_diff']:+9.3f}  p={p['p_value']:.3e}")

    print("\n[3] Share of the post-fork erasure attributable to incremental learning")
    for col, res in payload["erasure_share_post_fork"].items():
        p = res["pooled"]
        if p is None:
            continue
        print(f"    {col:16s} median share = {p['median_share_learn']:.3f} "
              f"[{p['q25']:.3f}, {p['q75']:.3f}]  n={p['n']}  "
              f"(median E_total={p['median_e_total']:.2f}, E_learn={p['median_e_learn']:.2f}, "
              f"dropped={p['n_dropped_non_positive_e_total']})")
    print("\n[3-bis] Exact decomposition on the tau*-anchored reference (S8 ab initio arms)")
    for col, res in payload["decomposition_ab_initio"].items():
        if res["status"] != "PRODUCED":
            print(f"    {col:16s} {res['status']} -- missing arms: {res['missing_arms']}")
            continue
        m, ci = res["median_terms"], res["share_ci"]
        print(f"    {col:16s} n={res['n_cells']} cells, additivity residual "
              f"{res['additivity_residual_max']:.2e}, dropped={res['n_dropped_non_positive_e_total']}")
        print(f"      median E_total={m['e_total']:.3f}  E_learn_pure={m['e_learn_pure']:.3f}  "
              f"E_swap_first={m['e_swap_first']:.3f}  E_swap_rest={m['e_swap_rest']:.3f}")
        for name in ("share_learn_pure", "share_swap_first", "share_swap_rest", "share_swap_all"):
            c = ci[name]
            print(f"      {name:17s} = {c['median']:+.4f}  95% CI [{c['lo']:+.4f}, {c['hi']:+.4f}]")
        st = res["sign_test_a_abinit_minus_a_full"]
        print(f"      sign test (A_abinit - A_full): {st['n_positive']}/{st['n']} positive, "
              f"p = {st['p_value']:.3e}, median {st['median_diff']:+.3f}")
        print(f"      D1 = {res['D1_verdict']}   D2 = {res['D2_verdict']}")

    kg = payload["kappa_gate_transfer_S1"]
    print(f"\n[4] transfer_S1 blocking gate at Delta_e = {kg['delta_e_used']:.4f} "
          f"(target {kg['delta_e_target']}), n={kg['n']}")
    print(f"    mean tau_swap^(1/M) = {kg['mean_tau_swap_1m']:.1f} "
          f"(transfer_S1 asserts {kg['transfer_S1_mean_tau_swap']})  |  "
          f"q05 = {kg['q05_tau_swap_1m']:.1f} (asserts {kg['transfer_S1_q05_tau_swap']})")
    print(f"    mean tau_erase = {kg['mean_tau_erase']:.1f}  (W* = {kg['transfer_S1_W_star']:.0f})")
    print(f"    kappa (mean basis) = {kg['kappa_mean_basis']:.2f} vs kappa* = "
          f"{kg['kappa_star_mean']:.2f}  -> {kg['verdict_mean_basis']}")
    print(f"    kappa (q05 basis)  = {kg['kappa_q05_basis']:.2f} vs kappa* = "
          f"{kg['kappa_star_q05']:.2f}  -> {kg['verdict_q05_basis']}")
    print(f"    per-run median kappa = {kg['median_per_run_kappa']:.2f}, "
          f"{100 * kg['fraction_runs_above_kappa_star_mean']:.1f}% of runs above kappa*_mean")
    es = kg["estimability"]
    print(f"    ESTIMABILITY of tau_err(delta_P): p_0 measured = {es['p0_measured']:.4f}, "
          f"delta_P = {es['delta_p_in_se_units']:.2f} SE of the W={es['window']} rolling mean "
          f"(3 SE would need W >= {es['window_required_for_3_se']})")
    print(f"      null control on the {es['null_horizon']}-step pre-drift window (no drift): "
          f"mean tau_err = {es['null_mean_tau_err']:.1f} = "
          f"{100 * es['null_mean_as_fraction_of_horizon']:.0f}% of horizon, "
          f"censored {100 * es['null_censored_rate']:.0f}%  -> estimable = {es['estimable']}")
    for name, srg in kg["erasure_surrogates"].items():
        print(f"    surrogate {name:16s} mean={srg['mean']:7.1f} (censored "
              f"{100 * srg['censoring_rate']:.1f}%)  kappa_mean={srg['kappa_mean_basis']:6.2f}  "
              f"kappa_q05={srg['kappa_q05_basis']:6.2f}  -> {srg['verdict_mean_basis']}")
    print(f"\n[INFO] wrote {out.relative_to(ssot.ROOT_DIR)}")
    return payload


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data")
