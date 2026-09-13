# S7 / TASK 4 — Experimental configuration matrix (R1..R9)

Source of truth: the module-level constants of `experiments/**/*.py` as of the S7 baseline
(`results/audit_S7/_baseline/constants_pre.json`, AST parse, no import, no execution).
Every cell below is quoted with its `file:line` provenance. No value is inferred.

---

## 1. Stream / timing / ensemble

| Exp | script | `N_STEPS` | `T_DRIFT` | post-drift horizon | warm-up | `N_MODELS` |
|-----|--------|-----------|-----------|--------------------|---------|------------|
| R1 | `exp_R1_generate_data.py:21-23` | 54000 | 4000 | 50000 (tolerance) | 1000 steps of pre-drift error buffer (`:70-71`) | 10 (`:50`) |
| R2 | `exp_R2_instrumented_blind_spot.py:34` | 8000 | 4000 | 4000 | 1000 steps of pre-drift error buffer (`:82-84`) | 10 |
| R3 | `exp_R3_regime_crossover.py:35-38` | 8000 | 4000 (`DRIFT_TIME`) | `TOLERANCE = 1000` scoring window | none (PHT armed from t=0) | 10 (`:74`, `:77`) |
| R4 | `exp_R4_main_table.py:72`, `:195` | 8000 (`n_steps`) | 4000 (`tp`) | `tau = max(1000, w)` | none (detector armed from t=0) | 10 (`:174`, `:176`, `:180`) |
| R5 BAF | `exp_R5_config.py:36-38` | full stream (~1e6) | 7 canonical positions `[125000 … 875000]` | `BAF_TAU_TOL = 5000` | `BAF_WARMUP = 100000` | `ARF_N_MODELS = 10` (`:87`) |
| R5 INSECTS | `exp_R5_config.py:44-47`, `exp_R5_common.py:22-29` | full stream (52847 / 24149 / 79985) | canonical positions (`:53-57`) | `min(5000, 0.05·n)` → 2642 / 1207 / 3999 | `min(100000, 0.10·n)` → 5284 / 2414 / 7998 | 10 |
| R6 | `exp_R6_generate_data.py:28` | 8000 | 4000 | 4000 | none | **1** (single HAT) |
| R7 | `exp_R7_generate_data.py:29` | 8000 | 4000 | 4000 | none | 10 |
| R8 | `exp_R8_lambda_op_sweep.py:34-38` | 52000 | 2000 (`WARMUP 1000` + `DRIFT_GAP 1000`) | `TOLERANCE = 50000` | 1000 (`WARMUP`) | 10 |
| R9 | `exp_R9_generate_data.py:25-26` | 8000 | 4000 | 4000 | `DELTA_E_WINDOW = 500` pre/post error window | **1** (single HAT) |

## 2. Seed scheme and magnitude grid

| Exp | seed scheme | n seeds | magnitude / parameter grid |
|-----|-------------|---------|----------------------------|
| R1 | `SeedSequence(42).spawn(200)` → `generate_state(1)[0]` (`:121-122`) | 200 | `LAMBDAS_TO_TEST = [2.5, 5, 10, 25, 50, 100]` at fixed `DELTA_E = 0.25` (`:24-25`) |
| R2 | naive `range(1, 101)` (`:39`) | 100 | `BOUNDARY_SHIFTS = linspace(0.1, 4.0, 20)` (`:35`) × 3 scenarios λ ∈ {50, 25, 8} (`:54-58`) |
| R3 | naive `range(0, 100)` (`:126`) | 100 | `DELTA_E_VALUES = linspace(0.02, 0.50, 15)` (`:39`) × 3 pipelines |
| R4 | `SEEDS = list(range(1, 31))` (`:47`); bootstrap `BOOTSTRAP_SEED = 12345` (`:48`) | 30 | 12 transitions (`permutations(TICKERS, 2)`, `:67`) × `w ∈ {100, 500, 1000}` (`:68`) × 3 GARCH regimes |
| R5 | `SeedSequence(42).spawn(30)` mod `2**31-1` (`exp_R5_common.py:16-19`) | 30 | 3 BAF variants + 3 INSECTS variants × 3 pipelines |
| R6 | naive `range(1, 101)` (`:30`) | 100 | `BOUNDARY_SHIFTS = linspace(0.1, 4.0, 20)` (`:29`) |
| R7 | naive `range(1, 101)` (`:31`) | 100 | `linspace(0.1, 4.0, 20)` × 3 clock scenarios (`:34-38`) |
| R8 | `SeedSequence(42).spawn(200)` (`:83-84`) | 200 | `DELTA_E_GRID = linspace(0.10, 0.50, 21)` (`:43`) |
| R9 | naive `range(1, 101)` (`:29`) | 100 | `linspace(0.1, 4.0, 20)` (`:28`); downstream `TARGET_DELTAS = [0.10, 0.15, 0.20, 0.25, 0.33, 0.40, 0.50]` × `LAMBDAS = [8, 25, 50]` (`exp_R9_compute_mcrit.py:21-25`) |

R1, R5 and R8 use `SeedSequence`; R2, R3, R6, R7, R9 use a naive integer range, and R4 uses `1..30`.
The naive ranges are documented in-source as deliberate ("AE Visual Match", `exp_R2:37-39`, `exp_R3:124-125`)
to reproduce the submitted streams bit-for-bit.

## 3. Detector pinning — internal (ARF) and external

| Exp | ARF `drift_detector` | ARF `warning_detector` | external monitor | ADWIN `delta` | CUSUM / PHT threshold | `DELTA_P` |
|-----|----------------------|------------------------|------------------|---------------|-----------------------|-----------|
| R1 | `ADWIN(clock=1)` (`:55`) | **`ADWIN(clock=1)` pinned** (`:55`) | **two arms**: nominal `StrictCUSUM(0.05, DELTA_P, λ)` (`:56`) → `tau_det_fixed`; empirical `StrictCUSUM(p_pre_emp, DELTA_P, λ)` (`:81`) → `tau_det_emp`. **Every published aggregate is the empirical arm** | river default 0.002 | λ ∈ {2.5, 5, 10, 15, 20, 25, 50, 100} (S7/G2) | **0.01** ← `CUSUM_DELTA_P` (A1) |
| R2 | `ADWIN(clock=c_int)` (`:71`) | **pinned** `ADWIN(clock=c_int)` (`:71`) | **one arm**: `StrictCUSUM(p_pre_empirical, δ=`ssot.R2_CUSUM_DELTA`, λ)` (`:91`), `p_pre_empirical = np.mean(errors_pre)` (`:90`) over the 1000-step warm-up | river default 0.002 | λ ∈ {50, 25, 8} (`:58-60`) | 0.01 ← `CUSUM_DELTA_P` (A1 de-literalised `:91`) |
| R3 | `ADWIN(clock=1)` (`:78`) | **pinned since S7-ter** `ADWIN(delta=R3_WARN_DELTA, clock=R3_C_WARN)` = `(0.002, 1)`; was **river ARF default** `ADWIN(delta=0.01, clock=32)` | `PageHinkley(threshold=25.0, delta=0.005)` (`:85`, `:111`) | drift 0.002 (bare-ADWIN default); warning 0.002 since S7-ter, 0.01 before | 25.0 | 0.005 |
| R4 | `adwin(c)` = `ADWIN(delta=0.002, clock=c)` (`:166`, `:177`) | **pinned since S7-ter** `ADWIN(delta=R4_WARN_DELTA, clock=c)` = `(0.002, c)` for `make_arf`; `make_srp` (`:178-181`) already pinned both and is the pattern copied | `pht()` = `PageHinkley(threshold=15.0)`, `adwin(c)`, `EDDM()`, `kswin(seed)` = `KSWIN(alpha=0.005, window_size=100, stat_size=30)` (`:165-173`) | drift 0.002 (explicit); warning 0.002 since S7-ter, 0.01 before | PHT 15.0; KSWIN α=0.005 | PHT river default 0.005 (`:165` comment) |
| R5 | `ADWIN(clock=clock)` (`exp_R5_common.py:52-55`) | **pinned** `ADWIN(clock=clock)` (`:52-55`) | PHT with **bisection-calibrated** λ on the warm-up error stream, budget `PHT_TARGET_FA = 1` fallback 3 (`:59-85`), or `ADWIN(clock=clock)` (`:126`) | river default 0.002 | λ calibrated per (variant, seed), recorded in `lambda_calibrated` | `PHT_DELTA = 0.005` (`exp_R5_config.py:85`) |
| R6 | `ADWIN(clock=C_INT=1)` (`:41`) | **pinned** `ADWIN(clock=1)` (`:42`) | none (τ_HAT only) | river default 0.002 | — | — |
| R7 | `ADWIN(clock=c_int)` (`:49`) | **pinned** `ADWIN(clock=c_int)` (`:50`) | `ADWIN(delta=EXT_DELTA, clock=c_ext)` (`:51`) | internal river default 0.002 / **external `EXT_DELTA = 0.002`** (`:32`) | — | — |
| R8 | `ADWIN(clock=C_INT=1)` (`:56`) | **pinned** `ADWIN(clock=1)` (`:57`) | none simulated; nothing accumulates | river default 0.002 | — (λ_limit **purged** by A2) | **none** — `R8_DELTA_P` removed by A2 |
| R9 | `ADWIN(clock=C_INT=1)` (`:38`) | **pinned** `ADWIN(clock=1)` (`:39`) | `ADWIN(delta=0.002, clock=C_EXT=32)` (`:40`) | 0.002 explicit external | downstream `LAMBDAS = [8, 25, 50]` | **0.01** ← `CUSUM_DELTA_P` (A1) |

**Action S7-ter/D-3 — R1 carries two external CUSUM arms; R2 carries one.** Escalated during the
stream and verified in source and against the frozen artifact, read-only — R1 was neither touched nor
re-run.

| | R1 nominal | R1 empirical | R2 |
|---|---|---|---|
| construction | `StrictCUSUM(0.05, DELTA_P, λ)`, `exp_R1_generate_data.py:56` | `StrictCUSUM(p_pre_emp, DELTA_P, λ)`, `:81` | `StrictCUSUM(p_pre_empirical, R2_CUSUM_DELTA, λ)`, `exp_R2:91` |
| `p_0` | literal **0.05**, fixed before the stream starts | mean error over the 1000-step pre-drift warm-up (`:79`) | idem (`exp_R2:90`); the literal 0.05 is a fallback reachable only on an empty warm-up buffer |
| column | `tau_det_fixed` | `tau_det_emp` | — |
| read by | **nothing** | `blind_spot_observed` (`:106-111`), `tau_det_emp_finite` (`:120`), Figure 1 (`exp_R1_plot_figure.py:37-40`) | everything |
| at λ = 25 | detection 0.390, blind-spot share 0.965 | detection **0.920**, blind-spot share **0.895** | — |

**Every published R1 numeral is the empirical arm.** Proof, obtained by recomputing the generator's
own blind-spot rule (`:106-111`) column by column on the frozen parquet: the stored
`blind_spot_observed` reproduces the empirical-arm recomputation exactly on all eight λ, and the
nominal-arm recomputation on none. The nominal arm's `p_0 = 0.05` sits far above the measured
pre-drift error rate, so that arm accumulates only on a much larger excess and starves earlier —
which is why its detection rate at λ = 25 is less than half the empirical arm's. The escalation
records this extra slack as an effective tolerance of 0.036; that figure is **not derivable from the
committed artifact**, which stores no `p_pre_emp` column, and verifying it would require re-running
R1, which is out of scope by instruction. It is recorded as stated, not as measured.

R2 has no such ambiguity: one arm, warm-up-calibrated, and the later campaigns (R5, R8, S6) inherit
the same convention.

**Action A1 — δ_P is two quantities, not one contested value.** The manuscript states both, each for
its own detector: the fixed-`p_0` StrictCUSUM of `eq:cusum` at `\DeltaPtext = 0.01` (`.tex` L277),
and River's adaptive mean-tracking PageHinkley at 0.005 (`.tex` L480, named there as explicitly
distinct from `eq:cusum`). `config/experiment_ssot.py` now carries one name per family:
`CUSUM_DELTA_P = 0.01` (R1, R2, R9, S6 audit) and `DELTA_P = 0.005` (R3, R4, R5). R1 and R9 were
reading the PageHinkley tolerance for a StrictCUSUM quantity and are regenerated; R3/R4/R5 were
already correct and are untouched, artifact hashes unchanged. The S6 campaign traces stay at 0.005 —
a recorded property of the committed Parquet, re-accumulated post hoc at 0.01 by
`s6_recompute_cusum_delta001.py`, which is where every published S6 numeral comes from.

**Action A2 — R8 requalified, not retired.** The plan's three options (removal, historical annex,
repointing the test at `envelope_stats.json`) all rest on R8 being dead. It is not: `q05_tau_arf`
supplies four live numerals to `.tex` L395 — the plateau at 12.95 for Δe ≤ 0.16 at
`T_drift = 2000`, and its dissolution to 25.70 / 30.95 / 54.70 / 54.70 at `T_drift = 4000`. That
pair is the refutation of the noise-driven-swap reading, so removing R8 would orphan a current
result. What was dead is one column: `lambda_limit`, the rectangular surrogate withdrawn at
`.tex` L385, whose target values (4.2, 12.4) have zero occurrences in the manuscript of record.
The column and `R8_DELTA_P` are purged, the two aggregation artifacts regenerated, and the test
repointed onto what the sweep actually establishes — including the `_tdrift4000` arm, which was
cited by the manuscript and guarded by nothing.

**Action S7-ter/B-1 — the delta column conflated two River defaults.** The column above read
"river default 0.002" for every ARF-internal cell, which is the default of a **bare** `drift.ADWIN()`.
It is not what an unset `ARFClassifier` detector resolves to. Measured on the pinned build:

| construction | delta | clock |
|---|---|---|
| `ARFClassifier(...)` unset `drift_detector` | **0.001** | 32 |
| `ARFClassifier(...)` unset `warning_detector` | **0.01** | 32 |
| `drift.ADWIN()` | **0.002** | 32 |

So R3 and R4 ran their warning detector at `delta = 0.01`, not at 0.002, and the unification onto the
drift configuration moves **two** parameters — `0.01 → 0.002` and `32 → c` — not the clock alone.
Every cell whose `drift_detector` is explicitly constructed (all of them) was unaffected by the
conflation; only the warning column was, and only for R3 and R4, the two experiments that left it
unset.

### README §5 verdict — verified in source, then superseded by the unification

`README.md:291` claimed: *"in R1, R2 and R5 the ARF pins both its internal `drift_detector` and
`warning_detector`… In R3 and R4 only the `drift_detector` is pinned."*

**The claim was accurate when written**, and is verified line by line: R1 `:50`, R2 `:67`,
R5 `exp_R5_common.py:52-55` pin both; R3 and R4's `make_arf` pinned only `drift_detector`.

Two additions the README omitted, recorded here:

1. `exp_R4_main_table.py:178` — `make_srp` pins **both** detectors for the SRP model. R4 was therefore
   not uniformly "drift_detector only": it was drift-only for ARF, both for SRP, in the same file.
2. R6, R7, R8 and R9 all pin **both** detectors and were outside README §5's enumeration entirely.

Since S7-ter/B-1 the heterogeneity is gone: the three sites that left the warning unset
(`exp_R3_regime_crossover.py`, `exp_R4_main_table.make_arf`, `exp_R4_kswin_sweep.make_arf`) now pin it
onto the drift configuration, and `README.md` §5 is rewritten accordingly.

## 4. Non-regression test coverage (amendment G3)

| Exp | manuscript object produced | non-regression test |
|-----|---------------------------|---------------------|
| R1 | Figure 1 (race condition), Zombie-Alarm 88 % / detection 96.5 % (`.tex` L190) | **no** |
| R2 | Figures 2A–2C, τ_ARF power law, starvation rates (L190, L210, L217) | **no** |
| R3 | Figure 3 (regime crossover), RF resolution (L373–L377, L396, L402) | **no** |
| R4 | **Table I** + KSWIN α-sweep, all of Section IV-B (L332–L357, L398–L400) | **no** |
| R5 | **Table II** + flooding decomposition, Section IV-C (L388) | **no** |
| R6 | Hydra factor, `K_HAT`/`K_ARF`, `α_HAT`/`α_ARF` (L150, L217, L222, L312) | yes — `tests/test_R6_hydra.py` |
| R7 | Regime-1 clock matrix (L201) | yes — `tests/test_R7_regime1.py` |
| R8 | `λ_op` bound of Definition 11 (L295, L411) | yes — `tests/test_R8_lambda_op.py` |
| R9 | `M_crit` worked example (L276) | yes — `tests/test_R9_mcrit.py` |

**Finding (G3).** The two tables reviewers actually read — Table I (R4) and Table II (R5) — carry
**no** non-regression test, and neither do R1, R2 and R3. The five missing test specifications are
written to `results/audit_S7/regeneration_spec.md` (not implemented in this stream).

## 5. CRITICAL divergence — R1/R8 warm-up parity (F17, amendment G1)

> `.tex` L411: *"On heteroscedastic streams, guaranteeing reliable detection caps the CUSUM threshold
> ($\lambda_{\mathrm{op}} \le 12.4$), whereas controlling GARCH-induced false alarms requires
> $\lambda \ge 15$. This empty admissible set ($\{\lambda \le 12.4\} \cap \{\lambda \ge 15\}$) forces
> a choice among three architectural fixes:"*

The two members of this prescriptive inequality are produced under **different pre-drift warm-up**:

| member | provenance (exact) | pre-drift warm-up |
|--------|--------------------|-------------------|
| `λ_op ≤ 12.4` | R8. `max(lambda_limit)` over `Δe ∈ [0.20, 0.50]` = **12.438** at `Δe = 0.22` (`results/R8_lambda_op_sweep/data/exp_R8_lambda_op_sweep.csv`) | `T_DRIFT = 2000` = `WARMUP 1000` + `DRIFT_GAP 1000` (`exp_R8_lambda_op_sweep.py:34-37`) |
| `λ ≥ 15` | **not an R1 measurement.** It is the PHT operating threshold `PageHinkley(threshold=15.0)` of `exp_R4_main_table.py:162`, documented at `.tex` L362 footnote as *"calibrated against ProteuS pre-drift volatility to allow at most one false alarm per warm-up window"* | R4/ProteuS: `n_steps = 8000`, `tp = 4000`, detector armed from `t = 0` (`exp_R4_main_table.py:72`, `:124-138`) |

`τ_ARF` depends on forest maturity, hence so do `q05(τ_ARF)` and `lambda_limit`. Comparing a bound
measured on a 2000-step-warm-up forest (R8) against a threshold calibrated on an 8000-step ProteuS
stream with drift at 4000 (R4) is a **warm-up parity defect**: the "empty admissible set" is asserted
across two non-commensurable calibrations.

Second, `12.438 > 12.4` strictly: the manuscript's `λ_op ≤ 12.4` holds only at the stated one-decimal
precision. `.tex` L295 states it as *"never exceeds 12.4"*, which is false at full precision.

**Not corrected here.** The correction requires an R8 sweep at ProteuS-comparable warm-up or a
sensitivity analysis. Specification written to `results/audit_S7/regeneration_spec.md`; an R8 second
sweep at `T_DRIFT = 4000` was executed under Phase −1 and is reported in
`results/audit_S7/reconciliation_report.md`.

## 6. Second finding — R4 pipeline count comment

`exp_R4_main_table.py:183` comments `"14 Pipelines per (transition, seed)"`, and `:378` prints
`"14 pipelines"`. `process_transition_seed` emits **15** `rec(...)` calls per regime:
3 HT baselines + 6 ARF (3 detectors × c ∈ {1,32}) + 2 SRP + 2 KSWIN + 2 static RF.
Confirmed in the artifact: `exp_R4_results_aligned_fusion.csv` holds 16200 rows
= 15 pipelines × 3 regimes × 12 transitions × 30 seeds, and contains an `EDDM + ARF` / `Clock = 32`
cell (F1 = 0.100 / 0.072 / 0.069) that `ROW_SPECS` (`:282-301`, 14 data rows) never renders.

The manuscript's *"14 configurations"* (L327) matches the **table**; the code comment is what is
wrong. Comment-only fix, no behavioural change — applied, diff in the reconciliation report.

## 7. S7-bis — the R4 registry hole: closed (option A), with its residue named

R4's registry values lived in `simulate_stream` argument defaults and in the detector/model
factories, i.e. outside the module-level `Assign` walk of `tests/test_S7_consistency.py`. Since R4
produces Table I, the table's constants were unprotected. Option A was taken: the diff is bounded to
one token per site.

**Routed to the SSOT (14 sites, all value-identical):**

| file | site | before | after |
|------|------|--------|-------|
| `exp_R1_generate_data.py` | ARF factory | `n_models=10` | `ssot.R1_N_MODELS` |
| `exp_R3_regime_crossover.py` | ARF factory | `n_models=10` | `ssot.R3_N_MODELS` |
| `exp_R3_regime_crossover.py` | Bagging factory | `n_models=10` | `ssot.R3_N_MODELS` |
| `exp_R3_regime_crossover.py` | PHT construct ×2 | `threshold=25.0` | `ssot.R3_PHT_LAMBDA` |
| `exp_R4_main_table.py` | `simulate_stream` defaults | `n_steps=8000, tp=4000` | `ssot.R4_N_STEPS`, `ssot.R4_T_DRIFT` |
| `exp_R4_main_table.py` | `pht()` | `threshold=15.0` | `ssot.R4_PHT_LAMBDA` |
| `exp_R4_main_table.py` | ARF / SRP / Bagging factories | `n_models=10` | `ssot.R4_N_MODELS` |
| `exp_R4_kswin_sweep.py` | `simulate_stream` defaults | `n_steps=8000, tp=4000` | `ssot.R4_N_STEPS`, `ssot.R4_T_DRIFT` |
| `exp_R4_kswin_sweep.py` | ARF factory | `n_models=10` | `ssot.R4_N_MODELS` |

Two new derived constants were declared for this: `R1_N_MODELS = N_MODELS` and
`R3_N_MODELS = N_MODELS`.

**Guard extended.** `tests/test_S7_consistency.py` now also walks function-argument defaults and
call keywords, and fails when a guarded registry parameter — `n_steps`, `tp`, `t_drift`,
`n_models`, `threshold` — is bound to a bare literal. Only an `ast.Constant` is a violation: a
`Name`/`Attribute` default resolves to a module-level constant, which the existing module-level walk
already covers, so `run_tau_arf(t_drift=T_DRIFT)` (R8) is not a false positive.

**DECLARED UNGUARDED PERIMETER (option B applied to the remainder, not silence).** The following
registry-adjacent literals remain outside the guard, because their parameter names are generic
enough that guarding them would fire on River's own API surface:

| site | literal | SSOT reference that declares it |
|------|---------|---------------------------------|
| `exp_R3_regime_crossover.py:78` | `drift.ADWIN(clock=1)` | `R3_C_INT` |
| `exp_R3_regime_crossover.py:78` | `drift.ADWIN(clock=R3_C_WARN, delta=R3_WARN_DELTA)` — **routed**, no literal | `R3_C_WARN`, `R3_WARN_DELTA` (S7-ter) |
| `exp_R4_main_table.py`, `exp_R4_kswin_sweep.py` | `drift.ADWIN(delta=R4_WARN_DELTA, clock=c)` — **routed**, no literal | `R4_WARN_DELTA` (S7-ter) |
| `exp_R3_regime_crossover.py:85, :111` | `PageHinkley(delta=0.005)` | `R3_DELTA_P` |
| `exp_R4_main_table.py`, `exp_R4_kswin_sweep.py` | `drift.ADWIN(delta=0.002)` | `R4_ADWIN_DELTA` |
| `exp_R4_main_table.py` | `drift.KSWIN(alpha=0.005)` | `R4_KSWIN_ALPHA` |
| `exp_R4_*.py`, `exp_R9_compute_mcrit.py` | `seed=42` | not a registry name (a fixed nuisance seed) |

R5 is unaffected: `exp_R5_config.py` already routes its registry through `config/experiment_ssot.py`.
