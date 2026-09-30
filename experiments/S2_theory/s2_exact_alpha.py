"""Exact windowed level of the restarted StrictCUSUM, and the floors re-derived from it.

Stream H10, objections CONS-013/CONS-016. The manuscript's Definition 2 replaces the
geometric approximation alpha ~ W/ARL_0 by the exact first-passage probability of the
monitor as implemented: statistic restarted at tau* with S = 0, reference p0_hat plugged
in from the 1000 pre-drift steps, increments +(1 - p0 - delta_P) on an error and
-(p0 + delta_P) otherwise, reflected at 0. Under the i.i.d. Bernoulli(p0) null the
windowed level alpha = P0(max_{t <= W} S_t >= lambda) is computed exactly by a lattice
recursion on the increment lattice.

The chord floor of Theorem 1 is then evaluated at that alpha, at the theoretical marginal
Delta_max = 0.3268 and at the measured almost-sure bound Delta_max = 0.36 (the post-change
conditional error probability of the model frozen at tau*, results/S8_ab_initio: per-run
post-drift error mean max 0.358 absolute, 0.333 in excess of e_pre, over 100 runs; plus
three standard errors of the 2500-step estimate, 0.009).

Output: results/S2_theory/tables/s2_exact_alpha.json
"""
import json
from math import gcd, log
from pathlib import Path

import numpy as np

ROOT_DIR = Path(__file__).resolve().parents[2]
sys_path = __file__
import sys  # noqa: E402

sys.path.insert(0, str(ROOT_DIR))
from config import experiment_ssot as ssot  # noqa: E402

OUT = ROOT_DIR / "results" / "S2_theory" / "tables" / "s2_exact_alpha.json"
DP = 0.01
EPS = 0.05
W_FIRST = 57.4                      # tau_swap^(1/M), s6_causal.json
W_TRANSIENT = 391                   # mean argmax of the delta_P = 0.01 walk, s6_window_budgets.json
W_ARGMAX_005 = 611.9                 # mean argmax of the delta_P = 0.005 walk (superseded reading)
W_LAST_CROSS = 1367                  # median last crossing at rho = 0.01, s6_window_budgets.json
P0 = 0.024
BAND = [0.015, 0.032]
LADDER = [8.0, 15.0, 25.0, 50.0]
N_STAT = 30
EPS_MARGIN_FIRST = (W_FIRST / 2 * log(1 / EPS)) ** 0.5     # 9.2724, s2_gate_T20.json
DMAX_THEORY = 0.3268
DMAX_MEASURED = 0.36


def exact_alpha(p0, lam, W, dp=DP):
    """P0(max_{t<=W} S_t >= lam) for the restarted, reflected CUSUM -- exact lattice DP."""
    up = int(round((1 - p0 - dp) * 10000))
    dn = int(round((p0 + dp) * 10000))
    g = gcd(up, dn)
    up, dn = up // g, dn // g
    L = int(round(lam * 10000 / g))
    assert abs(lam * 10000 / g - L) < 1e-9, (p0, lam, g)
    p = np.zeros(L, dtype=np.float64)
    p[0] = 1.0
    crossed = 0.0
    for _ in range(int(W)):
        new = np.zeros_like(p)
        if up < L:
            new[up:] += p[:L - up] * p0
            crossed += p[L - up:].sum() * p0
        else:
            crossed += p.sum() * p0
        if dn < L:
            new[:L - dn] += p[dn:] * (1 - p0)
            new[0] += p[:dn].sum() * (1 - p0)
        else:
            new[0] += p.sum() * (1 - p0)
        p = new
    return float(crossed)


def d_kl(a, b):
    return a * log(a / b) + (1 - a) * log((1 - a) / (1 - b))


def chord_floor(p0, dmax, W, alpha, dp=DP, eps=EPS):
    coef = dmax / d_kl(p0 + dmax, p0)
    return {"floor": coef * d_kl(1 - eps, alpha) - W * dp, "coef": coef,
            "chi2_coef": p0 * (1 - p0) / dmax, "alpha": alpha}


def main():
    out = {"delta_P": DP, "eps": EPS, "p0": P0, "band": BAND, "ladder": LADDER,
           "W_first_swap": W_FIRST, "W_transient_argmax_dp001": W_TRANSIENT,
           "W_last_crossing_dp001": W_LAST_CROSS,
           "dmax": {"theoretical_marginal": DMAX_THEORY, "measured_a.s.": DMAX_MEASURED},
           "alpha_exact": {}, "floors": {}, "table_first_swap": {}}

    for p0b in [P0, *BAND]:
        for lam in LADDER:
            out["alpha_exact"][f"W57_lam{lam:g}_p0{p0b:g}"] = exact_alpha(p0b, lam, 57)
    for W, tag in ((W_TRANSIENT, "W391"), (W_ARGMAX_005, "W612"), (W_LAST_CROSS, "W1367")):
        for lam in (15.0, 50.0):
            out["alpha_exact"][f"{tag}_lam{lam:g}_p0{P0:g}"] = exact_alpha(P0, lam, int(W))

    for dmax, tag in ((DMAX_THEORY, "dmax_theory"), (DMAX_MEASURED, "dmax_meas")):
        for p0b in [P0, *BAND]:
            a = out["alpha_exact"][f"W57_lam50_p0{p0b:g}"]
            out["floors"][f"{tag}_W57_lam50_p0{p0b:g}"] = chord_floor(p0b, dmax, W_FIRST, a)
        for lam in LADDER:
            a = out["alpha_exact"][f"W57_lam{lam:g}_p0{P0:g}"]
            out["floors"][f"{tag}_W57_lam{lam:g}_p0{P0:g}"] = chord_floor(P0, dmax, W_FIRST, a)
        for W, tagw in ((W_TRANSIENT, "W391"), (W_ARGMAX_005, "W612"), (W_LAST_CROSS, "W1367")):
            a = out["alpha_exact"][f"{tagw}_lam50_p0{P0:g}"]
            out["floors"][f"{tag}_{tagw}_lam50_p0{P0:g}"] = chord_floor(P0, dmax, W, a)

    for lam in LADDER:
        a = out["alpha_exact"][f"W57_lam{lam:g}_p0{P0:g}"]
        out["table_first_swap"][f"lam{lam:g}"] = {
            "alpha": a, "log_1_over_alpha": log(1 / a),
            "R_CUSUM": lam + EPS_MARGIN_FIRST,
            "R_ADWIN": (W_FIRST / 2 * log(4 * W_FIRST / a)) ** 0.5 + EPS_MARGIN_FIRST,
            "R_KSWIN": (N_STAT * log(2 / a)) ** 0.5 + EPS_MARGIN_FIRST}

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=1, sort_keys=True, default=float) + "\n",
                   encoding="utf-8")
    print(f"written: {OUT}")
    for k, v in out["table_first_swap"].items():
        print(k, {kk: round(vv, 4) for kk, vv in v.items()})


if __name__ == "__main__":
    main()
