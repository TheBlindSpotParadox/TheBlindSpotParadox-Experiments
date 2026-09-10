"""Predictive power of the first swap (faille F6).

F6 says `tau_swap^(1/M) = min_i tau_i` is a contested proxy for ensemble adaptation. "Contested" is
not a measurement. This script asks the proxy to earn its place in two ways:

  1. Rank correlation. Spearman between tau_swap^(1/M) and the quantities the manuscript actually
     reasons about -- the proof budget A, the erasure time tau_erase, the recovery times
     tau_err(rho). A proxy that ranks runs the same way as the quantity it stands for is usable even
     if biased; one that does not is a different variable wearing its name.
  2. Accelerated failure time. A log-normal AFT model for tau_erase with EXACT right censoring,
     log T = X beta + sigma eps, eps ~ N(0,1), maximised by `scipy.optimize.minimize` on the
     censored log-likelihood -- uncensored runs contribute the log-density, censored runs the log
     survival at the horizon. Runs that never settle inside T_h are censored, not dropped: dropping
     them would condition the fit on fast adaptation, which is the very thing under test.

Standard errors come from the numerical Hessian of the negative log-likelihood at the optimum. The
fit is deterministic: the start point is the OLS solution on the uncensored subset.

Output: results/S6_synchronized_traces/tables/first_swap_predictive_power.tex
"""
import sys
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq
from scipy.optimize import approx_fprime, minimize
from scipy.stats import norm, spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from config import experiment_ssot as ssot  # noqa: E402

T_HORIZON = ssot.S6_T_HORIZON
RHO_GRID = ssot.S6_RHO_GRID
RESULTS_DIR = ssot.RESULTS_DIR / "S6_synchronized_traces"

TARGETS = [("a_fw", r"$A$ (framework)"), ("a", r"$A$ (Phase-1)"),
           ("tau_erase_fw", r"$\tau_{\mathrm{erase}}$"), ("tau_erase", r"$\tau_{\mathrm{erase}}^{\mathrm{argmax}}$")]
TARGETS += [(f"tau_err_rho{int(round(r * 100)):03d}", rf"$\tau_{{\mathrm{{err}}}}({r:.2f})$")
            for r in RHO_GRID]


def load(which="data"):
    path = RESULTS_DIR / which / "runs.parquet"
    if not path.exists():
        raise SystemExit(f"[FATAL] {path} absent -- run s6_runner.py first")
    return pq.read_table(path).to_pandas()


def spearman_table(full):
    """Spearman between tau_swap^(1/M) and each target, pooled and inside three magnitude bands.

    Pooled over a 20-point magnitude grid, ANY monotone-in-Delta_e pair correlates through the
    common driver. The bands are what separate a real association from that confound."""
    x_col = "tau_swap_q010"
    bands = [("weak", full.delta_e <= 0.15), ("mid", (full.delta_e > 0.15) & (full.delta_e <= 0.35)),
             ("strong", full.delta_e > 0.35)]
    rows = []
    for col, label in TARGETS:
        entry = {"col": col, "label": label}
        for name, mask in [("pooled", np.ones(len(full), bool))] + bands:
            sub = full[mask]
            ok = np.isfinite(sub[x_col]) & np.isfinite(sub[col])
            if ok.sum() < 3:
                entry[name] = (np.nan, np.nan, int(ok.sum()))
                continue
            r, p = spearmanr(sub.loc[ok, x_col], sub.loc[ok, col])
            entry[name] = (float(r), float(p), int(ok.sum()))
        rows.append(entry)
    return rows


def _nll(theta, x, log_t, event, k):
    """MEAN negative log-likelihood of a log-normal AFT with exact right censoring.

    The mean, not the sum: on 2000 runs the summed gradient is O(10^3) and no absolute `gtol`
    reachable by BFGS certifies a stationary point, so the fit reports failure at its own optimum.
    The argmin is identical; the observed information is recovered by scaling the Hessian by n."""
    beta, log_sigma = theta[:k], theta[k]
    z = (log_t - x @ beta) / np.exp(log_sigma)
    ll = np.where(event, -0.5 * z ** 2 - 0.5 * np.log(2 * np.pi) - log_sigma, norm.logsf(z))
    return -float(ll.mean())


def aft_lognormal(full, horizon=T_HORIZON):
    """Log-normal AFT for tau_erase on log tau_swap^(1/M) and log Delta_e, right-censored at T_h."""
    d = full[np.isfinite(full.tau_swap_q010) & (full.tau_swap_q010 > 0)
             & np.isfinite(full.delta_e_emp) & (full.delta_e_emp > 0)].copy()
    event = np.isfinite(d.tau_erase_fw.to_numpy())
    t = np.where(event, d.tau_erase_fw.to_numpy(), float(horizon))
    keep = t > 0
    d, event, t = d[keep], event[keep], t[keep]

    x = np.column_stack([np.ones(len(d)), np.log(d.tau_swap_q010.to_numpy()),
                         np.log(d.delta_e_emp.to_numpy())])
    names = ["intercept", "log tau_swap^(1/M)", "log Delta_e_emp"]
    log_t = np.log(t)

    beta0, *_ = np.linalg.lstsq(x[event], log_t[event], rcond=None)
    resid = log_t[event] - x[event] @ beta0
    start = np.append(beta0, np.log(max(resid.std(ddof=x.shape[1]), 1e-3)))

    args = (x, log_t, event, x.shape[1])
    fit = minimize(_nll, start, args=args, method="BFGS", options={"gtol": 1e-8, "maxiter": 2000})
    if not fit.success:                      # flat directions on small samples stall BFGS
        fit = minimize(_nll, minimize(_nll, fit.x, args=args, method="Nelder-Mead",
                                      options={"xatol": 1e-10, "fatol": 1e-10, "maxiter": 20000}).x,
                       args=args, method="BFGS", options={"gtol": 1e-6, "maxiter": 2000})
    step = np.maximum(np.abs(fit.x) * 1e-5, 1e-7)
    hess = np.array([approx_fprime(fit.x, lambda th, i=i: approx_fprime(
        th, _nll, step, x, log_t, event, x.shape[1])[i], step) for i in range(fit.x.size)])
    hess = 0.5 * (hess + hess.T) * len(log_t)      # mean Hessian -> observed information
    try:
        se = np.sqrt(np.diag(np.linalg.inv(hess)))
    except np.linalg.LinAlgError:
        se = np.full(fit.x.size, np.nan)

    beta, log_sigma = fit.x[:-1], fit.x[-1]
    z = beta / se[:-1]
    return {"names": names, "beta": beta.tolist(), "se": se[:-1].tolist(),
            "z": z.tolist(), "p": (2 * norm.sf(np.abs(z))).tolist(),
            "sigma": float(np.exp(log_sigma)), "sigma_se": float(np.exp(log_sigma) * se[-1]),
            "n": int(len(d)), "n_censored": int((~event).sum()),
            "censoring_rate": float((~event).mean()), "horizon": float(horizon),
            "converged": bool(fit.success), "nll": float(fit.fun) * len(log_t),
            "grad_inf_norm": float(np.abs(approx_fprime(fit.x, _nll, step, *args)).max())}


def _fmt(r, p):
    if not np.isfinite(r):
        return "--"
    stars = "^{***}" if p < 1e-3 else "^{**}" if p < 1e-2 else "^{*}" if p < 5e-2 else ""
    return f"${r:.3f}{stars}$"


def latex_table(rows, aft, path):
    n_lo = min(r["pooled"][2] for r in rows)
    n_hi = max(r["pooled"][2] for r in rows)
    lines = [
        r"% Generated by experiments/S6_synchronized_traces/s6_predictive_power.py",
        r"% Stream S6, arm 'full'. Do not edit by hand.",
        r"\begin{table}[t]", r"\centering",
        r"\caption{Predictive power of the first internal swap $\tau_{\mathrm{swap}}^{(1/M)}$"
        r" (stream S6, arm \texttt{full}, $M=10$, $c_{\mathrm{int}}=1$)."
        r" Top: Spearman rank correlation, pooled over the canonical magnitude grid and inside three"
        r" magnitude bands. Bottom: log-normal AFT for $\tau_{\mathrm{erase}}$ with exact right"
        rf" censoring at $T_h$. Pairwise complete cases, $n$ from {n_lo} to {n_hi} of 2000 runs;"
        r" a target is dropped from a pair only when it is censored."
        r" $^{*}p<0.05$, $^{**}p<0.01$, $^{***}p<0.001$.}",
        r"\label{tab:s6_first_swap_predictive_power}",
        r"\begin{tabular}{lrrrr}", r"\toprule",
        r"Target & pooled & weak & mid & strong \\",
        r"\midrule",
    ]
    for r in rows:
        cells = " & ".join(_fmt(*r[b][:2]) for b in ("pooled", "weak", "mid", "strong"))
        lines.append(f"{r['label']} & {cells} " + r"\\")
    lines += [
        r"\midrule",
        r"\multicolumn{5}{l}{\emph{Log-normal AFT:} "
        r"$\log \tau_{\mathrm{erase}} = \beta_0 + \beta_1 \log \tau_{\mathrm{swap}}^{(1/M)}"
        r" + \beta_2 \log \Delta e + \sigma \varepsilon$} \\",
        r"\midrule",
        r"Coefficient & estimate & s.e. & $z$ & $p$ \\",
        r"\midrule",
    ]
    # The coefficient names carry ^ and _ and cannot go into a LaTeX cell as text.
    tex_name = {"intercept": r"$\beta_0$ (intercept)",
                "log tau_swap^(1/M)": r"$\log \tau_{\mathrm{swap}}^{(1/M)}$",
                "log Delta_e_emp": r"$\log \Delta e$"}
    for name, b, s, z, p in zip(aft["names"], aft["beta"], aft["se"], aft["z"], aft["p"]):
        lines.append(f"{tex_name.get(name, name)} & ${b:.4f}$ & ${s:.4f}$ & ${z:.2f}$ & "
                     + (r"$<10^{-4}$" if p < 1e-4 else f"${p:.4f}$") + r" \\")
    lines += [
        rf"$\sigma$ & ${aft['sigma']:.4f}$ & ${aft['sigma_se']:.4f}$ & -- & -- \\",
        r"\midrule",
        rf"\multicolumn{{5}}{{l}}{{$n = {aft['n']}$, right-censored at $T_h = {aft['horizon']:.0f}$: "
        rf"{aft['n_censored']} runs ({100 * aft['censoring_rate']:.1f}\%)}} \\",
        r"\bottomrule", r"\end{tabular}", r"\end{table}", "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main(which="data"):
    runs = load(which)
    full = runs[runs.arm == "full"].reset_index(drop=True)
    rows = spearman_table(full)
    aft = aft_lognormal(full)
    path = latex_table(rows, aft, RESULTS_DIR / "tables" / "first_swap_predictive_power.tex")

    print(f"=== S6 predictive power ({which}) === n_full = {len(full)}")
    print(f"{'target':28s} {'pooled':>18s} {'weak':>18s} {'mid':>18s} {'strong':>18s}")
    for r in rows:
        cells = "".join(f"{r[b][0]:>12.3f} (n={r[b][2]:>4d})"[-19:] for b in
                        ("pooled", "weak", "mid", "strong"))
        print(f"{r['col']:28s}{cells}")
    print(f"\nAFT log-normal (converged={aft['converged']}, n={aft['n']}, "
          f"censored={aft['n_censored']} = {100 * aft['censoring_rate']:.1f}%)")
    for name, b, s, z, p in zip(aft["names"], aft["beta"], aft["se"], aft["z"], aft["p"]):
        print(f"  {name:22s} beta={b:9.4f}  se={s:7.4f}  z={z:8.2f}  p={p:.3e}")
    print(f"  sigma = {aft['sigma']:.4f} (se {aft['sigma_se']:.4f})")
    print(f"[INFO] wrote {path.relative_to(ssot.ROOT_DIR)}")
    return rows, aft


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data")
