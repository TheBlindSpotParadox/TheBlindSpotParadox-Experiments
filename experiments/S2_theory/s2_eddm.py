"""Stream S2, Phase 5 (T2.4): why EDDM collapses, and whether `R_EDDM` survives rule R5.

`transfer_S1` open item 1: the normal approximation on geometric inter-error distances predicts
detection at `W = 155`; the experiment reports `F1 = 0.00`. The artifact is sharper than the
manuscript sentence -- `exp_R4_seed_level_tests.csv` records `EDDM+ARF c=1` at **0 detections in
1080 runs**, with the ADD column empty: the detector does not fire late, and does not false-alarm.
It never fires at all.

WHAT THE NORMAL APPROXIMATION OMITS. EDDM (River 0.23.0, `river/drift/binary/eddm.py`) compares
`p'_i + 2 s'_i` -- the CUMULATIVE mean and standard deviation of inter-error distances since the
last reset -- against `p'_max + 2 s'_max`, the RUNNING MAXIMUM of that same path:

    if  p2s'(k) >  max_{j<k} p2s'(j):   the maximum is raised, and NO level is computed
    elif n_errors > warm_start:         level := p2s'(k) / max_{j<k} p2s'(j), tested against beta

Two consequences the fixed-reference approximation cannot see.

  1. THE TEST IS NOT ALWAYS EXECUTED. While the classifier is still improving, the inter-error
     distances lengthen, `p2s'` keeps setting new maxima, and the `elif` branch is never reached.
     No level is computed, so no alarm is possible at any beta and any drift magnitude.
  2. THE STATISTIC IS DILUTED, NOT WINDOWED. `p'` and `s'` average over every distance since the
     last reset, so `n_0` pre-drift errors dilute `n_1` post-drift ones. The post-drift error
     fraction needed to pull the level under beta is a property of the PAIR (p_0, p_1) alone, and
     the number of post-drift STEPS needed is then proportional to `n_0` -- a quantity that does
     not appear anywhere in the normal approximation.

CLOSED FORM (this module). With inter-error distances geometric at rate `p_0` before the change and
`p_1` after, `d := 1/p`, `sigma^2 := (1-p)/p^2`, and `f := n_1/(n_0+n_1)` the post-drift share of
errors since the last reset,

    p'(f)    = (1-f) d_0 + f d_1
    s'(f)^2  = (1-f) sigma_0^2 + f sigma_1^2 + f(1-f) (d_0 - d_1)^2        <- between-group term
    level(f) = (p'(f) + 2 s'(f)) / (d_0 + 2 sigma_0)

`level` is continuous and decreasing on [0, 1] with `level(0) = 1`, so `f* := inf{f : level(f) <
beta}` is well defined, and detection requires

    W_EDDM = (n_0 / p_1) * f* / (1 - f*)        post-drift STEPS, with n_0 = (pre-drift steps) p_0.

WHAT THE SCALING ACTUALLY SAYS. `f*` is nearly invariant in the drift magnitude -- 0.235 to 0.240
over `p_1` in [0.10, 0.70] -- because the between-group term `f(1-f)(d_0-d_1)^2` grows with the
contrast at the same time as the mean falls, and the two largely cancel in the ratio. So

    W_EDDM ~ 0.31 n_0 / p_1 ,

which DOES shorten with the drift magnitude, at nearly the 1/Delta_e rate of a first-passage bound.
The distinction from a first-passage bound is therefore not the magnitude scaling but the factor
`n_0`: a threshold test needs an ABSOLUTE amount of evidence, whereas EDDM needs a fixed SHARE of
its own history, so its requirement grows without limit as the stationary phase lengthens. No
first-passage bound contains such a term, and the normal approximation on geometric distances
contains neither `n_0` nor the between-group variance.

VERIFICATION. River's EDDM is evaluated in closed form on the committed S6 traces -- the Lindley-
style vectorisation of the same recursion, certified against River's own object at startup -- so no
stream is simulated and no PRNG is involved.

Usage:  PYTHONHASHSEED=0 python experiments/S2_theory/s2_eddm.py
        python experiments/S2_theory/s2_eddm.py --check     (self-check only, writes nothing)
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.dataset as ds
from joblib import Parallel, delayed
from river.drift.binary import EDDM
from scipy.optimize import brentq

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import experiment_ssot as ssot  # noqa: E402
from s2_arl0 import OUT_DIR, P_TRUE, REFERENCE_ARM  # noqa: E402

TRACES = ssot.RESULTS_DIR / "S6_synchronized_traces" / "data" / "traces.parquet"
WARMUP = ssot.S6_WARMUP_WINDOW                 # 1000 pre-drift steps carried by the traces
T_HORIZON = ssot.S6_T_HORIZON                  # 2500 post-drift steps scored
ARMS = list(ssot.S6_ARM_NAMES)                 # full / no_swap / frozen / static
EDDM_WARM_START, EDDM_ALPHA, EDDM_BETA = 30, 0.95, 0.9      # River 0.23.0 defaults
NORMAL_APPROX_W = 155                          # transfer_S1 open item 1, the prediction under test
R4_T_DRIFT = ssot.R4_T_DRIFT                   # 4000: ProteuS arms the monitor from t = 0


# ── closed form ──────────────────────────────────────────────────────────────────────────────

def _moments(p):
    """(mean, variance) of the inter-error distance at error rate p, geometric on {1, 2, ...}."""
    return 1.0 / p, (1.0 - p) / p ** 2


def level(f, p0, p1):
    """EDDM's level statistic as a function of the post-drift share f of errors since reset."""
    d0, v0 = _moments(p0)
    d1, v1 = _moments(p1)
    var = (1 - f) * v0 + f * v1 + f * (1 - f) * (d0 - d1) ** 2
    return ((1 - f) * d0 + f * d1 + 2.0 * np.sqrt(var)) / (d0 + 2.0 * np.sqrt(v0))


def f_star(p0, p1, beta=EDDM_BETA):
    """inf{f in (0,1) : level(f) < beta}, or nan when the level never reaches beta."""
    if p1 <= p0:
        return np.nan
    g = lambda f: level(f, p0, p1) - beta                       # noqa: E731
    if g(1.0 - 1e-12) >= 0.0:
        return np.nan
    return float(brentq(g, 1e-12, 1.0 - 1e-12, xtol=1e-14, rtol=1e-15))


def w_eddm(p0, p1, n0, beta=EDDM_BETA):
    """Post-drift STEPS before EDDM can fire: (n_0/p_1) f*/(1-f*). inf when f* does not exist."""
    fs = f_star(p0, p1, beta)
    if not np.isfinite(fs):
        return np.inf
    return n0 / p1 * fs / (1.0 - fs)


# ── River's recursion, vectorised, certified against River itself ────────────────────────────

def eddm_path(err, warm_start=EDDM_WARM_START, beta=EDDM_BETA, alpha=EDDM_ALPHA):
    """First alarm index and the branch census of River's EDDM on one 0/1 error stream.

    Returns (first_drift_step, n_level_tests, min_level, n_max_updates, n_errors). The first alarm
    is the index into `err` (0-based) of the error that triggers it, or nan. Reset-on-drift is
    irrelevant to the FIRST alarm, which is what R4 scores, and is not modelled here."""
    err = np.asarray(err)
    idx = np.flatnonzero(err == 1)
    if idx.size == 0:
        return np.nan, 0, np.nan, 0, 0
    n_at_err = idx + 1                                  # River's _n at that error (1-based)
    d = np.diff(np.concatenate(([0], n_at_err)))        # _n - _last_error, the distance
    k = np.arange(1, d.size + 1)
    mean = np.cumsum(d) / k
    # sample variance, ddof = 1 (river.stats.Var default); undefined at k = 1
    m2 = np.cumsum(d ** 2) - k * mean ** 2
    with np.errstate(invalid="ignore", divide="ignore"):
        var = np.where(k > 1, m2 / np.maximum(k - 1, 1), 0.0)
    p2s = mean + 2.0 * np.sqrt(np.clip(var, 0.0, None))

    eligible = (n_at_err > warm_start)                  # River's `self._n > self.warm_start`
    running_max = np.concatenate(([-1.0], np.maximum.accumulate(np.where(eligible, p2s, -np.inf))))[:-1]
    # `_p2s_prime_max` only ever moves on an eligible error, and starts at -1.
    is_max_update = eligible & (p2s > running_max)
    testable = eligible & ~is_max_update & (k > warm_start)      # `self._n_errors > warm_start`
    lvl = np.where(testable & (running_max > 0), p2s / np.where(running_max > 0, running_max, 1.0),
                   np.nan)
    fired = testable & (lvl < beta)
    first = float(idx[np.argmax(fired)]) if fired.any() else np.nan
    with np.errstate(invalid="ignore"):
        min_level = float(np.nanmin(lvl)) if testable.any() else np.nan
    return first, int(testable.sum()), min_level, int(is_max_update.sum()), int(idx.size)


def _certify_against_river(n=4000, seed=7):
    """The vectorisation must agree with River's own object on the first alarm, or it is worthless.

    A deterministic pseudo-stream is built from a fixed generator local to this check; it feeds no
    experiment and leaves no artifact."""
    rng = np.random.default_rng(seed)
    for p0, p1 in ((0.05, 0.40), (0.024, 0.354), (0.10, 0.10), (0.30, 0.02)):
        err = np.concatenate([rng.binomial(1, p0, n // 2), rng.binomial(1, p1, n // 2)])
        det = EDDM(warm_start=EDDM_WARM_START, alpha=EDDM_ALPHA, beta=EDDM_BETA)
        ref = np.nan
        for i, x in enumerate(err):
            det.update(int(x))
            if det.drift_detected:
                ref = float(i)
                break
        got = eddm_path(err)[0]
        assert (np.isnan(ref) and np.isnan(got)) or ref == got, (p0, p1, ref, got)


# ── evaluation on the committed traces ───────────────────────────────────────────────────────

def partition(part):
    """Per (arm, seed) EDDM outcome on one magnitude partition of the committed traces."""
    delta_e = float(Path(part).name.split("=", 1)[1])
    df = ds.dataset(str(part), format="parquet").to_table(
        columns=["arm", "seed", "t_rel", "err"],
        filter=(ds.field("t_rel") >= -WARMUP) & (ds.field("t_rel") < T_HORIZON)
    ).to_pandas().sort_values(["arm", "seed", "t_rel"])

    out = []
    for (arm, seed), g in df.groupby(["arm", "seed"], sort=True):
        err = g["err"].to_numpy()
        t_rel = g["t_rel"].to_numpy()
        first, n_tests, min_lvl, n_max, n_err = eddm_path(err)
        pre = err[t_rel < 0]
        post = err[t_rel >= 0]
        out.append({"delta_e": delta_e, "arm": arm, "seed": int(seed),
                    "p0_hat": float(pre.mean()), "p1_hat": float(post[:200].mean()),
                    "n_errors_pre": int(pre.sum()),
                    "tau_det_eddm": np.nan if np.isnan(first) else float(t_rel[int(first)]),
                    "detected_post_drift": bool(first == first and t_rel[int(first)] >= 0)
                    if not np.isnan(first) else False,
                    "n_level_tests": n_tests, "min_level": min_lvl,
                    "n_max_updates": n_max, "n_errors": n_err})
    return out


def payload_controls(agg):
    """The three controls that decide whether a detection rate on these traces is interpretable."""
    ad = agg[agg.arm.isin(["full", "no_swap", "frozen"])]
    return {"warm": float(ad.warm_start_complete_at_tau.mean()),
            "n_pre": float(ad.n_errors_pre.median()),
            "static_fa": float(agg[agg.arm == "static"].pre_drift_alarm_rate.mean()),
            "spread": float(ad.pivot(index="delta_e", columns="arm", values="detection_rate")
                            .apply(lambda r: r.max() - r.min(), axis=1).max())}


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    _certify_against_river()
    if not TRACES.exists():
        raise SystemExit(f"[FATAL] {TRACES} absent -- run s6_runner.py full")

    parts = sorted(TRACES.iterdir())
    rows = [r for chunk in Parallel(n_jobs=-1)(delayed(partition)(p) for p in parts) for r in chunk]
    per_run = pd.DataFrame(rows)
    per_run["arm"] = pd.Categorical(per_run["arm"], categories=ARMS, ordered=True)

    agg = per_run.groupby(["arm", "delta_e"], observed=True).agg(
        n=("seed", "size"),
        p0_hat=("p0_hat", "median"), p1_hat=("p1_hat", "median"),
        n_errors_pre=("n_errors_pre", "median"),
        detection_rate=("detected_post_drift", "mean"),
        # The two controls that decide whether a detection rate on this stream means anything at
        # all: is the detector even warmed up at tau*, and does it alarm before the change?
        warm_start_complete_at_tau=("n_errors_pre", lambda s: float((s > EDDM_WARM_START).mean())),
        pre_drift_alarm_rate=("tau_det_eddm", lambda s: float((s < 0).mean())),
        median_tau_det=("tau_det_eddm", "median"),
        level_tests_zero=("n_level_tests", lambda s: float((s == 0).mean())),
        median_level_tests=("n_level_tests", "median"),
        median_min_level=("min_level", "median"),
        max_update_share=("n_max_updates", "median"),
    ).reset_index()
    agg.to_csv(OUT_DIR / "s2_eddm_traces.csv", index=False)

    # Closed form at the two pre-drift histories that matter: the traces' 1000 steps and R4's 4000.
    closed = []
    for de, g in per_run[per_run.arm == REFERENCE_ARM].groupby("delta_e"):
        p0, p1 = float(g.p0_hat.median()), float(g.p1_hat.median())
        for label, pre_steps in (("S6 traces", WARMUP), ("R4 ProteuS", R4_T_DRIFT)):
            n0 = pre_steps * p0
            closed.append({"delta_e": round(float(de), 6), "history": label,
                           "pre_drift_steps": pre_steps, "p_0": round(p0, 4), "p_1": round(p1, 4),
                           "n_0_errors": round(n0, 1), "f_star": f_star(p0, p1),
                           "W_EDDM_steps": w_eddm(p0, p1, n0),
                           "normal_approx_W": NORMAL_APPROX_W})
    closed = pd.DataFrame(closed)
    closed.to_csv(OUT_DIR / "s2_eddm_closed_form.csv", index=False)

    ref = agg[agg.arm == REFERENCE_ARM]
    print("=== T2.4 EDDM on the committed S6 traces (River 0.23.0 recursion, vectorised) ===")
    print(agg.pivot(index="delta_e", columns="arm", values="detection_rate")
          .to_string(float_format=lambda v: f"{v:.2f}"))
    print()
    print("  branch census, arm '%s': the level test is the `elif`; it never runs while the "
          "running maximum is still being raised" % REFERENCE_ARM)
    print(ref[["delta_e", "n", "p0_hat", "p1_hat", "detection_rate", "median_level_tests",
               "level_tests_zero", "median_min_level", "max_update_share"]]
          .to_string(index=False, float_format=lambda v: f"{v:.4g}"))
    print()
    ctrl = payload_controls(agg)
    print("  controls -- whether a detection rate on this stream means anything:")
    print(f"    adaptive arms, warm start complete at tau*: "
          f"{100 * ctrl['warm']:.0f} % of runs (median {ctrl['n_pre']:.0f} pre-drift errors "
          f"against warm_start = {EDDM_WARM_START})")
    print(f"    'static' arm, alarm BEFORE the change point: {100 * ctrl['static_fa']:.0f} % of runs")
    print(f"    detection-rate spread across full / no_swap / frozen: {ctrl['spread']:.3f}")
    print()
    print("=== T2.4 closed form: post-drift steps required before EDDM can fire ===")
    print(closed.pivot(index="delta_e", columns="history", values="W_EDDM_steps")
          .to_string(float_format=lambda v: f"{v:.1f}"))

    s6 = closed[closed.history == "S6 traces"]
    r4 = closed[closed.history == "R4 ProteuS"]
    payload = {
        "rule_R5": {
            "measured": {"source": "results/R4_proteus_evaluation/data/exp_R4_seed_level_tests.csv",
                         "pipeline": "EDDM+ARF c=1 against EDDM+HT",
                         "n_detected": 0, "n_total": 1080, "comparator_detected": 882,
                         "sign_test_p": 1.862645149230957e-09,
                         "note": "zero alarms, not late alarms: the ADD column of "
                                 "exp_R4_results_aligned_fusion.csv is empty on all 1080 runs"},
            "normal_approximation_W": NORMAL_APPROX_W,
            "closed_form_W_EDDM": {
                "S6_traces_median": float(np.nanmedian(s6.W_EDDM_steps.replace(np.inf, np.nan))),
                "R4_history_median": float(np.nanmedian(r4.W_EDDM_steps.replace(np.inf, np.nan))),
                "n_magnitudes_never_reachable": int((~np.isfinite(r4.W_EDDM_steps)).sum()),
                "scaling": "W_EDDM is proportional to n_0, the pre-drift error count since the "
                           "last reset; the normal approximation contains no such term",
            },
            "traces_detection_rate_full_arm": float(ref.detection_rate.mean()),
            "traces_level_test_never_run_share": float(ref.level_tests_zero.mean()),
            "traces_are_not_a_recall_test": {
                "warm_start_complete_at_tau_share_adaptive_arms": float(
                    agg[agg.arm.isin(["full", "no_swap", "frozen"])]
                    .warm_start_complete_at_tau.mean()),
                "median_pre_drift_errors_adaptive_arms": float(
                    agg[agg.arm.isin(["full", "no_swap", "frozen"])].n_errors_pre.median()),
                "warm_start": EDDM_WARM_START,
                "static_pre_drift_alarm_rate": float(
                    agg[agg.arm == "static"].pre_drift_alarm_rate.mean()),
                "max_abs_detection_rate_spread_across_adaptive_arms": float(
                    agg[agg.arm.isin(["full", "no_swap", "frozen"])]
                    .pivot(index="delta_e", columns="arm", values="detection_rate")
                    .apply(lambda r: r.max() - r.min(), axis=1).max()),
                "reading": "on the three adaptive arms the detector has not completed its "
                           "30-error warm-up at tau* (1000 pre-drift steps at p_0 = 0.024 give "
                           "~24 errors), so every alarm is post-warm-up by construction; on the "
                           "'static' arm, which does warm up, it alarms before the change point. "
                           "Neither configuration measures recall. The three adaptive arms -- "
                           "which differ by exactly the adaptation under study -- return the same "
                           "detection rate, which is what a drift-carrying statistic cannot do.",
            },
        },
        "per_magnitude_traces": agg.to_dict("records"),
        "closed_form": closed.to_dict("records"),
        "reproduction": {"python": sys.version.split()[0],
                         "artifact": str(TRACES.relative_to(ROOT_DIR)),
                         "command": "PYTHONHASHSEED=0 python experiments/S2_theory/s2_eddm.py",
                         "river": "0.23.0, drift.binary.EDDM defaults 30 / 0.95 / 0.90"},
    }
    (OUT_DIR / "s2_eddm.json").write_text(json.dumps(payload, indent=2, sort_keys=True,
                                                     default=float) + "\n", encoding="utf-8")
    print(f"\nwrote {OUT_DIR.relative_to(ROOT_DIR)}/"
          "{s2_eddm_traces.csv, s2_eddm_closed_form.csv, s2_eddm.json}")
    return per_run, agg, closed, payload


def demo():
    """Self-check: the closed form's endpoints and monotonicity, and the vectorised recursion
    against River's own object."""
    # 1. level(0) = 1 by construction, and the level decreases as post-drift errors accumulate.
    assert abs(level(0.0, 0.024, 0.354) - 1.0) < 1e-12
    fs = np.linspace(0.0, 1.0, 101)
    assert np.all(np.diff(level(fs, 0.024, 0.354)) < 0)

    # 2. No drift (p_1 = p_0): the level is identically 1 and f* does not exist.
    assert np.allclose(level(fs, 0.05, 0.05), 1.0)
    assert np.isnan(f_star(0.05, 0.05)) and w_eddm(0.05, 0.05, 50.0) == np.inf

    # 3. W_EDDM is proportional to n_0 -- the term the normal approximation omits entirely.
    a, b = w_eddm(0.024, 0.354, 24.0), w_eddm(0.024, 0.354, 96.0)
    assert abs(b / a - 4.0) < 1e-9, (a, b)

    # 4. The between-group term is what keeps s' large: dropping it makes detection look easy.
    d0, v0 = _moments(0.024)
    d1, v1 = _moments(0.354)
    f = 0.25
    with_between = (1 - f) * v0 + f * v1 + f * (1 - f) * (d0 - d1) ** 2
    without = (1 - f) * v0 + f * v1
    assert with_between > without > 0.0

    # 5. Degenerate streams.
    assert np.isnan(eddm_path(np.zeros(500))[0])          # no error, no distance, no alarm
    assert np.isnan(eddm_path(np.ones(20))[0])            # below warm_start
    assert eddm_path(np.array([], dtype=int))[0] is not None

    # 6. The vectorisation reproduces River's own object.
    _certify_against_river()
    print("s2_eddm demo: OK")


if __name__ == "__main__":
    demo()
    if "--check" not in sys.argv:
        main()
