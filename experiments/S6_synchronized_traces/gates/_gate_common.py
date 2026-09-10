"""Shared primitives for the stream S6 Phase-0 gates (G0..G3).

One module so the triple RNG lock, the ARF factory and the boundary-shift map are byte-identical
across the four gates: G0 measures an equality between two arms, and that measurement is only
meaningful if every gate builds the model and the stream the same way.
"""
import hashlib
import json
import platform
import random
import sys
from pathlib import Path

import numpy as np
import scipy
from river import drift, forest
from scipy.stats import norm

ROOT_DIR = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT_DIR))
from config import experiment_ssot as ssot  # noqa: E402

import river  # noqa: E402

GATES_DIR = Path(__file__).resolve().parent


def lock_rng(seed):
    """Triple per-worker lock, R2/R6/R7 scheme. Returns (safe_seed, local generator)."""
    safe_seed = int(seed % (2**31 - 1))
    random.seed(safe_seed)
    np.random.seed(safe_seed)
    return safe_seed, np.random.default_rng(safe_seed)


def boundary_shift(delta_e):
    """b such that Delta_e = Phi(b / sqrt(2)) - 0.5."""
    return float(np.sqrt(2.0) * norm.ppf(0.5 + delta_e))


def make_arf(safe_seed, n_models, clock):
    """ARFClassifier with both ADWINs on the same clock, guarded against a River version drift."""
    return ssot.require_drift_tracker(
        forest.ARFClassifier(
            n_models=n_models,
            seed=safe_seed,
            drift_detector=drift.ADWIN(clock=clock),
            warning_detector=drift.ADWIN(clock=clock),
        ),
        warning=True,
    )


def seed_pool(n):
    seq = np.random.SeedSequence(ssot.S6_SEED_MASTER)
    return [int(s.generate_state(1)[0]) for s in seq.spawn(n)]


def tracker_vector(tracker, n_models):
    """Per-tree counter vector read without inserting keys into the defaultdict."""
    return tuple(int(tracker.get(i, 0)) for i in range(n_models))


def state_digest(*objs):
    return hashlib.sha256(repr(objs).encode("utf-8")).hexdigest()[:16]


def rng_digests(arf):
    """Digest of the forest generator and of both global generators.

    The forest generator is the one River threads into every tree (`tree.rng is arf._rng`); the two
    globals are what the triple lock pins. Equality of the three digests after a run is the direct
    evidence that a call consumed no entropy, independent of what the drift trackers show."""
    return {
        "forest_rng": state_digest(arf._rng.getstate()),
        "global_random": state_digest(random.getstate()),
        "global_np_random": state_digest(np.random.get_state()),
    }


def env_stamp():
    return {
        "python": platform.python_version(),
        "river": river.__version__,
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "executable": sys.executable,
    }


def emit(name, payload):
    path = GATES_DIR / name
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=float) + "\n",
                    encoding="utf-8")
    print(f"[INFO] wrote {path.relative_to(ROOT_DIR)}")
    return path
