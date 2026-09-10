"""Gate G0 -- RNG neutrality of predict_one() (faille F25).

R1 and R8 dropped `predict_one()` from the instrumented loop, on the stated argument that it is
deterministic, consumes no RNG state, and therefore leaves tau_ARF unchanged while halving the cost
(exp_R8_lambda_op_sweep.py, methodological alignment 2). S6 needs the ensemble error and the
internal per-tree statistics on the SAME trajectory, so predict_one() must return to the loop. This
gate measures that argument instead of inheriting it.

Design. 50 seeds x Delta_e in {0.10, 0.25, 0.40}; for each pair, two arms under one identical triple
RNG lock -- arm `with_predict` (predict_one then learn_one, R2 ordering) and arm `without_predict`
(learn_one only, R8 ordering). Four quantities are compared, from weakest to strongest:

  1. tau_swap^(1/M)  -- first post-drift step at which the aggregate replacement counter increments.
  2. per-tree first swap -- the full M-vector of first post-drift increments, which is what F6 needs
     and what a min_i-only comparison cannot certify.
  3. final per-tree drift and warning counters.
  4. the forest generator state and both global generator states at end of run.

(4) is the direct evidence: if predict_one() consumed entropy, the digests would differ even on the
runs where no swap ever fires. PASS requires strict equality on all four.
"""
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


def trace_arm(seed, delta_e, predict):
    """One ARF run; returns the swap chronology and the end-of-run generator digests."""
    safe_seed, rng = common.lock_rng(seed)
    arf = common.make_arf(safe_seed, N_MODELS, C_INT)
    b_shift = common.boundary_shift(delta_e)

    first_per_tree = [None] * N_MODELS
    tau_first = None
    prev = (0,) * N_MODELS
    t0 = time.perf_counter()

    for t in range(N_STEPS):
        x0, x1 = rng.normal(), rng.normal()
        x_dict = {0: x0, 1: x1}
        y = int(x0 + x1 > (0.0 if t < T_DRIFT else b_shift))

        if predict:
            arf.predict_one(x_dict)
        arf.learn_one(x_dict, y)

        now = common.tracker_vector(arf._drift_tracker, N_MODELS)
        if t >= T_DRIFT and now != prev:
            for i in range(N_MODELS):
                if first_per_tree[i] is None and now[i] > prev[i]:
                    first_per_tree[i] = t - T_DRIFT
            if tau_first is None:
                tau_first = t - T_DRIFT
        prev = now

    return {
        "tau_first": tau_first,
        "first_per_tree": tuple(first_per_tree),
        "drift_totals": prev,
        "warning_totals": common.tracker_vector(arf._warning_tracker, N_MODELS),
        "rng": common.rng_digests(arf),
        "seconds": time.perf_counter() - t0,
    }


def compare(seed, delta_e):
    a = trace_arm(seed, delta_e, predict=True)
    b = trace_arm(seed, delta_e, predict=False)
    checks = {
        "tau_first": a["tau_first"] == b["tau_first"],
        "first_per_tree": a["first_per_tree"] == b["first_per_tree"],
        "drift_totals": a["drift_totals"] == b["drift_totals"],
        "warning_totals": a["warning_totals"] == b["warning_totals"],
        "rng_state": a["rng"] == b["rng"],
    }
    return {
        "seed": int(seed), "delta_e": float(delta_e),
        "identical": all(checks.values()), "checks": checks,
        "with_predict": {k: a[k] for k in ("tau_first", "first_per_tree", "drift_totals",
                                           "warning_totals", "rng")},
        "without_predict": {k: b[k] for k in ("tau_first", "first_per_tree", "drift_totals",
                                              "warning_totals", "rng")},
        "seconds_with": a["seconds"], "seconds_without": b["seconds"],
    }


def main():
    seeds = common.seed_pool(N_SEEDS)
    grid = [(s, de) for de in DELTA_E_GRID for s in seeds]
    print(f"[INFO] G0: {len(grid)} pairs x 2 arms | M={N_MODELS} c_int={C_INT} "
          f"n_steps={N_STEPS} t_drift={T_DRIFT}")

    t0 = time.perf_counter()
    rows = Parallel(n_jobs=-1)(delayed(compare)(s, de)
                               for s, de in tqdm(grid, desc="G0 predict_one neutrality"))
    wall = time.perf_counter() - t0

    failed = [r for r in rows if not r["identical"]]
    per_delta = []
    for de in DELTA_E_GRID:
        sub = [r for r in rows if r["delta_e"] == float(de)]
        taus = [r["with_predict"]["tau_first"] for r in sub
                if r["with_predict"]["tau_first"] is not None]
        per_delta.append({
            "delta_e": float(de),
            "n_pairs": len(sub),
            "n_identical": sum(r["identical"] for r in sub),
            "n_censored": len(sub) - len(taus),
            "median_tau_first": float(np.median(taus)) if taus else None,
            "q05_tau_first": float(np.quantile(taus, 0.05)) if taus else None,
            "mean_seconds_with": float(np.mean([r["seconds_with"] for r in sub])),
            "mean_seconds_without": float(np.mean([r["seconds_without"] for r in sub])),
        })

    payload = {
        "gate": "G0",
        "flaw": "F25 -- R1/R8 omitted predict_one(), forbidding simultaneous observation of the "
                "ensemble error and the internal statistics",
        "hypothesis": "predict_one() consumes no RNG state, so the per-tree swap chronology is "
                      "strictly identical with and without it",
        "verdict": "PASS" if not failed else "FAIL",
        "config": {"n_models": N_MODELS, "c_int": C_INT, "n_steps": N_STEPS, "t_drift": T_DRIFT,
                   "censoring_horizon": ssot.S6_CENSORING_HORIZON,
                   "rng_lock": "random.seed + np.random.seed + default_rng(seed % (2**31-1))",
                   "seed_scheme": f"SeedSequence({ssot.S6_SEED_MASTER}).spawn({N_SEEDS})"},
        "grid": {"n_seeds": N_SEEDS, "delta_e": [float(d) for d in DELTA_E_GRID],
                 "n_pairs": len(grid)},
        "n_pairs": len(rows),
        "n_identical": sum(r["identical"] for r in rows),
        "n_mismatched": len(failed),
        "checks_passed": {k: sum(r["checks"][k] for r in rows) for k in rows[0]["checks"]},
        "per_delta_e": per_delta,
        "mismatches": failed[:20],
        "cost_ratio_with_over_without": float(
            np.mean([r["seconds_with"] for r in rows]) / np.mean([r["seconds_without"] for r in rows])),
        "wall_clock_s": wall,
        "env": common.env_stamp(),
    }
    common.emit("g0_report.json", payload)

    print(f"\n=== G0 {payload['verdict']} === {payload['n_identical']}/{payload['n_pairs']} pairs "
          f"strictly identical | cost ratio with/without = "
          f"{payload['cost_ratio_with_over_without']:.2f}x | {wall:.1f}s")
    for row in per_delta:
        print(f"  Delta_e={row['delta_e']:.2f}  identical={row['n_identical']}/{row['n_pairs']}"
              f"  censored={row['n_censored']}  median tau_first={row['median_tau_first']}")
    if failed:
        for r in failed[:5]:
            print(f"  MISMATCH seed={r['seed']} Delta_e={r['delta_e']} checks={r['checks']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
