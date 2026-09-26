"""Tests for S13 evidence bell, refitted exponent, and skill floor."""
import json
from pathlib import Path
import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
S13_DIR = REPO_ROOT / "results" / "S13_evidence_bell"
BELL_CSV = S13_DIR / "evidence_bell.csv"
GATE_JSON = S13_DIR / "s13_gate.json"


def test_evidence_bell_contract():
    assert BELL_CSV.exists(), f"Missing {BELL_CSV}"
    assert GATE_JSON.exists(), f"Missing {GATE_JSON}"

    df = pd.read_csv(BELL_CSV, float_precision="round_trip")
    with open(GATE_JSON) as f:
        gate = json.load(f)

    # 0. Assertion de non vacuité sur la grille d'amplitudes
    assert len(df) >= 10, f"Amplitude grid too sparse or empty: {len(df)} rows"

    # 1. La cloche a un maximum intérieur
    idxmax = int(df["smax_mean"].idxmax())
    assert 0 < idxmax < len(df) - 1, (
        f"Maximum is not interior: peak index {idxmax} on grid size {len(df)}"
    )

    # 2. Son sommet dépasse strictement ses deux extrémités
    peak_val = df["smax_mean"].iloc[idxmax]
    left_val = df["smax_mean"].iloc[0]
    right_val = df["smax_mean"].iloc[-1]
    assert peak_val > left_val, f"Peak {peak_val} does not exceed left extremity {left_val}"
    assert peak_val > right_val, f"Peak {peak_val} does not exceed right extremity {right_val}"

    # 3. L'exposant réajusté est inférieur à -1.5
    slope = gate["tau_exponent"]["estimate"]
    assert slope < -1.5, f"Expected adaptation exponent < -1.5, got {slope}"

    # 4. Episode skill crosses zero inside the grid; converged skill either
    #    crosses or the absence is declared as null (never a placeholder).
    zero_cross = gate["skill_zero_crossing_episode"]
    min_de = df["delta_e"].min()
    max_de = df["delta_e"].max()
    assert min_de < zero_cross < max_de, (
        f"Skill zero-crossing {zero_cross} is outside the interior grid ({min_de}, {max_de})"
    )
    conv = gate["skill_zero_crossing_converged"]
    assert conv is None or min_de < conv < max_de, (
        f"Converged skill zero-crossing {conv} is neither interior nor declared null"
    )

def test_baseline_bias_is_measured_not_substituted():
    gate = json.load(open(GATE_JSON))
    source = gate["baseline_bias_source"]
    if source == "measured_from_traces":
        assert gate["baseline_bias_n"] >= 100
        # A round placeholder is the signature of a fallback that fired.
        assert abs(gate["baseline_bias_1000_vs_3000"] - 0.007) > 1e-9
    else:
        # Declared gap: an uncomputable R-5 must be recorded as such, with
        # null values, never masked by a substituted constant.
        assert source.startswith("uncomputable_"), (
            f"Unknown baseline_bias_source {source}"
        )
        assert gate["baseline_bias_1000_vs_3000"] is None
        assert gate["baseline_bias_area_units"] is None


def test_mode_is_reported_as_a_plateau_not_a_point():
    df = pd.read_csv(BELL_CSV, float_precision="round_trip")
    gate = json.load(open(GATE_JSON))
    top = df.nlargest(2, "smax_mean")
    lo = top["smax_ci_lo"].max()
    hi = top["smax_ci_hi"].min()
    if hi > lo:                       # the two candidates overlap
        assert max(gate["mode_posterior"].values()) < 0.90, (
            "Overlapping CIs: the mode is not identified and must not be "
            "reported as a point estimate"
        )