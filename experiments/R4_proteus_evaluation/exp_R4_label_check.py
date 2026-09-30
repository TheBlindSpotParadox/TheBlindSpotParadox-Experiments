# exp_R4_label_check.py
# =============================================================================
# LABEL-CONSTRUCTION CHECK (stream H10, objection CONS-014).
#
# The published ProteuS label is a step function of time: `regime = (f_t > 0.5)`
# with f_t = expit(4 (t - tp) / w), so it is 0 at every t <= 4000 and 1 at every
# t >= 4001 for every seed, transition, GARCH regime and drift width. The monitored
# error stream is therefore a run of zeros followed by a short burst of ones,
# whatever the volatility process, and the zero pre-change error is a property of
# that construction rather than of the pipelines.
#
# This script re-runs the two pipelines of the published contrast -- PHT + ARF
# (c=1) and PHT + HT -- on streams whose COVARIATES are byte-identical to the
# published ones (same generator, same seeds, same GARCH regimes) but whose label
# is a half-plane rule on the covariates, rotated at tp, with declared label noise
# eta = 0.05:
#
#     y_t = 1[ cos(phi_t) r_t + sin(phi_t) vol_t > 0 ]  flipped w.p. eta,
#     phi_t = pi/4 for t < tp,  pi/4 + pi Delta_e / (1 - 2 eta) for t >= tp.
#
# The label takes both values before tp, the covariates predict it up to the
# declared noise, and the pre-change error is the Bayes rate eta rather than zero,
# so a false-alarm budget exists. A third pipeline replaces the classifier by a
# predictor returning the last observed label (no learning at all), so each F1 is
# printed beside that baseline. The external monitor, the reset protocol and the
# tolerance window are the published R4 ones; only the label law changes.
#
# Usage:  exp_R4_label_check.py [n_seeds]      (default 30, the published pool)
# Output: results/R4_proteus_evaluation/data/exp_R4_label_check.csv
# =============================================================================
import itertools
import random
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from joblib import Parallel, delayed

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exp_R4_main_table import (  # noqa: E402
    ETF_PARAMS_A, ETF_PARAMS_B, TICKERS, TRANSITIONS, evaluate, make_arf, make_ht, pht,
    run_concept_drift,
)

warnings.filterwarnings("ignore")

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))
from config import experiment_ssot as ssot  # noqa: E402

RESULTS_DIR = ROOT_DIR / "results" / "R4_proteus_evaluation" / "data"
OUT_CSV = RESULTS_DIR / "exp_R4_label_check.csv"

ETA = 0.05            # declared label noise: Bayes error of the label rule
DELTA_E = 0.30        # rotation magnitude, the canonical operating point
PHI_PRE = np.pi / 4
PHI_POST = np.pi / 4 + np.pi * DELTA_E / (1 - 2 * ETA)


def covariates(p_from, p_to, regime_name, w, n_steps, tp, seed):
    """The published simulate_stream, up to (and excluding) the label column.

    Byte-identical covariates: same np.random.seed(seed), same draw order."""
    np.random.seed(seed)
    t_arr = np.arange(n_steps, dtype=float)
    f_t = 1.0 / (1.0 + np.exp(-4.0 * (t_arr - tp) / w))
    mu_t = p_from["mu"] * (1 - f_t) + p_to["mu"] * f_t
    r, h, eps = np.zeros(n_steps), np.zeros(n_steps), np.zeros(n_steps)
    if regime_name == "IID":
        var_from = p_from["omega"] / (1 - p_from["alpha"] - p_from["beta"])
        var_to = p_to["omega"] / (1 - p_to["alpha"] - p_to["beta"])
        var_t = var_from * (1 - f_t) + var_to * f_t
        r = mu_t + np.sqrt(var_t) * np.random.standard_normal(n_steps)
    else:
        omega_t = p_from["omega"] * (1 - f_t) + p_to["omega"] * f_t
        alpha_t = p_from["alpha"] * (1 - f_t) + p_to["alpha"] * f_t
        beta_t = p_from["beta"] * (1 - f_t) + p_to["beta"] * f_t
        nu = 7.0
        z_arr = np.random.standard_t(nu, size=n_steps) * np.sqrt((nu - 2) / nu)
        h[0] = omega_t[0] / (1 - alpha_t[0] - beta_t[0])
        eps[0] = np.sqrt(h[0]) * z_arr[0]
        r[0] = mu_t[0] + eps[0]
        for t in range(1, n_steps):
            h[t] = max(omega_t[t] + alpha_t[t] * eps[t - 1] ** 2 + beta_t[t] * h[t - 1], 1e-12)
            eps[t] = np.sqrt(h[t]) * z_arr[t]
            r[t] = mu_t[t] + eps[t]
    rs = pd.Series(r)
    vol = rs.rolling(20, min_periods=1).std(ddof=1).fillna(0).values
    return r, vol


def predictable_label_stream(p_from, p_to, regime_name, w, seed, n_steps=ssot.R4_N_STEPS,
                             tp=ssot.R4_T_DRIFT):
    """(df, drift_points, label stats) with the rotated half-plane label.

    The label noise is drawn from a generator spawned AFTER the covariate block, so
    the covariates are byte-identical to the published streams at equal seed."""
    r, vol = covariates(p_from, p_to, regime_name, w, n_steps, tp, seed)
    rng = np.random.default_rng(seed * 1_000_003 + 17)
    phi = np.full(n_steps, PHI_PRE)
    phi[tp:] = PHI_POST
    score = np.cos(phi) * r + np.sin(phi) * vol
    y = (score > 0).astype(int)
    flips = rng.random(n_steps) < ETA
    y = np.where(flips, 1 - y, y)
    df = pd.DataFrame({"log_return": r, "rolling_vol": vol, "regime": y})
    pre = y[:tp].mean()
    post = y[tp:].mean()
    return df, [tp], {"pre_label_rate": float(pre), "post_label_rate": float(post)}


class LastLabel:
    """Predictor returning the last observed label. No learning, no state but one bit."""

    def __init__(self):
        self.last = None

    def predict_one(self, x):
        return self.last

    def learn_one(self, x, y):
        self.last = int(y)

    def clone(self):
        return LastLabel()


def process_transition_seed(trans, seed):
    from_t, to_t, w, name = trans
    safe_seed = seed % (2 ** 31 - 1)
    random.seed(safe_seed)
    np.random.seed(safe_seed)
    out = []
    for regime, params in [("IID", ETF_PARAMS_A), ("Cal. A", ETF_PARAMS_A), ("Cal. B", ETF_PARAMS_B)]:
        df, dpts, stats = predictable_label_stream(params[from_t], params[to_t], regime, w, seed)
        tau = max(1000, w)
        n = len(df)

        def pre_change_error(model_factory):
            m = model_factory()
            errs = []
            yv, Xv = df["regime"].values, df[["log_return", "rolling_vol"]].values
            for t in range(ssot.R4_T_DRIFT):
                x = {0: Xv[t, 0], 1: Xv[t, 1]}
                yp = m.predict_one(x)
                errs.append(float(int(yv[t]) != (yp or 0)))
                m.learn_one(x, int(yv[t]))
            return float(np.mean(errs))

        for label, factory in [("PHT + ARF", lambda: make_arf(safe_seed, 1)),
                               ("PHT + HT", make_ht),
                               ("PHT + LastLabel", LastLabel)]:
            dets = run_concept_drift(df, factory(), pht)
            add, f1 = evaluate(dets, dpts, n, tau)
            e_pre = pre_change_error(factory)
            out.append({"regime": regime, "pipeline": label, "transition": name, "w": w,
                        "seed": seed, "F1": f1, "ADD": add, "n_alarms": len(dets),
                        "pre_change_error": e_pre, **stats})
    return out


def main(n_seeds=30):
    seeds = list(ssot.R4_SEEDS[:n_seeds])
    res = Parallel(n_jobs=-1, verbose=2)(
        delayed(process_transition_seed)(t, s) for t in TRANSITIONS for s in seeds)
    rows = [r for block in res for r in block]
    df = pd.DataFrame(rows)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_CSV, index=False)
    agg = df.groupby(["regime", "pipeline"]).agg(
        F1_mean=("F1", "mean"), F1_sd=("F1", "std"), alarms=("n_alarms", "mean"),
        e_pre=("pre_change_error", "mean"), n=("F1", "size"))
    print(agg.round(4))
    print(f"\nwritten: {OUT_CSV}")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 30)
