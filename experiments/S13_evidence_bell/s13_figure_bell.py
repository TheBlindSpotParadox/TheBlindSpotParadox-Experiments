"""Generates the evidence bell curve figure and the blind-spot map."""
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = REPO_ROOT / "results" / "S13_evidence_bell"
FIG_DIR = DATA_DIR / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

bell = pd.read_csv(DATA_DIR / "evidence_bell.csv", float_precision="round_trip")
bmap = pd.read_csv(DATA_DIR / "blindspot_map.csv", float_precision="round_trip")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), dpi=300)

# Panneau A : Cloche d'évidence E[S_max]
ax1.plot(bell["delta_e"], bell["smax_mean"], "b-o", lw=2, ms=4, label=r"$\mathbb{E}[S_{\max}(H)]$ (Empirical Peak)")
ax1.fill_between(bell["delta_e"], bell["smax_ci_lo"], bell["smax_ci_hi"], color="b", alpha=0.2, label="95% Bootstrap CI")
ax1.axhline(8, color="green", linestyle="--", lw=1.5, label=r"$\lambda = 8$ (Safe / Sub-bell)")
ax1.axhline(25, color="orange", linestyle="--", lw=1.5, label=r"$\lambda = 25$ (Crossover / Secant)")
ax1.axhline(50, color="red", linestyle="--", lw=1.5, label=r"$\lambda = 50$ (Starvation / Dominant)")
ax1.axvline(0.193621, color="grey", linestyle=":", lw=1, label=r"Peak ($\Delta e = 0.1936$)")

ax1.set_xlabel(r"Drift magnitude $\Delta e$", fontsize=11)
ax1.set_ylabel(r"Evidence Peak $S_{\max}$", fontsize=11)
ax1.set_title("(A) The Evidence Bell Curve", fontsize=12, fontweight="bold")
ax1.grid(True, alpha=0.3)
ax1.legend(loc="upper right", fontsize=8.5)

# Panneau B : Carte de détection exacte via pcolormesh (grille non-équidistante)
pivot = bmap.pivot(index="lam", columns="delta_e", values="detect")
X = pivot.columns.to_numpy(dtype=float)
Y = pivot.index.to_numpy(dtype=float)
Z = pivot.to_numpy(dtype=float)

mesh = ax2.pcolormesh(X, Y, Z, cmap="RdYlGn", shading="auto", vmin=0.0, vmax=1.0)
cbar = fig.colorbar(mesh, ax=ax2)
cbar.set_label("Detection Probability", fontsize=10)

ax2.set_xlabel(r"Drift magnitude $\Delta e$", fontsize=11)
ax2.set_ylabel(r"CUSUM Threshold $\lambda$", fontsize=11)
ax2.set_title(r"(B) Detection Probability in $(\Delta e, \lambda)$ plane", fontsize=12, fontweight="bold")
ax2.grid(True, alpha=0.2)

plt.tight_layout()
out_fig = FIG_DIR / "Fig_S13_evidence_bell.png"
plt.savefig(out_fig)
plt.close()
print(f"Figure émise : {out_fig}")