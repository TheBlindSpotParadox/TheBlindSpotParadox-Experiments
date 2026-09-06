# experiment_ssot.py
"""Single source of truth for the experimental constants of "The Blind Spot Paradox" (ICDM 2026).

Form generalised from `experiments/R5_real_world_evaluation/exp_R5_config.py`: dynamic `ROOT_DIR`,
named module-level constants, no experiment logic. The only callable is the River private-attribute
guard, shared by every script that instruments `_drift_tracker` / `_warning_tracker`.

Registry (S7/CONFIG §6): N_STEPS, T_DRIFT, CENSORING_HORIZON, N_MODELS, SEED_SCHEME,
BOUNDARY_SHIFTS, DELTA_E_GRID, C_INT, C_EXT, EXT_DELTA, DELTA_P, LAMBDAS, WARMUP_WINDOW,
DELTA_E_WINDOW, N_SEEDS_REAL, TAU_TOL.

Intentional per-experiment divergences are DERIVED CONSTANTS carrying an `R<n>_` prefix and a motive,
never local literals. `tests/test_S7_consistency.py` walks every module-level assignment in
`experiments/**/*.py` and fails if a registry name is re-bound to a local literal, or if any resolved
value drifts from `results/audit_S7/_baseline/constants_pre.json`.

VALUE-PRESERVING BY CONSTRUCTION. No RNG call site, no draw ordering and no predict_one/learn_one
ordering is defined here: the two-`rng.normal()`-per-step invariant lives in the experiment loops and
is what makes the artifacts bit-comparable. The triple per-worker lock (`random.seed` +
`np.random.seed` + `default_rng`) is likewise left verbatim in each worker function -- it is required
by River's Cython tree-spawn path and must not be centralised or "cleaned up".

R4 (ProteuS) and R5 (real world) carry their registry values in function defaults and in
`exp_R5_config.py` respectively; the constants declared here for them are the audited reference used
by the consistency test, not a replacement of their call sites.
"""
from pathlib import Path

import numpy as np

# --- Dynamic, portable paths (mandated FAIR layout) ---
ROOT_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT_DIR / "results"
DATA_DIR = ROOT_DIR / "data"

# ══════════════════════════════════════════════════════════════════════════════
# Canonical registry — the instrumented Bernoulli boundary-shift family (R2, R6, R7, R9)
# ══════════════════════════════════════════════════════════════════════════════
N_STEPS = 8000
T_DRIFT = 4000
CENSORING_HORIZON = N_STEPS - T_DRIFT          # 4000 post-drift steps; NaN tau == censored here
N_MODELS = 10
BOUNDARY_SHIFTS = np.linspace(0.1, 4.0, 20)    # Delta_e = Phi(b/sqrt(2)) - 0.5
C_INT = 1                                      # internal ADWIN clock (blind-spot configuration)
C_EXT = 32                                     # River's default external clock
EXT_DELTA = 0.002                              # external ADWIN sensitivity
DELTA_P = 0.005                                # PageHinkley / CUSUM drift tolerance

# Seed schemes. The naive integer range is deliberate ("AE Visual Match"): it reproduces the feature
# streams of the submitted manuscript bit-for-bit. Do not replace it with a SeedSequence.
SEED_SCHEME_NAIVE_1_100 = list(range(1, 101))
SEED_SCHEME_NAIVE_0_99 = list(range(100))
SEED_SCHEME_NAIVE_1_30 = list(range(1, 31))
SEED_SCHEME_SEEDSEQ_ENTROPY = 42               # np.random.SeedSequence(42).spawn(n)

# ══════════════════════════════════════════════════════════════════════════════
# R1 — race condition (Figure 1)
# ══════════════════════════════════════════════════════════════════════════════
R1_CENSORING_HORIZON = 50_000                  # starvation bounds, cf. Fig. 1
R1_T_DRIFT = 4000
R1_N_STEPS = R1_T_DRIFT + R1_CENSORING_HORIZON # 54000
R1_N_SEEDS = 200
R1_DELTA_E = 0.25                              # single magnitude; the sweep is over lambda
R1_LAMBDAS = [2.5, 5.0, 10.0, 15.0, 20.0, 25.0, 50.0, 100.0]  # S7/G2: 15 and 20 added to measure
                                               # lambda* instead of interpolating it across [10, 25]
R1_DELTA_P = DELTA_P
R1_WARMUP_WINDOW = 1000                        # pre-drift error buffer for the empirical CUSUM p_pre
R1_C_INT = C_INT

# ══════════════════════════════════════════════════════════════════════════════
# R2 — instrumented blind spot (Figures 2A-2C)
# ══════════════════════════════════════════════════════════════════════════════
R2_N_STEPS = N_STEPS
R2_T_DRIFT = T_DRIFT
R2_N_MODELS = N_MODELS
R2_BOUNDARY_SHIFTS = BOUNDARY_SHIFTS
R2_SEEDS = SEED_SCHEME_NAIVE_1_100
R2_WARMUP_WINDOW = 1000                        # last 1000 pre-drift steps calibrate p_pre
R2_LAMBDAS = [50.0, 25.0, 8.0]                 # scenarios A / B / C (declared; SCENARIOS carries the
                                               # display strings and is not a registry name)
R2_CUSUM_DELTA = 0.01                          # NOT DELTA_P: R2's StrictCUSUM tolerance is 0.01

# ══════════════════════════════════════════════════════════════════════════════
# R3 — regime crossover (Figure 3)
# ══════════════════════════════════════════════════════════════════════════════
R3_N_STEPS = N_STEPS
R3_T_DRIFT = T_DRIFT
R3_TAU_TOL = 1000                              # post-drift scoring window
R3_N_SEEDS = 100
R3_SEEDS = SEED_SCHEME_NAIVE_0_99
R3_DELTA_E_GRID = np.linspace(0.02, 0.50, 15)
R3_PHT_LAMBDA = 25.0                           # declared: constructed inline in run_single_seed
R3_DELTA_P = DELTA_P
R3_C_INT = C_INT                               # warning_detector left at river default (see README §5)

# ══════════════════════════════════════════════════════════════════════════════
# R4 — ProteuS / Table I (declared reference; literals live in function defaults)
# ══════════════════════════════════════════════════════════════════════════════
R4_N_STEPS = N_STEPS
R4_T_DRIFT = T_DRIFT
R4_N_MODELS = N_MODELS
R4_N_SEEDS = 30
R4_SEEDS = SEED_SCHEME_NAIVE_1_30
R4_PHT_LAMBDA = 15.0                           # calibrated on ProteuS pre-drift volatility (.tex L362)
R4_ADWIN_DELTA = 0.002
R4_KSWIN_ALPHA = 0.005
R4_DRIFT_WIDTHS = [100, 500, 1000]
R4_TAU_TOL_FLOOR = 1000                        # tau = max(R4_TAU_TOL_FLOOR, w)

# ══════════════════════════════════════════════════════════════════════════════
# R5 — real-world streams / Table II
# ══════════════════════════════════════════════════════════════════════════════
N_SEEDS_REAL = 30
TAU_TOL = 5_000                                # BAF_TAU_TOL and the INSECTS adaptive-tolerance cap
R5_PHT_DELTA = DELTA_P
R5_N_MODELS = N_MODELS
R5_SEED_MASTER = SEED_SCHEME_SEEDSEQ_ENTROPY

# ══════════════════════════════════════════════════════════════════════════════
# R6 — Hydra factor (single HAT)
# ══════════════════════════════════════════════════════════════════════════════
R6_N_STEPS = N_STEPS
R6_T_DRIFT = T_DRIFT
R6_N_MODELS = 1                                # M = 1: the single-tree reference arm of the factor
R6_C_INT = C_INT
R6_BOUNDARY_SHIFTS = BOUNDARY_SHIFTS
R6_SEEDS = SEED_SCHEME_NAIVE_1_100

# ══════════════════════════════════════════════════════════════════════════════
# R7 — clock mismatch (Regime 1)
# ══════════════════════════════════════════════════════════════════════════════
R7_N_STEPS = N_STEPS
R7_T_DRIFT = T_DRIFT
R7_N_MODELS = N_MODELS
R7_BOUNDARY_SHIFTS = BOUNDARY_SHIFTS
R7_SEEDS = SEED_SCHEME_NAIVE_1_100
R7_EXT_DELTA = EXT_DELTA

# ══════════════════════════════════════════════════════════════════════════════
# R8 — lambda_op sweep (Decoupling Principle)
# ══════════════════════════════════════════════════════════════════════════════
R8_WARMUP_WINDOW = 1000
R8_DRIFT_GAP = 1000
R8_CENSORING_HORIZON = 50_000                  # post-drift tracking tolerance, aligned with R1
R8_T_DRIFT = R8_WARMUP_WINDOW + R8_DRIFT_GAP   # 2000
R8_N_STEPS = R8_T_DRIFT + R8_CENSORING_HORIZON # 52000
R8_N_MODELS = N_MODELS
R8_C_INT = C_INT
R8_N_SEEDS = 200
R8_DELTA_E_GRID = np.linspace(0.10, 0.50, 21)
R8_DELTA_P = DELTA_P
R8_Q_LEVEL = 0.05
R8_PREQUENTIAL_PREDICT = False                 # tau_ARF only; predict_one intentionally omitted
R8_PARITY_T_DRIFT = 4000                       # S7/G1: warm-up parity sweep, written alongside 2000

# ══════════════════════════════════════════════════════════════════════════════
# R9 — critical ensemble size M_crit
# ══════════════════════════════════════════════════════════════════════════════
R9_N_STEPS = N_STEPS
R9_T_DRIFT = T_DRIFT
R9_N_MODELS = 1
R9_C_INT = C_INT
R9_C_EXT = C_EXT
R9_EXT_DELTA = EXT_DELTA
R9_DELTA_E_WINDOW = 500                        # pre/post window for the empirical Delta_e
R9_BOUNDARY_SHIFTS = BOUNDARY_SHIFTS
R9_SEEDS = SEED_SCHEME_NAIVE_1_100
R9_LAMBDAS = [8, 25, 50]
R9_DELTA_P = DELTA_P
R9_RELIABILITY_TARGETS = [0.99, 0.95, 0.50]    # S7/TASK 3: r = 1 - P_miss, replaces the beta letter
R9_DKW_ALPHA = 0.05
R9_TARGET_DELTAS = [0.10, 0.15, 0.20, 0.25, 0.33, 0.40, 0.50]


def require_drift_tracker(model, warning=False):
    """River private-attribute guard, shared by R1, R2, R6, R7, R8 and R9.

    Every instrumented experiment reads `model._drift_tracker` (and R9 also `_warning_tracker`) to
    time the internal tree swap. These are private and version-sensitive: a River other than the
    pinned 0.23.0 silently changes or drops them, which would turn a hard failure into a stream of
    NaN tau values. Fail loudly instead."""
    missing = [a for a in ("_drift_tracker",) + (("_warning_tracker",) if warning else ())
               if not hasattr(model, a)]
    if missing:
        raise RuntimeError(
            f"{type(model).__name__} missing {', '.join(missing)}: incompatible River version. "
            "Ensure River 0.23.0 is installed for proper internal tree swap tracking.")
    return model
