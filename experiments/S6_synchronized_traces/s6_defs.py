"""Stopping metrics and proof integrals of stream S6.

Three failures fix the definitions here.

F6 -- `tau_ARF = min_i tau_i` is a contested proxy for ensemble adaptation. Every tau_swap in this
module is computed on DISTINCT trees, from the per-key diff of `_drift_tracker`, never from
`sum(values())`: a tree that is replaced three times contributes one adapted tree, not three. The
Hydra count is kept as a separate observable (`swaps_cum`) so the gap between the two is measurable
rather than hidden.

F7 -- the real transient is not rectangular. `A` is the integrated post-drift error excess actually
observed; `A_rect` is the rectangle R8's reasoning implies (empirical Delta_e held over
tau_swap^(1/M)); `A_refl` is the reflected accumulation an external CUSUM can see. The three are
reported side by side and their ordering is the evidence, not an assumption.

F25 -- the ensemble error and the internal statistics must come from one trajectory. Gate G0
established that `predict_one()` consumes no RNG state, so the harness runs both on the same stream.

Sign convention. The excess of one step is `err - e_pre - delta_P`. `A_unrefl` is its running sum,
free to decrease; `A_refl` is the same sum floored at zero at every step, which is exactly the
`StrictCUSUM` statistic. `A_refl[t] >= A_unrefl[t]` holds at every t by construction, and
`tau_erase` reads the instant at which the unreflected evidence stops growing -- the step where the
internal adaptation has erased the fuel the external detector was accumulating.
"""
import sys
from pathlib import Path

import numpy as np

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))
from config import experiment_ssot as ssot  # noqa: E402

WARMUP = ssot.S6_WARMUP_WINDOW
ERR_WINDOW = ssot.S6_ERR_WINDOW
HYSTERESIS = ssot.S6_ERR_HYSTERESIS
RHO_GRID = ssot.S6_RHO_GRID
Q_GRID = ssot.S6_Q_GRID
T_HORIZON = ssot.S6_T_HORIZON
DELTA_P = ssot.DELTA_P


def distinct_trees_cum(replaced_per_step):
    """Cumulative count of DISTINCT trees replaced at least once since the drift.

    `replaced_per_step[t]` is the set of tree indices whose `_drift_tracker` entry INCREMENTED at
    step t -- the per-key diff of the tracker, never `sum(values())`. A tree replaced three times
    contributes one, which is the whole of F6: the Hydra count and the adaptation count are not the
    same number, and only the second is an adaptation.

    A tree that had already been replaced before the drift keeps its tracker key, so first-appearance
    of a key would miss its post-drift replacement entirely. Counting increments does not; the runner
    records how many trees were in that state at the drift instant (`n_trees_swapped_pre_drift`) so
    the edge case is documented by data rather than by assumption. Returns an int array."""
    seen, out = set(), np.empty(len(replaced_per_step), dtype=np.int32)
    for t, replaced in enumerate(replaced_per_step):
        seen |= set(replaced)
        out[t] = len(seen)
    return out


def tau_swap(trees_cum, n_models, q):
    """First post-drift step at which ceil(q * M) DISTINCT trees have been replaced.

    q = 1/M recovers the first-swap instant the manuscript calls tau_swap^(1/M). NaN when the
    threshold is never reached inside the traced window (censored)."""
    need = int(np.ceil(q * n_models))
    hit = np.flatnonzero(trees_cum >= need)
    return float(hit[0]) if hit.size else np.nan


def rolling_mean(x, window):
    """Trailing mean over `window` steps; the first `window - 1` entries are NaN."""
    x = np.asarray(x, dtype=np.float64)
    if x.size < window:
        return np.full(x.size, np.nan)
    c = np.concatenate(([0.0], np.cumsum(x)))
    out = np.full(x.size, np.nan)
    out[window - 1:] = (c[window:] - c[:-window]) / window
    return out


def tau_err(err_post, e_pre, delta_e_emp, rho, window=ERR_WINDOW, hysteresis=HYSTERESIS):
    """First post-drift step at which the smoothed error has stayed under the recovery threshold
    for `hysteresis` consecutive steps.

    Threshold = e_pre + rho * Delta_e_emp, with Delta_e_emp the EMPIRICAL jump measured on this run,
    not the theoretical one: the recovery level has to be read against the error the run actually
    reached. The hysteresis is H = W/2, the R4 smoothing convention; without it a single-window
    excursion under the threshold would be read as a recovery. Returned instant is the step at which
    the run of H steps COMPLETES. NaN when it never does."""
    if not np.isfinite(delta_e_emp) or delta_e_emp <= 0:
        return np.nan
    smooth = rolling_mean(err_post, window)
    under = np.zeros(smooth.size, dtype=bool)
    valid = np.isfinite(smooth)
    under[valid] = smooth[valid] <= e_pre + rho * delta_e_emp
    run = 0
    for t, u in enumerate(under):
        run = run + 1 if u else 0
        if run >= hysteresis:
            return float(t)
    return np.nan


def accumulations(err_post, e_pre, delta=DELTA_P):
    """(A_unrefl, A_refl) over the post-drift steps.

    A_unrefl is the free running sum of `err - e_pre - delta`; A_refl is the same sum reflected at
    zero, i.e. the StrictCUSUM statistic. Both are float64 arrays of the input length."""
    excess = np.asarray(err_post, dtype=np.float64) - e_pre - delta
    a_unrefl = np.cumsum(excess)
    a_refl = np.empty_like(excess)
    s = 0.0
    for t, e in enumerate(excess):
        s = max(0.0, s + e)
        a_refl[t] = s
    return a_unrefl, a_refl


def tau_erase(a_unrefl, tau_star, horizon=T_HORIZON):
    """argmax of A_unrefl on [tau_star, tau_star + horizon].

    The peak of the unreflected evidence: past it, the post-swap error has fallen back under
    e_pre + delta_P and every further step subtracts from the accumulation an external detector was
    building. NaN when tau_star is not finite (no swap ever fired)."""
    if not np.isfinite(tau_star):
        return np.nan
    lo = int(tau_star)
    hi = min(lo + int(horizon), a_unrefl.size)
    if hi <= lo:
        return np.nan
    return float(lo + int(np.argmax(a_unrefl[lo:hi])))


def error_budget(err_post, e_pre, delta_e_emp, tau_star, horizon=T_HORIZON):
    """(A, A_rect) -- the observed integrated excess and the rectangle R8's reasoning implies.

    A       = sum over [0, horizon) of (err - e_pre): the error budget the drift actually spends,
              with no delta_P tolerance subtracted -- this is a physical quantity, not a detector
              statistic.
    A_rect  = Delta_e_emp * tau_swap^(1/M): height x width, the rectangular proxy. F7 is the claim
              that this proxy misses; the ratio A / A_rect is what measures the miss."""
    n = min(int(horizon), len(err_post))
    a = float(np.sum(np.asarray(err_post[:n], dtype=np.float64) - e_pre))
    a_rect = float(delta_e_emp * tau_star) if np.isfinite(tau_star) else np.nan
    return a, a_rect


def empirical_delta_e(err_pre, err_post, window=ERR_WINDOW):
    """(e_pre, Delta_e_emp) -- the pre-drift error rate and the jump it takes at the drift.

    e_pre is the mean over the whole calibration warm-up (WARMUP steps, R1/R2 convention);
    Delta_e_emp is the mean over the first `window` post-drift steps minus e_pre. Reading the jump on
    a short post window and the baseline on a long pre window is deliberate: the baseline is
    stationary and wants precision, the jump is transient and wants promptness."""
    e_pre = float(np.mean(err_pre)) if len(err_pre) else np.nan
    n = min(int(window), len(err_post))
    e_post = float(np.mean(err_post[:n])) if n else np.nan
    return e_pre, e_post - e_pre


def demo():
    """Self-check: the invariants the test suite asserts on real traces, on constructed inputs."""
    err = np.concatenate([np.ones(30), np.zeros(970)])          # 30 post-drift steps in error
    e_pre, d_emp = empirical_delta_e(np.zeros(WARMUP), err, window=50)
    assert e_pre == 0.0 and abs(d_emp - 0.6) < 1e-12, (e_pre, d_emp)

    a_u, a_r = accumulations(err, e_pre)
    assert np.all(a_r >= a_u - 1e-12), "reflection invariant broken"
    assert a_u.argmax() == 29, a_u.argmax()                     # last step before the excess turns
    assert tau_erase(a_u, 0.0, horizon=1000) == 29.0

    # tree 0 replaced at steps 0 and 1 (Hydra: two swaps), tree 3 at step 2 -> 1, 1, 2 distinct
    trees = distinct_trees_cum([frozenset({0}), frozenset({0}), frozenset({3})])
    assert list(trees) == [1, 1, 2], list(trees)
    assert tau_swap(trees, 10, 0.1) == 0.0 and np.isnan(tau_swap(trees, 10, 0.5))

    a, a_rect = error_budget(err, e_pre, d_emp, tau_star=29.0, horizon=1000)
    assert a == 30.0 and abs(a_rect - 17.4) < 1e-12, (a, a_rect)

    # Recovery at rho=0.5: threshold 0.3, so the trailing W=10 window must hold <= 3 error steps,
    # first true at t=36; the run of H=5 completes at t=40.
    assert tau_err(err, e_pre, d_emp, rho=0.5, window=10, hysteresis=5) == 40.0
    assert np.isnan(tau_err(err, e_pre, 0.0, rho=0.5))

    m = rolling_mean([1, 2, 3, 4], 2)
    assert np.isnan(m[0]) and list(m[1:]) == [1.5, 2.5, 3.5], m
    print("s6_defs demo: OK")


if __name__ == "__main__":
    demo()
