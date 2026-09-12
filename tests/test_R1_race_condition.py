# tests/test_R1_race_condition.py
"""Non-regression test for Experiment R1 (race condition, Figure 1).

Specified by `results/audit_S7/regeneration_spec.md` G3 and implemented in stream S7-ter. Reads the
committed artifact only -- no re-run -- and skips with an explicit motive when it is absent, so the
suite is green on a fresh clone and enforcing after a full reproduction.

The two headline figures are POST-A1 values. Action A1 moved the external StrictCUSUM from the
PageHinkley tolerance 0.005 to the fixed-p_0 tolerance CUSUM_DELTA_P = 0.01 that the manuscript
states for eq:cusum, which moved Share_Blind_Spot at lambda = 25 from 0.880 to 0.895 and
Detection_Rate from 0.965 to 0.920 (`results/audit_S7/_baseline/authorized_deviations.txt`). The
specification quotes the pre-A1 pair; this test pins the artifact, which is the live value.

WHICH ARM THESE ASSERTIONS COVER. R1 runs TWO external CUSUM monitors on the same error stream, at
the same tolerance and the same threshold, differing only in p_0:

  nominal   `StrictCUSUM(0.05, DELTA_P, lambda)` built at `exp_R1_generate_data.py:56`, p_0 pinned
            to the historical literal 0.05 before the stream starts   -> column `tau_det_fixed`
  empirical `StrictCUSUM(p_pre_emp, DELTA_P, lambda)` built at `:81` at t == T_DRIFT, p_0 being the
            mean error over the 1000-step pre-drift warm-up           -> column `tau_det_emp`

Every published R1 aggregate is the EMPIRICAL arm, and the assertions below are therefore on that
arm: `Detection_Rate` is `tau_det_emp_finite` (`:120`), and `blind_spot_observed` (`:106-111`) is
defined on `tau_det_ext_emp` alone. Verified against the frozen artifact by recomputing the
generator's own blind-spot rule on each column: the stored flag reproduces the empirical arm exactly
and the nominal arm not at all. Figure 1 plots `tau_det_emp` for the same reason
(`exp_R1_plot_figure.py:37-40`).

The nominal arm is recorded in the artifact and read by nothing. At lambda = 25 it gives a
detection rate of 0.390 against the empirical arm's 0.920, and a blind-spot share of 0.965 against
0.895 -- a p_0 of 0.05 is far above the measured pre-drift error rate, so the nominal arm carries a
large extra slack and starves much earlier. Quoting 0.895 / 0.920 as nominal-arm figures would be a
factual error; the two arms are not interchangeable and this docstring exists so the next reader
cannot conflate them.

R2 has one arm only: `p_pre_empirical = np.mean(errors_pre)`
(`exp_R2_instrumented_blind_spot.py:90`), the same warm-up calibration, with the literal 0.05 reached
only if the warm-up buffer were empty -- which a 1000-step window makes unreachable.

Usage:  PYTHONHASHSEED=0 python -m pytest tests/test_R1_race_condition.py -v
"""
from pathlib import Path

import pandas as pd
import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent
R1_PATH = ROOT_DIR / "results" / "R1_race_condition" / "data" / "R1_race_condition.parquet"

LAMBDAS = [2.5, 5.0, 10.0, 15.0, 20.0, 25.0, 50.0, 100.0]
N_SEEDS = 200


def _read(path, **kw):
    if not path.exists():
        pytest.skip(f"artifact absent -- run ./run_experiment_R{path.parts[-3][1]}.sh")
    return pd.read_parquet(path) if path.suffix == ".parquet" else pd.read_csv(path, **kw)


def _per_lambda():
    """(share_blind_spot, detection_rate) per lambda, the two curves Figure 1 reports."""
    df = _read(R1_PATH)
    g = df.groupby("lambda_val").agg(share=("blind_spot_observed", "mean"),
                                     det=("tau_det_emp_finite", "mean"),
                                     n=("seed", "size"))
    return df, g


def test_shape_is_the_full_lambda_grid():
    df, g = _per_lambda()
    assert len(df) == len(LAMBDAS) * N_SEEDS, (
        f"{len(df)} rows, expected {len(LAMBDAS)} lambdas x {N_SEEDS} seeds")
    assert sorted(g.index) == LAMBDAS, f"lambda grid is {sorted(g.index)}, expected {LAMBDAS}"
    assert (g["n"] == N_SEEDS).all(), g["n"].to_string()


def test_blind_spot_share_and_detection_rate_at_lambda_25():
    _, g = _per_lambda()
    share, det = g.loc[25.0, "share"], g.loc[25.0, "det"]
    assert share == pytest.approx(0.895, abs=0.01), f"Share_Blind_Spot(25) = {share}, expected 0.895"
    assert det == pytest.approx(0.920, abs=0.01), f"Detection_Rate(25) = {det}, expected 0.920"


def test_regime_ordering_across_the_lambda_grid():
    """Detector-wins at low lambda, total starvation at high lambda."""
    _, g = _per_lambda()
    low = {lam: g.loc[lam, "share"] for lam in (2.5, 5.0, 10.0)}
    assert all(v < 0.10 for v in low.values()), f"low-lambda blind-spot share not < 0.10: {low}"
    high = {lam: g.loc[lam, "share"] for lam in (50.0, 100.0)}
    assert all(v == 1.0 for v in high.values()), f"high-lambda blind-spot share not 1.00: {high}"


def test_lambda_star_is_bracketed_by_the_extended_grid():
    """Action G2 added lambda = 15 and 20 so the transition band is measured, not interpolated."""
    _, g = _per_lambda()
    s15, s20, s25 = (g.loc[lam, "share"] for lam in (15.0, 20.0, 25.0))
    assert s15 < s20 < s25, f"blind-spot share not monotone across 15 < 20 < 25: {s15}, {s20}, {s25}"
