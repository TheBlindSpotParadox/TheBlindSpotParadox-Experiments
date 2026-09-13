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

Stream S8 adds two arms forked at tau* instead, requested by `arms` and off by default so the S6
corpus and its frozen contract are untouched:

  no_swap_ab_initio  fork at tau* -- the drift instant, BEFORE the first replacement -- both internal
                     detector paths inert. Learning continues, no tree is EVER replaced.
  frozen_ab_initio   same fork, learn_one no longer called. The single reference anchored at tau*.

The S6 forks are taken AFTER the learn_one that produced the first replacement, so both branches
carry that one swap and neither takes another: 'no_swap' has zero ADDITIONAL swap, which is the
invariant `tests/test_S6_traces.py` asserts. The traced prefix of a branch is the prefix of 'full'
-- it is the same trajectory -- and `fork_t_rel` marks where they part. That fork point is ENDOGENOUS
(it depends on the arm), which is why the ab initio branches exist: tau* is exogenous, fixed by the
protocol, so the four arms become a decomposition anchored on one common reference.

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
AB_INITIO_ARMS = ssot.S8_AB_INITIO_ARMS
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


def _first_increment_per_tree(replaced_per_step, n_models=N_MODELS):
    """[tau_i] -- the post-drift step at which tree i was replaced for the FIRST time, NaN if never.

    `transfer_S3.md` section 6 open item 1 declares that no committed artifact carries the per-tree
    tau_i of the ARF, only the four order statistics tau_swap^(q). The information is already in
    `segment`'s per-key tracker diff; this persists it. Order statistics of this vector recover
    tau_swap^(q) exactly, so the two are checkable against each other."""
    tau = np.full(n_models, np.nan)
    for t, replaced in enumerate(replaced_per_step):
        for i in replaced:
            if np.isnan(tau[i]):
                tau[i] = float(t)
    return tau


def _metrics(seed, delta_e, arm, post, err_pre, pre_swaps, fork_t_rel, n_nodes_at_drift):
    """One runs.parquet record plus the derived trace columns, from the raw post-drift segment.

    `per_tree_tau` rides on the record but is NOT a RUNS_SCHEMA field -- `s6_writer.write_runs`
    projects onto the schema and drops it, so the frozen Parquet contract is unchanged and the
    vector is available to whichever campaign pilot wants to persist it."""
    err_post = post["err"].astype(np.float64)
    e_pre, delta_e_emp = defs.empirical_delta_e(err_pre, err_post)
    trees_cum = defs.distinct_trees_cum(post["replaced"])
    a_unrefl, a_refl = defs.accumulations(err_post, e_pre)
    tau_star = defs.tau_swap(trees_cum, N_MODELS, 1.0 / N_MODELS)
    t_erase = defs.tau_erase(a_unrefl, tau_star)
    a, a_rect = defs.error_budget(err_post, e_pre, delta_e_emp, tau_star)
    t_erase_fw = defs.tau_err_framework(err_post, e_pre, defs.DELTA_P)
    a_fw, a_rect_fw = defs.budget_framework(err_post, e_pre, t_erase_fw, delta_e_emp)
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
        "tau_erase_fw": t_erase_fw, "w_fw": t_erase_fw, "a_fw": a_fw, "a_rect_fw": a_rect_fw,
        "kappa": defs.kappa(t_erase_fw, tau_star),
        "n_nodes_mean_at_drift": float(n_nodes_at_drift),
        "n_nodes_mean_at_horizon": float(post["n_nodes_mean"][horizon]),
        "n_active_leaves_mean_at_horizon": float(post["n_active_leaves_mean"][horizon]),
        "err_post_mean": float(err_post[:horizon + 1].mean()),
        "per_tree_tau": _first_increment_per_tree(post["replaced"]),
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


def simulate(seed, delta_e, arms=ARM_NAMES, stream_fn=make_stream):
    """One (seed, Delta_e) cell -> (records, frames) for the requested arms.

    'full' is always simulated: it is the trunk the two forks are taken from and the only arm that
    locates tau_swap^(1/M). Restricting `arms` to ('full',) skips the two branch replays and the
    independent static run, which is what the refinement sweep wants -- Delta_e_c is a property of
    the nominal arm and the counterfactuals would triple its cost for nothing.

    `stream_fn(seed, delta_e) -> (safe_seed, X, y)` is the generator. The default is the canonical
    boundary-shift family; stream S8 injects the rotation family through the same signature, which
    is what makes the two comparable seed by seed rather than only in distribution."""
    safe_seed, x, y = stream_fn(seed, delta_e)
    records, frames = [], []

    # --- adaptive trunk: warm-up, then the post-drift run up to the first replacement ------------
    arf = common.make_arf(safe_seed, N_MODELS, C_INT)
    segment(arf, x, y, 0, T_DRIFT - TRACE_PRE, observe=False, track=False)
    pre, _ = segment(arf, x, y, T_DRIFT - TRACE_PRE, T_DRIFT)
    pre_swaps = len(arf._drift_tracker)
    nodes_at_drift = _forest_shape(arf)[0]

    # Taken BEFORE the head segment, hence at tau* and before any post-drift replacement. `deepcopy`
    # reads state and consumes no entropy, so the trunk below stays bit-identical whether or not the
    # ab initio arms are requested -- which the S8 trunk acceptance gate verifies on runs.parquet.
    drift_src = copy.deepcopy(arf) if set(AB_INITIO_ARMS) & set(arms) else None

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
    for arm in [a for a in ("no_swap", "frozen") if a in arms]:
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

    # --- ab initio branches: forked at tau*, before any post-drift replacement ---------------------
    # The post segment is the WHOLE [T_DRIFT, N_STEPS) window, with no `_concat(head, ...)`: these
    # branches share no post-drift prefix with 'full'. That absence of a shared prefix is exactly
    # what identifies the effect of the first replacement. `fork_t_rel = 0.0` marks the fork at tau*.
    for arm in [a for a in AB_INITIO_ARMS if a in arms]:
        branch = copy.deepcopy(drift_src)
        branch._drift_detection_disabled = True
        branch._warning_detection_disabled = True
        seg, _ = segment(branch, x, y, T_DRIFT, N_STEPS, learn=(arm == "no_swap_ab_initio"))
        rec, der = _metrics(seed, delta_e, arm, seg, pre["err"], pre_swaps, 0.0, nodes_at_drift)
        records.append(rec)
        frames.append(_frame(seed, delta_e, arm, pre, seg, der))

    # --- static reference: independent model class on the same stream -----------------------------
    if "static" not in arms:
        return records, frames
    stat = make_static(safe_seed)
    segment(stat, x, y, 0, T_DRIFT - TRACE_PRE, observe=False, track=False)
    s_pre, _ = segment(stat, x, y, T_DRIFT - TRACE_PRE, T_DRIFT, track=False)
    s_post, _ = segment(stat, x, y, T_DRIFT, N_STEPS, track=False)
    rec, der = _metrics(seed, delta_e, "static", s_post, s_pre["err"], 0, None,
                        _forest_shape(stat)[0])
    records.append(rec)
    frames.append(_frame(seed, delta_e, "static", s_pre, s_post, der))

    return records, frames


def campaign(seeds, delta_e_grid, out_dir, n_jobs=-1, desc="S6", arms=ARM_NAMES,
             stream_fn=make_stream):
    """Simulate the grid one magnitude at a time, writing each trace partition before the next.

    The full grid is 100 x 20 x 4 arms x 5000 traced steps = 40 million rows; holding them all in
    the parent to write once at the end costs several GB for no benefit, and the hive layout is one
    file per magnitude anyway. Records are small and are written once at the end, sorted, and are
    also returned under `record_rows` so a pilot can persist the off-schema columns (`per_tree_tau`)
    without a second pass over the corpus."""
    t0 = time.perf_counter()
    root = writer.trace_root(out_dir, reset=True)
    records, rows, parts = [], 0, []
    bar = tqdm(delta_e_grid, desc=desc)
    for de in bar:
        out = Parallel(n_jobs=n_jobs)(delayed(simulate)(s, de, arms, stream_fn) for s in seeds)
        frames = [f for _, frs in out for f in frs]
        records += [r for recs, _ in out for r in recs]
        rows += sum(f["t_rel"].size for f in frames)
        parts.append(writer.write_trace_partition(frames, root, de))
        bar.set_postfix(rows=f"{rows:,}")
        del out, frames
    return {"cells": len(seeds) * len(delta_e_grid), "records": len(records),
            "frames": len(parts), "trace_rows": rows,
            "runs_path": writer.write_runs(records, out_dir), "traces_path": root, "parts": parts,
            "record_rows": records, "wall_clock_s": time.perf_counter() - t0}


def demo():
    """Self-check: the materialised stream equals the scalar-draw convention, and one cell obeys
    the four arm invariants."""
    _, x, _ = make_stream(1, 0.25)
    _, rng = common.lock_rng(1)
    ref = np.array([[rng.normal(), rng.normal()] for _ in range(64)])
    assert np.array_equal(x[:64], ref), "materialised stream broke the two-draws-per-step convention"

    seed = common.seed_pool(1)[0]
    records, frames = simulate(seed, 0.40)
    by_arm = {r["arm"]: r for r in records}
    assert set(by_arm) == set(ARM_NAMES), sorted(by_arm)
    assert by_arm["full"]["swaps_total"] >= by_arm["no_swap"]["swaps_total"]
    assert by_arm["no_swap"]["swaps_total"] == by_arm["frozen"]["swaps_total"] == 1
    assert by_arm["static"]["swaps_total"] == 0
    for f in frames:
        assert np.all(np.diff(f["err_cum"]) >= 0) and np.all(np.diff(f["swaps_cum"]) >= 0)
        assert np.all(f["a_refl"] >= f["a_unrefl"] - 1e-9)

    # tau_swap^(q) is the q-th order statistic of the per-tree vector, by definition of both.
    swapped = np.sort(by_arm["full"]["per_tree_tau"])
    k = int(np.ceil(Q_GRID[0] * N_MODELS))
    assert np.isnan(by_arm["full"][writer.tau_swap_col(Q_GRID[0])]) == np.isnan(swapped[k - 1]) and (
        np.isnan(swapped[k - 1]) or swapped[k - 1] == by_arm["full"][writer.tau_swap_col(Q_GRID[0])]), \
        "per-tree tau vector disagrees with the published order statistic"

    # S8 arms: the intervention is proved by two invariants, not by the arm name.
    s8, s8_frames = simulate(seed, 0.40, arms=ssot.S8_ARM_NAMES)
    by_s8 = {r["arm"]: r for r in s8}
    assert set(by_s8) == set(ssot.S8_ARM_NAMES), sorted(by_s8)
    for arm in AB_INITIO_ARMS:
        assert by_s8[arm]["swaps_total"] == 0, (arm, by_s8[arm]["swaps_total"])
        assert by_s8[arm]["trees_swapped_total"] == 0, arm
        assert by_s8[arm]["fork_t_rel"] == 0.0, arm
        assert np.all(np.isnan(by_s8[arm]["per_tree_tau"])), arm
    # the trunk is unperturbed by the extra deepcopy: same record, arm by arm
    for arm in ("full", "no_swap", "frozen"):
        assert by_s8[arm]["a_unrefl_peak"] == by_arm[arm]["a_unrefl_peak"], arm
        assert by_s8[arm]["e_pre"] == by_arm[arm]["e_pre"], arm
    frozen_ab = [f for f in s8_frames if f["arm"][0] == "frozen_ab_initio"][0]
    post = frozen_ab["t_rel"] >= 0
    assert (frozen_ab["n_nodes_mean"][post] == frozen_ab["n_nodes_mean"][post][0]).all(), \
        "frozen_ab_initio forest moved after tau*"

    print("s6_runner demo: OK  " + ", ".join(
        f"{a}: swaps={by_s8[a]['swaps_total']} trees={by_s8[a]['trees_swapped_total']}"
        for a in ssot.S8_ARM_NAMES) + f", static: swaps={by_arm['static']['swaps_total']}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        demo()
        sys.exit(0)
    mode = sys.argv[1] if len(sys.argv) > 1 else "full"
    if mode == "smoke":
        seeds, grid, arms = common.seed_pool(ssot.S6_SMOKE_N_SEEDS), ssot.S6_SMOKE_DELTA_E, ARM_NAMES
    elif mode == "refine":
        seeds = common.seed_pool(ssot.S6_REFINE_N_SEEDS)
        grid, arms = ssot.S6_REFINE_DELTA_E, ssot.S6_REFINE_ARMS
    elif mode == "full":
        seeds = common.seed_pool(len(ssot.S6_CAMPAIGN_SEEDS))
        grid = [float(np.round(common.norm.cdf(b / np.sqrt(2)) - 0.5, 6))
                for b in ssot.S6_CAMPAIGN_BOUNDARY_SHIFTS]
        arms = ARM_NAMES
    else:
        raise SystemExit(f"usage: s6_runner.py [full|smoke|refine|demo]  (got {mode!r})")
    out = RESULTS_DIR / {"smoke": "smoke", "refine": "data_refine", "full": "data"}[mode]
    print(f"[INFO] S6 {mode} campaign: {len(seeds)} seeds x {len(grid)} magnitudes x "
          f"{len(arms)} arm(s) {list(arms)} -> {out.relative_to(ssot.ROOT_DIR)}")
    summary = campaign(seeds, grid, out, desc=f"S6 {mode}", arms=arms)
    print(f"[INFO] {summary['records']} run records, {summary['frames']} traces, "
          f"{summary['trace_rows']:,} trace rows in {summary['wall_clock_s']:.1f}s")
