# S7 — Regeneration specification (written, not a mandate to execute)

Three items. G1 and G2 were **executed** under Phase −1 of stream S7; their specifications are
retained here as the definition of what was run. G3 is **specification only** — the five missing
tests are not implemented in this stream.

---

## G1 — R8 warm-up parity sweep (CRITICAL, F17)

**Defect.** `.tex` L411 juxtaposes `λ_op ≤ 12.4` (R8, `T_DRIFT = 2000`) and `λ ≥ 15` (the
`PageHinkley(threshold=15.0)` operating point of `exp_R4_main_table.py:162`, calibrated on ProteuS
streams with `n_steps = 8000`, `tp = 4000`) to assert an empty admissible set. `q05(τ_ARF)` and hence
`lambda_limit` depend on forest maturity at drift onset, so the two members are not commensurable.
See `config_matrix.md` §5.

**Specification.**

1. Re-run `exp_R8_lambda_op_sweep.py` with `t_drift = 4000` (`WARMUP 1000` + `DRIFT_GAP 3000`),
   `TOLERANCE = 50000` unchanged, `N_STEPS = t_drift + TOLERANCE`, everything else identical:
   `N_MODELS = 10`, `C_INT = 1`, `N_SEEDS = 200`, `DELTA_E_GRID = linspace(0.10, 0.50, 21)`,
   `DELTA_P = 0.005`, `Q_LEVEL = 0.05`, seed pool `SeedSequence(42).spawn(200)`.
2. Write **alongside** the 2000 output, never replacing it:
   `exp_R8_lambda_op_sweep_tdrift4000.csv`, `exp_R8_fine_grid_raw_tdrift4000.csv`.
3. Report `max(lambda_limit)` over `[0.20, 0.50]` at both warm-ups and state whether the
   `{λ ≤ λ_op} ∩ {λ ≥ 15}` intersection remains empty under the ProteuS-comparable warm-up.

**Executed.** Entry point: `python experiments/R8_lambda_op_sweep/exp_R8_lambda_op_sweep.py 4000`.
Result in `reconciliation_report.md` §4.

**Residual.** Full parity would require the R8 sweep to run on the ProteuS generator itself rather
than the Bernoulli boundary-shift stream. That is a manuscript-level change (Section III-E), out of
S7 scope.

## G2 — R1 λ-grid extension (closes the `λ* ≈ 15–25` interpolation)

**Defect.** `.tex` L195 (Figure 1 caption) states *"The transition `λ* ≈ 15–25` separates the
detector-wins, blind-spot (Zombie-dominated) and total-starvation regimes"*, and L419 repeats
`λ* ≈ 15–25`. The pre-S7 grid `LAMBDAS_TO_TEST = [2.5, 5, 10, 25, 50, 100]`
(`exp_R1_generate_data.py:25`) has **no point between 10 and 25**: the lower bound 15 was
interpolated across a factor-2.5 gap, not measured.

**Specification.** `LAMBDAS_TO_TEST = [2.5, 5.0, 10.0, 15.0, 20.0, 25.0, 50.0, 100.0]`, everything
else unchanged (`N_SEEDS = 200`, `DELTA_E = 0.25`, `N_STEPS = 54000`, `T_DRIFT = 4000`,
`DELTA_P = 0.005`, seed pool `SeedSequence(42).spawn(200)`). Because `run_diff_test(seed, λ)`
re-seeds per call, the pre-existing λ rows must be reproduced bit-for-bit; verify before accepting.

**Executed.** Result in `reconciliation_report.md` §4.

## G3 — Five missing non-regression tests (SPECIFICATION ONLY — not implemented)

Only `tests/test_R{6,7,8,9}.py` exist. Table I (R4) and Table II (R5), the two tables reviewers read,
have no test; nor do R1, R2, R3. Each test below reads the committed artifact only — no experiment
re-run — and must skip (never silently pass) with an explicit motive when the artifact is absent.

### `tests/test_R1_race_condition.py`
Artifact: `results/R1_race_condition/data/R1_race_condition.parquet`.
Assertions, against `.tex` L190 and the Figure 1 caption L195:
* `Share_Blind_Spot` at `λ = 25` == 0.88 ± 0.01 (Zombie-Alarm share).
* `Detection_Rate` at `λ = 25` > 0.95.
* Monotone regime ordering: `Share_Blind_Spot` at λ ∈ {2.5, 5, 10} < 0.10; == 1.00 at λ ∈ {50, 100}.
* λ* bracketing (post-G2): `Share_Blind_Spot(15) < Share_Blind_Spot(20) < Share_Blind_Spot(25)`.
* Row count == `len(LAMBDAS_TO_TEST) × 200`.

### `tests/test_R2_starvation.py`
Artifacts: `R2_instrumented_{A,B,C}_PHT_ARF.parquet`.
Assertions, against `.tex` L190, L210, L217:
* Scenario A (λ=50): overall detection rate < 0.01; pointwise miss rate == 1.00 at every Δe.
* Scenario B (λ=25): miss rate monotone non-decreasing for Δe ≥ 0.14 and == 1.00 for Δe ≥ 0.36.
* Scenario C (λ=8): miss rate < 0.05 for every Δe > 0.15 (the "safe zone" claim).
* Each parquet has exactly 2000 rows (100 seeds × 20 magnitudes).

### `tests/test_R3_crossover.py`
Artifact: `results/R3_regime_crossover/data/R3_regime_crossover_metrics.parquet`.
Assertions, against `.tex` L373, L375, L396, L402:
* `fp_mean(HT) / fp_mean(ARF)` ≈ 2.0 ± 0.1 (the "halving pre-drift false alarms" claim).
* `miss_mean(RF_Static)` == 0.0 at Δe = 0.50.
* `miss_mean(ARF)` == 100.0 at Δe = 0.50.
* `acc_mean(ARF) − acc_mean(RF_Static)` at Δe = 0.50 within ±0.5 pp of the manuscript's `~24 pp`
  (currently **23.41 pp** — see the reconciliation report, this assertion will fail against the
  prose value `~24` until L402/L413 are corrected).
* 45 rows = 15 magnitudes × 3 pipelines.

### `tests/test_R4_table1.py` (highest value — Table I)
Artifacts: `exp_R4_results_aligned_fusion.csv`, `exp_R4_seed_level_tests.csv`,
`exp_R4_results_KSWIN_alpha_sweep.csv`.
Assertions, against `.tex` L332–L357, L398–L400 and the Table I caption:
* Blind-spot collapse: `F1_mean == 0.00` exactly for `PHT + ARF|c=1`, `EDDM + ARF|c=1`,
  `SRP + PHT|c=1` in all three regimes; `ADD_mean` is NaN there.
* KSWIN resolution: `F1_mean == 1.00` and `ADD_mean == 14.0` with zero variance for
  `KSWIN + ARF` at c ∈ {1, 32}, all regimes; α-sweep keeps `F1 == 1.00` for α ∈ {0.001, 0.005, 0.01, 0.05}.
* Clock artefact: `ADD_mean == 31.0` with zero variance for `ADWIN + ARF|c=32`;
  `ADD_mean ≈ 9` for `ADWIN + ARF|c=1`.
* Safe configurations: `F1_mean ≥ 0.75` for `PHT + HT`, `≥ 0.80` for `ADWIN + HT`, all regimes.
* Static RF: `F1_mean` from 0.73 (IID) to 0.96 (Cal. B) for `PHT + RF (Static)`.
* Seed-level counts, exactly: `PHT+ARF c=1` 0/1080 vs `PHT+HT` 932/1080; `EDDM+ARF c=1` 0/1080 vs
  `EDDM+HT` 882/1080; `SRP+PHT c=1` 0/1080 vs 932/1080; `KSWIN+ARF c=1` 1080/1080 vs 0/1080;
  `PHT+RF` 913/1080; `ADWIN+RF` 959/1080 vs `ADWIN+ARF c=1` 1063/1080. All `sign_test_p < 2.1e-9`.
* Shape: 16200 rows = **15** pipelines × 3 regimes × 12 transitions × 30 seeds (note: 15, not the 14
  displayed — see `config_matrix.md` §6).

### `tests/test_R5_table2.py` (Table II + flooding)
Artifacts: `table2_values.csv`, `flooding_decomposition.parquet`, `delta_e.parquet`.
Assertions, against `.tex` L388 and the Table II caption:
* `delta_e` per variant: BAF |Δe| < 0.005 (all three); INSECTS abrupt 0.074, gradual 0.450,
  reoccurring 0.391, each ± 0.005.
* Per-jump abrupt vector == `[0.6801, -0.1474, 0.2448, -0.2717, -0.1341]` ± 1e-3 (the manuscript's
  `{0.68, −0.15, 0.24, −0.27, −0.13}`).
* Flooding, `gradual_balanced`: `pht_ht` `n_alarms == 7.0`, `precision ≈ 0.1429`;
  `pht_arf_c1` `n_alarms ≈ 85.667` (→ 86), `precision ≈ 0.0120`.
* Ratios: gradual `ratio == 10.57 ± 0.01`, reoccurring `1.61 ± 0.01`; both `sign_test_p < 2.1e-9`.
* `detection_genuine` is False for `gradual_balanced / pht_arf_c1` and True for
  `gradual_balanced / pht_ht` (the flooding-vs-genuine discriminator of Section IV-C).
