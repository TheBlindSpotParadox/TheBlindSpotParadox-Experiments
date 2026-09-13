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
