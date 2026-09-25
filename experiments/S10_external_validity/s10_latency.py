"""Stream S10 / T10.1 -- label latency: what a delay of l steps on the labels does to detection and
to the budget available before erasure.

The external monitor reads an error stream, and an error needs a label. Two latency models are
measured and never merged (docs/theory/S10_decision_rules.md, Part A):

  M1  monitor-only latency. The learner trains on labels as they arrive; the monitor reads e_t at
      t + l. The error sequence is the trunk's, so P-a and P-b of the prompt hold by construction.
  M2  shared latency. Learner and monitor wait for the same label. At wall-clock t the prediction of
      x_t precedes the arrival of y_{t-l}, so it is made by S_{t-l}, the state that has learnt
      samples 0 .. t-l-1.

ONE SIMULATION SERVES BOTH. Under M2 the learner absorbs the trunk's samples in the trunk's order,
and predict_one consumes no entropy (gate G0), so the state trajectory is the trunk's. Running the
trunk once and letting the CURRENT state S_t also score x[t + l] for every l > 0 therefore yields,
exactly, the prediction a learner with latency l makes at t + l. `LaggedARF` wraps the forest to do
it while `s6_runner.segment` runs unchanged; row 0 of its error matrix is the trunk's own column.
`tests/test_S10_external_validity.py` checks the identity against a forest that really waits.

THE TRUNK IS S6's. `simulate` reproduces arm 'full' of `s6_runner.simulate` step for step -- same
segments, same fork bookkeeping, same `_metrics` -- so its records are compared with the committed
S6 and S8 runs.parquet (rule L0) before any number is read. The deepcopies `s6_runner.simulate`
takes for its branches are omitted: gate G1 and S8's trunk gate established that they consume no
entropy.

  demo     one cell per stream, identity asserts, no write
  smoke    5 seeds x 3 magnitudes x 2 streams; rule L0(b) against the committed S6 smoke traces
  full     100 seeds x 20 magnitudes x 2 streams; rule L0(a) against the committed runs.parquet
  analyse  rules L0(c) and L1-L4 over the traces of `full` (`analyse smoke` reads the smoke corpus)

Usage:  PYTHONHASHSEED=0 python experiments/S10_external_validity/s10_latency.py [demo|smoke|full|analyse [smoke]]
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.dataset as ds
import pyarrow.parquet as pq
from joblib import Parallel, delayed
from scipy.stats import binomtest

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "S6_synchronized_traces"))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "S6_synchronized_traces" / "gates"))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "S8_generality"))
from config import experiment_ssot as ssot  # noqa: E402

import _gate_common as common  # noqa: E402
import s6_defs as defs  # noqa: E402
import s6_runner as runner  # noqa: E402
import s6_writer as writer  # noqa: E402
import s8_rotation as rot  # noqa: E402
from s6_detectors import PHT  # noqa: E402

N_STEPS = ssot.S6_N_STEPS
T_DRIFT = ssot.S6_T_DRIFT
N_MODELS = ssot.S6_N_MODELS
C_INT = ssot.S6_C_INT
WARMUP = ssot.S10_WARMUP_WINDOW
TRACE_POST = ssot.S10_TRACE_POST
T_HORIZON = ssot.S10_T_HORIZON
LAGS = list(ssot.S10_LAGS)
LAMBDAS = list(ssot.S10_LAMBDAS)
DELTA_P = ssot.DELTA_P                          # PageHinkley and def:budget read the River tolerance
TEST_LAMBDA = ssot.S10_TEST_LAMBDA
TEST_LAG = ssot.S10_TEST_LAG
S9_LAMBDAS = ssot.S6_AUDIT_LAMBDAS              # [15, 50], the thresholds S9's ordering tables carry
OUT_DIR = ssot.RESULTS_DIR / "S10_external_validity"
TABLES = OUT_DIR / "tables"

STREAMS = {"canonical": runner.make_stream, "rotation": rot.STREAM_FN[ssot.S10_ROTATION_ETA]}
ORACLES = {"canonical": ssot.RESULTS_DIR / "S6_synchronized_traces" / "data" / "runs.parquet",
           "rotation": (ssot.RESULTS_DIR / "S8_rotation_generator" / "data"
                        / rot.eta_tag(ssot.S10_ROTATION_ETA) / "runs.parquet")}
S6_SMOKE_TRACES = ssot.RESULTS_DIR / "S6_synchronized_traces" / "smoke" / "traces.parquet"
S9_ORDERING = {"canonical": ssot.RESULTS_DIR / "S9_detector_coverage" / "tables" / "s9_family_ordering.json",
               "rotation": (ssot.RESULTS_DIR / "S9_detector_coverage" / "tables"
                            / "s9_family_ordering_rotation.json")}

TRACES_SCHEMA = pa.schema([("seed", pa.int64()), ("t_rel", pa.int32())]
                          + [(f"err_l{lag}", pa.int8()) for lag in LAGS])
RUNS_SCHEMA = pa.schema(
    [("stream", pa.string()), ("delta_e", pa.float64()), ("seed", pa.int64()), ("lag", pa.int32()),
     ("tau_swap", pa.float64()), ("p0", pa.float64()), ("de_emp", pa.float64()), ("T", pa.float64()),
     ("w", pa.float64()), ("a", pa.float64()), ("a_avail_m1", pa.float64()),
     ("a_avail_m2", pa.float64()), ("w_s6", pa.float64())]
    + [(f"d_lambda{lam:g}", pa.float64()) for lam in LAMBDAS])


# ══════════════════════════════════════════════════════════════════════════════
# The lagged proxy and the trunk
# ══════════════════════════════════════════════════════════════════════════════
class LaggedARF:
    """Delegates to the forest. Each `predict_one(x_t)` also scores x[t + l], l > 0, with the CURRENT
    state S_t -- the prediction a learner whose labels arrive l steps late makes at t + l. Row k of
    `err` is the error stream under lag `lags[k]`; row 0 is the trunk's. Targets below `first` are
    not scored: no rule reads them."""

    def __init__(self, arf, x, y, lags, first):
        if list(lags)[0] != 0:
            raise ValueError("row 0 must be the trunk: lags must start at 0")
        self.arf, self.x, self.y, self.lags, self.first = arf, x, y, list(lags), int(first)
        self.err = np.zeros((len(self.lags), len(y)), dtype=np.int8)
        self.t = 0

    def _score(self, u):
        p = self.arf.predict_one({0: self.x[u, 0], 1: self.x[u, 1]})
        return int((p if p is not None else 0) != self.y[u])

    def predict_one(self, x_dict):
        for k, lag in enumerate(self.lags[1:], start=1):
            u = self.t + lag
            if self.first <= u < len(self.y):
                self.err[k, u] = self._score(u)
        p = self.arf.predict_one(x_dict)
        self.err[0, self.t] = int((p if p is not None else 0) != self.y[self.t])
        return p

    def learn_one(self, x_dict, y):
        self.arf.learn_one(x_dict, y)
        self.t += 1

    def __getattr__(self, name):              # _drift_tracker, data: read by segment / _forest_shape
        if name == "arf":
            raise AttributeError(name)
        return getattr(self.arf, name)


def simulate(seed, delta_e, stream):
    """Arm 'full' of `s6_runner.simulate`, step for step, with every lag scored on the way.
    Returns (the S6 run record of the trunk, one trace frame over t_rel in [-WARMUP, TRACE_POST))."""
    safe_seed, x, y = STREAMS[stream](seed, delta_e)
    arf = common.make_arf(safe_seed, N_MODELS, C_INT)
    m = LaggedARF(arf, x, y, LAGS, first=T_DRIFT - WARMUP)

    def run(lo, hi, **kw):
        seg, stopped = runner.segment(m, x, y, lo, hi, **kw)
        if m.t != stopped:
            raise RuntimeError(f"proxy clock {m.t} != segment clock {stopped}")
        return seg, stopped

    run(0, T_DRIFT - runner.TRACE_PRE, observe=False, track=False)
    pre, _ = run(T_DRIFT - runner.TRACE_PRE, T_DRIFT)
    pre_swaps = len(arf._drift_tracker)
    nodes_at_drift = runner._forest_shape(arf)[0]
    head, fork_abs = run(T_DRIFT, N_STEPS, stop_on_new_tree=True)
    fork_taken = fork_abs < N_STEPS
    fork_t_rel = fork_abs - 1 - T_DRIFT if fork_taken else None
    tail, _ = run(fork_abs, N_STEPS) if fork_taken else (None, None)
    post = runner._concat(head, tail) if fork_taken else head
    record, _ = runner._metrics(seed, delta_e, "full", post, pre["err"], pre_swaps, fork_t_rel,
                                nodes_at_drift)

    lo = T_DRIFT - WARMUP
    if not np.array_equal(m.err[0, lo:], np.concatenate([pre["err"], post["err"]])):
        raise RuntimeError("row 0 of the proxy is not the trunk's error column")
    n = N_STEPS - lo
    frame = {"seed": np.full(n, seed, dtype=np.int64),
             "t_rel": np.arange(-WARMUP, N_STEPS - T_DRIFT, dtype=np.int32),
             **{f"err_l{lag}": m.err[k, lo:].copy() for k, lag in enumerate(LAGS)}}
    return record, frame


def campaign(stream, seeds, grid, out_dir, n_jobs=-1):
    """One stream, one magnitude at a time: each hive partition is written before the next."""
    t0 = time.perf_counter()
    root = writer.trace_root(out_dir, reset=True)
    records, rows = [], 0
    for de in grid:
        out = Parallel(n_jobs=n_jobs)(delayed(simulate)(s, de, stream) for s in seeds)
        records += [r for r, _ in out]
        cols = {f.name: np.concatenate([fr[f.name] for _, fr in out]) for f in TRACES_SCHEMA}
        table = writer._sorted_table(cols, TRACES_SCHEMA, ["seed", "t_rel"])
        writer._write(table, root / f"delta_e={ssot.S6_PARQUET_PARTITION_FMT.format(de)}"
                      / "part-0.parquet")
        rows += table.num_rows
        print(f"    {stream} delta_e={de:.6f}: {len(out)} runs, {rows:,} trace rows "
              f"({time.perf_counter() - t0:.0f}s)", flush=True)
    return {"records": len(records), "trace_rows": rows,
            "runs_path": writer.write_runs(records, out_dir), "traces_path": root,
            "wall_clock_s": time.perf_counter() - t0}


# ══════════════════════════════════════════════════════════════════════════════
# Rule L0 -- the trunk is S6's and S8's
# ══════════════════════════════════════════════════════════════════════════════
def trunk_identity(new_path, oracle_path):
    """`s9_rotation_traces.trunk_identity`, restricted to arm 'full': the S6 oracle carries four."""
    a = pq.read_table(new_path).to_pandas()
    b = pq.read_table(oracle_path).to_pandas()
    b = b[b.arm == "full"].copy()
    keys = ["delta_e", "seed", "arm"]
    for df in (a, b):
        df["delta_e"] = df["delta_e"].round(6)
    m = a.merge(b, on=keys, suffixes=("_new", "_ref"), how="inner")
    shared = [c for c in a.columns if c not in keys and c in b.columns]
    bad = {}
    for c in shared:
        x, y = m[f"{c}_new"].to_numpy(), m[f"{c}_ref"].to_numpy()
        if x.dtype.kind in "fc" or y.dtype.kind in "fc":
            same = np.array_equal(np.nan_to_num(x.astype(float), nan=-np.inf),
                                  np.nan_to_num(y.astype(float), nan=-np.inf))
        else:
            same = np.array_equal(x, y)
        if not same:
            bad[c] = int((x != y).sum())
    return {"oracle": str(Path(oracle_path).relative_to(ssot.ROOT_DIR)),
            "rows_joined": int(len(m)), "rows_new": int(len(a)), "rows_ref_full": int(len(b)),
            "columns_compared": len(shared), "columns_divergent": bad,
            "verdict": "PRESERVED" if not bad and len(m) == len(a) == len(b) else "BREACH"}


def smoke_err_identity(s10_root):
    """L0(b): the lag-0 error column equals the committed S6 smoke traces, arm 'full', bit for bit."""
    ref = ds.dataset(str(S6_SMOKE_TRACES), format="parquet",
                     partitioning=writer.TRACES_PARTITIONING).to_table(
        columns=["delta_e", "arm", "seed", "t_rel", "err"],
        filter=ds.field("arm") == "full").to_pandas()
    new = ds.dataset(str(s10_root), format="parquet",
                     partitioning=writer.TRACES_PARTITIONING).to_table(
        columns=["delta_e", "seed", "t_rel", "err_l0"]).to_pandas()
    m = ref.merge(new, on=["delta_e", "seed", "t_rel"], how="outer", indicator=True)
    both = m["_merge"] == "both"
    diverge = int((m.loc[both, "err"].astype(int) != m.loc[both, "err_l0"].astype(int)).sum())
    return {"oracle": str(S6_SMOKE_TRACES.relative_to(ssot.ROOT_DIR)),
            "rows_ref": int(len(ref)), "rows_new": int(len(new)), "rows_joined": int(both.sum()),
            "err_divergent": diverge,
            "verdict": "PRESERVED" if diverge == 0 and both.all() else "BREACH"}


# ══════════════════════════════════════════════════════════════════════════════
# Per-run quantities (decision rules, Part B)
# ══════════════════════════════════════════════════════════════════════════════
def pht_trace(x):
    """River PageHinkley at an alarm-disabled threshold: the S9 sentinel, exact up to the first
    crossing of every finite threshold."""
    pht = PHT(threshold=ssot.S9_PHT_TRACE_THRESHOLD, delta=DELTA_P)
    out = np.empty(len(x))
    for j, v in enumerate(x):
        pht.update(float(v))
        out[j] = pht.statistic()
    return out


def lag_quantities(err, t_rel, tau_swap, horizon=T_HORIZON):
    """Per-run quantities of one error stream, Part B as amended by erratum E1.

    `T` is the erasure instant the manuscript names tau_erase (\\SixTauErase): the argmax of the
    unreflected accumulation, searched from the first replacement `tau_swap` by `s6_defs.tau_erase`.
    `w` is def:times W, kept as a descriptive reading only. `d` is a DATA index -- the t_rel of the
    error whose ingestion caused the crossing -- or None."""
    err = np.asarray(err, dtype=np.float64)
    pre, post = err[t_rel < 0], err[t_rel >= 0]
    p0, de_emp = defs.empirical_delta_e(pre, post)
    a_unrefl = defs.accumulations(post, p0)[0]
    fed = (t_rel >= -WARMUP) & (t_rel < horizon)
    stat, tr = pht_trace(err[fed]), t_rel[fed]
    d = {}
    for lam in LAMBDAS:
        hit = np.flatnonzero(stat > lam)
        d[lam] = int(tr[hit[0]]) if hit.size else None
    q = {"p0": p0, "de_emp": de_emp, "T": defs.tau_erase(a_unrefl, tau_swap), "a_unrefl": a_unrefl,
         "w": defs.tau_err_framework(post, p0, DELTA_P, horizon=horizon), "d": d}
    q["a"] = budget_read(q, 0)
    return q


def budget_read(q, lag):
    """Evidence read before the wall-clock erasure: the running maximum of the unreflected
    accumulation up to T - lag, floored at 0. 0 when the monitor has read no post-drift datum by
    then; NaN when T is censored (erratum E1)."""
    if not np.isfinite(q["T"]):
        return np.nan
    cut = int(q["T"]) - lag
    if cut < 0:
        return 0.0
    return max(0.0, float(np.max(q["a_unrefl"][:cut + 1])))


def detected_within(d, lag, deadline):
    """The crossing caused by datum d is raised at wall clock d + lag: before the erasure deadline?"""
    return bool(d is not None and d >= 0 and np.isfinite(deadline) and d + lag <= deadline)


def _same(x, y):
    return (np.isnan(x) and np.isnan(y)) or x == y


def run_rows(stream, delta_e, seed, frame, tau_swap, tau_erase_record):
    """Five rows, one per lag, for one (stream, magnitude, seed). Under M2 the first replacement
    reaches the predictions `lag` steps late, so the argmax search starts at tau_swap + lag."""
    t_rel = frame["t_rel"]
    e0 = frame["err_l0"]
    q0 = lag_quantities(e0, t_rel, tau_swap)
    if not _same(q0["T"], tau_erase_record):
        raise RuntimeError(f"L0: T(0) = {q0['T']} is not the record's tau_erase {tau_erase_record}")
    w_s6 = defs.tau_err_framework(np.asarray(e0, dtype=np.float64)[t_rel >= 0], q0["p0"], DELTA_P)
    rows = []
    for lag in LAGS:
        q = q0 if lag == 0 else lag_quantities(frame[f"err_l{lag}"], t_rel, tau_swap + lag)
        m1 = budget_read(q0, lag)
        if lag and np.isfinite(m1) and np.isfinite(rows[-1]["a_avail_m1"]) \
                and m1 > rows[-1]["a_avail_m1"] + 1e-9:
            raise AssertionError("M1 budget increased with the lag -- the truncation is broken")
        rows.append({"stream": stream, "delta_e": round(float(delta_e), 6), "seed": int(seed),
                     "lag": int(lag), "tau_swap": float(tau_swap + lag), "p0": q["p0"],
                     "de_emp": q["de_emp"], "T": q["T"], "w": q["w"], "a": q["a"],
                     "a_avail_m1": m1, "a_avail_m2": budget_read(q, lag),
                     "w_s6": w_s6 if lag == 0 else np.nan,
                     **{f"d_lambda{lam:g}": (np.nan if q["d"][lam] is None else float(q["d"][lam]))
                        for lam in LAMBDAS}})
    return rows


def partition_rows(stream, part, records):
    """`records`: {seed: (tau_swap_q010, tau_erase)} of this magnitude, from the trunk's runs.parquet."""
    delta_e = float(Path(part).name.split("=", 1)[1])
    df = pq.read_table(Path(part) / "part-0.parquet").to_pandas().sort_values(["seed", "t_rel"])
    out = []
    for seed, g in df.groupby("seed", sort=True):
        frame = {c: g[c].to_numpy() for c in g.columns}
        tau_swap, tau_erase = records[int(seed)]
        out += run_rows(stream, delta_e, seed, frame, tau_swap, tau_erase)
    return out


# ══════════════════════════════════════════════════════════════════════════════
# Inference -- the seed is the unit (deff = 20 magnitudes per seed)
# ══════════════════════════════════════════════════════════════════════════════
def cluster_median_ci(values, clusters, n_boot=ssot.S10_N_BOOTSTRAP, seed=ssot.S10_BOOTSTRAP_SEED,
                      level=0.95):
    """Percentile interval of the median, resampling whole CLUSTERS (seeds) with replacement."""
    values, clusters = np.asarray(values, dtype=np.float64), np.asarray(clusters)
    ok = np.isfinite(values)
    values, clusters = values[ok], clusters[ok]
    if values.size == 0:
        return None, None
    ids, inv = np.unique(clusters, return_inverse=True)
    groups = [values[inv == k] for k in range(ids.size)]
    draws = np.random.default_rng(seed).integers(0, ids.size, size=(n_boot, ids.size))
    meds = np.array([np.median(np.concatenate([groups[k] for k in row])) for row in draws])
    lo, hi = np.percentile(meds, [50 * (1 - level), 50 * (1 + level)])
    return float(lo), float(hi)


def sign_test(per_seed):
    """Two-sided sign test on per-seed statistics, ties dropped: the R4 / R5 form."""
    v = np.asarray([x for x in per_seed if x is not None and np.isfinite(x)], dtype=np.float64)
    n_plus, n_minus = int((v > 0).sum()), int((v < 0).sum())
    n = n_plus + n_minus
    p = float(binomtest(max(n_plus, n_minus), n, 0.5).pvalue) if n else 1.0
    return {"p": p, "n_plus": n_plus, "n_minus": n_minus, "n_eff": n, "n_seeds": int(v.size)}


def _med(x):
    x = np.asarray(x, dtype=np.float64)
    x = x[np.isfinite(x)]
    return float(np.median(x)) if x.size else None


def _deadline(df, lag, lam):
    """(detected before the erasure deadline T, deadline finite) for every row, alarm moved by `lag`."""
    d = df[f"d_lambda{lam:g}"].to_numpy()
    T = df["T"].to_numpy()
    det = np.array([detected_within(None if np.isnan(di) else int(di), lag, ti)
                    for di, ti in zip(d, T)], dtype=bool)
    return det, np.isfinite(T)


# ══════════════════════════════════════════════════════════════════════════════
# Aggregation
# ══════════════════════════════════════════════════════════════════════════════
def arm_view(runs, stream, arm, lag):
    """The rows an arm reads at `lag`. M1: the trunk's stream, deadline W(0), alarm moved by lag.
    M2: the lag-`lag` stream, its own W(lag). Indexed by (delta_e, seed)."""
    src = runs[(runs.stream == stream) & (runs.lag == (0 if arm == "M1" else lag))]
    return src.set_index(["delta_e", "seed"]).sort_index()


def rates(runs, stream, arm, lag, lam, delta_e=None):
    v = arm_view(runs, stream, arm, lag)
    if delta_e is not None:
        v = v.loc[[delta_e]]
    det, finite = _deadline(v, lag, lam)
    d = v[f"d_lambda{lam:g}"].to_numpy()
    n = len(v)
    return {"n": n, "n_deadline_finite": int(finite.sum()),
            "pre_drift_alarm_rate": round(float(np.mean(d < 0)), 4),
            "detect_within_W_rate": (None if not finite.any()
                                     else round(float(det.sum() / finite.sum()), 4)),
            "detect_at_all_rate": round(float(np.mean((d >= 0) & (d < T_HORIZON))), 4)}


def per_seed(runs, stream, fn):
    """[statistic of one seed] -- fn reads that seed's rows, every magnitude and every lag."""
    sub = runs[runs.stream == stream]
    return [fn(g) for _, g in sub.groupby("seed", sort=True)]


def _at(g, lag):
    """One seed's rows at `lag`, indexed by delta_e; every seed carries every (magnitude, lag)."""
    return g[g.lag == lag].set_index("delta_e").sort_index()


def _median_shift(lagged, trunk):
    ok = np.isfinite(lagged.to_numpy()) & np.isfinite(trunk.to_numpy())
    return float(np.median((lagged - trunk).to_numpy()[ok])) if ok.any() else None


def seed_erasure_shift(g):
    """L2 (erratum E1): median over magnitudes of T(500) - T(0)."""
    return _median_shift(_at(g, TEST_LAG)["T"], _at(g, 0)["T"])


def seed_budget_shift(g):
    """L3: median over magnitudes of A_avail^M2(500) - A(0)."""
    return _median_shift(_at(g, TEST_LAG)["a_avail_m2"], _at(g, 0)["a"])


def seed_detection_shift(arm):
    """L4: detections within the deadline at lag 500 minus at lag 0, over the magnitudes whose
    deadlines are finite at both lags. M1 moves the trunk's alarm; M2 reads the lag-500 stream."""
    def fn(g):
        lagged, trunk = _at(g, 0 if arm == "M1" else TEST_LAG), _at(g, 0)
        det_l, fin_l = _deadline(lagged, TEST_LAG, TEST_LAMBDA)
        det_0, fin_0 = _deadline(trunk, 0, TEST_LAMBDA)
        ok = fin_l & fin_0
        return float(det_l[ok].sum()) - float(det_0[ok].sum())
    return fn


def verdict_l1(lo, hi, lag):
    if lo is None:
        return "UNDECIDED"
    tol = max(1.0, 0.1 * lag)
    if -tol <= lo and hi <= tol:
        return "P-a HOLDS"
    if hi < -tol:
        return "EARLIER"
    if lo > tol:
        return "LATER"
    return "UNDECIDED"


def summarise(runs):
    out = {"streams": {}, "tests": {}}
    for stream in STREAMS:
        sub = runs[runs.stream == stream]
        trunk = sub[sub.lag == 0]
        s = {"p0": {"median": _med(trunk.p0), "min": float(trunk.p0.min()), "max": float(trunk.p0.max())},
             "n_runs": int(len(trunk)), "rates": [], "shifts": {}, "budgets": {}}
        grid = sorted(trunk.delta_e.unique())
        for arm in ("M1", "M2"):
            for lag in LAGS:
                for lam in LAMBDAS:
                    for de in [None] + grid:
                        s["rates"].append({"arm": arm, "lag": lag, "lambda": lam,
                                           "delta_e": de, **rates(runs, stream, arm, lag, lam, de)})
        for lag in LAGS[1:]:
            lagged = sub[sub.lag == lag].set_index(["delta_e", "seed"]).sort_index()
            base = trunk.set_index(["delta_e", "seed"]).sort_index()
            seeds = base.index.get_level_values("seed").to_numpy()
            dT = (lagged["T"] - base["T"]).to_numpy()
            dw = (lagged.w - base.w).to_numpy()
            entry = {"T_shift_median": _med(dT), "T_shift_ci": cluster_median_ci(dT, seeds),
                     "T_shift_over_lag_median": _med(dT / lag),
                     "T_shift_over_lag_ci": cluster_median_ci(dT / lag, seeds),
                     "n_T_finite_both": int(np.isfinite(dT).sum()),
                     "descriptive_def_times_W": {"shift_median": _med(dw),
                                                 "shift_ci": cluster_median_ci(dw, seeds),
                                                 "n_finite_both": int(np.isfinite(dw).sum()),
                                                 "W0_median": _med(base.w),
                                                 "W0_share_beyond_2000": float(np.mean(base.w > 2000))},
                     "d_shift": {}}
            for lam in LAMBDAS:
                dl, d0 = lagged[f"d_lambda{lam:g}"].to_numpy(), base[f"d_lambda{lam:g}"].to_numpy()
                ok = (dl >= 0) & (d0 >= 0) & (dl < T_HORIZON) & (d0 < T_HORIZON)
                delta = np.where(ok, dl - d0, np.nan)
                lo, hi = cluster_median_ci(delta, seeds)
                entry["d_shift"][f"{lam:g}"] = {"median": _med(delta), "ci": (lo, hi),
                                                "n_pairs": int(ok.sum()),
                                                "verdict_L1": (verdict_l1(lo, hi, lag)
                                                               if lam == TEST_LAMBDA else None)}
            s["shifts"][str(lag)] = entry
        # Both arms' budgets at lag l live on the lag-l row: a_avail_m1 is computed from the trunk's
        # stream (run_rows), a_avail_m2 from the lag-l stream.
        base = trunk.set_index(["delta_e", "seed"]).sort_index()
        seeds = base.index.get_level_values("seed").to_numpy()
        for arm, col in (("M1", "a_avail_m1"), ("M2", "a_avail_m2")):
            s["budgets"][arm] = {}
            for lag in LAGS:
                a_av = sub[sub.lag == lag].set_index(["delta_e", "seed"]).sort_index()[col].to_numpy()
                with np.errstate(divide="ignore", invalid="ignore"):
                    ratio = a_av / base["a"].to_numpy()
                s["budgets"][arm][str(lag)] = {"median": _med(a_av), "ci": cluster_median_ci(a_av, seeds),
                                               "over_A0_median": _med(ratio),
                                               "over_A0_ci": cluster_median_ci(ratio, seeds)}
        out["streams"][stream] = s
        out["tests"][f"S10-L2-{stream}"] = {"rule": "L2", "stream": stream, "arm": "M2",
                                            **sign_test(per_seed(runs, stream, seed_erasure_shift))}
        out["tests"][f"S10-L3-{stream}"] = {"rule": "L3", "stream": stream, "arm": "M2",
                                            **sign_test(per_seed(runs, stream, seed_budget_shift))}
        for arm in ("M1", "M2"):
            out["tests"][f"S10-L4-{arm}-{stream}"] = {
                "rule": "L4", "stream": stream, "arm": arm,
                **sign_test(per_seed(runs, stream, seed_detection_shift(arm)))}
    return out


def s9_crosscheck(runs, stream):
    """L0(c): at lag 0 and with W at S6's horizon, the PHT rates equal S9's ordering cells."""
    cells = json.loads(S9_ORDERING[stream].read_text(encoding="utf-8"))["cells"]
    ref = {(round(c["delta_e"], 6), c["threshold"]): c for c in cells
           if c["family"] == "PHT" and c["setting"] == "published" and c["input_arm"] == "raw"}
    trunk = runs[(runs.stream == stream) & (runs.lag == 0)]
    bad, checked = [], 0
    for (de, lam), c in sorted(ref.items()):
        g = trunk[np.isclose(trunk.delta_e, de)]
        d, w = g[f"d_lambda{lam:g}"].to_numpy(), g["w_s6"].to_numpy()
        fin = np.isfinite(w)
        inw = int(np.sum(fin & (d >= 0) & (d <= np.where(fin, w, -1))))
        mine = {"pre_drift_alarm_rate": round(float(np.mean(d < 0)), 4),
                "detect_within_W_rate": None if not fin.any() else round(inw / int(fin.sum()), 4)}
        checked += 1
        for k in mine:
            if mine[k] != c[k]:
                bad.append({"delta_e": de, "lambda": lam, "field": k, "s10": mine[k], "s9": c[k]})
    return {"oracle": str(S9_ORDERING[stream].relative_to(ssot.ROOT_DIR)), "cells_checked": checked,
            "divergent": bad, "verdict": "PRESERVED" if checked and not bad else "BREACH"}


# ══════════════════════════════════════════════════════════════════════════════
# Entry points
# ══════════════════════════════════════════════════════════════════════════════
def _grid():
    return [float(np.round(common.norm.cdf(b / np.sqrt(2)) - 0.5, 6))
            for b in ssot.S6_CAMPAIGN_BOUNDARY_SHIFTS]


def _env():
    return {k: v for k, v in common.env_stamp().items() if k != "executable"}


def _json_safe(x):
    if isinstance(x, dict):
        return {str(k): _json_safe(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_json_safe(v) for v in x]
    if isinstance(x, (float, np.floating)):
        return None if not np.isfinite(x) else float(x)
    if isinstance(x, np.integer):
        return int(x)
    return x


def _write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_json_safe(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"[INFO] wrote {path.relative_to(ssot.ROOT_DIR)}")


def _record_index(runs_path):
    """{delta_e: {seed: (tau_swap_q010, tau_erase)}} of the trunk records, for the argmax start."""
    r = pq.read_table(runs_path).to_pandas()
    r["delta_e"] = r["delta_e"].round(6)
    return {de: {int(s): (float(a), float(b)) for s, a, b in zip(g.seed, g.tau_swap_q010, g.tau_erase)}
            for de, g in r.groupby("delta_e")}


def demo():
    seed = common.seed_pool(1)[0]
    for stream in STREAMS:
        rec, frame = simulate(seed, ssot.S6_GATE_DELTA_E[1], stream)
        rows = run_rows(stream, ssot.S6_GATE_DELTA_E[1], seed, frame, rec["tau_swap_q010"],
                        rec["tau_erase"])
        assert [r["lag"] for r in rows] == LAGS
        print(f"s10_latency demo {stream}: e_pre={rec['e_pre']:.4f} tau_erase={rec['tau_erase']} "
              + " ".join(f"T({r['lag']})={r['T']}" for r in rows))
    print("s10_latency demo: OK")


def main(mode="full", which="data"):
    if mode == "demo":
        return demo()
    if mode in ("smoke", "full"):
        smoke = mode == "smoke"
        seeds = common.seed_pool(ssot.S10_SMOKE_N_SEEDS if smoke else ssot.S10_N_SEEDS)
        grid = list(ssot.S10_SMOKE_DELTA_E) if smoke else _grid()
        report = {"mode": mode, "seeds": len(seeds), "magnitudes": len(grid), "lags": LAGS,
                  "env": _env(), "streams": {}}
        for stream in STREAMS:
            out = OUT_DIR / ("smoke" if smoke else "data") / stream
            print(f"=== S10 T10.1 {mode}: {stream}, {len(seeds)} seeds x {len(grid)} magnitudes, "
                  f"lags {LAGS} -> {out.relative_to(ssot.ROOT_DIR)}")
            c = campaign(stream, seeds, grid, out)
            print(f"[INFO] {c['records']} records, {c['trace_rows']:,} trace rows in "
                  f"{c['wall_clock_s']:.1f}s")
            if smoke:
                ident = (smoke_err_identity(c["traces_path"]) if stream == "canonical" else
                         {"verdict": "SKIPPED", "reason": "no committed rotation smoke corpus"})
            else:
                ident = trunk_identity(c["runs_path"], ORACLES[stream])
            report["streams"][stream] = ident
            print(f"--- L0 {stream}: {ident['verdict']}")
        _write_json(TABLES / f"s10_latency_trunk_identity{'_smoke' if smoke else ''}.json", report)
        if any(v["verdict"] == "BREACH" for v in report["streams"].values()):
            raise SystemExit("[FATAL] rule L0 BREACH -- the trunk is not S6's; no T10.1 number is read")
        return report
    if mode == "analyse":
        base = OUT_DIR / ("smoke" if which == "smoke" else "data")
        suffix = "_smoke" if which == "smoke" else ""
        ident = json.loads((TABLES / f"s10_latency_trunk_identity{suffix}.json").read_text("utf-8"))
        if any(v["verdict"] == "BREACH" for v in ident["streams"].values()):
            raise SystemExit("[FATAL] rule L0 BREACH on record -- analysis refused")
        index = {stream: _record_index(base / stream / "runs.parquet") for stream in STREAMS}
        tasks = [(stream, p, index[stream][round(float(p.name.split("=", 1)[1]), 6)])
                 for stream in STREAMS for p in sorted((base / stream / "traces.parquet").iterdir())]
        res = Parallel(n_jobs=-1)(delayed(partition_rows)(s, p, rec) for s, p, rec in tasks)
        runs = pd.DataFrame([r for batch in res for r in batch])
        cols = {f.name: runs[f.name].to_numpy() for f in RUNS_SCHEMA}
        writer._write(writer._sorted_table(cols, RUNS_SCHEMA, ["stream", "delta_e", "seed", "lag"]),
                      TABLES / f"s10_latency_runs{suffix}.parquet")
        payload = summarise(runs)
        payload["L0"] = {"a_or_b": ident["streams"],
                         "c": ({s: s9_crosscheck(runs, s) for s in STREAMS} if which != "smoke" else
                               {"verdict": "SKIPPED", "reason": "S9 cells exist for the full grid only"})}
        if which != "smoke" and any(v["verdict"] == "BREACH" for v in payload["L0"]["c"].values()):
            _write_json(TABLES / f"s10_latency{suffix}.json", payload)
            raise SystemExit("[FATAL] rule L0(c) BREACH -- the lag-0 PHT rates do not reproduce S9")
        payload.update({"which": which, "lags": LAGS, "lambdas": LAMBDAS, "test_lambda": TEST_LAMBDA,
                        "test_lag": TEST_LAG, "t_horizon": T_HORIZON, "delta_p": DELTA_P,
                        "n_bootstrap": ssot.S10_N_BOOTSTRAP, "bootstrap_seed": ssot.S10_BOOTSTRAP_SEED,
                        "env": _env()})
        _write_json(TABLES / f"s10_latency{suffix}.json", payload)
        for name, t in sorted(payload["tests"].items()):
            print(f"    {name:26s} n+={t['n_plus']:3d} n-={t['n_minus']:3d} p={t['p']:.3g}")
        return payload
    raise SystemExit(f"usage: s10_latency.py [demo|smoke|full|analyse [smoke]]  (got {mode!r})")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "full", sys.argv[2] if len(sys.argv) > 2 else "data")
