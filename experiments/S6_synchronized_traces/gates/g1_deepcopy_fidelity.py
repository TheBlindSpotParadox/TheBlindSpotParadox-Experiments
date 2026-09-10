"""Gate G1 -- fidelity of a copy.deepcopy() fork of an ARF (prerequisite of the causal test).

The S6 causal test forks the ensemble mid-trajectory and runs two branches on one identical input
suffix. That is sound only if `copy.deepcopy` yields a state-equivalent but fully disjoint object:
equivalent, or the branches are not comparable; disjoint, or the counterfactual branch contaminates
the factual one.

Design. Same grid as G0 (50 seeds x three magnitudes). Each run advances to t_rel = +100 post-drift,
materialises the next 500 steps of the stream ONCE, takes the deepcopy, then replays that identical
suffix on the original and on the fork. Three families of assertion:

  1. Equivalence -- per-step prequential error sequence (500 values), per-step ensemble prediction,
     final per-tree drift and warning counters, final forest generator state.
  2. Disjunction -- `fork._rng is not orig._rng`, `fork.data[i] is not orig.data[i]`, and no shared
     `_drift_detectors` / `_warning_detectors` / `_background` element.
  3. Internal aliasing preserved -- River threads the forest generator into every tree
     (`tree.rng is forest._rng`); a fork that broke that memo would draw from the parent's stream.

The branches are replayed sequentially, original first. That is the Phase-1 ordering, and it also
exposes any River path that reaches for the global generators instead of `_rng`: such a path would
desynchronise the second branch and fail (1).
"""
import copy
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from joblib import Parallel, delayed
from tqdm import tqdm

import _gate_common as common
from _gate_common import ssot

N_STEPS = ssot.S6_N_STEPS
T_DRIFT = ssot.S6_T_DRIFT
N_MODELS = ssot.S6_N_MODELS
C_INT = ssot.S6_C_INT
N_SEEDS = ssot.S6_GATE_N_SEEDS
DELTA_E_GRID = ssot.S6_GATE_DELTA_E
FORK_T_REL = ssot.S6_G1_FORK_T_REL
FORK_HORIZON = ssot.S6_G1_FORK_HORIZON


def replay(arf, suffix):
    """Feed an identical (x, y) suffix; return the prequential error and prediction sequences."""
    errors, preds = [], []
    for x_dict, y in suffix:
        y_pred = arf.predict_one(x_dict)
        preds.append(y_pred)
        errors.append(float((y_pred if y_pred is not None else 0) != y))
        arf.learn_one(x_dict, y)
    return tuple(errors), tuple(preds)


def fork_run(seed, delta_e):
    safe_seed, rng = common.lock_rng(seed)
    arf = common.make_arf(safe_seed, N_MODELS, C_INT)
    b_shift = common.boundary_shift(delta_e)

    for t in range(T_DRIFT + FORK_T_REL):
        x0, x1 = rng.normal(), rng.normal()
        x_dict = {0: x0, 1: x1}
        arf.predict_one(x_dict)
        arf.learn_one(x_dict, int(x0 + x1 > (0.0 if t < T_DRIFT else b_shift)))

    suffix = []
    for _ in range(FORK_HORIZON):
        x0, x1 = rng.normal(), rng.normal()
        suffix.append(({0: x0, 1: x1}, int(x0 + x1 > b_shift)))

    fork = copy.deepcopy(arf)
    disjoint = {
        "rng_object": fork._rng is not arf._rng,
        "trees": all(fork.data[i] is not arf.data[i] for i in range(N_MODELS)),
        "drift_detectors": all(fork._drift_detectors[i] is not arf._drift_detectors[i]
                               for i in range(N_MODELS)),
        "warning_detectors": all(fork._warning_detectors[i] is not arf._warning_detectors[i]
                                 for i in range(N_MODELS)),
        "background": all(fork._background[i] is not arf._background[i]
                          for i in range(N_MODELS) if arf._background[i] is not None),
        "drift_tracker": fork._drift_tracker is not arf._drift_tracker,
    }
    aliasing = {
        "fork_trees_share_fork_rng": all(fork.data[i].rng is fork._rng for i in range(N_MODELS)),
        "orig_trees_share_orig_rng": all(arf.data[i].rng is arf._rng for i in range(N_MODELS)),
    }
    state_at_fork = {
        "drift_totals": common.tracker_vector(arf._drift_tracker, N_MODELS),
        "warning_totals": common.tracker_vector(arf._warning_tracker, N_MODELS),
        "live_background_trees": sum(bg is not None for bg in arf._background),
    }

    err_o, pred_o = replay(arf, suffix)
    err_f, pred_f = replay(fork, suffix)

    equivalent = {
        "error_sequence": err_o == err_f,
        "prediction_sequence": pred_o == pred_f,
        "drift_totals": (common.tracker_vector(arf._drift_tracker, N_MODELS)
                         == common.tracker_vector(fork._drift_tracker, N_MODELS)),
        "warning_totals": (common.tracker_vector(arf._warning_tracker, N_MODELS)
                           == common.tracker_vector(fork._warning_tracker, N_MODELS)),
        "forest_rng_state": (common.state_digest(arf._rng.getstate())
                             == common.state_digest(fork._rng.getstate())),
    }
    checks = {**{f"equivalent.{k}": v for k, v in equivalent.items()},
              **{f"disjoint.{k}": v for k, v in disjoint.items()},
              **{f"aliasing.{k}": v for k, v in aliasing.items()}}

    first_divergence = next((i for i in range(FORK_HORIZON) if err_o[i] != err_f[i]), None)
    return {
        "seed": int(seed), "delta_e": float(delta_e),
        "faithful": all(checks.values()), "checks": checks,
        "first_error_divergence_step": first_divergence,
        "state_at_fork": state_at_fork,
        "swaps_during_replay": int(sum(common.tracker_vector(arf._drift_tracker, N_MODELS))
                                   - sum(state_at_fork["drift_totals"])),
        "mean_error_after_fork": float(np.mean(err_o)),
    }


def main():
    seeds = common.seed_pool(N_SEEDS)
    grid = [(s, de) for de in DELTA_E_GRID for s in seeds]
    print(f"[INFO] G1: {len(grid)} forks | deepcopy at t_rel=+{FORK_T_REL}, "
          f"{FORK_HORIZON} identical replayed steps | M={N_MODELS} c_int={C_INT}")

    t0 = time.perf_counter()
    rows = Parallel(n_jobs=-1)(delayed(fork_run)(s, de)
                               for s, de in tqdm(grid, desc="G1 deepcopy fidelity"))
    wall = time.perf_counter() - t0

    failed = [r for r in rows if not r["faithful"]]
    payload = {
        "gate": "G1",
        "flaw": "prerequisite of the S6 causal test: a forked branch must be state-equivalent and "
                "memory-disjoint",
        "hypothesis": "copy.deepcopy of an ARFClassifier at t_rel=+%d reproduces the original "
                      "bit-for-bit over %d identical steps, sharing no mutable state"
                      % (FORK_T_REL, FORK_HORIZON),
        "verdict": "PASS" if not failed else "FAIL",
        "config": {"n_models": N_MODELS, "c_int": C_INT, "t_drift": T_DRIFT,
                   "fork_t_rel": FORK_T_REL, "fork_horizon": FORK_HORIZON,
                   "replay_order": "original then fork, sequential",
                   "rng_lock": "random.seed + np.random.seed + default_rng(seed % (2**31-1))"},
        "grid": {"n_seeds": N_SEEDS, "delta_e": [float(d) for d in DELTA_E_GRID],
                 "n_forks": len(grid)},
        "n_forks": len(rows),
        "n_faithful": sum(r["faithful"] for r in rows),
        "checks_passed": {k: sum(r["checks"][k] for r in rows) for k in rows[0]["checks"]},
        "n_forks_with_live_background_at_fork":
            sum(r["state_at_fork"]["live_background_trees"] > 0 for r in rows),
        "n_forks_with_swap_during_replay": sum(r["swaps_during_replay"] > 0 for r in rows),
        "per_delta_e": [
            {"delta_e": float(de),
             "n_faithful": sum(r["faithful"] for r in rows if r["delta_e"] == float(de)),
             "n_forks": sum(r["delta_e"] == float(de) for r in rows),
             "mean_error_after_fork": float(np.mean([r["mean_error_after_fork"] for r in rows
                                                     if r["delta_e"] == float(de)])),
             "mean_swaps_during_replay": float(np.mean([r["swaps_during_replay"] for r in rows
                                                        if r["delta_e"] == float(de)]))}
            for de in DELTA_E_GRID],
        "mismatches": failed[:20],
        "wall_clock_s": wall,
        "env": common.env_stamp(),
    }
    common.emit("g1_report.json", payload)

    print(f"\n=== G1 {payload['verdict']} === {payload['n_faithful']}/{payload['n_forks']} forks "
          f"faithful | {wall:.1f}s")
    print(f"  forks with a live background tree at the fork instant: "
          f"{payload['n_forks_with_live_background_at_fork']}/{payload['n_forks']}")
    print(f"  forks where a swap fires during the replayed suffix:  "
          f"{payload['n_forks_with_swap_during_replay']}/{payload['n_forks']}")
    for row in payload["per_delta_e"]:
        print(f"  Delta_e={row['delta_e']:.2f}  faithful={row['n_faithful']}/{row['n_forks']}"
              f"  mean post-fork error={row['mean_error_after_fork']:.4f}"
              f"  mean swaps={row['mean_swaps_during_replay']:.2f}")
    if failed:
        for r in failed[:5]:
            broken = [k for k, v in r["checks"].items() if not v]
            print(f"  UNFAITHFUL seed={r['seed']} Delta_e={r['delta_e']} broken={broken} "
                  f"first_divergence={r['first_error_divergence_step']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
