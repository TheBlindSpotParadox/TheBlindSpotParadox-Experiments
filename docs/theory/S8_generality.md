# Stream S8 — mechanistic generality report

Verdicts of the S8 campaigns against the decision rules fixed in
[`docs/prompts/s8-decision-rules.md`](../prompts/s8-decision-rules.md) (`eee494c`), committed before
any output was read. Every number below is read from a committed artifact; the commands that
regenerate them are at the end.

Stream branch `stream-s8`, parent `a03380f`. Plan of record: [`docs/plans/PLAN_S8.md`](../plans/PLAN_S8.md).

**S8 measures. It edits no section of the manuscript.** Manuscript charges are delivered unapplied in
[`transfer_S8.md`](transfer_S8.md); charges landing on `sec:race`, `sec:hydra`, `sec:starvation` or
`sec:decoupling` are routed to `docs/manuscript/sections/framework_v2.tex` per `CLAUDE.md`.

---

## 0. D0 — every published numeral S8 carries forward, re-derived

D0 forbids carrying a numeral on the strength of the planning phase's reading. All five are
re-derived mechanically by `experiments/S8_generality/s8_arms.py d0` from the committed artifacts.

| numeral | quoted | re-derived | source of the quotation | verdict |
|---|---:|---:|---|---|
| `\LearnShare` (`share_learn`, `a_pos_common`) | `0.993371` | `0.993371` | `S6_causal_evidence.md:157` | **REPRODUCED** |
| Hydra RMST ratio at `Delta_e = 0.141` | `4.1175` | `4.1175` | `hydra_survival.csv`, `transfer_S3.md` | **REPRODUCED** |
| Hydra RMST ratio at `Delta_e = 0.327` | `7.99` | `7.9909` | `.tex:224`, `sec:hydra` | **REPRODUCED** |
| `min_Delta_e median(A / A_rect)` | `-14.12` | `-14.1161` | `S6_causal_evidence.md` §3 | **REPRODUCED** |
| switch point of the canonical family | `0.452271` | `0.452271` | idem | **REPRODUCED** |
| R7 band means, three clock configurations | `76/39/63`, `72/6/2`, `70/6/3` | identical | `exp_R7_regime1_miss_summary.tex` | **REPRODUCED** |

`\LearnShare` is a trace-level quantity and `results/S6_synchronized_traces/data/traces.parquet/` is
gitignored and regenerable, so it is recomputed on the S8 campaign's own `tau_swap`-anchored arms.
That substitution is licensed by D3-bis below and by nothing else: those rows are identical to the
committed S6 rows, column by column.

Artifact: `results/S8_ab_initio/tables/s8_d0_reproduction.json`.

---

## 1. T8.1 — the ab initio arms

### 1.1 Campaign

| item | value |
|---|---|
| grid | 100 seeds x 20 canonical magnitudes x 5 arms = 10 000 run records |
| stream | canonical family, `N_STEPS = 8000`, drift at `t = 4000`, `M = 10`, `c_int = 1` |
| traces | 50 000 000 rows, `[tau* - 1000, tau* + 4000)`, hive-partitioned by `delta_e` |
| wall clock | 1 395.0 s (23 min 15 s) on 48 threads, `PYTHONHASHSEED=0` |
| artifacts | `results/S8_ab_initio/data/` (516 MB), `tables/` |

Arms. `full`, `no_swap` and `frozen` are the S6 arms, unchanged. `no_swap_ab_initio` and
`frozen_ab_initio` are `copy.deepcopy` forks taken at `tau*` — the drift instant, BEFORE any
post-drift replacement — with both internal detector paths made inert; the second additionally stops
`learn_one`. `static` is excluded: `S6_causal_evidence.md` §8.5 declares it unmatched in capacity.

Why the S6 arms could not answer. `no_swap` and `frozen` fork at `tau_swap^(1/M)`, **after** the
`learn_one` that produced the first replacement, so all three S6 arms carry that replacement
identically and no contrast between them can attribute anything to it —
`s6_causal.erasure_share` says so in its own docstring, and `rem:cf_scope` (.tex:233) says so in the
manuscript. The S6 fork point is also **endogenous**: it is a property of the trunk's trajectory and
differs from seed to seed. `tau*` is exogenous, fixed by the protocol, which is what restores the
pairing.

### 1.2 D3-bis — trunk acceptance gate (blocking, read first)

**PRESERVED.** The `full` / `no_swap` / `frozen` rows of `results/S8_ab_initio/data/runs.parquet` are
identical to the homonymous rows of `results/S6_synchronized_traces/data/runs.parquet`, joined on
`(seed, delta_e, arm)`: **6 000 of 6 000 rows, 30 of 30 columns, zero divergence**. The extra
`deepcopy` taken at `tau*` perturbs nothing — `deepcopy` reads state and consumes no entropy, and
this is the measurement of that, not the argument for it.

Artifact: `results/S8_ab_initio/tables/s8_trunk_identity.json`.

### 1.3 The decomposition, made exact

With `frozen_ab_initio` as the single reference anchored at `tau*`, the identity closes with no
residue. Budget statistic `A := a_pos_common`, the positive-part budget of `def:budget` integrated
over the **same** window `[0, T_h)` for every arm.

```
E_total      = A_frozen_abinit - A_full          all post-tau* adaptation
E_learn_pure = A_frozen_abinit - A_abinit        learning alone, no tree ever replaced
E_swap_first = A_abinit        - A_no_swap       the FIRST replacement, isolated
E_swap_rest  = A_no_swap       - A_full          every later replacement
```

Pooled over 1 999 of 2 000 cells (one dropped for `E_total <= 0`), measured additivity residual
`2.27e-13`:

| term | median | share of `E_total` | 95 % seed-paired bootstrap CI |
|---|---:|---:|---|
| `E_total` | 915.09 | 100 % | — |
| `E_learn_pure` | 901.98 | **98.64 %** | `[98.48, 98.82]` |
| `E_swap_first` | 5.56 | **0.71 %** | `[0.63, 0.78]` |
| `E_swap_rest` | 5.14 | **0.56 %** | `[0.47, 0.67]` |

Read on `a_signed_common` and on `a` the three shares are `97.96 / 1.14 / 0.86 %`; the ordering and
every verdict below are unchanged across the three budget columns.

### 1.4 D1 — the replacement mechanism is NOT INERT

`share_swap_all = (A_abinit - A_full) / E_total = 1.36 %`, 95 % CI `[1.18, 1.52]`.

The CI **is** inside the `[0, 5 %]` inertness band. The paired sign test is not: 1 706 of 1 998
differences positive, `p = 1.9e-242`, median `+11.81`. D1 requires **both**, so the verdict is
**NOT INERT** — the replacement mechanism is *small*, not inert, and the two words are not
interchangeable at this sample size.

### 1.5 D2 — the first replacement has its own contribution: MEASURED

`share_swap_first = 0.71 %`, 95 % CI `[0.63, 0.78]`, strictly positive. **The first replacement
alone carries more erasure than every later replacement combined** (0.71 % against 0.56 %).

`\LearnShare = 99.3` is `E_learn / E_total` with an `E_learn` that **contains** the first swap. The
tau*-anchored measurement reattributes it:

> `\LearnShare` restated: **98.6** (`98.64 %`, 95 % CI `[98.48, 98.82]`, n = 1 999), against the
> published `99.3`. The 0.7 points are the first replacement, which the S6 arms could not separate.

Per magnitude the decomposition is stable from `Delta_e >= 0.19` upward (`E_learn_pure` between
98.1 % and 98.7 %, `E_swap_first` between 0.60 % and 0.93 %). At `Delta_e = 0.028` it degenerates —
`E_total` has median 17.1 and the ratio is dominated by runs near zero, giving `share_learn > 1` and
negative swap shares. That magnitude is reported and excluded from no pooled statistic; the pooled
median is robust to it by construction.

### 1.6 D3 — the decisional reading

External StrictCUSUM at `lambda = 50`, `delta_P = CUSUM_DELTA_P = 0.01`, window `[0, T_h)`,
`p_pre` measured on each trajectory's own traced pre-drift window. Counts out of 100 seeds.

| `Delta_e` | `full` | `no_swap` | `no_swap_ab_initio` | `frozen` | `frozen_ab_initio` |
|---:|---:|---:|---:|---:|---:|
| 0.085 | 0 | 0 | 0 | 41 | 100 |
| 0.141 | 0 | 0 | 1 | 69 | 100 |
| 0.194 | 1 | 4 | 14 | 94 | 100 |
| 0.243 | 1 | 12 | 28 | 97 | 100 |
| **0.327** | **0** | **18** | **49** | 100 | 100 |
| 0.436 | 0 | 20 | 59 | 100 | 100 |
| 0.498 | 0 | 7 | 44 | 100 | 100 |

The two trunk counts at `Delta_e = 0.327` reproduce the published `0/100` and `18/100` exactly.

**This is the result of the arm.** A contribution of `0.71 %` of the erasure budget converts into a
**31-point** swing in detection rate — `18/100` to `49/100` — which is larger than the 18 points
bought by suppressing every *subsequent* replacement. The first replacement is nearly invisible
volumetrically and decisive at the threshold, which is the same "small residue, flipped decision"
structure `S6_causal_evidence.md` §5 found for the Hydra, now attributed one level deeper.

Artifacts: `results/S8_ab_initio/data/s8_causal.json`,
`results/S8_ab_initio/tables/s8_detection_counts.csv`.

### 1.7 Per-tree `tau_i` — `transfer_S3.md` §6 open item 1, CLOSED

`s3_competing_risks.py:23-27` states the gap in full: *"no committed artifact carries the per-tree
`tau_i` of the ARF"* — only the four order statistics `tau_swap^(q)`. The information was already
inside `segment()`'s per-key tracker diff; P1 persists it at no simulation cost.

`results/S8_ab_initio/data/s8_tau_per_tree.parquet`: 100 000 rows (20 magnitudes x 5 arms x 100
seeds x 10 trees), 0.04 MB. `tests/test_S8_generality.py::test_per_tree_tau_reproduces_the_published_order_statistic`
checks the vector against the published order statistics on every cell of the smoke artifact.

What it shows that the order statistics could not: within a single run, the **last** tree to be
replaced lags the first by a median factor of 9.1 to 23.4 across the grid (arm `full`).

| `Delta_e` | median `tau_i` | q05 | q95 | censored | median within-run `max_i tau_i / min_i tau_i` |
|---:|---:|---:|---:|---:|---:|
| 0.028 | 950.0 | 94.7 | 2847.5 | 2.6 % | 20.09 |
| 0.141 | 1421.0 | 246.2 | 3107.2 | 1.5 % | 9.13 |
| 0.327 | 207.5 | 45.0 | 1335.4 | 0.2 % | 23.35 |
| 0.498 | 53.0 | 25.0 | 517.8 | 1.5 % | 14.83 |

---

## 2. T8.6 — the standalone R7 figure

`space_constraints_audit.md` §2.1 reserves this: the only compression declared in the source is the
one-line `% Figure 4 merged with Figure 2 above to respect ICDM page limits.` (.tex:327,
`sec:hardware`, outside the excluded zone), and the absorbed figure carried the R7 clock-mismatch
regime.

R7 is **not** re-executed. `experiments/S8_generality/s8_figure_r7.py` reads the committed
`results/R7_clock_mismatch/tables/exp_R7_regime1_miss_curve.csv` (60 rows, 3 configurations x 20
magnitudes) and writes `results/S8_r7_figure/figures/Fig_R7_clock_mismatch.png`. Its band means
reproduce `exp_R7_regime1_miss_summary.tex` exactly: `76/39/63`, `72/6/2`, `70/6/3`.

The manuscript copy is **not deposited**. Inserting a figure changes the pagination and
`space_constraints_audit.md` §4 makes that wait for the M8 arbitration on the target venue. The
`\begin{figure}` block, ready to insert, is in `transfer_S8.md`;
`tests/test_manuscript_integrity.py::test_manuscript_assets_match_the_pipeline` globs
`results/*/figures/<name>`, so the pipeline twin is already in place for the day the copy lands.

---

## 3. T8.2 and T8.5 — the rotation generator and the high-magnitude domain

### 3.1 The defect, and the correction

The canonical family labels `y = 1[x0 + x1 > b]` with `b = sqrt(2) Phi^-1(0.5 + Delta_e)`, so the
post-drift class prior is `P(y = 1) = 0.5 - Delta_e`. Over the last seven points of the grid it falls
under 2.5 %, and at `Delta_e = 0.498` the majority-class predictor reaches an error of `0.002` —
**under** the measured `e_pre = 0.024`. That is mechanically the `A / A_rect = -14.12` of
`S6_causal_evidence.md` §3: at those magnitudes the drift makes the problem *easier*.

The pre-drift stream already **is** the rotation at `phi = pi/4`, so only the post-drift half-plane
turns:

```
phi     = pi/4 + pi Delta_e / (1 - 2 eta)
y_pre   = 1[x0 + x1 > 0]                                   canonical, bit-identical
y_post  = 1[cos(phi) x0 + sin(phi) x1 > 0]
```

Two half-planes through the origin whose normals are separated by `theta` disagree, under an
isotropic Gaussian, on exactly `theta / pi` of the mass. The class balance stays 50/50 at every
magnitude. Declared label noise `eta`, applied to both phases, makes the Bayes error `eta` rather
than `0` and leaves `Delta_e = (1 - 2 eta) theta / pi` exact.

**CONSTRAINT 1, verbatim.** `rng.normal(size=(N_STEPS, 2))` is untouched: two normal draws per step,
same order, same consumption. The label-noise draws come from a **separate** `Generator` spawned off
`SeedSequence(safe_seed)`. `tests/test_S8_generality.py` asserts both, plus that the pre-drift labels
at `eta = 0` are byte-identical to the canonical family's.

| item | value |
|---|---|
| grid | 2 `eta` arms x 100 seeds x 20 magnitudes x 1 arm (`full`) = 4 000 run records |
| wall clock | 736.1 s (`eta = 0`) + 1 015.1 s (`eta = 0.05`) = 1 751.2 s (29 min 11 s) |
| traces | 2 x 10 000 000 rows; `data/*/traces.parquet/` gitignored, same regime as S6 |
| artifacts | `results/S8_rotation_generator/data/` (215 MB), `tables/` |

### 3.2 D4 — generator identity: HELD

`|Delta_e_measured - (1 - 2 eta) theta / pi| <= 3 SE` at **40 of 40** grid points, worst deviation
`2.50 SE` (`eta = 0`, `Delta_e = 0.141`). Measured on the labels with the pre-drift Bayes rule as the
oracle, never off a trained classifier: `Delta_e` is a property of the generator, and reading it
through a learner would confound the two. Measured Bayes error `0.000000` at `eta = 0` and `0.050055`
at `eta = 0.05`.

Artifact: `results/S8_rotation_generator/tables/s8_rotation_identity.csv`.

### 3.3 D5 — the null is not degenerate on either arm

| arm | `e_pre` median | range over the grid | sd across seeds | pre-drift FA rate by `lambda` (50 / 25 / 8 / 4 / 2 / 1) |
|---|---:|---|---:|---|
| `eta = 0` | 0.0240 | [0.0120, 0.0400] | 0.0046 | 0.00 / 0.00 / 0.00 / **0.37** / 0.96 / 1.00 |
| `eta = 0.05` | 0.0690 | [0.0480, 0.0850] | 0.0080 | 0.00 / 0.00 / **0.18** / 0.96 / 1.00 / 1.00 |

**NON-DEGENERATE on both.** Two readings beyond the verdict:

- `e_pre = 0.0240` at `eta = 0` is the canonical family's own value, to four decimals. That is the
  cross-check that the pre-drift phase really is bit-identical, obtained from the campaign rather
  than from the construction.
- At `eta = 0.05` the Bayes floor is `0.05` and the measured `e_pre` is `0.069`: the ARF pays `0.019`
  above Bayes. That arm is the only one of the two carrying a binding false-alarm budget, which is
  why T8.3 runs on it.

### 3.4 D6 — the high-magnitude switch point

`A / A_rect`, median over 100 seeds, arm `full`:

| `Delta_e` | canonical | rotation `eta = 0` | rotation `eta = 0.05` |
|---:|---:|---:|---:|
| 0.085 | 0.74 | 0.61 | 0.59 |
| 0.194 | 1.79 | 0.60 | 1.23 |
| **0.243** | 2.18 | **−0.69** | 1.22 |
| 0.327 | 2.70 | 1.99 | 3.84 |
| **0.452** | **−0.15** | 6.91 | 7.12 |
| 0.498 | **−14.12** | **+7.96** | **+8.03** |

| dataset | D6 switch point | verdict |
|---|---|---|
| canonical family | 0.452271 | **PRESENT** (reproduces the published value) |
| rotation `eta = 0` | 0.242568 | **PRESENT** |
| rotation `eta = 0.05` | — | **ABSENT** |

**The prediction written before reading was that the switch must disappear. It disappears at
`eta = 0.05` and the rule fires at `eta = 0`, so the verdict is reported as the rule renders it and
the rule is not retro-edited.** What it fires on is not the phenomenon the rule was written to
detect, and the fraction of negative runs is what shows it:

| dataset | `Delta_e` | median `A / A_rect` | IQR | fraction of runs negative |
|---|---:|---:|---|---:|
| canonical | 0.452 | −0.15 | [−2.52, 1.81] | 0.51 |
| canonical | 0.498 | −14.12 | [−18.37, −9.37] | **1.00** |
| rotation `eta = 0` | 0.243 | −0.69 | [−1.53, 0.04] | 0.74 |
| rotation `eta = 0` | 0.287 | +0.40 | [−0.42, 1.25] | 0.35 |
| rotation `eta = 0` | 0.498 | +7.96 | [6.28, 10.89] | **0.01** |
| rotation `eta = 0.05` | 0.498 | +8.03 | [6.25, 11.61] | **0.00** |

The canonical family's ratio descends monotonically past `Delta_e = 0.33` into a regime where
**every** run is negative. Neither rotation arm has any analogue: both climb monotonically to `+8`
at the top magnitude. What `eta = 0` has instead is an **isolated mid-band dip** at
`Delta_e = 0.2426`, 74 % of runs negative, with positive medians on both sides.

Mechanism, and it is not the prior. At `eta = 0` the Bayes error is exactly `0` while
`e_pre = 0.024` is the learner's own imperfection, so after adapting the ARF keeps improving past
its pre-drift level on a noiseless problem and `A = sum(err - e_pre)` turns negative. At
`eta = 0.05` the Bayes floor is above `e_pre - 0.019` and the post-drift error cannot fall that far.
That is exactly the degeneracy CONSTRAINT 1-bis names and the reason the `eta = 0.05` arm exists.

**Verdicts.** The high-magnitude collapse of the canonical family **is** a generator artefact: it has
no analogue on a generator with a stable 50/50 prior. The `eta = 0` dip is a **second** degeneracy,
of the zero-Bayes-error kind, not a survival of the first.

**Declared gap, not repaired.** D6's `inf{Delta_e : median(A/A_rect) < 0}` does not discriminate an
isolated band from a regime; one negative grid point anywhere fixes the infimum. The rule is left as
written and the discrimination is made by the fraction-negative column above. Same treatment
`s2bis_proteus_calibration` gave its undeclared `NOT BINDING` case: the rules file is not
retro-edited, the gap is declared here.

### 3.5 Confrontation with the canonical family — read-only

No R2, R6 or R7 artifact is regenerated. `results/S8_rotation_generator/tables/s8_rotation_vs_canonical.csv`
joins on `delta_e` with `float_precision='round_trip'`.

| source | status |
|---|---|
| R2 (`R2_instrumented_A_PHT_ARF.parquet`) | **JOINED**, 20 of 20 magnitudes |
| canonical, same pipeline (`s8_detection_counts.csv`, arm `full`) | **JOINED** — the same ladder code applied to the canonical family, so old-vs-new is a difference of generator and of nothing else |
| R7 (`exp_R7_regime1_miss_curve.csv`) | **JOINED** for `A_mismatched`; the rotation campaign runs the `c_int = 1` configuration only, so the other two configurations have no arm-comparable counterpart |
| R6 (`tau_HAT`) | **NOT PRODUCED** — the missing measurement is an `M = 1` rotation arm. T8.2 runs `M = 10` only; T8.3 and T8.3-bis produce the `M = 1` quantities, not this campaign |

Two numbers carry the section:

| `Delta_e` | canonical miss at `lambda = 50` (same pipeline) | rotation `eta = 0.05` | `median tau_arf` → `tau_swap` |
|---:|---:|---:|---|
| 0.085 | 1.00 | 0.72 | 410 → 1052 |
| 0.141 | 1.00 | 0.37 | 270 → 443 |
| 0.327 | 1.00 | 0.60 | 53 → 62 |
| 0.416 | 1.00 | 0.33 | 37 → 42 |
| 0.498 | 1.00 | 0.42 | 28 → 34 |

**The blind spot survives the generator change and is markedly less extreme than the published
family implies.** On the canonical family the external CUSUM at `lambda = 50` misses 99–100 % of
drifts at every magnitude. On a generator with a stable 50/50 prior and a Bayes error of `0.05` it
misses **33 % to 77 %** — one drift in three to three in four, still a blind spot at the threshold
the starvation certificate is stated at, but not the near-total starvation the abstract reports.

The rotation family is also **slower to adapt**: `tau_swap^(1/M)` exceeds the canonical `tau_arf` at
every magnitude, by a factor of 2.6 at `Delta_e = 0.085` and by 4–7 steps at the top of the grid.
Part of the miss-rate reduction is therefore a longer transient, not a weaker mechanism.

---

## 4. T8.3 — internal mechanisms and ensemble families, at equal evidence budget

### 4.1 Campaign

| item | value |
|---|---|
| grid | 9 pipelines x 6 canonical magnitudes x 30 seeds = 1 620 run records |
| stream | rotation family at `eta = 0.05` — the only one of the two carrying a binding false-alarm budget (D5) |
| internal axis | `ARFClassifier(drift_detector=D, warning_detector=D)`, `D in {ADWIN, DDM, EDDM, PageHinkley, KSWIN}` |
| ensemble axis | `SRPClassifier`, `LeveragingBaggingClassifier`, `ADWINBaggingClassifier`, `HoeffdingAdaptiveTreeClassifier` |
| calibration | external StrictCUSUM bisected to one false alarm per warm-up **per pipeline**, never shared |
| artifacts | `results/S8_mechanisms/data/`, `tables/` |

Three of the four ensemble families had never been instantiated in this repository, and
`HoeffdingAdaptiveTreeClassifier` — the real Bifet–Gavaldà HAT — had never been executed here at
all (§ 7). The prompt's `OzaBagADWIN` does not exist under river 0.23.0; the object is
`ADWINBaggingClassifier`.

Feasibility of the internal axis was verified in the pinned package, not assumed:
`ARFClassifier._drift_detector_input` returns `int(not y_true == y_pred)`, exactly the binary stream
`river.drift.binary.DDM` / `EDDM` consume. `DDM` had never been instantiated in this repository.

**Calibration verdicts: `OK` on 1 620 of 1 620 cells.** No `SATURATED`, no `NOT ATTAINABLE`, no
`NOT ARMED`, no `NOT BINDING`. `lambda_eq` lands between `3.90` and `5.93` depending on the
pipeline — an order of magnitude under the `lambda = 50` the starvation certificate is stated at.

### 4.2 The measurement

Miss rate, 30 seeds per cell. `lambda_eq` is per-pipeline; `lambda = 50` is R2's scenario A.

| pipeline | median `lambda_eq` | miss at `lambda_eq` (0.028 … 0.452) | miss at `lambda = 50` (0.028 … 0.452) |
|---|---:|---|---|
| `ARF_ADWIN` | 4.04 | 0.03, 0, 0, 0, 0, 0 | 1.00, 0.40, **0.83**, **0.77**, 0.47, 0.43 |
| `ARF_PageHinkley` | 5.38 | 0.13, 0.20, 0.07, 0, 0, 0 | **1.00, 1.00, 1.00, 1.00, 0.93, 0.90** |
| `ARF_DDM` | 3.94 | 0.03, 0, 0, 0, 0, 0 | 1.00, **0, 0, 0, 0, 0** |
| `ARF_EDDM` | 4.22 | 0.07, 0, 0, 0, 0, 0 | 1.00, **0, 0, 0, 0, 0** |
| `ARF_KSWIN` | 4.06 | 0.03, 0, 0, 0, 0, 0 | 1.00, 0, 0, 0.03, 0.23, 0.37 |
| `ENS_SRP` | 4.62 | 0.10, 0, 0, 0, 0, 0 | 1.00, 0.57, 1.00, 0.57, 0.37, 0.50 |
| `ENS_ADWINBagging` | 5.93 | 0.37, 0, 0, 0, 0, 0 | 1.00, 0.93, 0.33, 0, 0, 0 |
| `ENS_LeveragingBagging` | 4.62 | 0.13, 0, 0, 0, 0, 0 | 1.00, 0.10, 0.03, 0, 0, 0 |
| `ENS_HAT` | 5.80 | 0.17, 0, 0, 0, 0, 0 | 1.00, 0.53, 0.27, 0.13, 0.07, 0.13 |

At `lambda_eq` the blind spot essentially does not exist for any pipeline above the weakest
magnitude. At `lambda = 50` it is severe for `ADWIN` and `PageHinkley`, absent for `DDM` and `EDDM`,
and intermediate for the rest. **EDDM arms on this stream**, contrary to its status on ProteuS:
`e_pre = 0.069` over a 1 000-step warm-up gives ~69 monitored errors against a `warm_start` of 30.

### 4.3 D7 — the collapse, and what it does and does not say

| reading | collapse | closed-loop clause |
|---|---|---|
| at `lambda_eq` (the protocol's calibration) | **COLLAPSE**, 4 of 4 A-bins | **UPHELD** |
| at `lambda = 25` (control) | **COLLAPSE**, 4 of 4 | **FALSE AS STATED** (1 cell) |
| at `lambda = 50` (control, the published operating point) | **DOES NOT COLLAPSE** | **FALSE AS STATED** (6 cells) |

**The `lambda_eq` collapse is near-degenerate and is reported as such.** Three of its four A-bins have
a miss rate of exactly 0 for every mechanism; they "collapse" because every mechanism sits on the
same boundary, not because the curves meet. Selling that as a positive result would be false.

The informative reading is at `lambda = 50`, and there exactly one bin is non-saturated:

| A-bin | mechanisms | spread | widest within-CI | collapses |
|---|---:|---:|---:|---|
| `A <= 24.9` | 5 | 0.000 | 0.125 | yes (all miss 1.00) |
| **`A in [25.0, 60.1]`** | 4 | **0.579** | 0.557 | **no** |
| `A in [60.4, 106.8]` | 4 | 0.000 | 0.133 | yes (all miss 0.00) |
| `A >= 107.4` | 2 | 0.000 | 0.038 | yes (all miss 0.00) |

Inside the non-collapsing bin, the miss rate is **monotone in the median A** across all four
mechanisms:

| pipeline | median A in bin | miss rate | Wilson 95 % |
|---|---:|---:|---|
| `ARF_DDM` | 54.3 | 0.375 | [0.137, 0.694] |
| `ARF_ADWIN` | 43.4 | 0.727 | [0.642, 0.799] |
| `ARF_KSWIN` | 38.8 | 0.714 | [0.529, 0.847] |
| `ARF_PageHinkley` | 35.1 | 0.954 | [0.873, 0.984] |

The bin spans `[25, 60]` and `lambda = 50` sits inside it, so a residual A gradient inside the bin
moves the miss rate. The non-collapse is therefore **not** evidence that the mechanism matters
beyond A; the ordering says the opposite, and it is declared here rather than converted into a
claim.

### 4.4 The closed-loop clause is FALSE AS STATED, and the reason is not the binning

D7's second clause is a different test: a non-ADWIN mechanism with **comparable `tau_erase`**, at
the same threshold, must produce a comparable blind spot. Six cells refute it.

| `Delta_e` | pipeline | median `tau_erase` | reference (`ARF_ADWIN`) | miss | reference miss | reference Wilson 95 % |
|---:|---|---:|---:|---:|---:|---|
| 0.141 | `ARF_DDM` | 1 296.5 | 1 113.0 | **0.00** | 0.40 | [0.246, 0.577] |
| 0.243 | `ARF_DDM` | 531.5 | 392.5 | **0.00** | 0.83 | [0.664, 0.927] |
| 0.327 | `ARF_DDM` | 836.0 | 808.5 | **0.00** | 0.77 | [0.591, 0.882] |
| 0.327 | `ARF_EDDM` | 1 135.0 | 808.5 | **0.00** | 0.77 | [0.591, 0.882] |
| 0.416 | `ARF_DDM` | 1 143.0 | 904.0 | **0.00** | 0.47 | [0.302, 0.639] |
| 0.416 | `ARF_EDDM` | 1 351.0 | 904.0 | **0.00** | 0.47 | [0.302, 0.639] |

**The mechanistic statement this yields is precise, and it is the result of T8.3:**

> `tau_erase` does not determine `A`. Two internal mechanisms can erase the drift over windows
> within 17 % of each other and leave the external monitor budgets differing by a factor of two:
> at `Delta_e = 0.327`, `ARF_ADWIN` erases over 808 steps leaving `A = 43.9`, `ARF_DDM` over 836
> steps leaving `A = 75.4`. The first is missed 77 times in 100 at `lambda = 50`; the second is
> never missed.

So the closed-loop reframing survives **if** it is stated on the evidence budget and **falls** if it
is stated on the erasure time. S5 stated it on the loop topology, which is neither; the charge
(S8-H) fixes the quantity.

### 4.5 The equalising-alpha reading, reused not re-derived

`s2bis_proteus_calibration.family_requirements`'s closed form, applied to each pipeline's own
measured `(lambda_eq, W)`:

| pipeline | median W | `lambda_eq` | `R_CUSUM(lambda_eq)` | equalising `alpha_ADWIN` | deployed / equalising (ADWIN) | deployed / equalising (KSWIN) |
|---|---:|---:|---:|---:|---:|---:|
| `ARF_ADWIN` | 742 | 4.04 | 37.3 | 2 841 | `7.1e-07` | `4.3e-03` |
| `ARF_DDM` | 967 | 3.94 | 41.9 | 3 745 | `5.4e-07` | `4.2e-03` |
| `ARF_EDDM` | 1 167 | 4.22 | 46.0 | 4 529 | `4.4e-07` | `4.5e-03` |
| `ARF_KSWIN` | 1 776 | 4.01 | 55.6 | 6 972 | `2.9e-07` | `4.3e-03` |
| `ARF_PageHinkley` | 188 | 5.38 | 22.1 | 552 | `3.7e-06` | `6.6e-03` |
| `ENS_LeveragingBagging` | 1 866 | 4.62 | 57.4 | 7 295 | `2.8e-07` | `5.1e-03` |

The internal detectors are deployed **six to seven orders of magnitude tighter** than the confidence
that would place them at the external monitor's level (`delta = 0.002` against an equalising
`alpha` of `550` to `7 300` — the closed form exceeds 1 and is a bound, not a probability, at these
`W`), and KSWIN's deployed `alpha = 0.005` is ~200x tighter than its equalising value. That
asymmetry is the internal-axis analogue of what S2-bis measured on the external axis, and it is the
reason the internal detector fires long before the external one can.

**Asymmetry declared, not repaired.** `clock` is an ADWIN parameter with no analogue in the other
four mechanisms, so the `c_int = 1` configuration the manuscript calls hyper-reactive **cannot** be
transported to `DDM`, `EDDM`, `PageHinkley` or `KSWIN`. Each runs at its own River defaults, pinned
by name. That the two mechanisms which do carry a reactivity knob (`ADWIN` via `clock`,
`PageHinkley` via `threshold`) are exactly the two that produce the blind spot is a finding of this
grid and not a control for it.

---

## 5. T8.3-bis — the marginal of a tree INSIDE the ARF, and the Hydra factor at budget

### 5.1 What the two open items asked for

`transfer_S3.md` §6 names two quantities as unmeasured rather than estimated. Both are closed here.

| open item | source | status |
|---|---|---|
| per-tree `tau_i` of the ARF | `s3_competing_risks.py:23-27` | **CLOSED by P1** — §1.7, no simulation cost |
| the pre-drift error stream of one tree INSIDE the ARF, and with it the equal-budget form of the Hydra factor | `dependence_v2.tex:262-265` | **CLOSED here** |

Campaign: 100 seeds x 2 S3 anchors x 2 arms (`M = 10`, `M = 1`) = 400 cells on the **canonical**
family — `4.12x` and `7.99x` are measured on it, and a re-derivation on another generator would not
be a re-derivation. The per-tree instrumentation adds one `predict_one` per member per step and is
restricted to the 1 000-step pre-drift calibration window; `demo()` asserts that the ensemble
trajectory is unchanged with the flag on and off, member by member.

**Calibration verdicts: `OK` on 400 of 400 cells.**

### 5.2 The member marginal: same rate, averaged ten times

| quantity | `M = 10` | `M = 1` |
|---|---:|---:|
| pre-drift error of ONE member (mean over trees, median over runs) | **0.0912 ± 0.0288** | 0.0895 |
| pre-drift error of the ENSEMBLE (`e_pre`) | **0.0240** | 0.0895 |
| per-step error variance of one member | 0.0822 | 0.0816 |
| per-step error variance of the ensemble | **0.0235** | 0.0816 |
| measured variance reduction | **3.51x** | — |
| `lambda_eq` (one false alarm per warm-up) | **2.45** | **6.84** |

The measurement is sharper than the hypothesis it tests. `dependence_v2.tex:126-140` establishes
that the HAT marginal is **not** the member marginal, refuted through the tails. What this adds is
that the two are nearly identical in **rate** — `0.0912` inside the ARF against `0.0895` standalone,
a difference of `0.0017` against a between-tree sd of `0.0288` — and differ by being *averaged*.
The ensemble's advantage at the monitor is entirely variance: `3.51x` reduction, and a `lambda_eq`
`2.8x` lower.

**That is the mechanism S2-bis inferred from two calibrated thresholds, measured directly here.**
S2-bis observed `lambda = 20.97` for the ARF against `132.50` for the HT and attributed it to
bagging variance reduction; this campaign measures the variance ratio itself on the same family.

### 5.3 D8 — the decomposition, PRODUCED

`log(A/R)` is additive, so the `M = 1` against `M = 10` contrast splits exactly:

```
log[(A_1/R_1) / (A_10/R_10)] = log(A_1/A_10)  -  log(R_1/R_10)
                                ensemble-size part   threshold part
R(arm) = lambda(arm) + sqrt(W(arm)/2 * ln(1/eps)),   W := tau_erase - tau*,   eps = 0.05
```

| `Delta_e` | arm | `mean tau_swap` | W | A | `lambda_eq` | `R(lambda_eq)` | `R(50)` | miss at 50 |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 0.141 | `M = 1` | 1 659.0 | 505.0 | 17.37 | 6.84 | 34.35 | 77.50 | 0.79 |
| 0.141 | `M = 10` | 361.8 | 606.0 | 28.77 | 2.45 | 32.58 | 80.13 | **1.00** |
| 0.327 | `M = 1` | 419.3 | 354.0 | 32.95 | 6.84 | 29.87 | 73.03 | 0.87 |
| 0.327 | `M = 10` | 57.4 | 340.5 | 31.21 | 2.45 | 25.03 | 72.58 | **1.00** |

| `Delta_e` | Hydra time factor (mean / median) | ensemble-size part | threshold part | threshold share |
|---:|---|---:|---:|---:|
| 0.141 | 4.59x / 5.03x | **−0.5046** | +0.0529 | **9.5 %** |
| 0.327 | 7.31x / 2.53x | +0.0542 | **+0.1767** | **76.5 %** |

**D8 = PRODUCED, and the answer is magnitude-dependent — it does not collapse to "it is all
threshold".** At the weak anchor the contrast between the two arms is 90 % ensemble size; at the
strong anchor it is 77 % threshold. Publishing a single "threshold share" for the Hydra factor
would be false at one of the two anchors whichever value were chosen.

**On the Hydra factor itself.** `4.59x` and `7.31x` here are ratios of MEANS over the uncensored
runs. The published `4.12x` and `7.99x` are **RMST ratios under administrative censoring**, a
different estimator, and they are reproduced as such in §0 directly from `hydra_survival.csv`. The
two are consistent in order and direction and are not interchangeable; no claim of reproduction is
made from this campaign, and the medians (`5.03x`, `2.53x`) diverge further still, as
`S6_causal_evidence.md` already reports for the published medians (`5.32x`, `3.10x`).

**The arm is ARF(M = 1), not a HAT** (§ 7). Substituting `HoeffdingAdaptiveTreeClassifier` here would
break comparability with R6; it enters T8.3 as a distinct family and never as a replacement.

---

## 6. T8.4 — replication outside River

### 6.1 MOA is infeasible, with the measurement

| check | result |
|---|---|
| `java -version` | `java: command not found` |
| MOA jar under `/home/m53` | none |
| `skmultiflow` | absent, and incompatible with py3.12 / numpy 1.26 |

The fallback the plan reserves is taken, and it is the stronger control: MOA shares the algorithmic
lineage of River's ARF; `experiments/S8_generality/s8_minimal_arf.py` shares **no line of code** with
it. That claim is not left as prose — `demo()` walks the module's own AST for an import of `river`
and checks that no River symbol is bound in its namespace.

Scope: ADWIN re-implemented from Bifet–Gavaldà 2007 (exponential histogram, variance-aware cut
`eps_cut = sqrt(2/m sigma^2 ln(2/delta')) + (2/3m) ln(2/delta')`, `delta' = delta/n`); a Hoeffding
tree from Domingos–Hulten 2000 (grace period, `max_features = sqrt(d)`, information gain,
`G1 - G2 > eps` or `eps < tau`); `M` trees with `Poisson(6)` weights, accuracy-weighted vote, one
ADWIN per member, whole-tree replacement on alarm. Declared ceilings: majority-class leaves rather
than naive-Bayes-adaptive, no warning detector and no background tree, equal-width numeric
histogram rather than a Gaussian summary.

### 6.2 D9 — the criterion, and the substitution that was made

**The operational criterion first written into the script was wrong and is replaced, with the
substitution declared rather than silenced.** It scored the miss rate at the per-pipeline calibrated
`lambda_eq` and returned `NOT REPRODUCED` on the smoke. §4.2 shows why that cannot be a test: at
`lambda_eq` the T8.3 campaign measures a miss rate of `0.00` for eight of its nine pipelines,
**River's own ARF included**. A criterion under which the reference implementation exhibits no blind
spot cannot decide whether a replication exhibits one.

The replacement is the manuscript's own `def:blindspot`, applied identically to both
implementations at the published operating point `lambda = 50`: `A < R`, plus adaptation before
erasure (`tau_swap` finite and `< tau_erase`), plus a miss rate not more than `0.25` below River's on
the same magnitude. The `lambda_eq` reading is kept as a second column, not dropped.

**The rules file is not retro-edited.** Precedent: `s2bis_proteus_calibration.calibration_verdict`
discovered the `NOT BINDING` state in measurement and declared it in `transfer_S2bis.md` rather than
amending `s2bis-decision-rules.md`.

### 6.3 The measurement

100 seeds x 2 anchors, rotation stream at `eta = 0.05`, the same generator T8.3 runs.

| `Delta_e` | implementation | median `tau_swap` | median `tau_erase` | A | R at `lambda = 50` | `A < R` | miss at 50 | miss at `lambda_eq` |
|---:|---|---:|---:|---:|---:|---|---:|---:|
| 0.141 | NumPy ARF | 307.0 | 481.0 | 19.06 | 76.84 | **yes** | **0.96** | 0.02 |
| 0.141 | River ARF | — | 1 113.0 | 54.94 | 90.83 | **yes** | 0.40 | 0.00 |
| 0.327 | NumPy ARF | 142.5 | 1 068.5 | 72.16 | 90.01 | **yes** | **0.06** | 0.00 |
| 0.327 | River ARF | — | 808.5 | 43.91 | 84.80 | **yes** | 0.77 | 0.00 |

**D9 = PARTIAL**, and the two halves say different things:

- **`def:blindspot` itself reproduces at both anchors and on both implementations.** `A < R` holds
  in all four rows, and the NumPy ARF adapts before it erases at both anchors. The race the
  manuscript formalises is not an artefact of River.
- **The miss rate at `lambda = 50` reproduces at `Delta_e = 0.141` and inverts at `0.327`.** The
  NumPy ARF misses `0.96` where River misses `0.40` at the weak anchor — a *more* severe blind
  spot — and `0.06` where River misses `0.77` at the strong anchor. The cause is measured, not
  guessed: at the strong anchor the NumPy implementation leaves `A = 72.2` against River's `43.9`,
  1.6x more evidence, and the monitor takes it.

The implementations therefore differ in **how completely the classifier adapts**, not in whether the
race exists. That is what the declared ceilings predict: no background tree means a replacement
installs a blank tree that must re-learn from nothing, which lengthens the transient and leaves more
budget at a strong drift, while at a weak drift the NumPy tree's cruder numeric splitter adapts
faster than River's.

**Escalated per D9, not decided here.** The rule reserves the continuation decision to the user
whenever the replication does not reproduce the phenomenon. It reproduces the definition and not the
magnitude; the decision on what that licenses the article to claim is not the stream's to take.

---

## 7. Ingestion finding — what this repository calls a HAT is not a HAT

Measured, not inferred, and load-bearing for two of the sections above.

`exp_R6_generate_data.py:44-47` builds
`ARFClassifier(n_models=1, drift_detector=ADWIN(clock=1), warning_detector=ADWIN(clock=1))`, and
`grep -rn "HoeffdingAdaptiveTree\|HATClassifier" experiments/ tests/ config/` returns **nothing**.
The base learner of that object is `BaseTreeClassifier(HoeffdingTreeClassifier)`
(`river/forest/adaptive_random_forest.py:251`) — a Hoeffding **Tree** with feature subsampling,
replaced wholesale by an external ADWIN. That is not the Bifet–Gavaldà HAT (one ADWIN per node,
alternate subtrees, no global reset) that `.tex:224` cites as `\cite{bifet_hat_2009}`.

| consequence | where it binds |
|---|---|
| `tau_HAT`, `4.12x` and `7.99x` are measured on ARF(`M = 1`) | T8.3-bis keeps that object as the paired arm (§5); substituting the real HAT would break comparability with R6 |
| `river.tree.HoeffdingAdaptiveTreeClassifier` exists in the pinned build and had **never** been executed in this repository | it enters T8.3 as a distinct family, `ENS_HAT` (§4.2), and is measured for the first time here |
| the terminology charge is not S8's to apply | `.tex:224` is inside `sec:hydra`, which `CLAUDE.md` excludes, and no v2 fragment carries the Hydra section yet — charge **S8-E**, recorded without a payload |

---

## 8. Verdict table

| rule | verdict | the number that carries it |
|---|---|---|
| **D0** reproduction of carried numerals | **REPRODUCED** 5/5 (+ the R7 band means) | `\LearnShare` 0.993371 exact; Hydra 4.1175 / 7.9909; `A/A_rect` min −14.1161; switch 0.452271 |
| **D3-bis** trunk acceptance gate | **PRESERVED** | 6 000 / 6 000 rows, 30 / 30 columns, zero divergence |
| **D1** replacement inert? | **NOT INERT** | `share_swap_all = 1.36 %` [1.18, 1.52]; sign test 1 706/1 998, `p = 1.9e-242` |
| **D2** own contribution of the first swap | **MEASURED** | `share_swap_first = 0.71 %` [0.63, 0.78] > `share_swap_rest = 0.56 %` [0.47, 0.67] |
| **D3** decisional reading | measured | `0/100` → `18/100` → **`49/100`** at `lambda = 50`, `Delta_e = 0.3268` |
| **D4** generator identity | **HELD** | 40 / 40 grid points within 3 SE, worst 2.50 SE |
| **D5** non-degenerate null | **NON-DEGENERATE** both arms | `e_pre` 0.0240 / 0.0690; binding `lambda` on both |
| **D6** high-magnitude switch | canonical **PRESENT** (0.452), rotation `eta=0` **PRESENT** (0.243), rotation `eta=0.05` **ABSENT** | the regime exists only on the canonical family; the `eta = 0` firing is an isolated mid-band dip, 74 % of runs negative, with positive medians on both sides |
| **D7** collapse of the miss-rate curves | **COLLAPSE** at `lambda_eq` (near-degenerate) and at `lambda = 25`; **DOES NOT COLLAPSE** at `lambda = 50` | only 1 of 4 A-bins is non-saturated; inside it the miss rate is monotone in median A |
| **D7** closed-loop clause | **FALSE AS STATED** | 6 cells: `DDM`/`EDDM` at comparable `tau_erase` miss `0.00` where `ADWIN` misses 0.40–0.83 |
| **D8** Hydra factor at equal budget | **PRODUCED** | threshold share `9.5 %` at `Delta_e = 0.141`, `76.5 %` at `0.327` — magnitude-dependent, not a single number |
| **D9** replication outside River | **PARTIAL**, escalated | `def:blindspot` holds on both implementations at both anchors; the miss rate at `lambda = 50` reproduces at 0.141 (0.96 vs 0.40) and inverts at 0.327 (0.06 vs 0.77) |

`transfer_S3.md` §6 open items **1 and 2 are both closed**.

---

## 9. Reproduction

```bash
cd /home/m53/wt-s8
PY=/home/m53/miniforge3/envs/Trading/bin/python

# P1 -- ab initio arms
PYTHONHASHSEED=0 $PY experiments/S6_synchronized_traces/s6_runner.py demo     # 6-arm invariants
PYTHONHASHSEED=0 $PY experiments/S8_generality/s8_arms.py d0                  # D0
PYTHONHASHSEED=0 $PY experiments/S8_generality/s8_arms.py smoke               # 5 seeds x 3 magnitudes
PYTHONHASHSEED=0 $PY experiments/S8_generality/s8_arms.py full                # 1 395.0 s
PYTHONHASHSEED=0 $PY experiments/S8_generality/s8_arms.py causal              # D3-bis, D1, D2, D3
#   16.2 s on a warm page cache; the first pass over the 50 M-row corpus is I/O bound.
#   Re-running it rewrites s8_causal.json, s8_detection_counts.csv and s8_trunk_identity.json
#   BYTE-IDENTICALLY, the 10 000-replicate seed-paired bootstrap included.

# P1 -- rotation generator
PYTHONHASHSEED=0 $PY experiments/S8_generality/s8_rotation.py demo            # generator invariants
PYTHONHASHSEED=0 $PY experiments/S8_generality/s8_rotation.py identity        # D4, no classifier
PYTHONHASHSEED=0 $PY experiments/S8_generality/s8_rotation.py full            # 1 751.2 s, both eta arms
PYTHONHASHSEED=0 $PY experiments/S8_generality/s8_rotation.py compare         # D5, D6, confrontation

# P1 -- standalone Figure 4, from the committed R7 curve
PYTHONHASHSEED=0 $PY experiments/S8_generality/s8_figure_r7.py

# P2 / P3
PYTHONHASHSEED=0 $PY experiments/S8_generality/s8_mechanisms.py full          # 684 s, D7
PYTHONHASHSEED=0 $PY experiments/S8_generality/s8_marginal.py full            #  65 s, D8
PYTHONHASHSEED=0 $PY experiments/S8_generality/s8_minimal_arf.py full         #  45 s, D9

# gates
PYTHONHASHSEED=0 $PY -m pytest tests/ -q
sha256sum -c results/audit_S7/_baseline/artifacts_sha256_pre_ssot.txt | tail -1
```

Every script carries a `demo` self-check. Wall clocks are those measured on the host of
`docs/ENVIRONMENT.md`, one stage at a time.

**Reproducibility regime.** S8 inherits S6's: no frozen digest, replay and compare. The analysis
path is verified directly — `s8_arms.py causal` re-run on the committed corpus reproduces its three
artifacts byte for byte, bootstrap included — and the simulation path by
`tests/test_S6_traces.py::test_parquet_replay_is_byte_identical`, which the S8 arms share. **No
entry is added to `results/audit_S7/_baseline/authorized_deviations.txt`**: `sha256sum -c` against
the frozen reference stays at 27 OK / 7 FAILED, the seven being exactly those already declared.

---

## 10. Residual risk and debt

- **`\LearnShare` is exposed and the conclusion's ordering is contradicted.** Charge S8-D. The
  abstract and the conclusion read the macro; `sec:starvation` reads it too and is inside the
  excluded zone, which is why the payload adds macros beside it rather than mutating it.
- **The article now carries two generator families.** R2, R6 and R7 are published on the
  boundary-shift family and are not regenerated. Which family is of record is an assembly decision;
  S8 delivers the measurement and takes no editorial position (charge S8-G).
- **D6's `inf` formulation does not discriminate an isolated band from a regime.** Declared in §3.4,
  not repaired; the rules file is not retro-edited.
- **D7's A-binning is coarse where it matters.** The non-collapsing bin spans `[25, 60]` with
  `lambda = 50` inside it. Declared in §4.3.
- **The `clock` asymmetry is a property of the grid, not a control.** Only ADWIN and PageHinkley
  carry a reactivity knob, and they are exactly the two mechanisms that produce the blind spot
  (§4.5). A grid in which every mechanism could be set to a common reactivity does not exist.
- **D9 is PARTIAL and is escalated**, per the rule. No article-level pivot is decided here.
- **`ARCHIVED_MAIN_TEX` is empty** (`tests/test_manuscript_integrity.py:52`): any v65 deposited in
  `docs/manuscript/` fails the suite until it is declared there. Outside S8's perimeter, flagged.
- **`run_tests.sh` and the nine `run_experiment_R*.sh` call bare `python`**, not the pinned
  interpreter. Reported by S-SYNC, still open, outside S8's perimeter.
