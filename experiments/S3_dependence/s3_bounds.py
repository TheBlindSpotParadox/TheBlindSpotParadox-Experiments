"""Stream S3 -- the two bounds on P_miss, the P_miss(M) curve, and the F22 exponentiality check.

`prop:starvation_boundary` states `P_miss = P(tau_ARF < tau_det*) = 1 - [1 - F(tau_det*)]^M` with an
EQUALITY, under a conditional independence that is never demonstrated. This module produces the two
bounds that replace it and evaluates both on committed artifacts:

  Jensen / exchangeability   P(min_i tau_i <= s) <= 1 - [1 - F(s)]^M     (needs D1 = FACTORISES)
  Boole                      P(min_i tau_i <= s) <= min(1, M F(s))       (any dependence structure)

Which of the two carries the published claim is fixed by rule D2 on the verdict of the D1 gate
(`results/S3/rng_factorization.json`), not by which is numerically tighter.

Estimator conventions, declared because they differ from R9's:

  * `F_hat(s)` counts censored runs in the DENOMINATOR, not out of the sample. Under a single
    administrative censoring at the common horizon t_c, a censored run is known to satisfy
    tau > t_c > s, so `#{tau <= s} / n_total` is the correct (and Kaplan--Meier-identical)
    estimate for s < t_c. `exp_R9_compute_mcrit.py` drops the censored runs, which inflates F at
    the four magnitudes that carry censoring; at the canonical point (Delta_e = 0.33) nothing is
    censored and the two conventions coincide, so the published numeral is unaffected.
  * `tau_ARF` is read from R2 scenario A. It is identical across scenarios A/B/C (asserted in
    `demo()`): the ARF's internal adaptation does not see the external threshold, so the same
    sample serves every lambda.

Outputs, all under `results/S3/`: `bounds_grid.csv`, `pmiss_vs_M.csv`, `ks_exponentiality.csv`,
`s3_verdicts.json`, `figures/Fig_S3_pmiss_vs_M.png`.
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats as stats

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))
from config import experiment_ssot as ssot  # noqa: E402

OUT_DIR = ROOT_DIR / "results" / "S3"
FIG_DIR = OUT_DIR / "figures"
R6_PARQUET = ROOT_DIR / "results/R6_hydra_factor/data/R6_hat_instrumented.parquet"
R2_PARQUET = ROOT_DIR / "results/R2_instrumented_blind_spot/data/R2_instrumented_A_PHT_ARF.parquet"
R9_CSV = ROOT_DIR / "results/R9_mcrit/data/exp_R9_mcrit_comparison.csv"
GATE_JSON = OUT_DIR / "rng_factorization.json"

DELTA_P = ssot.CUSUM_DELTA_P
HORIZON = ssot.CENSORING_HORIZON
LAMBDAS = sorted({float(x) for x in ssot.R9_LAMBDAS} | {float(x) for x in ssot.S6_AUDIT_LAMBDAS})
M_GRID = [1, 2, 3, 5, 10, 20, 50]       # closed by the plan; deliberately NOT a registry constant
OPERATIVE_DELTA_E = 0.24                # D8 grid: the band on which the manuscript claims the verdict persists
D8_BOUND_THRESHOLD = 0.5                # D8, declared before measurement
D7_ABS_TOL = 0.05                       # D7 model-fidelity tolerance at the M = 10 anchor
D7_IDENTITY_TOL = 1e-12                 # D7, the tautological M = 1 anchor
CANONICAL_DELTA_E = 0.33                # the manuscript's numerical example
CANONICAL_LAMBDA = 50.0
KS_N_BOOT = 2000                        # N of the bootstrap the manuscript reports


def delta_e_of(boundary_shift):
    """Delta_e = Phi(b / sqrt(2)) - 0.5, the R1/R2/R6/R9 boundary-shift map."""
    return stats.norm.cdf(np.asarray(boundary_shift, dtype=float) / np.sqrt(2.0)) - 0.5


def tau_det_star(lam, de):
    """The nominal accumulation time the v63 proposition races against. Kept only to index the grid
    on the same scalar the manuscript uses; P3 replaces it by the random tau_det."""
    return float(lam) / (float(de) - DELTA_P)


def cdf_censored(tau, s, horizon):
    """F_hat(s) = #{tau <= s} / n, censored runs kept in the denominator.

    Valid only for s < horizon: a censored run is then known to exceed s, so it is a legitimate
    'not yet adapted' observation rather than a missing one. Raises above the horizon instead of
    returning a silently biased number.
    """
    tau = np.asarray(tau, dtype=float)
    if not s < horizon:
        raise ValueError(f"F_hat requested at s = {s} >= horizon {horizon}: "
                         "censored runs are not orderable against s")
    return float(np.count_nonzero(tau <= s) / tau.size)


def wilson(k, n, alpha=0.05):
    """Wilson score interval for a binomial proportion; exact at k = 0 and k = n."""
    if n == 0:
        return (np.nan, np.nan)
    z = stats.norm.ppf(1.0 - alpha / 2.0)
    p, d = k / n, 1.0 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, centre - half), min(1.0, centre + half))


def boole(f, m):
    """Distribution-free: P(min <= s) <= min(1, M F(s)). Saturates at F >= 1/M."""
    return float(min(1.0, m * f))


def jensen(f, m):
    """Exchangeable + conditionally independent: P(min <= s) <= 1 - [1 - F(s)]^M."""
    return float(1.0 - (1.0 - f) ** m)


def mcrit_from_F(f, r):
    """M_crit = floor(ln r / ln(1 - F)), the inversion of the Jensen bound. Same conventions as
    `exp_R9_compute_mcrit.mcrit_from_F`: F <= 0 -> inf, F >= 1 -> 0."""
    if not np.isfinite(f):
        return np.nan
    if f <= 0.0:
        return np.inf
    if f >= 1.0:
        return 0.0
    return float(np.floor(np.log(r) / np.log(1.0 - f)))


def ks_bootstrap_expon(data, n_boot, seed_seq):
    """Lilliefors-style KS test of exponentiality: the rate is refitted on every replicate.

    Same statistic and same N as `exp_R9_compute_mcrit.ks_bootstrap_expon`; the generator is a
    locally spawned `SeedSequence` child instead of a per-magnitude integer seed, so no global
    state is touched.
    """
    rng = np.random.default_rng(seed_seq)
    n, mean_emp = len(data), float(np.mean(data))
    d_emp = float(stats.kstest(data, "expon", args=(0, mean_emp)).statistic)
    boot = np.empty(n_boot)
    for i in range(n_boot):
        sample = rng.exponential(scale=mean_emp, size=n)
        boot[i] = stats.kstest(sample, "expon", args=(0, float(np.mean(sample)))).statistic
    return d_emp, float(np.mean(boot >= d_emp))


def load():
    """The two committed samples, keyed on the shared boundary_shift grid."""
    hat = pd.read_parquet(R6_PARQUET)
    arf = pd.read_parquet(R2_PARQUET)
    shifts = np.sort(hat["boundary_shift"].unique())
    if not np.array_equal(shifts, np.sort(arf["boundary_shift"].unique())):
        raise ValueError("R6 and R2_A do not share the boundary_shift grid; the join key is broken")
    return hat, arf, shifts


def grid_table(hat, arf, shifts):
    """Both bounds at every (magnitude, lambda, M), with the two measurable anchors alongside."""
    rows = []
    for b in shifts:
        de = float(delta_e_of(b))
        tau_hat = hat.loc[hat.boundary_shift == b, "tau_hat"].to_numpy(dtype=float)
        tau_arf = arf.loc[arf.boundary_shift == b, "tau_arf"].to_numpy(dtype=float)
        cens_hat = float(np.count_nonzero(np.isnan(tau_hat)) / tau_hat.size)
        cens_arf = float(np.count_nonzero(np.isnan(tau_arf)) / tau_arf.size)
        min_hat = float(np.nanmin(tau_hat))
        min_arf = float(np.nanmin(tau_arf))
        for lam in LAMBDAS:
            s = tau_det_star(lam, de)
            if not s < HORIZON:
                continue
            f = cdf_censored(tau_hat, s, HORIZON)
            k_arf = int(np.count_nonzero(tau_arf <= s))
            p_arf = k_arf / tau_arf.size
            lo, hi = wilson(k_arf, tau_arf.size)
            for m in M_GRID:
                rows.append({
                    "boundary_shift": round(float(b), 6),
                    "delta_e": round(de, 4),
                    "lambda": lam,
                    "M": m,
                    "tau_det_star": round(s, 2),
                    "n_hat": int(tau_hat.size),
                    "censored_frac_hat": round(cens_hat, 4),
                    "F_hat": round(f, 4),
                    "bound_boole": round(boole(f, m), 6),
                    "bound_jensen": round(jensen(f, m), 6),
                    "measured_pmiss": round(p_arf, 4) if m == 10 else (
                        round(f, 4) if m == 1 else np.nan),
                    "measured_source": "R2_A tau_arf" if m == 10 else (
                        "R6 tau_hat (identity)" if m == 1 else ""),
                    "measured_n": int(tau_arf.size) if m == 10 else (
                        int(tau_hat.size) if m == 1 else 0),
                    "measured_wilson_lo": round(lo, 4) if m == 10 else np.nan,
                    "measured_wilson_hi": round(hi, 4) if m == 10 else np.nan,
                    "censored_frac_arf": round(cens_arf, 4),
                    "min_tau_hat": min_hat,
                    "min_tau_arf": min_arf,
                })
    return pd.DataFrame(rows)


def canonical_row(grid):
    """The magnitude and threshold of the manuscript's numerical example."""
    de = grid.loc[(grid.delta_e - CANONICAL_DELTA_E).abs().idxmin(), "delta_e"]
    return grid[(grid.delta_e == de) & (grid["lambda"] == CANONICAL_LAMBDA)].copy(), float(de)


def d7_grid(grid, carrier):
    """D7 applied to every measurable cell, not only to the canonical point.

    The `M = 1` rows are tautological by construction (the model there IS `F_hat` on the same
    sample), so the real test lives in the `M = 10` rows, where the model is built on R6 `tau_HAT`
    and the measurement comes from the independent R2 `tau_ARF` sample.
    """
    cells = grid[grid.M == 10].copy()
    lo = [wilson(int(round(p * n)), int(n))[0] for p, n in
          zip(cells.measured_pmiss, cells.measured_n)]
    cells["wilson_lo"] = np.round(lo, 6)
    cells["boole_refuted"] = cells.bound_boole < cells.wilson_lo
    cells["jensen_refuted"] = cells.bound_jensen < cells.wilson_lo
    cells["carrier_refuted"] = cells[f"bound_{carrier}"] < cells.wilson_lo
    offenders = cells[cells.carrier_refuted][
        ["delta_e", "lambda", "tau_det_star", "F_hat", f"bound_{carrier}", "measured_pmiss",
         "wilson_lo", "min_tau_hat", "min_tau_arf"]]
    return cells, offenders


def d7_anchors(curve):
    """D7: the tautological M = 1 identity, and the real test at M = 10."""
    carrier = curve.attrs["carrier"]
    out = {}
    for m in (1, 10):
        row = curve[curve.M == m].iloc[0]
        model = float(row["bound_jensen"])                    # the v63 model, monotone in M
        bound = float(row[f"bound_{carrier}"])
        measured = float(row["measured_pmiss"])
        entry = {"M": m, "model": model, "carrying_bound": bound, "measured": measured,
                 "measured_n": int(row["measured_n"])}
        if m == 1:
            entry["test"] = "identity (tautological: model at M=1 is F_hat on the same sample)"
            entry["deviation"] = abs(model - measured)
            entry["verdict"] = "IDENTITY HOLDS" if entry["deviation"] <= D7_IDENTITY_TOL \
                else "IDENTITY BROKEN"
        else:
            lo = float(row["measured_wilson_lo"])
            entry["measured_wilson"] = [lo, float(row["measured_wilson_hi"])]
            entry["bound_holds"] = bool(bound >= lo)
            entry["deviation"] = abs(model - measured)
            entry["model_verdict"] = "REPRODUCES" if entry["deviation"] <= D7_ABS_TOL else "DEPARTS"
            entry["verdict"] = "BOUND HOLDS" if entry["bound_holds"] else "BOUND REFUTED"
        out[f"M{m}"] = entry
    return out


def d8_verdict(grid, carrier, mcrit_branch):
    """D8: retained iff D5 = (a), or the carrying bound is <= 0.5 somewhere on the operative grid."""
    op = grid[(grid.delta_e >= OPERATIVE_DELTA_E) & (grid.M >= 2)]
    col = f"bound_{carrier}"
    best = float(op[col].min())
    where = op.loc[op[col].idxmin(), ["delta_e", "lambda", "M", "F_hat", col]].to_dict()
    informative = bool(best <= D8_BOUND_THRESHOLD)
    retained = bool(mcrit_branch == "a" or informative)
    return {
        "operative_grid": {"delta_e_min": OPERATIVE_DELTA_E, "lambdas": LAMBDAS, "M_min": 2,
                           "n_points": int(len(op))},
        "carrying_bound": carrier,
        "threshold": D8_BOUND_THRESHOLD,
        "best_bound_on_grid": round(best, 6),
        "best_bound_at": {k: (round(float(v), 6) if isinstance(v, float) else v)
                          for k, v in where.items()},
        "bound_informative_somewhere": informative,
        "mcrit_branch": mcrit_branch,
        "verdict": "REPAIRED / RETAINED" if retained else "WITHDRAWN",
    }


def ks_table(hat, shifts):
    """D6: the exponentiality of tau_HAT, re-verified rather than carried on the manuscript's word."""
    children = np.random.SeedSequence(ssot.SEED_SCHEME_SEEDSEQ_ENTROPY).spawn(len(shifts))
    rows = []
    for b, child in zip(shifts, children):
        tau = hat.loc[hat.boundary_shift == b, "tau_hat"].dropna().to_numpy(dtype=float)
        d_emp, p = ks_bootstrap_expon(tau, KS_N_BOOT, child)
        rows.append({"boundary_shift": round(float(b), 6),
                     "delta_e": round(float(delta_e_of(b)), 4),
                     "n_complete": int(tau.size),
                     "mean_tau_hat": round(float(np.mean(tau)), 2),
                     "ks_stat": round(d_emp, 6),
                     "p_bootstrap": round(p, 6),
                     "rejects_exponential_at_005": bool(p < 0.05)})
    return pd.DataFrame(rows)


def figure(curve, carrier, de, path):
    fig, ax = plt.subplots(figsize=(6.0, 4.0))
    ax.plot(curve.M, curve.bound_boole, "o-", color="#00748C",
            label=r"Boole $\min(1, M\hat{F})$" + (" (carrier)" if carrier == "boole" else ""))
    ax.plot(curve.M, curve.bound_jensen, "s--", color="#E08000",
            label=r"Jensen $1-(1-\hat{F})^M$" + (" (carrier)" if carrier == "jensen" else ""))
    meas = curve[curve.measured_pmiss.notna()]
    ax.errorbar(meas.M, meas.measured_pmiss,
                yerr=[meas.measured_pmiss - meas.measured_wilson_lo.fillna(meas.measured_pmiss),
                      meas.measured_wilson_hi.fillna(meas.measured_pmiss) - meas.measured_pmiss],
                fmt="D", color="#333333", capsize=3, label="measured anchors (Wilson 95 %)")
    ax.set_xscale("log")
    ax.set_xticks(curve.M)
    ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    ax.set_xlabel(r"ensemble size $M$")
    ax.set_ylabel(r"$P_{\mathrm{miss}}$")
    ax.set_ylim(-0.03, 1.03)
    ax.set_title(rf"$\Delta e = {de:.3f}$, $\lambda = {CANONICAL_LAMBDA:.0f}$, "
                 rf"$\hat{{F}}(\tau^*_{{\det}}) = {curve.F_hat.iloc[0]:.2f}$")
    ax.legend(fontsize=8, loc="lower right")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=200)
    plt.close(fig)


def demo():
    """Self-check: the invariants this module's conclusions rest on. Writes nothing."""
    assert boole(0.49, 10) == 1.0 and boole(0.0, 10) == 0.0
    assert abs(jensen(0.49, 10) - (1 - 0.51 ** 10)) < 1e-15
    assert jensen(0.0, 10) == 0.0 and jensen(1.0, 10) == 1.0
    # Boole dominates Jensen at M = 1 (they coincide) and is looser for M >= 2 at small F.
    assert abs(boole(0.3, 1) - jensen(0.3, 1)) < 1e-15
    assert boole(0.3, 3) >= jensen(0.3, 3)
    assert mcrit_from_F(0.49, 0.95) == 0.0 and mcrit_from_F(0.0, 0.95) == np.inf
    assert mcrit_from_F(1.0, 0.95) == 0.0
    # Reviewer #3's objection as arithmetic: an exchangeable, POSITIVELY correlated pair that
    # violates the independence bound. Positive correlation of the delays does not give positive
    # association of the indicators at a level, which is what the Jensen bound actually needs.
    support = [(1.0, 100.0, 0.3), (100.0, 1.0, 0.3), (2.0, 2.0, 0.2), (200.0, 200.0, 0.2)]
    e1 = sum(p_ * a for a, _, p_ in support)
    cov = sum(p_ * a * b for a, b, p_ in support) - e1 * e1
    var = sum(p_ * a * a for a, _, p_ in support) - e1 * e1
    f2 = sum(p_ for a, _, p_ in support if a <= 2.0)
    p_min = sum(p_ for a, b, p_ in support if min(a, b) <= 2.0)
    assert abs(cov / var - 0.5102) < 1e-4, cov / var
    assert abs(f2 - 0.5) < 1e-12 and abs(p_min - 0.8) < 1e-12
    assert p_min > jensen(f2, 2), (p_min, jensen(f2, 2))
    assert p_min <= boole(f2, 2)                      # Boole survives what Jensen does not
    assert wilson(0, 100)[0] < 1e-12 and wilson(100, 100)[1] > 1.0 - 1e-12
    tau = np.array([1.0, 2.0, np.nan, 4.0])
    assert cdf_censored(tau, 2.0, 4000) == 0.5        # the NaN stays in the denominator
    try:
        cdf_censored(tau, 4000.0, 4000)
    except ValueError:
        pass
    else:                                             # pragma: no cover
        raise AssertionError("F_hat above the horizon must raise")
    a = pd.read_parquet(R2_PARQUET)
    for tag in ("B", "C"):
        other = pd.read_parquet(R2_PARQUET.with_name(f"R2_instrumented_{tag}_PHT_ARF.parquet"))
        m = a.merge(other, on=["boundary_shift", "seed"], suffixes=("_a", f"_{tag.lower()}"))
        assert (m["tau_arf_a"] == m[f"tau_arf_{tag.lower()}"]).all(), \
            f"tau_arf differs between R2 scenarios A and {tag}: it is not lambda-free"
    # D0: the pre-read R9 numerals, re-derived from the artifact rather than trusted.
    r9 = pd.read_csv(R9_CSV, float_precision="round_trip")
    row = r9[(r9.delta_e == 0.33) & (r9["lambda"] == 50) & (r9.reliability_r == 0.95)].iloc[0]
    hat = pd.read_parquet(R6_PARQUET)
    b = hat.boundary_shift.unique()[np.argmin(np.abs(delta_e_of(hat.boundary_shift.unique()) - 0.33))]
    tau = hat.loc[hat.boundary_shift == b, "tau_hat"].to_numpy(dtype=float)
    s = tau_det_star(50.0, float(delta_e_of(b)))
    assert abs(s - float(row.tau_det_star)) < 0.01, (s, row.tau_det_star)
    assert abs(cdf_censored(tau, s, HORIZON) - float(row.F_emp)) < 5e-3
    assert abs(np.nanmean(tau) - float(row.E_tau_HAT)) < 0.01
    assert mcrit_from_F(float(row.F_emp), 0.95) == float(row.Mcrit_emp)
    print("[OK] s3_bounds self-check: bounds, censoring convention, tau_arf lambda-freedom, "
          "and the four pre-read R9 numerals all hold")


def main():
    if "--check" in sys.argv:
        demo()
        return 0

    gate = json.loads(GATE_JSON.read_text(encoding="utf-8"))
    factorises = gate["verdict"] == "FACTORISES"
    carrier = "jensen" if factorises else "boole"          # D2
    mcrit_branch = "a" if factorises else "b"              # D5

    hat, arf, shifts = load()
    grid = grid_table(hat, arf, shifts)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    grid.to_csv(OUT_DIR / "bounds_grid.csv", index=False)

    curve, de = canonical_row(grid)
    curve.attrs["carrier"] = carrier
    curve = curve[["M", "delta_e", "lambda", "tau_det_star", "F_hat", "bound_boole",
                   "bound_jensen", "measured_pmiss", "measured_source", "measured_n",
                   "measured_wilson_lo", "measured_wilson_hi"]].copy()
    curve["carrying_bound"] = carrier
    curve["model_v63_equality"] = curve.bound_jensen           # the retired `=` reading
    curve.to_csv(OUT_DIR / "pmiss_vs_M.csv", index=False)

    ks = ks_table(hat, shifts)
    ks.to_csv(OUT_DIR / "ks_exponentiality.csv", index=False)

    curve.attrs["carrier"] = carrier
    anchors = d7_anchors(curve)
    cells, offenders = d7_grid(grid, carrier)
    refuted_pairs = set(zip(offenders.delta_e, offenders["lambda"]))
    unrefuted = grid[~grid.set_index(["delta_e", "lambda"]).index.isin(refuted_pairs)]
    d8 = d8_verdict(grid, carrier, mcrit_branch)
    d8["as_written"] = d8["verdict"]
    d8["restricted"] = d8_verdict(unrefuted, carrier, mcrit_branch)
    d8["restricted_to_unrefuted_cells"] = d8["restricted"]["verdict"]
    d8["recorded_gap"] = (
        "the criterion fires on cells where the plug-in F_hat is refuted by the M = 10 "
        "measurement (D7). The rule was committed on the plug-in evaluation and is applied as "
        "committed; the restricted reading is reported beside it rather than substituted for it.")
    canon = curve[curve.M == 10].iloc[0]
    verdicts = {
        "D1": {"verdict": gate["verdict"],
               "residue_ok": gate["decision_variables"]["residue_ok"],
               "n_shift": gate["decision_variables"]["n_shift"]},
        "D2": {"carrying_bound": carrier,
               "reason": "D1 = " + gate["verdict"] + "; rule D2 keys the carrier to D1, "
                         "never to which bound is tighter"},
        "D5": {"branch": mcrit_branch,
               "verdict": "RECONSTRUCTION" if mcrit_branch == "a" else "WITHDRAWAL",
               "boole_saturates_from_F": round(1.0 / 10.0, 4),
               "mcrit_inversion_available": bool(mcrit_branch == "a")},
        "D6": {"n_magnitudes": int(len(ks)),
               "n_rejecting_exponential": int(ks.rejects_exponential_at_005.sum()),
               "p_max": float(ks.p_bootstrap.max()),
               "verdict": "L194 HALF GIVES" if bool(ks.rejects_exponential_at_005.all())
                          else "L372 HALF GIVES",
               "n_boot": KS_N_BOOT,
               "seed_source": "np.random.SeedSequence(ssot.SEED_SCHEME_SEEDSEQ_ENTROPY).spawn"},
        "D7": {
            "anchors_at_canonical_point": anchors,
            "grid": {
                "n_testable_cells": int(len(cells)),
                "n_carrier_refuted": int(cells.carrier_refuted.sum()),
                "n_boole_refuted": int(cells.boole_refuted.sum()),
                "n_jensen_refuted": int(cells.jensen_refuted.sum()),
                "verdict": "BOUND REFUTED" if bool(cells.carrier_refuted.any()) else "BOUND HOLDS",
                "refuted_cells": json.loads(offenders.to_json(orient="records")),
                "mechanism": (
                    "Boole and Jensen are statements about the marginal F of a tree INSIDE the "
                    "ARF. No committed artifact carries that marginal, so both are evaluated with "
                    "the plug-in F = F_HAT, the assimilation the manuscript makes silently at "
                    "prop:starvation_boundary. The refutation is of that SUBSTITUTION, not of "
                    "either inequality: the ARF member's left tail is strictly faster than any "
                    "HAT run, so F_HAT(s) = 0 where the ARF has already adapted in a measurable "
                    "fraction of runs. No F_hat, no s and no M is adjusted to recover the bound."),
            },
        },
        "D8": d8,
        "canonical_point": {
            "delta_e": float(de), "lambda": CANONICAL_LAMBDA,
            "tau_det_star": float(canon.tau_det_star), "F_hat": float(canon.F_hat),
            "boole_M10": float(canon.bound_boole), "jensen_M10": float(canon.bound_jensen),
            "measured_M10": float(canon.measured_pmiss),
            "mcrit_from_jensen_r095": mcrit_from_F(float(canon.F_hat), 0.95)},
        "estimator_conventions": {
            "F_hat": "#{tau <= s} / n_total, censored runs kept in the denominator (s < t_c)",
            "horizon": HORIZON,
            "delta_P": DELTA_P,
            "tau_arf_source": "R2 scenario A; identical to scenarios B and C (asserted in demo())"},
    }
    (OUT_DIR / "s3_verdicts.json").write_text(
        json.dumps(verdicts, indent=2, sort_keys=True, default=float) + "\n", encoding="utf-8")

    figure(curve, carrier, de, FIG_DIR / "Fig_S3_pmiss_vs_M.png")

    print(f"[INFO] wrote {len(grid)} grid rows, {len(curve)} curve rows, {len(ks)} KS rows")
    print(f"\n=== D2 carrier = {carrier.upper()} (D1 {gate['verdict']}) ===")
    print(curve[["M", "F_hat", "bound_boole", "bound_jensen", "measured_pmiss"]].to_string(index=False))
    print(f"\nD5 branch ({mcrit_branch}): "
          f"{'RECONSTRUCTION' if mcrit_branch == 'a' else 'WITHDRAWAL'} of cor:mcrit")
    print(f"D6: {verdicts['D6']['n_rejecting_exponential']}/{len(ks)} magnitudes reject "
          f"exponentiality, p_max = {verdicts['D6']['p_max']:.4f} -> {verdicts['D6']['verdict']}")
    print(f"D7 M=1  {anchors['M1']['verdict']} (dev {anchors['M1']['deviation']:.2e})")
    print(f"D7 M=10 {anchors['M10']['verdict']} / model {anchors['M10']['model_verdict']} "
          f"(bound {anchors['M10']['carrying_bound']:.4f} vs measured "
          f"{anchors['M10']['measured']:.4f} {anchors['M10']['measured_wilson']})")
    print(f"D7 grid: {verdicts['D7']['grid']['verdict']} -- "
          f"{int(cells.carrier_refuted.sum())}/{len(cells)} testable M=10 cells refute the "
          f"plug-in F = F_HAT (Boole {int(cells.boole_refuted.sum())}, "
          f"Jensen {int(cells.jensen_refuted.sum())})")
    if len(offenders):
        print(offenders.to_string(index=False))
    print(f"D8: {d8['verdict']} (restricted reading: {d8['restricted_to_unrefuted_cells']} at "
          f"{d8['restricted']['best_bound_at']}) "
          f"-- best carrying bound on the operative grid "
          f"{d8['best_bound_on_grid']:.4f} at {d8['best_bound_at']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
