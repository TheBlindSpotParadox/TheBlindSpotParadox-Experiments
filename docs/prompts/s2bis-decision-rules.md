# Stream S2-bis — decision rules, fixed before measurement

Committed before any S2-bis script is run and before any S2-bis output is read. Every rule carries
its numeric threshold and its verdict on **both** sides, so no outcome of the stream can be
arbitrated after the fact. The shape follows `docs/prompts/s2-decision-rules.md`: no point estimate
is ever the decision variable.

Stream branch `stream-s2bis`, parent `3f59b35` (S2 close, phases 0–7).

---

## B0 — honesty declaration

The planning phase has already read the `lambda = 15` baseline in full. The rules below are blind
**only** with respect to the new measurements at `lambda_eq`. What was read before this file was
written:

- `results/S2_theory/tables/s2_flooding_retrodiction.json` — `lambda_calibrated` means 20.973
  (`pht_arf_c1`) and 132.504 (`pht_ht`), 85.67 alarms against 7.0, precision 0.0118 against 0.1429,
  `e_pre` 0.0580 against 0.0754, `e_post` 0.4979 against 0.4432, armed pre-change span 11 613.1,
  warm-up 2 414.9, `n_total` 24 149.
- `results/S2_theory/tables/s2_gate_T20.json` — the common-`alpha` ladder, the measured ceiling
  33.5115, the chord floor interval `[13.875, 18.288]`, `R_KSWIN_at_deployed_alpha = 22.679`,
  `1/theta* = 1.4678`.
- `experiments/R5_real_world_evaluation/exp_R5_common.py` — `calibrate_lambda` (`:59-85`) and
  `run_evaluation` (`:88-145`) in source.
- The seed-invariance of `pht_ht`: `lambda_calibrated_min == lambda_calibrated_max == 132.504`
  in the same artifact.
- `experiments/R1_race_condition/exp_R1_generate_data.py:56` and `:107-121` — the two-arm design and
  which arm feeds the published aggregation.
- `git log` on `docs/theory/transfer_S1.md`, `CUSUM_DELTA_P` and `P0_MEASURED`.

Two premises of the S2-bis brief were contradicted by source before this file was written, and both
are recorded here rather than discovered later:

- **R5 does not run at `lambda = 15`.** `exp_R5_common.py:121-123` calibrates per
  (variant, seed, pipeline). Table II's 10.57x is already an equal-false-alarm-budget comparison at
  the target *one false alarm per warm-up*. The site where `lambda = 15` is genuinely common is
  **R4** (`exp_R4_main_table.py:165`), which runs with **no warm-up at all**.
- **R1's mis-set `p_pre` does not touch the published numerals.** `exp_R1_generate_data.py:56`
  feeds `tau_det_fixed`, a column no aggregation reads; `Share_Blind_Spot` and `Detection_Rate` are
  built at `:136-139` from the empirical arm.

---

## B1 — the `ARL_0` target

Two targets, both reported, the first carrying the verdict.

| target | definition | provenance |
|---|---|---|
| `T_span` | one expected false alarm over the **armed pre-change span** of the stream — the span the detector actually runs under the no-change law | protocol-defined, no free parameter |
| `T_warm` | one expected false alarm over the **warm-up** length — the target `exp_R5_common.calibrate_lambda` already uses (`PHT_TARGET_FA = 1`) | `exp_R5_config.py:89` |

Both are identical across pipelines on the same stream, so neither introduces a per-pipeline degree
of freedom. `T_span` carries the verdict because it is the budget over the span that produces the
alarms being counted; `T_warm` is reported beside it as the existing calibration's own target.

---

## B2 — the `lambda_eq` estimator

| estimator | definition | role |
|---|---|---|
| `lambda_eq^emp` | bisection to `<= 1` false alarm on the target span, detector re-armed after each alarm — `calibrate_lambda` with the span substituted for the warm-up | **carries the verdict** |
| `lambda_eq^ARL` | Siegmund inversion `arl0_inverse(target, theta*(p_pre, p_true), drift)` with `theta*` measured per pipeline | consistency check |

| condition | verdict |
|---|---|
| `max(lambda_eq^emp, lambda_eq^ARL) / min(...) <= 2` on a given (stream, pipeline) | the analytic model is **CONCORDANT** on that cell; both numbers are reported |
| ratio `> 2` | the analytic model is declared **INAPPLICABLE** to River's adaptive-mean PageHinkley on that cell. The disagreement is published as a finding with both numbers; it is never tuned away, and no parameter is moved to close it |

---

## B3 — the flooding gate (escalation criterion)

Decision variable
`rho_eq = F1(PHT+HT at lambda_eq) / F1(PHT+ARF c=1 at lambda_eq)` on INSECTS *gradual_balanced*,
`F1` being `F1_bp` (the bipartite score of `exp_R5_config.F1_COL`), with a **seed-paired bootstrap
CI** (10 000 resamples of the 30 seed-level pairs, seed 12345). Reference `rho = 10.57` at the
existing calibration.

| condition on the CI | verdict |
|---|---|
| CI **upper** bound `< 2` | **COLLAPSE** — the flooding ratio at a common false-alarm budget is an artefact of calibration. Escalate before T-C; the narrative payload is written against the new reading |
| CI **lower** bound `> 5` | **SURVIVES** — flooding is an effect of the coupling and the paper gains the fairness control |
| otherwise | **INTERMEDIATE** — publish the decomposition (B4), never an average |

**Degenerate handling, fixed here and not after the measurement.** If either `F1` is exactly 0 the
ratio is undefined. The verdict is then read off `dF1 = F1_HT - F1_ARF`, whose range is `[-1, 1]`,
with the same three bands scaled to the unit interval: CI upper bound `< 0.02` -> COLLAPSE, CI lower
bound `> 0.05` -> SURVIVES, otherwise INTERMEDIATE. Both statistics are computed and reported in
every branch; only the declared one arbitrates.

None of the three branches is a failure.

---

## B4 — decomposition (T-A d)

Four cells `{ARF, HT} x {lambda_ref, lambda_eq}`, read off the same lambda-sweep:

```
ln rho(lambda_ref) = ln rho_eq
                   + [ (ln F1_HT(lambda_ref)  - ln F1_HT(lambda_eq))
                     - (ln F1_ARF(lambda_ref) - ln F1_ARF(lambda_eq)) ]
```

Two numbers with CIs: the **residual** `ln rho_eq` and the **threshold-attributable** bracket. No
single "percentage explained" is reported unless both terms share a sign; when they do not, the
decomposition is published as two signed terms and the ratio of the ratio is not reduced to a
percentage. A zero `F1` in any cell makes the log form undefined on that cell: the cell is then
reported on the difference scale with the substitution declared, never with an epsilon added.

---

## B5 — R1 `p_pre` status (T-B d)

| condition | verdict |
|---|---|
| any published numeral routes through `tau_det_fixed` (the arm built at `exp_R1_generate_data.py:56`) | **DEFECT** — one sentence owed to the manuscript **and** a re-run of R1 is required |
| no published numeral routes through it | **UNDOCUMENTED DELIBERATE CHOICE** — one sentence owed to the manuscript, no re-run warranted on this ground |

The sentence is owed in either branch. Only the first branch is a re-run trigger, and the re-run
decision belongs to the orchestrator, not to this stream.

---

## B6 — R1(b) coincidence (T-E)

`transfer_S1.md` L73 states the universal floor at 4.56 for `Delta_e = 0.10`, `W = 13`; S2
reproduces 6.277 under L73's identified inputs (`p_0 = 0.05`, `delta_P = 0.005`, `eps = 0.05`,
`lambda = 50`). The hypothesis under test is that 4.56 was computed with R1's **effective
tolerance** 0.036 = `p_pre + delta_P - p_true` rather than with `delta_P`.

**CONFIRMED requires both tests to pass:**

1. *Numeric.* The floor evaluated at `p_0 <- 0.0360`, all other inputs as identified at L73, rounds
   to 4.56 at the printed precision (two decimals).
2. *Chronological.* 0.036 was computable when the line was written: both `CUSUM_DELTA_P = 0.01` and
   `P0_MEASURED = 0.024` existed at or before the commit that introduced the line.

| condition | verdict |
|---|---|
| both tests pass | **CONFIRMED** — R1(b) is a second symptom of the same configuration defect, not an independent reproduction failure |
| either test fails | **REFUTED** — R1(b) stands as S2 recorded it (UNREPRODUCED), and the coincidence is arithmetic only |

The competing explanation `Delta_max = 0.137` is evaluated and reported beside the verdict in both
branches.

---

## B7 — saturation and arming

Three terminal, publishable verdicts. None is a reason to widen a bracket or to relax a target.

| condition | verdict |
|---|---|
| bisection returns the ceiling of its bracket (500.0 for `calibrate_lambda`) | **SATURATED** — the ceiling is reported as a bound, never as a value of `lambda_eq` |
| the target false-alarm count is not attainable on the available span at any `lambda` in the bracket | **NOT ATTAINABLE** — the attained bound is reported with the span that produced it |
| the span is shorter than the detector's arming time (`min_instances = 30` for River PageHinkley; `warm_start = 30` errors for EDDM) | **NOT ARMED** — no `lambda_eq` is reported for that cell and the arming deficit is stated |

---

## B8 — bands

Any statement consuming `ARL_0` is written as an **interval** over the per-run `p_true` band of
**its own** stream and pipeline, measured from that campaign's own seeds. The band `[0.015, 0.032]`
belongs to the S6 Bernoulli arm (`s2_gate_T20.json`, `p_true_sensitivity.band_used`) and is used
only for S6-anchored statements. An INSECTS or ProteuS statement uses the band measured on that
stream, or states that it has none.

---

## B9 — alpha disclosure for family requirements (T-C)

Every requirement `R_CUSUM`, `R_ADWIN`, `R_KSWIN` is reported **with the `alpha` it is read at**.
`R_KSWIN = 22.679` is the *deployed* reading at `alpha = R4_KSWIN_ALPHA = 0.005`; at the common
`alpha` implied by a `lambda = 50` CUSUM (`alpha ~ 6.3e-16`) the same artifact gives 41.997. A
requirement quoted without its `alpha` is a defect of statement, and both numbers appear wherever
one does.

---

## B10 — pseudo-replication (T-A, reads only)

`build_model` returns an unseeded `tree.HoeffdingTreeClassifier()` for every `*_ht` pipeline, so the
30 `pht_ht` runs of a given variant are one deterministic run repeated 30 times.

| condition | verdict |
|---|---|
| `lambda_calibrated`, `F1_bp` and `n_detections` each have zero variance across the 30 seeds on all three INSECTS variants | **PSEUDO-REPLICATED** — the effective number of independent HT replicates is 1 on that arm, and the Table I/II caption's *"seed is the unit of statistical independence"* does not hold for it |
| any of the three varies | **REPLICATED** on that arm, with the measured dispersion reported |

The verdict is read on the frozen artifacts; nothing is regenerated. Under PSEUDO-REPLICATED the
consequence for the reported `p` is stated as a bound, not as a corrected `p`-value.
