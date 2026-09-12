# tests/test_R4_table1.py
"""Non-regression test for Experiment R4 (Table I + KSWIN alpha-sweep).

Specified by `results/audit_S7/regeneration_spec.md` G3 and implemented in stream S7-ter. Reads the
committed artifacts only -- no re-run -- and skips with an explicit motive when one is absent.

Table I is the table reviewers read and it carried no test. This file was also the measuring
instrument of stream S7-ter LOT B, and it has now taken its measurement. Written against the
pre-unification artifact, it reported exactly one failure after the re-run -- the ADWIN+RF vs
ADWIN+ARF seed-level count, 1063 -> 1070 of 1080 -- and passed on everything else. The values below
are RE-PINNED onto the post-unification artifact so the guard is armed again; the superseded value
is kept beside each one rather than deleted, because a pin with no memory of what it replaced is a
pin nobody can audit.

The seed-paired bootstrap correction of LOT B changes the CI half-widths only. Measured: between the
two R4 re-runs every raw CSV is byte-identical and only the two rendered .tex files move. That is
what separates the two causes, and it is why the counts asserted here isolate the unification
alone.

Usage:  PYTHONHASHSEED=0 python -m pytest tests/test_R4_table1.py -v
"""
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent
R4_DIR = ROOT_DIR / "results" / "R4_proteus_evaluation" / "data"
RAW_CSV = R4_DIR / "exp_R4_results_aligned_fusion.csv"
SIGN_CSV = R4_DIR / "exp_R4_seed_level_tests.csv"
SWEEP_CSV = R4_DIR / "exp_R4_results_KSWIN_alpha_sweep.csv"

REGIMES = ["IID", "Cal. A", "Cal. B"]
N_ROWS = 16200          # 15 pipelines x 3 regimes x 12 transitions x 30 seeds (15, not the 14 rendered)
N_PER_CELL = 360        # 12 transitions x 30 seeds
SIGN_FLOOR = 2.0 ** -29  # two-sided sign test resolution floor at n_eff = 30

# (pipeline_A, pipeline_B) -> (n_det_A, n_det_B); complete separations of the Table I caption.
SEED_LEVEL_COUNTS = {
    ("PHT+ARF c=1", "PHT+HT"):            (0, 932),
    ("SRP+PHT c=1", "PHT+HT"):            (0, 932),
    ("KSWIN+ARF c=1", "PHT+ARF c=1"):     (1080, 0),
    ("PHT+RF", "PHT+ARF c=1"):            (913, 0),
    # 1063 before S7-ter/LOT B. The unification gave the windowed monitor 7 more detected runs out
    # of 1080; the static arm is unmoved, having no warning detector to unify.
    ("ADWIN+RF", "ADWIN+ARF c=1"):        (959, 1070),
    ("EDDM+ARF c=1", "EDDM+HT"):          (0, 882),
}


def _read(path, **kw):
    if not path.exists():
        pytest.skip(f"artifact absent -- run ./run_experiment_R{path.parts[-3][1]}.sh")
    return pd.read_parquet(path) if path.suffix == ".parquet" else pd.read_csv(path, **kw)


def _agg():
    """Cell-level (F1 mean, ADD mean, ADD population std) keyed by (Detector, Clock, Calibration)."""
    df = _read(RAW_CSV, float_precision="round_trip")
    return df, df.groupby(["Detector", "Clock", "Calibration"]).agg(
        F1=("F1", "mean"),
        ADD=("ADD", lambda x: np.nan if x.dropna().empty else x.dropna().mean()),
        ADD_sd=("ADD", lambda x: np.nan if x.dropna().empty else x.dropna().std(ddof=0)),
        n=("F1", "size"))


def test_shape_is_15_pipelines_not_the_14_rendered():
    df, agg = _agg()
    assert len(df) == N_ROWS, f"{len(df)} rows, expected {N_ROWS}"
    assert (agg["n"] == N_PER_CELL).all(), agg[agg["n"] != N_PER_CELL].to_string()
    assert len(agg) == 15 * 3, f"{len(agg)} cells, expected 15 pipelines x 3 regimes"


@pytest.mark.parametrize("detector,clock", [("PHT + ARF", 1), ("EDDM + ARF", 1), ("SRP + PHT", 1)])
def test_blind_spot_collapse_is_total(detector, clock):
    """F1 is exactly zero and ADD undefined: no alarm falls in the tolerance window, in any regime."""
    _, agg = _agg()
    for regime in REGIMES:
        cell = agg.loc[(detector, clock, regime)]
        assert cell.F1 == 0.0, f"{detector} c={clock} {regime}: F1 = {cell.F1}, expected exactly 0"
        assert np.isnan(cell.ADD), f"{detector} c={clock} {regime}: ADD = {cell.ADD}, expected NaN"


def test_kswin_resolves_the_blind_spot_at_both_clocks():
    _, agg = _agg()
    for clock in (1, 32):
        for regime in REGIMES:
            cell = agg.loc[("KSWIN + ARF", clock, regime)]
            assert cell.F1 == 1.0, f"KSWIN c={clock} {regime}: F1 = {cell.F1}, expected exactly 1"
            assert cell.ADD == 14.0, f"KSWIN c={clock} {regime}: ADD = {cell.ADD}, expected 14"
            assert cell.ADD_sd == 0.0, f"KSWIN c={clock} {regime}: ADD sd = {cell.ADD_sd}, expected 0"


def test_adwin_clock_artefact_locks_the_delay_at_31():
    """eq:clock: at c = 32 the worst-case phase alignment fixes ADD with zero variance."""
    _, agg = _agg()
    for regime in REGIMES:
        c32 = agg.loc[("ADWIN + ARF", 32, regime)]
        assert c32.ADD == 31.0, f"ADWIN+ARF c=32 {regime}: ADD = {c32.ADD}, expected 31"
        assert c32.ADD_sd == 0.0, f"ADWIN+ARF c=32 {regime}: ADD sd = {c32.ADD_sd}, expected 0"
        c1 = agg.loc[("ADWIN + ARF", 1, regime)]
        assert c1.ADD == pytest.approx(9.0, abs=0.5), f"ADWIN+ARF c=1 {regime}: ADD = {c1.ADD}"


def test_safe_configurations_detect():
    _, agg = _agg()
    for regime in REGIMES:
        pht_ht = agg.loc[("PHT + HT", 1, regime)].F1
        adwin_ht = agg.loc[("ADWIN + HT", 1, regime)].F1
        assert pht_ht >= 0.75, f"PHT+HT {regime}: F1 = {pht_ht}, expected >= 0.75"
        assert adwin_ht >= 0.80, f"ADWIN+HT {regime}: F1 = {adwin_ht}, expected >= 0.80"


def test_static_rf_restores_the_cumulative_monitor():
    _, agg = _agg()
    assert agg.loc[("PHT + RF (Static)", 1, "IID")].F1 == pytest.approx(0.73, abs=0.02)
    assert agg.loc[("PHT + RF (Static)", 1, "Cal. B")].F1 == pytest.approx(0.96, abs=0.02)
    for regime in REGIMES:
        add = agg.loc[("PHT + RF (Static)", 1, regime)].ADD
        assert 19.0 <= add <= 21.0, f"PHT+RF {regime}: ADD = {add}, expected 19-20"


def test_seed_level_counts_and_complete_separations():
    sign = _read(SIGN_CSV, float_precision="round_trip").set_index(["pipeline_A", "pipeline_B"])
    assert len(sign) == len(SEED_LEVEL_COUNTS), f"{len(sign)} contrasts, expected {len(SEED_LEVEL_COUNTS)}"
    for pair, (det_a, det_b) in SEED_LEVEL_COUNTS.items():
        row = sign.loc[pair]
        assert (row.n_det_A, row.n_det_B) == (det_a, det_b), (
            f"{pair}: {row.n_det_A}/{row.n_total_A} vs {row.n_det_B}/{row.n_total_B}, "
            f"expected {det_a} vs {det_b}")
        assert row.n_total_A == row.n_total_B == 1080
        assert row.sign_test_p == pytest.approx(SIGN_FLOOR, rel=1e-12), (
            f"{pair}: p = {row.sign_test_p}, expected the 2^-29 resolution floor")
        assert row.seeds_tied == 0, f"{pair}: {row.seeds_tied} tied seeds, expected complete separation"


def test_kswin_alpha_sweep_is_flat():
    sweep = _read(SWEEP_CSV, float_precision="round_trip")
    per_cell = sweep.groupby(["Detector", "Calibration"]).F1.agg(["mean", "size"])
    assert len(per_cell) == 4 * 3, f"{len(per_cell)} cells, expected 4 alphas x 3 regimes"
    assert (per_cell["size"] == N_PER_CELL).all(), per_cell.to_string()
    assert (per_cell["mean"] == 1.0).all(), (
        "KSWIN loses F1 = 1.00 somewhere on the alpha sweep:\n" + per_cell.to_string())
