# S7-ter / LOT B — arm archive

Three R4 renders and two R3 renders, kept side by side so that every numeral the stream moved can be
attributed to one cause and only one. Nothing here is an input to any pipeline; nothing here is in
`artifacts_sha256_pre_ssot.txt`. These are measurements, retained as evidence.

## The two configurations

| arm | `warning_detector` of the ARF | what it is |
|---|---|---|
| **U0** | `ADWIN(delta=0.01, clock=32)` | River 0.23.0's resolution of an **unset** `warning_detector` on `ARFClassifier`. This is what a practitioner who does not name one actually deploys, and the only configuration in which the warning genuinely leads the drift. It is also the configuration every artifact of this repository was produced under before S7-ter. |
| **U1** | `ADWIN(delta=0.002, clock=c)` | The drift detector's own configuration. Makes the two detectors exact clones: they are fed the same error sequence, fire at the same step, and no background tree ever trains. Comparable with R1, R2, R5–R9 and with `make_srp`, which already pinned both. |

The unification is therefore **two parameters, not one**: `delta 0.01 → 0.002` and `clock 32 → c`.

## Directories

| directory | contents |
|---|---|
| `u0_frozen/` | the committed pre-S7-ter artifacts, copied before any change. These **are** the U0 arm: R3 and R4 left `warning_detector` unset, which River resolves to exactly U0. |
| `b31_u1/` | R4 re-run under U1, bootstrap unchanged. Isolates the effect of the unification. |
| `b32_u1_boot/` | R4 re-run under U1 **and** the seed-paired bootstrap. Isolates the effect of the resampling unit. |
| `r3_u0/` | R3 re-run with U0 written out explicitly, for comparison against `u0_frozen/`. |
| `r3_u1/` | R3 under U1, the ablation arm. |

## Published arms

| experiment | OWAD 2026 paper (`docs/manuscript/owad2026/`) | journal manuscript v65 (`docs/manuscript/CURRENT`) |
|---|---|---|
| R3 | U0 | U0 |
| R4 | U0, intervals resampling the 360 runs of a cell: the `owad2026` arm, whose fusion and sign-test CSVs equal `u0_frozen/` byte for byte | U1, intervals resampling the 30 seeds: the current arm |

## Reproducing an arm

| arm | command | writes |
|---|---|---|
| R3 U0 | `python experiments/R3_regime_crossover/exp_R3_regime_crossover.py` (`--arm U0` is the default, and what `run_experiment_R3.sh` runs) | `results/R3_regime_crossover/` |
| R3 U1 | `python experiments/R3_regime_crossover/exp_R3_regime_crossover.py --arm U1` | the same paths as U0 |
| R4 U0, run-level intervals | `python experiments/R4_proteus_evaluation/exp_R4_main_table.py --arm owad2026` | `results/R4_proteus_evaluation/owad2026/` |
| R4 U0, seed-level intervals | the same with `--bootstrap seed` | `results/R4_proteus_evaluation/owad2026_seedboot/tables/` |
| R4 U1, seed-level intervals | `python experiments/R4_proteus_evaluation/exp_R4_main_table.py` (the current arm) | `results/R4_proteus_evaluation/data/`, `tables/` |

`--summarise-only` re-renders an R4 arm's table and sign tests from its committed fusion CSV,
without simulating. `experiments/R4_proteus_evaluation/exp_R4_kswin_sweep.py` has no arm switch:
its U0 files in `u0_frozen/` are reproduced by deleting the `warning_detector` keyword from its
`make_arf`, which River 0.23.0 resolves to `ADWIN(delta=0.01, clock=32)`. Writing that detector
explicitly is equivalent, and `r3_u0/` is the R3 run that verifies the equivalence against the
frozen artifact byte for byte.
