"""Offline replay of the three uninstrumented monitor families on the committed S6 traces.

V7 of stream S6 instrumented the external StrictCUSUM alone. PHT, ADWIN and KSWIN carry no
synchronised trajectory anywhere in this repository, so the "structurally immune" claim of
`.tex:500` rests on no measurement of the canonical family. This script closes that gap by REPLAY:
it reads `results/S6_synchronized_traces/data/traces.parquet` partition by partition and re-runs the
three detectors on the committed per-step error column. No stream is simulated, no classifier is
trained, and nothing under `results/S6_synchronized_traces/` is written.

The read path is `s6_recompute_cusum_delta001.partition` verbatim in shape -- column projection
`["arm", "seed", "t_rel", "err"]`, pushed-down filter on the arm set and the window -- and the write
path is the deterministic Parquet contract of `s6_writer`. The detector wrappers come from
`s6_detectors`; their `.update / .drift_detected / .statistic() / .threshold / .alarm_sense` contract
is used as it stands and is not extended.

WHEN THE KSWIN STATISTIC EXISTS. `KSWIN._reset()` initialises `p_value = 0`, and River consults it
only inside its `len(window) >= window_size` branch, so the attribute reads 0 on every step before
the first test is performed. A derived alarm rule applied to the raw attribute therefore fires at
t = 0 at every alpha. The trace carries NaN until River's own precondition holds; this was measured
against a live re-armed `drift.KSWIN`, which returns zero pre-drift alarms on the raw arm where the
ungated reading returned a 100 % rate.

WHY ONE PASS SUFFICES FOR EVERY THRESHOLD. River's `PageHinkley` and `KSWIN` both call `_reset()` on
the update following a detection, so a statistic trace taken at a live threshold is
threshold-dependent from the first alarm onward. Taken at a threshold that never fires
(`S9_PHT_TRACE_THRESHOLD = inf`, `S9_KSWIN_TRACE_ALPHA = 1e-300`) the trace is exact for EVERY
threshold up to the first crossing -- which is the whole of what `def:requirement` reads,
`P(tau_det <= tau* + W)`. Past the first alarm this replay reconstructs nothing and claims nothing.
A second property follows and is the reason to prefer it: the KSWIN reservoir draw is then identical
across the whole alpha grid, so the alpha comparison is paired run by run rather than confounded
with a different random reference window.

THE ALARM RULE IS RIVER'S, NOT A RECODING. `kswin.py` fires on `p_value <= alpha` AND `st > 0.1`.
The second conjunct is checked against the exact lattice in `requirement_lattice()` and asserted
slack at every cell of `S9_NSTAT_GRID x S9_KSWIN_ALPHA_GRID` before any alarm is derived; if it ever
binds, this script raises rather than silently dropping a conjunct. KSWIN's inverted alarm sense
(p-value against alpha) is carried as such -- no monotone recoding into an evidence scale.

DETERMINISM. KSWIN is the one stochastic detector here: its reference window is drawn by
`random.Random(seed)`. Each cell `(delta_e, arm, seed, input arm)` derives its own seed from
`SeedSequence`, never from global state, and the triple per-worker lock of `_gate_common.lock_rng`
is applied verbatim. Two runs must produce identical SHA-256 on all four artifacts.

DECLARED DEBT. The trace corpus is reached through a symlink to an artifact that lives outside this
worktree and is not versioned; until it is regenerated, the outputs of this script are not
reproducible from a fresh clone. `docs/ENVIRONMENT.md` carries the same statement.

Usage:  PYTHONHASHSEED=0 python experiments/S9_detector_coverage/s9_offline_detectors.py [smoke|data]
"""
import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.dataset as ds
import pyarrow.parquet as pq
from joblib import Parallel, delayed
from scipy import stats

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "S6_synchronized_traces"))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "S6_synchronized_traces" / "gates"))
from config import experiment_ssot as ssot  # noqa: E402

import s6_writer as writer  # noqa: E402
import _gate_common as common  # noqa: E402
from s6_detectors import ADWINDetector, KSWINDetector, PHT  # noqa: E402

SOURCE_DIR = ssot.RESULTS_DIR / "S6_synchronized_traces"
OUT_DIR = ssot.RESULTS_DIR / "S9_detector_coverage"

WARMUP = ssot.S9_WARMUP_WINDOW
T_HORIZON = ssot.S9_T_HORIZON
TRACE_PRE = ssot.S9_TRACE_PRE
ARMS = list(ssot.S9_OFFLINE_ARMS)
INPUT_ARMS = list(ssot.S9_INPUT_ARMS)
LAMBDAS = ssot.S9_OFFLINE_LAMBDAS
ALPHAS = ssot.S9_KSWIN_ALPHA_GRID
NSTAT_GRID = ssot.S9_NSTAT_GRID
DELTA_P = ssot.DELTA_P                          # A1: PHT and KSWIN read the River tolerance; only
                                                # the StrictCUSUM family reads CUSUM_DELTA_P, and
                                                # that family is already instrumented by S6
N_STAT = ssot.S9_KSWIN_STAT
BUFFER = ssot.S9_KSWIN_BUFFER
PHT_TRACE_THRESHOLD = ssot.S9_PHT_TRACE_THRESHOLD
KSWIN_TRACE_ALPHA = ssot.S9_KSWIN_TRACE_ALPHA
PARTITION_FMT = ssot.S6_PARQUET_PARTITION_FMT

TRACES_SCHEMA = pa.schema(
    [("arm", pa.string()), ("input_arm", pa.string()), ("seed", pa.int64()), ("t_rel", pa.int32()),
     ("pht_stat", pa.float32()), ("adwin_mean", pa.float32()), ("adwin_width", pa.int32()),
     ("adwin_alarm", pa.bool_()), ("kswin_p", pa.float32()), ("kswin_k", pa.int8())]
)


# ══════════════════════════════════════════════════════════════════════════════
# The exact requirement lattice -- computed, not simulated
# ══════════════════════════════════════════════════════════════════════════════
def _ks_lattice(n_stat):
    """[(p_value, method)] indexed by k, for D = k / n_stat at n = m = n_stat.

    The two-sample KS statistic at n = m is always a multiple of 1/n_stat, and `ks_2samp`'s p-value
    depends on the samples only through (n, m, D). Evaluating it on tie-free integer samples
    realising D = k/n_stat therefore tabulates the whole attainable null distribution with River's
    own call -- `method="auto"`, exactly as `kswin.py` invokes it -- rather than re-deriving it."""
    out = []
    for k in range(n_stat + 1):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            r = stats.ks_2samp(np.arange(n_stat), np.arange(n_stat) + k, method="auto")
        fell_back = any("asymp" in str(w.message) for w in caught)
        out.append((float(r.pvalue), "asymp" if fell_back else "exact"))
    return out


def requirement_lattice():
    """`eq:Rkswin` against River+scipy on the declared grid. Rule D1 of the gate."""
    margin = float(np.sqrt(ssot.S9_W_TRANSIENT_REF / 2.0 * np.log(1.0 / ssot.S9_EPS)))
    cells, guard_binds = [], []
    for n_stat in NSTAT_GRID:
        lat = _ks_lattice(n_stat)
        pv = np.array([p for p, _ in lat])
        floor = ssot.S9_KSWIN_ST_FLOOR * n_stat
        for alpha in ALPHAS:
            hit = np.flatnonzero(pv <= alpha)
            k_star = int(hit[0]) if hit.size else None
            asym = float(np.sqrt(n_stat * np.log(2.0 / alpha)))
            r_exact = None if k_star is None else float(max(k_star, floor))
            if k_star is not None and k_star <= floor:
                guard_binds.append((n_stat, alpha, k_star, floor))
            cells.append({
                "n_stat": n_stat, "alpha": alpha,
                "k_star": k_star, "R_fa_exact": None if k_star is None else float(k_star),
                "R_fa_asymptotic": round(asym, 4),
                "guard_floor_0p1_n_stat": floor,
                "R_exact": None if r_exact is None else round(r_exact, 4),
                "deviation_pct": None if r_exact is None else round(100.0 * (r_exact - asym) / asym, 2),
                "verdict_D1": None if r_exact is None else (
                    "CONFIRMED" if abs(asym - r_exact) <= 0.5
                    else "ANTI-CONSERVATIVE" if asym < r_exact else "CONSERVATIVE"),
                "scipy_method": lat[k_star][1] if k_star is not None else None,
                "R_KSWIN_at_W_ref": None if k_star is None else round(asym + margin, 4),
            })
    return {"grid": cells, "guard_binding_cells": guard_binds,
            "epsilon_margin": round(margin, 6),
            "margin_form": "sqrt(W/2 * ln(1/eps)), s2_arl0.py:387 and "
                           "s2bis_proteus_calibration.py:344",
            "W_used_for_margin": ssot.S9_W_TRANSIENT_REF, "eps": ssot.S9_EPS,
            "D1_tolerance": 0.5,
            "verdict_D1_overall": sorted({c["verdict_D1"] for c in cells if c["verdict_D1"]})}


def alarm_lattice(n_stat=N_STAT):
    """(k lattice p-values, minimum k the `st > 0.1` guard admits). Raises if the guard binds."""
    lat = _ks_lattice(n_stat)
    pv = np.array([p for p, _ in lat])
    k_guard = int(np.floor(ssot.S9_KSWIN_ST_FLOOR * n_stat)) + 1
    for alpha in ALPHAS:
        hit = np.flatnonzero(pv <= alpha)
        if hit.size and int(hit[0]) <= ssot.S9_KSWIN_ST_FLOOR * n_stat:
            raise SystemExit(f"[FATAL] the st > 0.1 guard binds at n_stat={n_stat}, alpha={alpha}: "
                             f"k* = {int(hit[0])} <= {ssot.S9_KSWIN_ST_FLOOR * n_stat}. The offline "
                             f"alarm derivation drops a conjunct and is invalid here.")
    return pv, k_guard


# ══════════════════════════════════════════════════════════════════════════════
# One cell
# ══════════════════════════════════════════════════════════════════════════════
def cell_seed(delta_e, arm, seed, input_arm):
    """SeedSequence-derived, order-independent, never the global state."""
    key = (ssot.S9_SEED_MASTER, int(round(delta_e * 1e6)), ARMS.index(arm), int(seed),
           INPUT_ARMS.index(input_arm))
    return int(np.random.SeedSequence(key).generate_state(1)[0])


def _input_stream(err, input_arm):
    """(values fed to the detector, index of the first fed step in `err`'s own indexing)."""
    if input_arm == "raw":
        return err, 0
    # R4 convention, run_concept_drift_kswin: a BUFFER-step moving average, the detector updated
    # only once the buffer is full. `valid` output j corresponds to err index j + BUFFER - 1.
    return np.convolve(err, np.ones(BUFFER) / BUFFER, mode="valid"), BUFFER - 1


def replay(err, t_rel, delta_e, arm, seed, input_arm, pv_lattice):
    """Run the three detectors over one cell. Returns (per-step arrays, per-run scalars)."""
    values, first = _input_stream(err, input_arm)
    n = err.size
    safe_seed, _ = common.lock_rng(cell_seed(delta_e, arm, seed, input_arm))

    pht = PHT(threshold=PHT_TRACE_THRESHOLD, delta=DELTA_P)
    adw = ADWINDetector(delta=ssot.S9_ADWIN_DELTA, clock=ssot.S9_ADWIN_CLOCK)
    ksw = KSWINDetector(alpha=KSWIN_TRACE_ALPHA, seed=safe_seed,
                        window_size=ssot.S9_KSWIN_WINDOW, stat_size=N_STAT)

    ps = np.full(n, np.nan, dtype=np.float32)
    am = np.full(n, np.nan, dtype=np.float32)
    aw = np.zeros(n, dtype=np.int32)
    aa = np.zeros(n, dtype=bool)
    kp = np.full(n, np.nan, dtype=np.float32)
    for j in range(first, n):
        x = float(values[j - first])
        pht.update(x)
        adw.update(x)
        ksw.update(x)
        ps[j] = pht.statistic()
        am[j] = adw.statistic()
        aw[j] = adw.width
        aa[j] = adw.drift_detected
        # `KSWIN._reset()` sets `p_value = 0` and River only ever reads it inside its own
        # `len(window) >= window_size` branch, so the attribute is 0 -- not 1 -- on every step
        # before the first test. Read unconditionally it would alarm at t = 0 at every alpha.
        # The precondition is River's, read off River's own state, not a tolerance.
        if len(ksw.detector.window) >= ssot.S9_KSWIN_WINDOW:
            kp[j] = ksw.statistic()

    # D = k / n_stat, recovered from River's own p-value against the tabulated null. Verified exact
    # for every k >= 2; the lattice saturates at p == 1 for k in {0, 1}, where this returns 1. The
    # 1/n_stat ambiguity is confined to D <= 1/30, where no alpha of the grid can fire.
    kk = np.where(np.isnan(kp), -1,
                  len(pv_lattice) - 1 - np.searchsorted(pv_lattice[::-1], kp, side="left"))
    kk = np.clip(kk, -1, N_STAT).astype(np.int8)

    def first_cross(mask):
        hit = np.flatnonzero(mask)
        return int(t_rel[hit[0]]) if hit.size else None

    scal = {"pht_peak": float(np.nanmax(ps)) if np.isfinite(ps).any() else None,
            "kswin_p_min": float(np.nanmin(kp)) if np.isfinite(kp).any() else None,
            "kswin_k_max": int(kk.max()),
            "adwin_n_alarms_pre": int(aa[t_rel < 0].sum()),
            "adwin_n_alarms_post": int(aa[t_rel >= 0].sum()),
            "adwin_t_first": first_cross(aa)}
    for lam in LAMBDAS:
        scal[f"pht_t_first_lambda{lam:g}"] = first_cross(ps > lam)
    for alpha in ALPHAS:
        scal[f"kswin_t_first_alpha{alpha:g}"] = first_cross(kp <= alpha)

    keep = t_rel >= -TRACE_PRE
    trace = {"arm": np.full(int(keep.sum()), arm), "input_arm": np.full(int(keep.sum()), input_arm),
             "seed": np.full(int(keep.sum()), seed, dtype=np.int64),
             "t_rel": t_rel[keep].astype(np.int32),
             "pht_stat": ps[keep], "adwin_mean": am[keep], "adwin_width": aw[keep],
             "adwin_alarm": aa[keep], "kswin_p": kp[keep], "kswin_k": kk[keep]}
    return trace, scal


# ══════════════════════════════════════════════════════════════════════════════
# One partition
# ══════════════════════════════════════════════════════════════════════════════
def partition(part, root, pv_lattice, seed_cap=None):
    delta_e = float(Path(part).name.split("=", 1)[1])
    df = ds.dataset(str(part), format="parquet").to_table(
        columns=["arm", "seed", "t_rel", "err"],
        filter=ds.field("arm").isin(ARMS) & (ds.field("t_rel") >= -WARMUP)
        & (ds.field("t_rel") < T_HORIZON)).to_pandas().sort_values(["arm", "seed", "t_rel"])

    traces, rows = [], []
    for arm, g_arm in df.groupby("arm", sort=False):
        seeds = sorted(g_arm["seed"].unique())[:seed_cap]
        for s in seeds:
            g = g_arm[g_arm.seed == s]
            err = g["err"].to_numpy(dtype=np.float64)
            t_rel = g["t_rel"].to_numpy()
            p0_hat = float(err[t_rel < 0].mean())
            for input_arm in INPUT_ARMS:
                tr, sc = replay(err, t_rel, delta_e, arm, int(s), input_arm, pv_lattice)
                traces.append(tr)
                rows.append({"delta_e": round(delta_e, 6), "arm": arm, "seed": int(s),
                             "input_arm": input_arm, "p0_hat": p0_hat, **sc})

    cols = {f.name: np.concatenate([t[f.name] for t in traces]) for f in TRACES_SCHEMA}
    table = writer._sorted_table(cols, TRACES_SCHEMA, ["arm", "input_arm", "seed", "t_rel"])
    writer._write(table, Path(root) / f"delta_e={PARTITION_FMT.format(delta_e)}" / "part-0.parquet")
    return rows


# ══════════════════════════════════════════════════════════════════════════════
# Aggregation
# ══════════════════════════════════════════════════════════════════════════════
def _quant(v, q):
    """Quantile over the finite entries. `w_fw` is NaN wherever tau_err(delta_P) is censored inside
    the horizon, and those runs must drop out of the quantile rather than poison it -- and rather
    than reach the JSON as a bare NaN, which is not valid JSON."""
    ok = np.asarray([x for x in v if x is not None], dtype=np.float64)
    ok = ok[np.isfinite(ok)]
    return None if ok.size == 0 else round(float(np.quantile(ok, q)), 2)


def summarise(rows, runs):
    """Per (delta_e, arm, input_arm, detector, threshold) detection reading, on the def:times W."""
    key = runs.set_index(["delta_e", "arm", "seed"])[["w_fw", "tau_erase", "a_fw",
                                                      "a_unrefl_peak", "e_pre"]]
    cells = {}
    for r in rows:
        idx = (round(r["delta_e"], 6), r["arm"], r["seed"])
        ctx = key.loc[idx] if idx in key.index else None
        w = float(ctx["w_fw"]) if ctx is not None else np.nan
        for det, thr, t in ([("PHT", lam, r[f"pht_t_first_lambda{lam:g}"]) for lam in LAMBDAS]
                            + [("KSWIN", a, r[f"kswin_t_first_alpha{a:g}"]) for a in ALPHAS]
                            + [("ADWIN", None, r["adwin_t_first"])]):
            c = cells.setdefault((r["delta_e"], r["arm"], r["input_arm"], det, thr),
                                 {"n": 0, "n_pre_alarm": 0, "n_detect_in_W": 0, "n_any_post": 0,
                                  "delays": [], "w": [], "a_fw": [], "ceiling": []})
            c["n"] += 1
            c["w"].append(w)
            if ctx is not None:
                c["a_fw"].append(float(ctx["a_fw"]))
                c["ceiling"].append(float(ctx["a_unrefl_peak"]))
            if t is None:
                continue
            if t < 0:
                c["n_pre_alarm"] += 1
                continue
            c["n_any_post"] += 1
            if np.isfinite(w) and t <= w:
                c["n_detect_in_W"] += 1
                c["delays"].append(t)

    out = []
    for (de, arm, ia, det, thr), c in sorted(cells.items(),
                                             key=lambda kv: (kv[0][0], kv[0][1], kv[0][2],
                                                             kv[0][3], -1 if kv[0][4] is None
                                                             else kv[0][4])):
        n_w = int(np.isfinite(np.asarray(c["w"], dtype=np.float64)).sum())
        out.append({
            "delta_e": round(de, 6), "arm": arm, "input_arm": ia, "detector": det,
            "threshold": thr, "n": c["n"], "n_with_finite_W": n_w,
            "pre_drift_alarm_rate": round(c["n_pre_alarm"] / c["n"], 4),
            "post_drift_alarm_rate": round(c["n_any_post"] / c["n"], 4),
            "detect_within_W_rate": None if n_w == 0 else round(c["n_detect_in_W"] / n_w, 4),
            "add_median": _quant(c["delays"], 0.5), "add_q95": _quant(c["delays"], 0.95),
            "w_median": _quant(c["w"], 0.5), "a_fw_median": _quant(c["a_fw"], 0.5),
            "ceiling_median": _quant(c["ceiling"], 0.5)})
    return out


def w_provenance(runs):
    """D0: which quantity is the `W = 57.4` every published requirement numeral is evaluated at?"""
    f = runs[(runs.arm == "full") & (np.isclose(runs.delta_e, ssot.S9_DELTA_E_REF))]
    swap = f["tau_swap_q010"].to_numpy(dtype=np.float64)
    w_fw = f["w_fw"].to_numpy(dtype=np.float64)
    w_fw = w_fw[np.isfinite(w_fw)]
    margin = lambda w: float(np.sqrt(w / 2.0 * np.log(1.0 / ssot.S9_EPS)))  # noqa: E731
    base = float(np.sqrt(N_STAT * np.log(2.0 / 0.005)))
    ceiling = float(np.median(f["a_unrefl_peak"].to_numpy(dtype=np.float64)))
    w_med = float(np.median(w_fw))
    return {
        "delta_e": ssot.S9_DELTA_E_REF, "arm": "full", "n": int(len(f)),
        "tau_swap_1_over_M_mean": round(float(np.mean(swap)), 3),
        "w_def_times_median": round(w_med, 3),
        "w_def_times_n_finite": int(w_fw.size),
        "W_published_in_requirements": ssot.S9_W_TRANSIENT_REF,
        "measured_ceiling_median_A_unrefl": round(ceiling, 4),
        "R_KSWIN_at_published_W": round(base + margin(ssot.S9_W_TRANSIENT_REF), 4),
        "R_KSWIN_at_def_times_W": round(base + margin(w_med), 4),
        "ceiling_meets_R_at_published_W": bool(ceiling >= base + margin(ssot.S9_W_TRANSIENT_REF)),
        "ceiling_meets_R_at_def_times_W": bool(ceiling >= base + margin(w_med)),
        "B2_cells_on_this_corpus": int((w_fw < N_STAT).sum()),
        "w_def_times_min_over_corpus": round(float(np.nanmin(
            runs.loc[runs.arm.isin(ARMS), "w_fw"].to_numpy(dtype=np.float64))), 1)}


# ══════════════════════════════════════════════════════════════════════════════
def main(which="data"):
    root_src = SOURCE_DIR / "data" / "traces.parquet"
    if not root_src.exists():
        raise SystemExit(f"[FATAL] {root_src} absent -- the S6 trace corpus is not reachable")
    pv_lattice, k_guard = alarm_lattice()
    seed_cap = ssot.S9_SMOKE_N_SEEDS if which == "smoke" else None
    parts = sorted(root_src.iterdir())
    if which == "smoke":
        # The smoke anchors are round numbers; the campaign grid is Phi(b/sqrt(2)) - 0.5 and holds
        # none of them exactly. Take the nearest partition to each, the same nearest-match rule
        # s6_recompute_cusum_delta001 applies to its four landmark magnitudes.
        grid = np.array([float(q.name.split("=", 1)[1]) for q in parts])
        parts = [parts[int(np.argmin(np.abs(grid - d)))] for d in ssot.S9_SMOKE_DELTA_E]

    suffix = "" if which == "data" else f"_{which}"
    data_dir, tab_dir = OUT_DIR / ("data" if which == "data" else which), OUT_DIR / "tables"
    tab_dir.mkdir(parents=True, exist_ok=True)
    root = writer.trace_root(data_dir, reset=True)

    print(f"=== S9 offline replay -- {len(parts)} magnitudes, arms {ARMS}, "
          f"input arms {INPUT_ARMS} ===")
    print(f"    window [tau* - {WARMUP}, tau* + {T_HORIZON}), stored from t_rel = -{TRACE_PRE}")
    print(f"    KSWIN(window={ssot.S9_KSWIN_WINDOW}, stat={N_STAT}) at alarm-disabled "
          f"alpha={KSWIN_TRACE_ALPHA:g}; st > {ssot.S9_KSWIN_ST_FLOOR} admits k >= {k_guard}")

    res = Parallel(n_jobs=-1)(delayed(partition)(p, root, pv_lattice, seed_cap) for p in parts)
    rows = [r for batch in res for r in batch]

    runs = pq.read_table(SOURCE_DIR / "data" / "runs.parquet").to_pandas()
    runs["delta_e"] = runs["delta_e"].round(6)
    summary = summarise(rows, runs)

    lattice = requirement_lattice()
    lat_path = tab_dir / f"s9_requirement_lattice{suffix}.json"
    lat_path.write_text(json.dumps(lattice, indent=2, sort_keys=True, default=float) + "\n",
                        encoding="utf-8")

    payload = {"source": str((SOURCE_DIR / "data" / "traces.parquet").relative_to(ssot.ROOT_DIR)),
               "which": which, "n_cells": len(rows), "arms": ARMS, "input_arms": INPUT_ARMS,
               "lambdas": LAMBDAS, "alphas": ALPHAS,
               "delta_p": DELTA_P, "adwin_delta": ssot.S9_ADWIN_DELTA,
               "adwin_clock": ssot.S9_ADWIN_CLOCK,
               "kswin": {"window_size": ssot.S9_KSWIN_WINDOW, "stat_size": N_STAT,
                         "buffer": BUFFER, "alarm_sense": "below"},
               "protocol": "First crossing only. Both alarm-disabled detectors are read up to "
                           "their first threshold crossing; R4 re-arms a monitor after every alarm "
                           "and scores pre-drift alarms as false positives, and that post-re-arm "
                           "behaviour is NOT reconstructed here. A cell whose "
                           "pre_drift_alarm_rate is 1.0 therefore carries no post-drift detection "
                           "reading, and its detect_within_W_rate of 0 means 'not measured by this "
                           "pass', not 'measured and negative'. ADWIN is exempt: it carries no "
                           "threshold, so its alarms are live and its counts are complete.",
               "W_provenance": w_provenance(runs),
               "env": common.env_stamp(), "cells": summary}
    sum_path = tab_dir / f"s9_offline_summary{suffix}.json"
    sum_path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=float) + "\n",
                        encoding="utf-8")

    wp = payload["W_provenance"]
    print(f"\n--- D0 / W provenance at Delta_e = {wp['delta_e']} ---")
    print(f"    tau_swap^(1/M) mean = {wp['tau_swap_1_over_M_mean']}  <-- the published "
          f"'W = {wp['W_published_in_requirements']}'")
    print(f"    def:times W median  = {wp['w_def_times_median']}  "
          f"({wp['w_def_times_n_finite']}/{wp['n']} finite)")
    print(f"    R_KSWIN  published W {wp['R_KSWIN_at_published_W']} (met: "
          f"{wp['ceiling_meets_R_at_published_W']})   def:times W "
          f"{wp['R_KSWIN_at_def_times_W']} (met: {wp['ceiling_meets_R_at_def_times_W']})"
          f"   ceiling {wp['measured_ceiling_median_A_unrefl']}")
    print(f"    branch B2 cells (W < n_stat) on this corpus: {wp['B2_cells_on_this_corpus']}"
          f"   min W = {wp['w_def_times_min_over_corpus']}")

    print(f"\n--- D1 / requirement lattice --- verdicts {lattice['verdict_D1_overall']}, "
          f"guard binds at {len(lattice['guard_binding_cells'])} cells")
    for c in lattice["grid"]:
        if c["n_stat"] == N_STAT:
            print(f"    n_stat={c['n_stat']} alpha={c['alpha']:<6} k*={c['k_star']:>3} "
                  f"exact={c['R_exact']:>6} asym={c['R_fa_asymptotic']:>6} "
                  f"{c['deviation_pct']:>+6.2f}%  {c['verdict_D1']} [{c['scipy_method']}]")

    print(f"\n[INFO] wrote {root.relative_to(ssot.ROOT_DIR)} ({len(parts)} partitions)")
    print(f"[INFO] wrote {sum_path.relative_to(ssot.ROOT_DIR)} ({len(summary)} cells)")
    print(f"[INFO] wrote {lat_path.relative_to(ssot.ROOT_DIR)} "
          f"({len(lattice['grid'])} lattice cells)")
    return payload


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data")
