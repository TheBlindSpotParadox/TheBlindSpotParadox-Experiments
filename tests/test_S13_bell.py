"""Tests for S13 evidence bell, refitted exponent, and skill floor."""
import json
from pathlib import Path
import numpy as np
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


def test_converged_windows_carry_event_counts():
    """R-6: an equality claim at the degenerate end must carry its power."""
    df = pd.read_csv(BELL_CSV, float_precision="round_trip")
    for col in (
        "err_converged_1000",
        "skill_converged_1000",
        "skill_converged_1000_ci_lo",
        "skill_converged_1000_ci_hi",
        "n_errors_converged",
        "n_errors_converged_1000",
    ):
        assert col in df.columns, f"Missing column {col}"
    last = df.nlargest(3, "delta_e")
    assert (last["n_errors_converged"] > 0).all(), (
        "Event counts must be actual error counts, never a placeholder zero"
    )
    assert (last["n_errors_converged_1000"] > last["n_errors_converged"]).all(), (
        "The widened window must carry strictly more events than the 200-step one"
    )


def test_hat_refit_is_committed_with_its_interval():
    """R-7: the single-tree onset refit must be a committed, intervalled artifact."""
    gate = json.load(open(GATE_JSON))
    hat = gate["tau_exponent_hat"]
    assert hat["domain_min"] == 0.10
    assert hat["ci_lo"] <= hat["estimate"] <= hat["ci_hi"]
    assert hat["n_censored"] >= 0

def test_segmented_comparison_is_derived_from_the_committed_fit():
    """R-8: the numerals rem:exponent quotes are arithmetic on the committed fit and grid."""
    seg = json.load(open(GATE_JSON))["tau_segmented"]
    df = pd.read_csv(BELL_CSV, float_precision="round_trip")
    valid = df[df["delta_e"] >= 0.10]
    past = valid[valid["delta_e"] > seg["de_star"]]
    n = len(valid)
    assert seg["sse_gain"] == pytest.approx(1 - seg["sse_segmented"] / seg["sse_pooled"])
    assert seg["post_hoc"]["f_stat"] == pytest.approx(
        (seg["sse_pooled"] - seg["sse_segmented"]) / (seg["sse_segmented"] / (n - 3)))
    assert seg["minus2_decline_past_break"] == pytest.approx(
        1 - (past["delta_e"].min() / past["delta_e"].max()) ** 2)
    assert seg["median_decline_past_break"] == pytest.approx(
        1 - past["tau_arf_median"].iloc[-1] / past["tau_arf_median"].iloc[0])
    lo, hi = seg["post_hoc"]["exponent_ci_break_fixed"]
    assert lo <= seg["exponent"] <= hi


def test_local_slopes_are_arithmetic_on_the_committed_medians():
    """rem:exponent cites the half-steps of the right end and the quadratic term; both are read
    from the gate, which must agree with the committed medians."""
    gate = json.load(open(GATE_JSON))
    df = pd.read_csv(BELL_CSV, float_precision="round_trip")
    valid = df[df["delta_e"] >= 0.10]
    x, m = np.log(valid["delta_e"].to_numpy()), valid["tau_arf_median"].to_numpy()
    slopes = gate["local_slopes"]
    assert len(slopes) == len(valid) - 1 == 17
    for i, s in enumerate(slopes):
        assert s["slope"] == pytest.approx(np.log(m[i + 1] / m[i]) / (x[i + 1] - x[i]))
        assert s["half_steps"] == round(2 * abs(m[i + 1] - m[i]))
    assert sum(s["half_steps"] for s in slopes[-5:]) == 4
    curv = gate["curvature"]
    assert curv["quadratic_coef"] == pytest.approx(np.polyfit(x, np.log(m), 2)[0])
    assert curv["quadratic_ci"][0] <= curv["quadratic_coef"] <= curv["quadratic_ci"][1]


def test_curvature_robustness_is_recomputable():
    """The quadratic onset term survives removing the leftmost magnitude and the six quantised
    largest ones; every entry is recomputable from the committed medians."""
    rob = json.load(open(GATE_JSON))["curvature"]["robustness"]
    df = pd.read_csv(BELL_CSV, float_precision="round_trip")
    valid = df[df["delta_e"] >= 0.10]
    x, y = np.log(valid["delta_e"].to_numpy()), np.log(valid["tau_arf_median"].to_numpy())
    subsets = {"all": slice(0, None), "without the leftmost point": slice(1, None),
               "without the six largest magnitudes": slice(0, -6), "without both": slice(1, -6)}
    assert [s["points"] for s in rob["subsets"]] == list(subsets)
    for s in rob["subsets"]:
        xs, ys = x[subsets[s["points"]]], y[subsets[s["points"]]]
        X = np.column_stack([np.ones_like(xs), xs, xs ** 2])
        beta, res, *_ = np.linalg.lstsq(X, ys, rcond=None)
        se = np.sqrt(res[0] / (len(xs) - 3) * np.linalg.inv(X.T @ X)[2, 2])
        assert (s["n"], s["c2"], s["stderr_ols"]) == (len(xs), pytest.approx(beta[2]), pytest.approx(se))
        assert s["ci"][0] > 0, s
    blocks = rob["disjoint_blocks"]
    assert blocks["slopes"] == pytest.approx([np.polyfit(x[:6], y[:6], 1)[0], np.polyfit(x[6:12], y[6:12], 1)[0]])
    assert blocks["difference_ci"][1] < 0
