# exp_R6_hydra_survival.py
"""
exp_R6_hydra_survival.py
Experiment R6 (S7/F23): the Hydra acceleration factor under administrative censoring.

The published factor tau_HAT / tau_ARF (exp_R6_compute_hydra.py) is a COMPLETE-CASE ratio: runs
whose internal swap never occurs inside the post-drift window contribute NaN and are dropped. That
drop is informative -- it removes precisely the slowest adaptations -- so the complete-case ratio is
biased DOWNWARDS. Here the NaNs are treated as what they are: administrative censoring at the common
horizon t_c = N_STEPS - T_DRIFT = 4000 post-drift steps, identical for both arms, with no loss to
follow-up.

Inputs : results/R6_hydra_factor/data/R6_hat_instrumented.parquet          (tau_hat, M = 1)
         results/R2_instrumented_blind_spot/data/R2_instrumented_A_PHT_ARF.parquet (tau_arf, M = 10)
Outputs: results/audit_S7/hydra_survival.csv
         results/audit_S7/hydra_survival.tex   (old complete-case factor vs new RMST factor)
"""
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.stats import norm

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
R6 = ROOT_DIR / "results" / "R6_hydra_factor" / "data" / "R6_hat_instrumented.parquet"
R2 = ROOT_DIR / "results" / "R2_instrumented_blind_spot" / "data" / "R2_instrumented_A_PHT_ARF.parquet"
OUT_DIR = ROOT_DIR / "results" / "audit_S7"
OUT_DIR.mkdir(parents=True, exist_ok=True)

HORIZON = 4000          # N_STEPS - T_DRIFT: the single administrative censoring time, both arms
N_BOOT = 10000
BOOT_SEED = 20260906
RMST_TOL = 1e-9         # KM-vs-mean identity: structurally exact, float product accumulates ~1e-13
CENSORING_FREE = 0.01   # below this censored fraction the reference arm is effectively uncensored


def km_curve(time, observed):
    """Kaplan-Meier survival estimate. Returns (event_times, S at those times)."""
    ts = np.sort(np.unique(time[observed]))
    s, out = 1.0, []
    for ti in ts:
        at_risk = np.count_nonzero(time >= ti)
        d = np.count_nonzero((time == ti) & observed)
        s *= 1.0 - d / at_risk
        out.append(s)
    return ts, np.asarray(out)


def rmst(ts, surv, horizon):
    """Restricted mean survival time = integral of S over [0, horizon]."""
    edges = np.concatenate(([0.0], ts, [float(horizon)]))
    vals = np.concatenate(([1.0], surv))
    return float(np.sum(vals * np.clip(np.diff(edges), 0.0, None)))


def km_median(ts, surv):
    """Smallest event time with S <= 0.5; NaN when the curve never reaches 0.5."""
    hit = np.flatnonzero(surv <= 0.5)
    return float(ts[hit[0]]) if hit.size else np.nan


def arm(df, col):
    """(time, observed, restricted) for one arm: NaN == censored at HORIZON."""
    tau = df[col].to_numpy(dtype=float)
    observed = ~np.isnan(tau)
    time = np.where(observed, np.minimum(tau, HORIZON), float(HORIZON))
    return time, observed, time


def main():
    hat = pd.read_parquet(R6)
    arf = pd.read_parquet(R2)
    if "delta_e" not in arf.columns:
        arf["delta_e"] = norm.cdf(arf["boundary_shift"] / np.sqrt(2)) - 0.5

    grid = np.sort(hat["delta_e"].unique())
    assert len(grid) == 20, f"expected the 20-point Delta_e grid, got {len(grid)}"
    rng = np.random.default_rng(BOOT_SEED)
    rows = []

    for de in grid:
        h = hat[np.isclose(hat["delta_e"], de)].sort_values("seed")
        a = arf[np.isclose(arf["delta_e"], de)].sort_values("seed")
        assert (h["seed"].to_numpy() == a["seed"].to_numpy()).all(), \
            f"arms are not seed-paired at Delta_e={de}"
        n = len(h)

        th, oh, yh = arm(h, "tau_hat")
        ta, oa, ya = arm(a, "tau_arf")

        # (2) KM per (arm, Delta_e) + the identity check that validates single administrative censoring
        rows_km = {}
        for name, (t, o, y) in (("hat", (th, oh, yh)), ("arf", (ta, oa, ya))):
            ts, surv = km_curve(t, o)
            r_km, r_mean = rmst(ts, surv, HORIZON), float(np.mean(y))
            assert abs(r_km - r_mean) <= RMST_TOL, (
                f"RMST({HORIZON}) != mean(min(tau,{HORIZON})) for arm {name} at Delta_e={de}: "
                f"{r_km} vs {r_mean} (delta {r_km - r_mean:.3e}). Censoring is NOT purely "
                f"administrative at the horizon -- HALT.")
            rows_km[name] = (r_km, km_median(ts, surv), abs(r_km - r_mean))

        rmst_h, med_h, dev_h = rows_km["hat"]
        rmst_a, med_a, dev_a = rows_km["arf"]

        # (4) paired-on-seed bootstrap. Under the verified identity RMST == mean(min(tau, HORIZON)),
        #     so a resample of seed indices reduces to a mean of the restricted times.
        idx = rng.integers(0, n, size=(N_BOOT, n))
        ratio_boot = yh[idx].mean(axis=1) / ya[idx].mean(axis=1)
        lo, hi = np.percentile(ratio_boot, [2.5, 97.5])

        cc_h = float(np.nanmean(h["tau_hat"].to_numpy(dtype=float)))
        cc_a = float(np.nanmean(a["tau_arf"].to_numpy(dtype=float)))

        rows.append({
            "delta_e": round(float(de), 6), "n_seeds": n,
            "censored_frac_hat": round(float(np.mean(~oh)), 4),
            "censored_frac_arf": round(float(np.mean(~oa)), 4),
            "rmst_hat": round(rmst_h, 4), "rmst_arf": round(rmst_a, 4),
            "rmst_ratio": round(rmst_h / rmst_a, 4),
            "rmst_ratio_ci_lo": round(float(lo), 4), "rmst_ratio_ci_hi": round(float(hi), 4),
            "median_hat": med_h, "median_arf": med_a,
            "median_ratio": round(med_h / med_a, 4) if med_a else np.nan,
            "complete_case_hat": round(cc_h, 4), "complete_case_arf": round(cc_a, 4),
            "complete_case_ratio": round(cc_h / cc_a, 4),
            "rmst_identity_dev": max(dev_h, dev_a),
        })

    res = pd.DataFrame(rows)
    res.to_csv(OUT_DIR / "hydra_survival.csv", index=False)

    # (5) the reference arm carries the bias direction
    arf_cens = res["censored_frac_arf"].max()
    bound = ("LOWER BOUND" if arf_cens < CENSORING_FREE else "POINT ESTIMATE")
    note = (rf"The ARF arm is censoring-free (max censored fraction ${arf_cens:.3f}$), so the "
            rf"RMST ratio is a \textbf{{lower bound}} on the true acceleration: only the HAT arm "
            rf"is truncated at $t_c={HORIZON}$."
            if arf_cens < CENSORING_FREE else
            rf"Both arms carry censoring (ARF max ${arf_cens:.3f}$); the RMST ratio is a point "
            rf"estimate restricted to $t_c={HORIZON}$.")

    tex = [r"\begin{table}[t]", r"  \centering",
           r"  \caption{Hydra acceleration factor $\tau_{\mathrm{HAT}}/\tau_{\mathrm{ARF}}$: published "
           r"complete-case ratio vs.\ censoring-aware RMST ratio at the common administrative horizon "
           rf"$t_c = {HORIZON}$ post-drift steps ($100$ seeds/magnitude, $95\%$ percentile CI from "
           rf"${N_BOOT}$ bootstrap resamples paired on the seed index). " + note + "}",
           r"  \label{tab:hydra_survival}", r"  \begin{tabular}{@{}lrrrr@{}}", r"    \toprule",
           r"    $\Delta e$ & cens. HAT & complete-case & RMST ratio & $95\%$ CI \\", r"    \midrule"]
    for _, r in res.iterrows():
        tex.append(rf"    {r.delta_e:.3f} & {r.censored_frac_hat:.2f} & {r.complete_case_ratio:.2f}$\times$ "
                   rf"& {r.rmst_ratio:.2f}$\times$ & $[{r.rmst_ratio_ci_lo:.2f}, {r.rmst_ratio_ci_hi:.2f}]$ \\")
    tex += [r"    \bottomrule", r"  \end{tabular}", r"\end{table}", ""]
    (OUT_DIR / "hydra_survival.tex").write_text("\n".join(tex), encoding="utf-8")

    print(res.to_string(index=False))
    print(f"\n[R6/S7] max |RMST - mean(min(tau,{HORIZON}))| = {res['rmst_identity_dev'].max():.3e} "
          f"(tolerance {RMST_TOL:g}) -> single administrative censoring confirmed.")
    print(f"[R6/S7] ARF arm max censored fraction = {arf_cens:.4f} -> RMST ratio is a {bound}.")
    for target in (0.14, 0.33):
        i = (res["delta_e"] - target).abs().idxmin()
        r = res.loc[i]
        print(f"[R6/S7] manuscript anchor Delta_e~{target} (grid {r.delta_e:.6f}): "
              f"complete-case {r.complete_case_ratio:.2f}x -> RMST {r.rmst_ratio:.2f}x "
              f"[{r.rmst_ratio_ci_lo:.2f}, {r.rmst_ratio_ci_hi:.2f}]")
    print(f"[R6/S7] RMST ratio over the full grid: {res.rmst_ratio.min():.2f}x .. {res.rmst_ratio.max():.2f}x")
    print(f"[R6/S7] -> results/audit_S7/hydra_survival.{{csv,tex}}")


if __name__ == "__main__":
    main()
