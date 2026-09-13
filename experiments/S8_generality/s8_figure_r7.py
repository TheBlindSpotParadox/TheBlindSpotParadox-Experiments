"""Stream S8 / T8.6 -- the standalone Figure 4 of the clock-mismatch regime.

`space_constraints_audit.md` section 2.1 reserves this. The manuscript anchor is textual, not
numerical: `% Figure 4 merged with Figure 2 above to respect ICDM page limits.` (.tex:327,
`sec:hardware`, outside the zone CLAUDE.md excludes).

R7 is NOT re-executed. `results/R7_clock_mismatch/tables/exp_R7_regime1_miss_curve.csv` already
carries `config, delta_e, miss_rate` for the three clock configurations over the twenty canonical
magnitudes, and that file is the sole input. Committed R7 artifacts stay byte-identical.

The three bands the compact summary table reports (`exp_R7_regime1_miss_summary.tex`) are drawn as
background spans, so the figure and the table are readable against each other rather than as two
independent claims.

The manuscript copy is NOT deposited by this stream. Inserting a figure changes the pagination and
`space_constraints_audit.md` section 4 makes that wait for the M8 arbitration on the target venue;
`tests/test_manuscript_integrity.py::test_manuscript_assets_match_the_pipeline` globs
`results/*/figures/<name>`, so the twin is in place the day the copy lands.

Output: results/S8_r7_figure/figures/Fig_R7_clock_mismatch.png
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))
from config import experiment_ssot as ssot  # noqa: E402

CURVE = ssot.RESULTS_DIR / "R7_clock_mismatch" / "tables" / "exp_R7_regime1_miss_curve.csv"
OUT_DIR = ssot.RESULTS_DIR / "S8_r7_figure" / "figures"

BLUE, ORANGE, RED, GREEN, GRAY = "#04617b", "#E8A000", "#C62828", "#2E7D32", "#546E7A"
CONFIG_STYLE = {
    "A_mismatched": (RED, "-", "o", r"Mismatched  $c_{\mathrm{int}}{=}1,\ c_{\mathrm{ext}}{=}32$"),
    "B_matched": (BLUE, "--", "s", r"Matched  $c_{\mathrm{int}}{=}1,\ c_{\mathrm{ext}}{=}1$"),
    "C_decoupled": (GREEN, "-.", "^", r"Decoupled  $c_{\mathrm{int}}{=}32,\ c_{\mathrm{ext}}{=}1$"),
}
BANDS = [(-np.inf, 0.15), (0.15, 0.35), (0.35, np.inf)]
BAND_LABEL = [r"$\Delta e \leq 0.15$", r"$0.15 < \Delta e \leq 0.35$", r"$\Delta e > 0.35$"]

plt.rcParams.update({"figure.dpi": 300, "font.family": "sans-serif", "font.size": 9,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "mathtext.fontset": "stix"})


def band_means(df):
    """Mean miss rate per (config, band) -- the numbers of exp_R7_regime1_miss_summary.tex."""
    out = {}
    for cid, g in df.groupby("config"):
        out[cid] = [float(g[(g.delta_e > lo) & (g.delta_e <= hi)].miss_rate.mean())
                    for lo, hi in BANDS]
    return out


def figure(df, out_dir=OUT_DIR):
    out_dir.mkdir(parents=True, exist_ok=True)
    means = band_means(df)
    lo, hi = float(df.delta_e.min()), float(df.delta_e.max())

    fig, ax = plt.subplots(figsize=(5.4, 3.4))
    for i, (b_lo, b_hi) in enumerate(BANDS):
        x0, x1 = max(b_lo, lo - 0.02), min(b_hi, hi + 0.02)
        if i % 2 == 0:
            ax.axvspan(x0, x1, color=GRAY, alpha=0.06, lw=0)
        ax.text((x0 + x1) / 2, 1.02, BAND_LABEL[i], ha="center", va="bottom",
                fontsize=7.5, color=GRAY, transform=ax.get_xaxis_transform())

    for cid in ("A_mismatched", "B_matched", "C_decoupled"):
        g = df[df.config == cid].sort_values("delta_e")
        color, ls, marker, label = CONFIG_STYLE[cid]
        ax.plot(g.delta_e, g.miss_rate, color=color, ls=ls, marker=marker, ms=3.2, lw=1.6,
                label=f"{label}   [{', '.join(f'{m:.0%}' for m in means[cid])}]")

    ax.set_xlabel(r"drift magnitude $\Delta e$")
    ax.set_ylabel(r"miss rate  $P(\tau_{\mathrm{ARF}} < \tau_{\mathrm{det}})$")
    ax.set_ylim(-0.03, 1.03)
    ax.set_xlim(lo - 0.02, hi + 0.02)
    ax.grid(axis="y", color=GRAY, alpha=0.18, lw=0.6)
    ax.legend(loc="upper right", frameon=False, fontsize=7, handlelength=2.6,
              title="clock configuration   [band means]", title_fontsize=7)
    fig.tight_layout()
    path = out_dir / ssot.S8_R7_FIGURE_NAME
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path, means


def main():
    if not CURVE.exists():
        raise SystemExit(f"[HALT] R7 curve absent: {CURVE} -- run ./run_experiment_R7.sh")
    df = pd.read_csv(CURVE, float_precision="round_trip")
    path, means = figure(df)
    print(f"[INFO] {len(df)} rows, {df.config.nunique()} configurations x "
          f"{df.delta_e.nunique()} magnitudes")
    for cid, m in sorted(means.items()):
        print(f"    {cid:14s} band means = " + ", ".join(f"{v:.0%}" for v in m))
    print(f"[INFO] wrote {path.relative_to(ssot.ROOT_DIR)}")
    return path


if __name__ == "__main__":
    main()
