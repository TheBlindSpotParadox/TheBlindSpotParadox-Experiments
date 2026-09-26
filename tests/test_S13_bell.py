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

    # 4. Le score d'habileté franchit zéro à l'intérieur de la grille
    zero_cross = gate["skill_zero_crossing"]
    min_de = df["delta_e"].min()
    max_de = df["delta_e"].max()
    assert min_de < zero_cross < max_de, (
        f"Skill zero-crossing {zero_cross} is outside the interior grid ({min_de}, {max_de})"
    )