import shutil
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
FIGS = HERE / "figures"
FIGS.mkdir(exist_ok=True)
ROOT = HERE.parent.parent

for f in (HERE / "fonts").glob("*.ttf"):
    font_manager.fontManager.addfont(str(f))

plt.rcParams.update({
    "font.family": "Carlito",
    "text.color": "#2C3E50",
    "axes.edgecolor": "#5D6D7E",
    "axes.labelcolor": "#2C3E50",
    "axes.linewidth": 0.8,
    "xtick.color": "#5D6D7E",
    "ytick.color": "#5D6D7E",
    "xtick.labelsize": 7.5,
    "ytick.labelsize": 7.5,
    "axes.labelsize": 8,
    "savefig.transparent": True,
})

TEAL_DARK = "#00748C"
TEAL = "#1B7A8A"
BLUE = "#2980B9"
ORANGE = "#E08000"
RED = "#C0392B"
RED_LT = "#E74C3C"
GREEN = "#27AE60"
TXT_DARK = "#2C3E50"
TXT_BODY = "#5D6D7E"
TXT_FAINT = "#8A9BB0"
BG_CREAM = "#FFF8F0"


def fr(t):
    return t.replace(" :", "\u00A0:").replace(" ;", "\u00A0;")


def frnum(x, nd):
    return f"{x:.{nd}f}".replace(".", ",")


def save(fig, name):
    fig.savefig(FIGS / name, dpi=200, transparent=True)
    plt.close(fig)


def load_bell():
    return pd.read_csv(ROOT / "results" / "S13_evidence_bell" / "evidence_bell.csv",
                       float_precision="round_trip")


# FIG-1 (slide 10) -- les deux termes de la borne
def fig1_borne_deux_termes():
    df = load_bell()
    deltas = [0.10, 0.33, 0.50]
    eps = 0.05
    W = [float(df.loc[(df["delta_e"] - d).abs().idxmin(), "tau_arf_median"])
         for d in deltas]
    drift = [(d - 0.01) * w for d, w in zip(deltas, W)]
    fluct = [np.sqrt(w / 2.0 * np.log(w / eps)) for w in W]
    x = np.arange(3)
    fig, ax = plt.subplots(figsize=(4.6, 2.2))
    ax.bar(x, drift, width=0.55, color=TEAL, label="terme de dérive μW")
    ax.bar(x, fluct, width=0.55, bottom=drift, color=ORANGE,
           label="terme de fluctuation √((W/2)·ln(W/ε))")
    for i in range(3):
        ax.text(i, drift[i] / 2, frnum(drift[i], 1), ha="center", va="center",
                color="white", fontsize=7.5, fontweight="bold")
        ax.text(i, drift[i] + fluct[i] / 2, frnum(fluct[i], 1), ha="center",
                va="center", color="white", fontsize=7.5, fontweight="bold")
    ax.text(0, drift[0] + fluct[0] + 4, "la fluctuation domine", ha="center",
            fontsize=8, fontweight="bold", color=ORANGE)
    ax.set_xticks(x)
    ax.set_xticklabels([f"Δe = {frnum(d, 2)}\nW = {frnum(w, 1)}"
                        for d, w in zip(deltas, W)], fontsize=7.5)
    ax.set_ylabel("valeur du terme")
    ax.set_ylim(0, 96)
    ax.legend(fontsize=6.5, frameon=False, loc="upper right")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    save(fig, "fig1_borne_deux_termes.png")


# FIG-2 (slide 12) -- décomposition causale
def fig2_decomposition_causale():
    fig = plt.figure(figsize=(5.1, 2.6))
    ax = fig.add_axes([0.06, 0.62, 0.90, 0.30])
    ax.barh([0], [98.64], height=0.5, color=TEAL)
    ax.barh([0], [0.71], left=98.64, height=0.5, color=ORANGE)
    ax.barh([0], [0.56], left=99.35, height=0.5, color=RED)
    ax.text(49, 0, "98,64 %  [98,48 ; 98,82]", ha="center", va="center",
            color="white", fontsize=7.5, fontweight="bold")
    ax.annotate("0,71 %  [0,63 ; 0,78]", xy=(99.0, -0.30), xytext=(70, -0.78),
                fontsize=7, color=ORANGE, ha="center",
                arrowprops=dict(arrowstyle="-", color=ORANGE, lw=0.8))
    ax.annotate("0,56 %  [0,47 ; 0,67]", xy=(99.6, 0.30), xytext=(70, 0.78),
                fontsize=7, color=RED, ha="center",
                arrowprops=dict(arrowstyle="-", color=RED, lw=0.8))
    ax.set_xlim(0, 100)
    ax.set_ylim(-1.05, 1.05)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_yticks([])
    ax.tick_params(labelsize=6.5, pad=1)
    ax.set_xlabel("contribution à l'effacement (%)", fontsize=7, labelpad=1)

    centers = [0.22, 0.50, 0.78]
    labels = ["0/100", "18/100", "49/100"]
    caps = ["forêt complète", "sans remplacements\npostérieurs au premier",
            "sans aucun\nremplacement"]
    side_x = 0.15
    side_y = side_x * 5.1 / 2.6
    for cx, lab, cap in zip(centers, labels, caps):
        fig.patches.append(Rectangle((cx - side_x / 2, 0.30 - side_y / 2),
                                     side_x, side_y, facecolor="white",
                                     edgecolor=TEAL_DARK, lw=1.2, zorder=3))
        fig.text(cx, 0.30, lab, ha="center", va="center", fontsize=10,
                 fontweight="bold", color=TEAL_DARK, zorder=4)
        fig.text(cx, 0.09, cap, ha="center", va="center", fontsize=6.5,
                 color=TXT_BODY)
    for a, b in zip(centers[:-1], centers[1:]):
        fig.add_artist(FancyArrowPatch(
            (a + side_x / 2 + 0.012, 0.30), (b - side_x / 2 - 0.012, 0.30),
            arrowstyle="-|>", mutation_scale=12, color=ORANGE, lw=2))
    fig.text(0.50, 0.022, "0,71 % du volume, 31 points de détection",
             ha="center", fontsize=8, fontweight="bold", color=ORANGE)
    save(fig, "fig2_decomposition_causale.png")


# FIG-3 (slide 16) -- généralité et plancher trivial
def fig3_generalite_plancher():
    df = load_bell()
    x = np.linspace(0.02, 0.50, 200)
    orig = np.full_like(x, 0.995)
    corr = 0.77 + (0.33 - 0.77) * (x - 0.02) / 0.48
    fig, ax1 = plt.subplots(figsize=(4.7, 2.5))
    ax1.plot(x, orig, color=RED, lw=1.8, label="famille d'origine")
    ax1.plot(x, corr, color=GREEN, lw=1.8, label="générateur corrigé")
    ax1.set_xlim(0.02, 0.50)
    ax1.set_ylim(0, 1.1)
    ax1.set_xlabel("Δe")
    ax1.set_ylabel("taux de manqués")
    ax2 = ax1.twinx()
    ax2.plot(df["delta_e"], df["skill_episode"], color=TXT_FAINT, lw=1.0,
             label="score d'habileté")
    ax2.axhline(0, color=TXT_FAINT, lw=0.8, ls=(0, (3, 3)))
    ax2.set_ylim(-3.8, 1.0)
    ax2.set_ylabel("score d'habileté")
    ax2.axvspan(0.482, 0.50, facecolor="none", hatch="////",
                edgecolor=TXT_FAINT, lw=0, alpha=0.6)
    ax1.text(0.4905, 0.52, "régime\ndégénéré", rotation=90, ha="center",
             va="center", fontsize=6.5, color=TXT_BODY)
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, fontsize=6.5, frameon=False, loc="lower left")
    save(fig, "fig3_generalite_plancher.png")


# FIG-4 (slide 18) -- deux panneaux
def fig4_deux_panneaux():
    fig, (axl, axr) = plt.subplots(1, 2, figsize=(4.9, 2.4))
    vals = [10.57, 1.27]
    err = [[10.57 - 9.354, 1.27 - 1.156], [12.114 - 10.57, 1.426 - 1.27]]
    axl.bar([0, 1], vals, width=0.5, color=[RED_LT, GREEN], yerr=err,
            capsize=3, ecolor=TXT_DARK, error_kw=dict(lw=1))
    axl.axhline(1.00, color=TXT_BODY, lw=1, ls=(0, (3, 3)))
    axl.text(1.42, 1.15, "parité", fontsize=7, color=TXT_BODY, ha="right")
    axl.annotate("effet seuil, −89,9 %", xy=(0.95, 2.6), xytext=(0.55, 7.2),
                 fontsize=8, fontweight="bold", color=ORANGE, ha="center",
                 arrowprops=dict(arrowstyle="-|>", color=ORANGE, lw=1.6))
    axl.text(0, 12.6, "10,57", ha="center", fontsize=8, fontweight="bold",
             color=TXT_DARK)
    axl.text(1, 2.1, "1,27", ha="center", fontsize=8, fontweight="bold",
             color=TXT_DARK)
    axl.set_xticks([0, 1])
    axl.set_xticklabels(["écart publié", "à budget égal"], fontsize=7.5)
    axl.set_ylabel("rapport d'erreur")
    axl.set_ylim(0, 13.5)
    axl.set_xlim(-0.5, 1.5)

    axr.plot([0, 8, 15, 20], [1, 1, 0, 0], color=TEAL_DARK, lw=1.8)
    axr.axvspan(8, 15, color=TXT_FAINT, alpha=0.25)
    axr.text(11.5, 0.5, "plafond de preuve mesuré", rotation=90, ha="center",
             va="center", fontsize=6.5, color=TXT_BODY)
    axr.scatter([15], [0], s=36, color=RED, zorder=5)
    axr.text(15, 0.09, "seuil publié", fontsize=7, fontweight="bold",
             color=RED, ha="center")
    axr.scatter([5], [1], s=36, color=GREEN, zorder=5)
    axr.text(5, 1.07, "1080/1080, 6,05 pas", fontsize=7, fontweight="bold",
             color=GREEN, ha="center")
    axr.set_xlim(0, 20)
    axr.set_ylim(-0.1, 1.2)
    axr.set_xlabel("λ")
    axr.set_ylabel("taux de détection")
    axr.set_xticks([0, 5, 10, 15, 20])
    fig.subplots_adjust(wspace=0.38, left=0.10, right=0.97, top=0.96,
                        bottom=0.13)
    save(fig, "fig4_deux_panneaux.png")


# FIG-5 (slide 15) -- boucle fermée
def fig5_boucle_fermee():
    fig = plt.figure(figsize=(4.6, 2.7))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    def box(x, y, w, h, text, ec, fc="white", lw=1.2, fs=7.0):
        fig.patches.append(FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.006", facecolor=fc,
            edgecolor=ec, lw=lw, zorder=3))
        fig.text(x + w / 2, y + h / 2, text, ha="center", va="center",
                 fontsize=fs, color=TXT_DARK, zorder=4)

    def arrow(pA, pB, color=TEAL_DARK, lw=1.4, ms=13, cs=None):
        fig.add_artist(FancyArrowPatch(
            pA, pB, arrowstyle="-|>", mutation_scale=ms, color=color, lw=lw,
            connectionstyle=cs, zorder=2))

    box(0.01, 0.80, 0.16, 0.13, "flux X", TEAL_DARK)
    box(0.24, 0.80, 0.20, 0.13, "classifieur\nadaptatif", TEAL, lw=1.6)
    box(0.51, 0.80, 0.16, 0.13, "prédiction", TEAL)
    box(0.74, 0.80, 0.25, 0.13, "comparaison\nà l'étiquette", TEAL)
    box(0.76, 0.42, 0.15, 0.13, "erreur e_t", ORANGE, lw=1.8)
    box(0.46, 0.42, 0.18, 0.13, "moniteur\nexterne", BLUE)
    box(0.22, 0.42, 0.14, 0.13, "alarme", RED)
    fig.patches.append(FancyBboxPatch(
        (0.01, 0.30), 0.19, 0.34, boxstyle="round,pad=0.006",
        facecolor=BG_CREAM, edgecolor=ORANGE, lw=1.2, zorder=3))
    fig.text(0.105, 0.585, "Trois objectifs", ha="center", fontsize=7,
             fontweight="bold", color=ORANGE, zorder=4)
    fig.text(0.105, 0.45, "s'adapter\nsurveiller\nalarmer", ha="center",
             va="center", fontsize=7, color=TXT_DARK, zorder=4)

    arrow((0.175, 0.865), (0.232, 0.865))
    arrow((0.445, 0.865), (0.502, 0.865))
    arrow((0.675, 0.865), (0.732, 0.865))
    arrow((0.835, 0.795), (0.835, 0.557))
    arrow((0.755, 0.485), (0.648, 0.485))
    arrow((0.452, 0.485), (0.368, 0.485))
    arrow((0.76, 0.50), (0.40, 0.79), color=ORANGE, lw=3.0, ms=18)
    fig.text(0.58, 0.665, "le modèle agit sur la grandeur mesurée",
             ha="center", fontsize=7, style="italic", color=ORANGE)
    save(fig, "fig5_boucle_fermee.png")


# FIG-6 (slide 27) -- retard d'étiquetage
def fig6_retard_etiquetage():
    fig, ax = plt.subplots(figsize=(9.0, 2.5))
    ax.set_xlim(0, 700)
    ax.set_ylim(-0.12, 1.02)
    ax.axis("off")

    ax.plot([0, 700], [0.06, 0.06], color=TXT_BODY, lw=1)
    for t in [0, 150, 300, 450, 600]:
        ax.plot([t, t], [0.06, 0.02], color=TXT_BODY, lw=0.8)
        ax.text(t, -0.09, str(t), ha="center", fontsize=7, color=TXT_BODY)
    ax.text(696, -0.09, "pas", ha="right", fontsize=7, color=TXT_BODY)

    # frise haute : moniteur seul retardé
    ax.text(5, 0.72, "moniteur seul retardé", va="center", fontsize=8,
            fontweight="bold", color=TXT_DARK)
    ax.plot([150, 150], [0.55, 0.89], color=TEAL_DARK, lw=1.5)
    ax.text(150, 0.92, "rupture", ha="center", fontsize=7.5,
            fontweight="bold", color=TEAL_DARK)
    ax.plot([450, 450], [0.55, 0.89], color=TXT_DARK, lw=1.5)
    ax.text(450, 0.92, "effacement", ha="center", fontsize=7.5, color=TXT_DARK)
    ax.add_patch(Rectangle((250, 0.67), 200, 0.10, facecolor=RED, alpha=0.45))
    ax.text(350, 0.615, "fenêtre utile rétrécie", ha="center", fontsize=7,
            color=RED)
    ax.scatter([400], [0.72], marker="D", s=28, color=RED, zorder=5)
    ax.text(400, 0.80, "alarme repoussée de ℓ", ha="center", fontsize=7,
            color=RED)
    ax.annotate("", xy=(250, 0.50), xytext=(150, 0.50),
                arrowprops=dict(arrowstyle="<|-|>", color=TXT_BODY, lw=1))
    ax.text(200, 0.545, "ℓ = 100 pas", ha="center", fontsize=7,
            color=TXT_BODY)

    # frise basse : retard partagé
    ax.text(5, 0.30, "retard partagé", va="center", fontsize=8,
            fontweight="bold", color=TXT_DARK)
    ax.plot([150, 150], [0.13, 0.47], color=TEAL_DARK, lw=1.5)
    ax.plot([549.8, 549.8], [0.13, 0.47], color=TXT_DARK, lw=1.5)
    ax.text(549.8, 0.50, "effacement reculé de 0,998·ℓ", ha="center",
            fontsize=7.5, color=TXT_DARK)
    ax.add_patch(Rectangle((250, 0.25), 299.8, 0.10, facecolor=GREEN,
                           alpha=0.45))
    ax.text(400, 0.195, "fenêtre utile conservée", ha="center", fontsize=7,
            color=GREEN)
    ax.annotate("", xy=(250, 0.13), xytext=(150, 0.13),
                arrowprops=dict(arrowstyle="<|-|>", color=TXT_BODY, lw=1))
    ax.text(200, 0.165, "ℓ", ha="center", fontsize=7, color=TXT_BODY)
    save(fig, "fig6_retard_etiquetage.png")


def copy_fig0():
    src = ROOT / "results" / "S13_evidence_bell" / "figures" / "Fig_S13_evidence_bell.png"
    shutil.copy(src, FIGS / "Fig_S13_evidence_bell.png")


if __name__ == "__main__":
    copy_fig0()
    fig1_borne_deux_termes()
    fig2_decomposition_causale()
    fig3_generalite_plancher()
    fig4_deux_panneaux()
    fig5_boucle_fermee()
    fig6_retard_etiquetage()
    print(f"figures written to {FIGS}")
    for p in sorted(FIGS.glob("*.png")):
        print(f"  {p.name}")
