# exp_R5_compute_delta_e.py
"""Effective-error-jump (Delta_e) estimation for the BAF and INSECTS streams of Table II.

Two estimates per variant, from the SAME pass over the stream and the same drift positions:

  adaptive -- one Hoeffding Tree that keeps calling learn_one at every step. This is the published
              estimator, and it is measured on a model that is already absorbing the change it is
              meant to reveal.
  oracle   -- a deepcopy fork of that same tree, taken ONCE at the end of the warm-up and never
              trained again (predict_one only). S7-ter/LOT C. It cannot absorb the drift, so a jump
              it does not see is a jump that is not in the stream, and a jump it sees while the
              adaptive estimator does not is evidence of masking by adaptation.

The fork mechanics are transplanted from the S6 'frozen' arm (s6_runner.py: copy.deepcopy, then
segment(..., learn=False)), whose fidelity is certified by gate G1 and whose immobility is asserted
by tests/test_S6_traces.py::test_frozen_arm_is_immobile. Both estimates then go through the same
estimate_delta_e_adaptive with the same positions and the same adaptive windows, so they differ in
exactly one input: the error stream. Fast (minutes).

# ponytail: the oracle is a frozen Hoeffding Tree, not a frozen ARF. The decision below turns only
# on whether a NON-ADAPTING model sees an error jump at the canonical positions, which a frozen HT
# settles; an ARF pass over 3 x 10^6 BAF rows costs roughly an order of magnitude more. Upgrade path
# if an ARF-specific reading is ever needed: swap the constructor and reuse common.make_arf.
"""
import copy
import sys
import numpy as np
import pandas as pd
from river import tree, stream

import exp_R5_config as cfg
import exp_R5_common as common


def _err(model, x, y, none_fill):
    y_pred = model.predict_one(x)
    return float(y != (y_pred if y_pred is not None else none_fill))


def error_stream_baf(variant):
    """Adaptive and frozen-fork HT error streams on a BAF variant (warm-up-fitted z-score).

    The fork is taken at t == BAF_WARMUP, i.e. after the warm-up rows have been learned and before
    the warm-up row itself is predicted. Every canonical BAF drift (125000 ... 875000) and every
    adaptive window around it lies strictly downstream of that point, so the oracle is frozen for
    the whole of the region the estimator reads."""
    df = pd.read_csv(cfg.BAF_DIR / f"{variant}.csv")
    num_cols = df.select_dtypes(include=["number"]).columns.drop(
        ["fraud_bool", "month"], errors="ignore")
    means = df.iloc[:cfg.BAF_WARMUP][num_cols].mean()
    stds = df.iloc[:cfg.BAF_WARMUP][num_cols].std().replace(0, 1)
    X_vals = ((df[num_cols] - means) / stds).values
    y_vals = df["fraud_bool"].values.astype(int)
    cols = list(num_cols)
    model, frozen = tree.HoeffdingTreeClassifier(), None
    errs, errs_frozen = [], []
    for t in range(len(df)):
        x = {cols[i]: X_vals[t, i] for i in range(len(cols))}
        if t == cfg.BAF_WARMUP:
            frozen = copy.deepcopy(model)
        e = _err(model, x, y_vals[t], cfg.BAF_NONE_FILL)
        errs.append(e)
        # Before the fork the two models ARE the same object, so the streams coincide by
        # construction; recording e keeps the arrays index-aligned for identical windows.
        errs_frozen.append(e if frozen is None else _err(frozen, x, y_vals[t], cfg.BAF_NONE_FILL))
        model.learn_one(x, int(y_vals[t]))
    return errs, errs_frozen, len(df)


def error_stream_insects(variant):
    """Adaptive and frozen-fork HT error streams on an INSECTS variant.

    Warm-up is get_warmup_steps(n) = min(100000, 0.10 n) -> 5284 / 2414 / 7998, each strictly before
    that variant's first canonical drift (14352 / 14028 / 26568) and before the left edge of its
    first adaptive window."""
    df = pd.read_csv(cfg.INSECTS_DIR / f"{variant}.csv")
    target = df.columns[-1]
    warmup = common.get_warmup_steps(len(df))
    it = stream.iter_pandas(df.drop(columns=[target]), df[target])
    model, frozen = tree.HoeffdingTreeClassifier(), None
    errs, errs_frozen = [], []
    for t, (x, y) in enumerate(it):
        if t == warmup:
            frozen = copy.deepcopy(model)
        e = _err(model, x, y, cfg.INSECTS_NONE_FILL)
        errs.append(e)
        errs_frozen.append(e if frozen is None else _err(frozen, x, y, cfg.INSECTS_NONE_FILL))
        model.learn_one(x, y)
    return errs, errs_frozen, len(df)


def main():
    rows, oracle_rows = [], []

    def record(dataset, variant, errs, errs_frozen, drifts, n, warmup):
        """Both estimators, same positions, same windows -- one input apart.

        `err_mean_post_fork` is the saturation diagnostic, and it is not optional: a frozen model at
        chance cannot exhibit an error jump, so an oracle Delta_e near zero is only evidence of
        "no jump in the stream" when the frozen model still discriminates. Without this column the
        two readings are indistinguishable in the artifact."""
        out = common.estimate_delta_e_adaptive(errs, drifts, n)
        out_frozen = common.estimate_delta_e_adaptive(errs_frozen, drifts, n)
        assert out["windows"] == out_frozen["windows"], (
            f"{dataset}/{variant}: adaptive and oracle windows differ ({out['windows']} vs "
            f"{out_frozen['windows']}); the two estimates would not be comparable -- HALT")
        # The diagnostic columns live in the ORACLE artifact only. delta_e.parquet is one of the 34
        # frozen hashes and LOT C is required to leave it byte-identical: adding a column to it would
        # cost an authorized deviation for a control that changes none of its values.
        rows.append({"dataset": dataset, "variant": variant, **out})
        oracle_rows.append({"dataset": dataset, "variant": variant, **out_frozen,
                            "err_mean_post_fork": float(np.mean(errs_frozen[warmup:])),
                            "err_mean_post_fork_adaptive": float(np.mean(errs[warmup:]))})
        print(f"  {dataset.upper()} {variant}: adaptive = {out['delta_e_mean']:+.4f} "
              f"[{out['delta_e_ci_lo']:+.4f}, {out['delta_e_ci_hi']:+.4f}]   "
              f"oracle = {out_frozen['delta_e_mean']:+.4f} "
              f"[{out_frozen['delta_e_ci_lo']:+.4f}, {out_frozen['delta_e_ci_hi']:+.4f}]   "
              f"| post-fork error: adaptive {oracle_rows[-1]['err_mean_post_fork_adaptive']:.4f}, "
              f"frozen {oracle_rows[-1]['err_mean_post_fork']:.4f}")

    print("[R5/Delta_e] BAF ...", flush=True)
    for v in cfg.BAF_VARIANTS:
        errs, errs_frozen, n = error_stream_baf(v)
        record("baf", v, errs, errs_frozen, cfg.BAF_DRIFTS, n, cfg.BAF_WARMUP)

    print("[R5/Delta_e] INSECTS ...", flush=True)
    for v in cfg.INSECTS_VARIANTS:
        errs, errs_frozen, n = error_stream_insects(v)
        record("insects", v, errs, errs_frozen, cfg.INSECTS_DRIFTS_DELTA_E[v], n,
               common.get_warmup_steps(n))

    pd.DataFrame(rows).to_parquet(cfg.OUT_DELTA_E, index=False)
    pd.DataFrame(oracle_rows).to_parquet(cfg.OUT_DELTA_E_ORACLE, index=False)
    print(f"[R5/Delta_e] DONE -> {cfg.OUT_DELTA_E}")
    print(f"[R5/Delta_e] DONE -> {cfg.OUT_DELTA_E_ORACLE}")


if __name__ == "__main__":
    main()