# exp_R5_baf_timing.py
"""One-off throughput measurement for the BAF stage (docs/ENVIRONMENT.md, 2026-10-01).

Times one Base.csv prefix per pipeline through the canonical run_evaluation to
extrapolate the full-stage wall clock. Not part of the R5 pipeline: writes nothing.

Usage: python exp_R5_baf_timing.py
"""
import time

import pandas as pd

import exp_R5_config as cfg
import exp_R5_common as common

PREFIXES = [("pht_arf_c1", 125_000), ("pht_arf_c1", 250_000),
            ("pht_ht", 250_000), ("adwin_arf_c1", 250_000)]


def main():
    df_full = pd.read_csv(cfg.BAF_DIR / "Base.csv")
    num_cols = df_full.select_dtypes(include=["number"]).columns.drop(
        ["fraud_bool", "month"], errors="ignore")
    seed = common.make_seed_pool()[0]
    for pipeline, prefix in PREFIXES:
        df = df_full.iloc[:prefix]
        means = df.iloc[:cfg.BAF_WARMUP][num_cols].mean()
        stds = df.iloc[:cfg.BAF_WARMUP][num_cols].std().replace(0, 1)
        x_vals = ((df[num_cols] - means) / stds).values
        y_vals = df["fraud_bool"].values.astype(int)
        cols = list(num_cols)

        def feature_stream():
            for t in range(len(df)):
                yield {cols[i]: x_vals[t, i] for i in range(len(cols))}, int(y_vals[t])

        t0 = time.perf_counter()
        detections, _, _ = common.run_evaluation(
            pipeline, seed, feature_stream(), cfg.BAF_WARMUP, cfg.BAF_NONE_FILL)
        elapsed = time.perf_counter() - t0
        print(f"RESULT pipeline={pipeline} prefix={len(df)} elapsed_s={elapsed:.1f} "
              f"rows_per_s={len(df) / elapsed:.0f} detections={len(detections)}", flush=True)


if __name__ == "__main__":
    main()
