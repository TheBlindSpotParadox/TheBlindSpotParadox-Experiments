# tests/test_R3_crossover.py
"""Non-regression test for Experiment R3 (regime crossover, Figure 3).

Specified by `results/audit_S7/regeneration_spec.md` G3 and implemented in stream S7-ter. Reads the
committed artifact only -- no re-run -- and skips with an explicit motive when it is absent.

This file was the measuring instrument of stream S7-ter LOT B, and it has taken its measurement.
Written against the pre-unification artifact, it reported exactly two failures after the re-run and
passed on everything else. The two are RESTATED below onto the unified arm, with the superseded
value kept beside each one.

WHICH ARM. The unification pins the ARF's warning_detector onto its drift_detector, moving two River
parameters (delta 0.01 -> 0.002, clock 32 -> c). The committed artifact is the UNIFIED arm; the
control arm under River's own defaults is archived at results/audit_S7/s7ter_arms/r3_u0/ and
reproduces the pre-S7-ter artifact byte for byte. The 15 HT rows and the 15 RF_Static rows are
identical under both arms -- neither model carries a warning detector -- so only the ARF assertions
below are arm-dependent, and they are marked as such.

The measurement is not a detail: starvation is STRONGER under River's defaults. Making the two
ADWINs identical clones means the warning never leads the drift and no background tree ever trains,
which attenuates the very effect the experiment measures. Which arm the manuscript publishes is
escalated, not decided here; see authorized_deviations.txt.

The specification's note that the accuracy gap assertion "will fail against the prose value ~24 pp"
is stale: the manuscript of record already reads 23.4 pp. The artifact gives 22.99 pp on the unified
arm and 23.41 pp on the control arm, so the prose value survives on both within half a point.

Usage:  PYTHONHASHSEED=0 python -m pytest tests/test_R3_crossover.py -v
"""
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent
R3_PATH = ROOT_DIR / "results" / "R3_regime_crossover" / "data" / "R3_regime_crossover_metrics.parquet"

PIPELINES = ["HT", "ARF", "RF_Static"]
N_MAGNITUDES = 15                 # linspace(0.02, 0.50, 15)
DE_MAX = 0.50
DE_BLIND_SPOT_ONSET = 0.26        # first grid point of the blind-spot band, .tex sec:crossover
DE_MONOTONE_FROM = 0.29           # the unified arm dips once at 0.29 before climbing; the
                                  # control arm is monotone from DE_BLIND_SPOT_ONSET
DE_MIN = 0.02


def _read(path, **kw):
    if not path.exists():
        pytest.skip(f"artifact absent -- run ./run_experiment_R{path.parts[-3][1]}.sh")
    return pd.read_parquet(path) if path.suffix == ".parquet" else pd.read_csv(path, **kw)


def _metrics():
    return _read(R3_PATH)


def _at(df, pipeline, delta_e, column):
    row = df[(df.pipeline == pipeline) & np.isclose(df.delta_e, delta_e)]
    assert len(row) == 1, f"{pipeline} at Delta_e = {delta_e}: {len(row)} rows"
    return float(row[column].iloc[0])


def test_shape_is_15_magnitudes_by_3_pipelines():
    df = _metrics()
    assert len(df) == N_MAGNITUDES * len(PIPELINES), (
        f"{len(df)} rows, expected {N_MAGNITUDES} x {len(PIPELINES)}")
    assert sorted(df.pipeline.unique()) == sorted(PIPELINES), sorted(df.pipeline.unique())


def test_ensemble_halves_the_pre_drift_false_alarms():
    """Safe-zone claim of sec:crossover: bagging acts as a stochastic filter on the CUSUM trajectory."""
    df = _metrics()
    fp = df.groupby("pipeline")["fp_mean"].mean()
    ratio = fp["HT"] / fp["ARF"]
    assert ratio == pytest.approx(2.0, abs=0.1), (
        f"fp(HT)/fp(ARF) = {ratio:.4f}, expected ~2.0 (halving claim)")
    ratio_rf = fp["HT"] / fp["RF_Static"]
    assert ratio_rf > 1.5, f"the static RF loses the noise-filtering benefit: fp ratio {ratio_rf:.2f}"


def test_starvation_dominates_the_adaptive_arm_at_the_top_of_the_grid():
    """ARM-DEPENDENT. 100.0 on the control arm (River defaults), 80.0 on the unified arm.

    The manuscript's "driving Missed Detections to 100%" is a control-arm statement and does not
    survive the unification; the qualitative claim -- the adaptive arm starves while both
    non-adaptive arms detect every drift -- survives on both."""
    df = _metrics()
    assert _at(df, "ARF", DE_MAX, "miss_mean") == 80.0, "ARF miss rate at Delta_e = 0.50 moved again"
    assert _at(df, "RF_Static", DE_MAX, "miss_mean") == 0.0, "the static RF misses a drift at Delta_e = 0.50"
    assert _at(df, "HT", DE_MAX, "miss_mean") == 0.0, "the HT misses a drift at Delta_e = 0.50"


def test_missed_detections_climb_monotonically_across_the_blind_spot_band():
    """ARM-DEPENDENT. `.tex` sec:crossover reads "from 1% at Delta_e = 0.26 to 100% at 0.50", which
    is the control arm. On the unified arm the band runs 4% -> 80% and its monotone stretch starts
    one grid point later, at 0.29: the onset reads 4, 2, 5, 13, 18, 39, 65, 80."""
    df = _metrics()
    band = (df[(df.pipeline == "ARF") & (df.delta_e >= DE_BLIND_SPOT_ONSET)]
            .sort_values("delta_e"))
    assert band.miss_mean.iloc[0] == pytest.approx(4.0, abs=0.5), (
        f"miss rate at the band onset is {band.miss_mean.iloc[0]}, expected 4% on the unified arm")
    assert band.miss_mean.iloc[-1] == 80.0
    mono = band[band.delta_e >= DE_MONOTONE_FROM]
    assert (np.diff(mono.miss_mean.values) >= -1e-12).all(), (
        "miss rate is not monotone over the stretch it is claimed for:\n"
        + mono[["delta_e", "miss_mean"]].to_string(index=False))


def test_weak_signal_zone_shows_the_HT_stochastic_resonance():
    """.tex sec:crossover: the HT's artefactual miss rate reaches 77% at the bottom of the grid."""
    df = _metrics()
    assert _at(df, "HT", DE_MIN, "miss_mean") == pytest.approx(77.0, abs=1.0)
    assert _at(df, "ARF", DE_MIN, "miss_mean") == 100.0


def test_monitoring_fidelity_costs_23_4_accuracy_points():
    """.tex sec:solution_rf and the (S2) fix of sec:discussion both quote this gap."""
    df = _metrics()
    gap_pp = 100.0 * (_at(df, "ARF", DE_MAX, "acc_mean") - _at(df, "RF_Static", DE_MAX, "acc_mean"))
    # 23.41 pp on the control arm, 22.99 on the unified one: the manuscript's 23.4 survives both
    # within half a point, which is the only reason this assertion is arm-independent.
    assert gap_pp == pytest.approx(23.2, abs=0.5), (
        f"post-drift accuracy gap ARF - RF at Delta_e = 0.50 is {gap_pp:.2f} pp")
    assert _at(df, "ARF", DE_MAX, "acc_mean") == pytest.approx(0.982, abs=0.005)
    assert _at(df, "RF_Static", DE_MAX, "acc_mean") == pytest.approx(0.750, abs=0.005)
