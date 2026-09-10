"""Gate G3 -- instrumented throughput and extrapolated cost of the Phase-1 campaign.

The S6 harness records, at every step, what R1/R8 recorded at one step: the ensemble error
(predict_one, F25), the per-tree replacement and warning counters (F6) and the ADWIN window
statistics of every tree (F7). There is no early break -- the integrated error budget A needs the
whole post-drift window, not the instant of the first swap. This gate measures the cost of that
step and extrapolates the declared campaign shape `config.experiment_ssot.S6_ARMS`.

Three measurements, none of them assumed:
  1. seconds per instrumented step, per factorial arm, plus a bare learn_one loop on the reference
     arm to isolate the instrumentation overhead from the model cost;
  2. the parallel efficiency actually obtained on this host -- one saturating round of identical
     tasks under joblib, wall clock against serial time, rather than a nominal division by 48;
  3. a cross-check of the extrapolation against the wall clock G0 already measured on this machine.
"""
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from joblib import Parallel, delayed

import _gate_common as common
from _gate_common import ssot

N_STEPS = ssot.S6_N_STEPS
T_DRIFT = ssot.S6_T_DRIFT
N_MODELS = ssot.S6_N_MODELS
C_INT = ssot.S6_C_INT
BENCH_STEPS = ssot.S6_G3_BENCH_STEPS
ARMS = ssot.S6_ARMS
CAMPAIGN_SEEDS = ssot.S6_CAMPAIGN_SEEDS
CAMPAIGN_SHIFTS = ssot.S6_CAMPAIGN_BOUNDARY_SHIFTS
PROBE_DELTA_E = ssot.S6_GATE_DELTA_E[1]


def bench(n_models, clock, steps, instrumented=True, seed=1):
    """One timed run of `steps` steps. `instrumented` toggles the whole S6 per-step record."""
    safe_seed, rng = common.lock_rng(seed)
    arf = common.make_arf(safe_seed, n_models, clock)
    b_shift = common.boundary_shift(PROBE_DELTA_E)
    t_drift = steps // 2
    trace = []

    t0 = time.perf_counter()
    for t in range(steps):
        x0, x1 = rng.normal(), rng.normal()
        x_dict = {0: x0, 1: x1}
        y = int(x0 + x1 > (0.0 if t < t_drift else b_shift))

        if not instrumented:
            arf.learn_one(x_dict, y)
            continue

        y_pred = arf.predict_one(x_dict)
        arf.learn_one(x_dict, y)
        trace.append((
            t,
            float((y_pred if y_pred is not None else 0) != y),
            common.tracker_vector(arf._drift_tracker, n_models),
            common.tracker_vector(arf._warning_tracker, n_models),
            tuple((d.width, d.estimation, d.variance) for d in arf._drift_detectors),
            tuple(bg is not None for bg in arf._background),
        ))
    elapsed = time.perf_counter() - t0
    return elapsed, len(trace)


def arm_name(n_models, clock):
    return f"M{n_models}_clock{clock}"


def main():
    n_cpu = os.cpu_count()
    print(f"[INFO] G3: {BENCH_STEPS} instrumented steps per arm | {len(ARMS)} arms | "
          f"os.cpu_count()={n_cpu}")
    t_gate = time.perf_counter()

    arms = []
    for n_models, clock in ARMS:
        elapsed, n_rows = bench(n_models, clock, BENCH_STEPS)
        arms.append({
            "arm": arm_name(n_models, clock), "n_models": int(n_models), "clock": int(clock),
            "instrumented": True, "steps": BENCH_STEPS, "seconds": elapsed,
            "sec_per_step": elapsed / BENCH_STEPS, "steps_per_second": BENCH_STEPS / elapsed,
            "trace_rows": n_rows,
        })
        print(f"  {arms[-1]['arm']:14s} {elapsed:7.2f}s  "
              f"{arms[-1]['steps_per_second']:8.1f} steps/s")

    bare_s, _ = bench(N_MODELS, C_INT, BENCH_STEPS, instrumented=False)
    ref = next(a for a in arms if a["arm"] == arm_name(N_MODELS, C_INT))
    overhead = {
        "reference_arm": ref["arm"],
        "instrumented_seconds": ref["seconds"],
        "bare_learn_one_seconds": bare_s,
        "overhead_ratio": ref["seconds"] / bare_s,
        "overhead_sec_per_step": (ref["seconds"] - bare_s) / BENCH_STEPS,
        "note": "bare loop = learn_one only, R8 ordering, no predict_one and no per-step record",
    }
    print(f"  bare learn_one {bare_s:7.2f}s  -> instrumentation overhead "
          f"{overhead['overhead_ratio']:.2f}x")

    # --- Measured parallel efficiency, not a nominal division by the core count ----------------
    t0 = time.perf_counter()
    Parallel(n_jobs=-1)(delayed(bench)(N_MODELS, C_INT, BENCH_STEPS, True, s)
                        for s in range(n_cpu))
    par_wall = time.perf_counter() - t0
    efficiency = (n_cpu * ref["seconds"]) / (n_cpu * par_wall)
    scaling = {
        "n_logical_cpus": n_cpu,
        "n_tasks": n_cpu,
        "serial_seconds_per_task": ref["seconds"],
        "wall_seconds_for_one_saturating_round": par_wall,
        "measured_efficiency": efficiency,
        "effective_workers": n_cpu * efficiency,
        "note": "one round of n_cpu identical reference-arm tasks under joblib n_jobs=-1; "
                "efficiency < 1 is the hyperthread and scheduling cost, 24 physical cores for "
                "48 logical threads",
    }
    print(f"  parallel round {par_wall:7.2f}s  -> efficiency {efficiency:.2f}, "
          f"effective workers {scaling['effective_workers']:.1f}")

    # --- Campaign extrapolation ----------------------------------------------------------------
    n_seeds, n_magnitudes = len(CAMPAIGN_SEEDS), len(CAMPAIGN_SHIFTS)
    n_runs_per_arm = n_seeds * n_magnitudes
    per_arm = []
    for a in arms:
        core_s = n_runs_per_arm * N_STEPS * a["sec_per_step"]
        per_arm.append({"arm": a["arm"], "n_runs": n_runs_per_arm, "n_steps": N_STEPS,
                        "sec_per_run": N_STEPS * a["sec_per_step"], "core_seconds": core_s})
    serial_core_s = sum(p["core_seconds"] for p in per_arm)
    campaign = {
        "design": {
            "arms": [arm_name(m, c) for m, c in ARMS],
            "factorial": "(M in {%s}) x (ADWIN clock in {%s})"
                         % (", ".join(sorted({str(m) for m, _ in ARMS})),
                            ", ".join(sorted({str(c) for _, c in ARMS}))),
            "n_seeds": n_seeds, "n_magnitudes": n_magnitudes, "n_steps": N_STEPS,
            "t_drift": T_DRIFT, "early_break": False,
            "total_runs": len(ARMS) * n_runs_per_arm,
            "total_steps": len(ARMS) * n_runs_per_arm * N_STEPS,
            "source": "config.experiment_ssot.S6_ARMS / S6_CAMPAIGN_SEEDS / "
                      "S6_CAMPAIGN_BOUNDARY_SHIFTS",
        },
        "per_arm": per_arm,
        "serial_core_seconds": serial_core_s,
        "wall_clock_estimate_s": {
            "measured_efficiency": serial_core_s / (n_cpu * efficiency),
            "ideal_logical_48": serial_core_s / n_cpu,
            "physical_cores_24": serial_core_s / (n_cpu // 2),
        },
        "rescale_formula": "wall_s = n_arms_scaled * n_seeds * n_magnitudes * n_steps * "
                           "sec_per_step(arm) / (n_cpu * measured_efficiency); sec_per_step is in "
                           "bench.arms and is the only quantity that needs re-measuring",
    }

    cross_check = {"available": False}
    g0_path = common.GATES_DIR / "g0_report.json"
    if g0_path.exists():
        g0 = json.loads(g0_path.read_text(encoding="utf-8"))
        g0_steps = g0["n_pairs"] * 2 * g0["config"]["n_steps"]
        predicted = g0_steps * ref["sec_per_step"] / (n_cpu * efficiency)
        cross_check = {
            "available": True,
            "reference": "g0_report.json, same host, same session",
            "g0_total_steps": g0_steps,
            "predicted_wall_s": predicted,
            "observed_wall_s": g0["wall_clock_s"],
            "ratio_predicted_over_observed": predicted / g0["wall_clock_s"],
            "note": "upper bound: G0 records only the drift-counter vector, the reference arm here "
                    "records the full S6 per-step payload, and G0's second arm has no predict_one",
        }

    payload = {
        "gate": "G3",
        "flaw": "F6 / F7 / F25 -- the full-trace harness has no early break and no dropped "
                "predict_one, so its cost is not R8's cost",
        "verdict": "PASS",
        "host": {"os_cpu_count": n_cpu, "platform": sys.platform},
        "bench": {"steps_per_arm": BENCH_STEPS, "probe_delta_e": PROBE_DELTA_E, "arms": arms},
        "instrumentation_overhead": overhead,
        "parallel_scaling": scaling,
        "campaign": campaign,
        "cross_check_vs_g0": cross_check,
        "wall_clock_s": time.perf_counter() - t_gate,
        "env": common.env_stamp(),
    }
    common.emit("g3_report.json", payload)

    est = campaign["wall_clock_estimate_s"]
    print(f"\n=== G3 PASS === campaign {campaign['design']['total_runs']} runs / "
          f"{campaign['design']['total_steps']:,} steps")
    for p in per_arm:
        print(f"  {p['arm']:14s} {p['n_runs']:5d} runs x {p['sec_per_run']:6.2f}s = "
              f"{p['core_seconds']/3600:7.2f} core-hours")
    print(f"  serial total {serial_core_s/3600:.2f} core-hours")
    print(f"  wall clock estimate: {est['measured_efficiency']/3600:.2f} h at measured efficiency "
          f"({efficiency:.2f}) | {est['ideal_logical_48']/3600:.2f} h ideal-{n_cpu} | "
          f"{est['physical_cores_24']/3600:.2f} h on {n_cpu//2} physical cores")
    if cross_check["available"]:
        print(f"  cross-check vs G0: predicted {cross_check['predicted_wall_s']:.1f}s "
              f"observed {cross_check['observed_wall_s']:.1f}s "
              f"(ratio {cross_check['ratio_predicted_over_observed']:.2f})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
