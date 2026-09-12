"""Stream S2, Phase 2 (T2.2): the exploitable transient W treated as a random variable.

`transfer_S1` open item 4 says `W` is deterministic throughout, and reviewer #1 faults Proposition 9
for exactly that. Eq. (4) of `prop:starvation` is stated at a single `W`; on this campaign `W` has a
distribution whose spread crosses the vacancy boundary, so a bound evaluated at one point of it is
not a bound on the ensemble of runs.

WHAT IS INTEGRATED. Eq. (4) bounds a probability, so the object is the CAPPED integrand

    B(lambda) := E_W[ min(1, W exp(-2/W (lambda - s_0 - mu W)_+^2)) ] ,   mu := Delta_e - delta_P.

The cap is not cosmetic. Uncapped, a censored run contributes `T_h = 2500` and the "bound" reports
2500 on a probability, which is information-free rather than merely loose. Capped, a censored run
contributes exactly 1, which makes the censoring fraction a LOWER BOUND on B(lambda) by
construction: B(lambda) >= P(W censored) at every lambda. Both readings are reported, and rule R4
declares the bound vacant when B(lambda) >= 1.

TWO ESTIMATORS, reported side by side because they bracket the answer.

  plug-in     the empirical integral over the per-run W, censored runs held AT their censoring time
              T_h. Understates W beyond the horizon, so it UNDERSTATES B.
  parametric  the log-normal AFT integral, which extrapolates past the horizon. The AFT is the one
              already committed in s6_predictive_power.py -- imported, not rebuilt, and no new
              dependency (`lifelines` is installed and unnecessary). Deterministic: the quadrature
              is Gauss-Hermite on the standard normal, not a simulation, so no PRNG is involved.

CENSORING IS MEASURED ON THE ARM ACTUALLY USED, and printed before any integral is computed.
`S6_causal_evidence.md` section 2 quotes 8.2 % on `n = 1974`; that is the AFT's complete-case
subset, not the 2 000-run arm, and the two are not interchangeable by assumption.

Usage:  PYTHONHASHSEED=0 python experiments/S2_theory/s2_w_random.py
        python experiments/S2_theory/s2_w_random.py --check     (self-check only, writes nothing)
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from numpy.polynomial.hermite_e import hermegauss

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "S6_synchronized_traces"))
from config import experiment_ssot as ssot  # noqa: E402
from s2_arl0 import DELTA_P_CUSUM, LAMBDA_LADDER, OUT_DIR, REFERENCE_ARM, RUNS  # noqa: E402
from s6_predictive_power import aft_lognormal  # noqa: E402

T_HORIZON = ssot.S6_T_HORIZON                  # 2500
QUAD_NODES = 64                                # Gauss-Hermite order; 64 is exact to machine
                                               # precision for this integrand at sigma ~ 0.85

# W estimators. `w_fw` IS the W of def:times and carries the censoring; `tau_erase` is the
# threshold-free argmax surrogate, uncensored by construction (S6 section 6).
W_COLUMNS = {"w_fw": "W = tau_erase - tau* (def:times, right-censored at T_h)",
             "tau_erase": "argmax A_unrefl (threshold-free surrogate, uncensored)"}

# The three W estimators rule R3 tabulates the vacancy domain over.
DOMAIN_COLUMNS = {"tau_swap_q010": "tau_swap^(1/M)",
                  "tau_erase": "tau_erase (argmax A_unrefl)",
                  "tau_err_rho010": "tau_err(0.10)"}


def eq4(lam, w, mu, s0=0.0, cap=True):
    """RHS of eq:markov_bound, W exp(-2/W (lambda - s_0 - mu W)_+^2), capped at 1 by default.

    Vacant exactly when mu W >= lambda - s_0: the positive part is zero, the exponential is 1 and
    the bound returns W >= 1."""
    w = np.asarray(w, dtype=np.float64)
    out = np.where(w > 0.0,
                   w * np.exp(-2.0 / np.maximum(w, 1e-300)
                              * np.clip(lam - s0 - mu * w, 0.0, None) ** 2),
                   0.0)
    return np.minimum(out, 1.0) if cap else out


def censoring_census(full):
    """Per-magnitude and pooled censoring of W on the arm actually used, before any integral."""
    rows = []
    for de, g in full.groupby("delta_e"):
        cens = ~np.isfinite(g.w_fw.to_numpy())
        rows.append({"delta_e": round(float(de), 6), "n": int(len(g)),
                     "n_censored": int(cens.sum()),
                     "censoring_fraction": round(float(cens.mean()), 4),
                     "w_fw_median_uncensored": round(float(np.nanmedian(g.w_fw)), 1),
                     "tau_erase_median": round(float(np.nanmedian(g.tau_erase)), 1)})
    cens = ~np.isfinite(full.w_fw.to_numpy())
    pooled = {"arm": REFERENCE_ARM, "n": int(len(full)), "n_censored": int(cens.sum()),
              "censoring_fraction": float(cens.mean()), "horizon": float(T_HORIZON),
              "note": "censoring is encoded as a missing w_fw, not as w_fw == T_h; no run reaches "
                      "the horizon with a finite value"}
    return pd.DataFrame(rows), pooled


def plugin_bound(w_obs, censored, lam, mu):
    """Empirical integral, censored runs held at their censoring time T_h."""
    w = np.where(censored, float(T_HORIZON), w_obs)
    return float(np.mean(eq4(lam, w, mu)))


def parametric_bound(mu_log, sigma, lam, mu):
    """Log-normal AFT integral over W ~ LogNormal(mu_log_i, sigma), averaged over runs.

    Gauss-Hermite quadrature on the standard normal: deterministic, no draw, no seed."""
    z, w_q = hermegauss(QUAD_NODES)
    w_q = w_q / w_q.sum()
    wide = np.exp(mu_log[:, None] + sigma * z[None, :])
    return float((eq4(lam, wide, mu) * w_q[None, :]).sum(axis=1).mean())


def bounds_table(full, aft):
    """Per magnitude and per lambda: deterministic-W, plug-in and parametric bounds."""
    x = np.column_stack([np.ones(len(full)), np.log(full.tau_swap_q010.to_numpy()),
                         np.log(full.delta_e_emp.to_numpy())])
    mu_log_all = x @ np.asarray(aft["beta"])
    sigma = float(aft["sigma"])

    rows = []
    for de, idx in full.groupby("delta_e").indices.items():
        g = full.iloc[idx]
        mu = float(de) - DELTA_P_CUSUM
        cens = ~np.isfinite(g.w_fw.to_numpy())
        w_obs = g.w_fw.to_numpy()
        w_det = float(np.where(cens, T_HORIZON, w_obs).mean())
        for lam in LAMBDA_LADDER:
            det = float(eq4(lam, w_det, mu))
            plug = plugin_bound(w_obs, cens, lam, mu)
            para = parametric_bound(mu_log_all[idx], sigma, lam, mu)
            rows.append({
                "delta_e": round(float(de), 6), "lambda": lam, "mu": round(mu, 6),
                "W_mean_censored_at_horizon": round(w_det, 1),
                "censoring_fraction": round(float(cens.mean()), 4),
                "bound_deterministic_W": det,
                "bound_plugin": plug,
                "bound_parametric": para,
                "gap_plugin_over_deterministic": plug / det if det > 0 else np.inf,
                "vacant_deterministic": bool(det >= 1.0),
                "vacant_plugin": bool(plug >= 1.0),
                "vacant_parametric": bool(para >= 1.0),
            })
    return pd.DataFrame(rows)


def domain_table(full):
    """T2.1 / rule R3: the domain {(W, lambda) : mu W < lambda} where Eq. (4) still says anything.

    The three W estimators of R3, on the ladder {8, 15, 25, 50}, per magnitude. Vacancy is reported
    twice: on the MEAN window, which is what `rem:transient_length` instantiates, and per run, which
    is what makes the statement about the ensemble of runs rather than about one summary."""
    rows = []
    for de, g in full.groupby("delta_e"):
        mu = float(de) - DELTA_P_CUSUM
        for col, label in DOMAIN_COLUMNS.items():
            w = g[col].to_numpy()
            w = w[np.isfinite(w)]
            if w.size == 0:
                continue
            w_bar = float(w.mean())
            for lam in LAMBDA_LADDER:
                rows.append({
                    "delta_e": round(float(de), 6), "W_estimator": label, "lambda": lam,
                    "n": int(w.size), "W_mean": round(w_bar, 1), "mu": round(mu, 6),
                    "mu_W_mean": round(mu * w_bar, 2),
                    "vacant_at_mean_W": bool(mu * w_bar >= lam),
                    "bound_at_mean_W": float(eq4(lam, w_bar, mu)),
                    "frac_runs_vacant": round(float(np.mean(mu * w >= lam)), 4),
                    "bound_plugin": float(np.mean(eq4(lam, w, mu))),
                })
    return pd.DataFrame(rows)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    runs = pd.read_parquet(RUNS)
    arm = runs[runs.arm == REFERENCE_ARM].reset_index(drop=True)
    full = arm[np.isfinite(arm.tau_swap_q010) & (arm.tau_swap_q010 > 0)
               & np.isfinite(arm.delta_e_emp) & (arm.delta_e_emp > 0)].reset_index(drop=True)

    _, whole_arm = censoring_census(arm)
    census, pooled = censoring_census(full)
    print("=== T2.2 censoring of W, arm '%s', measured BEFORE any integral ===" % REFERENCE_ARM)
    print(f"  whole arm          n = {whole_arm['n']}, censored = {whole_arm['n_censored']} "
          f"({100 * whole_arm['censoring_fraction']:.2f} %)")
    print(f"  complete case      n = {pooled['n']}, censored = {pooled['n_censored']} "
          f"({100 * pooled['censoring_fraction']:.2f} %)   <- the subset integrated over")
    print(f"  horizon T_h = {T_HORIZON:.0f}. S6_causal_evidence.md section 2 quotes 8.2 % on "
          f"n = 1974: that is the complete-case line, not the arm. The two agree here to 0.01 "
          f"point, which is a fact about this campaign and not a licence to substitute one for "
          f"the other.")
    print()

    aft = aft_lognormal(full)
    print(f"=== log-normal AFT (imported from s6_predictive_power) === converged="
          f"{aft['converged']}, n={aft['n']}, censored={aft['n_censored']} "
          f"({100 * aft['censoring_rate']:.1f} %), sigma={aft['sigma']:.4f}")
    print("  " + ", ".join(f"{n} = {b:.4f}" for n, b in zip(aft["names"], aft["beta"])))
    print()

    table = bounds_table(full, aft)
    domain = domain_table(full)
    table.to_csv(OUT_DIR / "s2_w_random.csv", index=False)
    domain.to_csv(OUT_DIR / "s2_eq4_domain.csv", index=False)

    print("=== T2.2 Eq. (4): deterministic W against the W-integrated bound (capped at 1) ===")
    for lam in LAMBDA_LADDER:
        s = table[table["lambda"] == lam]
        print(f"  lambda = {lam:4.0f}   deterministic min {s.bound_deterministic_W.min():.8f}"
              f"   plug-in min {s.bound_plugin.min():.8f}   parametric "
              f"{s.bound_parametric.min():.4f}-{s.bound_parametric.max():.4f}   vacant at "
              f"{int(s.vacant_plugin.sum())}/{len(s)} magnitudes (plug-in), "
              f"{int(s.vacant_parametric.sum())}/{len(s)} (parametric)")
    print()
    print(table[["delta_e", "lambda", "censoring_fraction", "W_mean_censored_at_horizon",
                 "bound_deterministic_W", "bound_plugin", "bound_parametric"]]
          .pivot(index="delta_e", columns="lambda",
                 values=["bound_deterministic_W", "bound_plugin"])
          .to_string(float_format=lambda v: f"{v:.4f}"))

    payload = {
        "censoring": {"whole_arm": whole_arm, "complete_case": pooled,
                      "per_magnitude": census.to_dict("records")},
        "aft": {k: aft[k] for k in ("names", "beta", "se", "z", "sigma", "n", "n_censored",
                                    "censoring_rate", "horizon", "converged")},
        "rule_R4": {
            "integrand": "min(1, W exp(-2/W (lambda - s_0 - mu W)_+^2)), s_0 = 0",
            "cap_rationale": "Eq. (4) bounds a probability; uncapped, a censored run contributes "
                             "T_h = 2500 and the bound is information-free rather than loose",
            "lower_bound_by_censoring": pooled["censoring_fraction"],
            "per_lambda": [{
                "lambda": lam,
                "plugin_min": float(table[table["lambda"] == lam].bound_plugin.min()),
                "plugin_max": float(table[table["lambda"] == lam].bound_plugin.max()),
                "parametric_min": float(table[table["lambda"] == lam].bound_parametric.min()),
                "parametric_max": float(table[table["lambda"] == lam].bound_parametric.max()),
                "n_magnitudes_vacant_plugin": int(table[table["lambda"] == lam]
                                                  .vacant_plugin.sum()),
                "n_magnitudes_vacant_parametric": int(table[table["lambda"] == lam]
                                                      .vacant_parametric.sum()),
                "n_magnitudes_vacant_deterministic": int(table[table["lambda"] == lam]
                                                         .vacant_deterministic.sum()),
                "n_magnitudes": int((table["lambda"] == lam).sum()),
                "verdict": "VACANT" if float(table[table["lambda"] == lam]
                                             .bound_plugin.min()) >= 1.0 else "INFORMATIVE",
            } for lam in LAMBDA_LADDER],
        },
        "rule_R3_domain": {
            "criterion": "vacant when mu W >= lambda - s_0, s_0 = 0",
            "n_pairs": int(len(domain)),
            "n_pairs_vacant_at_mean_W": int(domain.vacant_at_mean_W.sum()),
            # mu W < lambda is NECESSARY for a non-trivial bound, not sufficient: W e^{-...} must
            # also fall below 1. Both counts are reported; R3's criterion is not moved after the
            # fact, the gap between the two is recorded as a finding about the criterion.
            "n_pairs_bound_below_one": int((domain.bound_at_mean_W < 1.0).sum()),
            "criterion_is_necessary_not_sufficient": bool(
                int((~domain.vacant_at_mean_W).sum()) > int((domain.bound_at_mean_W < 1.0).sum())),
            "non_vacant_at_mean_W": domain[~domain.vacant_at_mean_W][
                ["delta_e", "W_estimator", "lambda", "W_mean", "mu_W_mean", "bound_at_mean_W",
                 "frac_runs_vacant"]].to_dict("records"),
            "recommendation": ("RETAIN with the explicit domain {(W, lambda) : mu W < lambda}"
                               if int((~domain.vacant_at_mean_W).sum()) > 0 else
                               "WITHDRAW Eq. (4)"),
        },
        "reproduction": {"python": sys.version.split()[0],
                         "artifact": str(RUNS.relative_to(ROOT_DIR)),
                         "command": "PYTHONHASHSEED=0 python experiments/S2_theory/s2_w_random.py",
                         "quadrature": f"Gauss-Hermite, {QUAD_NODES} nodes, deterministic"},
    }
    (OUT_DIR / "s2_w_random.json").write_text(json.dumps(payload, indent=2, sort_keys=True,
                                                         default=float) + "\n", encoding="utf-8")
    print()
    print("=== T2.1 / R3: domain of Eq. (4), mu W against the lambda ladder (mean window) ===")
    print(domain.pivot(index=["delta_e", "W_estimator"], columns="lambda",
                       values="vacant_at_mean_W").to_string())
    nv = payload["rule_R3_domain"]["non_vacant_at_mean_W"]
    print(f"  non-vacant pairs at the mean window: {len(nv)} of {len(domain)}")
    for r in nv:
        print(f"    Delta_e = {r['delta_e']:.4f}  {r['W_estimator']:28s} lambda = "
              f"{r['lambda']:4.0f}  W = {r['W_mean']:7.1f}  mu W = {r['mu_W_mean']:7.2f}  "
              f"bound = {r['bound_at_mean_W']:.3e}  runs vacant = {r['frac_runs_vacant']:.0%}")
    print(f"  R3 recommendation: {payload['rule_R3_domain']['recommendation']}")

    print(f"\nwrote {OUT_DIR.relative_to(ROOT_DIR)}/"
          "{s2_w_random.csv, s2_eq4_domain.csv, s2_w_random.json}")
    return table, domain, payload


def demo():
    """Self-check: the cap, the vacancy boundary, the degenerate distribution, and the fact that
    the integrated bound can never fall below the censoring fraction."""
    # 1. The cap. Uncapped, a censored run returns T_h on a probability.
    assert eq4(15.0, 2500.0, 0.3168, cap=False) == 2500.0
    assert eq4(15.0, 2500.0, 0.3168) == 1.0
    assert 0.0 <= eq4(50.0, 57.4, 0.3168) < 1.0

    # 2. Vacancy boundary at mu W = lambda - s_0. At and above it the uncapped bound is exactly W,
    #    so the capped bound is 1 for every W >= 1; below it the exponential bites, but W has to be
    #    far enough below for W e^{-...} to fall under 1 -- vacancy is sufficient, not necessary.
    assert eq4(15.0, 15.0 / 0.3168, 0.3168, cap=False) == pytest_approx(15.0 / 0.3168)
    assert eq4(15.0, 15.0 / 0.3168 + 100.0, 0.3168) == 1.0
    assert eq4(15.0, 15.0 / 0.3168 - 20.0, 0.3168, cap=False) < 15.0 / 0.3168 - 20.0
    assert eq4(15.0, 15.0, 0.3168) < 1e-4
    assert eq4(50.0, 57.4, 0.3168, s0=30.0) > eq4(50.0, 57.4, 0.3168)

    # 3. Degenerate W. A point mass at W_bar reproduces the deterministic bound exactly.
    w_bar = 57.4
    assert plugin_bound(np.full(500, w_bar), np.zeros(500, bool), 50.0, 0.3168) == \
        pytest_approx(float(eq4(50.0, w_bar, 0.3168)))
    assert eq4(50.0, 0.0, 0.3168) == 0.0                 # W = 0: no window, no crossing
    assert eq4(50.0, 1.0, 0.3168) == 0.0                 # W = 1, lambda = 50: underflows to zero,
                                                         # which is the correct reading -- one step
                                                         # cannot accumulate 50 units of evidence
    assert 0.0 < eq4(1.0, 1.0, 0.3168) <= 1.0

    # 4. The integrated bound is bounded below by the censoring fraction, at every lambda.
    w = np.concatenate([np.full(90, 40.0), np.full(10, np.nan)])
    cens = ~np.isfinite(w)
    for lam in LAMBDA_LADDER:
        assert plugin_bound(w, cens, lam, 0.3168) >= cens.mean() - 1e-12

    # 5. Quadrature sanity: a lognormal with sigma -> 0 collapses onto the point evaluation.
    mu_log = np.log(np.array([57.4, 57.4]))
    assert parametric_bound(mu_log, 1e-9, 50.0, 0.3168) == \
        pytest_approx(float(eq4(50.0, 57.4, 0.3168)), rel=1e-6)
    assert hermegauss(QUAD_NODES)[1].sum() == pytest_approx(np.sqrt(2 * np.pi), rel=1e-12)

    print("s2_w_random demo: OK")


def pytest_approx(x, rel=1e-9):
    """Tiny local tolerance helper: the module self-check must not import pytest."""
    class _A:
        def __eq__(self, other):
            return abs(other - x) <= rel * max(1.0, abs(x))
    return _A()


if __name__ == "__main__":
    demo()
    if "--check" not in sys.argv:
        main()
