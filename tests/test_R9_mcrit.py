# tests/test_R9_mcrit.py
"""
Non-regression test for Experiment R9 (worked M_crit example, distribution-free).
Asserts that the regenerated artifact reproduces the numerical example of the manuscript Corollary
at the reliability target r = 0.95 (r = 1 - P_miss; the manuscript's eq:mcrit uses ln r).
Run after run_experiment_R9.sh.   Usage:  python -m pytest tests/test_R9_mcrit.py
"""
import numpy as np
import pandas as pd
import pytest
from pathlib import Path
from pytest import approx

ROOT_DIR = Path(__file__).resolve().parent.parent
CSV = ROOT_DIR / "results" / "R9_mcrit" / "data" / "exp_R9_mcrit_comparison.csv"

def test_mcrit_numerical_example():
    df = pd.read_csv(CSV, float_precision="round_trip")
    if "reliability_r" not in df.columns or not np.isclose(df["reliability_r"], 0.95).any():
        pytest.skip("R9 artifact predates RELIABILITY_TARGETS=[0.99,0.95,0.50]; "
                    "test is false by construction until R9 is regenerated")
    r95 = np.isclose(df["reliability_r"], 0.95)
    row = df[r95 & np.isclose(df["delta_e"], 0.33) & (df["lambda"] == 50)].iloc[0]
    assert row["E_tau_HAT"]      == approx(463, rel=0.05), row["E_tau_HAT"]
    assert row["tau_det_star"]   == approx(155, rel=0.05), row["tau_det_star"]
    assert row["F_emp"]          == approx(0.49, abs=0.03), row["F_emp"]
    assert int(row["Mcrit_emp"]) == 0, row["Mcrit_emp"]
    assert row["Pmiss_M10"]      == approx(0.999, abs=0.003), row["Pmiss_M10"]
