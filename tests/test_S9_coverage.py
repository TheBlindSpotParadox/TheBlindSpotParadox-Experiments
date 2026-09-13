# tests/test_S9_coverage.py
"""
Stream S9 detector-coverage guard -- one runnable check per piece of non-trivial logic the stream
introduces, and no more.

1. The requirement lattice. `eq:Rkswin` is re-derived here and checked against BOTH the committed
   numeral it must reproduce (`s2bis_proteus_gate.json :: R_KSWIN_at_deployed_alpha`, the same
   expression as `s2_arl0.py:387` and `s2bis_proteus_calibration.py:344`) and the exact two-sample
   lattice of `docs/prompts/s9-decision-rules.md` A.3. The pre-registered row at `n_stat = 30` is
   `k* = (11, 13, 14, 15)`; if scipy or River ever moves, this fails rather than the stream
   silently publishing a different table.
2. The guard slackness that the offline alarm derivation depends on. River fires on
   `p_value <= alpha` AND `st > 0.1`. `s9_offline_detectors` derives alarms from the p-value alone,
   which is valid only while the second conjunct is slack at every declared cell. That precondition
   is asserted, never assumed.
3. The alarm senses. KSWIN's is inverted and ADWIN publishes no scalar test quantity; both are
   contract, and a later "harmonisation" of either is an editorial act on a measurement.
4. First crossing against a LIVE re-armed `drift.KSWIN`. This is the regression guard for the trap
   that `KSWIN._reset()` leaves `p_value = 0` until the window fills: River never reads the
   attribute before its own `len(window) >= window_size` branch, so an offline reading that does
   alarms at t = 0 at every alpha. Measured once at a 100 % spurious pre-drift rate; this test is
   what keeps it measured.
5. Bit-identical replay. KSWIN is the one stochastic detector in the pass; its reservoir seed is
   derived per cell by `SeedSequence` and never from global state, so two replays of one cell must
   agree exactly.

Usage:  PYTHONHASHSEED=0 python -m pytest tests/test_S9_coverage.py -v
"""
import json
import sys
from pathlib import Path

import numpy as np
import pytest
from river import drift

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "S6_synchronized_traces"))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "S6_synchronized_traces" / "gates"))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "S9_detector_coverage"))
from config import experiment_ssot as ssot  # noqa: E402

import s9_offline_detectors as off  # noqa: E402
from s6_detectors import ADWINDetector, KSWINDetector, PHT  # noqa: E402

GATE_JSON = ssot.RESULTS_DIR / "S2bis_calibration" / "tables" / "s2bis_proteus_gate.json"

# The A.3 table, committed in docs/prompts/s9-decision-rules.md BEFORE any measurement.
PREREGISTERED_K_STAR = {0.05: 11, 0.01: 13, 0.005: 14, 0.001: 15}


def _stream(n=2600, p0=0.024, jump=0.30, seed=11):
    """A pre-drift Bernoulli(p0) window followed by an elevated one -- the canonical family's shape,
    built here rather than read, so the guard is green on a fresh clone."""
    rng = np.random.default_rng(seed)
    pre, post = 1000, n - 1000
    err = np.concatenate([rng.random(pre) < p0, rng.random(post) < p0 + jump]).astype(np.float64)
    return err, np.arange(-pre, post, dtype=np.int32)


# ══════════════════════════════════════════════════════════════════════════════
# 1-2. the requirement lattice and the guard it rests on
# ══════════════════════════════════════════════════════════════════════════════
def test_eq_Rkswin_reproduces_the_committed_requirement_numeral():
    """Identity against s2_arl0.py:387 / s2bis_proteus_calibration.py:344, not a re-derivation."""
    gate = json.loads(GATE_JSON.read_text(encoding="utf-8"))["family_requirements_at_lambda_eq"]
    at = gate["at"]
    assert (at["W"], at["n_stat"], at["eps"]) == (ssot.S9_W_TRANSIENT_REF, ssot.S9_KSWIN_STAT,
                                                  ssot.S9_EPS), "the S9 anchor left the artifact"
    margin = np.sqrt(at["W"] / 2.0 * np.log(1.0 / at["eps"]))
    r = np.sqrt(at["n_stat"] * np.log(2.0 / 0.005)) + margin
    assert abs(margin - gate["epsilon_margin"]) < 1e-12, (margin, gate["epsilon_margin"])
    assert abs(r - gate["R_KSWIN_at_deployed_alpha"]) < 1e-12, (r, gate["R_KSWIN_at_deployed_alpha"])


def test_exact_lattice_matches_the_preregistered_A3_table():
    lat = off.requirement_lattice()
    row = {c["alpha"]: c for c in lat["grid"] if c["n_stat"] == ssot.S9_KSWIN_STAT}
    assert set(row) == set(PREREGISTERED_K_STAR), sorted(row)
    for alpha, k in PREREGISTERED_K_STAR.items():
        assert row[alpha]["k_star"] == k, (alpha, row[alpha]["k_star"], k)
        assert row[alpha]["scipy_method"] == "exact", (alpha, row[alpha]["scipy_method"])
    # The pre-registration also predicted the SIGN of the deviation: anti-conservative at three of
    # the four levels, conservative at the fourth. Only the fourth is asserted here, because it is
    # the one the 0.5-lattice-step tolerance of rule D1 cannot absorb in either direction.
    assert row[0.001]["R_fa_asymptotic"] > row[0.001]["R_fa_exact"], row[0.001]
    assert row[0.05]["R_fa_asymptotic"] < row[0.05]["R_fa_exact"], row[0.05]


def test_the_st_guard_is_slack_at_every_declared_cell():
    """`alarm_lattice` raises when it is not; the offline p-value-only alarm rule depends on it."""
    pv, k_guard = off.alarm_lattice()
    assert k_guard == int(np.floor(ssot.S9_KSWIN_ST_FLOOR * ssot.S9_KSWIN_STAT)) + 1
    for alpha in ssot.S9_KSWIN_ALPHA_GRID:
        k_star = int(np.flatnonzero(pv <= alpha)[0])
        assert k_star > ssot.S9_KSWIN_ST_FLOOR * ssot.S9_KSWIN_STAT, (alpha, k_star)


# ══════════════════════════════════════════════════════════════════════════════
# 3. the alarm senses are contract
# ══════════════════════════════════════════════════════════════════════════════
def test_alarm_senses_are_carried_not_recoded():
    ks = KSWINDetector(alpha=0.005, seed=1, window_size=ssot.S9_KSWIN_WINDOW,
                       stat_size=ssot.S9_KSWIN_STAT)
    assert ks.alarm_sense == "below" and ks.threshold == 0.005
    for x in np.r_[np.zeros(150), np.ones(60)]:
        ks.update(float(x))
    assert 0.0 <= ks.statistic() <= 1.0, ks.statistic()
    ad = ADWINDetector(delta=ssot.S9_ADWIN_DELTA, clock=ssot.S9_ADWIN_CLOCK)
    assert ad.threshold is None and ad.alarm_sense is None, "ADWIN was given a scalar it has not got"
    assert PHT(threshold=ssot.S9_OFFLINE_LAMBDAS[-1]).alarm_sense == "above"


# ══════════════════════════════════════════════════════════════════════════════
# 4. the offline reading against a live re-armed detector
# ══════════════════════════════════════════════════════════════════════════════
@pytest.mark.parametrize("input_arm", list(ssot.S9_INPUT_ARMS))
def test_offline_first_crossing_matches_a_live_rearmed_kswin(input_arm):
    err, t_rel = _stream()
    pv, _ = off.alarm_lattice()
    _, scal = off.replay(err, t_rel, 0.25, off.ARMS[0], 7, input_arm, pv)

    crossings = [scal[f"kswin_t_first_alpha{a:g}"] for a in ssot.S9_KSWIN_ALPHA_GRID]
    assert any(c is not None for c in crossings), (
        f"no crossing at any alpha on the {input_arm} arm -- the comparison below would hold "
        f"vacuously. Either the stream stopped exercising KSWIN or KSWIN stopped firing.")

    values, first = off._input_stream(err, input_arm)
    safe_seed = off.cell_seed(0.25, off.ARMS[0], 7, input_arm) % (2 ** 31 - 1)
    for alpha in ssot.S9_KSWIN_ALPHA_GRID:
        live = drift.KSWIN(alpha=alpha, window_size=ssot.S9_KSWIN_WINDOW,
                           stat_size=ssot.S9_KSWIN_STAT, seed=safe_seed)
        hit = None
        for j, x in enumerate(values):
            live.update(float(x))
            if live.drift_detected:
                hit = int(t_rel[j + first])
                break
        assert scal[f"kswin_t_first_alpha{alpha:g}"] == hit, (input_arm, alpha, hit)


# ══════════════════════════════════════════════════════════════════════════════
# 5. determinism
# ══════════════════════════════════════════════════════════════════════════════
def test_replay_of_one_cell_is_bit_identical():
    err, t_rel = _stream(n=1400)
    pv, _ = off.alarm_lattice()
    a, sa = off.replay(err, t_rel, 0.25, off.ARMS[0], 3, "smoothed", pv)
    b, sb = off.replay(err, t_rel, 0.25, off.ARMS[0], 3, "smoothed", pv)
    assert sa == sb
    for k in a:
        assert np.array_equal(a[k], b[k], equal_nan=np.issubdtype(a[k].dtype, np.floating)), k
    # and a different cell must NOT collide: the seed is derived per cell, not shared
    c, _ = off.replay(err, t_rel, 0.25, off.ARMS[0], 4, "smoothed", pv)
    assert not np.array_equal(a["kswin_p"], c["kswin_p"], equal_nan=True)
