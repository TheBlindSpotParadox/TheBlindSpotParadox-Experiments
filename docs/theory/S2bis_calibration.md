# Stream S2-bis — calibration measurements

The measurements, the artifact hashes and the statutory guard-rail matrix. Every assertion is
executable; none is a narrative claim. The verdicts and the manuscript payloads are in
`docs/theory/transfer_S2bis.md` and `docs/theory/S2bis_narrative_payload.md`.

## 1. Reproduction

```bash
PYTHONHASHSEED=0 python experiments/S2bis_calibration/s2bis_lambda_eq.py --check            # writes nothing
PYTHONHASHSEED=0 python experiments/S2bis_calibration/s2bis_proteus_calibration.py --check
PYTHONHASHSEED=0 python experiments/S2bis_calibration/s2bis_r1_ppre.py --check

PYTHONHASHSEED=0 python experiments/S2bis_calibration/s2bis_r1_ppre.py              # T-B, T-E   (~3 s)
PYTHONHASHSEED=0 python experiments/S2bis_calibration/s2bis_lambda_eq.py            # T-A vol. 1
PYTHONHASHSEED=0 python experiments/S2bis_calibration/s2bis_proteus_calibration.py  # T-A vol. 2, T-D

PYTHONHASHSEED=0 python -m pytest tests/test_S2bis_calibration.py tests/test_S2_theory.py \
                                  tests/test_S7_consistency.py tests/test_manuscript_integrity.py -v
sha256sum -c results/audit_S7/_baseline/artifacts_sha256_pre_ssot.txt   # expect 29 OK, 5 FAILED
git status --short                                                      # no R1-R9 artifact modified
```

Interpreter and package pins: `docs/ENVIRONMENT.md`. Run from the repository root. Measured
wall-clock times are in that file's table, one row per S2-bis stage.

**Data dependency.** `s2bis_lambda_eq.py` reads `data/insects/*.csv`, which `.gitignore` excludes;
on a clone without them the stream cannot be reproduced and
`tests/test_S2bis_calibration.py` skips the affected checks with that remedy named.
`s2bis_proteus_calibration.py` generates its own streams and needs no data file.
`s2bis_r1_ppre.py` reads only committed artifacts.

**Randomness.** No S2-bis module draws a random number outside two declared places: the seed-paired
bootstrap, which runs on `np.random.default_rng(ssot.S2BIS_BOOTSTRAP_SEED)` and is re-seeded per
statistic so it does not depend on call order; and the experiment workers, which inherit the
per-worker PRNG locks of R4 and R5 verbatim. Neither a global `np.random.seed` nor a
`random.seed` is issued at module level.

## 2. Artifact hashes

*(filled on completion of the two campaigns)*

## 3. Measurements

### 3.1 INSECTS — `lambda_eq` under both targets of rule B1

Calibration pass: 180 detector-free runs over `[0, first valid drift)`, 3 variants x 30 seeds x 2
pipelines. `T_warm` is R5's own target; `T_span` is one expected false alarm over the armed
pre-change span.

| variant | warm-up | armed span | span/warm | pipeline | `lambda_eq(T_warm)` | `lambda_eq(T_span)` | `lambda_eq^ARL` | B2 | alarms over the span at the `T_warm` threshold | B7 |
|---|---:|---:|---:|---|---:|---:|---:|---|---:|---|
| gradual_balanced | 2 414 | 11 614 | 4.81 | `pht_arf_c1` | 20.9731 ± 4.6495 | 92.9558 ± 15.4870 | 27.399 | INAPPL. (3.39) | **11.33** | OK |
| | | | | `pht_ht` | 132.5039 ± 0.0000 | 185.7085 ± 0.0000 | 36.359 | INAPPL. (5.11) | 2.00 | OK |
| abrupt_balanced | 5 284 | 9 068 | 1.72 | `pht_arf_c1` | 46.7646 ± 10.6865 | 71.8047 ± 22.5127 | 31.027 | INAPPL. (2.31) | 2.73 | OK |
| | | | | `pht_ht` | 44.9024 ± 0.0000 | 47.6035 ± 0.0000 | 34.922 | CONCORDANT (1.36) | 3.00 | OK |
| incremental_reoccurring | 7 998 | 18 570 | 2.32 | `pht_arf_c1` | 77.9377 ± 8.4657 | 233.6326 ± 18.6556 | 38.017 | INAPPL. (6.15) | 3.07 | OK |
| | | | | `pht_ht` | 182.4685 ± 0.0000 | 191.2855 ± 0.0000 | 46.024 | INAPPL. (4.16) | 4.00 | **NOT ATTAINABLE** (3 alarms at the returned threshold, target 1) |

Every `pht_ht` standard deviation is exactly zero, on both targets and all three variants: rule B10
(`n_distinct = 1` on `lambda_calibrated`, `F1_bp` and `n_detections`), **PSEUDO-REPLICATED**.

The `T_warm` column reproduces `insects_per_episode.parquet`'s frozen `lambda_calibrated` **exactly**
on all six cells, from the raw CSVs through an independent driver — the identity of
`transfer_S2bis.md` §2.1.

### 3.2 INSECTS — the flooding gate and its decomposition

Sweep: 1 980 full prequential runs (11 thresholds x 30 seeds x 2 pipelines x 3 variants; no replay
shortcut, the classifier resets on every alarm). Full tables in
`transfer_S2bis.md` §2.3, §2.3 bis and §2.4. Headline:

| | `gradual_balanced` |
|---|---|
| `rho` at the frozen calibration (`T_warm`) | **10.570** [9.354, 12.114] — reproduces Table II's 10.57 |
| `rho` at the span budget (`T_span`) | **1.270** [1.156, 1.426] |
| rule B3 verdict | **COLLAPSE** (CI upper 1.426 < 2) |
| threshold-attributable share of `ln rho` | **89.9 %**, both terms positive |
| residual `ln rho_eq` | +0.2387 [0.1451, 0.3550] |

COLLAPSE on all three variants at `lambda_eq`. On `abrupt_balanced` and
`incremental_reoccurring_balanced` the residual and threshold terms differ in sign and **no single
percentage is reported**, per rule B4.

### 3.3 ProteuS — the structural result

The pre-drift error rate is **exactly zero** on every transition, regime and seed, because
`exp_R4_main_table.simulate_stream:105` makes the target a deterministic step function of the time
index and the classifier predicts the constant pre-change label from the first step. Consequences in
`transfer_S2bis.md` §2.7. The campaign's own tables are
`results/S2bis_calibration/tables/s2bis_{lambda_eq_proteus,proteus_sweep,proteus_eddm_arming}.csv`
and `s2bis_proteus_gate.json`.

### 3.4 R1 / R2 — the reference rate, analytic

`transfer_S2bis.md` §3. Effective tolerance 0.036 against a nominal 0.010 (factor 3.6); `theta*`
0.6813 -> 1.7001; `ARL_0(15)` x 4.83e5; post-drift accumulation −28.9 % at `Delta_e = 0.10` and
−8.1 % at 0.33. Effect on the two published numerals: **exactly zero**. Within-run counterfactual in
`s2bis_r1_counterfactual.csv`.

## 4. Verdicts

| rule | verdict |
|---|---|
| B1 | both targets reported; `T_span` carries the verdict, `T_warm` reproduced exactly |
| B2 | **ANALYTIC MODEL INAPPLICABLE** on 5 of 6 INSECTS cells, CONCORDANT on 1 — published, not tuned |
| B3 | **COLLAPSE** (`rho` 10.570 -> 1.270 [1.156, 1.426] on `gradual_balanced`; COLLAPSE on all three variants at `lambda_eq`) |
| B4 | `gradual_balanced` **89.9 %** threshold-attributable, both terms positive; the other two variants publish two signed terms and no percentage |
| B5 | **UNDOCUMENTED DELIBERATE CHOICE** — no re-run warranted |
| B6 | **REFUTED** on both tests |
| B7 | fired: one cell **NOT ATTAINABLE**; ProteuS **NOT BINDING**, a floor case the rule did not declare |
| B8 | applied; `[0.015, 0.032]` used only for S6-anchored statements |
| B9 | applied; `R_KSWIN` quoted at both `alpha` (22.68 deployed, 41.997 common) |
| B10 | **PSEUDO-REPLICATED** on all three variants |

## 5. Statutory guard-rail matrix

`tests/test_S2bis_calibration.py`. Each row states the expected behaviour and the reason a naive
expectation would be wrong. Rows 1-6 are the guard-rails rule B7 and rule B3 declare; rows 7-8 are
the two evaluator identities every measurement in this stream rests on.

| input | expected | why the opposite would pass on a wrong premise |
|---|---|---|
| `p_true >= p_pre + delta` | `cramer_root` raises `ValueError`; `lambda_eq_arl` returns `None` with the reason recorded | the null drift is non-negative, so the CUSUM has no positive Cramér root and `ARL_0` is `0/0`. A solver that returned the trivial root `theta = 0` would hand back `ARL_0 = 0/0` as a finite threshold, and nothing downstream would notice |
| `lambda_eq` at the bisection **ceiling** | **`SATURATED`**, reported as a bound and never as a value | `calibrate_lambda` returns `high`, which equals the bracket's upper end when the budget is unmet at every midpoint. A caller reading it as a calibrated threshold would publish "500" as a measurement |
| `lambda_eq` at the bisection **floor** | **`NOT BINDING`**, reported as a bound | the mirror case, **not declared by rule B7**, and the one ProteuS actually returns. A budget met at every admissible threshold constrains nothing; reading the floor as a calibration would publish `lambda_eq ~ 1` as a property of the pipeline |
| budget unmet at the returned threshold | **`NOT ATTAINABLE`** with the attained count and the span | `calibrate_lambda` falls back from `target_fa = 1` to `3` and then returns `high` regardless. Without the post-hoc count, a cell that never met its budget is indistinguishable from one that did |
| span shorter than the arming time | **`NOT ARMED`**, no `lambda_eq` reported | River's PageHinkley does not test before `min_instances = 30` observations, and EDDM before `warm_start = 30` **errors**. A short span returns zero alarms, which a naive reading scores as a *good* calibration |
| `F1 = 0` in one arm | the ratio is undefined; rule B3's declared `dF1` path is taken | `F1_HT / F1_ARF` with `F1_ARF = 0` is `inf`, which sorts above any threshold and would return `SURVIVES` on a degenerate cell |
| `lambda_eq` vs `p_true` at a fixed target | monotone **increasing** | the plan states *decreasing*. `theta*` shrinks as `p(1-p)` grows and `ARL_0` is increasing in `theta`, so a noisier pre-change stream costs **more** threshold. A test written in the plan's direction would fail on correct code and invite a "fix" that inverts the estimator |
| `run_at_lambda` at the calibrated `lambda` | detections, error stream and threshold **identical** to `exp_R5_common.run_evaluation` | the injected-threshold driver is the only new loop in the stream. If it diverged, every `lambda`-sweep point would be measuring a different pipeline from the one Table II reports |
| `evaluate_full` | `(ADD, F1)` identical to `exp_R4_main_table.evaluate` | S2-bis adds the precision R4 computes and discards. If the matching moved, the added columns would describe a different scorer from the one Table I reports |

## 6. Write perimeter, as executed

Created: `docs/prompts/s2bis-decision-rules.md`, `experiments/S2bis_calibration/**`,
`results/S2bis_calibration/**`, `docs/theory/S2bis_calibration.md`,
`docs/theory/S2bis_narrative_payload.md`, `docs/theory/transfer_S2bis.md`,
`tests/test_S2bis_calibration.py`.

Append-only: one `# S2-bis —` banner block at the end of `config/experiment_ssot.py`, below the S2
block; no existing line touched. One row per stage in the wall-clock table of
`docs/ENVIRONMENT.md`.

Never patched, and verified so by `git status --short`: the manuscript of record,
`docs/manuscript/sections/*.tex`, `results/**` outside `results/S2bis_calibration/`,
`experiments/R1..R9/**`, and the four excluded inline subsections `sec:race`, `sec:hydra`,
`sec:starvation`, `sec:decoupling`.

Every artifact this stream produces carries an `s2bis_` basename and lives under
`results/S2bis_calibration/tables/`, so it collides neither with the 34 named paths of
`results/audit_S7/_baseline/artifacts_sha256_pre_ssot.txt` — an open-world, per-file check, so a
new directory adds no line and the verdict stays `29 OK, 5 FAILED` — nor with the basename glob of
`tests/test_manuscript_integrity.py:68-69`. **No entry is added to
`results/audit_S7/_baseline/authorized_deviations.txt`**, following the S2 precedent.
