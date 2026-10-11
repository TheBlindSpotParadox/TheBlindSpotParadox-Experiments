# TheBlindSpotParadox-Experiments

Code, data and artifacts of *The Blind Spot Paradox: When Adaptive Classifiers Defeat Drift
Detectors*, by Raphaël Minato, Fabrice Popineau, Arpad Rimmel and Bich-Liên Doan, a paper of the
OWAD workshop at IEEE ICDM 2026 ([arXiv:2610.05853](https://arxiv.org/abs/2610.05853)). The
camera-ready, as published, is sealed in `docs/manuscript/owad2026/`.

The repository also holds the journal-track manuscript under development, *The Calibration Blind
Spot: Sizing Cumulative Drift Monitors Against Adaptive Classifiers*, which
`docs/manuscript/CURRENT` names. Section 4 lists the material that belongs to it alone.

## 1. Reproducing the OWAD 2026 paper

One command regenerates every artifact that `docs/OWAD_CLAIMS.md` cites, in a copy of the
repository, and compares each output with the repository's file:

```bash
./run_owad2026.sh --dry-run        # the stage table and the artifact -> stage map; runs nothing
./run_owad2026.sh --copy <dir>     # copies the repository to <dir>, outside it, and runs there
```

Before each stage it deletes every output the stage writes, so nothing resumes from a checkpoint.
It writes `<dir>/owad_regen_report.md`: the wall clock of each stage, a byte comparison of every
output against the repository, and the test suite run inside the copy. It refuses a directory inside
the repository. The measured run is recorded in `docs/ENVIRONMENT.md`.

| Element | Command | Artifact | Test |
|---|---|---|---|
| Fig. 1 | `python experiments/R1_race_condition/exp_R1_generate_data.py --arm owad2026`, then `python experiments/R1_race_condition/exp_R1_plot_figure.py --arm owad2026` | `results/R1_race_condition/owad2026/figures/Fig_R1_race_condition.png`, drawn from `results/R1_race_condition/owad2026/data/R1_race_condition.parquet` | `tests/test_owad_snapshot.py`; rows M28 and M29 of `tests/test_owad_claims.py` |
| Fig. 2A–2C | `./run_experiment_R2.sh` | `results/R2_instrumented_blind_spot/figures/` | `tests/test_owad_snapshot.py` |
| Fig. 3 | `./run_experiment_R3.sh` | `results/R3_regime_crossover/figures/Fig_R3_Regime_Crossover.png` | `tests/test_owad_snapshot.py` |
| Table I | `python experiments/R4_proteus_evaluation/exp_R4_main_table.py --arm owad2026` | `results/R4_proteus_evaluation/owad2026/tables/table1_proteus_summary.tex` | `tests/test_owad_snapshot.py`; row M30 |
| Table II | `./run_experiment_R5.sh` | `results/R5_real_world_evaluation/tables/table2_values.csv` | `tests/test_owad_snapshot.py`; row M23 |
| Numerals in the text | the stages of `./run_owad2026.sh` | the artifact each row of `docs/OWAD_CLAIMS.md` names | `tests/test_owad_claims.py` |

The figures and tables of the paper are the files of `docs/manuscript/owad2026/`. Where one differs
from the pipeline render, the difference is declared (section 3).

## 2. Errata and claim ledger

The printed paper is frozen at the publisher. `docs/OWAD_CLAIMS.md` is its erratum record: it
traces every numeral written in digits in the sealed `.tex` to the committed artifact that carries
it, and `tests/test_owad_claims.py` re-reads each artifact and fails when a row no longer holds.

| Status | Rows |
|---|---|
| MATCH | 41 |
| ANALYTIC | 6 |
| PROVENANCE | 3 |
| MISMATCH | 12 |
| AMBIGUOUS | 4 |
| UNTRACED | 3 |
| LAYOUT | 3 |
| QUALIFICATION | 4 |

These counts are generated from the registry, and `tests/test_owad_claims.py` fails when they drift
from it: they hold for every commit on which the suite passes.

- **MISMATCH**, rows X01–X12: the artifact contradicts the printed numeral.
- **UNTRACED**, rows U01–U03: no committed artifact carries the printed value.
- **QUALIFICATION**, rows Q01–Q04: a committed measurement qualifies a printed claim without
  contradicting it.

A corrected version of the paper will be posted on arXiv.

## 3. Configurations the paper does not state

- **R3 warning detector.** The published arm, U0, leaves the `warning_detector` of the ARF unset,
  which River 0.23.0 resolves to `ADWIN(delta=0.01, clock=32)`; `config/experiment_ssot.py` writes
  it out as `R3_WARN_DELTA_U0` and `R3_C_WARN_U0`. `--arm U1` runs the ablation that clones the drift
  detector instead (`results/audit_S7/s7ter_arms/README.md`).
- **R1, two arms.** Fig. 1 as published runs the external CUSUM at delta_P = 0.005
  (`R1_OWAD_DELTA_P`, `--arm owad2026`). The current arm, the default of both R1 scripts, runs it at
  delta_P = 0.01 (`R1_DELTA_P`).
- **R4, two arms.** Table I as published is arm U0 with intervals that resample the 360 runs of a
  cell (`--arm owad2026`). The current arm is U1 with intervals that resample the 30 seeds.
  `--arm owad2026 --bootstrap seed` gives seed-level intervals on the published data, in
  `results/R4_proteus_evaluation/owad2026_seedboot/` (row Q04).
- **Layout.** The captions of Table I and Table II, the row labels of Table II and the Fig. 1 image
  differ from the pipeline renders. Rows L01, L02 and L03 declare each difference, and
  `tests/test_owad_snapshot.py` checks them.

## 4. Journal-track material

`docs/manuscript/CURRENT` names the journal manuscript, `docs/manuscript/articleA_blindspot_v65_mlj.tex`,
which inputs the fragments of `docs/manuscript/sections/`. Its experiment set is larger than the
paper's; the artifact paths of `docs/OWAD_CLAIMS.md` split `results/` in two.

- **Cited by the OWAD registry:** `results/R1_race_condition/`, `results/R2_instrumented_blind_spot/`,
  `results/R3_regime_crossover/`, `results/R4_proteus_evaluation/`,
  `results/R5_real_world_evaluation/`, `results/R6_hydra_factor/`, `results/R7_clock_mismatch/`,
  `results/R9_mcrit/`, `results/S2bis_calibration/`, `results/S3/`,
  `results/S6_synchronized_traces/`, `results/S8_ab_initio/`, `results/S9_detector_coverage/`,
  `results/S13_evidence_bell/` and `results/audit_S7/`.
- **Journal track only:** `results/R8_lambda_op_sweep/`, `results/S2_theory/`,
  `results/S8_marginal/`, `results/S8_mechanisms/`, `results/S8_minimal_arf/`,
  `results/S8_r7_figure/`, `results/S8_rotation_generator/` and `results/S10_external_validity/`.

R9 sits on both sides. Only its data generation, `experiments/R9_mcrit/exp_R9_generate_data.py`,
feeds the OWAD rows X07 and X09; its M_crit comparison, `experiments/R9_mcrit/exp_R9_compute_mcrit.py`,
serves the journal manuscript.

## 5. History

- This repository extends and corrects the one submitted to the ICDM 2026 main track,
  [github.com/TheBlindSpot-ICDM2026/The-Blind-Spot-Paradox-Experiments](https://github.com/TheBlindSpot-ICDM2026/The-Blind-Spot-Paradox-Experiments).
- **The 93 → 86 flooding note.** The main-track submission quoted 93 alarms (precision 0.011) for
  PHT+ARF (c = 1) on `gradual_balanced`. The artifact gives 86 alarms (precision 0.012), the value
  both manuscripts print (row M23); PHT+HT emits 7 on the same stream, and the conclusion is
  unchanged.
- **The v64 lineage.** `docs/manuscript/articleA_blindspot_v64_camera_ready.tex` is an earlier,
  unsubmitted version of the journal manuscript, superseded by v65 and kept to seal the lineage of
  its numerals. `results/audit_S7/_baseline/artifacts_sha256_pre_ssot.txt` is the frozen hash list
  of the committed artifacts, and `results/audit_S7/_baseline/authorized_deviations.txt` declares
  every deviation from it, and every later change to an artifact, with its motive and measured
  effect.

## 6. Environment and tests

- **Environment.** The interpreter, Python 3.12.9, and the pins of `requirements.txt` are part of
  the determinism contract; `docs/ENVIRONMENT.md` records the host, the pins and the measured wall
  clocks. The pipeline runs Bash scripts; on Windows, use WSL or Git Bash.

  ```bash
  python -m venv blindspot_env && source blindspot_env/bin/activate
  pip install -r requirements.txt
  ```

- **Data.** `data/baf/` holds the three variants of the
  [NeurIPS 2022 Bank Account Fraud dataset](https://www.kaggle.com/datasets/sgpjesus/bank-account-fraud-dataset-neurips-2022),
  compressed: run `gunzip -k data/baf/*.gz` before R5. `data/insects/` holds the three streams of the
  [INSECTS repository](https://drive.google.com/drive/folders/1v-iRL6X4yWhKIn82-eS-w93wb-gxjSiz).
- **Current arms.** `./run_all.sh` runs R1 to R9 in dependency order, R6 after R2, then the tests.
- **OWAD paper.** `./run_owad2026.sh`, section 1.
- **Tests.** `python -m pytest tests/` runs the 23 test files of `tests/`.

## 7. Repository tree

Generated from the filesystem; the project's internal working documents are not listed.

```text
.
├── config/
│   └── experiment_ssot.py
├── data/
│   ├── baf/
│   │   ├── Base.csv.gz
│   │   ├── VariantI.csv.gz
│   │   └── VariantII.csv.gz
│   └── insects/
│       ├── abrupt_balanced.csv
│       ├── gradual_balanced.csv
│       └── incremental_reoccurring_balanced.csv
├── docs/
│   ├── manuscript/
│   │   ├── figures/
│   │   │   └── …
│   │   ├── owad2026/
│   │   │   ├── figures/
│   │   │   │   ├── Fig_R1_race_condition.png
│   │   │   │   ├── Fig_R2_A_PHT_ARF.png
│   │   │   │   ├── Fig_R2_B_PHT_ARF.png
│   │   │   │   ├── Fig_R2_C_PHT_ARF.png
│   │   │   │   └── Fig_R3_Regime_Crossover.png
│   │   │   ├── tables/
│   │   │   │   ├── table1_proteus_summary.tex
│   │   │   │   └── table2_real_data_summary.tex
│   │   │   ├── The_Blind_Spot_Paradox_ICDM_OWAD_2026.bib
│   │   │   ├── The_Blind_Spot_Paradox_ICDM_OWAD_2026.pdf
│   │   │   └── The_Blind_Spot_Paradox_ICDM_OWAD_2026.tex
│   │   ├── sections/
│   │   │   └── …
│   │   ├── tables/
│   │   │   └── …
│   │   ├── articleA_biblio_v64.bib
│   │   ├── articleA_blindspot_v64_camera_ready.tex
│   │   ├── articleA_blindspot_v65_mlj.tex
│   │   ├── CURRENT
│   │   ├── IEEEabrv.bib
│   │   ├── spmpsci.bst
│   │   ├── svglov3.clo
│   │   └── svjour3.cls
│   ├── slides/
│   │   └── …
│   ├── ENVIRONMENT.md
│   ├── METHODS.md
│   └── OWAD_CLAIMS.md
├── experiments/
│   ├── R1_race_condition/
│   │   ├── exp_R1_generate_data.py
│   │   └── exp_R1_plot_figure.py
│   ├── R2_instrumented_blind_spot/
│   │   └── exp_R2_instrumented_blind_spot.py
│   ├── R3_regime_crossover/
│   │   └── exp_R3_regime_crossover.py
│   ├── R4_proteus_evaluation/
│   │   ├── exp_R4_kswin_sweep.py
│   │   ├── exp_R4_label_check.py
│   │   └── exp_R4_main_table.py
│   ├── R5_real_world_evaluation/
│   │   ├── exp_R5_alarm_protocol.py
│   │   ├── exp_R5_baf_timing.py
│   │   ├── exp_R5_common.py
│   │   ├── exp_R5_compute_baf.py
│   │   ├── exp_R5_compute_delta_e.py
│   │   ├── exp_R5_compute_insects.py
│   │   ├── exp_R5_config.py
│   │   ├── exp_R5_make_table2.py
│   │   ├── exp_R5_preflight.py
│   │   └── exp_R5_smoke_test.py
│   ├── R6_hydra_factor/
│   │   ├── exp_R6_compute_hydra.py
│   │   ├── exp_R6_generate_data.py
│   │   └── exp_R6_hydra_survival.py
│   ├── R7_clock_mismatch/
│   │   ├── exp_R7_compute_regime1.py
│   │   └── exp_R7_generate_data.py
│   ├── R8_lambda_op_sweep/
│   │   └── exp_R8_lambda_op_sweep.py
│   ├── R9_mcrit/
│   │   ├── exp_R9_compute_mcrit.py
│   │   └── exp_R9_generate_data.py
│   ├── S10_external_validity/
│   │   ├── s10_dual_mode.py
│   │   ├── s10_holm.py
│   │   ├── s10_latency.py
│   │   └── s10_p0.py
│   ├── S13_evidence_bell/
│   │   ├── s13_evidence_bell.py
│   │   └── s13_figure_bell.py
│   ├── S2_theory/
│   │   ├── s2_arl0.py
│   │   ├── s2_eddm.py
│   │   ├── s2_exact_alpha.py
│   │   └── s2_w_random.py
│   ├── S2bis_calibration/
│   │   ├── s2bis_lambda_eq.py
│   │   ├── s2bis_proteus_calibration.py
│   │   └── s2bis_r1_ppre.py
│   ├── S3_dependence/
│   │   ├── s3_bounds.py
│   │   ├── s3_competing_risks.py
│   │   └── s3_gate_rng_factorization.py
│   ├── S6_synchronized_traces/
│   │   ├── gates/
│   │   │   ├── _gate_common.py
│   │   │   ├── g0_predict_one_neutrality.py
│   │   │   ├── g0_report.json
│   │   │   ├── g1_deepcopy_fidelity.py
│   │   │   ├── g1_report.json
│   │   │   ├── g2_api_map.json
│   │   │   ├── g2_river_introspection.py
│   │   │   ├── g3_report.json
│   │   │   └── g3_throughput.py
│   │   ├── s6_audit_ass_repair.py
│   │   ├── s6_causal.py
│   │   ├── s6_defs.py
│   │   ├── s6_detectors.py
│   │   ├── s6_envelope_stats.py
│   │   ├── s6_figure.py
│   │   ├── s6_predictive_power.py
│   │   ├── s6_recompute_cusum_delta001.py
│   │   ├── s6_runner.py
│   │   ├── s6_window_budgets.py
│   │   └── s6_writer.py
│   ├── S8_generality/
│   │   ├── s8_arms.py
│   │   ├── s8_figure_r7.py
│   │   ├── s8_marginal.py
│   │   ├── s8_mechanisms.py
│   │   ├── s8_minimal_arf.py
│   │   └── s8_rotation.py
│   └── S9_detector_coverage/
│       ├── s9_family_ordering.py
│       ├── s9_input_space.py
│       ├── s9_kswin_dilution.py
│       ├── s9_offline_detectors.py
│       └── s9_rotation_traces.py
├── results/
│   ├── audit_S7/
│   │   └── _baseline/, config_matrix.md, hydra_survival.csv, hydra_survival.tex, regeneration_spec.md, s7ter_arms/
│   ├── R1_race_condition/
│   │   └── data/, figures/, owad2026/
│   ├── R2_instrumented_blind_spot/
│   │   └── data/, figures/
│   ├── R3_regime_crossover/
│   │   └── data/, figures/
│   ├── R4_proteus_evaluation/
│   │   └── data/, owad2026/, owad2026_seedboot/, tables/
│   ├── R5_real_world_evaluation/
│   │   └── data/, tables/
│   ├── R6_hydra_factor/
│   │   └── data/, tables/
│   ├── R7_clock_mismatch/
│   │   └── data/, tables/
│   ├── R8_lambda_op_sweep/
│   │   └── data/
│   ├── R9_mcrit/
│   │   └── data/, figures/
│   ├── S10_external_validity/
│   │   └── .gitignore, data/, figures/, tables/
│   ├── S13_evidence_bell/
│   │   └── blindspot_map.csv, evidence_bell.csv, figures/, s13_gate.json
│   ├── S2_theory/
│   │   └── tables/
│   ├── S2bis_calibration/
│   │   └── tables/
│   ├── S3/
│   │   └── bounds_grid.csv, cif_bands.csv, figures/, hydra_equal_budget.json, ks_exponentiality.csv, pmiss_vs_M.csv, rho_meff.csv, rng_factorization.json, s3_competing_risks.json, s3_verdicts.json
│   ├── S6_synchronized_traces/
│   │   └── data/, data_refine/, figures/, smoke/, tables/
│   ├── S8_ab_initio/
│   │   └── data/, smoke/, tables/
│   ├── S8_marginal/
│   │   └── data/, tables/
│   ├── S8_mechanisms/
│   │   └── data/, tables/
│   ├── S8_minimal_arf/
│   │   └── data/, tables/
│   ├── S8_r7_figure/
│   │   └── figures/
│   ├── S8_rotation_generator/
│   │   └── data/, tables/
│   └── S9_detector_coverage/
│       └── rotation_eta0.05/, tables/
├── tests/
│   ├── test_debt_register.py
│   ├── test_manuscript_integrity.py
│   ├── test_owad_claims.py
│   ├── test_owad_snapshot.py
│   ├── test_R1_race_condition.py
│   ├── test_R2_starvation.py
│   ├── test_R3_crossover.py
│   ├── test_R4_table1.py
│   ├── test_R5_table2.py
│   ├── test_R6_hydra.py
│   ├── test_R7_regime1.py
│   ├── test_R8_lambda_op.py
│   ├── test_R9_mcrit.py
│   ├── test_S10_external_validity.py
│   ├── test_S13_bell.py
│   ├── test_S2_theory.py
│   ├── test_S2bis_calibration.py
│   ├── test_S2ter_predicate.py
│   ├── test_S3_dependence.py
│   ├── test_S6_traces.py
│   ├── test_S7_consistency.py
│   ├── test_S8_generality.py
│   └── test_S9_coverage.py
├── README.md
├── requirements.txt
├── run_all.sh
├── run_experiment_R1.sh
├── run_experiment_R2.sh
├── run_experiment_R3.sh
├── run_experiment_R4.sh
├── run_experiment_R5.sh
├── run_experiment_R6.sh
├── run_experiment_R7.sh
├── run_experiment_R8.sh
├── run_experiment_R9.sh
├── run_owad2026.sh
└── run_tests.sh
```
