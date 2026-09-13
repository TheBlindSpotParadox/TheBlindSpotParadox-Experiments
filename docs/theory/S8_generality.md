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
