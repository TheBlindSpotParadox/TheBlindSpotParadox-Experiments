# tests/test_R5_table2.py
"""Non-regression test for Experiment R5 (Table II + flooding decomposition).

Specified by `results/audit_S7/regeneration_spec.md` G3 and implemented in stream S7-ter. Reads the
committed artifacts only -- no re-run -- and skips with an explicit motive when one is absent.

Table II is the second table reviewers read and it carried no test. The three BAF rows are the
paper's weak-signal anchor: Delta_e indistinguishable from zero, intervals covering zero, and no
seed-level test reported. That is asserted here as a property, not left implicit, because it is the
claim stream S7-ter LOT C re-measures against a frozen-classifier oracle -- and the oracle writes to
a SEPARATE artifact (`delta_e_oracle.parquet`), so the adaptive values pinned below stay live.

Usage:  PYTHONHASHSEED=0 python -m pytest tests/test_R5_table2.py -v
"""
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent
R5_DATA = ROOT_DIR / "results" / "R5_real_world_evaluation" / "data"
R5_TABLES = ROOT_DIR / "results" / "R5_real_world_evaluation" / "tables"
DELTA_E = R5_DATA / "delta_e.parquet"
FLOODING = R5_DATA / "flooding_decomposition.parquet"
TABLE2 = R5_TABLES / "table2_values.csv"

SIGN_FLOOR = 2.0 ** -29
BAF_VARIANTS = ["Base", "VariantI", "VariantII"]
# Delta_e per INSECTS variant, adaptive estimator (reference Hoeffding Tree, never frozen).
INSECTS_DELTA_E = {"abrupt_balanced": 0.0743,
                   "gradual_balanced": 0.4503,
                   "incremental_reoccurring_balanced": 0.3914}
ABRUPT_PER_JUMP = [0.6801, -0.1474, 0.2448, -0.2717, -0.1341]


def _read(path, **kw):
    if not path.exists():
        pytest.skip(f"artifact absent -- run ./run_experiment_R{path.parts[-3][1]}.sh")
    return pd.read_parquet(path) if path.suffix == ".parquet" else pd.read_csv(path, **kw)


def test_baf_sits_at_the_weak_signal_anchor():
    d = _read(DELTA_E).set_index("variant")
    for v in BAF_VARIANTS:
        row = d.loc[v]
        assert abs(row.delta_e_mean) < 0.005, f"BAF {v}: Delta_e = {row.delta_e_mean}"
        assert row.delta_e_ci_lo < 0.0 < row.delta_e_ci_hi, (
            f"BAF {v}: 95% CI [{row.delta_e_ci_lo}, {row.delta_e_ci_hi}] does not cover zero")
        assert len(row.delta_e_per_drift) == 7, f"BAF {v}: {len(row.delta_e_per_drift)} jumps, expected 7"


def test_insects_delta_e_populates_the_crossover_boundary():
    d = _read(DELTA_E).set_index("variant")
    for v, expected in INSECTS_DELTA_E.items():
        got = d.loc[v].delta_e_mean
        assert got == pytest.approx(expected, abs=0.005), f"INSECTS {v}: Delta_e = {got}"
    per_jump = list(d.loc["abrupt_balanced"].delta_e_per_drift)
    assert np.allclose(per_jump, ABRUPT_PER_JUMP, atol=1e-3), (
        f"abrupt_balanced per-jump vector {per_jump}, expected {ABRUPT_PER_JUMP}")


def test_gradual_balanced_interval_is_degenerate_not_tight():
    """K = 1: one canonical drift, so every bootstrap replicate returns the same value."""
    row = _read(DELTA_E).set_index("variant").loc["gradual_balanced"]
    assert len(row.delta_e_per_drift) == 1
    assert row.delta_e_ci_lo == row.delta_e_ci_hi == row.delta_e_mean, (
        "the K = 1 interval is no longer degenerate; it must be reported as a degeneracy, "
        "never as a tight interval")


def test_flooding_separates_genuine_detection_from_false_alarm_spraying():
    f = _read(FLOODING).set_index(["variant", "pipeline"])
    ht = f.loc[("gradual_balanced", "pht_ht")]
    arf = f.loc[("gradual_balanced", "pht_arf_c1")]
    assert ht.n_alarms == 7.0, f"pht_ht alarms = {ht.n_alarms}, expected 7"
    assert ht.precision == pytest.approx(0.1429, abs=1e-3)
    assert arf.n_alarms == pytest.approx(85.667, abs=0.01), f"pht_arf_c1 alarms = {arf.n_alarms}"
    assert arf.precision == pytest.approx(0.0120, abs=1e-3)
    assert bool(ht.detection_genuine) is True, "pht_ht on gradual_balanced must read as genuine"
    assert bool(arf.detection_genuine) is False, "pht_arf_c1 on gradual_balanced must read as flooding"


def test_table2_ratios_and_seed_level_tests():
    t = _read(TABLE2, float_precision="round_trip").set_index("variant")
    gradual, reoccurring = t.loc["gradual_balanced"], t.loc["incremental_reoccurring_balanced"]
    assert gradual.ratio == pytest.approx(10.57, abs=0.01), f"gradual ratio = {gradual.ratio}"
    assert reoccurring.ratio == pytest.approx(1.61, abs=0.01), f"reoccurring ratio = {reoccurring.ratio}"
    for name, row in (("gradual", gradual), ("reoccurring", reoccurring)):
        assert row.sign_test_p == pytest.approx(SIGN_FLOOR, rel=1e-12), (
            f"{name}: p = {row.sign_test_p}, expected the 2^-29 resolution floor")
        assert row.seeds_favor_HT == 30.0 and row.seeds_favor_ARF == 0.0, (
            f"{name}: {row.seeds_favor_HT}/{row.seeds_favor_ARF}, expected complete separation")
    # The weak witness: the only INSECTS contrast that is not at the floor, and the one the
    # manuscript declines to attribute mechanically. Holm over the declared family does not keep it.
    abrupt = t.loc["abrupt_balanced"]
    assert abrupt.sign_test_p == pytest.approx(0.0428, abs=1e-3), (
        f"abrupt_balanced: p = {abrupt.sign_test_p}, expected 0.043 (weak witness)")
    assert 0.025 < abrupt.sign_test_p < 0.05, (
        "abrupt_balanced no longer sits between the Holm step alpha/2 and alpha; the multiplicity "
        "statement of the protocol section must be re-measured")


def test_baf_rows_carry_no_seed_level_test():
    t = _read(TABLE2, float_precision="round_trip").set_index("variant")
    for v in BAF_VARIANTS:
        assert pd.isna(t.loc[v].sign_test_p), (
            f"BAF {v} now reports a sign test; Delta_e is indistinguishable from zero there and "
            "the multiplicity family of the protocol section would change")


# ── S7-ter / LOT C — the frozen-classifier oracle beside the adaptive estimate ─────────────────
ORACLE = R5_DATA / "delta_e_oracle.parquet"
BAF_MAJORITY_ERROR = 0.0110   # the BAF fraud rate; a majority-class predictor errs at exactly this


def test_oracle_differs_from_the_adaptive_estimate_in_one_input_only():
    """Equal windows is the proof that the two estimates differ in the error stream and nothing else.

    Same drift positions, same adaptive windows, same bootstrap seed; one stream from a tree that
    keeps learning, the other from a copy of it forked at the end of warm-up and never trained
    again. If the window vectors ever diverge the two numbers stop being comparable, and a reader
    would have no way to see it from the artifact."""
    a, o = _read(DELTA_E), _read(ORACLE)
    assert len(o) == len(a) == 6, f"{len(o)} oracle rows against {len(a)} adaptive"
    assert list(o.variant) == list(a.variant)
    for va, vo, name in zip(a.windows, o.windows, a.variant):
        assert list(va) == list(vo), f"{name}: windows {list(va)} vs {list(vo)}"


def test_baf_negative_control_is_confirmed_by_a_non_adapting_model():
    """The BAF verdict, ruled on the measurement and not before it.

    A frozen model cannot absorb a drift, so a jump it does not see is not being masked by
    adaptation. On all three variants the oracle agrees with the adaptive estimate at |Delta_e| <
    0.005 with an interval covering zero: BAF is a negative control, not a stream whose drift
    adaptation erases."""
    o = _read(ORACLE).set_index("variant")
    for v in BAF_VARIANTS:
        row = o.loc[v]
        assert abs(row.delta_e_mean) < 0.005, f"BAF {v}: oracle Delta_e = {row.delta_e_mean}"
        assert row.delta_e_ci_lo < 0.0 < row.delta_e_ci_hi, (
            f"BAF {v}: oracle CI [{row.delta_e_ci_lo}, {row.delta_e_ci_hi}] does not cover zero")


def test_the_oracle_saturation_diagnostic_is_readable():
    """An oracle near zero is only evidence of absence while the frozen model still discriminates.

    On BAF it does, in the weakest possible sense that is still informative: both trees sit at the
    majority-class error rate, which IS the fraud rate, so neither ever learns to separate fraud and
    the streams carry no error transient for any monitor. On INSECTS the frozen tree is near chance
    on six classes after a warm-up of 10 % of a short stream, so its Delta_e is uninformative there
    and must not be read as evidence of a stationary concept -- the adaptive estimate is."""
    o = _read(ORACLE).set_index("variant")
    for v in BAF_VARIANTS:
        row = o.loc[v]
        assert row.err_mean_post_fork == pytest.approx(BAF_MAJORITY_ERROR, abs=5e-4), (
            f"BAF {v}: frozen error {row.err_mean_post_fork}, expected the majority-class rate")
        assert abs(row.err_mean_post_fork - row.err_mean_post_fork_adaptive) < 5e-4, (
            f"BAF {v}: the adaptive tree no longer sits at the majority-class rate either; the "
            "negative-control reading must be re-derived")
    for v in ("gradual_balanced", "incremental_reoccurring_balanced"):
        row = o.loc[v]
        assert row.err_mean_post_fork > row.err_mean_post_fork_adaptive + 0.15, (
            f"INSECTS {v}: the frozen tree is no longer saturated relative to the adaptive one "
            f"({row.err_mean_post_fork} vs {row.err_mean_post_fork_adaptive}); its oracle "
            "Delta_e may now be informative and the declared limitation should be revisited")
