# exp_R5_alarm_protocol.py
# =============================================================================
# ALARM PROTOCOL CHECK (stream H10, objection CONS-017).
#
# The published INSECTS evaluation runs River's PageHinkley with its default
# mode="both" -- a TWO-SIDED test that also alarms when the error falls -- and
# resets the classifier to an untrained one on every alarm, whose abstentions are
# scored as errors. The flooding counts of Table 4 are produced by that loop.
#
# This script runs, per stream and pipeline, two protocols on the same streams and
# seeds as the published evaluation:
#
#   A  published protocol, instrumented: two-sided monitor, classifier reset on
#      alarm. Three monitors ride the same error stream (both / up / down) so every
#      alarm is attributed to the increase or the decrease statistic; each alarm is
#      also positioned relative to the first canonical drift.
#   B  one-sided monitor (mode="up"), NO classifier reset; the monitor is re-armed
#      after each alarm and the threshold is calibrated on the warm-up by the same
#      one-false-alarm bisection, run with the one-sided monitor.
#
# The flooding claim survives only if the precision gap between PHT+ARF(c=1) and
# PHT+HT survives protocol B.
#
# Usage:  exp_R5_alarm_protocol.py
# Output: results/R5_real_world_evaluation/data/exp_R5_alarm_protocol.csv
# =============================================================================
import random
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from river import drift, stream, tree

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp_R5_config as cfg  # noqa: E402
import exp_R5_common as common  # noqa: E402

RESULTS_DIR = Path(__file__).resolve().parents[2] / "results" / "R5_real_world_evaluation" / "data"
OUT_CSV = RESULTS_DIR / "exp_R5_alarm_protocol.csv"


def calibrate_lambda_1sided(error_stream, target_fa=cfg.PHT_TARGET_FA, max_iter=25):
    """One-false-alarm bisection with the ONE-SIDED monitor (mode='up')."""
    low, high = 1.0, 500.0
    for _ in range(max_iter):
        mid = (low + high) / 2.0
        n_fa = 0
        pht = drift.PageHinkley(threshold=mid, delta=cfg.PHT_DELTA, mode="up")
        for e in error_stream:
            pht.update(e)
            if pht.drift_detected:
                n_fa += 1
                pht = drift.PageHinkley(threshold=mid, delta=cfg.PHT_DELTA, mode="up")
        if n_fa <= target_fa:
            high = mid
        else:
            low = mid
    final_fa = 0
    pht = drift.PageHinkley(threshold=high, delta=cfg.PHT_DELTA, mode="up")
    for e in error_stream:
        pht.update(e)
        if pht.drift_detected:
            final_fa += 1
            pht = drift.PageHinkley(threshold=high, delta=cfg.PHT_DELTA, mode="up")
    if final_fa > target_fa and target_fa == 1:
        return calibrate_lambda_1sided(error_stream, target_fa=3, max_iter=max_iter)
    return high


def run_protocol(pipeline_name, seed, feature_stream, warmup_steps, none_fill, protocol):
    """One (pipeline, seed, protocol) cell. Returns per-alarm records and aggregates.

    Protocol A: two-sided, classifier reset (the published loop), sign attributed by
    shadow one-sided monitors. Protocol B: one-sided, no classifier reset."""
    random.seed(seed)
    np.random.seed(seed % (2 ** 32 - 1))

    is_tree = pipeline_name.endswith("_ht")
    clock = 32 if "c32" in pipeline_name else 1
    model = common.build_model(pipeline_name, seed)

    it = iter(feature_stream)
    warmup_errors = []
    for _ in range(warmup_steps):
        try:
            x, y = next(it)
        except StopIteration:
            break
        y_pred = model.predict_one(x)
        y_pred = y_pred if y_pred is not None else none_fill
        warmup_errors.append(float(y != y_pred))
        model.learn_one(x, y)

    if protocol == "A":
        lambda_val = common.calibrate_lambda(warmup_errors)
        mode = "both"
    else:
        lambda_val = calibrate_lambda_1sided(warmup_errors)
        mode = "up"

    def fresh():
        return drift.PageHinkley(threshold=lambda_val, delta=cfg.PHT_DELTA, mode=mode)

    det = fresh()
    up = drift.PageHinkley(threshold=lambda_val, delta=cfg.PHT_DELTA, mode="up")
    down = drift.PageHinkley(threshold=lambda_val, delta=cfg.PHT_DELTA, mode="down")

    alarms = []
    t = warmup_steps
    for x, y in it:
        y_pred = model.predict_one(x)
        y_pred = y_pred if y_pred is not None else none_fill
        e_t = float(y != y_pred)
        det.update(e_t)
        up.update(e_t)
        down.update(e_t)
        if det.drift_detected:
            sign = "up" if up.drift_detected else ("down" if down.drift_detected else "both?")
            alarms.append({"t": t, "sign": sign})
            det = fresh()
            up = drift.PageHinkley(threshold=lambda_val, delta=cfg.PHT_DELTA, mode="up")
            down = drift.PageHinkley(threshold=lambda_val, delta=cfg.PHT_DELTA, mode="down")
            if protocol == "A":
                model = tree.HoeffdingTreeClassifier() if is_tree else model.clone()
        model.learn_one(x, y)
        t += 1
    return alarms, lambda_val


def simulate(variant, seed, pipeline_name, protocol):
    df = pd.read_csv(cfg.INSECTS_DIR / f"{variant}.csv", float_precision='round_trip')
    n_total = len(df)
    target = df.columns[-1]
    warmup = common.get_warmup_steps(n_total)
    tau = common.get_tau_tol(n_total)
    raw_drifts = cfg.INSECTS_DRIFTS[variant]
    f1_drifts = common.resolve_f1_drifts(raw_drifts, n_total, tau)

    def feature_stream():
        for x, y in stream.iter_pandas(df.drop(columns=[target]), df[target]):
            yield x, y

    alarms, lambda_val = run_protocol(pipeline_name, seed, feature_stream(), warmup,
                                     cfg.INSECTS_NONE_FILL, protocol)
    times = [a["t"] for a in alarms]
    add_fm, f1_fm, fp_fm, _, _, _ = common.evaluate_bipartite(times, f1_drifts, n_total, tau)
    first_drift = min(raw_drifts)
    n_up = sum(1 for a in alarms if a["sign"] == "up")
    n_down = sum(1 for a in alarms if a["sign"] == "down")
    n_before = sum(1 for t in times if t < first_drift)
    # TP / FP from the first-match protocol
    tp_pairs, used = [], set()
    for td in sorted(f1_drifts):
        cands = [d for d in times if td <= d <= td + tau and d not in used]
        if cands:
            first = min(cands)
            tp_pairs.append((td, first))
            used.add(first)
    TP = len(tp_pairs)
    FP = len([d for d in times if d not in used])
    precision = TP / (TP + FP) if (TP + FP) else 0.0
    return {"variant": variant, "seed": seed, "pipeline": pipeline_name, "protocol": protocol,
            "lambda": lambda_val, "n_alarms": len(times), "n_up": n_up, "n_down": n_down,
            "n_before_first_drift": n_before, "TP": TP, "FP": FP, "precision": precision,
            "F1": f1_fm}


def main():
    jobs = [(v, s, p, proto)
            for v in ["abrupt_balanced", "gradual_balanced", "incremental_reoccurring_balanced"]
            for s in common.make_seed_pool(cfg.N_SEEDS)
            for p in ["pht_arf_c1", "pht_ht"]
            for proto in ["A", "B"]]
    res = Parallel(n_jobs=-1, verbose=2)(delayed(simulate)(*j) for j in jobs)
    df = pd.DataFrame(res)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_CSV, index=False)
    agg = df.groupby(["variant", "pipeline", "protocol"]).agg(
        alarms=("n_alarms", "mean"), up=("n_up", "mean"), down=("n_down", "mean"),
        before=("n_before_first_drift", "mean"), precision=("precision", "mean"),
        F1=("F1", "mean"), n=("seed", "size"))
    print(agg.round(4))
    print(f"\nwritten: {OUT_CSV}")


if __name__ == "__main__":
    main()
