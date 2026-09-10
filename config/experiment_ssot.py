# experiment_ssot.py
"""Single source of truth for the experimental constants of "The Blind Spot Paradox" (ICDM 2026).

Form generalised from `experiments/R5_real_world_evaluation/exp_R5_config.py`: dynamic `ROOT_DIR`,
named module-level constants, no experiment logic. The only callable is the River private-attribute
guard, shared by every script that instruments `_drift_tracker` / `_warning_tracker`.

Registry (S7/CONFIG §6): N_STEPS, T_DRIFT, CENSORING_HORIZON, N_MODELS, SEED_SCHEME,
BOUNDARY_SHIFTS, DELTA_E_GRID, C_INT, C_EXT, EXT_DELTA, DELTA_P, LAMBDAS, WARMUP_WINDOW,
DELTA_E_WINDOW, N_SEEDS_REAL, TAU_TOL.

Intentional per-experiment divergences are DERIVED CONSTANTS carrying an `R<n>_` prefix and a motive,
never local literals. Stream-scoped constants that belong to no single R<n> carry the stream prefix
instead (`S6_`), under the same rule. `tests/test_S7_consistency.py` walks every module-level assignment in
`experiments/**/*.py` and fails if a registry name is re-bound to a local literal, or if any resolved
value drifts from `results/audit_S7/_baseline/constants_pre.json`.

VALUE-PRESERVING BY CONSTRUCTION. No RNG call site, no draw ordering and no predict_one/learn_one
ordering is defined here: the two-`rng.normal()`-per-step invariant lives in the experiment loops and
is what makes the artifacts bit-comparable. The triple per-worker lock (`random.seed` +
`np.random.seed` + `default_rng`) is likewise left verbatim in each worker function -- it is required
by River's Cython tree-spawn path and must not be centralised or "cleaned up".

R4 (ProteuS) carried n_steps / tp / n_models / threshold in function defaults and call keywords,
outside the module-level AST walk. S7-bis routes those four to this module in R1, R3 and R4 and
extends the guard to argument defaults and call keywords. Still unguarded, by name and not by
silence: `clock`, `delta`, `alpha` and `seed` literals (R3:78 `clock=1`, R3 `delta=0.005`,
R4 `delta=0.002` / `alpha=0.005`, R4/R9 `seed=42`) -- generic parameter names whose guarding would
produce false positives across River's own API. R5 keeps its registry in `exp_R5_config.py`, which
already routes through this module.
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
R1_N_MODELS = N_MODELS
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
R3_N_MODELS = N_MODELS
R3_PHT_LAMBDA = 25.0
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


# ══════════════════════════════════════════════════════════════════════════════
# S6 — synchronized traces (F6 / F7 / F25). Phase 0 = verification gates G0..G3.
# ══════════════════════════════════════════════════════════════════════════════
# S6 adopts the canonical family (R2/R6/R7/R9) rather than the R1/R8 timing: the triple per-worker
# RNG lock and the 8000/4000 split are the configuration under which the manuscript's tau_ARF
# figures were produced, and F7 needs a bounded post-drift window that every run reaches, not an
# early break at the first swap.
S6_N_STEPS = N_STEPS
S6_T_DRIFT = T_DRIFT
S6_CENSORING_HORIZON = CENSORING_HORIZON       # 4000 post-drift steps, traced without early break:
                                               # F6 requires every per-tree swap, not min_i tau_i
S6_N_MODELS = N_MODELS
S6_C_INT = C_INT
S6_C_EXT = C_EXT
S6_SEED_MASTER = SEED_SCHEME_SEEDSEQ_ENTROPY   # np.random.SeedSequence(42).spawn(n)

# Phase-0 gate grid. The three magnitudes are R8's OVERLAP_REF anchors (weak / mid / strong band).
S6_GATE_N_SEEDS = 50
S6_GATE_DELTA_E = [0.10, 0.25, 0.40]
S6_G1_FORK_T_REL = 100                         # deepcopy taken at t_rel = +100 post-drift
S6_G1_FORK_HORIZON = 500                       # identical steps replayed on original and fork
S6_G3_BENCH_STEPS = 10_000

# Phase-1 campaign shape, declared here so G3 extrapolates a stated design and not a guess.
# 2x2 factorial (M, ADWIN clock): the Hydra factor (R6) crossed with the clock mismatch (R7).
S6_ARMS = ((N_MODELS, C_INT), (N_MODELS, C_EXT), (R6_N_MODELS, C_INT), (R6_N_MODELS, C_EXT))
S6_CAMPAIGN_BOUNDARY_SHIFTS = BOUNDARY_SHIFTS  # 20 magnitudes, canonical family
S6_CAMPAIGN_SEEDS = SEED_SCHEME_NAIVE_1_100    # 100 seeds, canonical family

# --- Phase 1: harness, causal arms and stopping definitions --------------------------------------
S6_ARM_NAMES = ("full", "no_swap", "frozen", "static")
# 'full'    nominal ARF.
# 'no_swap' deepcopy fork at tau_swap^(1/M); both internal detector paths made inert. Learning
#           continues, replacements cease. River draws the Poisson weight BEFORE the detector blocks
#           and the blocks themselves consume no entropy, so making them inert removes no draw: the
#           branch diverges from 'full' only through the tree structures the suppressed replacements
#           would have produced, which is the effect under study.
# 'frozen'  same fork, learn_one no longer called.
# 'static'  ensemble.BaggingClassifier(HoeffdingTreeClassifier, M) -- the non-adaptive reference of
#           R3 ("Static Bagging without internal ADWIN tree resets").
S6_WARMUP_WINDOW = R2_WARMUP_WINDOW            # 1000 pre-drift steps calibrate e_pre and the CUSUM
                                               # p_pre, the R1/R2 convention
S6_ERR_WINDOW = 200                            # W, rolling recovery estimate. R4 smooths the error
                                               # over 30 with a W/2 lag; 200 is the width at which
                                               # the rolling-mean noise floor sqrt(p(1-p)/W) ~ 0.015
                                               # stays under rho * Delta_e at the weak anchor
S6_ERR_HYSTERESIS = S6_ERR_WINDOW // 2         # H = W/2 consecutive steps under the threshold
S6_RHO_GRID = [0.50, 0.25, 0.10]               # residual fraction of the empirical Delta_e
S6_Q_GRID = [0.1, 0.25, 0.5, 1.0]              # fraction of DISTINCT trees replaced; 0.1 == 1/M
S6_T_HORIZON = R3_TAU_TOL                      # T_h = 1000, the post-drift scoring window of R3
S6_TRACE_PRE = S6_WARMUP_WINDOW                # traced window = [t_drift - 1000, t_drift + 4000)
S6_TRACE_POST = CENSORING_HORIZON
S6_SMOKE_N_SEEDS = 5
S6_SMOKE_DELTA_E = S6_GATE_DELTA_E             # same three anchors the Phase-0 gates used

# Deterministic Parquet contract. Every value is pinned: a byte-different artifact on replay is a
# defect, and tests/test_S6_traces.py is the oracle.
S6_PARQUET_COMPRESSION = "zstd"
S6_PARQUET_COMPRESSION_LEVEL = 9
S6_PARQUET_VERSION = "2.6"
S6_PARQUET_ROW_GROUP = 100_000
S6_PARQUET_PARTITION_FMT = "{:.6f}"            # delta_e -> hive directory name


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
