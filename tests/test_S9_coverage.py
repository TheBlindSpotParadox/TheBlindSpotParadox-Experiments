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


# ══════════════════════════════════════════════════════════════════════════════
# 6. T9.2 -- the two competing models are the committed formulas, not paraphrases
# ══════════════════════════════════════════════════════════════════════════════
import s9_kswin_dilution as dil  # noqa: E402
import s9_input_space as isp  # noqa: E402


def test_t92_model_predicates_are_the_committed_formulas():
    """B1 is `A >= R_KSWIN` of eq:Rkswin; the contrast model is `min(W, n_stat) Delta_e >= k*`."""
    n_stat, alpha, w, de = 30, 0.005, 20, 0.9
    k = PREREGISTERED_K_STAR[alpha]
    b1, ctr, A, R = dil.predictions(de, w, n_stat, alpha, k)
    assert A == pytest.approx((de - ssot.DELTA_P) * w)
    assert R == pytest.approx(np.sqrt(n_stat * np.log(2 / alpha))
                              + np.sqrt(w / 2 * np.log(1 / ssot.S9_EPS)))
    assert b1 is (A >= R) and ctr is (min(w, n_stat) * de >= k)
    # and the two models must actually disagree somewhere on the declared grid, or T9.2 compares
    # one model with itself
    kstar = {(n, a): PREREGISTERED_K_STAR[a] for n in ssot.S9_NSTAT_GRID
             for a in ssot.S9_KSWIN_ALPHA_GRID}
    kstar.update({(n, a): dil.k_star_table()[(n, a)] for n in ssot.S9_NSTAT_GRID
                  for a in ssot.S9_KSWIN_ALPHA_GRID})
    disagree = sum(dil.predictions(d, w2, n2, a2, kstar[(n2, a2)])[0]
                   != dil.predictions(d, w2, n2, a2, kstar[(n2, a2)])[1]
                   for d in ssot.S9_T92_DELTA_E_GRID for w2 in ssot.S9_T92_W_GRID
                   for n2 in ssot.S9_NSTAT_GRID for a2 in ssot.S9_KSWIN_ALPHA_GRID)
    assert disagree > 0, "B1 and the contrast model agree on every cell of the declared grid"


def test_t92_grid_reaches_the_region_D3_is_decided_on():
    """The B2 region -- W < n_stat AND A >= R_KSWIN -- must be non-empty, or D3 is NOT PRODUCED by
    construction and the grid proves nothing. This is why the magnitude axis runs past 0.498."""
    kstar = dil.k_star_table()
    reachable = [(d, w, n, a) for d in ssot.S9_T92_DELTA_E_GRID for w in ssot.S9_T92_W_GRID
                 for n in ssot.S9_NSTAT_GRID for a in ssot.S9_KSWIN_ALPHA_GRID
                 if w < n and dil.predictions(d, w, n, a, kstar[(n, a)])[2]
                 >= dil.predictions(d, w, n, a, kstar[(n, a)])[3]]
    assert reachable, "the declared grid contains no cell of the B2 region"
    assert min(d for d, _, _, _ in reachable) > 0.498, (
        "if the B2 region were reachable inside the canonical magnitude range, extending the grid "
        "past it would need a different justification than the one declared")


# ══════════════════════════════════════════════════════════════════════════════
# 7. T9.3 -- the instrument, before any null it reports
# ══════════════════════════════════════════════════════════════════════════════
def test_hellinger_distance_hits_both_endpoints():
    rng = np.random.default_rng(0)
    a = rng.normal(size=(400, 2))
    assert isp.hellinger(a, a) == pytest.approx(0.0, abs=1e-12)
    # disjoint supports: every bin of one is empty in the other, so the distance is sqrt(2)
    assert isp.hellinger(a, a + 1e6) == pytest.approx(np.sqrt(2.0), abs=1e-9)


def test_hdddm_finds_a_covariate_shift_it_must_find():
    """The positive control, as an assertion. A null from an instrument nobody checked is not a
    measurement, and T9.3's whole result is a null."""
    c = isp.positive_control(shifts=[ssot.S9_HDDDM_CONTROL_SHIFTS[-1]], n_seeds=8)
    assert c["verdict"] == "SENSITIVE", c
    assert c["detection_rate"] >= ssot.S9_HDDDM_CONTROL_GATE, c


def test_hdddm_is_blind_to_a_boundary_rotation_at_fixed_PX():
    """The same detector, same size of change in the LABELS, no change in P(X): output identical."""
    import s8_rotation as rot
    seed = 12345
    h_lo, _ = isp.hdddm(rot.make_rotation_stream(seed, 0.05, ssot.S9_HDDDM_ETA)[1])
    h_hi, _ = isp.hdddm(rot.make_rotation_stream(seed, 0.45, ssot.S9_HDDDM_ETA)[1])
    assert np.array_equal(np.nan_to_num(h_lo, nan=-1.0), np.nan_to_num(h_hi, nan=-1.0)), (
        "the HDDDM trace moved with Delta_e; P(X) is supposed to be invariant under this generator")


def test_cluster_bootstrap_does_not_understate_the_interval():
    """The design effect, as a guard. Rows within a seed share one X; resampling rows instead of
    seeds is what turned a null correlation into an interval excluding zero."""
    rng = np.random.default_rng(3)
    n_clusters, per = 40, 20
    cluster = np.repeat(np.arange(n_clusters), per)
    # Both quantities carry their information at the CLUSTER level, which is the shape of the real
    # data: peak_excess is constant within a seed and tau_erase's cluster mean is what any
    # correlation with it can see. Effective n is 40, not 800.
    a = np.repeat(rng.normal(size=n_clusters), per)
    b = np.repeat(rng.normal(size=n_clusters), per) + 0.3 * rng.normal(size=n_clusters * per)
    wide = isp.spearman_ci(a, b, cluster, n_boot=2000)
    narrow = isp.spearman_ci(a, b, np.arange(a.size), n_boot=2000)   # one row per "cluster"
    ratio = (wide["ci_hi"] - wide["ci_lo"]) / (narrow["ci_hi"] - narrow["ci_lo"])
    assert ratio > 3.0, (f"design effect not integrated: cluster/row CI width ratio {ratio:.2f}, "
                         f"sqrt(deff) = sqrt({per}) = {per ** 0.5:.2f} expected", wide, narrow)


# ══════════════════════════════════════════════════════════════════════════════
# 8. D6 -- the ProteuS null, established on the generator rather than asserted
# ══════════════════════════════════════════════════════════════════════════════
def test_proteus_pre_drift_label_is_constant_zero_by_construction():
    """`regime = 1[f_t > 0.5]` with `f_t = expit(4(t - tp)/w)` is identically 0 for every t < tp, on
    every transition and every regime. With `run_concept_drift`'s `y_pred = predict_one(x) or 0`
    predicting that constant from the first step, the pre-drift error is exactly zero and no
    false-alarm budget constrains any threshold on this stream.

    This is D6's "establish formally on the generator": it is a property of `simulate_stream`, read
    off the generator with no classifier and no campaign, and it is what makes every false-alarm
    statement measured on ProteuS void -- including the alpha sweep of `.tex:500`."""
    sys.path.insert(0, str(ROOT_DIR / "experiments" / "R4_proteus_evaluation"))
    import exp_R4_main_table as r4

    checked = 0
    for from_t, to_t, w, _ in r4.TRANSITIONS:
        for regime in ("IID", "GARCH"):
            df, tps = r4.simulate_stream(r4.ETF_PARAMS_A[from_t], r4.ETF_PARAMS_B[to_t],
                                         regime, w)
            tp = tps[0]
            pre = df["regime"].to_numpy()[:tp]
            assert pre.max() == 0, (from_t, to_t, regime, int(pre.max()))
            assert df["regime"].to_numpy()[tp:].max() == 1, (from_t, to_t, regime)
            checked += 1
    assert checked == len(r4.TRANSITIONS) * 2, checked


# ══════════════════════════════════════════════════════════════════════════════
# 9. the transfer payloads resolve, and none lands in an excluded subsection
# ══════════════════════════════════════════════════════════════════════════════
import re  # noqa: E402

TRANSFER = ROOT_DIR / "docs" / "theory" / "transfer_S9.md"
EXCLUDED = {"sec:race", "sec:hydra", "sec:starvation", "sec:decoupling"}
PAYLOAD_RE = re.compile(r"~{9}\n(?P<f>[^\n]+)\n<<<<<<< SEARCH\n(?P<s>.*?)\n=======\n"
                        r"(?P<r>.*?)\n>>>>>>> REPLACE\n~{9}", re.S)


def _payloads():
    if not TRANSFER.exists():
        pytest.skip("transfer_S9.md absent")
    return PAYLOAD_RE.findall(TRANSFER.read_text(encoding="utf-8"))


def test_transfer_S9_anchors_resolve_exactly_once():
    """An anchor that matches twice patches the wrong site; one that matches zero times is lost at
    assembly. Both are silent failures at apply time, so they fail here instead."""
    payloads = _payloads()
    assert len(payloads) >= 8, f"only {len(payloads)} payloads parsed -- the fence shape changed"
    for f, search, _ in payloads:
        target = ROOT_DIR / f
        assert target.exists(), f
        assert target.read_text(encoding="utf-8").count(search) == 1, (
            f, search.splitlines()[0][:80])


def test_transfer_S9_payloads_avoid_the_excluded_subsections():
    """`CLAUDE.md` forbids patching the four superseded subsections of the live manuscript. Checked
    by character offset against the real subsection boundaries, not by line number or by eye."""
    live = ROOT_DIR / "docs" / "manuscript" / "articleA_blindspot_v64_camera_ready.tex"
    text = live.read_text(encoding="utf-8")
    subs = [(m.start(), m.group(1))
            for m in re.finditer(r"\\subsection\{[^}]*\}\\label\{(sec:[^}]+)\}", text)]
    zones = [(lab, pos, subs[i + 1][0] if i + 1 < len(subs) else len(text))
             for i, (pos, lab) in enumerate(subs) if lab in EXCLUDED]
    assert len(zones) == len(EXCLUDED), [z[0] for z in zones]
    for f, search, _ in _payloads():
        if not f.endswith("articleA_blindspot_v64_camera_ready.tex"):
            continue
        off = text.find(search)
        inside = [lab for lab, a, b in zones if a <= off < b]
        assert not inside, (f, off, inside, search.splitlines()[0][:80])
