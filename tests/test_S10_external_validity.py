# tests/test_S10_external_validity.py
"""
Stream S10 guard -- one runnable check per piece of non-trivial logic the stream introduces.

1. The lagged proxy is neutral. `LaggedARF` makes extra `predict_one` calls on future covariates;
   gate G0 says `predict_one` consumes no entropy, and this keeps it measured on the proxy itself:
   errors, replacement chronology and all three generator digests must be identical with and
   without it.
2. Look-ahead IS a learner whose labels arrive late. The whole of rule L2-L4 under shared latency
   rests on the identity `e^(l)_t = 1[S_{t-l}(x_t) != y_t]`, computed by scoring x[t + l] with the
   current state. It is checked against a second forest that really waits: fed through a FIFO,
   learning `x_{t-l}` after predicting `x_t` (docs/theory/S10_decision_rules.md A.2).
3. Monitor-only latency is a pure shift. Under M1 the budget read before erasure and the rate of
   detection within the deadline are non-increasing in `l` by construction; the analysis asserts it
   and this test pins it on a constructed stream.
4. The design effect is integrated. A seed's twenty magnitudes share one feature stream, so an
   interval resampling runs instead of seeds understates its width.

Every model is built right after `common.lock_rng`: River's Cython tree-spawn path reads the global
generators, and two forests run back to back without re-locking would differ for a reason unrelated
to the property under test.

Usage:  PYTHONHASHSEED=0 python -m pytest tests/test_S10_external_validity.py -v
"""
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "S6_synchronized_traces"))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "S6_synchronized_traces" / "gates"))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "S10_external_validity"))
from config import experiment_ssot as ssot  # noqa: E402

import _gate_common as common  # noqa: E402
import s6_runner as runner  # noqa: E402
import s10_latency as lat  # noqa: E402

DEMO_DELTA_E = ssot.S6_GATE_DELTA_E[1]          # 0.25, a Phase-0 gate anchor


def _fresh(seed):
    """(x, y, forest) under a fresh triple lock -- the order s6_runner.simulate uses."""
    safe, x, y = runner.make_stream(seed, DEMO_DELTA_E)
    return x, y, common.make_arf(safe, ssot.S6_N_MODELS, ssot.S6_C_INT)


# ══════════════════════════════════════════════════════════════════════════════
# 1-2. the lagged proxy
# ══════════════════════════════════════════════════════════════════════════════
def test_lagged_proxy_leaves_the_trunk_bit_identical():
    seed, n = common.seed_pool(1)[0], 1500
    x, y, plain = _fresh(seed)
    ref, _ = runner.segment(plain, x, y, 0, n)
    digests = common.rng_digests(plain)

    x, y, arf = _fresh(seed)
    proxy = lat.LaggedARF(arf, x, y, [0, 10, 50], first=0)
    got, _ = runner.segment(proxy, x, y, 0, n)

    for key in ("err", "swap_delta", "n_nodes_mean", "n_active_leaves_mean"):
        assert np.array_equal(ref[key], got[key]), key
    assert ref["replaced"] == got["replaced"]
    assert common.rng_digests(arf) == digests, "the look-ahead predictions consumed entropy"
    assert proxy.t == n
    assert np.array_equal(proxy.err[0, :n], got["err"]), "row 0 is not the trunk's error column"


@pytest.mark.parametrize("lag", [10, 50])
def test_lookahead_equals_a_learner_whose_labels_arrive_late(lag):
    seed, n = common.seed_pool(1)[0], 1200
    x, y, arf = _fresh(seed)
    proxy = lat.LaggedARF(arf, x, y, [0, lag], first=0)
    runner.segment(proxy, x, y, 0, n, observe=False, track=False)

    x, y, late = _fresh(seed)
    err = np.zeros(n, dtype=np.int8)
    for t in range(n):
        p = late.predict_one({0: x[t, 0], 1: x[t, 1]})          # test ...
        err[t] = int((p if p is not None else 0) != y[t])
        if t >= lag:                                            # ... then train on the label
            late.learn_one({0: x[t - lag, 0], 1: x[t - lag, 1]}, int(y[t - lag]))   # that arrives
    assert np.array_equal(proxy.err[1, lag:n], err[lag:n])


# ══════════════════════════════════════════════════════════════════════════════
# 3. monitor-only latency
# ══════════════════════════════════════════════════════════════════════════════
def _transient(seed=11, jump=0.35, length=800):
    """A pre-drift window without error, then an excess decaying linearly to zero over `length`
    post-drift steps -- the shape erasure leaves, built here so the guard is green on a fresh
    clone."""
    rng = np.random.default_rng(seed)
    pre, post = ssot.S10_WARMUP_WINDOW, ssot.S10_TRACE_POST
    k = np.arange(post)
    p = np.concatenate([np.zeros(pre), jump * np.clip(1.0 - k / length, 0.0, None)])
    return (rng.random(pre + post) < p).astype(np.int8), np.arange(-pre, post, dtype=np.int32)


def test_monitor_only_latency_is_a_pure_shift():
    err, t_rel = _transient()
    q = lat.lag_quantities(err, t_rel, tau_swap=0.0)
    assert np.isfinite(q["T"]) and q["T"] > max(ssot.S10_LAGS), q["T"]
    budgets = [lat.budget_read(q, lag) for lag in ssot.S10_LAGS]
    assert budgets[0] == pytest.approx(q["a"]) and budgets[0] > 0
    assert all(b1 <= b0 + 1e-9 for b0, b1 in zip(budgets, budgets[1:])), budgets
    for lam in ssot.S10_LAMBDAS:
        det = [lat.detected_within(q["d"][lam], lag, q["T"]) for lag in ssot.S10_LAGS]
        assert all(b <= a for a, b in zip(det, det[1:])), (lam, det)
    # a crossing is classified by the datum that caused it, never by the wall clock
    assert not lat.detected_within(-5, 500, q["T"])
    assert lat.budget_read(q, int(q["T"]) + 1) == 0.0


# ══════════════════════════════════════════════════════════════════════════════
# 4. the design effect
# ══════════════════════════════════════════════════════════════════════════════
def test_cluster_bootstrap_does_not_understate_the_interval():
    rng = np.random.default_rng(3)
    n_clusters, per = 40, 20
    values = np.repeat(rng.normal(size=n_clusters), per) + 0.1 * rng.normal(size=n_clusters * per)
    clusters = np.repeat(np.arange(n_clusters), per)
    lo_c, hi_c = lat.cluster_median_ci(values, clusters, n_boot=2000)
    lo_r, hi_r = lat.cluster_median_ci(values, np.arange(values.size), n_boot=2000)
    assert (hi_c - lo_c) > 3.0 * (hi_r - lo_r), ((lo_c, hi_c), (lo_r, hi_r))


# ══════════════════════════════════════════════════════════════════════════════
# 5. T10.2 -- the admissible window and the placement of a published failure
# ══════════════════════════════════════════════════════════════════════════════
import s10_dual_mode as dual  # noqa: E402


def test_admissible_window_handles_contiguous_empty_and_silent_cases():
    lams = [1.0, 2.0, 5.0, 10.0, 50.0]
    # flooding at low lambda, starvation at high lambda, admissible in between
    assert dual.admissible(lams, [1.0, 1.0, 0.97, 0.96, 0.10], [0.01, 0.2, 0.6, 0.9, None]) == \
        {"lo": 5.0, "hi": 10.0, "contiguous": True}
    # no alarm at all: precision undefined, counted as satisfied -- silence is not flooding
    assert dual.admissible([5.0], [0.99], [None]) == {"lo": 5.0, "hi": 5.0, "contiguous": True}
    # the two cliffs overlap: no threshold is admissible
    assert dual.admissible(lams, [1.0, 1.0, 0.9, 0.5, 0.0], [0.1, 0.2, 0.4, 0.9, None]) is None
    # a dip inside the window is reported, not smoothed over
    assert dual.admissible(lams, [1.0, 0.99, 0.90, 0.97, 0.0],
                           [0.9, 0.9, 0.9, 0.9, None])["contiguous"] is False
    # drawn at grid resolution: a one-point window spans the geometric midpoints with its neighbours
    assert dual.grid_extent([1.0, 4.0, 16.0], {"lo": 4.0, "hi": 4.0}) == pytest.approx((2.0, 8.0))
    assert dual.grid_extent([1.0, 4.0, 16.0], {"lo": 1.0, "hi": 16.0}) == pytest.approx((1.0, 16.0))


def test_a_published_failure_must_fail_by_its_own_criterion_only():
    assert dual.failure_verdict("starvation", 0.0, None) == "HOLDS"
    assert dual.failure_verdict("flooding", 1.0, 0.01) == "HOLDS"
    assert dual.failure_verdict("flooding", 0.5, 0.01) == "DOUBLE"
    assert dual.failure_verdict("starvation", 0.99, 0.9) == "FAILS"
    assert dual.failure_verdict("flooding", 0.99, 0.9) == "FAILS"


# ══════════════════════════════════════════════════════════════════════════════
# 6. T10.3 -- the identity rule P0-1 declares rather than measures
# ══════════════════════════════════════════════════════════════════════════════
def test_adwin_and_pht_arf_pipelines_monitor_the_same_classifier():
    """p0 is measured for pht_arf_c1 and declared identical for adwin_arf_c1: build_model reads only
    the '_ht' suffix and 'c32', so both build the same ARF(c = 1). Pinned here, including the nested
    drift and warning detectors, so a future pipeline name cannot silently break the declaration."""
    sys.path.insert(0, str(ROOT_DIR / "experiments" / "R5_real_world_evaluation"))
    import exp_R5_common as r5
    for seed in (7, 8):
        assert (r5.build_model("adwin_arf_c1", seed)._get_params()
                == r5.build_model("pht_arf_c1", seed)._get_params())


# ══════════════════════════════════════════════════════════════════════════════
# 7. T10.4 -- Holm, by hand and against the verdict protocol_v2 already states
# ══════════════════════════════════════════════════════════════════════════════
import s10_holm as holm_mod  # noqa: E402


def test_holm_step_down_matches_a_hand_computed_case():
    retained, adjusted = holm_mod.holm([0.01, 0.04, 0.03, 0.005], alpha=0.05)
    assert list(retained) == [True, False, False, True]
    assert np.allclose(adjusted, [0.03, 0.06, 0.06, 0.02])


def test_the_declared_ten_reproduce_the_protocol_verdict():
    """protocol_v2.tex section Multiplicity: eight at the 2^-29 floor retained, abrupt_balanced
    compared against alpha / 2 and not retained, the degenerate alpha-sweep contrast not retained."""
    fam = holm_mod.apply(holm_mod.declared_members())
    kept = {r["member"]: r["retained"] for r in fam["members"]}
    assert fam["m"] == 10 and sum(kept.values()) == 8
    assert not kept["R5-abrupt_balanced"] and not kept["R4-alpha"]
    abrupt = next(r for r in fam["members"] if r["member"] == "R5-abrupt_balanced")
    assert abrupt["threshold"] == pytest.approx(0.05 / 2)


# ══════════════════════════════════════════════════════════════════════════════
# 8. the perimeter, and the transfer payloads
# ══════════════════════════════════════════════════════════════════════════════
import re  # noqa: E402

TRANSFER = ROOT_DIR / "docs" / "theory" / "S10_transfer.md"
EXCLUDED = {"sec:race", "sec:hydra", "sec:starvation", "sec:decoupling"}
MANUSCRIPT_DIR = ROOT_DIR / "docs" / "manuscript"
ARCHIVED_V64 = "articleA_blindspot_v64_camera_ready.tex"
PAYLOAD_RE = re.compile(r"~{9}\n(?P<f>[^\n]+)\n<<<<<<< SEARCH\n(?P<s>.*?)\n=======\n"
                        r"(?P<r>.*?)\n>>>>>>> REPLACE\n~{9}", re.S)


def test_s10_writes_only_inside_its_perimeter():
    """PROMPT_S10: no write under results/S6_*, S8_*, S9_*, R*_*, and no new authorized deviation."""
    tables = ssot.RESULTS_DIR / "S10_external_validity" / "tables"
    if tables.exists():
        unprefixed = [p.name for p in tables.iterdir() if p.is_file() and not p.name.startswith("s10_")]
        assert not unprefixed, unprefixed
    foreign = [str(p.relative_to(ssot.RESULTS_DIR)) for pattern in ("S6_*", "S8_*", "S9_*", "R*_*")
               for p in ssot.RESULTS_DIR.glob(f"{pattern}/**/*s10_*")]
    assert not foreign, foreign
    ledger = ssot.RESULTS_DIR / "audit_S7" / "_baseline" / "authorized_deviations.txt"
    assert "S10" not in ledger.read_text(encoding="utf-8")


def _payloads():
    if not TRANSFER.exists():
        pytest.skip("S10_transfer.md absent")
    return PAYLOAD_RE.findall(TRANSFER.read_text(encoding="utf-8"))


def _target(f):
    if Path(f).name == ARCHIVED_V64:
        return MANUSCRIPT_DIR / (MANUSCRIPT_DIR / "CURRENT").read_text(encoding="utf-8").strip()
    return ROOT_DIR / f


def test_transfer_S10_anchors_resolve_exactly_once():
    payloads = _payloads()
    assert len(payloads) == 3, f"{len(payloads)} payloads parsed -- the fence shape changed"
    for f, search, replace in payloads:
        target = _target(f)
        assert target.exists(), f
        text = target.read_text(encoding="utf-8")
        state = (text.count(search) - text.count(replace) * replace.count(search), text.count(replace))
        assert state in [(1, 0), (0, 1)], (f, state, search.splitlines()[0][:80])


def test_transfer_S10_payloads_avoid_the_excluded_subsections():
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
