"""Statutory guard-rail of stream S3: one guard per published numerical statement.

The stream replaces an EQUALITY resting on an undemonstrated conditional independence by a
two-sided distribution-free envelope, and it publishes a refutation rather than a repair: the
substitution `F = F_HAT` that `prop:starvation_boundary` made silently is measured false on 10 of
the 80 testable cells. Every assertion below is written so that a later change which silently
REPAIRS the refutation fails the suite instead of passing it -- an exact census, not an inequality.

Three input classes:

1. DEGENERATE. `F = 0`, `F = 1`, `M = 1`, the saturated region `M F >= 1`, a level beyond the
   censoring horizon, and the `k = 0` / `k = n` ends of the Wilson interval. At `M = 1` the two
   bounds COINCIDE -- a test finding one strictly tighter there is testing a bug, not a bound.
2. ADVERSARIAL. Reviewer #3's objection as arithmetic: an exchangeable pair with
   `Corr = +0.51` that VIOLATES the independence bound. A future edit restoring "positive
   correlation suffices" fails here.
3. PUBLISHED NUMERALS. Every number that reaches `docs/theory/S3_*.md`,
   `docs/manuscript/sections/dependence_v2.tex` or the S3 zone of the manuscript of record, read
   back from `results/S3/` and from the committed upstream artifacts.

Usage:  PYTHONHASHSEED=0 python -m pytest tests/test_S3_dependence.py -v
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "S3_dependence"))
from config import experiment_ssot as ssot  # noqa: E402
import s3_bounds as sb  # noqa: E402
import s3_competing_risks as cr  # noqa: E402

S3 = ROOT_DIR / "results" / "S3"
MANUSCRIPT = ROOT_DIR / "docs" / "manuscript" / (
    ROOT_DIR / "docs" / "manuscript" / "CURRENT").read_text(encoding="utf-8").strip()

# Published censuses. Exact, because they ARE the result.
N_TESTABLE_CELLS = 80
N_BOOLE_REFUTED = 10
N_JENSEN_REFUTED = 11
N_KS_MAGNITUDES = 20
KS_P_MAX = 0.0030
D4_N_AGREE = 13
CANON_MEFF_LO, CANON_MEFF_HI = 6.99, 9.16


def artifact(name):
    path = S3 / name
    if not path.is_file():
        pytest.skip(f"{path.relative_to(ROOT_DIR)} absent; run the S3 scripts first")
    return path


def verdicts():
    return json.loads(artifact("s3_verdicts.json").read_text(encoding="utf-8"))


# ─────────────────────────────────────────────────────────────────────────────
# 1. Degenerate inputs
# ─────────────────────────────────────────────────────────────────────────────

def test_bounds_at_the_two_ends_of_F():
    """F = 0 and F = 1 are the only points where both bounds are forced, at every M."""
    for m in (1, 2, 10, 50):
        assert sb.boole(0.0, m) == 0.0 and sb.jensen(0.0, m) == 0.0
        assert sb.boole(1.0, m) == 1.0 and sb.jensen(1.0, m) == 1.0
    assert sb.mcrit_from_F(0.0, 0.95) == np.inf     # nothing adapts: no ensemble is too large
    assert sb.mcrit_from_F(1.0, 0.95) == 0.0        # one tree already starves the monitor


def test_the_two_bounds_coincide_at_M_equals_one():
    """They are not two bounds at M = 1; they are one. An ordering found here is a defect."""
    for f in (0.0, 0.02, 0.49, 0.7, 1.0):
        assert abs(sb.boole(f, 1) - sb.jensen(f, 1)) < 1e-15
        assert abs(sb.boole(f, 1) - f) < 1e-15


def test_boole_is_the_looser_bound_and_saturates_constant_in_M():
    """Above M F >= 1 the envelope does not depend on M: this is why the M_crit inversion is gone."""
    for f in (0.02, 0.15, 0.49):
        for m in (2, 3, 5, 10):
            assert sb.boole(f, m) >= sb.jensen(f, m) - 1e-15
    f = 0.49
    saturated = [sb.boole(f, m) for m in (3, 10, 20, 50)]      # 3 * 0.49 > 1
    assert saturated == [1.0, 1.0, 1.0, 1.0]
    assert len(set(saturated)) == 1, "a saturated Boole bound that moves with M is not Boole"


def test_empirical_cdf_keeps_censored_runs_in_the_denominator_and_refuses_the_horizon():
    tau = np.array([1.0, 2.0, np.nan, 4.0])
    assert sb.cdf_censored(tau, 2.0, 4000) == 0.5
    assert sb.cdf_censored(tau, 4.0, 4000) == 0.75
    with pytest.raises(ValueError):
        sb.cdf_censored(tau, float(ssot.CENSORING_HORIZON), ssot.CENSORING_HORIZON)


def test_wilson_interval_is_exact_at_the_two_ends():
    """A Wald interval degenerates to a point at k = 0 and k = n, and would declare a refutation
    that is a sampling artifact."""
    assert sb.wilson(0, 100)[0] < 1e-12 and sb.wilson(0, 100)[1] > 0.0
    assert sb.wilson(100, 100)[1] > 1.0 - 1e-12 and sb.wilson(100, 100)[0] < 1.0
    assert all(np.isnan(x) for x in sb.wilson(0, 0))


def test_restricted_time_and_the_race_coding():
    """A NaN tau_det is the monitor LOSING, never a censored unit: tau_ARF is observed on every
    run. Coding it as censored would discard the blind-spot events, which are the phenomenon."""
    assert np.array_equal(cr.restricted(np.array([10.0, np.nan]), 100), np.array([10.0, 100.0]))
    t, cause = cr.race(np.array([10.0, 10.0, 10.0]), np.array([np.nan, 5.0, 10.0]), 100)
    assert list(cause) == [1, 2, 2] and list(t) == [10.0, 5.0, 10.0]


def test_order_statistic_integrals_move_in_the_right_direction():
    s = np.array([1.0, 3.0, 8.0, 20.0])
    assert abs(cr.e_min_from_cdf(s, 1, 100) - s.mean()) < 1e-9
    assert abs(cr.e_max_from_cdf(s, 1, 100) - s.mean()) < 1e-9
    assert cr.e_min_from_cdf(s, 10, 100) < cr.e_min_from_cdf(s, 2, 100) < cr.e_min_from_cdf(s, 1, 100)
    assert cr.e_max_from_cdf(s, 10, 100) > cr.e_max_from_cdf(s, 2, 100) > cr.e_max_from_cdf(s, 1, 100)


# ─────────────────────────────────────────────────────────────────────────────
# 2. Adversarial: reviewer #3's objection
# ─────────────────────────────────────────────────────────────────────────────

def test_positive_correlation_does_not_license_the_independence_bound():
    """Exchangeable, Corr(tau_1, tau_2) = +0.51, and the bound 1 - (1-F)^M is VIOLATED at s = 2.

    What the bound needs is positive ASSOCIATION of the indicators at the level s, i.e.
    P(A_i and A_j) >= F(s)^2, which Pearson correlation of the delays does not deliver. The
    distribution-free envelope survives the same law, which is why it is the one that carries the
    published claim."""
    support = [(1.0, 100.0, 0.3), (100.0, 1.0, 0.3), (2.0, 2.0, 0.2), (200.0, 200.0, 0.2)]
    e1 = sum(p * a for a, _, p in support)
    cov = sum(p * a * b for a, b, p in support) - e1 * e1
    var = sum(p * a * a for a, _, p in support) - e1 * e1
    f = sum(p for a, _, p in support if a <= 2.0)
    joint = sum(p for a, b, p in support if a <= 2.0 and b <= 2.0)
    p_min = sum(p for a, b, p in support if min(a, b) <= 2.0)

    assert cov > 0 and abs(cov / var - 0.5102) < 1e-4      # positively correlated
    assert joint < f * f                                    # negatively ASSOCIATED at s = 2
    assert p_min > sb.jensen(f, 2), "the counterexample no longer violates the independence bound"
    assert p_min <= sb.boole(f, 2), "the distribution-free envelope must survive it"


# ─────────────────────────────────────────────────────────────────────────────
# 3. Published numerals
# ─────────────────────────────────────────────────────────────────────────────

def test_D1_gate_verdict_is_the_one_the_stream_published():
    g = json.loads(artifact("rng_factorization.json").read_text(encoding="utf-8"))
    assert g["verdict"] == "DOES NOT FACTORISE"
    assert g["decision_variables"]["residue_ok"] is False
    assert g["decision_variables"]["n_shift"] > 0
    assert g["aliasing_all_trees_share_forest_rng"] is True
    assert g["vote_feedback_into_per_tree_learning"]["absent"] is True
    assert verdicts()["D2"]["carrying_bound"] == "boole"
    assert verdicts()["D5"]["branch"] == "b"


def test_the_lower_Frechet_bound_holds_on_every_measurable_cell():
    """F_hat <= P_miss is the half of the envelope the measurement does NOT refute; if it ever
    failed, the ARF would be adapting more slowly than a single tree."""
    grid = pd.read_csv(artifact("bounds_grid.csv"), float_precision="round_trip")
    cells = grid[grid.M == 10]
    assert len(cells) == N_TESTABLE_CELLS
    assert (cells.F_hat <= cells.measured_pmiss + 1e-12).all()


def test_the_plug_in_refutation_census_is_exact():
    """The published result is a COUNT, not an inequality. A change that silently repairs the
    refutation, or that widens it, fails here."""
    d7 = verdicts()["D7"]["grid"]
    assert d7["verdict"] == "BOUND REFUTED"
    assert d7["n_testable_cells"] == N_TESTABLE_CELLS
    assert d7["n_boole_refuted"] == N_BOOLE_REFUTED
    assert d7["n_jensen_refuted"] == N_JENSEN_REFUTED
    assert all(c["lambda"] <= 25.0 for c in d7["refuted_cells"]), \
        "the refutation is published as confined to lambda <= 25"


def test_the_left_tail_mechanism_of_the_refutation_reproduces():
    """At the canonical magnitude the fastest HAT run adapts at 33 and the fastest ARF run at 24,
    so F_HAT vanishes where the ARF has already adapted. This is the published mechanism."""
    hat, arf, shifts = sb.load()
    b = shifts[int(np.argmin(np.abs(sb.delta_e_of(shifts) - sb.CANONICAL_DELTA_E)))]
    tau_hat = hat.loc[hat.boundary_shift == b, "tau_hat"].to_numpy(float)
    tau_arf = arf.loc[arf.boundary_shift == b, "tau_arf"].to_numpy(float)
    s = sb.tau_det_star(8.0, float(sb.delta_e_of(b)))
    assert np.nanmin(tau_hat) == 33.0 and np.nanmin(tau_arf) == 24.0
    assert sb.cdf_censored(tau_hat, s, sb.HORIZON) == 0.0
    assert np.count_nonzero(tau_arf <= s) == 4


def test_pmiss_anchors_reproduce_under_D7():
    curve = pd.read_csv(artifact("pmiss_vs_M.csv"), float_precision="round_trip")
    anchors = verdicts()["D7"]["anchors_at_canonical_point"]
    assert anchors["M1"]["verdict"] == "IDENTITY HOLDS"
    assert anchors["M1"]["deviation"] <= sb.D7_IDENTITY_TOL
    assert anchors["M10"]["verdict"] == "BOUND HOLDS"
    assert anchors["M10"]["model_verdict"] == "REPRODUCES"
    assert anchors["M10"]["deviation"] <= sb.D7_ABS_TOL
    row = curve[curve.M == 10].iloc[0]
    assert float(row.bound_boole) >= float(row.measured_wilson_lo)
    assert list(curve.M) == sb.M_GRID
    assert (curve.carrying_bound == "boole").all()


def test_the_canonical_numerals_of_the_retracted_instantiation_still_reproduce():
    """The retraction is of the SUBSTITUTION, not of the arithmetic. The four numerals of the v63
    numerical example must keep reproducing, or the retraction would be resting on a broken read."""
    c = verdicts()["canonical_point"]
    assert abs(c["delta_e"] - 0.3268) < 1e-9
    assert abs(c["tau_det_star"] - 157.83) < 0.01
    assert abs(c["F_hat"] - 0.49) < 5e-3
    assert c["mcrit_from_jensen_r095"] == 0.0
    r9 = pd.read_csv(ROOT_DIR / "results/R9_mcrit/data/exp_R9_mcrit_comparison.csv",
                     float_precision="round_trip")
    ref = r9[(r9.delta_e == 0.33) & (r9["lambda"] == 50) & (r9.reliability_r == 0.95)].iloc[0]
    assert abs(float(ref.E_tau_HAT) - 463.15) < 0.01 and float(ref.Mcrit_emp) == 0.0


def test_D3_rmst_identity_and_the_committed_hydra_table():
    c = json.loads(artifact("s3_competing_risks.json").read_text(encoding="utf-8"))
    assert c["D3"]["n_cells"] == 40 and c["D3"]["verdict"] == "REPRODUCED"
    assert c["D3"]["worst_identity_deviation"] <= cr.D3_TOL
    assert c["D3"]["worst_deviation_from_committed_rmst"] == 0.0


def test_the_measured_race_is_the_one_published():
    c = json.loads(artifact("s3_competing_risks.json").read_text(encoding="utf-8"))
    cif = pd.read_csv(artifact("cif_bands.csv"), float_precision="round_trip")
    assert c["P3"]["censored_frac"] == 0.0, "the race must carry no censored unit"
    assert c["P3"]["detector_won_frac"]["A"] == 0.0, \
        "at lambda = 50 the monitor wins none of the 2000 runs; this is the published claim"
    a = cif[(cif.scenario == "A") & (cif.t == ssot.CENSORING_HORIZON)]
    assert len(a) == 20
    assert (a.cif_arf == 1.0).all() and (a.cif_arf_lo == 1.0).all() and (a.cif_det == 0.0).all()
    # non-monotone at lambda = 25: the monitor does best at INTERMEDIATE magnitudes
    b = cif[(cif.scenario == "B") & (cif.t == ssot.CENSORING_HORIZON)].sort_values("delta_e")
    assert b.detector_won_frac.max() == 0.32
    assert b.loc[b.detector_won_frac.idxmax(), "delta_e"] == 0.1409
    assert b.detector_won_frac.iloc[-1] < b.detector_won_frac.max()


def test_M_eff_is_published_as_an_interval_and_never_averaged():
    c = json.loads(artifact("s3_competing_risks.json").read_text(encoding="utf-8"))
    meff = pd.read_csv(artifact("rho_meff.csv"), float_precision="round_trip")
    assert c["D4"]["verdict"] == "DISAGREE" and c["D4"]["n_agree"] == D4_N_AGREE
    assert c["D4"]["factor"] == cr.D4_AGREEMENT_FACTOR
    row = meff[meff.delta_e == 0.3268].iloc[0]
    lo, hi = sorted((float(row.M_eff_direct), float(row.M_eff_moments)))
    assert abs(lo - CANON_MEFF_LO) < 0.01 and abs(hi - CANON_MEFF_HI) < 0.01
    assert meff.rho_hat_moments.abs().max() < 0.06, \
        "the measured within-run correlation is published as indistinguishable from zero"
    assert c["D4bis"]["verdict"].startswith("NOT PRODUCED")


def test_F22_exponentiality_is_rejected_at_every_magnitude():
    ks = pd.read_csv(artifact("ks_exponentiality.csv"), float_precision="round_trip")
    d6 = verdicts()["D6"]
    assert len(ks) == N_KS_MAGNITUDES and bool(ks.rejects_exponential_at_005.all())
    assert d6["n_rejecting_exponential"] == N_KS_MAGNITUDES
    assert abs(d6["p_max"] - KS_P_MAX) < 1e-9 and d6["p_max"] < 0.05
    assert d6["verdict"] == "L194 HALF GIVES"


def test_the_F22_shortfall_is_mostly_non_exponentiality_not_correlation():
    """`sec:hydra` attributes the departure from 10x to inter-tree correlation. Measured, the order
    statistics of F_hat alone already give 9.22x at the canonical magnitude against 7.99x observed,
    so the residual left for dependence AND for the marginal mismatch together is 0.87."""
    meff = pd.read_csv(artifact("rho_meff.csv"), float_precision="round_trip")
    row = meff[meff.delta_e == 0.3268].iloc[0]
    assert abs(float(row.accel_order_only) - 9.2249) < 1e-3
    assert abs(float(row.hydra_rmst_ratio) - 7.9909) < 1e-3
    assert abs(float(row.accel_residual_over_order) - 0.8662) < 1e-3
    assert float(row.accel_order_only) < ssot.N_MODELS, \
        "an order-statistic acceleration at or above M would make F effectively exponential"


# ─────────────────────────────────────────────────────────────────────────────
# 4. The manuscript zone reflects the verdicts
# ─────────────────────────────────────────────────────────────────────────────

def test_the_S3_zone_of_the_manuscript_carries_the_repaired_statement():
    src = MANUSCRIPT.read_text(encoding="utf-8")
    for label in ("prop:starvation_boundary", "eq:pmiss", "cor:mcrit", "eq:mcrit",
                  "sec:starvation_boundary"):
        assert f"\\label{{{label}}}" in src, f"{label} is referenced from outside the S3 perimeter"
    assert "\\tau_{\\mathrm{det}}^" not in src, \
        "tau_det* is removed from the reasoning; the race is a competing risk (P3)"
    assert r"P_{\mathrm{miss}}(s) \;\le\; \min\bigl(1,\, M\,F(s)\bigr)" in src, \
        "eq:pmiss must carry the two-sided envelope, not the v63 equality"
    assert "Correlation disclaimer" not in src
    assert "Retraction of the single-tree instantiation" in src
    # the four subsections CLAUDE.md excludes from the S3 perimeter are untouched by this stream
    assert "the $M$-fold acceleration is exact for exponential $F$" in src or \
           "The $M$-fold acceleration is exact for exponential $F$" in src


def test_the_companion_section_declares_only_environments_the_preamble_supplies():
    """`tests/test_manuscript_integrity.py` covers this for every section; asserted here too so a
    failure names dependence_v2.tex rather than the whole tree."""
    section = ROOT_DIR / "docs/manuscript/sections/dependence_v2.tex"
    assert section.is_file()
    src = section.read_text(encoding="utf-8")
    assert "\\documentclass" not in src, "a section fragment must not become a second main document"
    for label in ("prop:min_jensen", "prop:min_boole", "cor:disclaimer",
                  "res:plugin_refuted", "rem:mcrit_withdrawn", "res:cif", "res:meff"):
        assert f"\\label{{{label}}}" in src
