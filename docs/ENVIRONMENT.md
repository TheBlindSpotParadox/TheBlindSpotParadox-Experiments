# Execution environment

Record of the host, the pinned toolchain and the measured wall-clock cost of a full reproduction.
`logs/` is in `.gitignore`, so this file is the versioned trace: the manuscript's
"AMD EPYC 8224P (24 cores, 48 threads) with 192 GB RAM in ~5 h total" (Section V) is traceable here
and nowhere else in the repository.

## Host

| item        | value                                                                            |
| ----------- | -------------------------------------------------------------------------------- |
| CPU         | AMD EPYC 8224P, 24 cores / 48 threads, 1 socket, 1 NUMA node                     |
| RAM         | 196 426 176 kB (`MemTotal`) = 187.3 GiB = 192 GB nominal                         |
| OS          | Rocky Linux 9.6 (Blue Onyx)                                                      |
| Kernel      | 5.14.0-570.55.1.el9_6.x86_64                                                     |
| Interpreter | `/home/m53/miniforge3/envs/Trading/bin/python`                                   |
| Determinism | `PYTHONHASHSEED=0`, exported by every `run_experiment_R*.sh` and by `run_all.sh` |
| Parallelism | `joblib.Parallel(n_jobs=-1)`, i.e. 48 workers                                    |

The host that produced the measurements below is the same machine class the manuscript names. The
S7 audit reported it as "48-core / 187 GB" (logical threads and `MemTotal` in GiB); the manuscript
states it as "24 cores, 48 threads / 192 GB". Same host, two conventions.

## Pinned packages (conda-forge, environment `Trading`)

| package      | version |
| ------------ | ------- |
| Python       | 3.12.9  |
| numpy        | 1.26.4  |
| pandas       | 2.3.2   |
| scipy        | 1.16.2  |
| scikit-learn | 1.6.1   |
| joblib       | 1.4.2   |
| matplotlib   | 3.10.6  |
| pyarrow      | 21.0.0  |
| river        | 0.23.0  |
| tqdm         | 4.67.1  |

`river == 0.23.0` is load-bearing, not cosmetic: the instrumented experiments read the private
attributes `_drift_tracker` and `_warning_tracker` to time the internal tree swap.
`config.experiment_ssot.require_drift_tracker` raises on any River build that renames or drops them,
so a version drift fails loudly instead of yielding a stream of NaN adaptation times.

## LaTeX toolchain

Tectonic 0.17.0, installed from `conda-forge` into a **dedicated** environment (`conda create -n tex
-c conda-forge tectonic`). It is deliberately not installed into `Trading`: that environment's solve
is already constrained, and the scientific pins must not move to accommodate a document build.

```bash
conda run -n tex tectonic -X compile docs/manuscript/articleA_blindspot_v64_camera_ready.tex
```

Tectonic runs XeTeX, which substitutes for the Type 1 `ptm` faces and emits four
`LaTeX Font Warning: Font shape 'TU/ptm/...' undefined` lines. These are toolchain artefacts of the
substitution, not document defects; the committed camera-ready PDF was produced with a pdfTeX
toolchain and is not replaced by the Tectonic output.

## Measured wall-clock times

Every figure below was measured on the host above, `PYTHONHASHSEED=0`, `joblib` at `n_jobs=-1`,
one experiment at a time (no two stages share the 48 threads). The `R*` rows were measured in
stream S7-bis; the `S2-bis` rows in stream S2-bis, under the same convention — the S2-bis chain
waits for the preceding stage to release the 48 threads before starting.

| stage                     | command                                                             |                                                                                                                                     wall clock | artifact identity vs. `artifacts_sha256_pre_ssot.txt`                                                                                                                                                                                                                                                 |
| ------------------------- | ------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------: | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| R1                        | `./run_experiment_R1.sh`                                            |                                                                                                                          1 066 s (17 min 46 s) | **deviates since A1** (`R1_race_condition.parquet`), declared in `authorized_deviations.txt`                                                                                                                                                                                                          |
| R2                        | `./run_experiment_R2.sh`                                            |                                                                                                                          1 186 s (19 min 46 s) | identical (3 parquets **and** 3 PNGs)                                                                                                                                                                                                                                                                 |
| R3                        | `./run_experiment_R3.sh`                                            |                                                                                         539 s (8 min 59 s); S7-ter re-measured 587 s and 676 s | **identical under restored U0** (`R3_regime_crossover_metrics.parquet` and its 300-dpi PNG reproduce the pre-S7-ter baseline byte for byte in 587 s). The U1 ablation arm is parameterized via `--arm U1`.                                                                                            |
| R4                        | `./run_experiment_R4.sh`                                            |                                                                                  3 241 s (54 min 01 s); S7-ter re-measured 3 823 s and 3 803 s | **deviates since S7-ter/LOT B** (`exp_R4_results_aligned_fusion.csv`, `exp_R4_seed_level_tests.csv` + Table I `.tex`). The two KSWIN-sweep CSVs stay **byte-identical**: the α sweep is invariant under the unification, raw data included                                                            |
| R6                        | `./run_experiment_R6.sh`                                            |                                                                                                                                           34 s | identical                                                                                                                                                                                                                                                                                             |
| R7                        | `./run_experiment_R7.sh`                                            |                                                                                                                            732 s (12 min 12 s) | identical                                                                                                                                                                                                                                                                                             |
| R8                        | `./run_experiment_R8.sh`                                            |                                                                                                                             244 s (4 min 04 s) | **deviates since A2** (both aggregation CSVs lose the purged `lambda_limit` column; the per-seed raw grids stay byte-identical). The `_tdrift4000` arm is a second invocation, `… exp_R8_lambda_op_sweep.py 4000`, not run by the wrapper                                                             |
| R9                        | `./run_experiment_R9.sh`                                            |                                                                                                                                           53 s | **deviates since A1** (`exp_R9_mcrit_comparison.csv`; its input `results_instrumented_A_ADWIN_HAT.csv` stays identical)                                                                                                                                                                               |
| **subtotal R1–R4, R6–R9** |                                                                     |                                                                                                                  **7 095 s = 1 h 58 min 15 s** | **27 of 34 baseline hashes identical since U0 restoration** (26 under S7-ter U1, 29 before it); the seven deviations (`hydra_survival.csv`, the two A1 artifacts, the two A2 artifacts, and the two S7-ter/LOT B R4 artifacts) are declared in `results/audit_S7/_baseline/authorized_deviations.txt` |
| R-1 (S7-bis)              | `python experiments/R9_mcrit/exp_R9_generate_data.py 1`             |                                                                                                                                           46 s | new artifact (matched-clock M=1 run)                                                                                                                                                                                                                                                                  |
| R5                        | `./run_experiment_R5.sh`                                            |                                                                  **not re-measured in full**; step 5 alone (Δe) re-executed by S7-ter in 393 s | step 5 **reproduces `delta_e.parquet` byte for byte**; `delta_e_oracle.parquet` is a new artifact, not in the manifest. Steps 1–4 and 6 untouched                                                                                                                                                     |
| S2-bis P3                 | `python experiments/S2bis_calibration/s2bis_r1_ppre.py`             |                                                                                                                                          1.6 s | new artifacts; **bit-reproducible**, two runs byte-identical                                                                                                                                                                                                                                          |
| S2-bis P1                 | `python experiments/S2bis_calibration/s2bis_lambda_eq.py`           |                                                                                              **3 768 s (1 h 02 min 48 s)**, second run 3 760 s | new artifacts; **bit-reproducible on the complete grid**, the two runs byte-identical. 180 detector-free calibration runs + 1 980 full prequential runs on the three INSECTS streams                                                                                                                  |
| S2-bis P2 (subset)        | `s2bis_proteus_calibration.main(transitions=r4.TRANSITIONS[:1])`    |                                                                                                                               412 s then 411 s | determinism control on 1 of 12 transitions, all 30 seeds, all 3 regimes; **bit-reproducible**, the two runs byte-identical                                                                                                                                                                            |
| S2-bis P2 (full)          | `python experiments/S2bis_calibration/s2bis_proteus_calibration.py` |                                                                                                                  **3 794 s (1 h 03 min 14 s)** | new artifacts; 12 transitions x 30 seeds x 3 regimes, 6 PageHinkley couples calibrated and re-measured at two thresholds, an 8-point ladder on the two headline couples, and the EDDM arming diagnostic                                                                                               |
| **S2-bis subtotal**       |                                                                     | **7 564 s = 2 h 06 min 04 s** for one full reproduction (P3 + P1 + P2 full); the double runs that prove bit-reproducibility add 4 583 s on top | no R1-R9 artifact regenerated; `sha256sum -c` stays at 29 OK / 5 FAILED and the five are exactly the declared deviations                                                                                                                                                                              |
| S8 P1 (ab initio arms)    | `python experiments/S8_generality/s8_arms.py full`                  | **1 395.0 s (23 min 15 s)** | new artifacts; 100 seeds x 20 magnitudes x 5 arms = 10 000 records, 50 M trace rows. Trunk rows identical to the committed S6 rows on 6 000 / 6 000 and 30 / 30 columns (`s8_trunk_identity.json`) |
| S8 P1 (causal reading)    | `python experiments/S8_generality/s8_arms.py causal`                | 16.2 s on a warm page cache; the first pass over the corpus is I/O bound | **bit-reproducible**: `s8_causal.json`, `s8_detection_counts.csv` and `s8_trunk_identity.json` are byte-identical on replay, the 10 000-replicate seed-paired bootstrap included |
| S8 P1 (rotation)          | `python experiments/S8_generality/s8_rotation.py full`              | **1 751.2 s (29 min 11 s)** = 736.1 s (`eta = 0`) + 1 015.1 s (`eta = 0.05`) | new artifacts; 2 x 100 seeds x 20 magnitudes, arm `full`, 2 x 10 M trace rows. `data/*/traces.parquet/` gitignored, S6 regime |
| S8 P2 (mechanisms)        | `python experiments/S8_generality/s8_mechanisms.py full`            | 684 s (11 min 24 s) | new artifacts; 9 pipelines x 6 magnitudes x 30 seeds = 1 620 cells, one external calibration per pipeline (1 620 / 1 620 verdicts `OK`) |
| S8 P2-bis (marginal)      | `python experiments/S8_generality/s8_marginal.py full`              | 65.3 s | new artifacts; 400 cells, per-member pre-drift error stream over the 1 000-step warm-up at the two S3 anchors |
| S8 P3 (NumPy replication) | `python experiments/S8_generality/s8_minimal_arf.py full`           | 45 s | new artifacts; 200 cells, no River import in the module. MOA declared infeasible: `java: command not found`, no MOA jar under `/home/m53`, `skmultiflow` absent and incompatible with py3.12 / numpy 1.26 |
| **S8 subtotal**           |                                                                     | **3 957 s = 1 h 05 min 57 s** | no R1-R9 and no S6 artifact regenerated; `sha256sum -c` stays at **27 OK / 7 FAILED** and the seven are exactly the declared deviations. **No entry added to `authorized_deviations.txt`** |

S2-bis writes only under `results/S2bis_calibration/`. Its verification differs by phase and the
difference is declared in `docs/theory/S2bis_calibration.md` §2: P1 and P3 carry a **full** double
run, P2 a **declared-subset** double run plus one full grid. A second full ProteuS grid is roughly
an hour of exclusive host time for a check whose failure modes -- joblib result ordering and the
per-worker PRNG lock -- are already exercised at 30-worker scale.

R5 was not re-executed. Its BAF stage reads three ~85 MB gzipped streams for 30 seeds across three
pipelines and is documented as long-running in `run_experiment_R5.sh` (step 3). Its artifacts are
committed and were reconciled numerically in `results/audit_S7/reconciliation_report.md`; only its
runtime is unmeasured here.

**Consequence for the manuscript.** The submitted text asserted "~5 h total". That figure is not
reproducible from any committed record, and the measured subtotal above (1 h 58 min for eight of the
nine stages) does not support it once R5 is added. Section V of the manuscript of record now states
the measured 1 h 58 min for R1–R4 and R6–R9 and points here, instead of an unverifiable total.

## Bit-freeze coverage — what the manifest holds, and what it does not

`results/audit_S7/_baseline/artifacts_sha256_pre_ssot.txt` is the live integrity oracle. It holds
**34 entries**, distributed as R1 ×1, R2 ×3, R3 ×1, R4 ×4, R5 ×15, R6 ×1, R7 ×2, R8 ×4, R9 ×2,
`audit_S7` ×1. Current verdict: **27 OK / 7 FAILED**, the seven being exactly the deviations declared
in `_baseline/authorized_deviations.txt`. Five predate this stream and were re-verified by action
D-3, each against its originating commit and against the numbers the ledger claims for it: R1
`8fb0875`, R9 `8fb0875`, the two R8 aggregations `70ca9ae`, `hydra_survival.csv` `c24dc7e`. Two
are stream S7-ter's own, produced by LOT B and declared with their measured effect at the moment
they were produced: the two R4 data CSVs (the R3 metrics parquet is identical under restored U0).

Note on the re-measured wall clock: the S7-ter R3 and R4 runs are 9 % to 18 % slower than the
S7-bis reference on the same host. The reference figures are retained as the reference; the slower
times are recorded rather than substituted, because nothing in this stream isolates the cause and a
timing figure with no attribution would be a worse record than two figures with their provenance.

**The extension to R2, R3 and R7 is already discharged.** The wall-clock table above is itself the
record: each of those stages was re-executed on this host and its artifacts verified identical
against the manifest. Nothing further is owed there, and stream S7-ter declares it rather than
re-running to produce a second record of the same fact.

Two real gaps remain, and they are named here rather than left to be discovered:

| gap    | state                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **R5** | 15 of the 34 frozen hashes are R5's. Before stream S7-ter **none had ever been empirically re-verified** — they were asserted from the committed files, never from a reproduction. S7-ter/LOT C closes **one** of the fifteen: re-running step 5 of the pipeline regenerates `delta_e.parquet` byte for byte on this host, which is the first execution-backed proof for any R5 artifact. The remaining fourteen — the BAF and INSECTS evaluations, the per-episode decomposition, the checkpoints and `table2_values.csv` — still rest on the committed files alone, and closing them means paying the ~4.5 h BAF stage. |
| **S8** | **Zero entries**, same regime as S6. The S8 corpus is outside the manifest; its integrity guards are `tests/test_S8_generality.py` (generator identity, PRNG neutrality, pre-drift bit-identity, ab initio arm invariants, write perimeter, payload anchors), the D3-bis trunk gate against the committed S6 rows, and the byte-identical replay of the causal reading. |
| **S6** | **Zero entries.** The S6 Parquet corpus is outside the manifest entirely; its only integrity guard is `tests/test_S6_traces.py::test_parquet_replay_is_byte_identical`, which replays and compares rather than checking a frozen digest. The deterministic Parquet contract (`S6_PARQUET_*` in `config/experiment_ssot.py`) is what makes that replay meaningful.                                                                                                                                                                                                                                                         |
| **S9** | **Zero entries**, and one debt the other rows do not carry. The stream's offline replay reads the S6 trace corpus through `results/S6_synchronized_traces/data/traces.parquet`, which in the `stream-s9` worktree is a **symlink to an artifact outside the repository** (`/home/m53/TheBlindSpotParadox-Experiments/...`, 20 partitions, 402 MB) and is not versioned anywhere. Until that corpus is regenerated by `s6_runner.py`, **no output of `experiments/S9_detector_coverage/s9_offline_detectors.py` is reproducible from a fresh clone**: the input does not exist there. The outputs are reproducible bit for bit GIVEN the corpus -- that is what `tests/test_S9_coverage.py::test_replay_of_one_cell_is_bit_identical` and the two-pass SHA-256 comparison establish -- and the S9 trace corpus is itself gitignored under the same regime as S6's and S8's. Declared, not masked. |

**Deprecated snapshot (action D-5).** `results/audit_S7/_baseline/sha256_pre.txt` is a pre-S7
historical snapshot of 11 manuscript/editorial artifacts. **Verified: it has no consumer.** A
repository-wide search over `.py`, `.sh`, `.md`, `.yml`, `.toml` and `.cfg` finds only prose
references — its own deprecation banner, one narrative line in `reconciliation_report.md`, and the
S7-ter specification and plan; there is no CI configuration and no Makefile in the repository. Its
live state matches its banner: 6 OK, 3 FAILED, 2 paths no longer resolving
(`articleA_blindspot_v63_camera_ready.tex` absent, `docs/sections/framework_v2.tex` moved by action
A5). One of its three mismatches is instructive rather than alarming: at snapshot time the two
copies of `table2_real_data_summary.tex` carried **different** digests, and commit `7c25fe0` — a full
R5 re-run — converged the pipeline copy onto the manuscript copy, which is the drift
`tests/test_manuscript_integrity.py::test_manuscript_assets_match_the_pipeline` now prevents.
**Whether to delete the file or retain it as lineage is a repository-policy call and is escalated,
not decided here.**

## Reproducing

```bash
./run_all.sh                 # R1..R9 in dependency order, then the pytest suite
./run_experiment_R2.sh       # a single stage
sha256sum -c results/audit_S7/_baseline/artifacts_sha256_pre_ssot.txt
```

A stage that regenerates a byte-different artifact is a defect, not an update: the pipeline is
bit-reproducible on a fixed host and interpreter, and the frozen hash list is the oracle.
