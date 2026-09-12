# tests/test_S2_theory.py
"""Statutory guard-rail of stream S2, run before any hypothesis is declared destroyed.

Two input classes, per the S2 specification.

1. DEGENERATE. W = 0, W = 1, lambda = 0, Delta_e = delta_P (so mu = 0), sigma = 0, and both
   p_0 -> 0 and p_0 -> 1 in thm:floor. The expected behaviour at the two ends of p_0 is that the
   KL bound d(x||y) <= (x-y)^2/(y(1-y)) DIVERGES -- p_0(1-p_0) is its denominator -- so the floor
   becomes VACUOUS, not tighter. A test asserting the opposite sign would pass on a wrong premise.
   sigma is not an independent knob here: the per-step error variance of a Bernoulli stream is
   sigma^2 = p_0(1-p_0), so sigma = 0 is exactly the two endpoints already covered.

2. SPECIFIC MATRIX. W at powers of two; Delta_e approaching delta_P from above; lambda near mu W;
   and Delta_e >= 0.452, where S6 section 3 measures A/A_rect at -0.15 and -14.12 because the
   adapted ensemble ends the window BELOW its pre-drift error rate. Any bound assuming A > 0 is
   void there, and the artifact is asked to confirm the sign rather than the report.

Usage:  PYTHONHASHSEED=0 python -m pytest tests/test_S2_theory.py -v
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "S2_theory"))
from config import experiment_ssot as ssot  # noqa: E402
import s2_arl0 as s2  # noqa: E402

RUNS = ssot.RESULTS_DIR / "S6_synchronized_traces" / "data" / "runs.parquet"
DELTA_P = ssot.CUSUM_DELTA_P
POWERS_OF_TWO = [2.0 ** k for k in range(0, 12)]


def eq4(lam, w, mu, s0=0.0):
    """Eq. (4) -- the RHS of eq:markov_bound, W exp(-2/W (lambda - s_0 - mu W)_+^2)."""
    return w * np.exp(-2.0 / w * max(lam - s0 - mu * w, 0.0) ** 2)


# ── 1. Degenerate inputs ─────────────────────────────────────────────────────────────────────

def test_floor_is_vacuous_at_both_ends_of_p0():
    """p_0(1-p_0) sits in the DENOMINATOR of the KL bound, hence in the NUMERATOR of the floor."""
    alpha = 57.4 / s2.arl0(50.0, s2.cramer_root(s2.P_TRUE, s2.P_TRUE, DELTA_P), DELTA_P)
    f = {p: s2.detection_floor(p, 0.3268, 57.4, alpha) for p in (1e-12, 1e-6, 0.024, 0.5,
                                                                 1 - 1e-6, 1 - 1e-12)}
    assert f[1e-12] < 0 and f[1 - 1e-12] < 0, f          # vacuous: a non-positive lower bound
    assert f[0.5] > f[0.024] > f[1e-6], f                # maximal at the maximal variance
    assert abs(f[1e-6] - f[1 - 1e-6]) < 1e-9, f          # symmetric under p_0 <-> 1 - p_0
    assert f[1e-12] == pytest.approx(-57.4 * DELTA_P, rel=1e-6)   # collapses to -W delta_P


def test_floor_sigma_zero_is_the_same_degeneracy():
    """sigma^2 = p_0(1-p_0) on a Bernoulli error stream: sigma = 0 is not an independent input."""
    for p in (1e-12, 1 - 1e-12):
        assert p * (1.0 - p) == pytest.approx(0.0, abs=1e-11)
        assert s2.detection_floor(p, 0.3268, 57.4, 1e-9) < 0


def test_arl0_at_lambda_zero_and_monotonicity():
    th = s2.cramer_root(s2.P_TRUE, s2.P_TRUE, DELTA_P)
    assert s2.arl0(0.0, th, DELTA_P) == 0.0              # no threshold buys no false-alarm time
    lams = np.linspace(0.0, 60.0, 61)
    assert np.all(np.diff([s2.arl0(l, th, DELTA_P) for l in lams]) > 0)


def test_cramer_root_degenerate_base_rates():
    """p_true = 0: the reflected statistic never leaves zero, ARL_0 is infinite by construction.
    A non-negative null drift admits no positive Cramer root at all."""
    assert s2.cramer_root(0.0, 0.0, DELTA_P) == np.inf
    assert s2.arl0(15.0, np.inf, DELTA_P) == np.inf
    with pytest.raises(ValueError):
        s2.cramer_root(0.5, 0.1, DELTA_P)                # drift +0.39 per step under the null


def test_starve_boundary_degenerate_windows():
    """W = 0 leaves s_0 alone; mu = 0 leaves the fluctuation margin alone; W = 1 is finite."""
    assert s2.lambda_starve(0.0, 0.3168) == 0.0
    assert s2.lambda_starve(0.0, 0.3168, s0=7.0) == 7.0
    assert s2.lambda_starve(1.0, 0.0) == pytest.approx(np.sqrt(0.5 * np.log(1.0 / ssot.EPS_MISS)))
    assert np.isfinite(s2.lambda_starve(1.0, 0.3168))


def test_mu_zero_when_delta_e_equals_the_tolerance():
    """Delta_e = delta_P kills the drift term: the boundary is pure fluctuation margin."""
    mu = DELTA_P - DELTA_P
    for w in POWERS_OF_TWO:
        assert s2.lambda_starve(w, mu) == pytest.approx(
            np.sqrt(w / 2.0 * np.log(w / ssot.EPS_MISS)))


# ── 2. Specific matrix ───────────────────────────────────────────────────────────────────────

def test_lambda_starve_is_increasing_in_w_at_powers_of_two():
    for mu in (0.0, 1e-6, 0.09, 0.3168, 0.488):
        v = s2.lambda_starve(np.array(POWERS_OF_TWO), mu)
        assert np.all(np.diff(v) > 0), (mu, v)


def test_delta_e_approaching_the_tolerance_from_above():
    """As Delta_e -> delta_P+, mu -> 0+ and lambda_starve descends continuously to the pure
    margin. No discontinuity, and no sign flip."""
    w = 57.4
    margin = s2.lambda_starve(w, 0.0)
    prev = np.inf
    for d in (1e-1, 1e-2, 1e-3, 1e-6, 1e-9, 1e-12):
        mu = (DELTA_P + d) - DELTA_P
        v = s2.lambda_starve(w, mu)
        assert margin < v < prev
        prev = v
    assert prev == pytest.approx(margin, rel=1e-9)


def test_eq4_vacancy_boundary_is_exactly_mu_w_equals_lambda():
    """Eq. (4) returns at least 1 -- a vacuous bound on a probability -- exactly when mu W >= lambda."""
    for w in POWERS_OF_TWO:
        for mu in (0.09, 0.3168, 0.488):
            lam = mu * w
            assert eq4(lam / 2.0, w, mu) == w            # below the boundary: positive part zero
            assert eq4(lam, w, mu) == w                  # at it: still exactly W >= 1
            assert eq4(lam + 4.0, w, mu) < w             # above it: strictly informative
    assert eq4(15.0, 611.9, 0.3168) >= 1.0               # tau_erase, canonical point: vacant
    assert eq4(50.0, 57.4, 0.3168) < 1.0                 # tau_swap^(1/M), same point: informative


def test_lambda_near_mu_w_is_continuous_and_bounded_by_w():
    w, mu = 57.4, 0.3168
    for eps in (1e-12, 1e-9, 1e-6, 1e-3):
        assert eq4(mu * w + eps, w, mu) == pytest.approx(w, rel=1e-3)
        assert eq4(mu * w - eps, w, mu) == pytest.approx(w, rel=1e-3)
    assert all(eq4(lam, w, mu) <= w for lam in np.linspace(0.0, 100.0, 201))


def test_budget_is_negative_above_delta_e_0p452_so_positive_budget_bounds_are_void():
    """S6 section 3: the adapted ensemble ends the window BELOW its pre-drift rate at the top of
    the grid, so A = sum(e_t - p_0) is negative and every bound assuming A > 0 is void there."""
    if not RUNS.exists():
        pytest.skip(f"{RUNS} absent -- run s6_runner.py full")
    f = pd.read_parquet(RUNS, columns=["arm", "delta_e", "e_pre", "err_post_mean", "a"])
    f = f[f.arm == "full"]
    top = f[f.delta_e >= 0.452].groupby("delta_e")[["e_pre", "err_post_mean"]].mean()
    assert (top.err_post_mean < top.e_pre).all(), top
    assert f[f.delta_e >= 0.452]["a"].median() <= f[f.delta_e < 0.452]["a"].median()
    # thm:floor is a lower bound on A; where A <= 0 and the floor is positive, the comparison is
    # void rather than violated, and must be declared so.
    alpha = 57.4 / s2.arl0(50.0, s2.cramer_root(s2.P_TRUE, s2.P_TRUE, DELTA_P), DELTA_P)
    assert s2.detection_floor(s2.P_TRUE, 0.498, 57.4, alpha) > 0.0


def test_transfer_S1_column_reproduces_under_R1a():
    """Decision rule R1(a). The 0.005 / p_0 = 0.05 pair certifies the solver; certification failing
    is an infrastructure fault, not a finding."""
    for (delta, p), claim in s2.TRANSFER_S1_CLAIM.items():
        theta = s2.cramer_root(p, p, delta)
        assert abs(theta - claim["theta"]) / claim["theta"] <= s2.R1_THETA_TOL, (delta, p, theta)
        for lam, v in claim["arl0"].items():
            assert s2._same_sig_fig(s2.arl0(lam, theta, delta), v), (delta, p, lam)
