"""Synthesis figure of stream S6: three detector regimes on one synchronised timeline.

`docs/theory/transfer_S1.md` states the requirement literally -- "S6 must also deliver, per magnitude
and per seed: the trajectory bar_e_t over [tau*, tau* + 3W], the swap counter N_swap(t), and the
external detector statistic S_t on a shared timeline. Reviewers #1 and #4 both demand exactly these
synchronised trajectories." This is that figure.

Layout: three columns, one per external-CUSUM threshold lambda (the R2 scenarios), three stacked
panels sharing the time axis.

  row 1  N_swap(t): the Hydra count sum_i n_i(t) against the DISTINCT-tree count, arm 'full'.
         The gap between the two curves is F6, drawn.
  row 2  bar_e_t, the smoothed ensemble error, for all four causal arms. 'frozen' is the branch that
         never adapts again and is therefore the trajectory the drift would have produced on its
         own; the distance between it and 'full' is the erasure.
  row 3  S_t, the external CUSUM statistic recomputed from the SAME error stream with p_pre = e_pre,
         against its threshold lambda. Whether the statistic reaches the line before the error is
         erased is the blind spot, per column.

The column labels are earned from the data, not asserted: each column reports its measured
pre-drift false-alarm rate and its measured P(tau_det <= tau_erase), and the regime name is assigned
from those two numbers.

Markers: tau* (drift), tau_swap^(1/M), tau_erase, tau_det -- medians over seeds.

Output: results/S6_synchronized_traces/figures/Fig_S6_synchronized.png
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pyarrow.dataset as ds
import pyarrow.parquet as pq

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import s6_defs as defs  # noqa: E402
from config import experiment_ssot as ssot  # noqa: E402

RESULTS_DIR = ssot.RESULTS_DIR / "S6_synchronized_traces"
LADDER = sorted(ssot.S6_FIGURE_LAMBDA_LADDER, reverse=True)
TARGET_DELTA_E = ssot.S6_KAPPA_DELTA_E_TARGET
ERR_WINDOW = ssot.S6_ERR_WINDOW
DELTA_P = ssot.DELTA_P
T_LOAD = -ssot.S6_TRACE_PRE          # the whole traced warm-up: the false-alarm rate is measured
                                     # over 1000 pre-drift steps, not over the plotted margin
T_LOAD_HI = ssot.S6_T_HORIZON        # tau_det is searched over the whole proof horizon, not over
                                     # the plotted window: censoring at 1000 would be an artefact
T_LO, T_HI = -ERR_WINDOW, 1000       # displayed window

BLUE, ORANGE, RED, GREEN, GRAY = "#04617b", "#E8A000", "#C62828", "#2E7D32", "#546E7A"
ARM_STYLE = {"full": (BLUE, "-", r"\texttt{full}"), "no_swap": (GREEN, "--", r"\texttt{no\_swap}"),
             "frozen": (RED, "-.", r"\texttt{frozen}"), "static": (GRAY, ":", r"\texttt{static}")}
plt.rcParams.update({"figure.dpi": 300, "font.family": "sans-serif", "font.size": 9,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "mathtext.fontset": "stix"})


def cusum_path(err, p_pre, delta=DELTA_P):
    """Reflected CUSUM statistic over a whole traced window, pre-drift included."""
    s, out = 0.0, np.empty(err.size)
    for i, x in enumerate(err):
        s = max(0.0, s + (x - p_pre) - delta)
        out[i] = s
    return out


def load(which="data"):
    base = RESULTS_DIR / which
    runs = pq.read_table(base / "runs.parquet").to_pandas()
    available = sorted(runs.delta_e.unique())
    de = min(available, key=lambda d: abs(d - TARGET_DELTA_E))
    part = base / "traces.parquet" / f"delta_e={ssot.S6_PARQUET_PARTITION_FMT.format(de)}"
    tbl = ds.dataset(str(part), format="parquet").to_table(
        filter=(ds.field("t_rel") >= T_LOAD) & (ds.field("t_rel") < T_LOAD_HI))
    return de, runs[np.isclose(runs.delta_e, de)], tbl.to_pandas().sort_values(["arm", "seed", "t_rel"])


def per_arm_matrices(traces, arm):
    """(t_rel axis, {column: seeds x steps matrix}) for one arm."""
    g = traces[traces.arm == arm]
    seeds = np.sort(g.seed.unique())
    t = np.sort(g[g.seed == seeds[0]].t_rel.unique())
    out = {}
    for col in ("err", "swaps_cum", "trees_swapped_cum"):
        out[col] = np.stack([g[g.seed == s].sort_values("t_rel")[col].to_numpy(dtype=np.float64)
                             for s in seeds])
    return t, seeds, out


def main(which="data"):
    de, runs, traces = load(which)
    full_runs = runs[runs.arm == "full"].set_index("seed")
    t, seeds, mats = per_arm_matrices(traces, "full")
    post = t >= 0
    disp = (t >= T_LO) & (t < T_HI)      # the warm-up beyond the display feeds the smoother and the
                                         # false-alarm count, it is not drawn

    # --- external CUSUM, recomputed on the same error stream ------------------------------------
    stats = np.stack([cusum_path(mats["err"][i], float(full_runs.loc[s, "e_pre"]))
                      for i, s in enumerate(seeds)])
    smoothed = {a: np.stack([defs.rolling_mean(r, ERR_WINDOW)
                             for r in per_arm_matrices(traces, a)[2]["err"]])
                for a in ARM_STYLE}

    tau_swap = float(np.nanmedian(full_runs.loc[seeds, "tau_swap_q010"]))
    # The framework tau_err(delta_P) is not estimable on this stream -- delta_P sits 0.32 standard
    # errors above p_0 at W = 200, and the pre-drift null control returns 79 % of its own horizon
    # (s6_causal.erasure_estimability). The figure therefore marks the estimable surrogate, the
    # argmax of A_unrefl, and says so in the label.
    tau_erase = float(np.nanmedian(full_runs.loc[seeds, "tau_erase"]))
    hydra_total = float(np.nanmedian(full_runs.loc[seeds, "swaps_total"]))
    distinct_total = float(np.nanmedian(full_runs.loc[seeds, "trees_swapped_total"]))

    erase = full_runs.loc[seeds, "tau_erase"].to_numpy(dtype=np.float64)
    ladder = []
    for lam in LADDER:
        pre_alarm = float(np.mean((stats[:, ~post] >= lam).any(axis=1)))
        det = np.array([float(t[post][h[0]]) if (h := np.flatnonzero(row >= lam)).size else np.nan
                        for row in stats[:, post]])
        in_time = float(np.mean(np.isfinite(det) & (det <= np.nan_to_num(erase, nan=np.inf))))
        ladder.append({"lambda": float(lam), "pre_drift_false_alarm_rate": pre_alarm,
                       "p_detect_before_erase": in_time,
                       "regime": ("flooding" if pre_alarm >= 0.5 else
                                  "safe zone" if in_time >= 0.5 else "starvation"),
                       "tau_det_median": float(np.nanmedian(det)) if np.isfinite(det).any() else np.nan,
                       "tau_det_censored": float(np.mean(~np.isfinite(det)))})

    def pick(regime, fallback):
        """The lambda that best exemplifies a regime; the R2 scenario when none does."""
        hits = [c for c in ladder if c["regime"] == regime]
        if not hits:
            c = dict(next(c for c in ladder if c["lambda"] == fallback))
            c["exemplifies"] = False
            return c
        # Each regime is exemplified by its BOUNDARY case: the largest lambda that still starves,
        # the one that detects most reliably without alarming, the largest that still floods. The
        # extreme members (lambda = 1 fires at t = 0) carry no information.
        key = {"starvation": lambda c: -c["lambda"],
               "safe zone": lambda c: (-c["p_detect_before_erase"], c["pre_drift_false_alarm_rate"]),
               "flooding": lambda c: -c["lambda"]}[regime]
        c = dict(sorted(hits, key=key)[0])
        c["exemplifies"] = True
        return c

    columns = [pick(r, f) for r, f in zip(("starvation", "safe zone", "flooding"),
                                          ssot.S6_FIGURE_LAMBDAS)]

    fig, axes = plt.subplots(3, 3, figsize=(11, 7.5), sharex=True,
                             gridspec_kw={"height_ratios": [1, 1.2, 1.2]})
    for j, col in enumerate(columns):
        lam = col["lambda"]
        ax_n, ax_e, ax_s = axes[:, j]
        marks = [(0.0, GRAY, r"$\tau^*$"), (tau_swap, BLUE, r"$\tau_{\mathrm{swap}}^{(1/M)}$"),
                 (tau_erase, RED, r"$\tau_{\mathrm{erase}}^{\mathrm{argmax}}$"),
                 (col["tau_det_median"], ORANGE, r"$\tau_{\mathrm{det}}$")]

        n_swap = mats["swaps_cum"] - mats["swaps_cum"][:, post][:, 0:1]
        ax_n.plot(t[disp], np.median(n_swap[:, disp], axis=0), color=RED, lw=2.6, alpha=0.9,
                  label=r"$N_{\mathrm{swap}}(t)$ (all replacements)")
        ax_n.plot(t[disp], np.median(mats["trees_swapped_cum"][:, disp], axis=0), color=BLUE,
                  lw=1.3, ls="--", label=r"distinct trees replaced")
        ax_n.set_ylim(bottom=0)
        # Inside the displayed window no tree is replaced twice, so the two curves coincide; the
        # Hydra repeats open the gap later. The horizon totals carry it, and are printed rather than
        # left to a reader who would otherwise read the overlap as "no Hydra".
        ax_n.text(0.97, 0.08, rf"horizon: $N_{{\mathrm{{swap}}}}$ = {hydra_total:.0f} / "
                              rf"{distinct_total:.0f} distinct",
                  transform=ax_n.transAxes, ha="right", fontsize=6.5, color=GRAY)
        if j == 0:
            ax_n.set_ylabel("replacements")
            ax_n.legend(fontsize=6.5, loc="upper left", framealpha=0.9)
        title = col["regime"] if col["exemplifies"] else f"{col['regime']} (no flooding on ladder)"
        ax_n.set_title(f"{title}  " + rf"($\lambda={lam:g}$)", fontsize=10,
                       fontweight="bold", pad=16)
        ax_n.text(0.5, 1.02, f"pre-drift FA = {col['pre_drift_false_alarm_rate']:.2f}   "
                             f"P(det before erase) = {col['p_detect_before_erase']:.2f}",
                  transform=ax_n.transAxes, ha="center", fontsize=6.5, color=GRAY)

        for arm, (color, style, label) in ARM_STYLE.items():
            ax_e.plot(t[disp], np.nanmedian(smoothed[arm][:, disp], axis=0), color=color, ls=style, lw=1.6,
                      label=label.replace("\\texttt{", "").replace("}", "").replace("\\_", "_"))
        ax_e.axhline(float(np.nanmedian(full_runs.loc[seeds, "e_pre"])) + DELTA_P,
                     color=GRAY, lw=0.8, ls=":", label=r"$p_0+\delta_P$")
        if j == 0:
            ax_e.set_ylabel(r"$\bar{e}_t$  (window " + f"{ERR_WINDOW})")
            ax_e.legend(fontsize=6.5, loc="upper right", ncol=2, framealpha=0.9)

        ax_s.plot(t[disp], np.median(stats[:, disp], axis=0), color=ORANGE, lw=1.8,
                  label=r"$S_t$ (CUSUM)")
        ax_s.fill_between(t[disp], np.quantile(stats[:, disp], 0.25, axis=0),
                          np.quantile(stats[:, disp], 0.75, axis=0), color=ORANGE, alpha=0.15, lw=0)
        ax_s.axhline(lam, color=RED, lw=1.2, ls="--", label=rf"$\lambda={lam:g}$")
        ax_s.set_ylim(0, max(lam * 1.35, float(np.quantile(stats[:, disp], 0.75, axis=0).max()) * 1.1))
        ax_s.set_xlabel(r"$t - \tau^*$")
        if j == 0:
            ax_s.set_ylabel("detector statistic")
            ax_s.legend(fontsize=6.5, loc="upper left", framealpha=0.9)

        # A marker outside the displayed window is not drawn: an axvline at t = 2000 would silently
        # rescale a shared axis and blank out the transient the figure exists to show.
        shown = [m for m in marks if np.isfinite(m[0]) and T_LO <= m[0] < T_HI]
        for ax in (ax_n, ax_e, ax_s):
            for pos, color, _ in shown:
                ax.axvline(pos, color=color, lw=0.9, ls="--", alpha=0.65)
        for k, (pos, color, label) in enumerate(shown):
            ax_n.annotate(label, xy=(pos, 1.0), xycoords=("data", "axes fraction"),
                          xytext=(2, -9 - 9 * (k % 3)), textcoords="offset points",
                          color=color, fontsize=6.5)

    for ax in axes.ravel():
        ax.set_xlim(T_LO, T_HI)
    fig.suptitle(r"Stream S6 -- synchronised trajectories at $\Delta e = "
                 rf"{de:.4f}$, $M={ssot.S6_N_MODELS}$, $c_{{\mathrm{{int}}}}={ssot.S6_C_INT}$, "
                 rf"{len(seeds)} seeds (medians, IQR shaded)", fontsize=11, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    out = RESULTS_DIR / "figures" / "Fig_S6_synchronized.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out)
    plt.close(fig)

    print(f"=== S6 figure ({which}) === Delta_e = {de:.4f}, {len(seeds)} seeds")
    print(f"  tau_swap^(1/M) median = {tau_swap:.1f} | tau_erase median = {tau_erase:.1f}")
    print(f"  lambda ladder (false alarms measured over {ssot.S6_TRACE_PRE} pre-drift steps):")
    for c in ladder:
        print(f"    lambda={c['lambda']:5g}  regime={c['regime']:<11s} "
              f"FA={c['pre_drift_false_alarm_rate']:.3f}  "
              f"P(det<=erase)={c['p_detect_before_erase']:.3f}  "
              f"tau_det median={c['tau_det_median']:.1f}")
    print("  columns selected:")
    for c in columns:
        print(f"  lambda={c['lambda']:5g}  regime={c['regime']:<11s} "
              f"pre-drift FA={c['pre_drift_false_alarm_rate']:.3f}  "
              f"P(det<=erase)={c['p_detect_before_erase']:.3f}  "
              f"tau_det median={c['tau_det_median']:.1f}  censored={c['tau_det_censored']:.3f}")
    print(f"[INFO] wrote {out.relative_to(ssot.ROOT_DIR)}")
    return {"delta_e": de, "ladder": ladder, "columns": columns,
            "tau_swap": tau_swap, "tau_erase": tau_erase}


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data")
