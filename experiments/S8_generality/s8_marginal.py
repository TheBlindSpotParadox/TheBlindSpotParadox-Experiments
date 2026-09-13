"""Stream S8 / T8.3-bis -- the marginal of one tree INSIDE the ARF, and the Hydra factor at budget.

Closes the two open items `transfer_S3.md` section 6 declares NOT PRODUCED for want of an artifact.

  item 1  per-tree tau_i of the ARF. `s3_competing_risks.py:23-27` states it in full: "no committed
          artifact carries the per-tree tau_i of the ARF", only the four order statistics
          tau_swap^(q). CLOSED BY P1 -- `s8_arms.write_per_tree` persists the vector at no simulation
          cost, and `tests/test_S8_generality.py` checks it against the published order statistics.
          Nothing is re-run here for it.
  item 2  the pre-drift error stream OF ONE TREE INSIDE THE ARF. `segment()` records the ENSEMBLE
          error only, so `F_hat` has always been the marginal of the M = 1 arm -- a different object:
          `max_features='sqrt'`, Poisson weighting, different capacity. D4's third gap in
          `s3-decision-rules.md` declares the assimilation; this measures it.

The paired arm is ARF(M = 1), NOT a HAT. `exp_R6_generate_data.py:44-47` builds
`ARFClassifier(n_models=1, drift_detector=ADWIN(clock=1), warning_detector=ADWIN(clock=1))`, whose
base learner is `BaseTreeClassifier(HoeffdingTreeClassifier)` -- a Hoeffding TREE with feature
subsampling, replaced wholesale by an external ADWIN. That is not the Bifet-Gavalda HAT (per-node
ADWIN, alternate subtrees, no global reset) the manuscript cites at .tex:224. Both 4.12x and 7.99x
are measured on that object, so it stays the paired arm; the real
`river.tree.HoeffdingAdaptiveTreeClassifier` enters T8.3 as a distinct family and never as a
substitute here.

D8's decomposition. The Hydra factor is a ratio of internal adaptation times and carries no
threshold, so "at equal budget" cannot mean re-timing it: it means re-deciding it. The decidable
quantity is the margin between the evidence the monitor RECEIVES and the evidence it REQUIRES,

    A(arm)  = median max_t A_unrefl                              measured ceiling
    R(arm)  = lambda(arm) + sqrt(W(arm) / 2 * ln(1 / eps))       requirement, s2bis family_requirements
    W(arm)  = median (tau_erase - tau_swap^(1/M))                measured exploitable transient

and log(A/R) is additive, so the M = 1 against M = 10 contrast splits exactly:

    log[(A_1/R_1) / (A_10/R_10)] = log(A_1/A_10) - log(R_1/R_10)
                                   ensemble-size part   threshold part

At the common nominal threshold both arms take lambda = 50 and the threshold part survives only
through W; at lambda_eq each arm takes the threshold its own pre-drift volatility earns, which is
where bagging's variance reduction enters -- and the per-tree error stream is what makes that
variance visible rather than inferred.

The stream is the CANONICAL family: 4.12x and 7.99x are measured on it, and a re-derivation on
another generator would not be a re-derivation.

Output: results/S8_marginal/data/s8_marginal_runs.parquet
        results/S8_marginal/data/s8_marginal_per_tree.parquet
        results/S8_marginal/tables/s8_marginal_hydra.json

Usage:  PYTHONHASHSEED=0 python experiments/S8_generality/s8_marginal.py [demo|smoke|full|read]
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from tqdm import tqdm

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "S6_synchronized_traces"))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "S6_synchronized_traces" / "gates"))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "S8_generality"))

import s6_defs as defs  # noqa: E402
import s6_runner as runner  # noqa: E402
import s8_mechanisms as mech  # noqa: E402
import _gate_common as common  # noqa: E402
from config import experiment_ssot as ssot  # noqa: E402

RESULTS_DIR = ssot.RESULTS_DIR / "S8_marginal"
N_STEPS = ssot.S8_N_STEPS
T_DRIFT = ssot.S8_T_DRIFT
WARMUP = ssot.S8_WARMUP_WINDOW
T_HORIZON = ssot.S8_T_HORIZON
ERR_WINDOW = ssot.S6_ERR_WINDOW
AUDIT_DELTA_P = ssot.S8_AUDIT_DELTA_P
C_INT = ssot.S8_C_INT
ARM_N_MODELS = (ssot.S8_N_MODELS, ssot.S8_MARGINAL_N_MODELS)     # 10 and 1
ANCHORS = ssot.S8_PER_TREE_DELTA_E
CONTROL_LAMBDA = ssot.S8_CONTROL_LAMBDAS[0]                      # 50.0, R2 scenario A
EPS = ssot.EPS_MISS


def run_cell(seed, delta_e, n_models, per_tree=True):
    """One prequential run of ARF(M = n_models) on the canonical stream.

    `per_tree` adds one `predict_one` per member per step, and ONLY over the pre-drift calibration
    window: that is where item 2's measurement lives, and M extra traversals over 8000 steps would
    triple the campaign for a post-drift quantity nobody asked for. Gate G0 established that
    `predict_one` consumes no RNG state, and `demo()` re-verifies it at the member level -- the
    ensemble error stream must be byte-identical with the flag on and off."""
    safe_seed, x, y = runner.make_stream(seed, delta_e)
    arf = common.make_arf(safe_seed, n_models, C_INT)
    err = np.zeros(N_STEPS, dtype=np.int8)
    tree_err = np.zeros((n_models, WARMUP), dtype=np.int8) if per_tree else None
    tracker = arf._drift_tracker
    swaps_at_drift, tau_swap = 0, np.nan
    lo = T_DRIFT - WARMUP

    for t in range(N_STEPS):
        x_dict = {0: x[t, 0], 1: x[t, 1]}
        y_pred = arf.predict_one(x_dict)
        err[t] = int((y_pred if y_pred is not None else 0) != y[t])
        if per_tree and lo <= t < T_DRIFT:
            for i, member in enumerate(arf.data):
                p = member.predict_one(x_dict)
                tree_err[i, t - lo] = int((p if p is not None else 0) != y[t])
        arf.learn_one(x_dict, int(y[t]))
        if t == T_DRIFT - 1:
            swaps_at_drift = sum(tracker.values())
        elif t >= T_DRIFT and np.isnan(tau_swap) and sum(tracker.values()) > swaps_at_drift:
            tau_swap = float(t - T_DRIFT)

    pre = err[lo:T_DRIFT].astype(np.float64)
    post = err[T_DRIFT:T_DRIFT + T_HORIZON].astype(np.float64)
    e_pre = float(pre.mean())
    a_unrefl, a_refl = defs.accumulations(post, e_pre, AUDIT_DELTA_P)
    tau_erase = float(np.argmax(a_unrefl))
    lam_eq, target = mech.calibrate_cusum(pre - e_pre - AUDIT_DELTA_P)
    attained = mech.count_alarms(pre - e_pre - AUDIT_DELTA_P, lam_eq)

    rec = {"seed": int(seed), "delta_e": float(delta_e), "n_models": int(n_models),
           "e_pre": e_pre, "delta_e_emp": float(post[:ERR_WINDOW].mean()) - e_pre,
           "tau_swap": tau_swap, "tau_erase": tau_erase,
           "w_transient": tau_erase - tau_swap if np.isfinite(tau_swap) else np.nan,
           "a_unrefl_peak": float(a_unrefl.max()),
           "lambda_eq": float(lam_eq), "lambda_eq_target_fa": int(target),
           "lambda_eq_verdict": mech.calibration_verdict(pre.size, lam_eq, attained, target),
           "tau_det_lambda_eq": mech.first_crossing(a_refl, lam_eq),
           f"tau_det_lambda{CONTROL_LAMBDA:g}": mech.first_crossing(a_refl, CONTROL_LAMBDA)}
    if per_tree:
        rates = tree_err.mean(axis=1)
        rec |= {"per_tree_e_pre_mean": float(rates.mean()),
                "per_tree_e_pre_sd": float(rates.std(ddof=1)) if n_models > 1 else np.nan,
                "per_tree_e_pre_min": float(rates.min()), "per_tree_e_pre_max": float(rates.max()),
                # variance of the per-step member error against the ensemble's, on the same window:
                # the bagging variance reduction S2-bis inferred from two calibrated thresholds
                "member_step_var_mean": float(tree_err.var(axis=1, ddof=1).mean()),
                "ensemble_step_var": float(pre.var(ddof=1))}
        per_tree_rows = [{"seed": int(seed), "delta_e": float(delta_e), "n_models": int(n_models),
                          "tree_index": int(i), "e_pre_tree": float(r)}
                         for i, r in enumerate(rates)]
    else:
        per_tree_rows = []
    return rec, per_tree_rows


def campaign(seeds, anchors=ANCHORS, arms=ARM_N_MODELS, n_jobs=-1, desc="S8 marginal"):
    cells = [(s, de, m) for de in anchors for m in arms for s in seeds]
    out = Parallel(n_jobs=n_jobs)(delayed(run_cell)(s, de, m) for s, de, m in tqdm(cells, desc=desc))
    return pd.DataFrame([r for r, _ in out]), pd.DataFrame([p for _, ps in out for p in ps])


# ══════════════════════════════════════════════════════════════════════════════
# D8 -- the decomposition
# ══════════════════════════════════════════════════════════════════════════════
def requirement(lam, w, eps=EPS):
    """R = lambda + sqrt(W/2 ln(1/eps)), the epsilon-margin form of s2bis family_requirements."""
    return float(lam) + float(np.sqrt(max(w, 0.0) / 2.0 * np.log(1.0 / eps)))


def hydra_decomposition(df, control=CONTROL_LAMBDA):
    """Per anchor: the Hydra time factor, and log(A/R) split into its two additive parts."""
    rows = []
    for de, g in df.groupby("delta_e"):
        arms = {int(m): gm for m, gm in g.groupby("n_models")}
        if set(arms) != set(ARM_N_MODELS):
            continue
        stat = {}
        for m, gm in arms.items():
            tau = gm.tau_swap.to_numpy(dtype=np.float64)
            stat[m] = {
                "n": int(len(gm)), "n_censored_tau_swap": int(np.sum(~np.isfinite(tau))),
                "mean_tau_swap": float(np.nanmean(tau)), "median_tau_swap": float(np.nanmedian(tau)),
                "median_w": float(gm.w_transient.median()),
                "median_a": float(gm.a_unrefl_peak.median()),
                "median_lambda_eq": float(gm.lambda_eq.median()),
                "median_e_pre": float(gm.e_pre.median()),
                "per_tree_e_pre_mean": float(gm.per_tree_e_pre_mean.median()),
                "per_tree_e_pre_sd": float(gm.per_tree_e_pre_sd.median()),
                "member_step_var_mean": float(gm.member_step_var_mean.median()),
                "ensemble_step_var": float(gm.ensemble_step_var.median()),
                "miss_rate_lambda_eq": float((~np.isfinite(gm.tau_det_lambda_eq)).mean()),
                "miss_rate_control": float(
                    (~np.isfinite(gm[f"tau_det_lambda{control:g}"])).mean())}
        one, ten = stat[ARM_N_MODELS[1]], stat[ARM_N_MODELS[0]]
        r_eq = {m: requirement(s["median_lambda_eq"], s["median_w"]) for m, s in stat.items()}
        r_nom = {m: requirement(control, s["median_w"]) for m, s in stat.items()}
        m1, m10 = ARM_N_MODELS[1], ARM_N_MODELS[0]

        ensemble_part = float(np.log(one["median_a"] / ten["median_a"]))
        threshold_eq = float(np.log(r_eq[m1] / r_eq[m10]))
        threshold_nom = float(np.log(r_nom[m1] / r_nom[m10]))
        rows.append({
            "delta_e": float(de),
            "hydra_time_factor": one["mean_tau_swap"] / ten["mean_tau_swap"],
            "hydra_time_factor_median": one["median_tau_swap"] / ten["median_tau_swap"],
            "variance_reduction_measured": (ten["member_step_var_mean"] / ten["ensemble_step_var"]
                                            if ten["ensemble_step_var"] else np.nan),
            "requirement_lambda_eq": r_eq, "requirement_lambda_control": r_nom,
            "log_margin_ratio_at_lambda_eq": ensemble_part - threshold_eq,
            "log_margin_ratio_at_control": ensemble_part - threshold_nom,
            "ensemble_size_part": ensemble_part,
            "threshold_part_at_lambda_eq": threshold_eq,
            "threshold_part_at_control": threshold_nom,
            "threshold_share_at_lambda_eq": (abs(threshold_eq)
                                             / (abs(threshold_eq) + abs(ensemble_part))
                                             if (abs(threshold_eq) + abs(ensemble_part)) else np.nan),
            "per_arm": stat})
    missing = [r["delta_e"] for r in rows
               if not np.isfinite(r["hydra_time_factor"]) or not np.isfinite(r["ensemble_size_part"])]
    return {"status": "NOT PRODUCED" if not rows or missing else "PRODUCED",
            "missing_measurement": ("mean tau_swap or median A censored on one arm at "
                                    f"Delta_e in {missing}" if missing else None),
            "control_lambda": float(control), "eps": float(EPS), "per_anchor": rows}


def read(path=None):
    base = RESULTS_DIR / "data"
    runs = pd.read_parquet(Path(path) if path else base / "s8_marginal_runs.parquet")
    tables = RESULTS_DIR / "tables"
    tables.mkdir(parents=True, exist_ok=True)
    payload = {"n_cells": int(len(runs)), "anchors": sorted(runs.delta_e.unique().tolist()),
               "arms_n_models": sorted(runs.n_models.unique().tolist()),
               "verdict_counts": runs.lambda_eq_verdict.value_counts().to_dict(),
               "D8_decomposition": hydra_decomposition(runs)}
    (tables / "s8_marginal_hydra.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=float) + "\n", encoding="utf-8")

    print(f"=== S8 marginal === {payload['n_cells']} cells, D8 "
          f"{payload['D8_decomposition']['status']}")
    for r in payload["D8_decomposition"]["per_anchor"]:
        a1, a10 = r["per_arm"][ssot.S8_MARGINAL_N_MODELS], r["per_arm"][ssot.S8_N_MODELS]
        print(f"  Delta_e = {r['delta_e']:.6f}")
        print(f"    Hydra time factor        = {r['hydra_time_factor']:.2f}x "
              f"(mean tau_swap {a1['mean_tau_swap']:.1f} vs {a10['mean_tau_swap']:.1f})")
        print(f"    lambda_eq                = {a1['median_lambda_eq']:.2f} (M=1) vs "
              f"{a10['median_lambda_eq']:.2f} (M=10)")
        print(f"    per-tree e_pre inside ARF= {a10['per_tree_e_pre_mean']:.4f} "
              f"+/- {a10['per_tree_e_pre_sd']:.4f}  vs M=1 arm {a1['per_tree_e_pre_mean']:.4f}")
        print(f"    measured variance reduct.= {r['variance_reduction_measured']:.2f}x")
        print(f"    log margin ratio: {r['log_margin_ratio_at_lambda_eq']:+.4f} at lambda_eq, "
              f"{r['log_margin_ratio_at_control']:+.4f} at lambda = {CONTROL_LAMBDA:g}")
        print(f"    ensemble-size part {r['ensemble_size_part']:+.4f} | threshold part "
              f"{r['threshold_part_at_lambda_eq']:+.4f} "
              f"(share {r['threshold_share_at_lambda_eq']:.1%})")
    print(f"[INFO] wrote {(tables / 's8_marginal_hydra.json').relative_to(ssot.ROOT_DIR)}")
    return payload


def demo():
    """Self-check: the per-tree instrumentation must not perturb the ensemble trajectory."""
    seed, de = common.seed_pool(1)[0], ANCHORS[1]
    with_flag, rows = run_cell(seed, de, ssot.S8_N_MODELS, per_tree=True)
    without, empty = run_cell(seed, de, ssot.S8_N_MODELS, per_tree=False)
    assert not empty and len(rows) == ssot.S8_N_MODELS, len(rows)
    for k in ("e_pre", "delta_e_emp", "tau_swap", "tau_erase", "a_unrefl_peak", "lambda_eq"):
        a, b = with_flag[k], without[k]
        assert (a == b) or (np.isnan(a) and np.isnan(b)), (k, a, b)
    assert 0.0 < with_flag["per_tree_e_pre_mean"] < 1.0
    assert with_flag["per_tree_e_pre_mean"] >= with_flag["e_pre"] - 1e-12, \
        "a single member beat the ensemble on the whole warm-up -- check the member predictor"
    assert requirement(50.0, 0.0) == 50.0
    print(f"s8_marginal demo: OK  e_pre={with_flag['e_pre']:.4f} "
          f"per-tree={with_flag['per_tree_e_pre_mean']:.4f}"
          f"+/-{with_flag['per_tree_e_pre_sd']:.4f} lambda_eq={with_flag['lambda_eq']:.2f}")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "full"
    if mode == "demo":
        demo()
    elif mode == "read":
        read()
    elif mode in ("smoke", "full"):
        seeds = common.seed_pool(5 if mode == "smoke" else ssot.S8_PER_TREE_N_SEEDS)
        print(f"[INFO] S8 marginal {mode}: {len(seeds)} seeds x {len(ANCHORS)} anchors x "
              f"{len(ARM_N_MODELS)} arms = {len(seeds) * len(ANCHORS) * len(ARM_N_MODELS)} cells")
        runs, per_tree = campaign(seeds, desc=f"S8 marginal {mode}")
        out = RESULTS_DIR / ("smoke" if mode == "smoke" else "data")
        out.mkdir(parents=True, exist_ok=True)
        runs.to_parquet(out / "s8_marginal_runs.parquet", index=False)
        per_tree.to_parquet(out / "s8_marginal_per_tree.parquet", index=False)
        print(f"[INFO] wrote {(out / 's8_marginal_runs.parquet').relative_to(ssot.ROOT_DIR)}")
        read(out / "s8_marginal_runs.parquet")
    else:
        raise SystemExit(f"usage: s8_marginal.py [demo|smoke|full|read]  (got {mode!r})")
