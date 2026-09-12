# tests/test_R8_lambda_op.py
"""
Non-regression test for Experiment R8 (fine-grid tau_ARF sweep, warm-up sensitivity).

Guards the two numerical statements the manuscript reads off this sweep at .tex L395: the
q_05(tau_ARF) plateau at T_drift = 2000, and its dissolution at T_drift = 4000. The plateau is
what identifies the low-magnitude floor as a property of an immature ensemble rather than a
signature of noise-driven swaps -- the interpretation the manuscript now states and the submitted
version had wrong -- so the refutation rests on the pair, not on either sweep alone.

Action A2 removed the two assertions that read `lambda_limit = q05(tau_ARF) * (Delta_e - delta_P)`.
That rectangular surrogate is withdrawn at .tex L385; its targets (4.2 at Delta_e = 0.20, and a
ceiling of 12.4 over [0.20, 0.50]) have zero occurrences in the manuscript of record. Both
assertions were green, so they certified an abandoned estimator instead of failing on it -- the
state a non-regression suite must never be left in. The column itself is purged from the artifacts.

Run after run_experiment_R8.sh.   Usage:  python -m pytest tests/test_R8_lambda_op.py
"""
import numpy as np
import pandas as pd
from pathlib import Path
import pytest
from pytest import approx

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA = ROOT_DIR / "results" / "R8_lambda_op_sweep" / "data"
CSV_T2000 = DATA / "exp_R8_lambda_op_sweep.csv"
CSV_T4000 = DATA / "exp_R8_lambda_op_sweep_tdrift4000.csv"

LOW_BAND = (0.10, 0.12, 0.14, 0.16)      # the four magnitudes .tex L395 quotes
PLATEAU = 12.95                          # q05(tau_ARF) at T_drift = 2000, constant over LOW_BAND
DISSOLVED = (25.70, 30.95, 54.70, 54.70)  # the same four at T_drift = 4000


def q05(csv, de):
    df = pd.read_csv(csv, float_precision="round_trip")
    return float(df[np.isclose(df["delta_e"], de)]["q05_tau_arf"].iloc[0])


def test_warmup_plateau_at_tdrift_2000():
    """.tex L395: q05(tau_ARF) is magnitude-independent, constant at 12.95, for Delta_e <= 0.16.

    This is the immature-ensemble floor at the published warm-up, NOT a signature of noise-driven
    swaps: the manuscript retracts that reading in the same sentence."""
    for de in LOW_BAND:
        assert q05(CSV_T2000, de) == approx(PLATEAU, abs=0.5), f"q05 at {de} = {q05(CSV_T2000, de)}"


def test_plateau_dissolves_at_tdrift_4000():
    """.tex L395: the identical sweep at T_drift = 4000 dissolves the plateau, q05 rising
    25.70 -> 30.95 -> 54.70 -> 54.70 over the same four magnitudes. Without this arm the floor
    reads as a property of the ARF; with it, as a property of the warm-up."""
    if not CSV_T4000.exists():
        pytest.skip(f"{CSV_T4000.name} absent; run exp_R8_lambda_op_sweep.py 4000")
    measured = [q05(CSV_T4000, de) for de in LOW_BAND]
    assert measured == approx(list(DISSOLVED), abs=0.5), measured
    assert measured[-1] > 2 * PLATEAU, (
        f"plateau has not dissolved: q05 at Delta_e = {LOW_BAND[-1]} is {measured[-1]}, "
        f"against {PLATEAU} at T_drift = 2000")


def test_withdrawn_surrogate_is_absent_from_the_artifacts():
    """A2: `lambda_limit` is purged, not merely unread. A column left in place is a value a future
    reader can cite, which is exactly how the delta_P conflation of action A1 survived."""
    for csv in (CSV_T2000, CSV_T4000):
        if not csv.exists():
            continue
        cols = list(pd.read_csv(csv, nrows=0).columns)
        assert "lambda_limit" not in cols, f"{csv.name} still carries the withdrawn surrogate: {cols}"
