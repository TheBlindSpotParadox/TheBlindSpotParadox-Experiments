"""Stream S2, Phase 1 (T2.0): stopping-time theory recomputed at the MEASURED base rate.

Pure theory on committed artifacts. No simulation, no stream is generated, nothing under
`results/` other than `results/S2_theory/tables/` is written.

`docs/theory/transfer_S1.md` L25-31 tabulates the Cramer root `theta*` and `ARL_0` for three
settings and states that no script in this repository produces them. This module is the
independent reproduction demanded by decision rule R1, and the `0.005 / p_0 = 0.05` column is its
certification: `transfer_S1` L23 states that column reproduces exactly, and that reproduction is
what licenses the other two.

THREE OBJECTS ARE CALLED `p_0` AND THEY NEVER SHARE A COLUMN HEADER.

  p_true  the classifier's actual pre-drift error rate. Measured at `ssot.P0_MEASURED = 0.024`
          (median `e_pre`, 2000 runs of arm 'full'; `p0_hat_median` flat at 0.024 across all
          twenty magnitudes of `tables/cusum_delta001_quantiles.csv`).
  p_pre   the reference rate the CUSUM recursion subtracts,
          `S_t = max(0, S_{t-1} + (x_t - p_pre) - delta)`. A DETECTOR PARAMETER, not a property
          of the stream, and passed per call site (see `PPRE_CALL_SITES` below).
  p_S1    the value stream S1 assumed, 0.05. Audited here, never registered.

`theta*` and `ARL_0` are properties of the PAIR `(p_pre, p_true)`, never of a single rate. When
`p_pre != p_true` the recursion carries a built-in drift of `p_true - p_pre` per step under the
null, and the Siegmund denominator is the resulting drift magnitude `p_pre + delta_P - p_true`,
which collapses to `delta_P` exactly when the detector is calibrated.

Outputs, all under `results/S2_theory/tables/`:
  s2_arl0_columns.csv   old/new columns, the (p_pre, p_true) census, the p_true sensitivity band
  s2_lambda_starve.csv  eq:starve_boundary per magnitude and per W estimator, at delta_P = 0.01
  s2_gate_T20.json      the lambda_FA gate verdict under R2, the thm:floor restitution, the eps
                        sensitivity, and the reproduction provenance

Usage:  PYTHONHASHSEED=0 python experiments/S2_theory/s2_arl0.py
        python experiments/S2_theory/s2_arl0.py --check     (self-check only, writes nothing)
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import brentq

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))
from config import experiment_ssot as ssot  # noqa: E402

OUT_DIR = ssot.RESULTS_DIR / "S2_theory" / "tables"
RUNS = ssot.RESULTS_DIR / "S6_synchronized_traces" / "data" / "runs.parquet"
REFERENCE_ARM = "full"

P_TRUE = ssot.P0_MEASURED                      # 0.024, measured
P_S1_ASSUMED = 0.05                            # the assumption under audit; deliberately NOT
                                               # registered -- a withdrawn value in the SSOT would
                                               # invite a call site to route through it
EPS = ssot.EPS_MISS
DELTA_P_CUSUM = ssot.CUSUM_DELTA_P             # 0.01, eq:cusum / \DeltaPtext
DELTA_P_SUPERSEDED = ssot.DELTA_P              # 0.005. Numerically River's PageHinkley tolerance;
                                               # the superseded S1 column inherited it from the
                                               # single pre-A1 registry name (transfer_S1 item 2)
LAMBDA_LADDER = sorted(set(list(ssot.R2_LAMBDAS) + [ssot.R4_PHT_LAMBDA]))   # 8 / 15 / 25 / 50
LAMBDA_FA_EMPIRICAL = ssot.R4_PHT_LAMBDA       # 15, ProteuS pre-drift calibration

# R2's decision interval: the bootstrap bounds of lambda_op on the [0.20, 0.40] envelope.
# envelope_stats.json, lambda_op_bootstrap./0.20_0.40, 10000 replicates, seed 12345.
LAMBDA_OP_CI = (19.876, 22.398)
LAMBDA_OP_POINT = 21.9283                      # reported, never the decision variable

# W estimators, arm 'full', per magnitude. Column -> label used in every table.
W_ESTIMATORS = {"tau_swap_q010": "tau_swap^(1/M)",
                "tau_erase": "tau_erase (argmax A_unrefl)",
                "tau_err_rho010": "tau_err(0.10)"}

# Call-site census of p_pre, established from source, not assumed. `p_true` is 0.024 throughout.
PPRE_CALL_SITES = {
    "R1 external fixed  (exp_R1_generate_data.py:56)": "0.05 literal -- p_pre != p_true",
    "R1 external empirical (exp_R1_generate_data.py:81)": "mean of the 1000-step warm-up",
    "R2 external (exp_R2_instrumented_blind_spot.py:90)": "mean of the warm-up, 0.05 if empty",
    "S6 audit (s6_recompute_cusum_delta001.py:partition)": "p0_hat per (arm, seed), own warm-up",
    "R3 / R4 / R5": "no p_pre -- River PageHinkley tracks its own mean, delta = 0.005",
}

# transfer_S1 L25-31, the column under reproduction (R1a), and L61-63 (R1b).
TRANSFER_S1_CLAIM = {
    (DELTA_P_SUPERSEDED, P_S1_ASSUMED): {"theta": 0.1983, "arl0": {8.0: 2.3e3, 25.0: 1.4e5, 50.0: 2.0e7}},
    (DELTA_P_CUSUM, P_S1_ASSUMED): {"theta": 0.3755, "arl0": {8.0: 4.3e3, 25.0: 3.2e6, 50.0: 3.8e10}},
    (DELTA_P_CUSUM, P_TRUE): {"theta": 0.6813, "arl0": {8.0: 3.3e4, 25.0: 3.7e9, 50.0: 9.1e16}},
}
R1_THETA_TOL = 1e-3                            # relative, decision rule R1(a)


def cramer_root(p_true, p_pre, delta):
    """theta* > 0 solving E[exp(theta (X - p_pre - delta))] = 1 for X ~ Bern(p_true).

    (1-p_true) e^{-theta a} + p_true e^{theta b} = 1 with a := p_pre + delta, b := 1 - a.
    g is convex with g(0) = 0 and g'(0) = p_true - p_pre - delta, so a positive root exists iff the
    null drift is negative and a positive increment is attainable. The trivial root is excluded by
    bracketing strictly above zero. Returns inf when no positive excursion is possible (p_true = 0:
    the reflected statistic never leaves zero and ARL_0 is infinite by construction)."""
    a = p_pre + delta
    b = 1.0 - a
    if p_true <= 0.0 or b <= 0.0:
        return np.inf
    if p_true - a >= 0.0:
        raise ValueError(f"non-negative null drift p_true - p_pre - delta = {p_true - a:.6g}: "
                         "the CUSUM has no Cramer root and ARL_0 is not defined")

    def g(theta):
        return (1.0 - p_true) * np.exp(-theta * a) + p_true * np.exp(theta * b) - 1.0

    lo, hi = 1e-9, 1.0
    while g(hi) < 0.0:
        hi *= 2.0
        if hi > 600.0 / b:
            return np.inf
    return float(brentq(g, lo, hi, xtol=1e-14, rtol=1e-15, maxiter=500))


def arl0(lam, theta, drift):
    """Siegmund (1985): ARL_0 = (exp(theta lambda) - theta lambda - 1) / (theta * drift).

    `drift` is the magnitude of the mean increment under the null, p_pre + delta_P - p_true, which
    equals delta_P exactly when the detector is calibrated (p_pre = p_true)."""
    if not np.isfinite(theta):
        return np.inf
    tl = theta * lam
    return float(np.expm1(tl) - tl) / (theta * drift)


def arl0_inverse(target, theta, drift):
    """lambda such that arl0(lambda, theta, drift) == target. Monotone increasing in lambda."""
    f = lambda lam: arl0(lam, theta, drift) - target      # noqa: E731
    hi = 1.0
    while f(hi) < 0.0:
        hi *= 2.0
        if hi > 1e4:
            raise ValueError("ARL_0 target unreachable below lambda = 1e4")
    return float(brentq(f, 0.0, hi, xtol=1e-12, rtol=1e-14, maxiter=500))


def kl_binary(a, b):
    """d(a || b) = a ln(a/b) + (1-a) ln((1-a)/(1-b)), the binary Kullback-Leibler divergence."""
    return a * np.log(a / b) + (1.0 - a) * np.log((1.0 - a) / (1.0 - b))


def detection_floor(p0, delta_max, w, alpha, eps=EPS, delta_p=DELTA_P_CUSUM):
    """RHS of eq:floor -- p0(1-p0)/Delta_max * d(1-eps || alpha) - W delta_P.

    p0 here is the pre-change error rate of thm:floor, i.e. p_true. The factor p0(1-p0) is the
    per-step variance that the chain-rule bound d(x||y) <= (x-y)^2/(y(1-y)) puts in the DENOMINATOR
    of the KL upper bound, so the floor collapses to -W delta_P as p0 -> 0 or p0 -> 1: the bound
    becomes vacuous at both ends, it does not tighten."""
    return p0 * (1.0 - p0) / delta_max * kl_binary(1.0 - eps, alpha) - w * delta_p


def detection_floor_chord(p0, delta_max, w, alpha, eps=EPS, delta_p=DELTA_P_CUSUM):
    """thm:floor with the chi-square relaxation replaced by the chord bound on a convex map.

    The proof of thm:floor bounds each term of the chain rule by
    d(x || y) <= (x-y)^2 / (y(1-y)), the chi-square relaxation. But u |-> d(p_0 + u || p_0) is
    CONVEX on [0, Delta_max] and vanishes at u = 0, so the chord through the endpoints already
    gives d(p_0 + u || p_0) <= (u / Delta_max) d(p_0 + Delta_max || p_0), hence

        KL(P_1 || P_0) <= (d_max / Delta_max) (A + W delta_P),
        A >= Delta_max d(1 - eps || alpha) / d_max - W delta_P,   d_max := d(p_0 + Delta_max||p_0).

    This is never weaker than eq:floor -- d_max <= Delta_max^2/(p_0(1-p_0)) is the same chi-square
    bound applied once instead of W times -- and the gap is the audit finding: the relaxation is
    loosest exactly where the measured base rate now sits."""
    d_max = kl_binary(p0 + delta_max, p0)
    return delta_max / d_max * kl_binary(1.0 - eps, alpha) - w * delta_p


def lambda_starve(w, mu, eps=EPS, s0=0.0):
    """eq:starve_boundary -- lambda >= s_0 + mu W + sqrt(W/2 ln(W/eps)).

    s_0 is the pre-drift value of the reflected statistic at tau*. It is the ONLY channel through
    which p_0 enters this boundary: mu = Delta_e - delta_P and the fluctuation margin carry no base
    rate. transfer_S1 L62 evaluates it at s_0 = 0 and that convention is kept here, so the move
    against L62 is attributable to W and to delta_P alone."""
    w = np.asarray(w, dtype=np.float64)
    margin = np.where(w > 0.0, np.sqrt(w / 2.0 * np.log(np.maximum(w, 1e-300) / eps)), 0.0)
    return s0 + mu * w + margin


def windows():
    """Per-magnitude mean of each W estimator and median evidence ceiling on arm 'full'."""
    df = pd.read_parquet(RUNS, columns=["arm", "delta_e", "e_pre", "a_unrefl_peak", *W_ESTIMATORS])
    f = df[df.arm == REFERENCE_ARM]
    g = f.groupby("delta_e")
    return g[list(W_ESTIMATORS)].mean(), g["a_unrefl_peak"].median(), f["e_pre"]


def columns_table(band):
    """The old/new column table, the (p_pre, p_true) census row, and the sensitivity band.

    `band` is (lo, hi) from `sensitivity_band`: a named quantile pair of a named estimator, never a
    range asserted without provenance."""
    lo, hi = band
    settings = [
        ("superseded", DELTA_P_SUPERSEDED, P_S1_ASSUMED, P_S1_ASSUMED),
        ("A1", DELTA_P_CUSUM, P_S1_ASSUMED, P_S1_ASSUMED),
        ("principal (S2)", DELTA_P_CUSUM, P_TRUE, P_TRUE),
        ("R1 fixed arm", DELTA_P_CUSUM, P_S1_ASSUMED, P_TRUE),
        ("band q0.025", DELTA_P_CUSUM, lo, lo),
        ("band q0.975", DELTA_P_CUSUM, hi, hi),
    ]
    rows = []
    for label, delta, p_pre, p_true in settings:
        theta = cramer_root(p_true, p_pre, delta)
        drift = p_pre + delta - p_true
        claim = TRANSFER_S1_CLAIM.get((delta, p_pre)) if p_pre == p_true else None
        row = {"setting": label, "delta_P": delta, "p_pre": p_pre, "p_true": p_true,
               "calibrated": p_pre == p_true, "null_drift": round(drift, 6),
               "theta_star": round(theta, 6),
               "approx_2dp_over_var": round(2.0 * delta / (p_true * (1.0 - p_true)), 6),
               "theta_star_S1": claim["theta"] if claim else None}
        row["approx_rel_error_pct"] = round(
            100.0 * (row["approx_2dp_over_var"] - theta) / theta, 1)
        for lam in LAMBDA_LADDER:
            row[f"ARL0_lambda{lam:g}"] = arl0(lam, theta, drift)
            row[f"ARL0_lambda{lam:g}_S1"] = (claim["arl0"].get(lam) if claim else None)
        rows.append(row)
    return pd.DataFrame(rows)


def sensitivity_band(e_pre):
    """Named estimator, named quantiles. transfer_S1 asserts a [0.012, 0.040] range with no stated
    provenance; this identifies it and replaces it with a quantile band that has one."""
    q = e_pre.quantile([0.025, 0.25, 0.5, 0.75, 0.975])
    return {"estimator": "empirical quantiles of e_pre over the 2000 runs of arm 'full' "
                         "(per-run pre-drift rate on the 1000-step warm-up, resolution 1e-3)",
            "n": int(e_pre.size),
            "min": float(e_pre.min()), "max": float(e_pre.max()),
            "q02p5": float(q.loc[0.025]), "q25": float(q.loc[0.25]), "median": float(q.loc[0.5]),
            "q75": float(q.loc[0.75]), "q97p5": float(q.loc[0.975]),
            "band_used": [float(q.loc[0.025]), float(q.loc[0.975])],
            "band_definition": "central 95 % of the per-run distribution (q0.025, q0.975)",
            "transfer_S1_asserted_range": [0.012, 0.040],
            "transfer_S1_range_identified_as":
                "the per-run MIN and MAX of the same column, not a quantile band and not the "
                "per-magnitude dispersion of the median, which is flat at 0.024 on all 20 points"}


def gate_verdict(band):
    """R2. Both readings of lambda_FA, and the verdict carried by the declared one."""
    theta_s1 = cramer_root(P_S1_ASSUMED, P_S1_ASSUMED, DELTA_P_CUSUM)
    theta_s2 = cramer_root(P_TRUE, P_TRUE, DELTA_P_CUSUM)
    target = arl0(LAMBDA_FA_EMPIRICAL, theta_s1, DELTA_P_CUSUM)
    lam_theoretical = arl0_inverse(target, theta_s2, DELTA_P_CUSUM)

    lo, hi = LAMBDA_OP_CI
    rule = lambda x: "EMPTY" if x > hi else ("NON-EMPTY" if x < lo else "UNDECIDED")  # noqa: E731
    over_band = [{"p_true": p,
                  "lambda_FA_ARL": arl0_inverse(target, cramer_root(p, p, DELTA_P_CUSUM),
                                                DELTA_P_CUSUM),
                  "verdict": rule(arl0_inverse(target, cramer_root(p, p, DELTA_P_CUSUM),
                                               DELTA_P_CUSUM))}
                 for p in band]
    return {"rule": "R2",
            "theoretical_over_sensitivity_band": over_band,
            "verdict_invariant_over_band": len({r["verdict"] for r in over_band}) == 1,
            "lambda_op_interval": list(LAMBDA_OP_CI),
            "lambda_op_point_estimate_NOT_the_decision_variable": LAMBDA_OP_POINT,
            "empirical": {"lambda_FA": float(LAMBDA_FA_EMPIRICAL),
                          "provenance": "R4_PHT_LAMBDA, ProteuS pre-drift calibration "
                                        "(\\LambdaFA); invariant by construction",
                          "verdict": rule(float(LAMBDA_FA_EMPIRICAL))},
            "theoretical": {"target_ARL0": target,
                            "target_definition": f"ARL_0(lambda = {LAMBDA_FA_EMPIRICAL:g}) at "
                                                 f"p_pre = p_true = {P_S1_ASSUMED}, "
                                                 f"delta_P = {DELTA_P_CUSUM}",
                            "theta_star_at_p_S1": theta_s1, "theta_star_at_p_true": theta_s2,
                            "lambda_FA_ARL": lam_theoretical,
                            "verdict": rule(lam_theoretical)},
            "verdict_carried_by": "empirical",
            "verdict_carried_by_reason":
                "lambda_FA is a calibration measured on ProteuS pre-drift volatility, not a "
                "quantity derived from ARL_0. Recomputing ARL_0 at the measured base rate changes "
                "what a given threshold buys in false-alarm time; it does not move a threshold "
                "that was set by measurement. The theoretical reading is reported as the "
                "consistency check it is.",
            "verdict": rule(float(LAMBDA_FA_EMPIRICAL)),
            "concordant": rule(float(LAMBDA_FA_EMPIRICAL)) == rule(lam_theoretical)}


def budget_restitution(ceiling):
    """T2.0(d) line 1. The claimed plateau, restated against the measured evidence ceiling rather
    than re-evaluated through the withdrawn rectangular surrogate."""
    band = ceiling[(ceiling.index >= 0.10) & (ceiling.index <= 0.50)]
    return {"claim_transfer_S1": {"K": 18.5, "alpha_exp": 0.98, "A_band": [16.8, 18.1],
                                  "over_delta_e": [0.10, 0.50],
                                  "surpassed_by": "the rectangular surrogate "
                                                  "A = q(tau_ARF)(Delta_e - delta_P), withdrawn "
                                                  "at .tex L385"},
            "measured": {"statistic": "median max_t A_unrefl, arm 'full' "
                                      "(runs.parquet:a_unrefl_peak)",
                         "over_delta_e": [float(band.index.min()), float(band.index.max())],
                         "min": float(band.min()), "max": float(band.max()),
                         "ratio_max_over_min": float(band.max() / band.min()),
                         "argmax_delta_e": float(band.idxmax()),
                         "monotone": bool(np.all(np.diff(band.to_numpy()) > 0)
                                          or np.all(np.diff(band.to_numpy()) < 0)),
                         "per_magnitude": {f"{k:.6f}": float(v) for k, v in ceiling.items()}},
            "verdict": "the profile is a hump peaking near Delta_e = 0.19 and declining "
                       "thereafter, not the claimed plateau; the constant sits above the claimed "
                       "band at every magnitude of the envelope"}


def floor_restitution():
    """T2.0(d) line 3. transfer_S1 L63 states the universal floor at two operating points, with
    alpha = W/ARL_0; both are recomputed at the new ARL_0 and against L63's own inputs."""
    theta_s1 = cramer_root(P_S1_ASSUMED, P_S1_ASSUMED, DELTA_P_SUPERSEDED)
    theta_s2 = cramer_root(P_TRUE, P_TRUE, DELTA_P_CUSUM)
    out = []
    for delta_e, w, claimed in ((0.33, 55.0, 1.45), (0.10, 13.0, 4.56)):
        a_s1 = arl0(50.0, theta_s1, DELTA_P_SUPERSEDED)
        a_s2 = arl0(50.0, theta_s2, DELTA_P_CUSUM)
        out.append({
            "delta_e": delta_e, "W": w, "lambda": 50.0,
            "transfer_S1_value": claimed,
            "S1_inputs": {"p_0": P_S1_ASSUMED, "delta_P": DELTA_P_SUPERSEDED, "ARL_0": a_s1,
                          "alpha": w / a_s1},
            "floor_at_S1_inputs": detection_floor(P_S1_ASSUMED, delta_e, w, w / a_s1,
                                                  delta_p=DELTA_P_SUPERSEDED),
            "S2_inputs": {"p_0": P_TRUE, "delta_P": DELTA_P_CUSUM, "ARL_0": a_s2,
                          "alpha": w / a_s2},
            "floor_at_S2_inputs": detection_floor(P_TRUE, delta_e, w, w / a_s2),
            "rectangular_surrogate_budget_S1": (delta_e - DELTA_P_SUPERSEDED) * w,
        })
    for r in out:
        r["reproduces_R1b"] = bool(abs(r["floor_at_S1_inputs"] - r["transfer_S1_value"]) < 5e-3)
    return out


def eps_sensitivity(w=57.4, delta_e=0.326793):
    """eps is assumed, never measured. ARL_0 carries NO eps dependence -- reporting one would be
    invention. The two quantities that do depend on it are reported instead."""
    theta = cramer_root(P_TRUE, P_TRUE, DELTA_P_CUSUM)
    a = arl0(50.0, theta, DELTA_P_CUSUM)
    mu = delta_e - DELTA_P_CUSUM
    return {"note": "ARL_0 = (exp(theta lambda) - theta lambda - 1)/(theta delta_P) contains no "
                    "eps. eps enters thm:floor through d(1-eps||alpha) and eq:starve_boundary "
                    "through sqrt(W/2 ln(W/eps)).",
            "at": {"W": w, "delta_e": delta_e, "lambda": 50.0, "ARL_0": a},
            "per_eps": [{"eps": e,
                         "floor": detection_floor(P_TRUE, delta_e, w, w / a, eps=e),
                         "lambda_starve": float(lambda_starve(w, mu, eps=e))}
                        for e in (0.01, 0.05, 0.10)]}


def floor_and_family(band, ceiling, w=57.4, delta_e=0.326793, lam=50.0,
                     n_stat=30, kswin_alpha=None):
    """thm:floor as an INTERVAL over the p_true band, and the three family requirements.

    ARL_0 moves nine orders of magnitude across the band, so no scalar evaluation of the floor is
    reportable. The floor depends on ARL_0 only through ln(1/alpha), which is why the interval it
    induces is narrow: that is a property of the bound, and it is the reason the floor can be
    stated robustly where ARL_0 itself cannot."""
    kswin_alpha = ssot.R4_KSWIN_ALPHA if kswin_alpha is None else kswin_alpha
    rows = []
    for p in sorted({band[0], P_TRUE, band[1]}):
        theta = cramer_root(p, p, DELTA_P_CUSUM)
        a = arl0(lam, theta, DELTA_P_CUSUM)
        alpha = w / a
        rows.append({"p_true": p, "theta_star": theta, "ARL_0": a, "alpha": alpha,
                     "floor_chi2": detection_floor(p, delta_e, w, alpha),
                     "floor_chord": detection_floor_chord(p, delta_e, w, alpha),
                     "kl_exact_at_delta_max": kl_binary(p + delta_e, p),
                     "kl_chi2_at_delta_max": delta_e ** 2 / (p * (1 - p))})
    for r in rows:
        r["chi2_looseness_factor"] = r["kl_chi2_at_delta_max"] / r["kl_exact_at_delta_max"]

    # Family requirements. cor:split compares three monitors, so they must be read at the SAME
    # windowed false-alarm level -- that is the whole purpose of def:monitor. Evaluating KSWIN at
    # its deployed alpha while ADWIN inherits the CUSUM's would compare calibrations, not families.
    margin = np.sqrt(w / 2.0 * np.log(1.0 / EPS))
    theta = cramer_root(P_TRUE, P_TRUE, DELTA_P_CUSUM)
    ceil_here = float(ceiling.loc[ceiling.index[np.argmin(np.abs(ceiling.index - delta_e))]])

    ladder = []
    for lam_i in LAMBDA_LADDER:
        a_i = w / arl0(lam_i, theta, DELTA_P_CUSUM)
        r = {"lambda_cusum": lam_i, "alpha": a_i, "log_1_over_alpha": float(np.log(1.0 / a_i)),
             "R_CUSUM": lam_i + margin,
             "R_ADWIN": float(np.sqrt(w / 2.0 * np.log(4.0 * w / a_i)) + margin),
             "R_KSWIN": float(np.sqrt(n_stat * np.log(2.0 / a_i)) + margin)}
        r["met_by"] = {k: bool(ceil_here >= v) for k, v in r.items() if k.startswith("R_")}
        ladder.append(r)

    req = {"epsilon_margin_sqrt_W_over_2_log_1_over_eps": margin,
           "common_alpha_ladder": ladder,
           "n_stat": n_stat,
           "deployed_alphas": {
               "KSWIN_R4": kswin_alpha, "ADWIN_R4": ssot.R4_ADWIN_DELTA,
               "R_KSWIN_at_deployed_alpha":
                   float(np.sqrt(n_stat * np.log(2.0 / kswin_alpha)) + margin),
               "note": "the deployed detectors do NOT share a false-alarm level: KSWIN runs at "
                       "alpha = 0.005 and ADWIN at delta = 0.002, while a lambda = 50 CUSUM at "
                       "this base rate runs at alpha ~ 6e-16. The measured F1 separation is "
                       "therefore not a like-for-like family comparison, and cor:split's content "
                       "is the SCALING in ln(1/alpha), not a verdict at one operating point."},
           "scaling": {
               "R_CUSUM": "lambda(alpha) = ln(1/alpha)/theta* (1+o(1)): LINEAR in ln(1/alpha), "
                          "and free of W",
               "R_ADWIN": "sqrt(W/2 ln(4W/alpha)): SQUARE ROOT of ln(1/alpha), and vanishes "
                          "with W",
               "R_KSWIN": "sqrt(n_stat ln(2/alpha)): SQUARE ROOT of ln(1/alpha), and free of W "
                          "-- eq:Rkswin carries no W in its alpha term, which cor:split as "
                          "written asserts that it does",
               "theta_star_inverse": float(1.0 / theta)},
           "measured_ceiling_median_A_unrefl": ceil_here}
    return {"at": {"delta_e": delta_e, "W": w, "lambda": lam, "eps": EPS,
                   "band": list(band)},
            "floor_over_band": rows,
            "floor_chi2_interval": [min(r["floor_chi2"] for r in rows),
                                    max(r["floor_chi2"] for r in rows)],
            "floor_chord_interval": [min(r["floor_chord"] for r in rows),
                                     max(r["floor_chord"] for r in rows)],
            "family_requirements": req,
            "reading": "the floor is logarithmic in ARL_0, so nine orders of magnitude of "
                       "uncertainty on ARL_0 collapse to a narrow interval on the floor. At the "
                       "canonical operating point the measured ceiling clears the floor but not "
                       "R_CUSUM, and clears R_KSWIN: the blind spot at lambda = 50 is a property "
                       "of the monitor's calibration, not an information-theoretic limit."}


def flooding_retrodiction():
    """T2.3. Can an ARL_0 model recover the 86 alarms of INSECTS gradual_balanced?

    `rem:flooding` states the flooding count as a consequence of the internal ADWIN clock. Two
    models are put to the artifact, and both are reported whatever they return.

      (A) ARL_0 model, as the task specifies it: alarms ~ (stream length)/ARL_0 at the recomputed
          ARL_0, p_true = 0.024, delta_P = 0.01, lambda = R4_PHT_LAMBDA = 15.
      (B) re-arm model: after a change the error rate does NOT return to p_pre on this stream, so
          a monitor re-armed after each alarm crosses lambda deterministically every
          lambda / (e_post - p_pre - delta_P) steps.

    DECLARED CAVEAT. R4 and R5 run River's adaptive mean-tracking PageHinkley at DELTA_P = 0.005,
    not the fixed-p_0 StrictCUSUM of eq:cusum at 0.01; the manuscript already states that
    distinction. Both models below are therefore order-of-magnitude consistency checks on a
    different estimator, and are labelled as such. Neither is a fit."""
    epi = pd.read_parquet(ssot.RESULTS_DIR / "R5_real_world_evaluation" / "data"
                          / "insects_per_episode.parquet")
    g = epi[epi.variant == "gradual_balanced"]
    n_total = float(g.n_total.median())
    drift_pos = float(g.drift_pos.median())
    warmup = n_total * 0.10                     # exp_R5_config.INSECTS_WARMUP_FRACTION
    post = n_total - drift_pos
    null_span = drift_pos - warmup              # armed, pre-change: the only span ARL_0 governs

    theta = cramer_root(P_TRUE, P_TRUE, DELTA_P_CUSUM)
    a15 = arl0(LAMBDA_FA_EMPIRICAL, theta, DELTA_P_CUSUM)

    out = {"stream": {"variant": "gradual_balanced", "n_total": n_total, "drift_pos": drift_pos,
                      "warmup_steps": warmup, "armed_pre_change_span": null_span,
                      "post_change_span": post, "tau_tol": float(g.tau_tol.median()),
                      "delta_e": 0.450341},
           "model_A_ARL0": {
               "definition": "E[alarms] = armed pre-change span / ARL_0",
               "p_true": P_TRUE, "delta_P": DELTA_P_CUSUM,
               "lambda": float(LAMBDA_FA_EMPIRICAL), "ARL_0": a15,
               "expected_alarms": null_span / a15},
           "pipelines": []}

    for pipe in ("pht_arf_c1", "pht_ht"):
        s = g[g.pipeline == pipe]
        e_pre, e_post = float(s.e_pre.median()), float(s.e_post.median())
        lam = float(s.lambda_calibrated.mean())
        measured = float(s.n_detections_total.mean())
        rate = e_post - e_pre - DELTA_P_SUPERSEDED
        out["pipelines"].append({
            "pipeline": pipe, "e_pre": e_pre, "e_post": e_post,
            "lambda_calibrated_mean": lam,
            "lambda_calibrated_min": float(s.lambda_calibrated.min()),
            "lambda_calibrated_max": float(s.lambda_calibrated.max()),
            "measured_alarms_mean": measured,
            "measured_false_alarms_mean": float(s.run_n_fp.mean()),
            "measured_precision_median": float(s.run_precision.median()),
            "model_B_accumulation_rate_per_step": rate,
            "model_B_steps_per_alarm": lam / rate if rate > 0 else np.inf,
            "model_B_expected_alarms": post * rate / lam if rate > 0 else np.inf,
        })

    arf, ht = out["pipelines"]
    out["verdict"] = {
        "model_A_ratio_predicted_over_measured":
            out["model_A_ARL0"]["expected_alarms"] / arf["measured_alarms_mean"],
        "model_B_ratio_predicted_over_measured_arf":
            arf["model_B_expected_alarms"] / arf["measured_alarms_mean"],
        "model_B_ratio_predicted_over_measured_ht":
            ht["model_B_expected_alarms"] / ht["measured_alarms_mean"],
        "measured_alarm_ratio_arf_over_ht":
            arf["measured_alarms_mean"] / ht["measured_alarms_mean"],
        "model_B_predicted_alarm_ratio":
            arf["model_B_expected_alarms"] / ht["model_B_expected_alarms"],
        "threshold_ratio_ht_over_arf": ht["lambda_calibrated_mean"] / arf["lambda_calibrated_mean"],
        "reading": "the ARL_0 model is out by four orders of magnitude because 84.7 of the 85.7 "
                   "alarms are not null-regime false alarms: they occur after a genuine change, "
                   "in a regime whose error rate is 0.50 against a reference of 0.058. The "
                   "re-arm model recovers both counts to a factor of 2-4 and their ratio to a "
                   "factor of 1.7, using no fitted constant. The threshold is not shared: the "
                   "one-false-alarm-per-warm-up calibration hands the ARF 20.97 and the HT "
                   "132.50, a factor of 6.3 that the pipelines' pre-change volatility fixes, "
                   "not their post-change behaviour.",
    }
    return out


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    w_table, ceiling, e_pre = windows()

    band = sensitivity_band(e_pre)
    cols = columns_table(band["band_used"])
    cols.to_csv(OUT_DIR / "s2_arl0_columns.csv", index=False)

    rows = []
    for delta_e, w in w_table.iterrows():
        mu = delta_e - DELTA_P_CUSUM
        for col, label in W_ESTIMATORS.items():
            rows.append({"delta_e": round(delta_e, 6), "W_estimator": label,
                         "W_mean": round(float(w[col]), 2), "mu": round(mu, 6),
                         "mu_W": round(mu * float(w[col]), 2),
                         "fluctuation_margin": round(
                             float(lambda_starve(float(w[col]), mu)) - mu * float(w[col]), 2),
                         "lambda_starve": round(float(lambda_starve(float(w[col]), mu)), 2)})
    starve = pd.DataFrame(rows)
    starve.to_csv(OUT_DIR / "s2_lambda_starve.csv", index=False)

    floors = floor_restitution()
    gate = gate_verdict(band["band_used"])
    r1a = {}
    for name, (d, p) in (("superseded", (DELTA_P_SUPERSEDED, P_S1_ASSUMED)),
                         ("A1", (DELTA_P_CUSUM, P_S1_ASSUMED)),
                         ("principal", (DELTA_P_CUSUM, P_TRUE))):
        claim, theta = TRANSFER_S1_CLAIM[(d, p)], cramer_root(p, p, d)
        rel = abs(theta - claim["theta"]) / claim["theta"]
        sig = {f"lambda{lam:g}": _same_sig_fig(arl0(lam, theta, d), v)
               for lam, v in claim["arl0"].items()}
        r1a[name] = {"delta_P": d, "p_0": p, "theta_rel_error": rel,
                     "theta_within_1e-3": bool(rel <= R1_THETA_TOL),
                     "arl0_same_first_sig_fig": sig,
                     "verdict": "REPRODUCED" if rel <= R1_THETA_TOL and all(sig.values())
                                else "UNREPRODUCED"}
    payload = {
        "gate_T2_0": gate,
        "p_pre_call_sites": PPRE_CALL_SITES,
        "p_true_sensitivity": band,
        "eps_sensitivity": eps_sensitivity(),
        "budget_restitution": budget_restitution(ceiling),
        "floor_restitution": floors,
        "floor_and_family": floor_and_family(band["band_used"], ceiling),
        # No absolute path is recorded: the interpreter is pinned in docs/ENVIRONMENT.md, and an
        # artifact carrying a server path is not portable evidence.
        "reproduction": {"python": sys.version.split()[0],
                         "artifact": str(RUNS.relative_to(ROOT_DIR)),
                         "command": "PYTHONHASHSEED=0 python experiments/S2_theory/s2_arl0.py"},
        "R1a": r1a,
    }
    (OUT_DIR / "s2_gate_T20.json").write_text(json.dumps(payload, indent=2, sort_keys=True,
                                                         default=float) + "\n", encoding="utf-8")
    flood = flooding_retrodiction()
    (OUT_DIR / "s2_flooding_retrodiction.json").write_text(
        json.dumps(flood, indent=2, sort_keys=True, default=float) + "\n", encoding="utf-8")

    pd.set_option("display.width", 200)
    print("=== T2.0 columns: theta*, ARL_0 -- Cramer root, Siegmund (1985) ===")
    show = ["setting", "delta_P", "p_pre", "p_true", "null_drift", "theta_star", "theta_star_S1",
            "approx_2dp_over_var", "approx_rel_error_pct"]
    print(cols[show].to_string(index=False))
    print()
    print(cols[["setting"] + [f"ARL0_lambda{l:g}" for l in LAMBDA_LADDER]]
          .to_string(index=False, float_format=lambda v: f"{v:.3g}"))
    print()
    print("=== T2.0 gate -- rule R2 ===")
    print(f"  lambda_op interval           {LAMBDA_OP_CI}   (point {LAMBDA_OP_POINT}, not the "
          f"decision variable)")
    print(f"  empirical   lambda_FA      = {gate['empirical']['lambda_FA']:.4f}  -> "
          f"{gate['empirical']['verdict']}")
    print(f"  theoretical lambda_FA^ARL  = {gate['theoretical']['lambda_FA_ARL']:.4f}  -> "
          f"{gate['theoretical']['verdict']}   "
          f"(target ARL_0 = {gate['theoretical']['target_ARL0']:.4g})")
    print("  theoretical over the p_true band  " + ", ".join(
        f"p={r['p_true']:.3f} -> {r['lambda_FA_ARL']:.2f} ({r['verdict']})"
        for r in gate["theoretical_over_sensitivity_band"]))
    print(f"  VERDICT = {gate['verdict']}   carried by the {gate['verdict_carried_by']} reading; "
          f"readings concordant: {gate['concordant']}; "
          f"invariant over the band: {gate['verdict_invariant_over_band']}")
    print()
    print("=== T2.0(d) line 2 -- lambda_starve at delta_P = 0.01, W from the S6 artifact ===")
    print(starve.pivot(index="delta_e", columns="W_estimator", values="lambda_starve")
          .to_string(float_format=lambda v: f"{v:.1f}"))
    print()
    b = payload["budget_restitution"]["measured"]
    print("=== T2.0(d) line 1 -- budget invariance, restated on the measured ceiling ===")
    print(f"  claimed K = 18.5, A in [16.8, 18.1] (plateau) over Delta_e in [0.10, 0.50]")
    print(f"  measured median max_t A_unrefl over [{b['over_delta_e'][0]:.4f}, "
          f"{b['over_delta_e'][1]:.4f}]: {b['min']:.2f} to {b['max']:.2f}, factor "
          f"{b['ratio_max_over_min']:.2f}, peak at Delta_e = {b['argmax_delta_e']:.4f}, "
          f"monotone = {b['monotone']}")
    print()
    print("=== T2.0(d) line 3 -- universal floor, alpha = W/ARL_0 at lambda = 50 ===")
    for r in floors:
        print(f"  Delta_e = {r['delta_e']:.2f}, W = {r['W']:.0f}: "
              f"transfer_S1 {r['transfer_S1_value']:.2f} | at S1 inputs "
              f"{r['floor_at_S1_inputs']:.3f} (reproduces: {r['reproduces_R1b']}) | "
              f"at S2 inputs {r['floor_at_S2_inputs']:.3f}")
    print()
    ff = payload["floor_and_family"]
    print("=== T2.5(c) thm:floor audited at the measured base rate, stated over the band ===")
    for r in ff["floor_over_band"]:
        print(f"  p_true = {r['p_true']:.3f}  ARL_0 = {r['ARL_0']:.3g}  alpha = {r['alpha']:.3g}  "
              f"floor(chi2) = {r['floor_chi2']:7.3f}  floor(chord) = {r['floor_chord']:7.3f}  "
              f"chi2 looseness = {r['chi2_looseness_factor']:.2f}x")
    print(f"  floor interval over the band: chi-square "
          f"[{ff['floor_chi2_interval'][0]:.2f}, {ff['floor_chi2_interval'][1]:.2f}], chord "
          f"[{ff['floor_chord_interval'][0]:.2f}, {ff['floor_chord_interval'][1]:.2f}]")
    q = ff["family_requirements"]
    print(f"  measured ceiling {q['measured_ceiling_median_A_unrefl']:.2f}; the three "
          f"requirements at a COMMON alpha (def:monitor), margin = "
          f"{q['epsilon_margin_sqrt_W_over_2_log_1_over_eps']:.2f}")
    print(f"  {'lambda':>7s} {'alpha':>10s} {'ln(1/a)':>8s} {'R_CUSUM':>9s} {'R_ADWIN':>9s} "
          f"{'R_KSWIN':>9s}   met")
    for r in q["common_alpha_ladder"]:
        print(f"  {r['lambda_cusum']:7.0f} {r['alpha']:10.2e} {r['log_1_over_alpha']:8.2f} "
              f"{r['R_CUSUM']:9.2f} {r['R_ADWIN']:9.2f} {r['R_KSWIN']:9.2f}   "
              + ", ".join(k[2:] for k, v in r["met_by"].items() if v))
    print(f"  R_KSWIN at its DEPLOYED alpha = {q['deployed_alphas']['KSWIN_R4']}: "
          f"{q['deployed_alphas']['R_KSWIN_at_deployed_alpha']:.2f} (met: "
          f"{q['measured_ceiling_median_A_unrefl'] >= q['deployed_alphas']['R_KSWIN_at_deployed_alpha']})")
    print()
    v = flood["verdict"]
    print("=== T2.3 flooding retrodiction, INSECTS gradual_balanced ===")
    print(f"  model A (ARL_0 at p_true = {P_TRUE}, delta_P = {DELTA_P_CUSUM}, lambda = "
          f"{LAMBDA_FA_EMPIRICAL:g}): {flood['model_A_ARL0']['expected_alarms']:.4g} alarms "
          f"expected against {flood['pipelines'][0]['measured_alarms_mean']:.1f} measured "
          f"-- out by {1 / v['model_A_ratio_predicted_over_measured']:.3g}x")
    for p in flood["pipelines"]:
        print(f"  model B {p['pipeline']:12s} lambda_cal = {p['lambda_calibrated_mean']:7.2f}, "
              f"rate = {p['model_B_accumulation_rate_per_step']:.4f}/step -> "
              f"{p['model_B_expected_alarms']:6.1f} expected against "
              f"{p['measured_alarms_mean']:6.1f} measured")
    print(f"  alarm ratio ARF/HT: measured {v['measured_alarm_ratio_arf_over_ht']:.2f}x, "
          f"model B {v['model_B_predicted_alarm_ratio']:.2f}x; calibrated-threshold ratio "
          f"HT/ARF = {v['threshold_ratio_ht_over_arf']:.2f}x")
    print()
    print(f"wrote {OUT_DIR.relative_to(ROOT_DIR)}/"
          "{s2_arl0_columns.csv, s2_lambda_starve.csv, s2_gate_T20.json, "
          "s2_flooding_retrodiction.json}")
    return cols, starve, payload, flood


def _same_sig_fig(x, y):
    """True when x and y agree to one significant figure (decision rule R1a)."""
    if not (np.isfinite(x) and np.isfinite(y)) or x <= 0 or y <= 0:
        return bool(x == y)
    r = lambda v: round(v, -int(np.floor(np.log10(abs(v)))))      # noqa: E731
    return bool(r(x) == r(y))


def demo():
    """Self-check. The 0.005 / p_0 = 0.05 pair certifies the solver; the degenerate inputs of the
    statutory guard-rail certify the sign of every bound before any hypothesis is touched."""
    # 1. Certification against the column transfer_S1 L23 declares reproduces exactly.
    for (delta, p), claim in TRANSFER_S1_CLAIM.items():
        theta = cramer_root(p, p, delta)
        rel = abs(theta - claim["theta"]) / claim["theta"]
        assert rel <= R1_THETA_TOL, (delta, p, theta, claim["theta"], rel)
        for lam, v in claim["arl0"].items():
            got = arl0(lam, theta, delta)
            assert _same_sig_fig(got, v), (delta, p, lam, got, v)

    # 2. The root solves its own defining equation.
    th = cramer_root(P_TRUE, P_TRUE, DELTA_P_CUSUM)
    a = P_TRUE + DELTA_P_CUSUM
    assert abs((1 - P_TRUE) * np.exp(-th * a) + P_TRUE * np.exp(th * (1 - a)) - 1.0) < 1e-10

    # 3. Degenerate inputs. lambda = 0 costs no false-alarm time; ARL_0 is monotone in lambda.
    assert arl0(0.0, th, DELTA_P_CUSUM) == 0.0
    assert all(arl0(x, th, DELTA_P_CUSUM) < arl0(y, th, DELTA_P_CUSUM)
               for x, y in zip(LAMBDA_LADDER, LAMBDA_LADDER[1:]))
    assert abs(arl0_inverse(arl0(15.0, th, DELTA_P_CUSUM), th, DELTA_P_CUSUM) - 15.0) < 1e-8

    # 4. p_true = 0: no positive excursion, ARL_0 infinite. Non-negative null drift: no root.
    assert cramer_root(0.0, 0.0, DELTA_P_CUSUM) == np.inf
    try:
        cramer_root(0.5, 0.1, DELTA_P_CUSUM)
    except ValueError:
        pass
    else:
        raise AssertionError("a non-negative null drift must not return a Cramer root")

    # 5. thm:floor becomes VACUOUS at both ends of p_0, it does not tighten. p_0(1-p_0) is in the
    #    DENOMINATOR of the KL upper bound, hence in the NUMERATOR of the floor.
    alpha = 57.4 / arl0(50.0, th, DELTA_P_CUSUM)
    f = [detection_floor(p, 0.3268, 57.4, alpha) for p in (1e-9, 0.024, 0.5, 1 - 1e-9)]
    assert f[0] < 0 and f[3] < 0, f                      # vacuous at both ends
    assert f[2] > f[1] > f[0], f                         # maximal at p_0 = 1/2
    assert abs(f[0] - f[3]) < 1e-6, f                    # symmetric in p_0 <-> 1 - p_0

    # 6. eq:starve_boundary: W = 0 leaves the pre-drift value alone; mu = 0 leaves the margin
    #    alone; both terms are non-decreasing in W.
    assert lambda_starve(0.0, 0.3) == 0.0
    assert abs(lambda_starve(1.0, 0.0) - np.sqrt(0.5 * np.log(1.0 / EPS))) < 1e-12
    ws = np.array([1.0, 2.0, 4.0, 8.0, 16.0, 32.0, 64.0, 128.0, 256.0])
    assert np.all(np.diff(lambda_starve(ws, 0.3168)) > 0)

    # 7. Eq. (4) is vacant exactly when mu W >= lambda: the bound returns at least 1.
    bound = lambda lam, w, mu: w * np.exp(-2.0 / w * max(lam - mu * w, 0.0) ** 2)  # noqa: E731
    assert bound(15.0, 611.9, 0.3168) >= 1.0             # tau_erase at the canonical point
    assert bound(50.0, 57.4, 0.3168) < 1.0               # tau_swap^(1/M), same point

    print("s2_arl0 demo: OK")


if __name__ == "__main__":
    demo()
    if "--check" not in sys.argv:
        main()
