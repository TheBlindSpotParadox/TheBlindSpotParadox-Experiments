# Stream S10 — decision rules, fixed before measurement

Committed before any S10 script is written or run, and before any S10 output exists. Every rule
carries its numeric threshold and its verdict on **both** sides, so no outcome of the stream can be
arbitrated after the fact. Part A is the prediction `PROMPT_S10.md` T10.1 orders written before
measurement, together with the competing prediction this stream derives.

Stream branch `stream-s10`, parent `19b9bde`. Plan of record: the operator-approved S10 plan of
2026-09-24. Entry gate measured before this commit: `pytest tests/ -q` = 156 passed (nominal 154 or
156 after the P1 debt-register test); `sha256sum -c results/audit_S7/_baseline/artifacts_sha256_pre_ssot.txt`
= 27 OK / 7 FAILED, the seven declared deviations.

**Scope.** S10 measures. It edits no section of the manuscript. Charges are delivered unapplied in
`docs/theory/S10_transfer.md`, and none lands inside `sec:race`, `sec:hydra`, `sec:starvation` or
`sec:decoupling`. Write perimeter: `experiments/S10_*/`, `results/S10_*/`, `docs/theory/S10_*.md`,
`tests/test_S10_*.py`, the `# S10 —` block of `config/experiment_ssot.py`. No write under
`results/S6_*`, `results/S8_*`, `results/S9_*`, `results/R*_*`; no entry in
`authorized_deviations.txt`.

**Three placements forced by that perimeter.** `docs/prompts/` is outside it, so these rules live
here rather than beside `s9-decision-rules.md`. The root `.gitignore` is outside it, so the
regenerated traces are ignored by a nested `results/S10_external_validity/.gitignore`.
`docs/ENVIRONMENT.md` is outside it, so the measured wall-clock times go into the S10 report.

**Operator arbitration on T10.3, recorded verbatim in substance.** The real-stream scope is the three
balanced INSECTS variants present in `data/insects/` (`abrupt_balanced`, `gradual_balanced`,
`incremental_reoccurring_balanced`) and the three BAF variants. Reason: River's INSECTS download URL
answers 404 and the other eight files are not in the repository, so any extension would introduce an
external dependency that a clean clone cannot verify. The imbalanced variants and the variants with
no discrete change point are out of scope, as they are in the manuscript's protocol. T10.3 therefore
measures the pre-change error floor `p0` of every real stream the repository instruments; it adds no
stream and no hypothesis test.

---

## Honesty declaration — what the planning phase read

Read before this commit: the D5 and D7 tables of `docs/theory/S9_detector_coverage.md` (PHT at
`lambda = 15` detects `0.928` of runs within `W` on the canonical family and `0.942` on the rotation
family; `e_pre` medians `0.024` and `0.069`); the first four rows of
`results/S2bis_calibration/tables/s2bis_insects_sweep.csv` and of `s2bis_lambda_eq_insects.csv` (four
values of `lambda_eq_span_emp` on `abrupt_balanced`, `pht_arf_c1`: `49.49, 42.74, 121.89, 56.39`);
the role counts of `s2bis_proteus_sweep.csv` and `lambda_eq = 1.0000149` on ProteuS; Table II
(`table2_values.csv`); the six R4 seed-level tests and the alpha-sweep test; the twenty
`p_bootstrap` values of `results/S3/ks_exponentiality.csv` and the Fisher homogeneity
`p_value = 1.0` of `envelope_stats.json`; Table 2 of Souza et al. (2020), arXiv:2005.00113, p. 37.

Not computed by anyone before this commit: any lagged error trace, any quantity under label latency,
any recall or precision curve on the synthetic streams, any S10 `p0` pass, any Holm verdict on an
enlarged family.

---

## Part A — T10.1: the prediction, written before measurement

### A.1 The prediction of the prompt, verbatim

> Prédiction à écrire AVANT mesure : la latence décale τ_det de l et ne décale pas τ_erase, donc elle
> réduit mécaniquement la fenêtre exploitable. Vérifie-la.

Operational form, the three clauses tested separately:

- **P-a** — the alarm moves by `l`: `tau_det(l) - tau_det(0) = l` on the wall clock.
- **P-b** — erasure does not move: `tau_erase(l) = tau_erase(0)`.
- **P-c** — hence the exploitable window and the budget available before erasure shrink, and the
  rate of detection within `W` falls.

### A.2 Two latency models, one convention

The monitor reads an error stream, and an error needs a label. Whether the learner also waits for
that label is not stated by the prompt and decides the answer.

- **M1, monitor-only latency.** The learner is trained on labels as they arrive (prequential,
  `l = 0`); the monitor receives `e_t` at `t + l`. The error sequence is the trunk's.
- **M2, shared latency.** The learner and the monitor are fed by the same delayed label stream. At
  wall-clock `t` the prediction of `x_t` is made **before** `y_{t-l}` arrives and is learnt
  (test-then-train, the order of the `l = 0` trunk). A reversed order would move every result by one
  step (`l - 1` in place of `l`); the convention is fixed here.

### A.3 What M1 decides, and why it is not evidence

Under M1 the error sequence is unchanged, so `tau_erase` is unchanged and the monitor's crossing moves
by exactly `l`: P-a and P-b hold **by construction**. Detection within `W` becomes
`d(0) + l <= W(0)`, non-increasing in `l`, and the budget read before erasure is `def:budget` truncated
at `W(0) - l`, non-increasing in `l`. All three are asserted as identities in the analysis and are
**declared tautological**; none is counted as a confirmation of the prompt. What M1 measures is a
magnitude: how many runs carry a slack `W - (d - tau*)` smaller than `l`.

### A.4 What M2 predicts — derived here, and contrary to the prompt

Let `S_k` be the ensemble state after learning samples `0 .. k-1` in stream order. Under M2 the
learner has absorbed samples `0 .. t-l-1` when it predicts `x_t`, so

```
e^(l)_t = 1[ S_{t-l}(x_t) != y_t ] .
```

The learning **sequence** is the trunk's -- same samples, same order, and River feeds each tree's
drift detector inside `learn_one` with that tree's error on the sample being learnt -- and
`predict_one` consumes no entropy (gate G0, `g0_report.json`, 150/150). The state trajectory
`{S_k}` is therefore the trunk's; only the step at which each state is used to predict moves.
Consequences, distributional rather than pathwise since `x_t` is not `x_{t-l}`:

1. For `t in [tau*, tau* + l)`, `S_{t-l}` has learnt no post-drift sample: `e^(l)` sits at the error
   of the pre-drift model on the post-drift concept, the maximum of the transient.
2. For `t >= tau* + l`, `S_{t-l}` has learnt `t - l - tau*` post-drift samples, like the trunk at
   `t - l`: `e^(l)_t` is distributed as `e^(0)_{t-l}`.
3. Hence the transient of `e^(l)` is the trunk's delayed by `l`, preceded by `l` steps at its maximum:
   **`W(l) ~ W(0) + l`**.
4. The monitor reads `e^(l)_d` at wall-clock `d + l`. At the wall-clock erasure `tau* + W(l)` it has
   read data up to `tau* + W(l) - l ~ tau* + W(0)`: `l` steps at the transient's maximum followed by
   the first `W(0) - l` steps of the trunk transient. The trunk's budget integrates its full `W(0)`
   steps. The difference replaces the last `l` trunk steps, the tail of a decaying transient whose
   excess is near zero at erasure, by `l` steps at its maximum: **`A_avail(l) >= A(0)`** is predicted.
   The 200-step smoothing and `p0(l) >= p0(0)` (a staler pre-drift model) blur this, and are not
   predicted to reverse its sign for `l <= 500`.
5. The monitor's input over the window stochastically dominates the trunk's, so its crossing comes
   no later in data index: **the rate of detection within the wall-clock deadline is not predicted to
   fall.**

**Competing prediction, committed:** under M2, P-b fails (`tau_erase` moves by about `l`), P-c fails
(the window and the available budget do not shrink), and P-a holds only for detections faster than
the first `l` post-drift steps; slower detections shift by less than `l` on the wall clock.

---

## Part B — T10.1 rules

**Grid.** Streams `canonical` (`s6_runner.make_stream`) and `rotation` (`s8_rotation.STREAM_FN[0.05]`,
`S10_ROTATION_ETA`); 100 seeds `common.seed_pool(100)`; the 20 canonical magnitudes
`round(Phi(b / sqrt 2) - 0.5, 6)` over `S6_CAMPAIGN_BOUNDARY_SHIFTS`; arm `full`; lags
`S10_LAGS = [0, 10, 50, 100, 500]`.

**Quantities, per run and lag.** `t_rel = t - tau*`, `tau* = 4000`. `p0(l)` = mean of `e^(l)` over
`t_rel in [-1000, 0)`. `W(l)` = `s6_defs.tau_err_framework(e^(l)[tau*:], p0(l), DELTA_P,
horizon=S10_T_HORIZON)`, i.e. `def:times` on the lag-`l` stream, NaN when censored.
`A(l)` = `s6_defs.budget_framework(e^(l)[tau*:], p0(l), W(l), .)`, i.e. `def:budget`.
`A_avail^M1(l)` = `budget_framework(e^(0)[tau*:], p0(0), W(0) - l, .)` and `A_avail^M2(l)` =
`budget_framework(e^(l)[tau*:], p0(l), W(l) - l, .)`, taken as 0 when the truncation is negative and
NaN when `W` is censored.

**Monitor.** River `PageHinkley(threshold = inf, delta = DELTA_P)` through `s6_detectors.PHT`, fed from
`t_rel = -1000`, its statistic read at every step -- the S9 sentinel, exact for every threshold up to
the first crossing. `d(lambda)` = first `t_rel` with statistic `> lambda`, for `lambda in S10_LAMBDAS`.
`d` is a **data index**: the `t_rel` of the error whose ingestion caused the crossing. A crossing with
`d < 0` is a pre-drift false alarm under every lag, whatever its wall-clock time; it carries no
post-drift detection reading.

**Detection.** M1: `det_W = 1[0 <= d(0) and d(0) + l <= W(0)]`. M2: `det_W = 1[0 <= d(l) and d(l) + l
<= W(l)]`. Rate = detections over runs whose deadline is finite, pre-drift alarms counted as
non-detections (the S9 convention). Also reported: **detection at all**, `1[0 <= d < S10_T_HORIZON]`
on the data index.

**Inference.** Unit of independence: the seed. A seed's 20 magnitudes share one feature stream
(`deff = 20`), so every interval is a seed-cluster bootstrap (`S10_BOOTSTRAP_SEED`,
`S10_N_BOOTSTRAP`, local `default_rng`) and every test is a two-sided sign test on per-seed
statistics, `scipy.stats.binomtest(max(n+, n-), n+ + n-, 0.5)`, ties dropped (the R4 and R5 form).

| rule | statistic | verdicts |
|---|---|---|
| **L0** trunk identity | (a) the 2 x 2000 `l = 0` records produced by `s6_runner._metrics` equal the oracle rows of arm `full` (`S6 data/runs.parquet`, `S8 data/eta0.05/runs.parquet`) on every shared column; (b) smoke: the `err` column over `t_rel in [-1000, 4000)` equals `S6 smoke/traces.parquet`, arm `full`, bit for bit; (c) at `l = 0`, with `W` = the record's `w_fw`, the PHT `pre_drift_alarm_rate` and `detect_within_W_rate` at `lambda in {15, 50}` equal the cells of `s9_family_ordering.json` / `s9_family_ordering_rotation.json` (family PHT, setting published, input arm raw) to four decimals at all 20 magnitudes | **PRESERVED** if (a), (b) and (c) hold; **BREACH** otherwise → HALT, no T10.1 number is read |
| **L1** P-a under M2 | at `lambda = 15`, runs with a post-drift crossing at both lags: median of `d(l) - d(0)` (equal to `tau_det(l) - tau_det(0) - l` on the wall clock), cluster 95 % CI, `tol = max(1, 0.1 l)`, for every `l > 0` | **P-a HOLDS** if CI within `[-tol, +tol]`; **EARLIER** than `l` if CI upper `< -tol`; **LATER** if CI lower `> +tol`; **UNDECIDED** otherwise |
| **L2** P-b under M2 | per seed, the median over magnitudes of `W(500) - W(0)` (both finite) → sign test, family member `S10-L2-<stream>`; pooled median of `W(l) - W(0)` and of its ratio to `l`, cluster CI, every `l` | **P-b REFUTED** if the member is retained by Holm (Part E), `n+ > n-`, and the pooled median of `(W(500) - W(0)) / 500` is `>= 0.5`; **P-b HOLDS** if the pooled median of `W(500) - W(0)` lies in `[-50, 50]` with its CI inside `[-50, 50]`; **UNDECIDED** otherwise |
| **L3** P-c (budget) under M2 | per seed, the median over magnitudes of `A_avail^M2(500) - A(0)` (both finite) → sign test, member `S10-L3-<stream>`; pooled medians of `A_avail^arm(l)` and of `A_avail^arm(l) / A(0)`, both arms, every `l` | **P-c HOLDS** under M2 if retained with `n- > n+`; **REFUTED** if retained with `n+ > n-`; **UNDECIDED** otherwise. Under M1 the decrease is a tautology and only its magnitude is reported |
| **L4** detection within `W` | at `lambda = S10_TEST_LAMBDA = 15`, `l = 500` against `l = 0`: per seed, `sum_j det_W(500) - sum_j det_W(0)` over magnitudes whose deadlines are finite at both lags → sign test, members `S10-L4-M1-<stream>` and `S10-L4-M2-<stream>` | **REDUCED** if retained with `n- > n+`; **INCREASED** if retained with `n+ > n-`; **NOT SHOWN** otherwise (including `n+ + n- = 0`, recorded with `p = 1`) |

Descriptive and never tested: every `(stream, arm, l, lambda)` rate, per magnitude and pooled, with
the pre-drift alarm rate and the detection-at-all rate; the median of `d(l) - d(0)` at every `lambda`.
L2, L3 and L4 verdicts are provisional until Part E returns the Holm decision.

---

## Part C — T10.2 rules: the dual mode on one axis

Six panels share one axis, the PageHinkley threshold `lambda`, on a log scale over `[1, 500]`.
Recall is drawn solid and precision dashed; the admissible window is shaded; `p0` is printed in each
panel title.

| panel | stream | data | protocol |
|---|---|---|---|
| a | canonical, `Delta_e = S10_DUAL_DELTA_E = 0.326793` | S10 traces, `l = 0`, 100 seeds | passive monitor, re-armed after each alarm, fed over `t_rel in [-1000, +S10_TAU_TOL]`; no classifier reset |
| b | rotation `eta = 0.05`, same `Delta_e` | idem | idem |
| c | ProteuS, PHT + ARF `c = 1` | `s2bis_proteus_sweep.csv`, roles `grid` and `lambda_ref`, 1 080 runs per `lambda` | deployed R4 protocol: monitor **and classifier** reset on each alarm |
| d, e, f | INSECTS `abrupt_balanced`, `gradual_balanced`, `incremental_reoccurring_balanced`, `pht_arf_c1` | `s2bis_insects_sweep.csv`, role `grid`, 30 seeds per `lambda` | deployed R5 protocol, idem |

**Scoring.** Panels a and b score with `exp_R5_common.evaluate_bipartite(alarms, [tau*], n,
tau=S10_TAU_TOL)`; panels c to f carry the scorer of their source run. Recall = `sum TP / sum(number
of changes)`; precision = `sum TP / sum(TP + FP)`, pooled over seeds, **undefined** (not drawn) when
no alarm is raised at all.

**Budget markers.** `lambda_FA` is the false-alarm budget over the armed pre-change span: the median
over seeds of `exp_R5_common.calibrate_lambda(e^(0)[t_rel in [-1000, 0)])` (a, b), of
`lambda_eq_span_emp` (d to f), and of `lambda_eq` from `s2bis_lambda_eq_proteus.csv` (c, the bracket
floor, verdict NOT BINDING). `lambda_op` is the evidence ceiling, the S6 construction transposed to
the PHT: the 5 % quantile over seeds of the maximum sentinel statistic over `t_rel in [0,
S10_TAU_TOL]` (a and b only; the closed-loop sweeps of c to f expose no such trace). **No margin
depending on `W` is used**: which quantity the symbol `W` denotes is under arbitration in S2-ter T3.

| rule | statistic | verdicts |
|---|---|---|
| **DM1** window | `{lambda on the panel grid : recall >= S10_RECALL_MIN = 0.95 and precision >= S10_PRECISION_MIN = 0.5}`, precision undefined counted as satisfied (no false alarm) | reported as `[min, max]`, flagged NON-CONTIGUOUS if so, or **EMPTY** |
| **DM2** edges against budgets | lower edge against `lambda_FA`; upper edge against `lambda_op` (a, b) | **AGREES** if the marker lies within one grid step of the edge; **DISAGREES** otherwise, with the ratio; descriptive |
| **DM3** published failures | each published failure point must fail by the criterion of its own mode, and by that one only. Starvation: recall `< 0.95` and precision not `< 0.5` — canonical PHT `lambda = 50` (a); ProteuS PHT + ARF `c = 1` at `lambda = 15` (c). Flooding: precision `< 0.5` and recall `>= 0.95` — INSECTS `gradual_balanced` and `incremental_reoccurring_balanced`, `pht_arf_c1`, at their per-seed `lambda_ref` (e, f; placed at the median `lambda_ref`) | per point **HOLDS**, **FAILS** or **DOUBLE** (fails both criteria); overall **HOLDS** iff all four points hold. `abrupt_balanced` (the weak witness), the rotation panel and the published success points are descriptive |

---

## Part D — T10.3 rules: `p0` of every instrumented real stream

| rule | content | verdicts |
|---|---|---|
| **P0-1** definition | `p0_span`: mean error of the classifier over the armed pre-change span `[warm-up, first valid change)`, with the external detector **disabled** (the S2-bis calibration pass, `s2bis_lambda_eq.run_at_lambda(..., None, stop_at=...)`); `p0_warm`: mean over the warm-up. Per (stream, variant, seed, pipeline), pipelines `S10_P0_PIPELINES = (pht_ht, pht_arf_c1)`, 30 seeds `make_seed_pool()`. INSECTS: warm-up `get_warmup_steps(n)`, span end = first valid change. BAF: warm-up `BAF_WARMUP = 100 000`, span end `BAF_DRIFTS[0] = 125 000`. `adwin_arf_c1` builds the same ARF(`c = 1`) as `pht_arf_c1` (`build_model` reads only the `_ht` suffix and `c32`), so its `p0` is identical by construction | reported as median, min and max over seeds, per variant and pipeline |
| **P0-2** INSECTS identity | the 180 recomputed `(p_true_warmup, p_true_span, lambda_eq_span_emp)` equal `s2bis_lambda_eq_insects.csv` exactly | **REPRODUCED**, or **BREACH** → HALT T10.3 |
| **P0-3** BAF parse identity | the S10 BAF loader reads with `float_precision='round_trip'` (the repository guard forbids a bare `read_csv` outside R5); R5 reads with the default parser. The HT error sequence over `[0, 125 000)` from the S10 loader is compared with `exp_R5_compute_delta_e.error_stream_baf` (R5's parse) | **IDENTICAL**, or **DIVERGENT** with the fraction of differing steps; a divergence marks the BAF `p0` as "S10 parse" and is not a HALT |

No test is added by T10.3. The Table II candidate asset carries `p0_span` for both classifiers and
re-computes nothing else.

---

## Part E — T10.4 rules: Holm over the enlarged family

**H0 — primary family, `m = 18`, the verdict of record.** The ten tests `protocol_v2.tex
§Multiplicity` declares, plus the eight S10 members of Part B:

| members | artifact key |
|---|---|
| R4-1 .. R4-6 | `results/R4_proteus_evaluation/data/exp_R4_seed_level_tests.csv`, rows 0-5, `sign_test_p` |
| R4-alpha | `results/R4_proteus_evaluation/data/exp_R4_seed_level_tests_KSWIN_alpha_sweep.csv`, row 0, `sign_test_p` |
| R5-abrupt, R5-gradual, R5-reoccurring | `results/R5_real_world_evaluation/tables/table2_values.csv`, rows `dataset == insects`, `sign_test_p` |
| S10-L2-{canonical, rotation}, S10-L3-{canonical, rotation}, S10-L4-M1-{canonical, rotation}, S10-L4-M2-{canonical, rotation} | `results/S10_external_validity/tables/s10_latency.json :: tests.<member>.p` |

**H1 — census family, `m = 39`, reported beside H0.** The live manuscript and its v2 fragments carry
p-values outside the declared ten, found by grep during planning: twenty KS exponentiality tests
(`.tex:408`, `dependence_v2.tex:228`, "largest p = 0.0030") and one Fisher homogeneity test
(`.tex:298`). H1 = H0 + S3-KS-1 .. S3-KS-20 (`results/S3/ks_exponentiality.csv`, `p_bootstrap`) +
S6-homogeneity (`results/S6_synchronized_traces/tables/envelope_stats.json ::
crossing_counts.envelope_homogeneity.fisher_exact.p_value`). A member retained in H0 but not in H1
is flagged; H1 does not overturn a verdict of record.

**H2 — procedure.** Holm step-down at `alpha = S10_HOLM_ALPHA = 0.05`: sort ascending (stable, ties in
member order); reject `H_(k)` while `p_(k) <= alpha / (m - k + 1)`; stop at the first failure.
Adjusted `p_(k) = max_{j <= k} min(1, (m - j + 1) p_(j))`. A bootstrap p-value of exactly 0 is
replaced by `1 / (N + 1)` with `N = s3_bounds.KS_N_BOOT = 2000`. Every non-survivor is listed with its
rank, threshold, adjusted p and the manuscript site carrying the claim. A retracted claim is reported
as retracted: a claim withdrawn by a declared correction outranks a claim kept without one.

---

## Terminal states

| state | trigger | consequence |
|---|---|---|
| HALT T10.1 | L0 BREACH | no T10.1 number is read; the divergent columns are reported |
| HALT T10.3 | P0-2 BREACH | no INSECTS `p0` is reported from the S10 pass |
| declared | P0-3 DIVERGENT | BAF `p0` reported with its parse flag |
| measured | every other rule | verdict as measured, never re-tuned; a refutation of the prompt's prediction is a result |

---

## Erratum E1 — the erasure estimator of Part B (2026-09-24, before any S10 measurement)

Committed after `22252da` and before any S10 campaign, smoke run or analysis. No S10 quantity had
been computed when it was written.

**What was read to write it.** The committed S6 trunk, `results/S6_synchronized_traces/data/runs.parquet`,
arm `full` — the `l = 0` stream S10 reproduces under L0 and does not measure. Per magnitude, the
distributions of `w_fw` (`def:times` W at horizon 2500), `tau_erase` (argmax of `A_unrefl`) and
`tau_err_rho050/025/010`. These bear on whether an estimator **can** move with a lag; they say
nothing about the size of any lag effect.

**The defect.** `def:times` reads W as the **last** crossing of `p0 + delta_P` by a 200-step trailing
mean. At `p0 = 0.024` the noise of that mean (`sqrt(p0 (1 - p0) / 200) ~ 0.011`) exceeds
`delta_P = 0.005`, so the last crossing is set by the latest noise excursion before the horizon, not
by the end of the transient. Measured on the trunk, at the 11 magnitudes with `Delta_e <= 0.327`:
median `w_fw` between 1 908 and 2 264 against a horizon of 2 500, 38 % to 60 % of runs beyond 2 000,
and 6 to 35 runs in 100 censored. An estimator pinned to the horizon cannot carry a shift of `l`.
Worse, under M2 the deadline `W(l) - l` would then shrink by `l` exactly as under M1, so Part B as
written would **manufacture** P-b and P-c rather than test them.

**What the manuscript calls `tau_erase`.** `\SixTauErase = 612` is "mean argmax A_unrefl"
(`articleA_blindspot_v64_camera_ready.tex:37`, `s6_causal.json`): the `s6_defs.tau_erase` estimator,
not `def:times`. The prompt's P-b is therefore a statement about the argmax estimator.

**Amendment to Part B**, applied to every rule that reads `W`, `A` or `A_avail`:

- `T(l) := s6_defs.tau_erase(A_unrefl(l), tau_swap(0) + l, horizon = S6_T_HORIZON)`, with
  `A_unrefl(l)` = `s6_defs.accumulations(e(l)[tau*:], p0(l))[0]` (`delta = DELTA_P`) and
  `tau_swap(0)` the trunk's `tau_swap_q010`. Under M2 the learning sequence is the trunk's, so the
  first replacement reaches the predictions at `tau_swap(0) + l`. The search window moves with it,
  so the estimator is shift-invariant and no horizon is asymmetric across lags. At `l = 0`, `T(0)`
  is the record's `tau_erase` and is asserted equal to it (part of L0).
- Budgets are read on the unreflected accumulation, floored at 0 (no positive evidence read):
  `A(l) := max(0, max_{0 <= t <= T(l)} A_unrefl(l)[t])`;
  `A_avail^M1(l) := max(0, max_{0 <= t <= T(0) - l} A_unrefl(0)[t])`;
  `A_avail^M2(l) := max(0, max_{0 <= t <= T(l) - l} A_unrefl(l)[t])`;
  0 when the bound is negative, NaN when `T` is NaN.
- Detection deadlines: M1 `0 <= d(0) and d(0) + l <= T(0)`; M2 `0 <= d(l) and d(l) + l <= T(l)`.
- L2 reads `T(500) - T(0)` in place of `W(500) - W(0)`, with thresholds, tolerance and ratio rule
  unchanged; L3 reads the amended budgets; L4 the amended deadlines. L1 is unchanged: it never read
  `W`.
- `def:times` W at `S10_T_HORIZON` stays in the tables as a **descriptive** secondary reading, so the
  horizon pinning above is shown rather than asserted. It is never tested. `S10_T_HORIZON` still
  bounds the monitor feed and the detection-at-all reading.

Rejected alternative: `tau_err(rho)`. It is a recovery time relative to the empirical jump. It is
not the instant at which the evidence stops accumulating, and not what the manuscript names
`tau_erase`.
