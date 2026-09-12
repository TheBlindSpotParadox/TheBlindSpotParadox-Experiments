"""Stream S2-bis, Phase 2 (T-A volet 2): equal-false-alarm-budget calibration on ProteuS / R4.

THIS IS WHERE `lambda = 15` IS GENUINELY COMMON. `exp_R4_main_table.py:165` builds every
PageHinkley couple as `drift.PageHinkley(threshold=ssot.R4_PHT_LAMBDA)` -- one threshold for fifteen
pipelines -- and `run_concept_drift:130-131` arms the detector at `t = 0`, so R4 has no warm-up at
all and never calibrated anything per pipeline. Table I's `0/1080`, its `p ~ 2e-9` and every EDDM /
ADWIN / KSWIN row sit on that uncalibrated comparison. R4's `evaluate:109-124` computes precision
and discards it, so `exp_R4_results_aligned_fusion.csv` carries only F1 and ADD.

WHAT THIS MODULE ADDS, AND WHAT IT REPRODUCES VERBATIM.

  added      the warm-up R4 never had: `[0, ssot.R4_T_DRIFT)`, the pre-drift span, run with the
             external detector DISABLED so no reset perturbs the pre-drift error stream -- the same
             convention R5's warm-up uses (`exp_R5_common.run_evaluation` constructs the detector
             only after the warm-up loop), declared as such;
  added      `lambda_eq` per (detector, classifier) couple, by `exp_R5_common.calibrate_lambda` on
             that stream, and the deviation of each from 15;
  added      alarm counts, precision and recall beside F1 and ADD;
  verbatim   `exp_R4_main_table.simulate_stream`, `run_concept_drift`, the model factories and the
             per-worker PRNG lock, all imported from R4 rather than re-implemented. R4 LEARNS BEFORE
             CLONING (`:136-140`) where R5 clones before learning (`:141-142`); the two loops are not
             interchangeable and R4's ordering is the one that holds here.

PER-WORKER PRNG LOCK, REPRODUCED VERBATIM FROM `exp_R4_main_table.process_transition_seed:189-199`.
Three seeding calls per worker, in this order, and no fourth:

  1. `safe_seed = seed % (2**31 - 1)`   C-level overflow prevention for the Cython extensions
  2. `np.random.seed(safe_seed)`        the generator River's tree-spawn path draws from
  3. `random.seed(safe_seed)`           the stdlib singleton the same path can reach
  4. then, once per regime, `simulate_stream(..., seed=seed)` re-seeds `np.random.seed(seed)` at
     `:76` with the RAW seed before generating the stream

R4 installs no `np.random.default_rng` -- the canonical lock named in `config/experiment_ssot.py`
:21-23 belongs to the R1/R2/R6/R7/R9 family, whose loops draw through a `Generator`. R4's stream
generator uses the legacy global API (`np.random.standard_normal`, `np.random.standard_t`), so a
`default_rng` here would consume no entropy and would advertise a generator the loop never reads.
The lock is reproduced as R4 has it, which is what keeps the streams bit-identical to Table I's.

PARALLELISM IS MANDATORY AND IS R4's OWN. `joblib.Parallel(n_jobs=-1)` over the
(transition, seed) grid, exactly as `exp_R4_main_table.main:385`. One worker owns one
(transition, seed) cell and runs all three GARCH regimes inside it, so `simulate_stream` is paid
once per (transition, seed, regime) and shared by every couple and every threshold in that cell --
the same amortisation R4 relies on. Sequential single-thread execution is not an option here: the
grid is 360 cells and the per-cell work is several times R4's.

FAMILY REQUIREMENTS AT THE COMMON ALPHA IMPLIED BY `lambda_eq`. `s2_arl0.floor_and_family`
already evaluates `R_CUSUM`, `R_ADWIN`, `R_KSWIN` on a fixed lambda ladder and records KSWIN's
DEPLOYED alpha beside it. That hook is extended here rather than in `s2_arl0.py`: re-running the S2
module would rewrite `results/S2_theory/tables/`, which is outside the S2-bis write perimeter. The
S2 primitives are imported; nothing in `results/S2_theory/` is touched. EDDM is declared OUT OF
SCOPE for the knob equalisation, with the reason: its level is a ratio against a running maximum and
carries no false-alarm parameter of the same kind as `lambda`, `delta` or `alpha`.

Outputs, all under `results/S2bis_calibration/tables/`:
  s2bis_lambda_eq_proteus.csv   per (couple, regime, transition, seed): lambda_eq and its deviation
                                from R4_PHT_LAMBDA, the pre-drift rate, the B7 verdict
  s2bis_proteus_sweep.csv       per (couple, regime, transition, seed, lambda): F1, ADD, alarms,
                                precision, recall -- what R4 never recorded
  s2bis_proteus_gate.json       couple-level summary, the R4 non-regression check at lambda = 15,
                                and the family requirements at the common alpha implied by lambda_eq

Usage:  PYTHONHASHSEED=0 python experiments/S2bis_calibration/s2bis_proteus_calibration.py
        PYTHONHASHSEED=0 python experiments/S2bis_calibration/s2bis_proteus_calibration.py --check
"""
import itertools
import json
import random
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from river import drift
from scipy.optimize import brentq
from tqdm import tqdm

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "R4_proteus_evaluation"))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "R5_real_world_evaluation"))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "S2_theory"))
from config import experiment_ssot as ssot          # noqa: E402
import exp_R4_main_table as r4                      # noqa: E402
import exp_R5_config as cfg                         # noqa: E402
import exp_R5_common as common                      # noqa: E402
import s2_arl0 as s2                                # noqa: E402

OUT_DIR = ssot.RESULTS_DIR / "S2bis_calibration" / "tables"
FROZEN_R4 = ssot.RESULTS_DIR / "R4_proteus_evaluation" / "data" / "exp_R4_results_aligned_fusion.csv"

SEED_LIST = ssot.R4_SEEDS
LAMBDA_REF = ssot.R4_PHT_LAMBDA
LAMBDA_GRID = list(ssot.S2BIS_PROTEUS_LAMBDA_GRID)
LAMBDA_LO, LAMBDA_HI = ssot.S2BIS_LAMBDA_BRACKET

# The six PageHinkley couples of Table I. `label` is R4's own Detector string, so a row of this
# campaign joins exp_R4_results_aligned_fusion.csv on (Detector, Clock, Calibration, Dataset, Seed).
COUPLES = [
    ("PHT + HT", 1, "ht"),
    ("PHT + ARF", 1, "arf"),
    ("PHT + ARF", 32, "arf"),
    ("SRP + PHT", 1, "srp"),
    ("SRP + PHT", 32, "srp"),
    ("PHT + RF (Static)", 1, "rf"),
]
HEADLINE = [("PHT + HT", 1), ("PHT + ARF", 1)]      # the pair carrying Table I's blind-spot collapse
REGIMES = [("IID", r4.ETF_PARAMS_A), ("Cal. A", r4.ETF_PARAMS_A), ("Cal. B", r4.ETF_PARAMS_B)]


def build_classifier(kind, seed, clock):
    """R4's own factories, by name. No model class is redefined here."""
    if kind == "ht":
        return r4.make_ht()
    if kind == "arf":
        return r4.make_arf(seed, clock)
    if kind == "srp":
        return r4.make_srp(seed, clock)
    return r4.make_rf(seed)


def pht_factory(lam):
    """R4's `pht()` with the threshold injected. R4 hard-codes ssot.R4_PHT_LAMBDA at :165 and
    accepts no external threshold; delta stays at River's default, which is what R4 runs."""
    return lambda: drift.PageHinkley(threshold=lam, delta=cfg.PHT_DELTA)


def run_no_detector(df, model, stop_at):
    """`r4.run_concept_drift` with the external detector removed, truncated at `stop_at`.

    The predict / learn ordering is R4's, verbatim: predict, then learn, and no reset can occur
    because there is no detector to fire. Returns the error stream over `[0, stop_at)`."""
    y, X = df['regime'].values, df[['log_return', 'rolling_vol']].values
    errs = []
    for t in range(min(stop_at, len(df))):
        x = {0: X[t, 0], 1: X[t, 1]}
        yt = int(y[t])
        yp = model.predict_one(x) or 0
        errs.append(float(yp != yt))
        model.learn_one(x, yt)
    return errs


def evaluate_full(detected, true_drifts, n, tau):
    """`r4.evaluate` with the precision it computes and discards, plus recall and the counts.

    The matching is R4's, character for character -- first unclaimed detection in the CLOSED window
    `[td, td + tau]` -- so (ADD, F1) is identical to `r4.evaluate`. `tests/test_S2bis_calibration.py`
    asserts that identity on the frozen grid rather than assuming it."""
    tp_pairs, used = [], set()
    for td in sorted(true_drifts):
        cands = [d for d in detected if td <= d <= td + tau and d not in used]
        if cands:
            first = min(cands)
            tp_pairs.append((td, first))
            used.add(first)
    TP = len(tp_pairs)
    FP = len([d for d in detected if d not in used])
    FN = len(true_drifts) - TP
    ADD = float(np.mean([b - a for a, b in tp_pairs])) if tp_pairs else np.nan
    pr = TP / (TP + FP) if (TP + FP) > 0 else 0.0
    rc = TP / (TP + FN) if (TP + FN) > 0 else 0.0
    f1 = 2 * pr * rc / (pr + rc) if (pr + rc) > 0 else 0.0
    return {"ADD": ADD, "F1": f1, "precision": pr, "recall": rc,
            "TP": TP, "FP": FP, "FN": FN, "n_detections": len(detected)}


def calibration_verdict(error_stream, lam, target_fa=cfg.PHT_TARGET_FA):
    """Rule B7, on the ProteuS pre-drift span. Same three terminal verdicts as Phase 1."""
    if len(error_stream) < ssot.S2BIS_PHT_MIN_INSTANCES:
        return "NOT ARMED", None
    n = 0
    pht = drift.PageHinkley(threshold=lam, delta=cfg.PHT_DELTA)
    for e in error_stream:
        pht.update(e)
        if pht.drift_detected:
            n += 1
            pht = drift.PageHinkley(threshold=lam, delta=cfg.PHT_DELTA)
    if lam >= LAMBDA_HI:
        return "SATURATED", n
    if n > target_fa:
        return "NOT ATTAINABLE", n
    return "OK", n


# ─── the worker ───────────────────────────────────────────────────────────────────────────────────
def process_transition_seed(trans, seed):
    """One (transition, seed) cell: three regimes, six couples, calibration then thresholds.

    The preamble is `exp_R4_main_table.process_transition_seed:189-199` verbatim -- the modulo, then
    `np.random.seed`, then `random.seed`. `simulate_stream` re-seeds `np.random` with the RAW seed at
    its own :76, which is the third seeding call and the one that fixes the stream."""
    # Strict RNG isolation per worker (Bit-wise reproducibility).
    # C-Level Overflow Prevention: apply modulo for Cython-compiled extensions
    safe_seed = seed % (2**31 - 1)
    np.random.seed(safe_seed)
    random.seed(safe_seed)

    from_t, to_t, w, name = trans
    cal_rows, sweep_rows = [], []
    for regime, params in REGIMES:
        df, dpts = r4.simulate_stream(params[from_t], params[to_t], regime, w, seed=seed)
        tau = max(ssot.R4_TAU_TOL_FLOOR, w)

        # 1. The warm-up R4 never had: pre-drift, external detector disabled.
        lam_eq = {}
        for label, clock, kind in COUPLES:
            errs = run_no_detector(df, build_classifier(kind, seed, clock), ssot.R4_T_DRIFT)
            lam = common.calibrate_lambda(errs)
            verdict, attained = calibration_verdict(errs, lam)
            lam_eq[(label, clock)] = lam
            cal_rows.append({"Calibration": regime, "Detector": label, "Clock": clock,
                             "Dataset": name, "w": w, "Seed": seed,
                             "lambda_ref": float(LAMBDA_REF), "lambda_eq": float(lam),
                             "deviation_from_ref": float(lam - LAMBDA_REF),
                             "ratio_to_ref": float(lam / LAMBDA_REF),
                             "p_true_pre_drift": float(np.mean(errs)),
                             "span_len": len(errs), "verdict_B7": verdict,
                             "attained_fa": attained})

        # 2. Thresholds. Every couple at lambda_ref and at its own lambda_eq; the two headline
        #    couples also on the common ladder.
        for label, clock, kind in COUPLES:
            thresholds = {round(float(LAMBDA_REF), 9): "lambda_ref",
                          round(float(lam_eq[(label, clock)]), 9): "lambda_eq"}
            if (label, clock) in HEADLINE:
                for lam in LAMBDA_GRID:
                    thresholds.setdefault(round(float(lam), 9), "grid")
            for lam, role in sorted(thresholds.items()):
                dets = r4.run_concept_drift(df, build_classifier(kind, seed, clock),
                                            pht_factory(lam))
                m = evaluate_full(dets, dpts, len(df), tau)
                sweep_rows.append({"Calibration": regime, "Detector": label, "Clock": clock,
                                   "Dataset": name, "w": w, "Seed": seed,
                                   "lambda": float(lam), "lambda_role": role, **m})
    return cal_rows, sweep_rows


# ─── family requirements at the common alpha implied by lambda_eq ─────────────────────────────────
def alpha_of_lambda(lam, p_true, w, delta_p=ssot.CUSUM_DELTA_P):
    """alpha = W / ARL_0(lambda) at the Cramer root of (p_true, p_true, delta_p)."""
    theta = s2.cramer_root(p_true, p_true, delta_p)
    return w / s2.arl0(lam, theta, delta_p), theta


def family_requirements(lam_eq_by_couple, w=57.4, delta_e=0.326793,
                        n_stat=30, eps=ssot.EPS_MISS):
    """`s2_arl0.floor_and_family`'s `deployed_alphas` hook, extended to the measured `lambda_eq`.

    Rule B8: W, the measured ceiling and the p_true band are S6-anchored quantities, so the band
    `[0.015, 0.032]` is the right one here and is used only for these S6-anchored statements. The
    ProteuS pre-drift rate is reported beside them and never substituted into a bound whose W comes
    from a different stream.

    `delta` and `alpha` that would place ADWIN and KSWIN at the CUSUM's level solve
        R_ADWIN(alpha) = R_CUSUM(lambda)  =>  alpha = 4 W exp(-2 lambda^2 / W)
        R_KSWIN(alpha) = R_CUSUM(lambda)  =>  alpha = 2 exp(-lambda^2 / n_stat)
    both obtained by cancelling the shared epsilon margin. River's ADWIN parameterises its
    confidence by `delta`, which is the same object as this alpha in eq:Radwin, so delta = alpha."""
    margin = float(np.sqrt(w / 2.0 * np.log(1.0 / eps)))
    band = [0.015, 0.032]
    ceiling = 33.5115                                # median max_t A_unrefl, s2_gate_T20.json
    rows = []
    for (label, clock), lam in sorted(lam_eq_by_couple.items()):
        entry = {"couple": f"{label} (c={clock})", "lambda_eq": lam,
                 "R_CUSUM": lam + margin,
                 "equalising_alpha_ADWIN": float(4.0 * w * np.exp(-2.0 * lam ** 2 / w)),
                 "equalising_alpha_KSWIN": float(2.0 * np.exp(-lam ** 2 / n_stat)),
                 "over_p_true_band": []}
        entry["equalising_delta_ADWIN"] = entry["equalising_alpha_ADWIN"]
        entry["deployed_alpha_ADWIN"] = ssot.R4_ADWIN_DELTA
        entry["deployed_alpha_KSWIN"] = ssot.R4_KSWIN_ALPHA
        for p in band:
            a, theta = alpha_of_lambda(lam, p, w)
            entry["over_p_true_band"].append({
                "p_true": p, "theta_star": theta, "alpha": a,
                "log_1_over_alpha": float(np.log(1.0 / a)),
                "R_ADWIN_at_common_alpha": float(np.sqrt(w / 2.0 * np.log(4.0 * w / a)) + margin),
                "R_KSWIN_at_common_alpha": float(np.sqrt(n_stat * np.log(2.0 / a)) + margin)})
        entry["met_by_measured_ceiling"] = {
            "R_CUSUM": bool(ceiling >= entry["R_CUSUM"]),
            "R_ADWIN_at_common_alpha": [bool(ceiling >= r["R_ADWIN_at_common_alpha"])
                                        for r in entry["over_p_true_band"]],
            "R_KSWIN_at_common_alpha": [bool(ceiling >= r["R_KSWIN_at_common_alpha"])
                                        for r in entry["over_p_true_band"]]}
        rows.append(entry)
    return {"at": {"W": w, "delta_e": delta_e, "eps": eps, "n_stat": n_stat,
                   "p_true_band": band, "measured_ceiling_median_A_unrefl": ceiling,
                   "band_provenance": "S6 Bernoulli arm, s2_gate_T20.json "
                                      "p_true_sensitivity.band_used -- rule B8"},
            "epsilon_margin": margin,
            "R_KSWIN_at_deployed_alpha": float(np.sqrt(n_stat * np.log(2.0 / ssot.R4_KSWIN_ALPHA))
                                               + margin),
            "per_couple": rows,
            "EDDM": {"status": "OUT OF SCOPE for the knob equalisation",
                     "reason": "EDDM's level is a ratio against a running maximum of the "
                               "between-error distance; it carries no false-alarm parameter of the "
                               "same kind as lambda, delta or alpha, so there is no knob to set to "
                               "a common alpha. Its empirical result stands on its own measurement "
                               "and is read in docs/theory/S2bis_narrative_payload.md (T-D)."}}


def cor_split_crossings(w=57.4, n_stat=30, p_true=None, delta_p=ssot.CUSUM_DELTA_P,
                        eps=ssot.EPS_MISS):
    """`cor:split` read off the exact requirement curves, not off the asymptotic slope alone.

    The three requirements share the epsilon margin, so it cancels and the crossings are where
        lambda = sqrt(W/2 ln(4W/alpha))      (ADWIN)
        lambda = sqrt(n_stat ln(2/alpha))    (KSWIN)
    with alpha = W / ARL_0(lambda) at the Cramer root, i.e. the EXACT alpha-to-lambda map rather
    than lambda ~ ln(1/alpha)/theta*. The asymptotic slope 1/theta* is reported beside them: it is
    the content of cor:split (linear against square root), while the crossing location depends on
    the constant the asymptote drops, which is why it is solved numerically here.

    The S2-bis plan quotes the crossing at `ln(1/alpha) ~ 13`. The artifact's own ladder brackets it
    higher -- at lambda = 25, ln(1/alpha) = 17.97 and R_CUSUM 34.27 has not yet passed R_ADWIN 35.19
    while it has passed R_KSWIN 32.94 -- so the value is measured here and the divergence is
    recorded in docs/theory/transfer_S2bis.md."""
    p_true = ssot.P0_MEASURED if p_true is None else p_true
    margin = float(np.sqrt(w / 2.0 * np.log(1.0 / eps)))
    theta = s2.cramer_root(p_true, p_true, delta_p)
    alpha = lambda lam: w / s2.arl0(lam, theta, delta_p)          # noqa: E731
    gap_ad = lambda lam: lam - np.sqrt(w / 2.0 * np.log(4.0 * w / alpha(lam)))       # noqa: E731
    gap_ks = lambda lam: lam - np.sqrt(n_stat * np.log(2.0 / alpha(lam)))            # noqa: E731
    out = {"at": {"W": w, "n_stat": n_stat, "p_true": p_true, "delta_P": delta_p, "eps": eps},
           "epsilon_margin": margin, "theta_star": float(theta),
           "R_CUSUM_slope_per_unit_log_1_over_alpha": float(1.0 / theta),
           "scaling": {"R_CUSUM": "linear in ln(1/alpha), free of W",
                       "R_ADWIN": "square root of ln(1/alpha), vanishes with W",
                       "R_KSWIN": "square root of ln(1/alpha), free of W"},
           "crossings": {}}
    for name, gap in (("R_ADWIN", gap_ad), ("R_KSWIN", gap_ks)):
        lo, hi = 1.0, 400.0
        if gap(lo) * gap(hi) > 0:
            out["crossings"][name] = {"status": "NO CROSSING on lambda in [1, 400]"}
            continue
        lam = float(brentq(gap, lo, hi, xtol=1e-10, rtol=1e-12, maxiter=500))
        a = alpha(lam)
        out["crossings"][name] = {
            "lambda": lam, "alpha": float(a), "log_1_over_alpha": float(np.log(1.0 / a)),
            "R_at_crossing": lam + margin,
            "reading": f"below ln(1/alpha) = {np.log(1.0 / a):.2f} the CUSUM asks LESS evidence "
                       f"than {name[2:]}; above it, more"}
    out["plan_quoted_crossing_log_1_over_alpha"] = 13.0
    return out


# ─── non-regression against the frozen R4 grid ────────────────────────────────────────────────────
def r4_non_regression(sweep):
    """At lambda_ref = R4_PHT_LAMBDA the six couples reproduce R4's own F1 and ADD, or they do not.
    Read on the frozen CSV with round-trip float parsing; nothing under results/R4_* is rewritten."""
    if not FROZEN_R4.exists():
        return {"status": "SKIPPED", "reason": f"{FROZEN_R4.relative_to(ROOT_DIR)} absent"}
    frozen = pd.read_csv(FROZEN_R4, float_precision="round_trip")
    mine = sweep[sweep.lambda_role == "lambda_ref"]
    key = ["Calibration", "Detector", "Clock", "Dataset", "Seed"]
    j = mine.merge(frozen, on=key, suffixes=("_s2bis", "_r4"))
    if j.empty:
        return {"status": "NO OVERLAP", "n_rows_frozen": int(len(frozen)), "n_rows_mine": int(len(mine))}
    d_f1 = (j.F1_s2bis - j.F1_r4).abs()
    d_add = (j.ADD_s2bis - j.ADD_r4).abs()
    both_nan = j.ADD_s2bis.isna() & j.ADD_r4.isna()
    return {"status": "CHECKED", "n_joined": int(len(j)),
            "max_abs_F1_delta": float(d_f1.max()),
            "max_abs_ADD_delta": float(d_add[~both_nan].max()) if (~both_nan).any() else 0.0,
            "ADD_nan_agreement": bool((j.ADD_s2bis.isna() == j.ADD_r4.isna()).all()),
            "identical": bool(d_f1.max() < 1e-12
                              and (d_add[~both_nan].max() < 1e-9 if (~both_nan).any() else True)
                              and (j.ADD_s2bis.isna() == j.ADD_r4.isna()).all())}


def summarise(cal, sweep):
    per_couple = (cal.groupby(["Detector", "Clock"])
                  .agg(lambda_eq_mean=("lambda_eq", "mean"),
                       lambda_eq_median=("lambda_eq", "median"),
                       lambda_eq_min=("lambda_eq", "min"), lambda_eq_max=("lambda_eq", "max"),
                       lambda_eq_std=("lambda_eq", "std"),
                       ratio_to_ref_mean=("ratio_to_ref", "mean"),
                       p_true_pre_drift_mean=("p_true_pre_drift", "mean"),
                       n_cells=("lambda_eq", "size")).reset_index())
    rows = []
    for _, c in per_couple.iterrows():
        s = sweep[(sweep.Detector == c.Detector) & (sweep.Clock == c.Clock)]
        at = {}
        for role in ("lambda_ref", "lambda_eq"):
            r = s[s.lambda_role == role]
            at[role] = {"F1_mean": float(r.F1.mean()), "ADD_mean": float(r.ADD.mean(skipna=True)),
                        "precision_mean": float(r.precision.mean()),
                        "recall_mean": float(r.recall.mean()),
                        "alarms_mean": float(r.n_detections.mean()),
                        "runs_with_a_detection": int((r.F1 > 0).sum()), "n_runs": int(len(r))}
        rows.append({"couple": f"{c.Detector} (c={int(c.Clock)})",
                     "Detector": c.Detector, "Clock": int(c.Clock),
                     "lambda_ref": float(LAMBDA_REF),
                     "lambda_eq_mean": float(c.lambda_eq_mean),
                     "lambda_eq_median": float(c.lambda_eq_median),
                     "lambda_eq_range": [float(c.lambda_eq_min), float(c.lambda_eq_max)],
                     "lambda_eq_std": float(c.lambda_eq_std),
                     "deviation_from_15_mean": float(c.lambda_eq_mean - LAMBDA_REF),
                     "ratio_to_15_mean": float(c.ratio_to_ref_mean),
                     "p_true_pre_drift_mean": float(c.p_true_pre_drift_mean),
                     "n_cells": int(c.n_cells), "at": at})
    return rows


def main(transitions=None, seed_list=None):
    transitions = r4.TRANSITIONS if transitions is None else transitions
    seed_list = SEED_LIST if seed_list is None else seed_list
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    grid = list(itertools.product(transitions, seed_list))
    n_thr = 2 * len(COUPLES) + len(HEADLINE) * len(LAMBDA_GRID)
    print(f"[S2-bis/P2] {len(transitions)} transitions x {len(seed_list)} seeds x 3 regimes; "
          f"per regime {len(COUPLES)} calibration runs + up to {n_thr} threshold runs", flush=True)
    print("[S2-bis/P2] Parallel execution (Joblib, n_jobs=-1) - Please wait...", flush=True)
    nested = Parallel(n_jobs=-1)(delayed(process_transition_seed)(t, s)
                                 for t, s in tqdm(grid, desc="S2-bis ProteuS"))

    cal = pd.DataFrame([r for sub, _ in nested for r in sub]).sort_values(
        ["Detector", "Clock", "Calibration", "Dataset", "Seed"]).reset_index(drop=True)
    sweep = pd.DataFrame([r for _, sub in nested for r in sub]).sort_values(
        ["Detector", "Clock", "Calibration", "Dataset", "lambda", "Seed"]).reset_index(drop=True)
    cal.to_csv(OUT_DIR / "s2bis_lambda_eq_proteus.csv", index=False)
    sweep.to_csv(OUT_DIR / "s2bis_proteus_sweep.csv", index=False)

    couples = summarise(cal, sweep)
    lam_eq = {(r["Detector"], r["Clock"]): r["lambda_eq_mean"] for r in couples}
    payload = {
        "design": {
            "lambda_ref": float(LAMBDA_REF),
            "lambda_ref_provenance": "ssot.R4_PHT_LAMBDA, common to all fifteen R4 pipelines, "
                                     "armed at t = 0 with no warm-up (exp_R4_main_table.py:165, "
                                     ":130-131)",
            "warmup_span": [0, int(ssot.R4_T_DRIFT)],
            "warmup_convention": "external detector disabled during the calibration pass, so no "
                                 "reset perturbs the pre-drift error stream",
            "target": f"at most PHT_TARGET_FA = {cfg.PHT_TARGET_FA} false alarm over "
                      f"[0, R4_T_DRIFT), detector re-armed after each alarm",
            "prng_lock": "exp_R4_main_table.process_transition_seed:189-199 verbatim -- "
                         "safe_seed = seed % (2**31 - 1); np.random.seed(safe_seed); "
                         "random.seed(safe_seed); then simulate_stream re-seeds np.random.seed(seed)",
            "ordering": "R4 learns before cloning (run_concept_drift:136-140); R5 clones before "
                        "learning. R4's ordering is reproduced here.",
            "scoring": "r4.evaluate's matching, closed window [d, d + tau], "
                       "tau = max(R4_TAU_TOL_FLOOR, w)"},
        "per_couple": couples,
        "r4_non_regression_at_lambda_ref": r4_non_regression(sweep),
        "family_requirements_at_lambda_eq": family_requirements(lam_eq),
        "cor_split_crossings": cor_split_crossings(),
        "reproduction": {
            "python": sys.version.split()[0],
            "artifacts_read": [str(FROZEN_R4.relative_to(ROOT_DIR))],
            "command": "PYTHONHASHSEED=0 python "
                       "experiments/S2bis_calibration/s2bis_proteus_calibration.py"}}
    (OUT_DIR / "s2bis_proteus_gate.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=float) + "\n", encoding="utf-8")

    print("\n=== lambda_eq per couple, against the common lambda = 15 ===")
    print(f"  {'couple':26s} {'lambda_eq':>10s} {'range':>22s} {'x15':>7s} {'e_pre':>7s}  "
          f"{'F1@15':>7s} {'F1@eq':>7s} {'prec@15':>8s} {'prec@eq':>8s}")
    for r in couples:
        print(f"  {r['couple']:26s} {r['lambda_eq_mean']:10.3f} "
              f"[{r['lambda_eq_range'][0]:8.3f},{r['lambda_eq_range'][1]:9.3f}] "
              f"{r['ratio_to_15_mean']:7.2f} {r['p_true_pre_drift_mean']:7.4f}  "
              f"{r['at']['lambda_ref']['F1_mean']:7.4f} {r['at']['lambda_eq']['F1_mean']:7.4f} "
              f"{r['at']['lambda_ref']['precision_mean']:8.4f} "
              f"{r['at']['lambda_eq']['precision_mean']:8.4f}")
    print(f"\n  R4 non-regression at lambda = 15: {payload['r4_non_regression_at_lambda_ref']}")
    print(f"wrote {OUT_DIR.relative_to(ROOT_DIR)}/"
          "{s2bis_lambda_eq_proteus.csv, s2bis_proteus_sweep.csv, s2bis_proteus_gate.json}")
    return cal, sweep, payload


def demo():
    """Self-check. Writes nothing and simulates no stream: the scoring identity against R4's own
    evaluator, the equalising-alpha algebra, and rule B7's three terminal verdicts."""
    # 1. evaluate_full reproduces r4.evaluate exactly on every shape that matters, including the
    #    empty-detection and no-match cases where ADD is NaN.
    for detected, truth, tau in (([4100], [4000], 1000), ([], [4000], 1000),
                                 ([7000], [4000], 1000), ([4050, 4900, 6000], [4000], 1000),
                                 ([4000], [4000], 1000)):
        add_r4, f1_r4 = r4.evaluate(detected, truth, 8000, tau)
        m = evaluate_full(detected, truth, 8000, tau)
        assert (np.isnan(add_r4) and np.isnan(m["ADD"])) or add_r4 == m["ADD"], (detected, add_r4, m)
        assert f1_r4 == m["F1"], (detected, f1_r4, m)

    # 2. The equalising alphas invert their own requirements.
    w, n_stat, eps = 57.4, 30, ssot.EPS_MISS
    margin = np.sqrt(w / 2.0 * np.log(1.0 / eps))
    for lam in (8.0, 15.0, 25.0):
        a_ad = 4.0 * w * np.exp(-2.0 * lam ** 2 / w)
        a_ks = 2.0 * np.exp(-lam ** 2 / n_stat)
        assert abs((np.sqrt(w / 2.0 * np.log(4.0 * w / a_ad)) + margin) - (lam + margin)) < 1e-9
        assert abs((np.sqrt(n_stat * np.log(2.0 / a_ks)) + margin) - (lam + margin)) < 1e-9

    # 3. A higher lambda demands a SMALLER equalising alpha: the CUSUM's requirement grows linearly
    #    in ln(1/alpha) while the other two grow as its square root.
    ad = [4.0 * w * np.exp(-2.0 * l ** 2 / w) for l in (8.0, 15.0, 25.0, 50.0)]
    assert all(a > b for a, b in zip(ad, ad[1:])), ad

    # 4. Rule B7's three terminal verdicts.
    assert calibration_verdict([0.0] * 10, 40.0)[0] == "NOT ARMED"
    assert calibration_verdict([0.0] * 100, LAMBDA_HI)[0] == "SATURATED"
    assert calibration_verdict([0.0] * 100, 40.0)[0] == "OK"

    # 5. cor:split's crossings are solved on the exact curves and bracket the ladder correctly:
    #    the KSWIN crossing sits between lambda = 15 and lambda = 25, the ADWIN one above 25.
    cs = cor_split_crossings()["crossings"]
    assert 15.0 < cs["R_KSWIN"]["lambda"] < 25.0, cs["R_KSWIN"]
    assert cs["R_ADWIN"]["lambda"] > cs["R_KSWIN"]["lambda"], cs

    # 6. alpha is decreasing in lambda at a fixed base rate, and ARL_0 has a Cramer root there.
    a = [alpha_of_lambda(l, 0.024, w)[0] for l in (8.0, 15.0, 25.0, 50.0)]
    assert all(x > y for x, y in zip(a, a[1:])), a

    print("s2bis_proteus_calibration demo: OK")


if __name__ == "__main__":
    demo()
    if "--check" not in sys.argv:
        main()
