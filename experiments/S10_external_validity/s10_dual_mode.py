"""Stream S10 / T10.2 -- starvation and flooding on one axis: the threshold.

The manuscript opposes two failure modes, starvation (recall -> 0) and flooding (precision -> 0),
as if they were two regimes of different streams. Both are placements of one threshold against two
budgets: the false-alarm budget of the armed pre-change span bounds it from below, the evidence the
loop leaves bounds it from above. This script draws recall and precision against the PageHinkley
threshold on six streams, shades the admissible window between the two cliffs, and marks where every
published failure sits (docs/theory/S10_decision_rules.md, Part C).

  a, b  canonical and rotation (eta = 0.05) families at Delta_e = 0.326793, the S10 lag-0 traces
        (trunk-identical to S6 and S8, rule L0). Passive monitor, re-armed after each alarm, fed over
        t_rel in [-1000, +1000]; the classifier is never reset (the S6 / S9 protocol).
  c     ProteuS, PHT + ARF(c = 1): s2bis_proteus_sweep.csv, the deployed R4 protocol.
  d-f   INSECTS, pht_arf_c1: s2bis_insects_sweep.csv, the deployed R5 protocol. In c-f the monitor
        AND the classifier are reset on each alarm; the legend says so.

No margin depending on W is used: which quantity the symbol W denotes is under arbitration in S2-ter.

Usage:  PYTHONHASHSEED=0 MPLBACKEND=Agg python experiments/S10_external_validity/s10_dual_mode.py
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import pyarrow.parquet as pq  # noqa: E402
from joblib import Parallel, delayed  # noqa: E402
from river import drift  # noqa: E402

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "R5_real_world_evaluation"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import experiment_ssot as ssot  # noqa: E402

import exp_R5_common as r5  # noqa: E402
import s10_latency as lat  # noqa: E402

GRID = list(ssot.S10_DUAL_LAMBDA_GRID)
DELTA_E = ssot.S10_DUAL_DELTA_E
T_DRIFT = ssot.S6_T_DRIFT
N_STEPS = ssot.S6_N_STEPS
WARMUP = ssot.S10_WARMUP_WINDOW
TAU_TOL = ssot.S10_TAU_TOL
RECALL_MIN = ssot.S10_RECALL_MIN
PRECISION_MIN = ssot.S10_PRECISION_MIN
S2BIS = ssot.RESULTS_DIR / "S2bis_calibration" / "tables"
OUT_DIR = ssot.RESULTS_DIR / "S10_external_validity"
INSECTS = ("abrupt_balanced", "gradual_balanced", "incremental_reoccurring_balanced")

# Palette validated with the dataviz validator (light surface, CVD and contrast: all checks pass).
# Identity never rests on hue alone: line style and marker carry it in greyscale print.
INK, INK2, RECALL_C, PRECISION_C = "#0b0b0b", "#52514e", "#2a78d6", "#eb6834"


# ══════════════════════════════════════════════════════════════════════════════
# Curves
# ══════════════════════════════════════════════════════════════════════════════
def rearmed_alarms(x, lam):
    """Alarm indices of a PageHinkley re-armed after each alarm -- the convention of R5's
    `calibrate_lambda` and S2-bis's `count_false_alarms`, with the instants kept."""
    pht = drift.PageHinkley(threshold=lam, delta=ssot.DELTA_P)
    out = []
    for j, e in enumerate(x):
        pht.update(float(e))
        if pht.drift_detected:
            out.append(j)
            pht = drift.PageHinkley(threshold=lam, delta=ssot.DELTA_P)
    return out


def synthetic_cell(err, t_rel):
    """One seed: TP / FP per threshold, the span budget lambda_FA, the post-drift PHT peak."""
    fed = (t_rel >= -WARMUP) & (t_rel <= TAU_TOL)
    x, tr = err[fed].astype(np.float64), t_rel[fed]
    row = {"lambda_FA": float(r5.calibrate_lambda(list(x[tr < 0]))),
           "pht_peak": float(np.max(lat.pht_trace(x)[tr >= 0])), "tp": {}, "fp": {}}
    for lam in GRID:
        alarms = [int(T_DRIFT + tr[j]) for j in rearmed_alarms(x, lam)]
        fp_bp = r5.evaluate_bipartite(alarms, [T_DRIFT], N_STEPS, TAU_TOL)[5]
        row["tp"][lam], row["fp"][lam] = len(alarms) - fp_bp, fp_bp
    row["p0"] = float(x[tr < 0].mean())
    return row


def synthetic_partition(stream, delta_e):
    part = (OUT_DIR / "data" / stream / "traces.parquet"
            / f"delta_e={ssot.S6_PARQUET_PARTITION_FMT.format(delta_e)}" / "part-0.parquet")
    df = pq.read_table(part, columns=["seed", "t_rel", "err_l0"]).to_pandas()
    df = df.sort_values(["seed", "t_rel"])
    cells = [synthetic_cell(g["err_l0"].to_numpy(), g["t_rel"].to_numpy())
             for _, g in df.groupby("seed", sort=True)]
    n = len(cells)
    tp = {lam: sum(c["tp"][lam] for c in cells) for lam in GRID}
    fp = {lam: sum(c["fp"][lam] for c in cells) for lam in GRID}
    return {"stream": stream, "delta_e": delta_e, "n_seeds": n, "lambdas": GRID,
            "recall": [tp[lam] / n for lam in GRID],
            "precision": [tp[lam] / (tp[lam] + fp[lam]) if tp[lam] + fp[lam] else None
                          for lam in GRID],
            "lambda_FA": float(np.median([c["lambda_FA"] for c in cells])),
            "lambda_op": float(np.quantile([c["pht_peak"] for c in cells], 0.05)),
            "p0": float(np.median([c["p0"] for c in cells]))}


def _pooled(df, tp, fp, n_changes):
    t, f, k = float(df[tp].sum()), float(df[fp].sum()), float(df[n_changes].sum())
    return t / k, (t / (t + f) if t + f else None)


def proteus_panel():
    sw = pd.read_csv(S2BIS / "s2bis_proteus_sweep.csv", float_precision="round_trip")
    sw = sw[(sw.Detector == "PHT + ARF") & (sw.Clock == 1)]
    sw["n_changes"] = sw.TP + sw.FN
    ladder = sw[sw.lambda_role.isin(["grid", "lambda_ref"])]
    lams = sorted(ladder["lambda"].unique())
    rec, prec = zip(*[_pooled(ladder[ladder["lambda"] == lam], "TP", "FP", "n_changes") for lam in lams])
    cal = pd.read_csv(S2BIS / "s2bis_lambda_eq_proteus.csv", float_precision="round_trip")
    cal = cal[(cal.Detector == "PHT + ARF") & (cal.Clock == 1)]
    ref = sw[sw.lambda_role == "lambda_ref"]
    r_pub, p_pub = _pooled(ref, "TP", "FP", "n_changes")
    return {"stream": "ProteuS, PHT + ARF(c = 1)", "lambdas": [float(v) for v in lams],
            "recall": list(rec), "precision": list(prec), "n_runs_per_lambda": int(len(ref)),
            "lambda_FA": float(cal.lambda_eq.median()), "lambda_FA_verdict": sorted(cal.verdict_B7.unique()),
            "lambda_op": None, "p0": float(cal.p_true_pre_drift.median()),
            "published": [{"label": "Table I, lambda = 15", "short": "Table I", "mode": "starvation",
                           "lambda": float(ref["lambda"].median()), "recall": r_pub, "precision": p_pub}]}


def insects_panel(variant):
    sw = pd.read_csv(S2BIS / "s2bis_insects_sweep.csv", float_precision="round_trip")
    sw = sw[(sw.pipeline == "pht_arf_c1") & (sw.variant == variant)]
    grid = sw[sw.lambda_role == "grid"]
    lams = sorted(grid["lambda"].unique())
    rec, prec = zip(*[_pooled(grid[grid["lambda"] == lam], "TP_bp", "FP_bp", "n_valid_drifts")
                      for lam in lams])
    cal = pd.read_csv(S2BIS / "s2bis_lambda_eq_insects.csv", float_precision="round_trip")
    cal = cal[(cal.pipeline == "pht_arf_c1") & (cal.variant == variant)]
    ref = sw[sw.lambda_role == "lambda_ref"]
    r_pub, p_pub = _pooled(ref, "TP_bp", "FP_bp", "n_valid_drifts")
    published = [] if variant == "abrupt_balanced" else [
        {"label": "Table II, warm-up calibration", "short": "Table II", "mode": "flooding",
         "lambda": float(ref["lambda"].median()), "recall": r_pub, "precision": p_pub}]
    return {"stream": f"INSECTS {variant}, pht_arf_c1", "lambdas": [float(v) for v in lams],
            "recall": list(rec), "precision": list(prec), "n_runs_per_lambda": int(len(ref)),
            "lambda_FA": float(cal.lambda_eq_span_emp.median()), "lambda_op": None,
            "p0": float(cal.p_true_span.median()), "published": published,
            "lambda_ref_median": float(ref["lambda"].median()),
            "at_lambda_ref": {"recall": r_pub, "precision": p_pub}}


# ══════════════════════════════════════════════════════════════════════════════
# Rules DM1-DM3
# ══════════════════════════════════════════════════════════════════════════════
def admissible(lambdas, recall, precision):
    """DM1: grid points with recall >= RECALL_MIN and precision >= PRECISION_MIN, an undefined
    precision (no alarm at all) counting as satisfied. None when empty."""
    ok = [lam for lam, r, p in zip(lambdas, recall, precision)
          if r >= RECALL_MIN and (p is None or p >= PRECISION_MIN)]
    if not ok:
        return None
    i, j = lambdas.index(ok[0]), lambdas.index(ok[-1])
    return {"lo": ok[0], "hi": ok[-1], "contiguous": len(ok) == j - i + 1}


def edge_agreement(lambdas, edge, marker):
    """DM2: AGREES when the marker lies between the grid neighbours of the edge."""
    if edge is None or marker is None:
        return None
    i = lambdas.index(edge)
    lo, hi = lambdas[max(0, i - 1)], lambdas[min(len(lambdas) - 1, i + 1)]
    return "AGREES" if lo <= marker <= hi else "DISAGREES"


def failure_verdict(mode, recall, precision):
    """DM3: a published failure must fail by the criterion of its own mode, and by that one only."""
    recall_fail = recall < RECALL_MIN
    precision_fail = precision is not None and precision < PRECISION_MIN
    if recall_fail and precision_fail:
        return "DOUBLE"
    own, other = (recall_fail, precision_fail) if mode == "starvation" else (precision_fail, recall_fail)
    return "HOLDS" if own and not other else "FAILS"


def rule_readings(panel):
    w = admissible(panel["lambdas"], panel["recall"], panel["precision"])
    panel["window"] = w
    panel["DM2"] = {"lower_vs_lambda_FA": edge_agreement(panel["lambdas"], w and w["lo"], panel["lambda_FA"]),
                    "upper_vs_lambda_op": edge_agreement(panel["lambdas"], w and w["hi"], panel["lambda_op"])}
    for p in panel.get("published", []):
        p["DM3"] = failure_verdict(p["mode"], p["recall"], p["precision"])
    return panel


# ══════════════════════════════════════════════════════════════════════════════
# Figure
# ══════════════════════════════════════════════════════════════════════════════
PROTOCOL = {"passive": "passive monitor", "reset": "reset on alarm"}
LEGEND_ORDER = ["recall", "precision", "admissible window",
                r"$\lambda_{\mathrm{FA}}$: one false alarm over the armed span",
                r"$\lambda_{\mathrm{op}} = q_{0.05}$ of the post-drift PHT peak", "published operating point"]


def draw(panels, path):
    fig, axes = plt.subplots(2, 3, figsize=(7.16, 5.2), sharex=True, sharey=True)
    for ax, (tag, panel, protocol) in zip(axes.flat, panels):
        lams = np.asarray(panel["lambdas"])
        rec = np.asarray(panel["recall"], dtype=float)
        prec = np.asarray([np.nan if p is None else p for p in panel["precision"]], dtype=float)
        if panel["window"]:
            ax.axvspan(panel["window"]["lo"], panel["window"]["hi"], color=INK2, alpha=0.12, lw=0,
                       label=LEGEND_ORDER[2])
        ax.axvline(panel["lambda_FA"], color=INK2, ls=":", lw=1.0, label=LEGEND_ORDER[3])
        if panel["lambda_op"] is not None:
            ax.axvline(panel["lambda_op"], color=INK2, ls="-.", lw=1.0, label=LEGEND_ORDER[4])
        ax.plot(lams, rec, color=RECALL_C, lw=1.4, marker="o", ms=3.2, label=LEGEND_ORDER[0])
        ax.plot(lams, prec, color=PRECISION_C, lw=1.4, ls="--", marker="s", ms=3.0, label=LEGEND_ORDER[1])
        for p in panel.get("published", []):
            ax.axvline(p["lambda"], color=INK, lw=0.9, alpha=0.85, label=LEGEND_ORDER[5])
            ax.text(p["lambda"], 1.03, f"{p['short']}, {p['mode']}", transform=ax.get_xaxis_transform(),
                    ha="center", va="bottom", fontsize=5.5, color=INK)
        ax.set_xscale("log")
        ax.set_xlim(0.8, 500)
        ax.set_ylim(-0.02, 1.02)
        ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}"))
        ax.grid(True, which="major", color=INK2, alpha=0.15, lw=0.5)
        ax.set_title(f"({tag}) {panel['title']}\n$p_0$ = {panel['p0']:.3f}, {PROTOCOL[protocol]}",
                     fontsize=6.5, color=INK, loc="left", pad=11)
        ax.tick_params(labelsize=6, colors=INK2)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
    for ax in axes[1]:
        ax.set_xlabel(r"PageHinkley threshold $\lambda$", fontsize=7, color=INK)
    for ax in axes[:, 0]:
        ax.set_ylabel("recall, precision", fontsize=7, color=INK)
    found = {}
    for ax in axes.flat:
        for h, lab in zip(*ax.get_legend_handles_labels()):
            found.setdefault(lab, h)
    labels = [lab for lab in LEGEND_ORDER if lab in found]
    fig.legend([found[lab] for lab in labels], labels, loc="lower center", ncol=3, fontsize=6, frameon=False)
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=300, metadata={"Software": None})
    plt.close(fig)
    print(f"[INFO] wrote {path}")


# ══════════════════════════════════════════════════════════════════════════════
def main():
    grid_de = lat._grid()
    tasks = [(stream, de) for stream in ("canonical", "rotation") for de in grid_de]
    res = Parallel(n_jobs=-1)(delayed(synthetic_partition)(s, de) for s, de in tasks)
    by = {(r["stream"], round(r["delta_e"], 6)): r for r in res}
    a, b = by[("canonical", DELTA_E)], by[("rotation", DELTA_E)]
    a["title"], b["title"] = "Bernoulli boundary shift", "Rotation, $\\eta = 0.05$"
    lam50 = GRID.index(ssot.S8_DECISION_LAMBDA)
    a["published"] = [{"label": "starvation certificate, lambda = 50", "short": "$\\lambda = 50$", "mode": "starvation",
                       "lambda": ssot.S8_DECISION_LAMBDA, "recall": a["recall"][lam50],
                       "precision": a["precision"][lam50]}]
    b["published"] = []
    c = proteus_panel()
    c["title"] = "ProteuS, PHT + ARF($c = 1$)"
    d, e, f = (insects_panel(v) for v in INSECTS)
    d["title"], e["title"], f["title"] = ("INSECTS abrupt", "INSECTS gradual", "INSECTS reoccurring")
    panels = [rule_readings(p) for p in (a, b, c, d, e, f)]
    points = [p for panel in panels for p in panel["published"]]
    dm3 = "HOLDS" if points and all(p["DM3"] == "HOLDS" for p in points) else "FAILS"

    draw(list(zip("abcdef", panels, ["passive", "passive", "reset", "reset", "reset", "reset"])),
         OUT_DIR / "figures" / "Fig_S10_dual_mode.png")
    payload = {"panels": {tag: p for tag, p in zip("abcdef", panels)},
               "DM3_overall": dm3,
               "all_magnitudes": {f"{s}|{de:.6f}": rule_readings(dict(r)) for (s, de), r in sorted(by.items())},
               "rules": {"recall_min": RECALL_MIN, "precision_min": PRECISION_MIN, "tau_tol": TAU_TOL,
                         "delta_p": ssot.DELTA_P, "grid": GRID},
               "env": lat._env()}
    lat._write_json(OUT_DIR / "tables" / "s10_dual_mode.json", payload)
    for tag, p in zip("abcdef", panels):
        w = p["window"]
        print(f"  ({tag}) {p['title']:32s} p0={p['p0']:.3f} window="
              f"{'EMPTY' if w is None else (w['lo'], w['hi'], 'contiguous' if w['contiguous'] else 'NON-CONTIGUOUS')}"
              f" lambda_FA={p['lambda_FA']:.2f} lambda_op={p['lambda_op']} DM2={p['DM2']} "
              + " ".join(f"[{q['mode']} @ {q['lambda']:.2f}: R={q['recall']:.3f} "
                         f"P={q['precision'] if q['precision'] is None else round(q['precision'], 3)} "
                         f"-> {q['DM3']}]" for q in p["published"]))
    print(f"--- DM3 overall: {dm3}")
    return payload


if __name__ == "__main__":
    main()
