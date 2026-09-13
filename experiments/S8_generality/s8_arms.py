"""Stream S8 / T8.1 -- the ab initio arms, and the erasure decomposition they close.

`rem:cf_scope` (.tex:234) declares the missing arm in words: "an arm with replacement suppressed
from tau^* onward". This is that arm, plus the frozen reference it needs to be additive.

Why the S6 arms cannot answer the question. 'no_swap' and 'frozen' are deepcopy forks taken at
tau_swap^(1/M) -- AFTER the learn_one that produced the first replacement -- so all three S6 arms
carry that replacement identically and no contrast between them can attribute anything to it.
`s6_causal.erasure_share` says so in its own docstring. The fork point is also ENDOGENOUS: it is a
property of the trunk's trajectory, and it differs from seed to seed. Forking at tau*, the exogenous
instant the protocol fixes, restores the pairing and closes the identity

    E_total = E_learn_pure + E_swap_first + E_swap_rest

with no residue. `\\LearnShare = 99.3` is currently E_learn/E_total with an E_learn that contains
the first swap; this campaign reattributes it or confirms it.

This module is a thin pilot over `s6_runner.campaign`: the arms live in the runner, next to the
three they must stay bit-identical to. Nothing under results/S6_synchronized_traces/ is written or
regenerated -- the identity of the trunk rows with the committed S6 rows IS the acceptance gate
(D3-bis), and regenerating S6 would move `envelope_stats.json` and the manuscript macros for
nothing.

  smoke   5 seeds x 3 magnitudes x 5 arms
  full    100 seeds x 20 magnitudes x 5 arms
  causal  trunk gate (D3-bis), the four-term decomposition (D1/D2), detection counts (D3)

Usage:  PYTHONHASHSEED=0 python experiments/S8_generality/s8_arms.py [smoke|full|causal]
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.dataset as ds
import pyarrow.parquet as pq
from joblib import Parallel, delayed

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "S6_synchronized_traces"))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "S6_synchronized_traces" / "gates"))

import s6_causal as causal  # noqa: E402
import s6_envelope_stats as envelope  # noqa: E402
import s6_runner as runner  # noqa: E402
import s6_writer as writer  # noqa: E402
import _gate_common as common  # noqa: E402
from config import experiment_ssot as ssot  # noqa: E402

RESULTS_DIR = ssot.RESULTS_DIR / "S8_ab_initio"
S6_DIR = ssot.RESULTS_DIR / "S6_synchronized_traces"
ARMS = ssot.S8_ARM_NAMES
TRUNK_ARMS = ("full", "no_swap", "frozen")
T_HORIZON = ssot.S8_T_HORIZON
WARMUP = ssot.S8_WARMUP_WINDOW
AUDIT_DELTA_P = ssot.S8_AUDIT_DELTA_P
DECISION_LAMBDA = ssot.S8_DECISION_LAMBDA
DECISION_DELTA_E = ssot.S8_DECISION_DELTA_E

PER_TREE_SCHEMA = pa.schema([("delta_e", pa.float64()), ("arm", pa.string()),
                             ("seed", pa.int64()), ("tree_index", pa.int32()),
                             ("tau_i", pa.float64())])


def write_per_tree(records, out_dir):
    """The per-tree tau_i vector, one row per (delta_e, arm, seed, tree).

    `transfer_S3.md` section 6 open item 1: "no committed artifact carries the per-tree tau_i of the
    ARF". Only the four order statistics tau_swap^(q) were persisted. This is the artifact that item
    asks for, and it costs no simulation -- `segment` already diffs the tracker per key."""
    rows = {"delta_e": [], "arm": [], "seed": [], "tree_index": [], "tau_i": []}
    for r in records:
        tau = np.atleast_1d(np.asarray(r["per_tree_tau"], dtype=np.float64))
        for i, t in enumerate(tau):
            rows["delta_e"].append(float(r["delta_e"]))
            rows["arm"].append(r["arm"])
            rows["seed"].append(int(r["seed"]))
            rows["tree_index"].append(np.int32(i))
            rows["tau_i"].append(float(t))
    table = writer._sorted_table(rows, PER_TREE_SCHEMA, ["delta_e", "arm", "seed", "tree_index"])
    return writer._write(table, Path(out_dir) / "s8_tau_per_tree.parquet")


# ══════════════════════════════════════════════════════════════════════════════
# D3-bis -- trunk acceptance gate, blocking, read before any causal output
# ══════════════════════════════════════════════════════════════════════════════
def trunk_identity(s8_runs_path, s6_runs_path):
    """Column-by-column identity of the 'full'/'no_swap'/'frozen' rows against the committed S6 run.

    A divergence means the extra `deepcopy` taken at tau* perturbed the trunk, which would void
    every contrast this campaign is for. The verdict is HALT, never a correction of the new arms."""
    if not s6_runs_path.exists():
        return {"status": "NOT CHECKABLE", "motive": f"absent: {s6_runs_path}"}
    a = pq.read_table(s6_runs_path).to_pandas()
    b = pq.read_table(s8_runs_path).to_pandas()
    keys = ["seed", "delta_e", "arm"]
    m = a.merge(b, on=keys, suffixes=("_s6", "_s8"))
    m = m[m.arm.isin(TRUNK_ARMS)]
    cols = [c[:-3] for c in m.columns if c.endswith("_s6")]
    divergent = {}
    for c in cols:
        u, v = m[f"{c}_s6"], m[f"{c}_s8"]
        if u.equals(v):
            continue
        bad = ~((u.isna() & v.isna()) | (u == v))
        divergent[c] = {"n_rows": int(bad.sum()),
                        "first": [float(u[bad].iloc[0]), float(v[bad].iloc[0])] if bad.any() else None}
    n_expected = len(a[a.arm.isin(TRUNK_ARMS)])
    return {"status": "PRESERVED" if not divergent and len(m) == n_expected else "BREACH",
            "n_rows_joined": int(len(m)), "n_rows_expected": int(n_expected),
            "n_columns_compared": len(cols), "divergent_columns": divergent}


# ══════════════════════════════════════════════════════════════════════════════
# D3 -- decisional reading: external CUSUM detections at lambda = 50, per arm
# ══════════════════════════════════════════════════════════════════════════════
def _detection_partition(part, lam=DECISION_LAMBDA, horizon=T_HORIZON, warmup=WARMUP,
                         delta=AUDIT_DELTA_P):
    """(delta_e, [{arm, n_cross, n}]) -- S_max of the external CUSUM over the common window.

    `p_pre` is the rate MEASURED on the traced pre-drift window of the same trajectory, which is
    what `s6_envelope_stats` does; reading it from runs.parquet instead would silently change the
    published 0/100 and 18/100 counts by a different route than the arm."""
    delta_e = float(Path(part).name.split("=", 1)[1])
    df = ds.dataset(str(part), format="parquet").to_table(
        columns=["arm", "seed", "t_rel", "err"],
        filter=(ds.field("t_rel") >= -warmup) & (ds.field("t_rel") < horizon)
    ).to_pandas().sort_values(["arm", "seed", "t_rel"])
    out = []
    for (arm, seed), g in df.groupby(["arm", "seed"], sort=True):
        err = g["err"].to_numpy(dtype=np.float64)
        post = g["t_rel"].to_numpy() >= 0
        p0 = float(err[~post].mean())
        out.append({"delta_e": delta_e, "arm": arm, "seed": int(seed), "p0_hat": p0,
                    "s_max": envelope.s_max(err[post] - p0 - delta),
                    "cross": bool(envelope.s_max(err[post] - p0 - delta) >= lam)})
    return out


def detection_counts(traces_root, n_jobs=-1):
    parts = sorted(Path(traces_root).iterdir())
    rows = [r for chunk in Parallel(n_jobs=n_jobs)(delayed(_detection_partition)(p) for p in parts)
            for r in chunk]
    df = pd.DataFrame(rows)
    return df.groupby(["delta_e", "arm"], as_index=False).agg(
        n=("cross", "size"), n_cross=("cross", "sum"),
        median_s_max=("s_max", "median"), median_p0_hat=("p0_hat", "median"))


# ══════════════════════════════════════════════════════════════════════════════
def run_campaign(mode):
    seeds = common.seed_pool(ssot.S8_SMOKE_N_SEEDS if mode == "smoke"
                             else len(ssot.S8_CAMPAIGN_SEEDS))
    grid = (list(ssot.S8_SMOKE_DELTA_E) if mode == "smoke" else
            [float(np.round(common.norm.cdf(b / np.sqrt(2)) - 0.5, 6))
             for b in ssot.S8_CAMPAIGN_BOUNDARY_SHIFTS])
    out = RESULTS_DIR / ("smoke" if mode == "smoke" else "data")
    print(f"[INFO] S8 ab initio {mode}: {len(seeds)} seeds x {len(grid)} magnitudes x "
          f"{len(ARMS)} arms {list(ARMS)} -> {out.relative_to(ssot.ROOT_DIR)}")
    summary = runner.campaign(seeds, grid, out, desc=f"S8 {mode}", arms=ARMS)
    per_tree = write_per_tree(summary["record_rows"], out)
    print(f"[INFO] {summary['records']} run records, {summary['trace_rows']:,} trace rows in "
          f"{summary['wall_clock_s']:.1f}s")
    print(f"[INFO] wrote {per_tree.relative_to(ssot.ROOT_DIR)}")
    return out


def run_causal(which="data"):
    base = RESULTS_DIR / which
    # smoke tables stay inside smoke/: a smoke run must never be able to leave its numbers behind
    # in the campaign table directory under a name that reads as the campaign's.
    tables = base if which == "smoke" else RESULTS_DIR / "tables"
    tables.mkdir(parents=True, exist_ok=True)
    s6_base = S6_DIR / ("smoke" if which == "smoke" else "data")

    gate = trunk_identity(base / "runs.parquet", s6_base / "runs.parquet")
    (tables / "s8_trunk_identity.json").write_text(
        json.dumps(gate, indent=2, sort_keys=True, default=float) + "\n", encoding="utf-8")
    print(f"[D3-bis] trunk identity vs {s6_base.relative_to(ssot.ROOT_DIR)}: {gate['status']} "
          f"({gate.get('n_rows_joined')} of {gate.get('n_rows_expected')} rows, "
          f"{gate.get('n_columns_compared')} columns)")
    if gate["status"] == "BREACH":
        raise SystemExit(f"[HALT] D3-bis trunk breach: {gate['divergent_columns']}")

    payload = causal.main(which, base=base, out_name="s8_causal.json")

    counts = detection_counts(base / "traces.parquet")
    counts.to_csv(tables / "s8_detection_counts.csv", index=False)
    anchor = counts[np.isclose(counts.delta_e, DECISION_DELTA_E)] if which != "smoke" else counts
    print(f"\n[D3] external CUSUM detections at lambda = {DECISION_LAMBDA:g}, "
          f"delta_P = {AUDIT_DELTA_P}, window [0, {T_HORIZON})")
    print(anchor.to_string(index=False))
    print(f"[INFO] wrote {(tables / 's8_detection_counts.csv').relative_to(ssot.ROOT_DIR)}")
    return payload


def demo():
    """Self-check of the two non-trivial helpers, on constructed inputs."""
    recs = [{"delta_e": 0.25, "arm": "full", "seed": 7,
             "per_tree_tau": np.array([3.0, np.nan, 1.0])}]
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        p = write_per_tree(recs, d)
        t = pq.read_table(p).to_pandas()
        assert list(t.tree_index) == [0, 1, 2] and t.tau_i.tolist()[0] == 3.0
        assert np.isnan(t.tau_i.tolist()[1]) and t.tau_i.tolist()[2] == 1.0
        assert pq.read_table(p).schema.equals(PER_TREE_SCHEMA)
    print("s8_arms demo: OK")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "full"
    if mode == "demo":
        demo()
    elif mode in ("smoke", "full"):
        run_campaign(mode)
    elif mode == "causal":
        run_causal(sys.argv[2] if len(sys.argv) > 2 else "data")
    else:
        raise SystemExit(f"usage: s8_arms.py [smoke|full|causal|demo]  (got {mode!r})")
