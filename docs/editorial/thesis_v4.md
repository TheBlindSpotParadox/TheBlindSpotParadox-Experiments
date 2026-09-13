# Thesis v4 — inventory, title, abstract, contributions, Table I framing, terminology

Stream S11-a. This document measures nothing and edits no section of the manuscript. It is the
scaffolding the v65 assembly applies.

Manuscript of record read through `docs/manuscript/CURRENT`
(`articleA_blindspot_v64_camera_ready.tex`, 576 lines after the S-SYNC pass), never through the
PDF. Entry gate verified: `docs/editorial/sync_pass_report.md` exists (22,238 bytes, pass of
2026-09-13).

**The statement this document carries.** Cumulative-evidence monitors are not condemned by
coupling. The published failures are threshold facts: a monitor calibrated on an open stationary
stream and deployed on a closed-loop one asks for more evidence than the loop leaves, at every
operating point this repository measures. The blind spot is the region where the budget an
adaptation leaves falls below the requirement a calibration sets, and both sides of that
comparison are measured here in one unit.

---

## T11a.1 — Inventory of publishable claims

One row per publishable claim. No row without a numeral and an artifact key. `status`:
`PUBLISHED` — already in the manuscript and reproduced from the artifact; `UNPUBLISHED` — measured
and committed, not yet carried by the manuscript; `ARCHIVED ABLATION` — measured, published arm is
elsewhere; `NOT SIGNIFICANT` — measured and carried, but does not survive the declared multiple
testing correction.

### (a) The framework quantities: floor, ceiling, requirement

| claim | value | interval | artifact key | status |
|---|---|---|---|---|
| Detectability floor on drift magnitude | `Δe_c = 0.120` | `[0.114, 0.127]`, 95 % bootstrap, 10,000 draws, n = 300 seeds × 6 magnitudes | `results/S6_synchronized_traces/tables/delta_e_c_data_refine.json :: delta_e_c.interpolated.{estimate=0.119708, ci_lo_2p5=0.11392, ci_hi_97p5=0.12715}` | PUBLISHED (`\DeCrit`, `\DeCritCI`) |
| Operational threshold from the evidence-ceiling certificate | `λ_op = 21.93` | `[19.876, 22.398]`, 10,000 seed-level resamples, no replicate below `λ_FA = 15` | `results/S6_synchronized_traces/tables/envelope_stats.json :: lambda_op_bootstrap."0.20_0.40"` | PUBLISHED (`\LambdaOpNarrow`, `\LambdaOpNarrowCI`) |
| Untruncated envelope `[0.20, 0.50]` is not identified | `62.6 %` of replicates below `λ_FA` | point `15.2194`, `[14.60, 15.22]` | idem `:: lambda_op_bootstrap."0.20_0.50"` | PUBLISHED (`\WideEnvUnstable`) |
| Information-theoretic floor, chord form `eq:floor_chord` | `[13.9, 18.3]` | over the measured base-rate band `p₀ ∈ [0.015, 0.032]`; exact endpoints `13.87540995`, `18.28784093` | `results/S2_theory/tables/s2_gate_T20.json :: floor_and_family.floor_chord_interval` | PUBLISHED (`\FloorBand`) |
| Same floor under the χ² relaxation `eq:floor` | `1.80` at `p₀ = 0.024` | band `[1.52, 1.95]`; looseness factor `6.74` at the operating point | idem `:: floor_and_family.floor_chi2_interval` and `.floor_over_band[1].chi2_looseness_factor` | PUBLISHED (`\ChiLoose`) |
| Measured evidence ceiling, canonical point `Δe = 0.3268` | `33.51` | grid range `19.24`–`36.60`, factor `1.90`, non-monotone, argmax at `Δe = 0.1936` | idem `:: budget_restitution.measured` (`median max_t A_unrefl`, arm `full`, `runs.parquet:a_unrefl_peak`) | PUBLISHED |
| `R_CUSUM` at the published threshold `λ = 50` | `59.27` | at `α = 6.28e-16`, `ln(1/α) = 35.00` | idem `:: floor_and_family.family_requirements.common_alpha_ladder[3].R_CUSUM` | PUBLISHED |
| `R_CUSUM` at `λ_op = 21.93` — the ceiling clears it | `31.20` | `[29.15, 31.67]` across the `λ_op` interval | `results/S2bis_calibration/tables/s2bis_proteus_gate.json :: family_requirements_at_lambda_eq.per_couple["S6 measured lambda_op (c=0)"].R_CUSUM` | UNPUBLISHED |
| `R_KSWIN` at its deployed level | `22.68` | at `α = 0.005`, `n_stat = 30` | `s2_gate_T20.json :: floor_and_family.family_requirements.deployed_alphas.R_KSWIN_at_deployed_alpha` | UNPUBLISHED |
| `R_KSWIN` at the common level of a `λ = 50` CUSUM — does not clear the ceiling | `42.00` | at `α = 6.28e-16` | idem `:: common_alpha_ladder[3].R_KSWIN` | UNPUBLISHED |
| `R_ADWIN` at the same common level — does not clear the ceiling | `43.34` | idem | idem `:: common_alpha_ladder[3].R_ADWIN` | UNPUBLISHED |
| `R_CUSUM` price per unit of `ln(1/α)` | `1.468` | `= 1/θ*`, `θ* = 0.68129075` at `p₀ = 0.024` | `s2bis_proteus_gate.json :: cor_split_crossings.R_CUSUM_slope_per_unit_log_1_over_alpha` | UNPUBLISHED |
| `cor:split` crossing, CUSUM against KSWIN | `ln(1/α) = 16.34` | `λ = 22.605`, `R = 31.88` | idem `:: cor_split_crossings.crossings.R_KSWIN` | UNPUBLISHED |
| `cor:split` crossing, CUSUM against ADWIN | `ln(1/α) = 18.97` | `λ = 26.466`, `R = 35.74` | idem `:: cor_split_crossings.crossings.R_ADWIN` | UNPUBLISHED |

### (b) Calibration: the families are not read at a common false-alarm level

| claim | value | interval | artifact key | status |
|---|---|---|---|---|
| Equalising `α` at `λ = 15`: ADWIN is deployed tighter than a common requirement asks | `45×` | equalising `α = 9.041e-2` against deployed `δ = 0.002` | `s2bis_proteus_gate.json :: family_requirements_at_lambda_eq.per_couple["R4 deployed lambda_ref (c=0)"].equalising_alpha_ADWIN` | UNPUBLISHED |
| Equalising `α` at `λ = 15`: KSWIN is deployed looser | `4.5×` | equalising `α = 1.106e-3` against deployed `α = 0.005` | idem `.equalising_alpha_KSWIN` | UNPUBLISHED |
| Spread of the deployed levels at `λ = 50` | thirteen orders of magnitude | KSWIN `α = 0.005` against CUSUM `α ≈ 6.3e-16` | `s2_gate_T20.json :: floor_and_family.family_requirements.deployed_alphas.note` | UNPUBLISHED |

### (c) ProteuS (Table I): the collapse is a threshold

| claim | value | interval | artifact key | status |
|---|---|---|---|---|
| Pre-drift error rate on ProteuS is identically zero, both arms | median `0`, max `0` | over 2,160 runs (2 couples × 1,080) | `results/S2bis_calibration/tables/s2bis_proteus_eddm_arming.csv :: n_pre_drift_errors` | UNPUBLISHED |
| PHT + ARF(`c=1`) at `λ = 5` | `1080/1080` detected, `F1 = 1.0000`, `ADD = 6.05`, precision `1.000`, `0` false alarms | exact census over 1,080 runs | `results/S2bis_calibration/tables/s2bis_proteus_sweep.csv`, filter `Detector = "PHT + ARF"`, `Clock = 1`, `lambda = 5.0` | UNPUBLISHED |
| Same pipeline at `λ = 8` | `1063/1080`, `F1 = 0.9843`, `ADD = 9.08` | idem | idem, `lambda = 8.0` | UNPUBLISHED |
| Same pipeline at the deployed `λ = 15` | `0/1080`, `F1 = 0.0000` | idem | idem, `lambda = 15.0` | PUBLISHED |
| Evidence ceiling of the ARF at `c_int = 1` on ProteuS | in `(8, 15]` | bracket resolution is the ladder's | `docs/theory/transfer_S2bis.md` §2.7 (v), read off the same sweep | UNPUBLISHED |
| EDDM + ARF(`c=1`) never arms | `100 %` of 1,080 runs unarmed; `warm_start = 30` required | total errors over the 8,000 steps: median `9`, range `[6, 12]` | `s2bis_proteus_gate.json :: eddm_arming_T_D.per_couple[0]`; `s2bis_proteus_eddm_arming.csv :: n_errors_total` | UNPUBLISHED |
| EDDM + HT(`c=1`), same diagnostic | detection rate `0.819`, arming lag after the change median `30` | `17.7 %` of runs never armed | idem `.per_couple[1]` | UNPUBLISHED |
| Seed-level separation, PHT+ARF(`c=1`) against PHT+HT | `0/1080` against `932/1080` | 30/30 seeds, `p = 2⁻²⁹` | `results/R4_proteus_evaluation/data/exp_R4_seed_level_tests.csv` row 0 | PUBLISHED |
| SRP+PHT(`c=1`) against PHT+HT | `0/1080` against `932/1080` | idem | idem row 1 | PUBLISHED |
| KSWIN+ARF(`c=1`) against PHT+ARF(`c=1`) | `1080/1080` against `0/1080` | idem | idem row 2 | PUBLISHED |
| PHT+RF against PHT+ARF(`c=1`) | `913/1080` against `0/1080` | idem | idem row 3 | PUBLISHED |
| ADWIN+RF against ADWIN+ARF(`c=1`) | `959/1080` against `1070/1080` | idem, 30/30 seeds favour the ARF | idem row 4 | PUBLISHED |
| EDDM+ARF(`c=1`) against EDDM+HT | `0/1080` against `882/1080` | idem | idem row 5 | PUBLISHED (caption only) |
| Sign-test p-value on every one of the six contrasts | `p = 1.8626451e-9 = 2⁻²⁹` | the two-sided resolution floor at `n = 30`, not an estimate; report as `p ≤ 2⁻²⁹` | idem `:: sign_test_p`; `docs/editorial/S7ter_state_transfer.md` §3 item 6 | PUBLISHED, **wrong form** (see register) |
| ADWIN + ARF(`c = 32`) delay | `ADD = 31`, zero variance over 360 runs per cell | phase alignment, `eq:clock` | `docs/manuscript/tables/table1_proteus_summary.tex` | PUBLISHED |
| KSWIN + ARF delay | `ADD = 14 [0]` | structural smoothing lag `W/2 = 15`, bracket is lag-corrected | idem | PUBLISHED |

### (d) Flooding (Table II, INSECTS)

| claim | value | interval | artifact key | status |
|---|---|---|---|---|
| F1 ratio at the frozen warm-up calibration, `gradual_balanced` | `10.570` | `[9.354, 12.114]`, seed-paired bootstrap, 10,000 resamples | `results/S2bis_calibration/tables/s2bis_flooding_gate.json :: B3_headline.at_lambda_ref` | PUBLISHED (`\RhoRefMeas`) |
| Same ratio at the span budget | `1.270` | `[1.156, 1.426]`, verdict `COLLAPSE` (CI upper < 2) | idem `:: B3_headline.at_lambda_eq` | PUBLISHED (`\RhoEqSpan`, `\RhoEqSpanCI`) |
| Threshold-attributable share of `ln ρ`, `gradual_balanced` | `89.9 %` | both terms positive; residual `ln ρ_eq = +0.2387 [0.1451, 0.3550]` | idem `:: variants.gradual_balanced.decomposition_B4.share_threshold_attributable = 0.89878349` | PUBLISHED (`\ThresholdShare` = 90) |
| Armed pre-change span over warm-up, `gradual_balanced` | `4.8×` | warm-up 2,414 steps, armed span 11,614 | idem `:: variants.gradual_balanced.geometry` | PUBLISHED (`\SpanOverWarm`) |
| Thresholds the warm-up calibration hands each pipeline | ARF `20.97`, HT `132.50` | factor `6.3`; re-calibrated over the span: `93` and `186` | idem `:: identity_lambda_calibrated_is_lambda_eq_T_warm[2], [3]` | PUBLISHED (`\FloodLamArf`, `\FloodLamHt`, `\LamEqArf`, `\LamEqHt`) |
| No single share is reportable on the other two variants | terms differ in sign | `abrupt`: threshold `+0.190 [-0.013, +0.393]`, residual `-0.539`; `reoccurring`: `+0.726 [0.630, 0.825]`, residual `-0.247` | idem `:: variants.*.decomposition_B4` | UNPUBLISHED |
| Table II F1 ratios | `10.5703` (gradual), `1.6143` (reoccurring) | both at `p = 2⁻²⁹`, 30/30 seeds | `results/R5_real_world_evaluation/tables/table2_values.csv` | PUBLISHED |
| Table II, `abrupt_balanced` ratio | `0.7056` | `p = 0.0428`; Holm at `α = 0.05` over the 10-member family does **not** retain it (`α/2 = 0.025`) | idem; `S7ter_state_transfer.md` §3 item 5 | NOT SIGNIFICANT |
| Multiple-testing family size | `10` members, `8` at the `2⁻²⁹` floor | 6 R4 seed-level contrasts + 1 α-sweep + 3 INSECTS rows; the 3 BAF rows carry no test | `S7ter_state_transfer.md` §3 item 5 | UNPUBLISHED |

### (e) Erasure, Hydra, dilation

| claim | value | interval | artifact key | status |
|---|---|---|---|---|
| Share of post-fork erasure performed by incremental learning of the surviving trees | `99.3 %` | IQR `[0.987, 0.998]`, `n = 1979`; `E_learn 819.228` / `E_total 826.686` | `results/S6_synchronized_traces/data/s6_causal.json :: erasure_share_post_fork.a_pos_common.pooled` | PUBLISHED (`\LearnShare`) |
| Complement, replacements after the first | `0.7 %` | idem | idem | PUBLISHED |
| Evidence ceiling by arm, canonical point | full `31.3`, no_swap `41.1`, frozen `650` | medians of `S_max` | idem campaign; macros `\SixCeilingFull`, `\SixCeilingNoSwap`, `\SixCeilingFrozen` | PUBLISHED |
| Ceiling spread over the grid | full `6.58×` against frozen `133×` | `\FullSpreadGrid`, `\FrozenSpreadGrid` | idem | PUBLISHED |
| Detection leak when replacements after the first are suppressed | `18 %` at `λ = 50` against `0` nominal | `\NoSwapLeak` | idem | PUBLISHED |
| Crossing rate at `λ = 50`, nominal arm, envelope `[0.20, 0.50]` | `1/1600` | Clopper–Pearson 95 % upper `0.35 %`; Fisher homogeneity over 16 magnitudes, `p = 1.0` | `envelope_stats.json :: crossing_counts.envelope_homogeneity` | PUBLISHED (`\StarvFullK`, `\StarvFullN`, `\StarvFullUpper`) |
| Same rate, adaptation suspended at the first replacement | `≥ 99.4 %` | Clopper–Pearson 95 % lower | idem | PUBLISHED (`\StarvFrozenLower`) |
| Ceiling suppression across the envelope | `12×` at `Δe = 0.24` to `59×` at `Δe = 0.50` | monotone increasing in `Δe` | idem | PUBLISHED (`\SuppressLo`, `\SuppressHi`) |
| Ensemble acceleration, canonical point | `7.99×` measured | `[6.400, 9.719]`, restricted-mean ratio, censoring-aware lower bound | `results/S3/rho_meff.csv`, row `delta_e = 0.3268`, `hydra_rmst_ratio` | PUBLISHED |
| Same quantity predicted by the order statistics of `F̂_HAT` alone | `9.22×` | `4.83×` at `Δe = 0.1409` against `4.12×` measured | idem `:: accel_order_only` | UNPUBLISHED |
| Within-run inter-tree correlation | indistinguishable from zero | `ρ̂ ∈ [-0.0206, 0.0526]` over the 20-magnitude grid | idem `:: rho_hat_moments` | UNPUBLISHED |
| First-replacement ratio and elasticity | `τ_swap^(1)/τ_swap^(1/M) = 17.9`, elasticity `0.66` | `z = -14.9` against unity | `s6_causal.json`; `\SwapRatio`, `\SwapElasticity`, `\SwapElasticityZ` | PUBLISHED |
| Dilation ratio `κ` | `κ ≥ 1` in `1835/1836` runs, median `14.6` | all `2000` under the hysteresis estimator | `docs/manuscript/sections/framework_v2.tex`, `def:kappa`; `s6_causal.json` | UNPUBLISHED |
| First swap carries no recovery information in the weak band | Spearman `0.06` (`τ_err(0.50)`), `0.10` (`τ_err(0.10)`), `Δe ≤ 0.15` | pooled values `0.850` and `0.694` | `docs/theory/S6_causal_evidence.md` §2 | UNPUBLISHED |
| Exponential fit of `τ_HAT` rejected | 20/20 magnitudes | largest `p = 0.0030`, parametric bootstrap `N = 2000` | `results/S3/ks_exponentiality.csv` | PUBLISHED |

### (f) R3 crossover — published arm and archived ablation

| claim | value | interval | artifact key | status |
|---|---|---|---|---|
| Missed detections at `Δe = 0.50`, ARF | `100 %` | 100 streams per grid point; SEM `0.0` | `results/R3_regime_crossover/data/R3_regime_crossover_metrics.parquet`, `pipeline = ARF`, `delta_e = 0.50` | PUBLISHED (arm **U0**) |
| Safe zone, published arm | `[0.09, 0.25]` | miss `1 %` at `0.0886`, `0 %` at `0.1914` and `0.2257` | idem | PUBLISHED (arm **U0**) |
| Post-drift accuracy cost of the static RF at `Δe = 0.50` | `23.41 pp` | ARF `0.983956` against RF `0.749841` | idem | PUBLISHED (`23.4` pp in the `.tex`, arm **U0**) |
| Same three quantities under the unified ablation | `80 %`, safe zone from `0.12`, `22.99 pp` | idem geometry | `results/audit_S7/s7ter_arms/r3_u1/R3_regime_crossover_metrics.parquet` | ARCHIVED ABLATION (U1) |

The published arm is **U0** — River's own ARF defaults for the warning detector,
`ADWIN(delta=0.01, clock=32)`, pinned as `R3_WARN_DELTA_U0` / `R3_C_WARN_U0` — since `44cc572`.
`sync_pass_report.md` §2 declares the six U1 charges `VOID` and §5 verifies the sites intact. The
inventory carries U0 as the published value and U1 as an archived ablation, never the reverse.

### (g) BAF — the negative control, and the `0.0110` claim

The only row of this inventory that required a new artifact read. Read-only: no write under
`results/`, no campaign re-run, no hash touched.

| claim | value | interval | artifact key | status |
|---|---|---|---|---|
| Frozen-fork HT post-fork error, BAF Base | `0.010985555555555556` | point measurement over 900,000 rows | `results/R5_real_world_evaluation/data/delta_e_oracle.parquet`, column `err_mean_post_fork`, row `dataset = "baf"`, `variant = "Base"` | **REPRODUCED** |
| BAF Base fraud rate over the same window | `0.010985555555555556` | `data/baf/Base.csv.gz`, column `fraud_bool`, rows `[100000:]` (`BAF_WARMUP`) | equality **exact**, not to rounding | **REPRODUCED** |
| Frozen error / fraud rate, Variant I | `0.011005555555555555` / `0.011005555555555555` | idem | idem, `variant = "VariantI"` | **REPRODUCED** |
| Frozen error / fraud rate, Variant II | `0.010981111111111112` / `0.010981111111111112` | idem | idem, `variant = "VariantII"` | **REPRODUCED** |
| Adaptive HT post-fork error | Base `0.011142`, Variant I `0.011179`, Variant II `0.011112` | column `err_mean_post_fork_adaptive` | idem | REPRODUCED |
| Oracle `Δe` on the three BAF variants | `-0.000714`, `-0.000057`, `+0.000086` | every interval covering zero, `|Δe| < 0.001` | idem, columns `delta_e_mean`, `delta_e_ci_lo`, `delta_e_ci_hi` | PUBLISHED |

**Verdict on the `0.0110` claim of `PROMPT_S9.md:115`.** REPRODUCED, and on a stronger reading than
the one claimed. `0.0110` is the frozen model's post-fork error to four decimals on all three
variants, and it equals the BAF fraud rate over the identical window **exactly** — the frozen
Hoeffding tree is a pure majority-class predictor, so its error rate *is* the positive-class rate,
bit for bit, not to rounding. The claim is therefore closed, not carried as an audit debt.

One numeral of the same source does not reproduce on one variant and is recorded rather than
absorbed: `PROMPT_S9.md:115` states the adaptive tree at `0.0111`. Measured, `0.0111` on Base
(`0.011142`) and Variant II (`0.011112`), `0.0112` on Variant I (`0.011179`). The discrepancy is a
rounding of the third variant, it does not touch the negative-control argument, and it is listed in
`debt_register.md` for the record.

`err_mean_post_fork` is the mean of the frozen fork's error over `[BAF_WARMUP:]` with
`BAF_WARMUP = 100_000` (`experiments/R5_real_world_evaluation/exp_R5_compute_delta_e.py:112`,
`exp_R5_config.py:40`); the fraud rate above is computed over exactly that slice. `dtype` read as
committed: `float64` in the parquet, `int64` after `astype(int)` on `fraud_bool`.

### (h) Sweep of the `.tex` for publishable numerals not covered above

| claim | value | artifact key | status |
|---|---|---|---|
| Static-RF F1 range on ProteuS | `0.73 ± 0.05` (IID) to `0.96 ± 0.02` (Cal. B) | `docs/manuscript/tables/table1_proteus_summary.tex` | PUBLISHED |
| PHT + ARF(`c = 32`) F1 range | `0.61`–`0.68` | idem | PUBLISHED |
| Power-law fits | `τ_ARF ≈ 18.5 (Δe)^-0.98`, `τ_HAT ≈ 102 (Δe)^-1.02` | `results/R2_instrumented_blind_spot/data/`, `results/R6_hydra_factor/data/` | PUBLISHED |
| Race outcome at `λ = 50` | `P(τ_ARF < τ_det) = 1`, paired bootstrap `[1.00, 1.00]`, all 20 magnitudes, 2,000 runs | `results/S3/s3_competing_risks.json` | PUBLISHED |
| Plug-in refutation | the plug-in upper end falls below the Wilson 95 % lower end of measured `P_miss` in `10` of `80` cells | idem; `results/S3/bounds_grid.csv` | PUBLISHED |
| `ARL_0` at the two thresholds, measured base rate | `4.0×10⁶` at `λ = 15`, `9.1×10¹⁶` at `λ = 50` | `results/S2_theory/tables/s2_arl0_columns.csv` | PUBLISHED (`\ArlFifteen`, `\ArlFifty`) |
| `ARL_0` dispersion over the base-rate band | `1.1×10¹⁴` to `1.1×10²³` at `λ = 50` | `s2_gate_T20.json :: floor_and_family.floor_over_band` | PUBLISHED |
| Re-arm flooding model | `210` predicted against `86` measured (ARF), `28` against `7` (HT) | `results/S2_theory/tables/s2_flooding_retrodiction.json` | PUBLISHED (`\FloodPredArf`, `\FloodPredHt`) |
| `ARL_0` shortfall factor on the flooding alarms | `3×10⁴` | idem | PUBLISHED (`\FloodArlGap`) |
| Alarms bought over the armed span at the warm-up threshold | ARF `11.3`, HT `2.0` | `s2bis_flooding_gate.json` | PUBLISHED (`\FaSpanArf`, `\FaSpanHt`) |
| Measured base rate and Cramér root | `p₀ = 0.024`, band `[0.015, 0.032]`, `θ* = 0.6813` | `s2_gate_T20.json :: R1a.principal`, `p_true_sensitivity` | PUBLISHED (`\PzeroMeas`, `\PzeroBand`, `\ThetaStar`) |
| RNG factorisation refutation | Oza weight `1`–`16` draws per tree and step, mean `7.07`; perturbing one tree displaces `9,839` draw positions | `results/S3/rng_factorization.json` | PUBLISHED |
| Rectangular surrogate ratio | `A/A_rect` spans `2.70` to `-14.12`, sign change at `Δe ≥ 0.452` | `s6_causal.json`; `framework_v2.tex` `rem:invariance_measured` | UNPUBLISHED |
| `τ_erase` and `μW` at the canonical point | `τ_swap^(1/M) = 57.4` (`μW = 18.2`), `τ_erase = 612` (`μW = 194`) | `s6_causal.json`; `\SixTauFirst`, `\SixTauErase`, `\SixMuWfirst`, `\SixMuWerase` | PUBLISHED |

### (i) What this inventory does **not** contain

Two numerals circulating in the stream inputs have no committed source and are not produced here.
Both are recorded in `debt_register.md` as audit debt, not as claims.

- **Confidence-interval width factors `5×` / `3×`.** Zero occurrences in the repository. No
  estimator is recomputed by this stream (operator arbitration). The Table I framing below treats
  the bootstrap defect qualitatively, on what `S7ter_state_transfer.md` §3 establishes, and quotes
  no factor.
- **A per-cell measurement of the effect of the bootstrap correction.** Not produced; the closing
  command is recorded in the register.

---

## T11a.2 — The title

### What the current title asserts, and what is measured

`When Adaptation Erases the Evidence: Detectability Limits of Drift Monitors Coupled with Adaptive
Classifiers`, arbitrated at action A8.

The first half survives measurement: adaptation does erase, and S6 quantifies the erasure at
`99.3 %` incremental learning against `0.7 %` replacement, which is exactly the agnosticism about
mechanism that `Erases the Evidence` was chosen for.

The second half does not. `Detectability Limits` asserts a limit where the arithmetic reports a
calibration. At the canonical operating point the information-theoretic floor is `1.80` under the
χ² relaxation and `15.40` under the chord bound; the measured evidence ceiling is `33.5`; the
CUSUM fails because `R_CUSUM(λ = 50) = 59.3` at a false-alarm level of `6.3×10⁻¹⁶`. The evidence
clears the floor by a factor between `1.8` and `2.4`. At `λ_op = 21.93 [19.88, 22.40]` the same
requirement is `31.2` and the ceiling clears it. There is no detectability limit at the canonical
point; there is a threshold above the evidence available.

### Constraints applied to the three candidates

No superlative. No verb of the `defeat` family (`defeat`, `starve`, `beat`, `break`). The measured
mechanism — calibration — in the first position, not erasure alone.

### Candidate A — recommended

> **Thresholds Calibrated on the Wrong Stream: Drift Monitoring Under Closed-Loop Adaptation**

*Gains.* States the measured mechanism in the first four words and nothing else. `Wrong Stream` is
carried by two independent measurements the paper already owns: the ProteuS pre-drift error rate is
identically zero on all 1,080 runs, so `λ = 15` is selected by no false-alarm budget and the same
monitor detects `1080/1080` at `λ = 5`; and the INSECTS warm-up is `4.8×` shorter than the span the
detector then runs armed over, which is `89.9 %` of the published flooding ratio. The subtitle is
the framing (C1) rests on and the one the fault-detection-under-feedback literature indexes on.
Shortest of the three.

*Costs.* Does not carry `blind spot`, so it leaves the A8 disjunction exactly where A8 left it.
`Wrong` is a judgement the opening paragraph must discharge immediately; it can, with the two
measurements above, but it is a debt the title incurs.

### Candidate B

> **The Blind Spot Is a Calibration: Sizing Cumulative Monitors Against the Evidence an Adaptive Classifier Leaves**

*Gains.* The only candidate that closes the A8 open point: it restores `blind spot` to the title
and simultaneously states the v4 thesis, so title and body stop diverging and the term stops
reading as a phenomenon the paper failed to name in its own title. `Sizing … Against the Evidence`
is the paper's own design framing (`def:budget` against `def:requirement`) and puts (C2) in the
title.

*Costs.* Fourteen words, long for the venue. `The Blind Spot Is a Calibration` is a declarative
that a reviewer who has not read `def:blindspot` will read as rhetorical. Narrows the scope to
cumulative monitors, which is accurate for the resolution but under-states `cor:split`, whose
content is the ordering of three families.

### Candidate C

> **Evidence Available, Evidence Required: Drift Monitors Coupled with Adaptive Classifiers**

*Gains.* Names the two quantities of the framework and nothing more, so it commits to no mechanism
and survives any later revision of the mechanism. The most legible to a change-point-theory
committee, which reads `available/required` as the sizing problem it is. No judgement term.

*Costs.* Says nothing about the closed loop, which is the paper's structural claim; a reader who
stops at the title learns that two quantities are compared, not why one of them is bounded. The
least specific of the three about what is new.

### Recommendation

**Candidate A.** It states the mechanism the measurements support, it is the shortest, and its
subtitle carries the closed-loop framing (C1) is built on. The title/body disjunction on `blind
spot` stays open under A.

**The A8 open point, taken up rather than carried on by silence.** A8 arbitrated the title and
explicitly left undecided whether the body keeps `blind spot` while the title does not.
`terminology_map.md` retains the term on its three conditions, one of which — *its removal would
force the article to be renamed* — was written when the term was in the title and is now, strictly,
no longer met. The other two hold: `blind spot` designates an object (`def:blindspot`, `A < R`) and
no SPC or change-point term covers it. This stream recommends keeping the term in the body under
those two conditions and keeping the disjunction open, because the alternative — renaming the
phenomenon — costs four labels (`sec:blindspot`, `def:blindspot`, `(C1)`, the Conclusion opening)
and gains nothing measurable. Candidate B is the only option that closes the disjunction, and the
gain is recorded here without being required.

---

## T11a.3 — The abstract

Delivered in LaTeX, preamble macros consumed as they are.

### Numeral budget, checkable one by one

Three **estimated** numerals, each with its interval:

1. floor `\FloorBand` — interval is the measured base-rate band `p₀ ∈ [0.015, 0.032]`;
2. ceiling `33.5` — interval is the measured grid range `19.2`–`36.6`;
3. requirement at two thresholds — `59.3` at `λ = 50`, `31.2` at `λ_op = \LambdaOpNarrow`
   `\LambdaOpNarrowCI`.

Everything else the block quotes is a **census over a declared population** — `1080/1080`, `0/1080`,
`8,000` runs — or a design parameter, not an estimate, and therefore carries no interval by
construction. That distinction is the checkable form of the three-numeral constraint.

Zero superlatives. Zero immunity claims: the block states no monitor family as immune, and the
KSWIN sentence of the current abstract is not carried forward. The calibration rule occupies the
principal-contribution position, sentence four.

```latex
\begin{abstract}
  Concept-drift monitoring composes an adaptive classifier with an external detector that reads
  the classifier's error stream. The composition closes a loop: the classifier reacts to the very
  residual the detector measures, so a persistent change leaves a transient signature and the
  evidence available to the monitor is bounded by adaptation rather than by the horizon. We treat
  the pipeline as fault detection on an endogenous residual and size it with two quantities in one
  unit---the evidence an adaptation leaves inside the window, and the evidence a monitor requires
  at a stated false-alarm level---so that a missed detection is attributed to a calibration rather
  than to a detector family. Synchronised instrumentation of $8{,}000$ runs measures the first
  directly: at the canonical operating point the median evidence ceiling is $33.5$ (grid range
  $19.2$--$36.6$), which clears the information-theoretic floor $\FloorBand$ that binds every
  monitor of that false-alarm level. A cumulative monitor nonetheless reports no detection there,
  and the arithmetic states why: at $\lambda = 50$ its requirement is $59.3$, while at the
  threshold the same certificate returns, $\lambda_{\mathrm{op}} = \LambdaOpNarrow$
  $\LambdaOpNarrowCI$, the requirement is $31.2$ and the ceiling clears it. The published collapses
  are threshold facts. On heteroscedastic ARMA--GARCH streams the same Page--Hinkley monitor that
  detects $0$ of $1{,}080$ drifts at the deployed threshold detects $1{,}080$ of $1{,}080$ at
  $\lambda = 5$ with precision $1.000$; the three detector families the evaluation compares are
  read at false-alarm levels thirteen orders of magnitude apart; and counterfactual arms sharing
  one stream and one fork assign $\LearnShare\%$ of the erasure to ordinary incremental learning by
  the surviving trees rather than to any internal detector. The rule these measurements support is
  operational: set the threshold from the false-alarm budget of the span the monitor will run armed
  over, on the error stream of the classifier it will be paired with, and check that the resulting
  requirement lies below the measured evidence ceiling. Validation spans instrumented Bernoulli
  streams, ProteuS, and six real-world streams (BAF, INSECTS), on which the two regime-dependent
  faces of the calibration---recall collapse and precision collapse---are reported separately.
\end{abstract}
```

*Note for the assembly.* `\LearnShare` appears in the block and is a fourth numeral by a strict
count; it carries no interval in the macro. Two options, both sound: quote it as
`$\LearnShare\%$ (IQR $[0.987, 0.998]$, $n = 1{,}979$)`, which restores the interval and keeps the
sentence; or drop the clause and let (C3) carry it. The block above keeps the clause without the
interval because the share is a pooled median over a declared population rather than an estimate of
a latent parameter; the assembly should pick one reading and apply it once.

*Literals with no preamble macro.* `33.5`, `19.2`, `36.6`, `59.3`, `31.2`. All five are read from
`s2_gate_T20.json` and `s2bis_proteus_gate.json`. If the assembly wants them under the
single-source rule that governs the other 55 constants, five `\newcommand` lines suffice; this
stream does not add them, because adding a macro to the preamble is an edit to the manuscript.

---

## T11a.4 — The contributions

`intro_v2.tex` L84-105 carries (C1)–(C4) under the v2 statement. The four below replace them under
v4. Each is followed by the artifact that carries it.

```latex
\noindent\textbf{Contributions.}
\begin{enumerate}[nosep, label=\textbf{(C\arabic*)}]
  \item \textbf{Monitoring under closed-loop adaptation.} We state the concept-drift monitoring
  problem as fault detection on an endogenous residual, give the mapping to the
  fault-detection-under-feedback setting, and derive the prediction that severity is governed by
  the comparison of the evidence the loop leaves against the evidence the monitor's calibration
  requires---not by River, by ARF, or by ADWIN, and not by any one internal detector
  (Section~\ref{sec:blindspot}).
  \item \textbf{A transient-detection analysis of the sizing problem.} We characterise the
  observability window adaptation induces, define the blind spot as a deficit of budget against
  requirement in a single unit, and derive a detection floor that binds every monitor at a given
  false-alarm level. The floor separates two regimes: below it no monitor detects, above it the
  deficit is a property of the calibration and a different setting escapes it
  (Section~\ref{sec:starvation}).
  \item \textbf{Synchronised measurement of the budget.} We instrument tree replacement, ensemble
  error and the monitor's statistic on a shared clock across counterfactual arms that share one
  stream, one history and one fork; we measure the evidence ceiling directly rather than through a
  rectangular surrogate, and we report the dilation between the first replacement and erasure as a
  measurement rather than as a definitional assumption (Section~\ref{sec:experiments}).
  \item \textbf{An ordering of monitor families, and the level at which it reverses.} We order
  cumulative, windowed and distributional monitors by the evidence each requires at a
  \emph{common} false-alarm level, show that the ordering follows a scaling law rather than a
  taxonomy---linear in $\ln(1/\alpha)$ for the cumulative monitor, square-root for the other
  two---and locate the crossings. The threshold this paper recommends lies on the side where the
  cumulative monitor is the cheaper of the three (Section~\ref{sec:related} and
  Section~\ref{sec:discussion}).
\end{enumerate}
```

**Tenable with.**

- **(C1)** — `results/S6_synchronized_traces/data/s6_causal.json`
  (`erasure_share_post_fork.a_pos_common.pooled`: `99.3 %` learning, IQR `[0.987, 0.998]`,
  `n = 1979`); `results/S2_theory/tables/s2_gate_T20.json :: budget_restitution.measured` (the
  nominal ceiling spreads `1.90×` and is non-monotone, the suspended arm spreads `124×` and is
  monotone); `framework_v2.tex` `rem:invariance_measured`.
- **(C2)** — `framework_v2.tex` `def:budget`, `def:requirement`, `def:blindspot`, `thm:floor`,
  `rem:floor_tight` (the chord form, `χ²` costs a factor `6.74`), `rem:floor_band`;
  `s2_gate_T20.json :: floor_and_family.floor_chord_interval = [13.88, 18.29]`.
- **(C3)** — `results/S6_synchronized_traces/data/runs.parquet` and `s6_causal.json`
  (`100` seeds × `20` magnitudes × four arms; `κ ≥ 1` in `1835/1836` runs, median `14.6`;
  `τ_swap^(1)/τ_swap^(1/M) = 17.9`, elasticity `0.66`, `z = -14.9`); `framework_v2.tex`
  `def:kappa`, `rem:order`.
- **(C4)** — `framework_v2.tex` `cor:split` and `rem:split_measured`;
  `results/S2bis_calibration/tables/s2bis_proteus_gate.json :: cor_split_crossings` (KSWIN at
  `ln(1/α) = 16.34`, `λ = 22.605`; ADWIN at `18.97`, `λ = 26.466`; CUSUM slope `1.468 = 1/θ*`);
  `envelope_stats.json` for `λ_op = 21.93 [19.876, 22.398]`, which lies entirely below the KSWIN
  crossing.

### What (C1) keeps, and why the two removals do not empty it

(C1) attributed the phenomenon to the Hydra Effect. Two measurements remove that attribution.
S6 leaves replacements `0.7 %` of the erased volume. S3 removes the attribution of the shortfall
from the `10×` parallel-chart reference: the order statistics of `F̂_HAT` alone predict `9.22×`
against `7.99×` measured, and the within-run correlation is `ρ̂ ∈ [-0.021, 0.053]`.

What remains, and is tenable: the **topology** — a monitor reading a residual the classifier
closes a loop on — plus the prediction that severity is set by the budget-against-requirement
comparison and by no implementation constant. The topology is not touched by either measurement;
the counterfactual arms demonstrate it directly, since suppressing adaptation restores the
monotone scaling of the ceiling on the same streams. The version at `intro_v2.tex` L86-91 is
already close; the rewrite above tightens it onto `A < R` and removes the word `Hydra`.

The rewrite also replaces *the ratio of erasure time to detector integration time* with the
budget-against-requirement comparison. That is not a stylistic change: `rem:shortwindow` retires
the window-based sufficient statistic in the manuscript's own words — *starvation is governed by
how much evidence exists, not by how long it lasts* — and a contribution stated on a ratio of times
contradicts the proposition three pages later.

### (C4): reformulated, not conditioned — and why

**Decision: reformulate.** S9 exists as a prompt and nothing else. `git log --all` shows no
branch, `results/` no directory, `docs/theory/` no transfer. An arm that is not delivered cannot
carry a contribution.

The reformulation is not a retreat to a weaker claim; it moves (C4) onto a result that is derived
and instantiated rather than promised. `cor:split` derives the ordering from a scaling law, and
`rem:split_measured` instantiates it at the measured operating point with a crossing point. That
is strictly more than the v2 (C4) offered, which ordered three families by exposure and stated a
cost per family without a number.

The input-space promise descends to future work and is declared there with its structural cost,
which the paper already states: `related_work_v2.tex` L92-95 records that an input-space monitor is
blind to a change in `P(Y|X)` at fixed `P(X)`, and the controlled generator of this paper moves the
decision boundary at fixed `P(X)`. The arm would therefore be blind to the drift the paper studies
by construction. Declaring that is a result about the design space, and it is the honest form of
the sentence at `related_work_v2.tex` L97-99 — *which is why we evaluate an input-space arm
alongside the error-stream arms* — which currently promises an experiment the repository does not
contain. That sentence is in the register.

---

## T11a.5 — The framing of Table I

Table I is the paper's flagship experiment. Five grievances are raised against it upstream. One is
false as stated and is corrected below rather than repeated.

### 1. The pre-drift phase carries an identically zero error rate

Measured: `0` pre-change errors, median and maximum, on all 1,080 runs of both arms
(`s2bis_proteus_eddm_arming.csv`, column `n_pre_drift_errors`). The target is a deterministic step
function of `t` (`simulate_stream`: `regime = (f_t > 0.5)` with `f_t = expit(4(t - t_p)/w)`,
constant `0` for `t < t_p`) and the classifier predicts that constant from the first step.

Consequence: no false-alarm budget is consumed on that span, every `λ > 0` satisfies every
false-alarm constraint, and `λ = 15` is selected by no measurement. The equalising threshold sits
at the bracket floor `1.000` — range `[1.000, 1.000]` over 1,080 cells — and at that floor all six
couples return the same `F1 = 0.0148` and the same precision `0.0075`, because the monitor floods,
the classifier is reset every few dozen steps and never learns. An equal-false-alarm-budget
calibration is not a fairer comparison on this stream; it is no comparison at all.

### 2. The families are compared at incommensurable false-alarm levels

At `λ = 15`, a common requirement asks ADWIN for `α = 9.0×10⁻²` and KSWIN for `α = 1.1×10⁻³`.
Deployed, ADWIN runs at `δ = 0.002` — `45×` tighter — and KSWIN at `α = 0.005` — `4.5×` looser.
The direction differs by family, so the discrepancy does not cancel in a ranking. At `λ = 50` the
gap widens to thirteen orders of magnitude: KSWIN at `α = 0.005` against a CUSUM at `α ≈ 6.3×10⁻¹⁶`.

**Correction of statement.** The grievance as received says *its three columns*. The three columns
of Table I are the GARCH regimes — IID, Cal. A, Cal. B — and they are not at issue; the blind-spot
signature is invariant across them, which is a result the table establishes. What compares
calibrations are the **rows**: the fourteen pipeline configurations, each carrying its own
detector at its own level. The framing states it that way.

### 3. One of its collapses is a detector that never arms

River's EDDM requires `warm_start = 30` monitored errors before it can signal. On these streams the
EDDM + ARF(`c=1`) arm accumulates `9` errors over the whole 8,000 steps (range `[6, 12]` over 1,080
runs) against zero before the change, and `100 %` of runs are never armed — `armed_at_t` is null on
every run. The `F1 = 0.00` row is therefore an arming failure, not an accumulation failure, and
`prop:starvation` never applies to it. The companion arm is the control: EDDM + HT accumulates `32`
errors, arms with a median lag of `30` steps after the change, and detects in `81.9 %` of runs.

`framework_v2.tex` already places EDDM outside `def:requirement` as instantiated, and claims no
`R_EDDM`: its statistic is a ratio against a running maximum of inter-error distances, not an
accumulated sum against a fixed threshold. The measurement and the theory agree; the manuscript's
prose does not yet.

### 4. The HT arm's replication — verified before being repeated, and corrected

The grievance as received states that the HT arm carries one effective replicate, `make_ht()` being
unseeded, so any paired ARF-against-HT test is a one-sample test against a constant. **Measured,
that is false for Table I.**

`make_ht()` (`exp_R4_main_table.py:174`) is indeed unseeded. But `simulate_stream(..., seed=seed)`
(`:202`) is seeded, and `simulate_stream` opens with `np.random.seed(seed)` (`:76`), so the 30 seeds
produce 30 distinct streams and the HT arm carries 30 replicates. Measured on
`exp_R4_results_aligned_fusion.csv`: the per-seed mean `F1` of PHT + HT takes `6` distinct values
over the 30 seeds, sd `0.0317`, range `[0.8056, 0.9444]`; ADWIN + HT, `5` distinct values, sd
`0.0334`. A constant has one value and zero spread.

What the asymmetry actually produces is weaker and different. `make_arf(seed, c)` and
`make_rf(seed)` consume the seed; `make_ht()` does not. The ARF and RF arms therefore carry two
sources of variation per seed — stream and forest initialisation — against one for the HT, and the
paired interval inherits the difference. The framing states that version, with the line citation,
and does **not** state the one-sample claim.

Within a single `(transition, regime)` cell the 30 seeds return one `F1` value and two `ADD`
values. That is the granularity of the scoring protocol — one drift per stream, a closed matching
window — and not an absence of replication; the seed-level statistic Table I reports is the mean
over the 36 cells, which does vary. The framing records the granularity so a reader does not
rediscover it as a defect.

*Collateral finding, carried to the register.* `simulate_stream` mutates the global NumPy state
(`np.random.seed(seed)`, `exp_R4_main_table.py:76`). The repository's determinism rule requires
locally injected generators. The call is load-bearing for bit-reproducibility today and is not
touched by this stream; it is recorded as debt.

### 5. The bootstrap measured the wrong variance component — stated, not quantified

Established by `S7ter_state_transfer.md` §3. The submitted version resampled the 360 rows of a cell
with `np.random.choice` drawn from the **global** NumPy state, while the caption asserted the seed
as the unit of statistical independence. The two statements are incompatible: the 36 streams a seed
produces share that seed's forest initialisation, so a run-level resample does not estimate the
dispersion the caption claims to report.

Corrected at `exp_R4_main_table.py:234-250` to a paired resample of the **seed index** on a locally
injected `default_rng`, percentiles taken of the per-replicate mean; the scheme is reused from
`exp_R6_hydra_survival.py:105-111`.

The framing states the defect and its correction and **quotes no factor**. The `5×` / `3×` widths
circulating upstream have no committed source — zero occurrences in the repository — and are not
produced here by operator arbitration. They are recorded in `debt_register.md` with the command
that would close them.

### What the table establishes

A complete, reproducible separation on identical streams. At `c_int = 1` the cumulative monitor
detects `0` of 1,080 drifts where the non-adaptive baseline detects `932`; the same separation
appears independently on a second cumulative family (EDDM, `0` against `882`), on a second ensemble
(SRP, `0` against `932`), and reverses under a static ensemble (`913` against `0`). Every one of
the six contrasts separates on all 30 seeds. The blind-spot signature is invariant across the three
GARCH regimes, which is what licenses calling it architectural rather than a property of input
volatility clustering.

### What the table does not establish

It is not a comparison of detector families: its rows are read at false-alarm levels that differ by
up to thirteen orders of magnitude, and no ranking survives equalising them. It arbitrates no
detection-against-false-alarm trade-off: its pre-change span carries zero errors, so no threshold on
it is bought at a false-alarm cost and none is selected by a budget. It exhibits no accumulation
mechanism for EDDM: that row is a detector that never arms. And it does not locate the threshold at
which the collapse begins, because it is measured at one threshold.

### Where the reader should go

`results/S2bis_calibration/tables/s2bis_proteus_sweep.csv` — an eight-point ladder in `λ` on the two
headline couples, 1,080 runs per point, the same pipeline and the same streams. It answers the
question Table I does not: the collapse is a cliff between `λ = 8` (`1063/1080`, `F1 = 0.9843`) and
`λ = 15` (`0/1080`), and at `λ = 5` the pipeline Table I prints in boldface as `F1 = 0.00` detects
`1080/1080` with precision `1.000` and a mean delay of `6.05` steps. The contrast with PHT + HT is
the mechanism in one column: the non-adaptive learner degrades gracefully across the whole ladder
(`0.9269 → 0.6509`, a factor `1.4` over a factor `26` in `λ`), the adaptive one has a cliff. That
cliff locates the evidence ceiling of the ARF at `c_int = 1` on ProteuS in `(8, 15]` — a direct
measurement, on the stream where the collapse is reported, of the quantity the framework is built
on.

---

## T11a.6 — The ontology of effects

`terminology_map.md` retains a proper name only when three conditions hold: it designates an object
or a derived mechanism, never an observed consequence or a measured quantity; no standard term of
SPC, change-point theory or FDI covers it; and its removal would force the article to be renamed.

### Retained

| term | status | why it is retained |
|---|---|---|
| `blind spot` | retained, lower case, unemphasised after `def:blindspot` | Designates the region of the design space where the budget falls below the requirement. It is an object and it is formally defined (`A < R(D, ε, α)`). The FDI sense — an unobservable fault — is close but not identical. Condition three is no longer met since A8 removed the term from the title; conditions one and two hold, and the recommendation of T11a.2 is to keep the term on those two. |
| `starvation` | retained, lower case | Designates the mechanism: truncation of the observation window below the evidence requirement. The neighbouring SPC term — power deficit under window truncation — describes the outcome without naming the cause of the truncation. |

### Removed, with the measured reason where one exists

| v64 term | v4 replacement | reason |
|---|---|---|
| Hydra Effect | `γ_M := τ_erase^(1) / τ_erase^(M)`, a measured quantity carrying a symbol | Lost its mechanism, not only its name. The order statistics of `F̂_HAT` alone predict `9.22×` at `Δe = 0.3268` against `7.99×` measured, so the shortfall from the `10×` parallel-chart reference is non-exponentiality of the delay law, not inter-tree correlation; the measured within-run correlation is `ρ̂ ∈ [-0.021, 0.053]`. And S6 leaves replacements `0.7 %` of the erased volume. What survives is an onset acceleration with a number, which is what a symbol is for. |
| Decoupling Principle | reactivity condition, sufficient | Lost its biconditional, withdrawn in the body of the manuscript itself (`def:decoupling` (i-bis): *which we withdraw*). ADWIN paired with the ARF at equal clocks detects reliably while violating the strict form, so the necessity direction is refuted by the paper's own data. A refuted principle does not keep a proper name. |
| Zombie Alarm | post-recovery alarm | An observed consequence, fully described by *the alarm arrives after the error has returned within tolerance*. |
| Fundamental Tension | empty admissible set / infeasible calibration region | Describes a calibration fact statable in one sentence. |
| fundamental race condition | concurrency between erasure and accumulation | `fundamental` is not demonstrated; `race condition` imports a software-concurrency metaphor with no formal counterpart. |
| blind spot **paradox** | blind spot | The suffix presented as counter-intuitive what transient-change detection theory predicts. |

### Superlatives and undemonstrated claims, unchanged from `terminology_map.md`

`permanently erasing` → erased over the observation window, finite horizon stated;
`single root cause` → dominant mechanism on the tested grid;
`structurally fail` → fail on the tested grid;
`perfect detection` → recall `1.00` on the tested grid;
`escapes this outright` → not subject to the same accumulation constraint;
`structurally immune` → outside the error loop, or a shorter integration constant;
`entirely inoperative` → null recall on the tested configurations;
`ADWIN hyper-reactivity` → time constant of the internal corrector.

Every site carrying one of these is listed in `debt_register.md` with its anchor.

### What the figure must add

`docs/manuscript/figures/fig_ontology.tex` is rewritten in place under the v4. The file already
exists, is already declared `AUTHORED` in `tests/test_manuscript_integrity.py`, is already
`\input` by `intro_v2.tex:82` under the label `fig:ontology`, and is **not** included by the v64
`.tex` (verified: zero occurrences). Rewriting it therefore edits no section of the manuscript and
does not change the compiled document. Creating a second file would force an extension of
`AUTHORED` for nothing.

Four things the S5 version does not carry and the v4 requires:

1. **`A` against `R(D, ε, α)` as the terminal node.** The comparison is `def:blindspot`; the figure
   must end on it rather than on a comparison of times.
2. **The separation of the two floors.** `thm:floor` splits two regimes: below the
   information-theoretic floor no monitor detects; above it but below `R(D, ε, α)` this monitor
   does not detect and another one can. That bifurcation is what makes the calibration rule legible
   in one image, and it is the difference between v2 and v4.
3. **The requirement's dependence on `α`**, since the ordering of families is a scaling law in
   `ln(1/α)` and not a taxonomy.
4. Retained unchanged from S5: the negative feedback loop, the single `λ` axis carrying starvation
   and flooding as two settings of one threshold, and the `P(X)` monitor outside the loop with its
   symmetric cost.

Compilation constraints: the preamble already loads `tikz` with
`arrows.meta,positioning,fit,backgrounds` (L11-12), so no new dependency. The label `fig:ontology`
and the filename are invariant, on pain of breaking `intro_v2.tex:82`.
