"""Stream S2-bis, Phase 1 (T-A volet 1): equal-false-alarm-budget calibration on INSECTS.

WHAT THIS MODULE CORRECTS IN THE BRIEF. R5 does not run at a common threshold.
`exp_R5_common.run_evaluation:121-123` calls `calibrate_lambda` per (variant, seed, pipeline) --
bisection on `S2BIS_LAMBDA_BRACKET` to at most `PHT_TARGET_FA = 1` false alarm on that pipeline's
own warm-up error stream, detector re-armed after each alarm. Table II's F1 ratio is therefore
already an equal-false-alarm-budget comparison, at the target "one FA per warm-up", and
`lambda_calibrated` IS the `lambda_eq` of rule B1 at that target. The site where `lambda = 15` is
genuinely common to every pipeline is R4 (`s2bis_proteus_calibration.py`).

What survives on R5, and what this module measures, is a budget/span mismatch: the budget is set on
a warm-up of `INSECTS_WARMUP_FRACTION` of the stream while the detector then runs armed over the
whole pre-change span, which is four to five times longer. Rule B1 therefore names two targets:

    T_warm   one expected false alarm over the warm-up          (R5's existing target)
    T_span   one expected false alarm over the armed pre-change span, [warmup, first valid drift)

Two estimators per rule B2. `lambda_eq^emp` is `calibrate_lambda` with the span substituted for the
warm-up and carries the verdict; `lambda_eq^ARL` is the Siegmund inversion of `s2_arl0` at
`theta*(p_pre, p_true)` and is the consistency check. River's PageHinkley tracks its own running
mean, so its reference rate is the stream's own pre-change rate and the Siegmund null drift is
`PHT_DELTA` exactly; that identification is declared here and is what makes `lambda_eq^ARL`
comparable at all.

THE CALIBRATION PASS RUNS WITH THE EXTERNAL DETECTOR DISABLED. A detection resets the classifier
(`run_evaluation:141`), so an armed detector makes the pre-change error stream a function of
`lambda` and the calibration circular. Disabling it is the same convention R5's own warm-up uses --
the detector is constructed only after the warm-up loop -- extended to the whole pre-change span.

NO REPLAY SHORTCUT EXISTS for the sweep. Because the classifier is reset on every alarm, the error
stream is a function of `lambda` and each grid point is a full prequential run.

Scoring convention: `evaluate_bipartite`, i.e. a detection matches a drift `d` on the CLOSED window
`[d, d + tau]`. `exp_R5_compute_insects.per_episode_match` uses the half-open `(d, d + tau]`; the
two differ only on a detection landing exactly at `d`, and the bipartite scorer is the one Table II
reports (`exp_R5_config.F1_COL = "F1_bp"`).

Outputs, all under `results/S2bis_calibration/tables/`:
  s2bis_lambda_eq_insects.csv   per (variant, seed, pipeline): both targets, both estimators,
                                the B7 verdict, the measured pre-change rate and span
  s2bis_insects_sweep.csv       per (variant, seed, pipeline, lambda): F1, ADD, alarms, precision
  s2bis_flooding_gate.json      rule B3 verdict, rule B4 decomposition, the T_warm identity proof,
                                the budget/span mismatch, and the rule B10 pseudo-replication read

Usage:  PYTHONHASHSEED=0 python experiments/S2bis_calibration/s2bis_lambda_eq.py
        PYTHONHASHSEED=0 python experiments/S2bis_calibration/s2bis_lambda_eq.py --check
"""
import json
import random
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from river import drift, stream, tree

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "R5_real_world_evaluation"))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "S2_theory"))
from config import experiment_ssot as ssot          # noqa: E402
import exp_R5_config as cfg                         # noqa: E402
import exp_R5_common as common                      # noqa: E402
from s2_arl0 import arl0, arl0_inverse, cramer_root  # noqa: E402

OUT_DIR = ssot.RESULTS_DIR / "S2bis_calibration" / "tables"
FROZEN_EPISODE = ssot.RESULTS_DIR / "R5_real_world_evaluation" / "data" / "insects_per_episode.parquet"
FROZEN_AGG = ssot.RESULTS_DIR / "R5_real_world_evaluation" / "data" / "insects_results.parquet"

PIPELINE_PAIR = tuple(cfg.PIPELINES_FLOODING)        # ("pht_ht", "pht_arf_c1")
PRIORITY_VARIANT = "gradual_balanced"
VARIANT_ORDER = [PRIORITY_VARIANT] + [v for v in cfg.INSECTS_VARIANTS if v != PRIORITY_VARIANT]
LAMBDA_GRID = list(ssot.S2BIS_INSECTS_LAMBDA_GRID)
LAMBDA_LO, LAMBDA_HI = ssot.S2BIS_LAMBDA_BRACKET


# ─── stream geometry ──────────────────────────────────────────────────────────────────────────────
def load_variant(variant):
    """INSECTS CSVs carry no header row, so `pd.read_csv` consumes record #1 and n_total is
    lines - 1. Reproduced exactly as `exp_R5_compute_insects.simulate:34-37` reads it; any other
    loader shifts every drift index."""
    df = pd.read_csv(cfg.INSECTS_DIR / f"{variant}.csv")
    return df, df.columns[-1]


def geometry(variant, n_total):
    """Spans and ground truth for one variant. `span` is the ARMED pre-change span of rule B1."""
    warmup = common.get_warmup_steps(n_total)
    tau = common.get_tau_tol(n_total)
    raw = cfg.INSECTS_DRIFTS[variant]
    valid = common.valid_drifts(raw, n_total, tau)
    return {"variant": variant, "n_total": int(n_total), "warmup_steps": int(warmup),
            "tau_tol": int(tau), "raw_drifts": list(raw), "valid_drifts": list(valid),
            "f1_drifts": common.resolve_f1_drifts(raw, n_total, tau),
            "first_drift": int(min(valid)), "span_lo": int(warmup),
            "span_hi": int(min(valid)), "span_len": int(min(valid) - warmup)}


def feature_stream(df, target):
    for x, y in stream.iter_pandas(df.drop(columns=[target]), df[target]):
        yield x, y


# ─── the lambda-injected driver ───────────────────────────────────────────────────────────────────
def run_at_lambda(pipeline_name, seed, features, warmup_steps, none_fill, lambda_val, stop_at=None):
    """`exp_R5_common.run_evaluation` reproduced with lambda INJECTED instead of calibrated.

    The single API gap in R5 is that `run_evaluation` hard-couples calibration to execution and
    accepts no external threshold. Every other line of the loop is verbatim: the same two global RNG
    seeds, the same `build_model`, the same warm-up, the same predict/learn ordering, the same
    re-arm-and-reset on detection. `tests/test_S2bis_calibration.py` asserts the two agree
    bit-for-bit when the injected lambda is the calibrated one.

    lambda_val = None runs with NO external detector -- the calibration pass of rule B1, in which no
    reset may perturb the pre-change error stream. `stop_at` truncates the run, so the calibration
    pass pays only for the pre-change span.

    Determinism hardening, verbatim from run_evaluation:98-99: pin the global RNGs per cell so that
    any unseeded draw on river's ARF clone / tree-spawn path is reproducible across process runs."""
    random.seed(seed)
    np.random.seed(seed % (2 ** 32 - 1))

    is_pht = pipeline_name.startswith("pht_")
    is_tree = pipeline_name.endswith("_ht")
    clock = 32 if "c32" in pipeline_name else 1

    model = common.build_model(pipeline_name, seed)
    it = iter(features)
    warmup_errors, error_stream_full, detections = [], [], []

    # 1. Warm-up
    for _ in range(warmup_steps):
        try:
            x, y = next(it)
        except StopIteration:
            break
        y_pred = model.predict_one(x)
        y_pred = y_pred if y_pred is not None else none_fill
        warmup_errors.append(float(y != y_pred))
        model.learn_one(x, y)

    # 2. Arm the external monitor at the injected threshold
    if lambda_val is None:
        detector = None
    elif is_pht:
        detector = drift.PageHinkley(threshold=lambda_val, delta=cfg.PHT_DELTA)
    else:
        lambda_val = float("nan")
        detector = drift.ADWIN(clock=clock)
    error_stream_full.extend(warmup_errors)

    # 3. Stream
    t = warmup_steps
    for x, y in it:
        if stop_at is not None and t >= stop_at:
            break
        y_pred = model.predict_one(x)
        y_pred = y_pred if y_pred is not None else none_fill
        e_t = float(y != y_pred)
        error_stream_full.append(e_t)
        if detector is not None:
            detector.update(e_t)
            if detector.drift_detected:
                detections.append(t)
                detector = (drift.PageHinkley(threshold=lambda_val, delta=cfg.PHT_DELTA)
                            if is_pht else drift.ADWIN(clock=clock))
                model = tree.HoeffdingTreeClassifier() if is_tree else model.clone()
        model.learn_one(x, y)
        t += 1

    return detections, error_stream_full, lambda_val


def count_false_alarms(error_stream, lam):
    """Alarms raised by a re-armed PageHinkley at `lam` over `error_stream`. Same re-arm convention
    as `calibrate_lambda:66-71`."""
    n = 0
    pht = drift.PageHinkley(threshold=lam, delta=cfg.PHT_DELTA)
    for e in error_stream:
        pht.update(e)
        if pht.drift_detected:
            n += 1
            pht = drift.PageHinkley(threshold=lam, delta=cfg.PHT_DELTA)
    return n


# ─── rule B7: saturation, attainability, arming ───────────────────────────────────────────────────
def calibration_verdict(error_stream, lam, target_fa=cfg.PHT_TARGET_FA):
    """One of OK / SATURATED / NOT ATTAINABLE / NOT ARMED, with the bound that produced it."""
    if len(error_stream) < ssot.S2BIS_PHT_MIN_INSTANCES:
        return {"verdict": "NOT ARMED", "attained_fa": None,
                "bound": f"span {len(error_stream)} < min_instances "
                         f"{ssot.S2BIS_PHT_MIN_INSTANCES}"}
    attained = count_false_alarms(error_stream, lam)
    if lam >= LAMBDA_HI:
        return {"verdict": "SATURATED", "attained_fa": attained,
                "bound": f"lambda_eq >= {LAMBDA_HI:g}, the bisection ceiling"}
    if attained > target_fa:
        return {"verdict": "NOT ATTAINABLE", "attained_fa": attained,
                "bound": f"{attained} alarms at lambda = {lam:.4f} over a span of "
                         f"{len(error_stream)} steps, target {target_fa}"}
    return {"verdict": "OK", "attained_fa": attained, "bound": None}


def lambda_eq_arl(span_len, p_true, delta_p=cfg.PHT_DELTA):
    """Siegmund inversion at the target "one expected false alarm over `span_len` steps".

    River's PageHinkley subtracts its own running mean, so p_pre = p_true and the null drift is
    delta_p exactly. Returns (lambda, theta*, note); lambda is None when no Cramer root exists."""
    if p_true <= 0.0:
        return None, np.inf, "p_true = 0: no positive excursion, ARL_0 infinite by construction"
    try:
        theta = cramer_root(p_true, p_true, delta_p)
    except ValueError as exc:
        return None, None, f"no Cramer root: {exc}"
    if not np.isfinite(theta):
        return None, float(theta), "theta* not finite"
    try:
        return float(arl0_inverse(span_len, theta, delta_p)), float(theta), None
    except ValueError as exc:
        return None, float(theta), f"target unreachable: {exc}"


# ─── stage A: the calibration pass ────────────────────────────────────────────────────────────────
def calibration_cell(variant, seed, pipeline):
    """One (variant, seed, pipeline): detector-free pass over [0, first drift), both targets."""
    df, target = load_variant(variant)
    geo = geometry(variant, len(df))
    _, errors, _ = run_at_lambda(pipeline, seed, feature_stream(df, target), geo["warmup_steps"],
                                 cfg.INSECTS_NONE_FILL, None, stop_at=geo["span_hi"])
    warm = errors[:geo["warmup_steps"]]
    span = errors[geo["span_lo"]:geo["span_hi"]]

    lam_warm = common.calibrate_lambda(warm)
    lam_span = common.calibrate_lambda(span)
    p_true_span = float(np.mean(span)) if span else float("nan")
    lam_arl, theta, arl_note = lambda_eq_arl(len(span), p_true_span)

    v_warm = calibration_verdict(warm, lam_warm)
    v_span = calibration_verdict(span, lam_span)
    ratio = (max(lam_span, lam_arl) / min(lam_span, lam_arl)) if lam_arl else None
    return {
        "variant": variant, "seed": seed, "pipeline": pipeline,
        "n_total": geo["n_total"], "warmup_steps": geo["warmup_steps"],
        "span_lo": geo["span_lo"], "span_hi": geo["span_hi"], "span_len": geo["span_len"],
        "span_over_warmup": geo["span_len"] / geo["warmup_steps"],
        "p_true_warmup": float(np.mean(warm)) if warm else float("nan"),
        "p_true_span": p_true_span,
        "lambda_eq_warm_emp": float(lam_warm), "lambda_eq_span_emp": float(lam_span),
        "lambda_eq_span_arl": lam_arl, "theta_star_span": theta, "arl_note": arl_note,
        "arl_emp_ratio": ratio,
        "arl_concordant": (None if ratio is None else bool(ratio <= 2.0)),
        "fa_of_warm_lambda_over_span": count_false_alarms(span, lam_warm),
        "verdict_warm": v_warm["verdict"], "verdict_span": v_span["verdict"],
        "bound_span": v_span["bound"], "attained_fa_span": v_span["attained_fa"],
    }


# ─── stage B: the lambda sweep ────────────────────────────────────────────────────────────────────
def sweep_cell(variant, seed, pipeline, lam, role):
    """One full prequential run at an injected threshold. Records what R4 never recorded."""
    df, target = load_variant(variant)
    geo = geometry(variant, len(df))
    detections, errors, lam_used = run_at_lambda(pipeline, seed, feature_stream(df, target),
                                                 geo["warmup_steps"], cfg.INSECTS_NONE_FILL, lam)
    add_fm, f1_fm, fp_fm, add_bp, f1_bp, fp_bp = common.evaluate_bipartite(
        detections, geo["f1_drifts"], geo["n_total"], geo["tau_tol"])
    n_det = len(detections)
    tp_bp = n_det - fp_bp
    k = len(geo["f1_drifts"])
    return {"variant": variant, "seed": seed, "pipeline": pipeline,
            "lambda": float(lam), "lambda_role": role,
            "F1_bp": f1_bp, "F1_fm": f1_fm, "ADD_bp": add_bp, "ADD_fm": add_fm,
            "n_detections": n_det, "TP_bp": tp_bp, "FP_bp": fp_bp,
            "precision_bp": (tp_bp / n_det) if n_det else np.nan,
            "recall_bp": (tp_bp / k) if k else np.nan,
            "n_valid_drifts": k,
            "e_pre_span": float(np.mean(errors[geo["span_lo"]:geo["span_hi"]])),
            "e_post": float(np.mean(errors[geo["first_drift"]:])),
            "alarms_pre_change": int(sum(1 for d in detections if d < geo["first_drift"]))}


# ─── rule B3 / B4 ─────────────────────────────────────────────────────────────────────────────────
def _paired(sweep, variant, role):
    """Seed-aligned (F1_HT, F1_ARF) at a given lambda role on one variant."""
    s = sweep[(sweep.variant == variant) & (sweep.lambda_role == role)]
    ht = s[s.pipeline == "pht_ht"].set_index("seed")["F1_bp"]
    arf = s[s.pipeline == "pht_arf_c1"].set_index("seed")["F1_bp"]
    idx = sorted(set(ht.index) & set(arf.index))
    return np.asarray([ht[i] for i in idx]), np.asarray([arf[i] for i in idx]), idx


def bootstrap_pairs(ht, arf, rng, n_boot=ssot.S2BIS_N_BOOTSTRAP):
    """Seed-paired bootstrap of the ratio and of the difference. The pair is the resampling unit:
    the two pipelines share the seed, the stream and the ground truth."""
    n = len(ht)
    draws = rng.integers(0, n, size=(n_boot, n))
    h, a = ht[draws].mean(axis=1), arf[draws].mean(axis=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = np.where(a > 0, h / a, np.nan)
    diff = h - a
    fin = ratio[np.isfinite(ratio)]
    return {"n_seeds": int(n),
            "F1_ht_mean": float(ht.mean()), "F1_arf_mean": float(arf.mean()),
            "ratio_point": float(ht.mean() / arf.mean()) if arf.mean() > 0 else None,
            "ratio_ci": ([float(np.percentile(fin, 2.5)), float(np.percentile(fin, 97.5))]
                         if fin.size else None),
            "ratio_undefined_fraction": float(1.0 - fin.size / n_boot),
            "diff_point": float(ht.mean() - arf.mean()),
            "diff_ci": [float(np.percentile(diff, 2.5)), float(np.percentile(diff, 97.5))]}


def gate_b3(stats):
    """Rule B3, applied exactly as written. The degenerate path is declared, not improvised."""
    degenerate = stats["F1_ht_mean"] == 0.0 or stats["F1_arf_mean"] == 0.0
    if degenerate or stats["ratio_ci"] is None:
        lo, hi = stats["diff_ci"]
        verdict = "COLLAPSE" if hi < 0.02 else ("SURVIVES" if lo > 0.05 else "INTERMEDIATE")
        return {"decision_variable": "dF1 = F1_HT - F1_ARF", "reason":
                "one arm has F1 = 0, the ratio is undefined; rule B3's declared degenerate path",
                "bands": {"COLLAPSE": "CI upper < 0.02", "SURVIVES": "CI lower > 0.05"},
                "point": stats["diff_point"], "ci": stats["diff_ci"], "verdict": verdict}
    lo, hi = stats["ratio_ci"]
    verdict = "COLLAPSE" if hi < 2.0 else ("SURVIVES" if lo > 5.0 else "INTERMEDIATE")
    return {"decision_variable": "rho_eq = F1_HT / F1_ARF", "reason": "both arms have F1 > 0",
            "bands": {"COLLAPSE": "CI upper < 2", "SURVIVES": "CI lower > 5"},
            "point": stats["ratio_point"], "ci": stats["ratio_ci"], "verdict": verdict}


def decompose_b4(sweep, variant, rng):
    """Rule B4. Four cells {ARF, HT} x {lambda_ref, lambda_eq}, on the log scale where every cell is
    strictly positive and on the difference scale otherwise -- the substitution is declared, never
    patched with an epsilon."""
    ht_r, arf_r, _ = _paired(sweep, variant, "lambda_ref")
    ht_e, arf_e, _ = _paired(sweep, variant, "lambda_eq_span")
    cells = {"F1_HT_lambda_ref": float(ht_r.mean()), "F1_ARF_lambda_ref": float(arf_r.mean()),
             "F1_HT_lambda_eq": float(ht_e.mean()), "F1_ARF_lambda_eq": float(arf_e.mean())}
    positive = all(v > 0 for v in cells.values())
    out = {"cells": cells, "scale": "log" if positive else "difference",
           "log_form_available": positive}
    if positive:
        n = len(ht_r)
        draws = rng.integers(0, n, size=(ssot.S2BIS_N_BOOTSTRAP, n))
        lr = np.log(ht_r[draws].mean(axis=1) / arf_r[draws].mean(axis=1))
        le = np.log(ht_e[draws].mean(axis=1) / arf_e[draws].mean(axis=1))
        out["ln_rho_ref"] = {"point": float(np.log(ht_r.mean() / arf_r.mean())),
                             "ci": [float(np.percentile(lr, 2.5)), float(np.percentile(lr, 97.5))]}
        out["ln_rho_eq_residual"] = {
            "point": float(np.log(ht_e.mean() / arf_e.mean())),
            "ci": [float(np.percentile(le, 2.5)), float(np.percentile(le, 97.5))]}
        out["threshold_attributable"] = {
            "point": float(np.log(ht_r.mean() / arf_r.mean()) - np.log(ht_e.mean() / arf_e.mean())),
            "ci": [float(np.percentile(lr - le, 2.5)), float(np.percentile(lr - le, 97.5))]}
        same_sign = (out["ln_rho_eq_residual"]["point"] > 0) == (
            out["threshold_attributable"]["point"] > 0)
        out["share_threshold_attributable"] = (
            out["threshold_attributable"]["point"] / out["ln_rho_ref"]["point"]
            if same_sign and out["ln_rho_ref"]["point"] != 0 else None)
        out["share_withheld_reason"] = (None if same_sign else
                                        "rule B4: the residual and the threshold-attributable term "
                                        "do not share a sign; no single percentage is reported")
    else:
        out["substitution"] = ("at least one cell has F1 = 0; the decomposition is reported on the "
                              "difference scale, dF1(lambda_ref) and dF1(lambda_eq), and the "
                              "log identity is not evaluated")
        out["dF1_ref"] = float(ht_r.mean() - arf_r.mean())
        out["dF1_eq"] = float(ht_e.mean() - arf_e.mean())
        out["threshold_attributable_difference"] = out["dF1_ref"] - out["dF1_eq"]
    return out


# ─── rule B10: pseudo-replication, frozen artifacts, reads only ───────────────────────────────────
def pseudo_replication():
    """`build_model` returns an unseeded HoeffdingTreeClassifier for every *_ht pipeline. Read on
    the frozen R5 artifacts; nothing is regenerated."""
    agg = pd.read_parquet(FROZEN_AGG)
    cols = ("lambda_calibrated", "F1_bp", "n_detections")
    out = {}
    for variant in cfg.INSECTS_VARIANTS:
        s = agg[(agg.variant == variant) & (agg.pipeline == "pht_ht")]
        # Zero variance is decided on EXACT distinctness, not on a computed standard deviation.
        # np.std over 30 bit-identical float64 values returns 5.6e-17 rather than 0 on the
        # reoccurring variant -- cancellation in the two-pass formula, not dispersion. nunique()
        # compares the stored values themselves and is the estimator rule B10 means.
        distinct = {c: int(s[c].nunique()) for c in cols}
        stds = {c: float(s[c].std(ddof=0)) for c in cols}
        out[variant] = {"n_runs": int(len(s)), "n_distinct": distinct,
                        "std_reported_as_a_diagnostic_only": stds,
                        "n_distinct_F1": distinct["F1_bp"],
                        "verdict": "PSEUDO-REPLICATED" if all(v == 1 for v in distinct.values())
                                   else "REPLICATED"}
    verdicts = {v["verdict"] for v in out.values()}
    out["overall"] = {
        "verdict": "PSEUDO-REPLICATED" if verdicts == {"PSEUDO-REPLICATED"} else "MIXED",
        "effective_independent_ht_replicates": 1 if verdicts == {"PSEUDO-REPLICATED"} else None,
        "consequence": ("the seed-level sign test of the Table I/II captions compares 30 ARF runs "
                        "against 30 copies of ONE HT run. With one effective replicate on the HT "
                        "arm the attainable two-sided sign-test p is 2^-1 x 2 = 1.0, so the "
                        "reported p is a bound on a statistic the design cannot support, not a "
                        "corrected value. The measured SEPARATION is unaffected; its stated unit "
                        "of statistical independence is."),
        "caption_claim": "the seed is the unit of statistical independence of the synthetic "
                         "generator (exp_R4_main_table.build_caption)"}
    return out


# ─── identity proof: lambda_calibrated == lambda_eq(T_warm) ───────────────────────────────────────
def identity_proof(cal):
    """Phase 1 step 3: re-derive the frozen `lambda_calibrated` column from the CSVs."""
    epi = pd.read_parquet(FROZEN_EPISODE)
    frozen = (epi.groupby(["variant", "pipeline"])["lambda_calibrated"]
              .agg(["mean", "min", "max", "std"]).reset_index())
    rows = []
    for _, f in frozen.iterrows():
        s = cal[(cal.variant == f.variant) & (cal.pipeline == f.pipeline)]
        if s.empty:
            continue
        d = float((s.lambda_eq_warm_emp.mean() - f["mean"]))
        rows.append({"variant": f.variant, "pipeline": f.pipeline,
                     "frozen_lambda_calibrated_mean": float(f["mean"]),
                     "frozen_min": float(f["min"]), "frozen_max": float(f["max"]),
                     "s2bis_lambda_eq_warm_mean": float(s.lambda_eq_warm_emp.mean()),
                     "abs_diff_mean": abs(d),
                     "identical": bool(abs(d) < 1e-9)})
    return rows


# ─── orchestration ────────────────────────────────────────────────────────────────────────────────
def run_calibration(variants, seed_pool):
    grid = [(v, s, p) for v in variants for s in seed_pool for p in PIPELINE_PAIR]
    print(f"[S2-bis/P1] calibration pass: {len(grid)} detector-free runs over the pre-change span",
          flush=True)
    res = Parallel(n_jobs=cfg.N_JOBS)(delayed(calibration_cell)(*a) for a in grid)
    return pd.DataFrame(res)


def sweep_tasks(cal, variants):
    """Per cell: the common ladder, plus that cell's own lambda_ref and lambda_eq. Deduplicated by
    exact threshold, ladder first, so a ladder point that coincides with a calibrated one is run
    once and carries the calibrated role."""
    tasks = []
    for variant in variants:
        for _, r in cal[cal.variant == variant].sort_values(["pipeline", "seed"]).iterrows():
            named = [(float(r.lambda_eq_warm_emp), "lambda_ref"),
                     (float(r.lambda_eq_span_emp), "lambda_eq_span")]
            seen = {}
            for lam, role in named:
                seen.setdefault(round(lam, 9), role)
            for lam in LAMBDA_GRID:
                if round(float(lam), 9) not in seen:
                    seen[round(float(lam), 9)] = "grid"
            for lam, role in sorted(seen.items()):
                tasks.append((variant, int(r.seed), r.pipeline, float(lam), role))
    return tasks


def run_sweep(tasks):
    print(f"[S2-bis/P1] lambda sweep: {len(tasks)} prequential runs "
          f"(no replay shortcut: the classifier resets on every alarm)", flush=True)
    res = Parallel(n_jobs=cfg.N_JOBS)(delayed(sweep_cell)(*a) for a in tasks)
    return pd.DataFrame(res)


def analyse(cal, sweep, variants):
    rng = np.random.default_rng(ssot.S2BIS_BOOTSTRAP_SEED)
    payload = {"targets": {
        "T_warm": "one expected false alarm over the warm-up "
                  f"(INSECTS_WARMUP_FRACTION = {cfg.INSECTS_WARMUP_FRACTION}); R5's own target",
        "T_span": "one expected false alarm over the armed pre-change span [warmup, first drift)",
        "carried_by": "T_span (rule B1)"},
        "scoring_convention": "evaluate_bipartite, closed window [d, d + tau]",
        "identity_lambda_calibrated_is_lambda_eq_T_warm": identity_proof(cal),
        "pseudo_replication_B10": pseudo_replication(),
        "variants": {}}
    for variant in variants:
        c = cal[cal.variant == variant]
        mismatch = {}
        for pipe in PIPELINE_PAIR:
            s = c[c.pipeline == pipe]
            mismatch[pipe] = {
                "lambda_eq_T_warm_mean": float(s.lambda_eq_warm_emp.mean()),
                "lambda_eq_T_span_mean": float(s.lambda_eq_span_emp.mean()),
                "lambda_eq_T_span_arl_mean": float(s.lambda_eq_span_arl.mean(skipna=True)),
                "theta_star_mean": float(s.theta_star_span.mean(skipna=True)),
                "arl_emp_ratio_mean": float(s.arl_emp_ratio.mean(skipna=True)),
                "B2_verdict": ("CONCORDANT" if bool(s.arl_concordant.all())
                               else "ANALYTIC MODEL INAPPLICABLE"),
                "p_true_span_mean": float(s.p_true_span.mean()),
                "p_true_span_band": [float(s.p_true_span.quantile(0.025)),
                                     float(s.p_true_span.quantile(0.975))],
                "expected_FA_of_T_warm_budget_over_span": float(s.fa_of_warm_lambda_over_span.mean()),
                "span_over_warmup": float(s.span_over_warmup.iloc[0]),
                "B7_verdict_T_span": sorted(set(s.verdict_span)),
                "B7_verdict_T_warm": sorted(set(s.verdict_warm))}
        entry = {"geometry": {k: v for k, v in
                              geometry(variant, int(c.n_total.iloc[0])).items()},
                 "budget_span_mismatch": mismatch,
                 "gate_B3": {}, "decomposition_B4": decompose_b4(sweep, variant, rng)}
        for role in ("lambda_ref", "lambda_eq_span"):
            ht, arf, idx = _paired(sweep, variant, role)
            st = bootstrap_pairs(ht, arf, np.random.default_rng(ssot.S2BIS_BOOTSTRAP_SEED))
            entry["gate_B3"][role] = {**st, "gate": gate_b3(st)}
        entry["gate_B3"]["verdict"] = entry["gate_B3"]["lambda_eq_span"]["gate"]["verdict"]
        entry["gate_B3"]["reference_ratio_at_frozen_calibration"] = 10.57
        payload["variants"][variant] = entry
    payload["B3_headline"] = {
        "variant": PRIORITY_VARIANT,
        "verdict": payload["variants"][PRIORITY_VARIANT]["gate_B3"]["verdict"],
        "at_lambda_eq": payload["variants"][PRIORITY_VARIANT]["gate_B3"]["lambda_eq_span"]["gate"],
        "at_lambda_ref": payload["variants"][PRIORITY_VARIANT]["gate_B3"]["lambda_ref"]["gate"]}
    return payload


def main(variants=None):
    variants = VARIANT_ORDER if variants is None else variants
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    seed_pool = common.make_seed_pool()

    cal = run_calibration(variants, seed_pool).sort_values(
        ["variant", "pipeline", "seed"]).reset_index(drop=True)
    cal.to_csv(OUT_DIR / "s2bis_lambda_eq_insects.csv", index=False)

    sweep = run_sweep(sweep_tasks(cal, variants)).sort_values(
        ["variant", "pipeline", "lambda", "seed"]).reset_index(drop=True)
    sweep.to_csv(OUT_DIR / "s2bis_insects_sweep.csv", index=False)

    payload = analyse(cal, sweep, variants)
    payload["reproduction"] = {
        "python": sys.version.split()[0],
        "artifacts_read": [str(FROZEN_EPISODE.relative_to(ROOT_DIR)),
                           str(FROZEN_AGG.relative_to(ROOT_DIR)),
                           "data/insects/*.csv"],
        "command": "PYTHONHASHSEED=0 python experiments/S2bis_calibration/s2bis_lambda_eq.py"}
    (OUT_DIR / "s2bis_flooding_gate.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=float) + "\n", encoding="utf-8")

    print("\n=== T_warm identity: lambda_calibrated == lambda_eq(T_warm) ===")
    for r in payload["identity_lambda_calibrated_is_lambda_eq_T_warm"]:
        print(f"  {r['variant']:33s} {r['pipeline']:11s} frozen "
              f"{r['frozen_lambda_calibrated_mean']:8.4f}  S2-bis "
              f"{r['s2bis_lambda_eq_warm_mean']:8.4f}  identical={r['identical']}")
    for variant in variants:
        e = payload["variants"][variant]
        print(f"\n=== {variant} ===")
        for pipe, m in e["budget_span_mismatch"].items():
            print(f"  {pipe:11s} lambda_eq(T_warm) {m['lambda_eq_T_warm_mean']:8.3f}  "
                  f"lambda_eq(T_span) {m['lambda_eq_T_span_mean']:8.3f}  "
                  f"ARL {m['lambda_eq_T_span_arl_mean']:8.3f}  "
                  f"B2 {m['B2_verdict']}  "
                  f"FA of the T_warm budget over the span "
                  f"{m['expected_FA_of_T_warm_budget_over_span']:.2f}")
        for role in ("lambda_ref", "lambda_eq_span"):
            g = e["gate_B3"][role]
            print(f"  {role:14s} F1_HT {g['F1_ht_mean']:.4f}  F1_ARF {g['F1_arf_mean']:.4f}  "
                  f"{g['gate']['decision_variable'].split('=')[0].strip()} = "
                  f"{g['gate']['point']}  CI {g['gate']['ci']}  -> {g['gate']['verdict']}")
        d = e["decomposition_B4"]
        print(f"  B4 scale={d['scale']}  cells={ {k: round(v, 4) for k, v in d['cells'].items()} }")
    print(f"\n[S2-bis/P1] B3 headline on {PRIORITY_VARIANT}: "
          f"{payload['B3_headline']['verdict']}")
    print(f"wrote {OUT_DIR.relative_to(ROOT_DIR)}/"
          "{s2bis_lambda_eq_insects.csv, s2bis_insects_sweep.csv, s2bis_flooding_gate.json}")
    return cal, sweep, payload


def demo():
    """Self-check. Writes nothing, touches no campaign: the statutory guard-rails of rule B7 and the
    monotonicity every downstream statement assumes."""
    # 1. lambda_eq is monotone INCREASING in p_true at a fixed target. The S2-bis plan states this
    #    guard-rail as "monotone decreasing"; the model's own arithmetic gives the opposite sign and
    #    the frozen measurement agrees, so the assertion is written in the direction the arithmetic
    #    fixes and the divergence is recorded in docs/theory/transfer_S2bis.md rather than silenced.
    #    A noisier pre-change stream has a SMALLER Cramer root -- theta* solves
    #    E[exp(theta (X - p_true - delta))] = 1 and shrinks as Var(X) = p(1-p) grows -- and ARL_0 is
    #    increasing in theta at fixed lambda, so a fixed false-alarm budget costs MORE threshold.
    #    Measured: e_pre 0.058 -> lambda 20.97 (ARF), e_pre 0.075 -> lambda 132.50 (HT).
    lams = [lambda_eq_arl(10_000.0, p)[0] for p in (0.01, 0.02, 0.04, 0.08)]
    assert all(a < b for a, b in zip(lams, lams[1:])), lams

    # 2. lambda_eq is monotone INCREASING in the target span.
    at = [lambda_eq_arl(n, 0.024)[0] for n in (1e3, 1e4, 1e5, 1e6)]
    assert all(a < b for a, b in zip(at, at[1:])), at

    # 3. p_true -> p_pre with River's adaptive mean is the calibrated case, not the degenerate one;
    #    the degenerate case is p_true >= p_pre + delta, where no positive Cramer root exists.
    try:
        cramer_root(0.5, 0.1, cfg.PHT_DELTA)
    except ValueError:
        pass
    else:
        raise AssertionError("a non-negative null drift must not return a Cramer root")
    assert lambda_eq_arl(1e4, 0.0)[0] is None

    # 4. The Siegmund inversion round-trips.
    th = cramer_root(0.024, 0.024, cfg.PHT_DELTA)
    assert abs(arl0(arl0_inverse(1e5, th, cfg.PHT_DELTA), th, cfg.PHT_DELTA) - 1e5) < 1e-3

    # 5. Rule B7. A span below the arming time is NOT ARMED; the bisection ceiling is SATURATED and
    #    is never returned as a value.
    assert calibration_verdict([0.0] * 10, 40.0)["verdict"] == "NOT ARMED"
    assert calibration_verdict([0.0] * 100, LAMBDA_HI)["verdict"] == "SATURATED"

    # 6. A constant error stream raises no PageHinkley alarm at any threshold: the statistic tracks
    #    its own mean, so a stream with no excursion cannot cross.
    assert count_false_alarms([0.0] * 500, 1.0) == 0

    # 7. Rule B3 arbitrates on the declared bands, and takes the difference path when an arm is 0.
    assert gate_b3({"F1_ht_mean": 0.25, "F1_arf_mean": 0.02, "ratio_point": 12.5,
                    "ratio_ci": [6.0, 20.0], "diff_point": 0.23,
                    "diff_ci": [0.1, 0.3]})["verdict"] == "SURVIVES"
    assert gate_b3({"F1_ht_mean": 0.25, "F1_arf_mean": 0.24, "ratio_point": 1.04,
                    "ratio_ci": [0.9, 1.2], "diff_point": 0.01,
                    "diff_ci": [-0.01, 0.019]})["verdict"] == "COLLAPSE"
    g = gate_b3({"F1_ht_mean": 0.0, "F1_arf_mean": 0.0, "ratio_point": None, "ratio_ci": None,
                 "diff_point": 0.0, "diff_ci": [-0.001, 0.001]})
    assert g["verdict"] == "COLLAPSE" and g["decision_variable"].startswith("dF1")

    print("s2bis_lambda_eq demo: OK")


if __name__ == "__main__":
    demo()
    if "--check" not in sys.argv:
        main()
