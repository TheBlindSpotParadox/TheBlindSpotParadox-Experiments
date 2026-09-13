"""Stream S8 / T8.3 -- internal mechanisms x ensemble families, at equal evidence budget.

Reviewer #2's objection is that the blind spot is a property of the River ADWIN/ARF configuration.
S5 answered it with an argument (closed-loop topology); without an inter-mechanism replication that
answer is an analogy. This is the experiment.

Two axes, one calibration rule.

  internal mechanism   ARFClassifier(drift_detector=D, warning_detector=D) for
                       D in {ADWIN, DDM, EDDM, PageHinkley, KSWIN}. Feasible on the pinned build:
                       `ARFClassifier._drift_detector_input` returns `int(not y_true == y_pred)`
                       (river/forest/adaptive_random_forest.py:710-713), exactly the binary stream
                       river.drift.binary.DDM / EDDM consume and an admissible input for the other
                       three. DDM and EDDM live under `river.drift.binary`, NOT `river.drift`; the
                       guarded import already written at exp_R4_main_table.py:168-171 is reused.
  ensemble family      SRPClassifier, LeveragingBaggingClassifier, ADWINBaggingClassifier and
                       HoeffdingAdaptiveTreeClassifier. The last three have never been instantiated
                       in this repository. The prompt's "OzaBagADWIN" does not exist under river
                       0.23.0; the object is ADWINBaggingClassifier.

What this file refuses to do. Three streams have now shown what a common NOMINAL threshold measures:
the INSECTS flooding ratio 10.57x collapses to 1.270 once the reach budget is equalised (89.9 % of
the log-ratio was the threshold), and at lambda = 15 ADWIN is deployed 45x tighter and KSWIN 4.5x
looser than the CUSUM. Comparing families at a shared nominal threshold compares calibrations. The
external monitor is therefore calibrated on the PRE-DRIFT stream OF ITS OWN PIPELINE -- never
shared, because pre-drift volatility is itself a property of the pipeline -- and the common-threshold
arm (lambda = 50 and 25, R2's scenarios A and B) is reported BESIDE it so the gap stays visible.

The internal mechanisms are NOT equalised against each other: their identity is the variable under
study. Only the external monitor is.

The stream is the rotation family at eta = S8_MECH_ETA, the only one of the two carrying a binding
false-alarm budget (D5) -- at eta = 0 the pre-drift Bayes error is exactly 0.

Boundary with S9, which must stay sharp: S8 varies the INTERNAL mechanism of the adaptive
classifier; S9 varies the family of the EXTERNAL monitor. Neither re-implements the other's
instrumentation.

Output: results/S8_mechanisms/data/s8_mechanisms_runs.parquet
        results/S8_mechanisms/tables/s8_mechanisms_calibration.csv
        results/S8_mechanisms/tables/s8_mechanisms_collapse.json

Usage:  PYTHONHASHSEED=0 python experiments/S8_generality/s8_mechanisms.py [demo|smoke|full|read]
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from river import drift, ensemble, forest, tree
from tqdm import tqdm

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "S6_synchronized_traces"))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "S6_synchronized_traces" / "gates"))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "S8_generality"))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "R5_real_world_evaluation"))

import s6_defs as defs  # noqa: E402
import s8_rotation as rot  # noqa: E402
import _gate_common as common  # noqa: E402
import exp_R5_common as r5  # noqa: E402
from config import experiment_ssot as ssot  # noqa: E402

try:                                            # exp_R4_main_table.py:168-171, verbatim
    from river.drift.binary import DDM, EDDM
except ImportError:                             # pragma: no cover - pinned build has the submodule
    from river.drift import DDM, EDDM

RESULTS_DIR = ssot.RESULTS_DIR / "S8_mechanisms"
N_STEPS = ssot.S8_N_STEPS
T_DRIFT = ssot.S8_T_DRIFT
N_MODELS = ssot.S8_N_MODELS
C_INT = ssot.S8_C_INT
WARMUP = ssot.S8_WARMUP_WINDOW
T_HORIZON = ssot.S8_T_HORIZON
ERR_WINDOW = ssot.S6_ERR_WINDOW
AUDIT_DELTA_P = ssot.S8_AUDIT_DELTA_P
ETA = ssot.S8_MECH_ETA
CONTROL_LAMBDAS = ssot.S8_CONTROL_LAMBDAS
LAMBDA_LO, LAMBDA_HI = ssot.S8_LAMBDA_BRACKET
TARGET_FA = ssot.S8_PHT_TARGET_FA
BISECT_ITER = 25                                # exp_R5_common.calibrate_lambda's max_iter

# River defaults, pinned by name rather than by literal: a bare `threshold=` or `n_models=` literal
# fails tests/test_S7_consistency.py, and River's own defaults are what make each mechanism itself.
INTERNAL_PHT_LAMBDA = ssot.R3_PHT_LAMBDA        # 25.0
INTERNAL_KSWIN_ALPHA = ssot.R4_KSWIN_ALPHA      # 0.005, R4's pinned value
INTERNAL_EDDM_WARM_START = ssot.S2BIS_EDDM_WARM_START


def _adwin():
    """The blind-spot configuration: River's ADWIN on the hyper-reactive internal clock."""
    return drift.ADWIN(clock=C_INT)


MECHANISMS = {
    "ADWIN": _adwin,
    "DDM": lambda: DDM(),
    "EDDM": lambda: EDDM(warm_start=INTERNAL_EDDM_WARM_START),
    "PageHinkley": lambda: drift.PageHinkley(threshold=INTERNAL_PHT_LAMBDA),
    "KSWIN": lambda: drift.KSWIN(alpha=INTERNAL_KSWIN_ALPHA),
}
# `clock` is an ADWIN parameter and has no analogue in the other four. The c_int = 1 configuration
# the manuscript calls hyper-reactive therefore CANNOT be transported to them; that asymmetry is a
# finding of this grid, not a defect of it, and is reported rather than papered over with a
# substitute knob.


def make_arf(mechanism, safe_seed):
    return forest.ARFClassifier(n_models=N_MODELS, seed=safe_seed,
                                drift_detector=MECHANISMS[mechanism](),
                                warning_detector=MECHANISMS[mechanism]())


def make_srp(safe_seed):
    return ensemble.SRPClassifier(model=tree.HoeffdingTreeClassifier(), n_models=N_MODELS,
                                  drift_detector=_adwin(), warning_detector=_adwin(),
                                  seed=safe_seed)


ENSEMBLES = {
    "SRP": make_srp,
    "LeveragingBagging": lambda s: ensemble.LeveragingBaggingClassifier(
        model=tree.HoeffdingTreeClassifier(), n_models=N_MODELS, seed=s),
    "ADWINBagging": lambda s: ensemble.ADWINBaggingClassifier(
        model=tree.HoeffdingTreeClassifier(), n_models=N_MODELS, seed=s),
    "HAT": lambda s: tree.HoeffdingAdaptiveTreeClassifier(seed=s),
}

PIPELINES = ({f"ARF_{m}": ("mechanism", m) for m in MECHANISMS}
             | {f"ENS_{e}": ("ensemble", e) for e in ENSEMBLES})


def build(pipeline, safe_seed):
    axis, key = PIPELINES[pipeline]
    return make_arf(key, safe_seed) if axis == "mechanism" else ENSEMBLES[key](safe_seed)


# ══════════════════════════════════════════════════════════════════════════════
# external monitor: one reflected CUSUM path, every threshold read off it
# ══════════════════════════════════════════════════════════════════════════════
def count_alarms(excess, threshold):
    """False alarms of a reflected CUSUM over `excess`, resetting at each alarm.

    Same recursion as `s6_detectors.StrictCUSUM` and as `s6_defs.accumulations`'s reflected branch;
    the reset on alarm is what a deployed monitor does and what `exp_R5_common.calibrate_lambda`
    counts on its own detector."""
    n, s = 0, 0.0
    for e in excess:
        s = max(0.0, s + e)
        if s >= threshold:
            n += 1
            s = 0.0
    return n


def calibrate_cusum(excess, target_fa=TARGET_FA, lo=LAMBDA_LO, hi=LAMBDA_HI, max_iter=BISECT_ITER):
    """Bisection of the CUSUM threshold to a false-alarm budget, `calibrate_lambda`'s scheme.

    The fallback to `target_fa = 3` when 1 is infeasible is R5's, kept so the two calibrations are
    the same procedure applied to two detector families."""
    low, high = lo, hi
    for _ in range(max_iter):
        mid = (low + high) / 2.0
        if count_alarms(excess, mid) <= target_fa:
            high = mid
        else:
            low = mid
    if count_alarms(excess, high) > target_fa and target_fa == 1:
        return calibrate_cusum(excess, target_fa=3, lo=lo, hi=hi, max_iter=max_iter)
    return high, target_fa


def calibration_verdict(span, lam, attained, target_fa=TARGET_FA):
    """The five terminal states the repository uses, as their UNION.

    Four come from `s2bis_lambda_eq.calibration_verdict` (OK / SATURATED / NOT ATTAINABLE /
    NOT ARMED) and the fifth from `s2bis_proteus_calibration.calibration_verdict`, which added
    NOT BINDING at the bisection FLOOR: a budget met at every admissible threshold constrains
    nothing and is a bound, never a calibrated value. On a low-e_pre stream NOT BINDING is the
    expected outcome and it is informative."""
    if span < ssot.S2BIS_PHT_MIN_INSTANCES:
        return "NOT ARMED"
    if lam >= LAMBDA_HI:
        return "SATURATED"
    if lam <= LAMBDA_LO * (1.0 + 1e-4):
        return "NOT BINDING"
    if attained > target_fa:
        return "NOT ATTAINABLE"
    return "OK"


def first_crossing(path, threshold):
    hit = np.flatnonzero(path >= threshold)
    return float(hit[0]) if hit.size else np.nan


# ══════════════════════════════════════════════════════════════════════════════
def run_cell(pipeline, seed, delta_e, eta=ETA):
    """One (pipeline, seed, Delta_e) prequential run on the rotation stream."""
    safe_seed, x, y = rot.make_rotation_stream(seed, delta_e, eta)
    model = build(pipeline, safe_seed)
    err = np.zeros(N_STEPS, dtype=np.int8)
    tracker = getattr(model, "_drift_tracker", None)
    swaps_before_drift, tau_swap = None, np.nan

    for t in range(N_STEPS):
        x_dict = {0: x[t, 0], 1: x[t, 1]}
        y_pred = model.predict_one(x_dict)
        err[t] = int((y_pred if y_pred is not None else 0) != y[t])
        model.learn_one(x_dict, int(y[t]))
        if tracker is None:
            continue
        if t == T_DRIFT - 1:
            swaps_before_drift = sum(tracker.values())
        elif t >= T_DRIFT and np.isnan(tau_swap) and sum(tracker.values()) > swaps_before_drift:
            tau_swap = float(t - T_DRIFT)

    pre = err[T_DRIFT - WARMUP:T_DRIFT].astype(np.float64)
    post = err[T_DRIFT:T_DRIFT + T_HORIZON].astype(np.float64)
    e_pre = float(pre.mean())
    delta_e_emp = float(post[:ERR_WINDOW].mean()) - e_pre

    a_unrefl, a_refl = defs.accumulations(post, e_pre, AUDIT_DELTA_P)
    lam_eq, target = calibrate_cusum(pre - e_pre - AUDIT_DELTA_P)
    attained = count_alarms(pre - e_pre - AUDIT_DELTA_P, lam_eq)
    lam_pht = float(r5.calibrate_lambda(list(pre)))

    rec = {"pipeline": pipeline, "axis": PIPELINES[pipeline][0], "seed": int(seed),
           "delta_e": float(delta_e), "eta": float(eta),
           "e_pre": e_pre, "delta_e_emp": delta_e_emp,
           "tau_swap": tau_swap, "has_internal_tracker": tracker is not None,
           "a_unrefl_peak": float(a_unrefl.max()),
           "tau_erase": float(np.argmax(a_unrefl)),
           "lambda_eq": float(lam_eq), "lambda_eq_target_fa": int(target),
           "lambda_eq_attained_fa": int(attained),
           "lambda_eq_verdict": calibration_verdict(pre.size, lam_eq, attained, target),
           "lambda_eq_pht": lam_pht,
           "tau_det_lambda_eq": first_crossing(a_refl, lam_eq)}
    for lam in CONTROL_LAMBDAS:
        rec[f"tau_det_lambda{lam:g}"] = first_crossing(a_refl, lam)
    return rec


def campaign(pipelines, seeds, grid, n_jobs=-1, desc="S8 mech"):
    cells = [(p, s, de) for de in grid for p in pipelines for s in seeds]
    rows = Parallel(n_jobs=n_jobs)(delayed(run_cell)(p, s, de)
                                   for p, s, de in tqdm(cells, desc=desc))
    return pd.DataFrame(rows)


# ══════════════════════════════════════════════════════════════════════════════
# D7 -- collapse of the miss-rate curves against A
# ══════════════════════════════════════════════════════════════════════════════
def wilson(k, n, z=1.959963984540054):
    """Wilson 95 % interval. At these frequencies a normal-approximation interval is nonsense."""
    if n == 0:
        return (np.nan, np.nan)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (float(c - h), float(c + h))


def miss_columns(df, lam_col="tau_det_lambda_eq"):
    out = df.copy()
    out["miss"] = ~np.isfinite(out[lam_col])
    out["miss_before_erase"] = ~(np.isfinite(out[lam_col]) & (out[lam_col] <= out.tau_erase))
    return out


def collapse(df, n_bins=4, min_cells=5, lam_col="tau_det_lambda_eq"):
    """D7 on the mechanism axis: at MATCHED A, does the between-mechanism spread stay inside the
    within-mechanism 95 % interval?

    Matching is on A (`a_unrefl_peak`) and not on Delta_e: A is the evidence an external monitor
    actually receives, and two mechanisms at the same Delta_e that hand it different budgets are not
    at the same operating point."""
    sub = miss_columns(df[df.axis == "mechanism"], lam_col)
    edges = np.quantile(sub.a_unrefl_peak, np.linspace(0, 1, n_bins + 1))
    edges[0], edges[-1] = -np.inf, np.inf
    sub = sub.assign(a_bin=pd.cut(sub.a_unrefl_peak, edges, labels=False, include_lowest=True))

    bins, verdicts = [], []
    for b, g in sub.groupby("a_bin"):
        per = []
        for mech, gm in g.groupby("pipeline"):
            k, n = int(gm.miss.sum()), int(len(gm))
            if n < min_cells:
                continue
            lo, hi = wilson(k, n)
            per.append({"pipeline": mech, "n": n, "miss_rate": k / n, "ci_lo": lo, "ci_hi": hi,
                        "ci_width": hi - lo, "median_a": float(gm.a_unrefl_peak.median()),
                        "median_tau_erase": float(gm.tau_erase.median()),
                        "median_lambda_eq": float(gm.lambda_eq.median())})
        if len(per) < 2:
            continue
        rates = [p["miss_rate"] for p in per]
        spread = float(max(rates) - min(rates))
        widest = float(max(p["ci_width"] for p in per))
        verdicts.append(spread <= widest)
        bins.append({"a_bin": int(b), "n_pipelines": len(per),
                     "a_range": [float(g.a_unrefl_peak.min()), float(g.a_unrefl_peak.max())],
                     "between_mechanism_spread": spread, "widest_within_ci": widest,
                     "collapses": spread <= widest, "per_pipeline": per})
    return {"n_bins_evaluated": len(bins),
            "verdict": ("COLLAPSE" if bins and all(verdicts) else
                        "NOT PRODUCED" if not bins else "DOES NOT COLLAPSE"),
            "bins": bins}


def closed_loop_check(df, reference="ARF_ADWIN", tau_factor=1.5, lam_col="tau_det_lambda_eq"):
    """D7 second clause: a non-ADWIN mechanism at comparable tau_erase and at lambda_eq must
    produce a comparable blind spot, or the closed-loop reframing is FALSE as stated."""
    sub = miss_columns(df[df.axis == "mechanism"], lam_col)
    rows, refuted = [], []
    for de, g in sub.groupby("delta_e"):
        ref = g[g.pipeline == reference]
        if ref.empty:
            continue
        k, n = int(ref.miss.sum()), int(len(ref))
        ref_lo, ref_hi = wilson(k, n)
        ref_tau = float(ref.tau_erase.median())
        for pipe, gp in g.groupby("pipeline"):
            if pipe == reference:
                continue
            tau = float(gp.tau_erase.median())
            comparable_tau = bool(tau <= tau_factor * ref_tau and tau >= ref_tau / tau_factor)
            rate = float(gp.miss.mean())
            comparable_spot = bool(ref_lo <= rate <= ref_hi)
            rows.append({"delta_e": float(de), "pipeline": pipe,
                         "median_tau_erase": tau, "reference_median_tau_erase": ref_tau,
                         "comparable_tau_erase": comparable_tau,
                         "miss_rate": rate, "reference_miss_rate": k / n,
                         "reference_ci": [ref_lo, ref_hi],
                         "comparable_blind_spot": comparable_spot,
                         "median_lambda_eq": float(gp.lambda_eq.median()),
                         "verdict_row": ("N/A" if not comparable_tau else
                                         "HOLDS" if comparable_spot else "REFUTES")})
            if comparable_tau and not comparable_spot:
                refuted.append(f"{pipe} @ Delta_e={de:.6f}")
    return {"reference": reference, "tau_comparability_factor": tau_factor,
            "verdict": "FALSE AS STATED" if refuted else "UPHELD",
            "refuting_cells": refuted, "rows": rows}


def read(path=None):
    path = Path(path) if path else RESULTS_DIR / "data" / "s8_mechanisms_runs.parquet"
    df = pd.read_parquet(path)
    tables = RESULTS_DIR / "tables"
    tables.mkdir(parents=True, exist_ok=True)

    cal = df.groupby(["axis", "pipeline", "delta_e"], as_index=False).agg(
        n=("seed", "size"), median_e_pre=("e_pre", "median"),
        median_delta_e_emp=("delta_e_emp", "median"),
        median_lambda_eq=("lambda_eq", "median"), median_lambda_eq_pht=("lambda_eq_pht", "median"),
        median_tau_swap=("tau_swap", "median"), median_tau_erase=("tau_erase", "median"),
        median_a=("a_unrefl_peak", "median"),
        verdict_mode=("lambda_eq_verdict", lambda s: s.mode().iat[0]))
    m = miss_columns(df)
    for lam in CONTROL_LAMBDAS:
        col = f"tau_det_lambda{lam:g}"
        cal[f"miss_rate_lambda{lam:g}"] = (
            df.assign(miss=~np.isfinite(df[col]))
              .groupby(["axis", "pipeline", "delta_e"]).miss.mean().values)
    cal["miss_rate_lambda_eq"] = m.groupby(["axis", "pipeline", "delta_e"]).miss.mean().values
    cal["miss_rate_before_erase_lambda_eq"] = (
        m.groupby(["axis", "pipeline", "delta_e"]).miss_before_erase.mean().values)
    cal.to_csv(tables / "s8_mechanisms_calibration.csv", index=False)

    payload = {"source": str(path.relative_to(ssot.ROOT_DIR)), "eta": float(df.eta.iloc[0]),
               "n_cells": int(len(df)), "pipelines": sorted(df.pipeline.unique()),
               "control_lambdas": CONTROL_LAMBDAS,
               "verdict_counts": df.lambda_eq_verdict.value_counts().to_dict(),
               "D7_collapse": collapse(df), "D7_closed_loop": closed_loop_check(df)}
    (tables / "s8_mechanisms_collapse.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=float) + "\n", encoding="utf-8")

    print(f"=== S8 mechanisms === {payload['n_cells']} cells, eta = {payload['eta']}")
    print("  calibration verdicts:", payload["verdict_counts"])
    print(cal[["pipeline", "delta_e", "median_lambda_eq", "median_a", "median_tau_erase",
               "miss_rate_lambda_eq", "miss_rate_lambda50"]].to_string(index=False))
    print(f"\n  D7 collapse    : {payload['D7_collapse']['verdict']} "
          f"({payload['D7_collapse']['n_bins_evaluated']} A-bins)")
    print(f"  D7 closed loop : {payload['D7_closed_loop']['verdict']} "
          f"{payload['D7_closed_loop']['refuting_cells'][:6]}")
    print(f"[INFO] wrote {(tables / 's8_mechanisms_collapse.json').relative_to(ssot.ROOT_DIR)}")
    return payload


def demo():
    """Self-check: every pipeline builds and learns, and the calibrator obeys its five states."""
    for pipeline in PIPELINES:
        model = build(pipeline, 7)
        for t in range(64):
            model.learn_one({0: float(t % 3), 1: float(t % 5)}, int(t % 2))
        assert model.predict_one({0: 1.0, 1: 2.0}) in (0, 1, None), pipeline

    quiet = np.full(1000, -AUDIT_DELTA_P)                       # no excess at all
    lam, _ = calibrate_cusum(quiet)
    assert calibration_verdict(quiet.size, lam, 0) == "NOT BINDING", lam
    flooding = np.ones(2000)                                    # crosses every admissible threshold
    lam, target = calibrate_cusum(flooding)
    assert calibration_verdict(flooding.size, lam, count_alarms(flooding, lam),
                               target) == "SATURATED", lam
    assert calibration_verdict(10, 5.0, 0) == "NOT ARMED"
    assert count_alarms([0.6, 0.6, 0.6], 1.0) == 1              # resets after the alarm
    assert first_crossing(np.array([0.0, 2.0, 1.0]), 1.5) == 1.0
    assert np.isnan(first_crossing(np.zeros(3), 1.0))
    lo, hi = wilson(0, 100)
    assert abs(lo) < 1e-12 and 0.03 < hi < 0.04, (lo, hi)
    print("s8_mechanisms demo: OK  " + ", ".join(sorted(PIPELINES)))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "full"
    if mode == "demo":
        demo()
    elif mode == "read":
        read()
    elif mode in ("smoke", "full"):
        seeds = common.seed_pool(5 if mode == "smoke" else ssot.S8_MECH_N_SEEDS)
        grid = (ssot.S8_MECH_DELTA_E[:2] if mode == "smoke" else ssot.S8_MECH_DELTA_E)
        print(f"[INFO] S8 mechanisms {mode}: {len(PIPELINES)} pipelines x {len(grid)} magnitudes "
              f"x {len(seeds)} seeds = {len(PIPELINES) * len(grid) * len(seeds)} cells, eta = {ETA}")
        df = campaign(list(PIPELINES), seeds, grid, desc=f"S8 mech {mode}")
        out = RESULTS_DIR / ("smoke" if mode == "smoke" else "data")
        out.mkdir(parents=True, exist_ok=True)
        path = out / "s8_mechanisms_runs.parquet"
        df.to_parquet(path, index=False)
        print(f"[INFO] wrote {path.relative_to(ssot.ROOT_DIR)}")
        read(path)
    else:
        raise SystemExit(f"usage: s8_mechanisms.py [demo|smoke|full|read]  (got {mode!r})")
