"""Step-by-step harness of stream S6: synchronized trajectories and the causal fork.

One simulation per (seed, Delta_e) produces three of the four arms. The stream is materialised once
from the locked generator, so 'full' and its two counterfactual branches see a byte-identical input
suffix; the branches are `copy.deepcopy` forks taken at tau_swap^(1/M), the instant of the first
post-drift replacement, which gate G1 certified as state-equivalent and memory-disjoint. 'static' is
a separate model class and is simulated independently on that same stream.

  full     nominal ARF.
  no_swap  fork at tau_swap^(1/M), both internal detector paths made inert. Learning continues, no
           further replacement fires. Isolates the Hydra -- the repeated swaps after the first.
  frozen   same fork, learn_one no longer called. The ensemble stops moving entirely.
  static   the non-adaptive reference of R3: BaggingClassifier over HoeffdingTreeClassifier, which
           learns but never resets a tree.

The forks are taken AFTER the learn_one that produced the first replacement, so both branches carry
that one swap and neither takes another: 'no_swap' has zero ADDITIONAL swap, which is the invariant
`tests/test_S6_traces.py` asserts. The traced prefix of a branch is the prefix of 'full' -- it is
the same trajectory -- and `fork_t_rel` marks where they part.

Stream construction. `rng.normal(size=(n, 2))` fills row-major and is bit-identical to 2n sequential
scalar `rng.normal()` calls, so materialising the stream preserves the two-draws-per-step invariant
the canonical family is built on. Verified, not assumed: see the demo at the bottom.

Cumulative columns are derived in one numpy pass after the loop rather than accumulated inside it.
That is what makes `a_refl >= a_unrefl` hold by construction at every step instead of by care.
"""
import copy
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from joblib import Parallel, delayed
from river import ensemble, tree
from tqdm import tqdm

import s6_defs as defs
import s6_writer as writer

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "S6_synchronized_traces" / "gates"))
import _gate_common as common  # noqa: E402
from _gate_common import ssot  # noqa: E402

N_STEPS = ssot.S6_N_STEPS
T_DRIFT = ssot.S6_T_DRIFT
N_MODELS = ssot.S6_N_MODELS
C_INT = ssot.S6_C_INT
WARMUP = ssot.S6_WARMUP_WINDOW
TRACE_PRE = ssot.S6_TRACE_PRE
TRACE_POST = ssot.S6_TRACE_POST
T_HORIZON = ssot.S6_T_HORIZON
Q_GRID = ssot.S6_Q_GRID
RHO_GRID = ssot.S6_RHO_GRID
ARM_NAMES = ssot.S6_ARM_NAMES
RESULTS_DIR = ssot.RESULTS_DIR / "S6_synchronized_traces"


def make_stream(seed, delta_e):
    """(safe_seed, X, y) under the triple lock. y flips boundary at T_DRIFT."""
    safe_seed, rng = common.lock_rng(seed)
    x = rng.normal(size=(N_STEPS, 2))
    b = np.concatenate([np.zeros(T_DRIFT), np.full(N_STEPS - T_DRIFT, common.boundary_shift(delta_e))])
    return safe_seed, x, (x.sum(axis=1) > b).astype(np.int8)


def make_static(safe_seed):
    """R3's non-adaptive ensemble: bagging over Hoeffding trees, no internal reset."""
    return ensemble.BaggingClassifier(model=tree.HoeffdingTreeClassifier(),
                                      n_models=N_MODELS, seed=safe_seed)


def _forest_shape(model):
    """(mean nodes, mean active leaves) over the ensemble.

    River returns None for both on a tree whose root has not been created yet -- the state every
    tree is in at t=0 and, per gate G2, the state every REPLACEMENT tree is in, since the blind-spot
    configuration promotes a background tree created in the same step. That None is the physical
    zero of the reconstruction curve, so it is read as 0 and not skipped."""
    nodes = leaves = 0
    for t in model.data:
        nodes += t.n_nodes or 0
        leaves += t.n_active_leaves or 0
    return nodes / N_MODELS, leaves / N_MODELS


def segment(model, x, y, lo, hi, learn=True, observe=True, track=True, stop_on_new_tree=False):
    """Run steps [lo, hi). Returns per-step arrays and the absolute step at which it stopped.

    `track` reads the per-tree replacement counters and diffs their KEYS; it is off for the static
    arm, which has no `_drift_tracker`. `stop_on_new_tree` returns as soon as a tree is replaced for
    the first time in this segment -- that step is tau_swap^(1/M) and the fork point."""
    n = hi - lo
    err = np.zeros(n, dtype=np.int8)
    swap_delta = np.zeros(n, dtype=np.int32)
    replaced = [frozenset()] * n
    nodes = np.zeros(n, dtype=np.float32)
    leaves = np.zeros(n, dtype=np.float32)
    prev = common.tracker_vector(model._drift_tracker, N_MODELS) if track else None
    stopped, seen = hi, set()

    for k in range(n):
        t = lo + k
        x_dict = {0: x[t, 0], 1: x[t, 1]}
        y_pred = model.predict_one(x_dict)
        err[k] = int((y_pred if y_pred is not None else 0) != y[t])
        if learn:
            model.learn_one(x_dict, int(y[t]))
        if track:
            now = common.tracker_vector(model._drift_tracker, N_MODELS)
            swap_delta[k] = sum(now) - sum(prev)
            replaced[k] = frozenset(i for i in range(N_MODELS) if now[i] > prev[i])
            prev = now
        if observe:
            nodes[k], leaves[k] = _forest_shape(model)
        if stop_on_new_tree and (replaced[k] - seen):
            stopped = t + 1
            n = k + 1
            err, swap_delta, nodes, leaves = err[:n], swap_delta[:n], nodes[:n], leaves[:n]
            replaced = replaced[:n]
            break
        seen |= replaced[k]

    return {"err": err, "swap_delta": swap_delta, "replaced": replaced,
            "n_nodes_mean": nodes, "n_active_leaves_mean": leaves}, stopped


def _concat(*segs):
    out = {k: np.concatenate([s[k] for s in segs]) for k in
           ("err", "swap_delta", "n_nodes_mean", "n_active_leaves_mean")}
    out["replaced"] = [r for s in segs for r in s["replaced"]]
    return out


def _metrics(seed, delta_e, arm, post, err_pre, pre_swaps, fork_t_rel, n_nodes_at_drift):
    """One runs.parquet record plus the derived trace columns, from the raw post-drift segment."""
    err_post = post["err"].astype(np.float64)
    e_pre, delta_e_emp = defs.empirical_delta_e(err_pre, err_post)
    trees_cum = defs.distinct_trees_cum(post["replaced"])
    a_unrefl, a_refl = defs.accumulations(err_post, e_pre)
    tau_star = defs.tau_swap(trees_cum, N_MODELS, 1.0 / N_MODELS)
    t_erase = defs.tau_erase(a_unrefl, tau_star)
    a, a_rect = defs.error_budget(err_post, e_pre, delta_e_emp, tau_star)
    horizon = min(int(T_HORIZON), err_post.size) - 1

    record = {
        "seed": int(seed), "delta_e": float(delta_e), "arm": arm,
        "n_models": int(N_MODELS), "clock": int(C_INT),
        "fork_taken": fork_t_rel is not None,
        "fork_t_rel": float(fork_t_rel) if fork_t_rel is not None else np.nan,
        "e_pre": e_pre, "delta_e_emp": delta_e_emp,
        "n_trees_swapped_pre_drift": int(pre_swaps),
        "swaps_total": int(post["swap_delta"].sum()),
        "trees_swapped_total": int(trees_cum[-1]) if trees_cum.size else 0,
        "tau_erase": t_erase, "a": a, "a_rect": a_rect,
        "a_refl": float(a_refl[horizon]), "a_unrefl_peak": float(a_unrefl.max()),
        "n_nodes_mean_at_drift": float(n_nodes_at_drift),
        "n_nodes_mean_at_horizon": float(post["n_nodes_mean"][horizon]),
        "n_active_leaves_mean_at_horizon": float(post["n_active_leaves_mean"][horizon]),
        "err_post_mean": float(err_post[:horizon + 1].mean()),
    }
    for q in Q_GRID:
        record[writer.tau_swap_col(q)] = defs.tau_swap(trees_cum, N_MODELS, q)
    for rho in RHO_GRID:
        record[writer.tau_err_col(rho)] = defs.tau_err(err_post, e_pre, delta_e_emp, rho)
    return record, {"trees_cum": trees_cum, "a_unrefl": a_unrefl, "a_refl": a_refl}


def _frame(seed, delta_e, arm, pre, post, derived):
    """One traces.parquet frame: [t_drift - TRACE_PRE, t_drift + TRACE_POST)."""
    n_post = min(TRACE_POST, post["err"].size)
    err = np.concatenate([pre["err"][-TRACE_PRE:], post["err"][:n_post]])
    n = err.size
    swaps = np.concatenate([pre["swap_delta"][-TRACE_PRE:], post["swap_delta"][:n_post]])
    trees = np.concatenate([np.zeros(n - n_post, dtype=np.int32), derived["trees_cum"][:n_post]])
    zeros = np.zeros(n - n_post)
    return {
        "delta_e": float(delta_e), "arm": np.full(n, arm), "seed": np.full(n, seed, dtype=np.int64),
        "t_rel": np.arange(-(n - n_post), n_post, dtype=np.int32),
        "err": err.astype(np.int8), "err_cum": np.cumsum(err).astype(np.int32),
        "swaps_cum": np.cumsum(swaps).astype(np.int32),
        "trees_swapped_cum": trees.astype(np.int16),
        "a_unrefl": np.concatenate([zeros, derived["a_unrefl"][:n_post]]),
        "a_refl": np.concatenate([zeros, derived["a_refl"][:n_post]]),
        "n_nodes_mean": np.concatenate([pre["n_nodes_mean"][-TRACE_PRE:],
                                        post["n_nodes_mean"][:n_post]]).astype(np.float32),
        "n_active_leaves_mean": np.concatenate([pre["n_active_leaves_mean"][-TRACE_PRE:],
                                                post["n_active_leaves_mean"][:n_post]]).astype(np.float32),
    }


def simulate(seed, delta_e):
    """One (seed, Delta_e) cell -> (records, frames) for the four arms."""
    safe_seed, x, y = make_stream(seed, delta_e)
    records, frames = [], []

    # --- adaptive trunk: warm-up, then the post-drift run up to the first replacement ------------
    arf = common.make_arf(safe_seed, N_MODELS, C_INT)
    segment(arf, x, y, 0, T_DRIFT - TRACE_PRE, observe=False, track=False)
    pre, _ = segment(arf, x, y, T_DRIFT - TRACE_PRE, T_DRIFT)
    pre_swaps = len(arf._drift_tracker)
    nodes_at_drift = _forest_shape(arf)[0]

    head, fork_abs = segment(arf, x, y, T_DRIFT, N_STEPS, stop_on_new_tree=True)
    fork_taken = fork_abs < N_STEPS
    branch_src = copy.deepcopy(arf) if fork_taken else None
    fork_t_rel = fork_abs - 1 - T_DRIFT if fork_taken else None

    tail, _ = segment(arf, x, y, fork_abs, N_STEPS) if fork_taken else (None, None)
    full_post = _concat(head, tail) if fork_taken else head

    for arm, post in (("full", full_post),):
        rec, der = _metrics(seed, delta_e, arm, post, pre["err"], pre_swaps, fork_t_rel, nodes_at_drift)
        records.append(rec)
        frames.append(_frame(seed, delta_e, arm, pre, post, der))

    # --- counterfactual branches ------------------------------------------------------------------
    for arm in ("no_swap", "frozen"):
        if not fork_taken:
            rec = {**records[0], "arm": arm, "fork_taken": False, "fork_t_rel": np.nan}
            rec.update({k: np.nan for k in rec if k.startswith(("tau_", "a", "e_", "delta_e_emp",
                                                                "err_post", "n_nodes", "n_active"))})
            rec["delta_e"], rec["swaps_total"], rec["trees_swapped_total"] = float(delta_e), 0, 0
            records.append(rec)
            continue
        branch = copy.deepcopy(branch_src)
        if arm == "no_swap":
            branch._drift_detection_disabled = True
            branch._warning_detection_disabled = True
            seg, _ = segment(branch, x, y, fork_abs, N_STEPS)
        else:
            seg, _ = segment(branch, x, y, fork_abs, N_STEPS, learn=False)
        post = _concat(head, seg)
        rec, der = _metrics(seed, delta_e, arm, post, pre["err"], pre_swaps, fork_t_rel, nodes_at_drift)
        records.append(rec)
        frames.append(_frame(seed, delta_e, arm, pre, post, der))

    # --- static reference: independent model class on the same stream -----------------------------
    stat = make_static(safe_seed)
    segment(stat, x, y, 0, T_DRIFT - TRACE_PRE, observe=False, track=False)
    s_pre, _ = segment(stat, x, y, T_DRIFT - TRACE_PRE, T_DRIFT, track=False)
    s_post, _ = segment(stat, x, y, T_DRIFT, N_STEPS, track=False)
    rec, der = _metrics(seed, delta_e, "static", s_post, s_pre["err"], 0, None,
                        _forest_shape(stat)[0])
    records.append(rec)
    frames.append(_frame(seed, delta_e, "static", s_pre, s_post, der))

    return records, frames


def campaign(seeds, delta_e_grid, out_dir, n_jobs=-1, desc="S6"):
    grid = [(s, de) for de in delta_e_grid for s in seeds]
    t0 = time.perf_counter()
    out = Parallel(n_jobs=n_jobs)(delayed(simulate)(s, de) for s, de in tqdm(grid, desc=desc))
    records = [r for recs, _ in out for r in recs]
    frames = [f for _, frs in out for f in frs]
    runs_path = writer.write_runs(records, out_dir)
    traces_path, parts = writer.write_traces(frames, out_dir)
    return {"cells": len(grid), "records": len(records), "frames": len(frames),
            "trace_rows": sum(f["t_rel"].size for f in frames),
            "runs_path": runs_path, "traces_path": traces_path, "parts": parts,
            "wall_clock_s": time.perf_counter() - t0}


def demo():
    """Self-check: the materialised stream equals the scalar-draw convention, and one cell obeys
    the four arm invariants."""
    _, x, _ = make_stream(1, 0.25)
    _, rng = common.lock_rng(1)
    ref = np.array([[rng.normal(), rng.normal()] for _ in range(64)])
    assert np.array_equal(x[:64], ref), "materialised stream broke the two-draws-per-step convention"

    records, frames = simulate(common.seed_pool(1)[0], 0.40)
    by_arm = {r["arm"]: r for r in records}
    assert set(by_arm) == set(ARM_NAMES), sorted(by_arm)
    assert by_arm["full"]["swaps_total"] >= by_arm["no_swap"]["swaps_total"]
    assert by_arm["no_swap"]["swaps_total"] == by_arm["frozen"]["swaps_total"] == 1
    assert by_arm["static"]["swaps_total"] == 0
    for f in frames:
        assert np.all(np.diff(f["err_cum"]) >= 0) and np.all(np.diff(f["swaps_cum"]) >= 0)
        assert np.all(f["a_refl"] >= f["a_unrefl"] - 1e-9)
    print("s6_runner demo: OK  " + ", ".join(
        f"{a}: swaps={by_arm[a]['swaps_total']} trees={by_arm[a]['trees_swapped_total']}"
        for a in ARM_NAMES))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        demo()
        sys.exit(0)
    smoke = len(sys.argv) > 1 and sys.argv[1] == "smoke"
    seeds = common.seed_pool(ssot.S6_SMOKE_N_SEEDS if smoke else len(ssot.S6_CAMPAIGN_SEEDS))
    grid = ssot.S6_SMOKE_DELTA_E if smoke else [
        float(np.round(common.norm.cdf(b / np.sqrt(2)) - 0.5, 6)) for b in ssot.S6_CAMPAIGN_BOUNDARY_SHIFTS]
    out = RESULTS_DIR / ("smoke" if smoke else "data")
    print(f"[INFO] S6 {'smoke' if smoke else 'FULL'} campaign: {len(seeds)} seeds x {len(grid)} "
          f"magnitudes x {len(ARM_NAMES)} arms -> {out.relative_to(ssot.ROOT_DIR)}")
    summary = campaign(seeds, grid, out, desc="S6 smoke" if smoke else "S6 campaign")
    print(f"[INFO] {summary['records']} run records, {summary['frames']} traces, "
          f"{summary['trace_rows']:,} trace rows in {summary['wall_clock_s']:.1f}s")
