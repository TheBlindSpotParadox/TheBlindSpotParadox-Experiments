"""Stream S10 / T10.3 -- p0, the pre-change error floor of every real stream the repository
instruments.

S9 D9: an ordering of monitor families that omits the stream's error floor orders streams, not
families, and Table II carries none. Operator arbitration (docs/theory/S10_decision_rules.md,
preamble): the three balanced INSECTS variants present in data/ and the three BAF variants; no
external data.

p0 is the classifier's own pre-change error with the external detector DISABLED -- the S2-bis
calibration pass, `s2bis_lambda_eq.run_at_lambda(..., None, stop_at=...)` -- because an armed
detector resets the classifier and makes the pre-change stream a function of lambda:

  p0_warm  mean error over the warm-up
  p0_span  mean error over the armed pre-change span [warm-up, first valid change)

per (stream, variant, seed, pipeline), pipelines S10_P0_PIPELINES. `adwin_arf_c1` builds the same
ARF(c = 1) as `pht_arf_c1` (`build_model` reads the `_ht` suffix and `c32` only), so its p0 is
identical by construction.

  INSECTS  `s2bis_lambda_eq.calibration_cell`, verbatim. Rule P0-2 compares all 180 cells with the
           committed s2bis_lambda_eq_insects.csv and halts on any difference.
  BAF      the stream of `exp_R5_compute_baf.simulate:17-24`, rebuilt from the .csv.gz this worktree
           holds with a round-trip parse (the repository guard forbids a bare read_csv outside R5).
           Rule P0-3: the adaptive Hoeffding tree run over the whole stream must reproduce, to the
           bit, the post-warm-up mean error that `exp_R5_compute_delta_e.error_stream_baf` committed
           with R5's parse (`delta_e_oracle.parquet :: err_mean_post_fork_adaptive`). R5 itself
           cannot re-run here: it reads uncompressed <variant>.csv files absent from this worktree.

Usage:  PYTHONHASHSEED=0 python experiments/S10_external_validity/s10_p0.py
"""
import functools
import hashlib
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
from joblib import Parallel, delayed
from river import tree

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "R5_real_world_evaluation"))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "S2bis_calibration"))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "S6_synchronized_traces"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import experiment_ssot as ssot  # noqa: E402

import exp_R5_common as r5  # noqa: E402
import exp_R5_config as cfg  # noqa: E402
import s2bis_lambda_eq as s2bis  # noqa: E402
from exp_R5_make_table2 import sci  # noqa: E402
import s6_writer as writer  # noqa: E402
import s10_latency as lat  # noqa: E402

PIPELINES = list(ssot.S10_P0_PIPELINES)
TABLES = ssot.RESULTS_DIR / "S10_external_validity" / "tables"
ORACLE_INSECTS = ssot.RESULTS_DIR / "S2bis_calibration" / "tables" / "s2bis_lambda_eq_insects.csv"
ORACLE_BAF = ssot.RESULTS_DIR / "R5_real_world_evaluation" / "data" / "delta_e_oracle.parquet"
TABLE2 = ssot.RESULTS_DIR / "R5_real_world_evaluation" / "tables" / "table2_values.csv"

CELLS_SCHEMA = pa.schema(
    [("stream", pa.string()), ("variant", pa.string()), ("seed", pa.int64()), ("pipeline", pa.string()),
     ("n_warm", pa.int64()), ("n_span", pa.int64()), ("p0_warm", pa.float64()), ("p0_span", pa.float64()),
     ("lambda_eq_span_emp", pa.float64())])


# ══════════════════════════════════════════════════════════════════════════════
# INSECTS -- the S2-bis calibration pass, verbatim
# ══════════════════════════════════════════════════════════════════════════════
def insects_cell(variant, seed, pipeline):
    c = s2bis.calibration_cell(variant, seed, pipeline)
    return {"stream": "insects", "variant": variant, "seed": int(seed), "pipeline": pipeline,
            "n_warm": int(c["warmup_steps"]), "n_span": int(c["span_len"]),
            "p0_warm": c["p_true_warmup"], "p0_span": c["p_true_span"],
            "lambda_eq_span_emp": c["lambda_eq_span_emp"]}


def rule_p0_2(cells):
    """P0-2: every recomputed cell equals the committed S2-bis row, to the bit."""
    ref = pd.read_csv(ORACLE_INSECTS, float_precision="round_trip").set_index(["variant", "seed", "pipeline"])
    bad = []
    for c in cells:
        r = ref.loc[(c["variant"], c["seed"], c["pipeline"])]
        for mine, theirs in (("p0_warm", "p_true_warmup"), ("p0_span", "p_true_span"),
                             ("lambda_eq_span_emp", "lambda_eq_span_emp")):
            if c[mine] != float(r[theirs]):
                bad.append({"variant": c["variant"], "seed": c["seed"], "pipeline": c["pipeline"],
                            "field": mine, "s10": c[mine], "s2bis": float(r[theirs])})
    return {"oracle": str(ORACLE_INSECTS.relative_to(ssot.ROOT_DIR)), "cells": len(cells),
            "divergent": bad, "verdict": "REPRODUCED" if cells and not bad else "BREACH"}


# ══════════════════════════════════════════════════════════════════════════════
# BAF -- R5's stream, round-trip parse
# ══════════════════════════════════════════════════════════════════════════════
@functools.lru_cache(maxsize=None)
def baf_stream(variant):
    """(columns, z-scored features, labels): exp_R5_compute_baf.simulate:17-24, parse aside."""
    df = pd.read_csv(ssot.DATA_DIR / "baf" / f"{variant}.csv.gz", float_precision="round_trip")
    num_cols = df.select_dtypes(include=["number"]).columns.drop(["fraud_bool", "month"], errors="ignore")
    means = df.iloc[:cfg.BAF_WARMUP][num_cols].mean()
    stds = df.iloc[:cfg.BAF_WARMUP][num_cols].std().replace(0, 1)
    return list(num_cols), ((df[num_cols] - means) / stds).values, df["fraud_bool"].values.astype(int)


def _features(variant):
    cols, x, y = baf_stream(variant)
    for t in range(len(y)):
        yield {cols[i]: x[t, i] for i in range(len(cols))}, int(y[t])


def baf_cell(variant, seed, pipeline):
    span_end = cfg.BAF_DRIFTS[0]
    _, errors, _ = s2bis.run_at_lambda(pipeline, seed, _features(variant), cfg.BAF_WARMUP,
                                       cfg.BAF_NONE_FILL, None, stop_at=span_end)
    warm, span = errors[:cfg.BAF_WARMUP], errors[cfg.BAF_WARMUP:span_end]
    return {"stream": "baf", "variant": variant, "seed": int(seed), "pipeline": pipeline,
            "n_warm": len(warm), "n_span": len(span), "p0_warm": float(np.mean(warm)),
            "p0_span": float(np.mean(span)), "lambda_eq_span_emp": np.nan}


def baf_adaptive_ht_error(variant):
    """The adaptive loop of error_stream_baf over the whole stream: predict, score, learn."""
    cols, x, y = baf_stream(variant)
    model, errs = tree.HoeffdingTreeClassifier(), np.empty(len(y))
    for t in range(len(y)):
        xt = {cols[i]: x[t, i] for i in range(len(cols))}
        p = model.predict_one(xt)
        errs[t] = float(y[t] != (p if p is not None else cfg.BAF_NONE_FILL))
        model.learn_one(xt, int(y[t]))
    return variant, float(np.mean(errs[cfg.BAF_WARMUP:])), errs


def rule_p0_3(ht_runs, cells):
    """P0-3: the S10 parse reproduces R5's committed adaptive-tree error, and the HT pass it rests on
    is the pht_ht calibration pass (the tree draws no randomness, so every seed must agree)."""
    ref = pd.read_parquet(ORACLE_BAF).set_index("variant")
    out, ok = {}, True
    for variant, mean_post, errs in ht_runs:
        committed = float(ref.loc[variant, "err_mean_post_fork_adaptive"])
        ht = [c for c in cells if c["variant"] == variant and c["pipeline"] == "pht_ht"]
        span_end = cfg.BAF_DRIFTS[0]
        seeds_agree = all(c["p0_span"] == float(np.mean(errs[cfg.BAF_WARMUP:span_end])) and
                          c["p0_warm"] == float(np.mean(errs[:cfg.BAF_WARMUP])) for c in ht)
        same = mean_post == committed
        ok &= same and seeds_agree
        out[variant] = {"s10_err_mean_post_warmup": mean_post, "committed": committed,
                        "identical": same, "pht_ht_cells_equal_the_full_pass": seeds_agree}
    return {"oracle": str(ORACLE_BAF.relative_to(ssot.ROOT_DIR)) + " :: err_mean_post_fork_adaptive",
            "per_variant": out, "verdict": "IDENTICAL" if ok else "DIVERGENT"}


# ══════════════════════════════════════════════════════════════════════════════
# Summary and the Table II candidate
# ══════════════════════════════════════════════════════════════════════════════
def summarise(cells):
    df = pd.DataFrame(cells)
    rows = []
    for (stream, variant, pipeline), g in df.groupby(["stream", "variant", "pipeline"], sort=True):
        rows.append({"stream": stream, "variant": variant, "pipeline": pipeline, "n_seeds": int(len(g)),
                     "n_warm": int(g.n_warm.iloc[0]), "n_span": int(g.n_span.iloc[0]),
                     **{f"{k}_{s}": float(getattr(g[k], s)()) for k in ("p0_warm", "p0_span")
                        for s in ("median", "min", "max")}})
    return rows


def table2_with_p0(summary):
    """Table II's committed rows, plus the pre-change floor of both classifiers. Nothing else is
    recomputed: F1, ratios and sign tests are read from table2_values.csv."""
    t2 = pd.read_csv(TABLE2, float_precision="round_trip")
    p0 = {(r["variant"], r["pipeline"]): r["p0_span_median"] for r in summary}

    def cell(x, fmt):
        return "---" if x is None or not np.isfinite(x) else fmt.format(x)

    lines = [r"\begin{tabular}{@{}lcccccccc@{}}", r"\toprule",
             r"Variant & $\Delta e$ & F1(PHT+HT) & F1(PHT+ARF$_{c=1}$) & F1(ADW+ARF$_{c=1}$) & "
             r"Ratio HT/ARF & Sign test $p$ & $p_0$ HT & $p_0$ ARF$_{c=1}$ \\", r"\midrule"]
    for _, r in t2.iterrows():
        p = r["sign_test_p"]
        de = (r"$\approx 0$" if r["dataset"] == "baf" and abs(r["delta_e"]) < 0.01   # R5's rule
              else f"${r['delta_e']:.2f}$")
        lines.append(f"{r['row']} & {de} & ${r['F1_PHT_HT']:.2f}$ & ${r['F1_PHT_ARF']:.2f}$ & "
                     f"${r['F1_ADW_ARF']:.2f}$ & {cell(r['ratio'], '${:.2f}$')} & "
                     f"{'---' if pd.isna(p) else sci(p)} & "
                     f"{cell(p0.get((r['variant'], 'pht_ht')), '${:.3f}$')} & "
                     f"{cell(p0.get((r['variant'], 'pht_arf_c1')), '${:.3f}$')} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    return "\n".join(lines) + "\n"


def _sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    # Workers receive this module's functions BY REFERENCE: run as __main__, they would be pickled
    # by value together with the lru_cache of baf_stream, which loky cannot un-serialize.
    import s10_p0 as mod
    seeds = r5.make_seed_pool()
    tasks = ([(mod.insects_cell, v, s, p) for v in cfg.INSECTS_VARIANTS for s in seeds for p in PIPELINES]
             + [(mod.baf_cell, v, s, p) for v in cfg.BAF_VARIANTS for s in seeds for p in PIPELINES])
    cells = Parallel(n_jobs=-1)(delayed(fn)(v, s, p) for fn, v, s, p in tasks)
    ht_runs = Parallel(n_jobs=len(cfg.BAF_VARIANTS))(delayed(mod.baf_adaptive_ht_error)(v)
                                                      for v in cfg.BAF_VARIANTS)

    p02 = rule_p0_2([c for c in cells if c["stream"] == "insects"])
    p03 = rule_p0_3(ht_runs, [c for c in cells if c["stream"] == "baf"])
    summary = summarise(cells)
    data_hashes = {str(p.relative_to(ssot.ROOT_DIR)): _sha256(p)
                   for p in sorted(list((ssot.DATA_DIR / "insects").glob("*.csv"))
                                   + list((ssot.DATA_DIR / "baf").glob("*.csv.gz")))}

    cols = {f.name: [c[f.name] for c in cells] for f in CELLS_SCHEMA}
    writer._write(writer._sorted_table(cols, CELLS_SCHEMA, ["stream", "variant", "pipeline", "seed"]),
                  TABLES / "s10_p0.parquet")
    lat._write_json(TABLES / "s10_p0.json",
                    {"P0-2": p02, "P0-3": p03, "summary": summary, "data_sha256": data_hashes,
                     "pipelines": PIPELINES, "n_seeds": len(seeds),
                     "adwin_arf_c1": "same ARF(c = 1) as pht_arf_c1: identical p0 by construction",
                     "env": lat._env()})
    (TABLES / "s10_table2_p0.tex").write_text(table2_with_p0(summary), encoding="utf-8")
    print(f"[INFO] wrote {(TABLES / 's10_table2_p0.tex').relative_to(ssot.ROOT_DIR)}")
    print(f"--- P0-2 {p02['verdict']} ({p02['cells']} cells)   P0-3 {p03['verdict']}")
    for r in summary:
        print(f"    {r['stream']:8s} {r['variant']:34s} {r['pipeline']:11s} "
              f"p0_span {r['p0_span_median']:.4f} [{r['p0_span_min']:.4f}, {r['p0_span_max']:.4f}]   "
              f"p0_warm {r['p0_warm_median']:.4f}")
    if p02["verdict"] == "BREACH":
        raise SystemExit("[FATAL] rule P0-2 BREACH -- the S10 pass is not the S2-bis calibration pass")
    return summary


if __name__ == "__main__":
    main()
