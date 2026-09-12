"""Stream S3 -- the race as competing risks, and the effective ensemble size.

`prop:starvation_boundary` races `tau_ARF` against a DETERMINISTIC scalar
`tau_det* = lambda / (Delta_e - delta_P)`. `tau_det` is a stopping time, not a scalar, and this
module drops `tau_det*` from the reasoning entirely: the event of interest is `{tau_ARF < tau_det}`
under a single administrative censoring at the common horizon `t_c = CENSORING_HORIZON`.

Framework reused, not reinvented. Under one administrative censoring at a common horizon,
Kaplan--Meier reduces to the empirical survival and `RMST(t_c) = mean(min(tau, t_c))` exactly;
`experiments/R6_hydra_factor/exp_R6_hydra_survival.py` already carries `km_curve`, `rmst` and the
identity check, and this module imports them rather than writing a second estimator. Rule D3 fixes
the reproduction tolerance at 1e-9, which is that module's own `RMST_TOL`.

Three deliverables:

  P3  cumulative incidence of the two causes (ARF adapts first / detector fires first) with
      paired-on-seed bootstrap bands, at the three R2 thresholds -- `results/S3/cif_bands.csv`
  P4  `rho_hat` and `M_eff` by two bracketing routes, and the Hydra factor they are confronted
      with -- `results/S3/rho_meff.csv`
  P4b whether the Hydra factor is an equal-budget comparison -- `results/S3/hydra_equal_budget.json`

Data constraint, declared rather than worked around: no committed artifact carries the per-tree
`tau_i` of the ARF. `runs.parquet` carries four order statistics per run --
`tau_swap^(q)` for `q in {0.10, 0.25, 0.50, 1.00}`, i.e. `tau_(1)`, `tau_(3)`, `tau_(5)`,
`tau_(10)` at `M = 10` -- with `tau_swap_q100` censored on 227 of the 2000 runs of arm `full`.
`rho` is therefore not directly estimable and is bracketed instead.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.stats as stats

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "R6_hydra_factor"))
from config import experiment_ssot as ssot  # noqa: E402
from exp_R6_hydra_survival import (BOOT_SEED, N_BOOT, RMST_TOL, km_curve,  # noqa: E402
                                   km_median, rmst)

OUT_DIR = ROOT_DIR / "results" / "S3"
R6_PARQUET = ROOT_DIR / "results/R6_hydra_factor/data/R6_hat_instrumented.parquet"
R2_DIR = ROOT_DIR / "results/R2_instrumented_blind_spot/data"
S6_RUNS = ROOT_DIR / "results/S6_synchronized_traces/data/runs.parquet"
HYDRA_CSV = ROOT_DIR / "results/audit_S7/hydra_survival.csv"

HORIZON = ssot.CENSORING_HORIZON
M_ENSEMBLE = ssot.N_MODELS
SCENARIOS = {"A": 50.0, "B": 25.0, "C": 8.0}          # R2_LAMBDAS, in the file-name order
CIF_TIMES = [25, 50, 100, 200, 400, 800, 1600, HORIZON]
D3_TOL = RMST_TOL                                      # 1e-9, as committed in D3
D4_AGREEMENT_FACTOR = 1.5                              # committed in D4
# tau_swap^(q) -> the order-statistic index it is, at M = 10. Fixed by the S6 writer's definition.
ORDER_STATS = {"tau_swap_q010": 1, "tau_swap_q025": 3, "tau_swap_q050": 5, "tau_swap_q100": 10}
# Trapezoidal quantile weights over the four available indices, normalised on [1, M].
# Declared approximation: the run mean is the average of ALL ten order statistics; six are missing.
L_WEIGHTS = np.array([1.0, 2.0, 3.5, 2.5]) / 9.0


def delta_e_of(b):
    return stats.norm.cdf(np.asarray(b, dtype=float) / np.sqrt(2.0)) - 0.5


def restricted(tau, horizon=HORIZON):
    """min(tau, t_c) with NaN read as censored AT the horizon -- never dropped."""
    tau = np.asarray(tau, dtype=float)
    return np.where(np.isnan(tau), float(horizon), np.minimum(tau, float(horizon)))


def rmst_identity(tau, horizon=HORIZON):
    """(RMST from Kaplan--Meier, mean(min(tau, t_c)), |deviation|) -- the D3 decision variable."""
    t = restricted(tau, horizon)
    observed = ~np.isnan(np.asarray(tau, dtype=float))
    ts, surv = km_curve(t, observed)
    r_km, r_mean = rmst(ts, surv, horizon), float(np.mean(t))
    return r_km, r_mean, abs(r_km - r_mean), km_median(ts, surv)


def race(tau_arf, tau_det, horizon=HORIZON):
    """First event and its cause. `tau_det` NaN means the detector never fired inside the horizon,
    which is a LOSS of the race, not a missing observation: the ARF is observed on every run."""
    a = np.asarray(tau_arf, dtype=float)
    d = np.where(np.isnan(np.asarray(tau_det, dtype=float)), np.inf, tau_det)
    t = np.minimum(np.minimum(a, d), float(horizon))
    cause = np.where(a < d, 1, np.where(d <= horizon, 2, 0))     # 1 = ARF, 2 = detector, 0 = censored
    return t, cause


def cif(t, cause, times, code):
    """Empirical cumulative incidence. Under a single administrative censoring at the common
    horizon the Aalen--Johansen estimator reduces to the sub-distribution proportion."""
    n = t.size
    return np.array([np.count_nonzero((t <= s) & (cause == code)) / n for s in times])


def cif_table(rng):
    rows = []
    for tag, lam in SCENARIOS.items():
        df = pd.read_parquet(R2_DIR / f"R2_instrumented_{tag}_PHT_ARF.parquet").sort_values(
            ["boundary_shift", "seed"])
        df["delta_e"] = delta_e_of(df.boundary_shift)
        for b, g in df.groupby("boundary_shift", sort=True):
            t, cause = race(g.tau_arf.to_numpy(float), g.tau_det.to_numpy(float))
            n = t.size
            idx = rng.integers(0, n, size=(N_BOOT, n))          # paired on seed: one index per run
            tb, cb = t[idx], cause[idx]
            boot_arf = np.stack([((tb <= s) & (cb == 1)).mean(axis=1) for s in CIF_TIMES], axis=1)
            boot_det = np.stack([((tb <= s) & (cb == 2)).mean(axis=1) for s in CIF_TIMES], axis=1)
            arf, det = cif(t, cause, CIF_TIMES, 1), cif(t, cause, CIF_TIMES, 2)
            lo_a, hi_a = np.percentile(boot_arf, [2.5, 97.5], axis=0)
            lo_d, hi_d = np.percentile(boot_det, [2.5, 97.5], axis=0)
            for k, s in enumerate(CIF_TIMES):
                rows.append({
                    "scenario": tag, "lambda": lam,
                    "boundary_shift": round(float(b), 6),
                    "delta_e": round(float(delta_e_of(b)), 4),
                    "t": s, "n": int(n),
                    "cif_arf": round(float(arf[k]), 4),
                    "cif_arf_lo": round(float(lo_a[k]), 4),
                    "cif_arf_hi": round(float(hi_a[k]), 4),
                    "cif_det": round(float(det[k]), 4),
                    "cif_det_lo": round(float(lo_d[k]), 4),
                    "cif_det_hi": round(float(hi_d[k]), 4),
                    # `or 0.0` normalises the -0.0 that float cancellation produces when
                    # the two incidences already sum to one.
                    "unresolved_at_t": round(float(1.0 - arf[k] - det[k]), 4) or 0.0,
                    "detector_fired_ever_frac": round(
                        float(np.count_nonzero(np.isfinite(g.tau_det.to_numpy(float))) / n), 4),
                    "detector_won_frac": round(float(np.count_nonzero(cause == 2) / n), 4),
                    "censored_frac": round(float(np.count_nonzero(cause == 0) / n), 4),
                })
    return pd.DataFrame(rows)


def d3_check(hat, arf):
    """Rule D3: the RMST identity, re-verified on the 40 cells and against the committed table."""
    committed = pd.read_csv(HYDRA_CSV, float_precision="round_trip")
    cells, worst, worst_committed = [], 0.0, 0.0
    for b, g in hat.groupby("boundary_shift", sort=True):
        de = float(delta_e_of(b))
        a = arf[arf.boundary_shift == b]
        ref = committed.iloc[int(np.argmin(np.abs(committed.delta_e.to_numpy() - de)))]
        for name, tau, ref_rmst in (("hat", g.tau_hat.to_numpy(float), float(ref.rmst_hat)),
                                    ("arf", a.tau_arf.to_numpy(float), float(ref.rmst_arf))):
            r_km, r_mean, dev, med = rmst_identity(tau)
            worst = max(worst, dev)
            worst_committed = max(worst_committed, abs(round(r_km, 4) - ref_rmst))
            cells.append({"delta_e": round(de, 4), "arm": name, "rmst_km": round(r_km, 4),
                          "rmst_mean": round(r_mean, 4), "dev": dev,
                          "committed": ref_rmst, "median": med})
    return cells, worst, worst_committed


def e_min_from_cdf(sample, m, horizon=HORIZON):
    """E[min of m i.i.d. draws from F_hat], with F_hat the censoring-aware empirical CDF.

    E[min] = int_0^{t_c} (1 - F(t))^m dt, evaluated exactly on the empirical step function. Runs
    censored at the horizon enter as values equal to t_c, so the integral is restricted and the
    result is a LOWER bound whenever the sample carries censoring.
    """
    t = np.sort(restricted(sample, horizon))
    n = t.size
    edges = np.concatenate(([0.0], t))
    surv = np.array([(np.count_nonzero(t > e) / n) for e in edges[:-1]])
    return float(np.sum(surv ** m * np.diff(edges)))


def meff_direct(e_tau_first, hat_sample, m_max=200):
    """M_eff^(b): the m whose E[min of m draws from F_hat] matches the measured E[tau_(1:M)].

    Solved on a continuous m by bisection on the (decreasing) map m -> E[min of m draws], so the
    estimator is not quantised to the integer grid.
    """
    lo, hi = 1.0, float(m_max)
    if e_min_from_cdf(hat_sample, lo) <= e_tau_first:
        return lo
    if e_min_from_cdf(hat_sample, hi) >= e_tau_first:
        return float("inf")
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if e_min_from_cdf(hat_sample, mid) > e_tau_first:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def meff_table(hat):
    """The two bracketing routes, per magnitude, plus the marginal-mismatch diagnostic of P4-bis."""
    runs = pd.read_parquet(S6_RUNS)
    full = runs[runs.arm == "full"]
    hydra = pd.read_csv(HYDRA_CSV, float_precision="round_trip")
    cols = list(ORDER_STATS)
    rows = []
    for de, g in full.groupby("delta_e", sort=True):
        q = g[cols].to_numpy(float)
        complete = ~np.isnan(q).any(axis=1)
        # (a) moments under exchangeability, on the complete cases only; the censored variant
        #     substitutes the horizon and brackets the estimate from the slow side.
        out_a = {}
        for tag, mat in (("complete", q[complete]), ("censored_at_horizon", restricted(q))):
            if mat.shape[0] < 2:
                out_a[tag] = (np.nan, np.nan)
                continue
            mu_r = mat @ L_WEIGHTS                       # L-estimator of the run mean
            m2_r = (mat ** 2) @ L_WEIGHTS                # L-estimator of the run second moment
            var_between = float(np.var(mu_r, ddof=1))
            sigma2 = float(np.mean(m2_r) - np.mean(mu_r) ** 2)
            meff = sigma2 / var_between if var_between > 0 else np.nan
            rho = ((M_ENSEMBLE / meff) - 1.0) / (M_ENSEMBLE - 1.0) if np.isfinite(meff) else np.nan
            out_a[tag] = (meff, rho)
        meff_a, rho_a = out_a["complete"]

        # (b) direct order-statistic matching against F_hat, no rho in the path
        b_shift = hat.boundary_shift.unique()[
            int(np.argmin(np.abs(delta_e_of(hat.boundary_shift.unique()) - de)))]
        tau_hat = hat.loc[hat.boundary_shift == b_shift, "tau_hat"].to_numpy(float)
        e_first = float(np.mean(restricted(g.tau_swap_q010.to_numpy(float))))
        meff_b = meff_direct(e_first, tau_hat)

        # P4-bis: is F_hat the marginal of an ARF MEMBER? The slowest member gives a second equation.
        e_last_measured = float(np.mean(restricted(g.tau_swap_q100.to_numpy(float))))
        # F22 decomposition: the acceleration the order statistics of F_hat alone predict. It is
        # exactly M when F is exponential, so the gap to M is the non-exponentiality share, and
        # the gap between the measured factor and this one is what is left for dependence and for
        # the marginal mismatch together.
        e_hat_restricted = float(np.mean(restricted(tau_hat)))
        e_min_model = e_min_from_cdf(tau_hat, M_ENSEMBLE)
        e_last_model = e_max_from_cdf(tau_hat, M_ENSEMBLE)
        ref = hydra.iloc[int(np.argmin(np.abs(hydra.delta_e.to_numpy() - de)))]
        ratio = (max(meff_a, meff_b) / min(meff_a, meff_b)
                 if np.isfinite(meff_a) and np.isfinite(meff_b) and min(meff_a, meff_b) > 0
                 else np.inf)
        rows.append({
            "delta_e": round(float(de), 4),
            "n_runs": int(len(g)),
            "n_complete_q100": int(complete.sum()),
            "censored_frac_q100": round(float(1.0 - complete.mean()), 4),
            "E_tau_first_measured": round(e_first, 2),
            "E_tau_hat_restricted": round(e_hat_restricted, 2),
            "E_min10_model_from_Fhat": round(e_min_model, 2),
            "accel_order_only": round(e_hat_restricted / e_min_model, 4) if e_min_model > 0 else np.nan,
            "E_tau_last_measured": round(e_last_measured, 2),
            "E_tau_last_model_from_Fhat": round(e_last_model, 2),
            "marginal_mismatch_last": round(e_last_model / e_last_measured, 4)
                                      if e_last_measured > 0 else np.nan,
            "rho_hat_moments": round(float(rho_a), 4) if np.isfinite(rho_a) else np.nan,
            "M_eff_moments": round(float(meff_a), 4) if np.isfinite(meff_a) else np.nan,
            "M_eff_moments_censored": round(float(out_a["censored_at_horizon"][0]), 4)
                                      if np.isfinite(out_a["censored_at_horizon"][0]) else np.nan,
            "M_eff_direct": round(float(meff_b), 4) if np.isfinite(meff_b) else np.inf,
            "agreement_ratio": round(float(ratio), 4) if np.isfinite(ratio) else np.inf,
            "agree_under_D4": bool(np.isfinite(ratio) and ratio <= D4_AGREEMENT_FACTOR),
            "hydra_rmst_ratio": float(ref.rmst_ratio),
            "hydra_ci_lo": float(ref.rmst_ratio_ci_lo),
            "hydra_ci_hi": float(ref.rmst_ratio_ci_hi),
            "hydra_median_ratio": float(ref.median_ratio),
            "accel_residual_over_order": round(
                float(ref.rmst_ratio) / (e_hat_restricted / e_min_model), 4)
                if e_min_model > 0 else np.nan,
        })
    return pd.DataFrame(rows)


def e_max_from_cdf(sample, m, horizon=HORIZON):
    """E[max of m i.i.d. draws from F_hat] = int_0^{t_c} (1 - F(t)^m) dt, same conventions."""
    t = np.sort(restricted(sample, horizon))
    n = t.size
    edges = np.concatenate(([0.0], t))
    cdf = np.array([(np.count_nonzero(t <= e) / n) for e in edges[:-1]])
    return float(np.sum((1.0 - cdf ** m) * np.diff(edges)))


def demo():
    """Self-check: the identities and the degenerate inputs the conclusions rest on."""
    tau = np.array([10.0, 20.0, np.nan])
    assert np.array_equal(restricted(tau, 100), np.array([10.0, 20.0, 100.0]))
    r_km, r_mean, dev, _ = rmst_identity(np.array([10.0, 20.0, 30.0]), 100)
    assert dev <= D3_TOL and abs(r_mean - 20.0) < 1e-12
    r_km, r_mean, dev, _ = rmst_identity(tau, 100)          # one censored AT the horizon
    assert dev <= D3_TOL, dev
    # A degenerate sample: every draw equal -> E[min of m] = E[max of m] = that value, any m.
    flat = np.full(50, 7.0)
    assert abs(e_min_from_cdf(flat, 5, 100) - 7.0) < 1e-9
    assert abs(e_max_from_cdf(flat, 5, 100) - 7.0) < 1e-9
    # m = 1 returns the restricted mean of the sample itself.
    s = np.array([1.0, 3.0, 8.0, 20.0])
    assert abs(e_min_from_cdf(s, 1, 100) - s.mean()) < 1e-9
    assert abs(e_max_from_cdf(s, 1, 100) - s.mean()) < 1e-9
    assert e_min_from_cdf(s, 5, 100) < e_min_from_cdf(s, 1, 100) < e_max_from_cdf(s, 5, 100)
    # The race: a NaN tau_det is a loss, never a censoring, because tau_arf is always observed.
    t, cause = race(np.array([10.0, 10.0]), np.array([np.nan, 5.0]), 100)
    assert list(cause) == [1, 2] and list(t) == [10.0, 5.0]
    # An exchangeable, independent synthetic sample must return M_eff close to M.
    rng = np.random.default_rng(0)
    draws = rng.exponential(100.0, size=(4000, M_ENSEMBLE))
    mat = np.sort(draws, axis=1)[:, [0, 2, 4, 9]]
    mu_r, m2_r = mat @ L_WEIGHTS, (mat ** 2) @ L_WEIGHTS
    meff = (float(np.mean(m2_r) - np.mean(mu_r) ** 2)) / float(np.var(mu_r, ddof=1))
    assert 6.0 < meff < 14.0, f"the L-estimator is biased beyond its declared range: M_eff={meff}"
    print(f"[OK] s3_competing_risks self-check: RMST identity, restricted moments, race coding, "
          f"and the L-estimator calibration (independent M=10 returns M_eff={meff:.2f})")


def main():
    if "--check" in sys.argv:
        demo()
        return 0

    hat = pd.read_parquet(R6_PARQUET).sort_values(["boundary_shift", "seed"])
    arf = pd.read_parquet(R2_DIR / "R2_instrumented_A_PHT_ARF.parquet").sort_values(
        ["boundary_shift", "seed"])

    cells, worst, worst_committed = d3_check(hat, arf)
    if worst > D3_TOL:
        raise RuntimeError(
            f"D3 HALT: the RMST identity deviates by {worst:.3e} > {D3_TOL:.0e} on the 40 cells. "
            "Censoring is not purely administrative at the common horizon; no estimator is "
            "substituted and no tolerance is widened.")

    rng = np.random.default_rng(BOOT_SEED)
    cifs = cif_table(rng)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cifs.to_csv(OUT_DIR / "cif_bands.csv", index=False)

    meff = meff_table(hat)
    meff.to_csv(OUT_DIR / "rho_meff.csv", index=False)

    # P4-bis: the equal-budget question. Branch fixed in D4-bis before the artifacts were read.
    runs = pd.read_parquet(S6_RUNS)
    e_pre = runs.groupby("arm").e_pre.agg(["mean", "std", "count"]).round(6)
    available_arms = sorted(runs.arm.unique())
    single_tree_arm = [a for a in available_arms if int(runs[runs.arm == a].n_models.iloc[0]) == 1]
    equal_budget_computable = bool(single_tree_arm)
    var_ratio = float((e_pre.loc["static", "std"] / e_pre.loc["full", "std"]) ** 2)
    anchors = meff[meff.delta_e.round(2).isin([0.14, 0.33])]
    budget = {
        "rule": "docs/prompts/s3-decision-rules.md :: D4-bis",
        "question": ("the Hydra factor compares tau_HAT (M = 1) against tau_ARF (M = 10) at a "
                     "COMMON NOMINAL internal-clock setting; S2 measured that equal-false-alarm "
                     "calibration hands the ARF a threshold 6.3x lower than the HT, so part of any "
                     "measured factor may be a calibration difference"),
        "branch": "declared gap" if not equal_budget_computable else "re-derived at equal budget",
        "verdict": "NOT PRODUCED -- the committed artifacts do not carry the inputs",
        "why": ("no committed artifact records the pre-drift error STREAM of a single tree, either "
                "standalone or inside the ARF. R6 commits tau_hat only (4 columns, no e_pre); "
                "runs.parquet commits e_pre for ensemble arms at n_models = 10 exclusively "
                f"(arms present: {available_arms}); no traces.parquet is committed. The "
                "equal-budget threshold is therefore not computable without a new campaign."),
        "sensitivity_bound_from_available_variances": {
            "e_pre_by_arm": json.loads(e_pre.to_json(orient="index")),
            "variance_ratio_static_over_full": round(var_ratio, 4),
            "reading": ("the only committed pre-drift variance contrast is adaptive-ARF (arm full) "
                        "against non-adaptive bagged HT (arm static), both at M = 10. It bounds "
                        "the effect of ADAPTATION on the pre-drift error stream, not the effect of "
                        "ENSEMBLE SIZE, and is reported as a bound of the wrong contrast rather "
                        "than as a substitute for the missing one."),
        },
        "measurable_substitute": {
            "statement": ("the marginal assimilation the manuscript makes silently -- F_hat, the "
                          "HAT's law, used as the law of a tree INSIDE the ARF -- is testable on "
                          "committed data through the slowest member: E[tau_(10)] measured on "
                          "runs.parquet against E[max of 10 draws from F_hat]"),
            "anchors": json.loads(anchors[[
                "delta_e", "E_tau_last_measured", "E_tau_last_model_from_Fhat",
                "marginal_mismatch_last", "hydra_rmst_ratio", "hydra_median_ratio"]]
                .to_json(orient="records")),
            "reading": ("a mismatch factor far from 1 says the two marginals differ, so the "
                        "measured Hydra factor mixes a marginal effect with an ensemble-minimum "
                        "effect and must not be published as a single number"),
        },
        "handed_forward": ("record the per-step pre-drift error stream of (i) a standalone HAT and "
                           "(ii) one tree inside the ARF, on matched seeds and magnitudes, then "
                           "calibrate both to one false alarm per warm-up and re-derive the factor"),
    }
    (OUT_DIR / "hydra_equal_budget.json").write_text(
        json.dumps(budget, indent=2, sort_keys=True, default=float) + "\n", encoding="utf-8")

    d4 = {
        "n_magnitudes": int(len(meff)),
        "n_agree": int(meff.agree_under_D4.sum()),
        "factor": D4_AGREEMENT_FACTOR,
        "verdict": "AGREE" if bool(meff.agree_under_D4.all()) else "DISAGREE",
    }
    summary = {
        "D3": {"tolerance": D3_TOL, "n_cells": len(cells),
               "worst_identity_deviation": worst,
               "worst_deviation_from_committed_rmst": round(worst_committed, 6),
               "verdict": "REPRODUCED"},
        "D4": d4,
        "D4bis": {"verdict": budget["verdict"], "branch": budget["branch"]},
        "P3": {
            "horizon": HORIZON,
            "detector_won_frac": {tag: round(float(
                cifs[cifs.scenario == tag].detector_won_frac.mean()), 4) for tag in SCENARIOS},
            "detector_fired_ever_frac": {tag: round(float(
                cifs[cifs.scenario == tag].detector_fired_ever_frac.mean()), 4) for tag in SCENARIOS},
            "censored_frac": round(float(cifs.censored_frac.max()), 6),
            "bootstrap": {"n_boot": N_BOOT, "seed": BOOT_SEED, "pairing": "on seed, per magnitude"},
            "reading": ("the race carries no censored unit: tau_ARF is observed on every run at "
                        "every magnitude (censored_frac_arf = 0 on all 20), so a NaN tau_det is "
                        "the detector LOSING, not a missing observation. tau_det* never enters."),
        },
    }
    (OUT_DIR / "s3_competing_risks.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True, default=float) + "\n", encoding="utf-8")

    print(f"[INFO] wrote cif_bands.csv ({len(cifs)} rows), rho_meff.csv ({len(meff)} rows), "
          f"hydra_equal_budget.json, s3_competing_risks.json")
    print(f"\n=== D3 RMST identity: worst |KM - mean| = {worst:.3e} over {len(cells)} cells "
          f"(tol {D3_TOL:.0e}) -> REPRODUCED; worst gap to committed rmst = {worst_committed:.2e}")
    print("\n=== P3 race outcome, pooled over the 20 magnitudes ===")
    for tag, lam in SCENARIOS.items():
        s = cifs[cifs.scenario == tag]
        print(f"  scenario {tag} (lambda={lam:>4.0f}): detector fires ever "
              f"{s.detector_fired_ever_frac.mean():.4f}, detector WINS {s.detector_won_frac.mean():.4f}, "
              f"censored {s.censored_frac.max():.4f}")
    print(f"\n=== D4 {d4['verdict']} ({d4['n_agree']}/{d4['n_magnitudes']} magnitudes within "
          f"the declared factor {D4_AGREEMENT_FACTOR}) ===")
    print(meff[["delta_e", "rho_hat_moments", "M_eff_moments", "M_eff_direct", "agreement_ratio",
                "marginal_mismatch_last", "hydra_rmst_ratio"]].to_string(index=False))
    print(f"\n=== D4-bis {budget['verdict']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
