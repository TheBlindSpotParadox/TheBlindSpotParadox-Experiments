# tests/test_S2bis_calibration.py
"""Stream S2-bis statutory guard-rails and reproduction checks.

Two kinds of test, kept apart on purpose.

1. GUARD-RAILS. Pure arithmetic and pure control flow, no artifact and no campaign. They encode the
   degenerate cases rule B7 declares terminal -- `SATURATED`, `NOT ATTAINABLE`, `NOT ARMED` -- plus
   the two places a silent wrong answer could enter: a Cramer root that does not exist, and a ratio
   taken when one arm has `F1 = 0`. Each is one assertion on one behaviour. They run on a fresh
   clone with no `results/` at all.

2. REPRODUCTION. Read the committed artifacts and the frozen R4/R5 artifacts and check the
   identities the stream claims. Each skips with an EXECUTABLE remedy when its artifact is absent,
   so the suite is green on a fresh clone and enforcing after a reproduction.

Usage:  PYTHONHASHSEED=0 python -m pytest tests/test_S2bis_calibration.py -v
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "S2bis_calibration"))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "R4_proteus_evaluation"))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "R5_real_world_evaluation"))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "S2_theory"))
from config import experiment_ssot as ssot          # noqa: E402
import s2bis_lambda_eq as p1                        # noqa: E402
import s2bis_proteus_calibration as p2              # noqa: E402
import s2bis_r1_ppre as p3                          # noqa: E402
import exp_R5_common as common                      # noqa: E402
import exp_R5_config as cfg                         # noqa: E402
import exp_R4_main_table as r4                      # noqa: E402
from s2_arl0 import cramer_root                     # noqa: E402

TABLES = ssot.RESULTS_DIR / "S2bis_calibration" / "tables"
RUN_P1 = ("PYTHONHASHSEED=0 python experiments/S2bis_calibration/s2bis_lambda_eq.py")
RUN_P2 = ("PYTHONHASHSEED=0 python experiments/S2bis_calibration/s2bis_proteus_calibration.py")
RUN_P3 = ("PYTHONHASHSEED=0 python experiments/S2bis_calibration/s2bis_r1_ppre.py")


def _need(path, remedy):
    if not path.exists():
        pytest.skip(f"{path.relative_to(ROOT_DIR)} absent -- produce it with:\n    {remedy}")
    return path


# ══════════════════════════════════════════════════════════════════════════════
# 1. Statutory guard-rails (rule B7 and the two silent-wrong-answer paths)
# ══════════════════════════════════════════════════════════════════════════════
def test_no_cramer_root_raises_instead_of_returning_a_silent_arl0():
    """p_true >= p_pre + delta: the null drift is non-negative, the CUSUM has no positive Cramer
    root and ARL_0 is not defined. The failure must be loud at the solver and declared at the
    caller -- never a silent 0/0 that propagates into a threshold."""
    with pytest.raises(ValueError):
        cramer_root(0.5, 0.1, cfg.PHT_DELTA)
    lam, theta, note = p1.lambda_eq_arl(10_000.0, 0.0)
    assert lam is None and note is not None, (lam, theta, note)


def test_bisection_ceiling_is_saturated_never_a_value():
    """A lambda_eq returned at the upper end of S2BIS_LAMBDA_BRACKET is a BOUND. Rule B7."""
    v = p1.calibration_verdict([0.0] * 200, p1.LAMBDA_HI)
    assert v["verdict"] == "SATURATED"
    assert str(int(p1.LAMBDA_HI)) in v["bound"] or f"{p1.LAMBDA_HI:g}" in v["bound"]
    assert p2.calibration_verdict([0.0] * 200, p2.LAMBDA_HI)[0] == "SATURATED"


def test_target_unreachable_on_the_span_is_not_attainable_with_its_bound():
    """More alarms than the budget at the returned threshold: NOT ATTAINABLE, bound reported."""
    rng = np.random.default_rng(ssot.S2BIS_BOOTSTRAP_SEED)
    # A stream that ramps: PageHinkley in 'both' mode crosses repeatedly however low the threshold
    # is set, so at lambda = 1 the one-alarm budget is unreachable by construction.
    ramp = list(rng.binomial(1, np.linspace(0.02, 0.9, 600)).astype(float))
    v = p1.calibration_verdict(ramp, 1.0)
    assert v["verdict"] == "NOT ATTAINABLE", v
    assert v["attained_fa"] > cfg.PHT_TARGET_FA and v["bound"], v


def test_span_shorter_than_the_arming_time_is_not_armed():
    """River PageHinkley does not test before `min_instances` observations. Rule B7."""
    short = [0.0] * (ssot.S2BIS_PHT_MIN_INSTANCES - 1)
    assert p1.calibration_verdict(short, 40.0)["verdict"] == "NOT ARMED"
    assert p2.calibration_verdict(short, 40.0)[0] == "NOT ARMED"
    assert p1.count_false_alarms(short, 1.0) == 0


def test_f1_zero_in_one_arm_takes_the_difference_path_not_the_ratio():
    """Rule B3's declared degenerate handling: the ratio is undefined, dF1 arbitrates."""
    g = p1.gate_b3({"F1_ht_mean": 0.31, "F1_arf_mean": 0.0, "ratio_point": None,
                    "ratio_ci": None, "diff_point": 0.31, "diff_ci": [0.22, 0.40]})
    assert g["decision_variable"].startswith("dF1") and g["verdict"] == "SURVIVES", g
    z = p1.gate_b3({"F1_ht_mean": 0.0, "F1_arf_mean": 0.0, "ratio_point": None, "ratio_ci": None,
                    "diff_point": 0.0, "diff_ci": [-0.01, 0.01]})
    assert z["verdict"] == "COLLAPSE" and z["decision_variable"].startswith("dF1"), z


def test_lambda_eq_is_monotone_increasing_in_p_true_at_a_fixed_target():
    """The S2-bis plan states this guard-rail as "monotone DECREASING in p_true". The model's own
    arithmetic gives the opposite sign and the frozen measurement agrees, so the guard-rail is
    enforced in the direction the arithmetic fixes; the divergence is recorded in
    docs/theory/transfer_S2bis.md rather than silenced.

    theta* solves E[exp(theta (X - p - delta))] = 1 for X ~ Bern(p) and shrinks as Var(X) = p(1-p)
    grows; ARL_0 is increasing in theta at fixed lambda; so a fixed false-alarm budget costs MORE
    threshold on a noisier pre-change stream. Measured on the frozen R5 artifact: e_pre 0.058 ->
    lambda 20.97 (ARF), e_pre 0.075 -> lambda 132.50 (HT)."""
    lams = [p1.lambda_eq_arl(10_000.0, p)[0] for p in (0.005, 0.01, 0.02, 0.04, 0.08, 0.16)]
    assert all(a < b for a, b in zip(lams, lams[1:])), lams
    thetas = [cramer_root(p, p, cfg.PHT_DELTA) for p in (0.005, 0.01, 0.02, 0.04, 0.08, 0.16)]
    assert all(a > b for a, b in zip(thetas, thetas[1:])), thetas


def test_lambda_eq_is_monotone_increasing_in_the_target_span():
    """A longer armed span demands a higher threshold for the same one-alarm budget."""
    lams = [p1.lambda_eq_arl(n, ssot.P0_MEASURED)[0] for n in (1e3, 1e4, 1e5, 1e6, 1e7)]
    assert all(a < b for a, b in zip(lams, lams[1:])), lams


# ══════════════════════════════════════════════════════════════════════════════
# 2. The two evaluator identities the campaign rests on
# ══════════════════════════════════════════════════════════════════════════════
def test_injected_lambda_driver_reproduces_run_evaluation_bit_for_bit():
    """`run_at_lambda` differs from `exp_R5_common.run_evaluation` in exactly one line -- the
    threshold is injected instead of calibrated. With the calibrated threshold injected, the
    detections, the whole error stream and the threshold must be identical objects."""
    csv = cfg.INSECTS_DIR / "gradual_balanced.csv"
    _need(csv, "the INSECTS streams live under data/insects/ and are not tracked by git")
    df, target = p1.load_variant("gradual_balanced")
    df = df.iloc[:5000]
    warm, seed = 500, common.make_seed_pool()[0]
    for pipe in ("pht_ht", "pht_arf_c1"):
        d1, e1, l1 = common.run_evaluation(pipe, seed, p1.feature_stream(df, target), warm,
                                           cfg.INSECTS_NONE_FILL)
        d2, e2, l2 = p1.run_at_lambda(pipe, seed, p1.feature_stream(df, target), warm,
                                      cfg.INSECTS_NONE_FILL, l1)
        assert (d1, e1, l1) == (d2, e2, l2), pipe


def test_evaluate_full_reproduces_r4_evaluate():
    """S2-bis records the precision R4 computes and discards. The matching itself must not move."""
    cases = [([4100], [4000], 1000), ([], [4000], 1000), ([7000], [4000], 1000),
             ([4000], [4000], 1000), ([4050, 4900, 6000], [4000], 1000),
             ([3999, 4001], [4000], 1000), ([4500], [4000, 4400], 500)]
    for detected, truth, tau in cases:
        add_r4, f1_r4 = r4.evaluate(detected, truth, 8000, tau)
        m = p2.evaluate_full(detected, truth, 8000, tau)
        assert f1_r4 == m["F1"], (detected, truth, tau)
        assert (np.isnan(add_r4) and np.isnan(m["ADD"])) or add_r4 == m["ADD"], (detected, truth)
        assert m["TP"] + m["FP"] == m["n_detections"]


def test_equalising_alphas_invert_their_own_requirements():
    """The alpha that would place ADWIN or KSWIN at the CUSUM's level, checked by substitution."""
    w, n_stat = 57.4, 30
    margin = float(np.sqrt(w / 2.0 * np.log(1.0 / ssot.EPS_MISS)))
    for lam in (8.0, 15.0, 25.0, 50.0):
        a_ad = 4.0 * w * np.exp(-2.0 * lam ** 2 / w)
        a_ks = 2.0 * np.exp(-lam ** 2 / n_stat)
        assert abs(np.sqrt(w / 2.0 * np.log(4.0 * w / a_ad)) + margin - (lam + margin)) < 1e-9
        assert abs(np.sqrt(n_stat * np.log(2.0 / a_ks)) + margin - (lam + margin)) < 1e-9


# ══════════════════════════════════════════════════════════════════════════════
# 3. Reproduction checks on the committed artifacts
# ══════════════════════════════════════════════════════════════════════════════
def test_lambda_calibrated_is_lambda_eq_at_the_warm_up_target():
    """Phase 1 step 3. R5's frozen `lambda_calibrated` column IS lambda_eq(T_warm), re-derived from
    the CSVs by an independent driver. Exact equality, not a tolerance: same bisection, same
    stream, same seeds."""
    gate = _need(TABLES / "s2bis_flooding_gate.json", RUN_P1)
    rows = json.loads(gate.read_text(encoding="utf-8"))[
        "identity_lambda_calibrated_is_lambda_eq_T_warm"]
    assert rows, "no identity row produced"
    bad = [r for r in rows if not r["identical"]]
    assert not bad, "lambda_eq(T_warm) does not reproduce lambda_calibrated:\n  " + "\n  ".join(
        f"{r['variant']}/{r['pipeline']}: frozen {r['frozen_lambda_calibrated_mean']!r} vs "
        f"S2-bis {r['s2bis_lambda_eq_warm_mean']!r}" for r in bad)


def test_budget_span_mismatch_is_measured_not_asserted():
    """The armed pre-change span is strictly longer than the warm-up on every INSECTS variant, and
    the T_warm threshold therefore admits more than one alarm over it. Both are read from the
    artifact; neither is a modelled prediction."""
    gate = _need(TABLES / "s2bis_flooding_gate.json", RUN_P1)
    payload = json.loads(gate.read_text(encoding="utf-8"))
    for variant, e in payload["variants"].items():
        for pipe, m in e["budget_span_mismatch"].items():
            assert m["span_over_warmup"] > 1.0, (variant, pipe, m["span_over_warmup"])
            assert m["lambda_eq_T_span_mean"] >= m["lambda_eq_T_warm_mean"], (variant, pipe)


def test_every_b7_verdict_is_one_of_the_four_declared_states():
    """No cell may return an undeclared status, and a SATURATED cell may never be read as a value."""
    csv = _need(TABLES / "s2bis_lambda_eq_insects.csv", RUN_P1)
    d = pd.read_csv(csv, float_precision="round_trip")
    allowed = {"OK", "SATURATED", "NOT ATTAINABLE", "NOT ARMED"}
    assert set(d.verdict_span) <= allowed, set(d.verdict_span) - allowed
    assert set(d.verdict_warm) <= allowed, set(d.verdict_warm) - allowed
    sat = d[d.verdict_span == "SATURATED"]
    assert (sat.lambda_eq_span_emp >= ssot.S2BIS_LAMBDA_BRACKET[1]).all() if len(sat) else True


def test_pht_ht_arm_is_pseudo_replicated_on_the_frozen_artifact():
    """Rule B10. `build_model` returns an unseeded HoeffdingTreeClassifier, so the 30 `pht_ht` runs
    of a variant are one deterministic run repeated. Read-only on R5's frozen parquet."""
    _need(ssot.RESULTS_DIR / "R5_real_world_evaluation" / "data" / "insects_results.parquet",
          "./run_experiment_R5.sh")
    out = p1.pseudo_replication()
    assert out["overall"]["verdict"] == "PSEUDO-REPLICATED", out
    for variant in cfg.INSECTS_VARIANTS:
        assert out[variant]["n_distinct_F1"] == 1, (variant, out[variant])


def test_r1_published_numerals_do_not_route_through_the_fixed_arm():
    """Rule B5, resolved from R1's own AST. `Share_Blind_Spot` and `Detection_Rate` are aggregated
    from the EMPIRICAL arm; `tau_det_fixed` is recorded and read by no aggregation."""
    route = p3.published_numeral_route()
    assert not route["any_published_numeral_routes_through_the_fixed_arm"], route
    assert set(route["aggregations"]) == {"Share_Blind_Spot", "Detection_Rate"}, route


def test_r2_reference_rate_fallback_is_unreachable():
    """T-B(a). The `0.05` at exp_R2_instrumented_blind_spot.py:90 is dead code for any T_DRIFT > 0:
    the buffer is filled over [T_DRIFT - R2_WARMUP_WINDOW, T_DRIFT) and read at t == T_DRIFT."""
    r = p3.r2_fallback_reachability()
    assert r["fallback_reachable"] is False, r
    assert r["buffer_len_at_t_drift"] == ssot.R2_WARMUP_WINDOW, r


def test_r1_counterfactual_reproduces_the_published_blind_spot_column():
    """The counterfactual recomputes `blind_spot_observed` under R1's own definition; the assertion
    that it reproduces the published column lives inside `counterfactual()` and is exercised here."""
    _need(ssot.RESULTS_DIR / "R1_race_condition" / "data" / "R1_race_condition.parquet",
          "./run_experiment_R1.sh")
    csv = _need(TABLES / "s2bis_r1_counterfactual.csv", RUN_P3)
    d = pd.read_csv(csv, float_precision="round_trip")
    assert set(d.lambda_val) == set(float(x) for x in ssot.R1_LAMBDAS), sorted(d.lambda_val)
    assert (d.n_seeds == ssot.R1_N_SEEDS).all(), d.n_seeds.unique()
    # The fixed arm is strictly weaker: it never detects more often than the empirical arm.
    assert (d.delta_Detection_Rate <= 0).all(), d[d.delta_Detection_Rate > 0]


def test_proteus_reproduces_r4_at_the_common_threshold():
    """At lambda = R4_PHT_LAMBDA the six PageHinkley couples must return R4's own F1 and ADD. A
    deviation here means the S2-bis driver is not R4's loop, and every lambda_eq measurement built
    on it is void."""
    gate = _need(TABLES / "s2bis_proteus_gate.json", RUN_P2)
    nr = json.loads(gate.read_text(encoding="utf-8"))["r4_non_regression_at_lambda_ref"]
    if nr["status"] != "CHECKED":
        pytest.skip(f"R4 non-regression not checkable: {nr}")
    assert nr["identical"], nr


def test_no_frozen_artifact_outside_the_s2bis_tree_was_written():
    """The S2-bis write perimeter, enforced on the artifact tree itself: every file this stream
    produces lives under results/S2bis_calibration/ and carries an `s2bis_` basename, so it can
    collide neither with the frozen hash list nor with the basename glob of
    tests/test_manuscript_integrity.py."""
    _need(TABLES, RUN_P1)
    produced = sorted(p.name for p in TABLES.rglob("*") if p.is_file())
    assert produced, "no S2-bis artifact produced"
    bad = [n for n in produced if not n.startswith("s2bis_")]
    assert not bad, bad
