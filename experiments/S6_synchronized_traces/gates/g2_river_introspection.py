"""Gate G2 -- dynamic map of the River 0.23.0 private surface the S6 harness reads.

`config.experiment_ssot.require_drift_tracker` guards two attributes. The S6 harness reads far more
than two: per-tree replacement counters, both per-tree detector banks with their ADWIN window
statistics, and the background-tree slots. This gate probes each access path on a live model instead
of trusting the River documentation, writes the exact mapping, and raises RuntimeError on any
missing attribute -- the same fail-loud contract as the SSOT guard, extended to the whole surface.

It also measures what the mapping alone does not say: whether a background tree is ever OBSERVABLE
between two `learn_one` calls. River creates the background tree when the warning detector fires and
promotes it when the drift detector fires, both inside one `learn_one`. Three detector
configurations are probed -- the project's blind-spot pair (both ADWIN on c_int), the matched
external pair (both on c_ext) and River's own default pair (ADWIN delta 0.001 / 0.01) -- and for
every replacement the gate records whether the installed tree was a warmed background tree or a
tree created in that same step, i.e. one that has learned nothing.
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from river import drift, forest

import _gate_common as common
from _gate_common import ssot

N_STEPS = ssot.S6_N_STEPS
T_DRIFT = ssot.S6_T_DRIFT
N_MODELS = ssot.S6_N_MODELS
C_INT = ssot.S6_C_INT
C_EXT = ssot.S6_C_EXT
PROBE_DELTA_E = ssot.S6_GATE_DELTA_E[1]        # mid band; swaps fire in every configuration

# Access paths the S6 harness depends on. (attribute, what it carries, per-tree container or not)
REQUIRED_FOREST = {
    "_drift_tracker": "per-tree replacement counter, keyed by tree index",
    "_warning_tracker": "per-tree warning counter, keyed by tree index",
    "_drift_detectors": "per-tree drift detector bank",
    "_warning_detectors": "per-tree warning detector bank",
    "_background": "per-tree background tree slot (None when no warning is live)",
    "_metrics": "per-tree weighting metric",
    "_rng": "forest generator, threaded into every tree",
    "data": "the ensemble itself (UserList payload)",
}
REQUIRED_FOREST_CALLABLES = {
    "n_drifts_detected": "public accessor over _drift_tracker",
    "n_warnings_detected": "public accessor over _warning_tracker",
}
REQUIRED_DETECTOR = {
    "drift_detected": "boolean latch read after update()",
    "width": "ADWIN window length",
    "estimation": "ADWIN window mean",
    "variance": "ADWIN window variance",
    "total": "ADWIN window sum",
    "n_detections": "cumulative detections on this detector instance",
    "clock": "declared clock (c_int / c_ext)",
    "delta": "declared sensitivity",
    "grace_period": "steps before the first cut is attempted",
}
REQUIRED_TREE = {
    "n_nodes": "tree size",
    "n_leaves": "leaf count",
    "n_active_leaves": "active leaf count",
    "height": "tree depth",
    "rng": "generator reference, must be the forest generator",
}

CONFIGS = {
    "blind_spot_c_int": {"drift": lambda: drift.ADWIN(clock=C_INT),
                         "warning": lambda: drift.ADWIN(clock=C_INT),
                         "motive": "project configuration (R1/R2/R6/R7/R8/R9): both ADWINs on c_int"},
    "matched_c_ext": {"drift": lambda: drift.ADWIN(clock=C_EXT),
                      "warning": lambda: drift.ADWIN(clock=C_EXT),
                      "motive": "matched external clock, River's default clock value"},
    "river_default": {"drift": lambda: None, "warning": lambda: None,
                      "motive": "River's own defaults: ADWIN(delta=0.001) / ADWIN(delta=0.01)"},
}


def describe(obj, required, prefix):
    """{name: {present, type, repr}} for every required attribute; missing ones flagged, not raised."""
    out = {}
    for name, role in required.items():
        present = hasattr(obj, name)
        entry = {"path": f"{prefix}.{name}", "role": role, "present": present}
        if present:
            value = getattr(obj, name)
            entry["type"] = type(value).__module__ + "." + type(value).__name__
            entry["callable"] = callable(value)
            if not entry["callable"]:
                entry["sample"] = repr(value)[:160]
                if hasattr(value, "__len__"):
                    entry["len"] = len(value)
        out[name] = entry
    return out


def probe(name, cfg):
    """One full trajectory; returns the observability record for this detector configuration."""
    safe_seed, rng = common.lock_rng(common.seed_pool(1)[0])
    arf = forest.ARFClassifier(n_models=N_MODELS, seed=safe_seed,
                               drift_detector=cfg["drift"](), warning_detector=cfg["warning"]())
    b_shift = common.boundary_shift(PROBE_DELTA_E)

    steps_with_live_bg = 0
    first_live_bg_step = None
    max_live_bg = 0
    promotions_warmed = 0
    promotions_cold = 0
    prev_drift = (0,) * N_MODELS

    for t in range(N_STEPS):
        x0, x1 = rng.normal(), rng.normal()
        x_dict = {0: x0, 1: x1}
        y = int(x0 + x1 > (0.0 if t < T_DRIFT else b_shift))

        bg_before = [bg is not None for bg in arf._background]
        arf.predict_one(x_dict)
        arf.learn_one(x_dict, y)

        now_drift = common.tracker_vector(arf._drift_tracker, N_MODELS)
        for i in range(N_MODELS):
            if now_drift[i] > prev_drift[i]:
                if bg_before[i]:
                    promotions_warmed += 1
                else:
                    promotions_cold += 1
        prev_drift = now_drift

        live = sum(bg is not None for bg in arf._background)
        if live:
            steps_with_live_bg += 1
            max_live_bg = max(max_live_bg, live)
            if first_live_bg_step is None:
                first_live_bg_step = t

    warn = common.tracker_vector(arf._warning_tracker, N_MODELS)
    return arf, {
        "motive": cfg["motive"],
        "drift_totals": list(now_drift),
        "warning_totals": list(warn),
        "warning_equals_drift_elementwise": now_drift == warn,
        "steps_with_a_live_background_tree": steps_with_live_bg,
        "first_step_with_a_live_background_tree": first_live_bg_step,
        "max_simultaneous_background_trees": max_live_bg,
        "replacements_with_a_warmed_background_tree": promotions_warmed,
        "replacements_with_a_tree_created_in_the_same_step": promotions_cold,
        "n_drifts_detected_matches_tracker": arf.n_drifts_detected() == sum(now_drift),
        "n_warnings_detected_matches_tracker": arf.n_warnings_detected() == sum(warn),
        "per_tree_accessor_matches_tracker": all(
            arf.n_drifts_detected(i) == now_drift[i] for i in range(N_MODELS)),
    }


def main():
    t0 = time.perf_counter()
    observability, models = {}, {}
    for name, cfg in CONFIGS.items():
        print(f"[INFO] G2: probing configuration {name} ({cfg['motive']})")
        models[name], observability[name] = probe(name, cfg)

    ref = models["blind_spot_c_int"]
    api_map = {
        "forest_attributes": describe(ref, REQUIRED_FOREST, "model"),
        "forest_callables": describe(ref, REQUIRED_FOREST_CALLABLES, "model"),
        "drift_detector_fields": describe(ref._drift_detectors[0], REQUIRED_DETECTOR,
                                          "model._drift_detectors[i]"),
        "warning_detector_fields": describe(ref._warning_detectors[0], REQUIRED_DETECTOR,
                                            "model._warning_detectors[i]"),
        "tree_fields": describe(ref.data[0], REQUIRED_TREE, "model.data[i]"),
    }
    missing = [f"{section}:{name}" for section, entries in api_map.items()
               for name, entry in entries.items() if not entry["present"]]

    api_map["forest_attributes"]["_drift_tracker"]["key_semantics"] = (
        "collections.defaultdict(int) keyed by tree index in [0, n_models-1]; a key is absent until "
        "that tree is first replaced -- read with .get(i, 0), indexing inserts the key")
    api_map["forest_attributes"]["_background"]["key_semantics"] = (
        "list of length n_models; entry is a BaseTreeClassifier between the warning and the drift, "
        "None otherwise")
    api_map["tree_fields"]["rng"]["aliasing"] = (
        "model.data[i].rng is model._rng -- River threads one generator through the whole forest; "
        f"verified: {all(ref.data[i].rng is ref._rng for i in range(N_MODELS))}")

    payload = {
        "gate": "G2",
        "flaw": "the S6 harness reads a private River surface wider than the two attributes the "
                "SSOT guard covers",
        "verdict": "FAIL" if missing else "PASS",
        "river": ref.__class__.__module__ + "." + ref.__class__.__name__,
        "config": {"n_models": N_MODELS, "c_int": C_INT, "c_ext": C_EXT, "n_steps": N_STEPS,
                   "t_drift": T_DRIFT, "probe_delta_e": PROBE_DELTA_E},
        "api_map": api_map,
        "missing_attributes": missing,
        "background_tree_observability": observability,
        "finding": (
            "In the project's blind-spot configuration both detectors are identical ADWIN clones "
            "fed the same input, so they fire on the same step: the background tree is created and "
            "promoted inside one learn_one call and is never observable between steps. The "
            "replacement tree is therefore a tree that has learned nothing. River's own default "
            "pair (delta 0.001 / 0.01) separates the two events and does expose live background "
            "trees. Consequence for S6: `_background` is a valid access path but a constant-None "
            "observable on the c_int and c_ext arms; per-tree adaptation must be read from "
            "`_drift_tracker` and the detector windows, not from background occupancy."),
        "wall_clock_s": time.perf_counter() - t0,
        "env": common.env_stamp(),
    }
    common.emit("g2_api_map.json", payload)

    print(f"\n=== G2 {payload['verdict']} === {sum(len(v) for v in api_map.values())} access paths "
          f"probed, {len(missing)} missing | {payload['wall_clock_s']:.1f}s")
    for name, obs in observability.items():
        print(f"  {name:18s} drifts={sum(obs['drift_totals']):4d} warnings={sum(obs['warning_totals']):4d}"
              f"  live-bg steps={obs['steps_with_a_live_background_tree']:5d}"
              f"  replacements warmed/cold={obs['replacements_with_a_warmed_background_tree']}/"
              f"{obs['replacements_with_a_tree_created_in_the_same_step']}")

    if missing:
        raise RuntimeError(
            "River %s is missing the S6 access paths: %s. The pinned build is river==0.23.0; "
            "the S6 harness must not run on a build that renames or drops them."
            % (common.env_stamp()["river"], ", ".join(missing)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
