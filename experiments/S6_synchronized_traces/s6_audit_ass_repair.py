# %%
"""Post-hoc audit: test `ass:repair` on the committed S6 traces.

`docs/manuscript/sections/framework_v2.tex` carried an assumption, "no recovery without
replacement", stating that the smoothed ensemble error satisfies

    bar_e_t > p_0 + delta_P   for every t in [tau*, tau_swap^(1/M)).

Stream S6 handed it forward as open item 4 of `docs/theory/S6_causal_evidence.md`: unverified, and
directly testable on the committed traces. This is that test, and it is what action A7 acts on.

Three readings of `bar_e_t` are evaluated, because `def:times` does not say which estimator it
denotes on an interval shorter than its own smoothing window:
  cumulative mean from tau*   defined from the first post-drift step, hypersensitive early;
  trailing mean over 20       defined once 20 steps have elapsed;
  trailing mean over S6_ERR_WINDOW = 200, the estimator `tau_err_framework` actually uses.

Separately, the audit measures what `prop:order` needs, which is strictly weaker than the pointwise
assumption: `tau_err` quantifies over all s >= t, so a transient dip below tolerance does not move
it. The two are not the same statement and they do not have the same verdict.

Reads committed artifacts only. No RNG, no global state, nothing regenerated.

Usage:  PYTHONHASHSEED=0 python experiments/S6_synchronized_traces/s6_audit_ass_repair.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.dataset as ds

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))
from config import experiment_ssot as ssot

DATA = ROOT_DIR / "results" / "S6_synchronized_traces" / "data"
RUNS = DATA / "runs.parquet"
TRACES = DATA / "traces.parquet"
ARM = "full"                                   # the nominal arm; the interval precedes every fork
PARTITION_DECIMALS = 6                         # S6_PARQUET_PARTITION_FMT = "{:.6f}"
SHORT_WINDOW = 20
ESTIMATORS = {"cumulative mean from tau*": None,
              f"trailing mean over {SHORT_WINDOW}": SHORT_WINDOW,
              f"trailing mean over {ssot.S6_ERR_WINDOW} (def:times)": ssot.S6_ERR_WINDOW}


def stays_above(err, threshold, window):
    """True if the estimator is strictly above `threshold` at every point where it is defined.

    NaN when the estimator is undefined on the whole interval, which is the verdict that matters
    for the 200-step window: an interval shorter than the window carries no value to test."""
    if err.size == 0:
        return np.nan
    if window is None:
        est = np.cumsum(err) / np.arange(1, err.size + 1)
    elif err.size < window:
        return np.nan
    else:
        c = np.concatenate(([0.0], np.cumsum(err)))
        est = (c[window:] - c[:-window]) / window
    return bool(np.all(est > threshold))


def pre_swap_errors():
    """{(seed, delta_e_key): (err before the first post-drift swap, e_pre)} for the nominal arm."""
    runs = pd.read_parquet(RUNS)
    nominal = runs[runs.arm == ARM].copy()
    # Join on the hive partition string, never on the float: the partition key is written through
    # a fixed format and a float compare here would reintroduce the 1-ULP join loss the repository
    # guards against elsewhere.
    nominal["de_key"] = nominal["delta_e"].map(lambda v: f"{float(v):.{PARTITION_DECIMALS}f}")
    index = nominal.set_index(["seed", "de_key"])[["fork_t_rel", "e_pre"]]

    cap = int(nominal.fork_t_rel.max()) + 1
    table = ds.dataset(TRACES, format="parquet", partitioning="hive").to_table(
        columns=["arm", "seed", "t_rel", "err", "delta_e"],
        filter=(ds.field("arm") == ARM) & (ds.field("t_rel") >= 0) & (ds.field("t_rel") < cap),
    ).to_pandas()

    out = {}
    for (seed, de_key), g in table.groupby(["seed", "delta_e"], sort=True):
        fork, e_pre = index.loc[(seed, de_key), ["fork_t_rel", "e_pre"]]
        err = g.sort_values("t_rel")["err"].to_numpy(dtype=np.float64)[:int(fork)]
        out[(seed, de_key)] = (err, float(e_pre))
    return out, nominal


def main():
    pre, nominal = pre_swap_errors()
    n = len(pre)
    intervals = np.array([e.size for e, _ in pre.values()])
    short = int((intervals < ssot.S6_ERR_WINDOW).sum())

    print(f"=== A7 audit of ass:repair === arm '{ARM}', {n} runs "
          f"({nominal.seed.nunique()} seeds x {nominal.delta_e.nunique()} magnitudes)")
    print(f"interval [tau*, tau_swap^(1/M)): mean {intervals.mean():.1f} steps, "
          f"median {np.median(intervals):.0f}, max {intervals.max()}")
    print(f"  shorter than the def:times window ({ssot.S6_ERR_WINDOW}): {short}/{n} "
          f"({100 * short / n:.1f} %)\n")

    print("1. The assumption AS WRITTEN: bar_e_t > p_0 + delta_P at every t of the interval.")
    print(f"{'estimator':<46s} {'delta_P':>8s} {'holds':>7s} {'fails':>7s} {'undef':>7s} {'% holds':>9s}")
    verdicts = {}
    for dp_name, dp in (("0.005", ssot.DELTA_P), ("0.01", ssot.CUSUM_DELTA_P)):
        for label, window in ESTIMATORS.items():
            v = np.array([stays_above(err, e_pre + dp, window) for err, e_pre in pre.values()],
                         dtype=object)
            holds = int(sum(x is True for x in v))
            fails = int(sum(x is False for x in v))
            undef = int(sum(x is not True and x is not False for x in v))
            pct = 100 * holds / (holds + fails) if holds + fails else float("nan")
            verdicts[(label, dp_name)] = (holds, fails, undef)
            print(f"{label:<46s} {dp_name:>8s} {holds:>7d} {fails:>7d} {undef:>7d} {pct:>8.1f}%")

    print("\n2. What prop:order actually needs, which is weaker: tau_err quantifies over all s >= t,")
    print("   so a transient dip below tolerance does not move tau_erase.")
    for col, name in (("tau_erase_fw", "tau_erase (def:times estimator)"),
                      ("tau_erase", "tau_erase (hysteresis estimator)")):
        defined = nominal[col].notna()
        ok = (nominal.loc[defined, col] >= nominal.loc[defined, "fork_t_rel"]).sum()
        print(f"   {name:<36s} >= tau_swap^(1/M): {ok}/{int(defined.sum())} "
              f"({100 * ok / defined.sum():.1f} %), undefined in {int((~defined).sum())}")

    print("\n3. The converse bound of the submitted version: tau_erase <= tau_swap^(1).")
    both = nominal.tau_erase_fw.notna() & nominal.tau_swap_q100.notna()
    ok = (nominal.loc[both, "tau_erase_fw"] <= nominal.loc[both, "tau_swap_q100"]).sum()
    print(f"   holds {ok}/{int(both.sum())} ({100 * ok / both.sum():.1f} %) where defined; "
          f"tau_swap^(1) undefined in {int(nominal.tau_swap_q100.isna().sum())}/{n} runs "
          f"({100 * nominal.tau_swap_q100.isna().mean():.1f} %)")

    print("\n4. def:kappa asserts kappa >= 1.")
    k = nominal["kappa"].replace([np.inf, -np.inf], np.nan).dropna()
    ge = int((k >= 1).sum())
    print(f"   kappa >= 1 in {ge}/{len(k)} ({100 * ge / len(k):.1f} %), median {k.median():.1f}, "
          f"min {k.min():.3f}, defined in {len(k)}/{n}")

    # Invariants this audit establishes. They are what action A7 rewrote framework_v2.tex on; a
    # trace regeneration that moves them invalidates that rewrite rather than this script.
    cum = verdicts[("cumulative mean from tau*", "0.01")]
    assert cum[0] + cum[1] == n and cum[0] / n < 0.5, cum
    assert short / n > 0.5, "the def:times window is no longer wider than most intervals"
    assert ge / len(k) > 0.99, "kappa >= 1 no longer holds at the measured rate"
    print("\n[OK] invariants hold")


if __name__ == "__main__":
    main()
