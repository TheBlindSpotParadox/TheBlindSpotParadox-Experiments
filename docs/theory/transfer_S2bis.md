# Transfer document — stream S2-bis (calibration, comparison fairness, narrative payload)

Parent `3f59b35`, branch `stream-s2bis`. Decision rules fixed before measurement in
`docs/prompts/s2bis-decision-rules.md` (`acbf764`).

**Headline.** The published flooding ratio is reproduced to four figures (10.570 against Table II's 10.57)
and **collapses to 1.270 [1.156, 1.426]** once each pipeline's false-alarm budget is set over the
span its detector actually runs armed. Rule B3 fires **COLLAPSE**; 89.9 % of the published
log-ratio is threshold-attributable. The flooding half of the thesis is reformulated, not
withdrawn — see §2.3 for the measurement and §2.8 for the patch.

**State of the manuscript assumed by every payload below.** S2's patches A (12 macros) and B
(`rem:flooding`) are **already applied on `main`** at `688bcf5`. Every SEARCH anchor in this
document is quoted against that post-patch text, not against the v64 text S2 saw. Line numbers
quote `main`; the pre-patch numbering of `plans/PLAN_S2-bis.md` is lower by 15 before
`rem:flooding` and by 19 after it. **Anchors are text, never line numbers.**

---

## 0. Two premises of the brief, contradicted by source before any measurement

Both were verified from source and are recorded in rule B0 rather than discovered late.

**(A) R5 does not run at a common `lambda = 15`.** `exp_R5_common.py:121-123` calibrates per
(variant, seed, pipeline) with `calibrate_lambda` (`:59-85`): bisection on
`S2BIS_LAMBDA_BRACKET` to at most `PHT_TARGET_FA = 1` false alarm on that pipeline's own warm-up
error stream, detector re-armed after each alarm. Table II's F1 ratio is **already** an
equal-false-alarm-budget comparison at the target *one FA per warm-up*, and `lambda_calibrated`
**is** the `lambda_eq` of rule B1 at that target. S2-bis proves the identity by re-deriving the
frozen column from the CSVs with an independent driver: exact equality on all six (variant,
pipeline) cells.

The site where `lambda = 15` is genuinely common to every pipeline is **R4**
(`exp_R4_main_table.py:165`), and R4 has **no warm-up at all** — the detector is armed at `t = 0`
(`:130-131`). Table I's `0/1080`, its `p ~ 2e-9` and every EDDM / ADWIN / KSWIN row sit on that
uncalibrated comparison. `evaluate:109-124` computes precision and discards it, so
`exp_R4_results_aligned_fusion.csv` carries only F1 and ADD.

**(B) R1's mis-set `p_pre` does not touch the published numerals.**
`exp_R1_generate_data.py:56` is real — `StrictCUSUM(0.05, DELTA_P, lambda_val)`, a bare literal in
the first positional slot — but it feeds `tau_det_fixed`, a column no aggregation reads.
`Share_Blind_Spot` and `Detection_Rate` are built at `:136-139` from `blind_spot_observed` and
`tau_det_emp_finite`, both functions of the **empirical** arm constructed at `:81` from the
1 000-step warm-up mean. R1 is a deliberate two-arm design whose control arm has never been
published.

---

## 1. Verdicts, one line each

| rule | object | verdict |
|---|---|---|
| B1 | the `ARL_0` target | **both reported**; `T_span` carries the verdict, `T_warm` is R5's own target and is reproduced exactly |
| B2 | `lambda_eq^emp` vs `lambda_eq^ARL` | **INAPPLICABLE** on five of six INSECTS cells (§2.5); CONCORDANT on one |
| B3 | the flooding gate | **COLLAPSE.** `rho` falls from **10.570** [9.354, 12.114] at the frozen calibration — which reproduces the published 10.57 — to **1.270** [1.156, 1.426] at the span budget, CI upper below the threshold of 2. COLLAPSE on all three variants at `lambda_eq` (§2.3) |
| B4 | threshold / residual decomposition | `gradual_balanced`: both terms positive, **89.9 %** threshold-attributable, residual `rho = 1.27`. The other two variants: terms differ in sign, **no percentage reported** (§2.4) |
| B5 | R1 `p_pre` | **UNDOCUMENTED DELIBERATE CHOICE** — no published numeral routes through the fixed arm; a sentence is owed, **no re-run is warranted** |
| B6 | R1(b) coincidence (T-E) | **REFUTED** on both tests |
| B7 | saturation and arming | fired: one INSECTS cell **NOT ATTAINABLE**; ProteuS returns **NOT BINDING**, a degenerate case B7 did not declare (§5) |
| B8 | bands | applied; the `[0.015, 0.032]` band is used only for S6-anchored statements |
| B9 | `alpha` disclosure | applied; `R_KSWIN` is quoted at both `alpha` everywhere |
| B10 | pseudo-replication | **PSEUDO-REPLICATED** on all three INSECTS variants |
| — | R4 non-regression | **identical** on all 6 480 rows at `lambda = R4_PHT_LAMBDA`: `F1` and `ADD` deltas both `0.0`, absent-`ADD` pattern identical (§2.7) |
| — | bit-reproducibility | P1 and P3 **full double run**, byte-identical; P2 **declared-subset double run** plus one full grid (`S2bis_calibration.md` §2) |

---

## 2. T-A — equal false-alarm budget

### 2.1 What R5 already is: `lambda_calibrated` IS `lambda_eq(T_warm)`

Re-derived from `data/insects/*.csv` by an independent driver that reproduces
`exp_R5_common.run_evaluation` with the threshold injected instead of calibrated (the two agree
bit-for-bit at the calibrated threshold — `tests/test_S2bis_calibration.py`). **Exact equality on
all six (variant, pipeline) cells**, not agreement to a tolerance:

| variant | pipeline | frozen `lambda_calibrated` | S2-bis `lambda_eq(T_warm)` |
|---|---|---:|---:|
| gradual_balanced | `pht_arf_c1` | 20.973088084657988 | identical |
| gradual_balanced | `pht_ht` | 132.5039466023445 | identical |
| abrupt_balanced | `pht_arf_c1` | 46.7646 | identical |
| abrupt_balanced | `pht_ht` | 44.9024 | identical |
| incremental_reoccurring | `pht_arf_c1` | 77.9377 | identical |
| incremental_reoccurring | `pht_ht` | 182.4685 | identical |

Table II's F1 ratio is therefore **already** an equal-false-alarm-budget comparison. What T-A has
to answer is not *"what if the budget were equalised"* — it is — but *"is the budget measured over
the right span"*.

### 2.2 It is not: the budget is set on the warm-up, the detector runs over the span

`get_warmup_steps` takes `INSECTS_WARMUP_FRACTION = 0.10` of the stream. The detector is then armed
over the whole **pre-change span** `[warmup, first valid drift)`, which is 1.7 to 4.8 times longer.
Measured on the detector-free calibration pass (30 seeds, external detector disabled so no reset
perturbs the pre-change error stream):

| variant | warm-up | armed span | span/warm | pipeline | `lambda_eq(T_warm)` | `lambda_eq(T_span)` | alarms over the span **at the T_warm threshold** |
|---|---:|---:|---:|---|---:|---:|---:|
| gradual_balanced | 2 414 | 11 614 | **4.81** | `pht_arf_c1` | 20.97 ± 4.65 | **92.96** ± 15.49 | **11.33** |
| | | | | `pht_ht` | 132.50 ± 0.00 | **185.71** ± 0.00 | **2.00** |
| abrupt_balanced | 5 284 | 9 068 | 1.72 | `pht_arf_c1` | 46.76 ± 10.69 | 71.80 ± 22.51 | 2.73 |
| | | | | `pht_ht` | 44.90 ± 0.00 | 47.60 ± 0.00 | 3.00 |
| incremental_reoccurring | 7 998 | 18 570 | 2.32 | `pht_arf_c1` | 77.94 ± 8.47 | 233.63 ± 18.66 | 3.07 |
| | | | | `pht_ht` | 182.47 ± 0.00 | 191.29 ± 0.00 | 4.00 |

**The headline finding of T-A.** The factor `6.3` that `rem:flooding` attributes to *"bagging
halves the ARF's pre-change error volatility"* is neither a property of bagging nor stable across
streams. It is the ratio `lambda_eq(T_warm)` HT / ARF, and it moves as follows:

| variant | HT/ARF at `T_warm` | HT/ARF at `T_span` |
|---|---:|---:|
| gradual_balanced | **6.318** | **1.998** |
| abrupt_balanced | 0.960 | **0.663** |
| incremental_reoccurring | 2.341 | **0.819** |

On *gradual_balanced* moving the budget from the warm-up to the span cuts the asymmetry by a factor
of **3.2**. On the other two variants **the sign reverses**: at the span budget the ARF receives a
*higher* threshold than the HT, which is the opposite of the mechanism the manuscript states. A
mechanism that holds on one of three streams and inverts on the other two is not a property of the
classifier family.

The direct measurement of the mismatch is the last column. At a nominally equal budget of one false
alarm, the ARF's warm-up-calibrated threshold admits **11.33** alarms over the span it actually runs
on *gradual_balanced* while the HT's admits **2.00** — a 5.7x asymmetry in *realised* false alarms
under a nominally equal budget, and again specific to that variant (2.73 vs 3.00 on abrupt, 3.07 vs
4.00 on reoccurring).

### 2.3 Rule B3 — the flooding gate: **COLLAPSE**

Decision variable `rho_eq = F1_bp(PHT+HT) / F1_bp(PHT+ARF c=1)`, seed-paired bootstrap, 10 000
resamples of the 30 seed-level pairs, `np.random.default_rng(S2BIS_BOOTSTRAP_SEED)`.

| variant | threshold | `F1` HT | `F1` ARF | `rho` | 95 % CI | verdict |
|---|---|---:|---:|---:|---|---|
| **gradual_balanced** | `lambda_ref` (`T_warm`, the frozen calibration) | 0.2500 | 0.0237 | **10.570** | [9.354, 12.114] | SURVIVES |
| | `lambda_eq` (`T_span`) | 0.5000 | 0.3938 | **1.270** | **[1.156, 1.426]** | **COLLAPSE** |
| abrupt_balanced | `lambda_ref` | 0.1270 | 0.1800 | 0.706 | [0.625, 0.811] | COLLAPSE |
| | `lambda_eq` | 0.1860 | 0.3190 | 0.583 | [0.517, 0.662] | COLLAPSE |
| incremental_reoccurring | `lambda_ref` | 0.3077 | 0.1906 | 1.614 | [1.508, 1.733] | COLLAPSE |
| | `lambda_eq` | 0.3077 | 0.3938 | 0.781 | [0.729, 0.845] | COLLAPSE |

**The `lambda_ref` row of `gradual_balanced` reproduces the published ratio to four figures**:
`10.570` against Table II's `10.57`, from an independent driver on the raw CSVs. The campaign is
therefore measuring the same object the manuscript reports, and the collapse below is not a
different experiment.

**At an equal false-alarm budget over the span the detector actually runs, the ratio falls from
10.570 to 1.270 and the CI upper bound is 1.426, below the COLLAPSE threshold of 2.** The verdict
is COLLAPSE on `gradual_balanced` and COLLAPSE on all three variants at `lambda_eq`.

**Both arms improve; the ARF improves far more.** On `gradual_balanced` the HT goes `0.2500 ->
0.5000` (x2.0) and the ARF `0.0237 -> 0.3938` (**x16.6**). The published `F1 = 0.02` for
PHT+ARF(c=1) is not what that pipeline can do on that stream — it is what it does at a threshold
calibrated on a 2 414-step warm-up and then run over an 11 614-step armed span.

**The mechanism, measured.** The asymmetry exists because the ARF's warm-up error rate is lower than
the HT's, and the manuscript is right about that much. It is not, however, a bagging-variance
property: it is a **learning-speed artefact of a short warm-up**, and the measurement separates the
two.

| variant | warm-up length | ARF warm-up rate | HT warm-up rate | ratio | `rho` at `lambda_ref` |
|---|---:|---:|---:|---:|---:|
| **gradual_balanced** | **2 414** (shortest) | **0.1329** | 0.4234 | **3.19** | **10.570** |
| incremental_reoccurring | 7 998 | 0.3038 | 0.4135 | 1.36 | 1.614 |
| abrupt_balanced | 5 284 | 0.3295 | 0.3925 | 1.19 | 0.706 |

The variant whose warm-up is shortest is the one where the two classifiers have least converged, is
the one with the largest warm-up-rate ratio, is the one with the largest `span/warm` mismatch
(4.81), and is the only one where the ratio survives at the frozen calibration. Lengthen the
calibration window and the asymmetry goes away; it is a property of *how long the operator looked*,
not of bagging.

### 2.3 bis The ladder at a genuinely common threshold — the brief's premise inverted

The brief asks whether the published flooding result is *"an artefact of comparing two pipelines at
a common threshold"*. The common ladder answers the opposite: it is an artefact of comparing them at
**different** thresholds. `F1_bp`, `gradual_balanced`, 30 seeds, both pipelines at the same
`lambda`:

| `lambda` | `F1` ARF(c=1) | `F1` HT | alarms ARF | alarms HT | pre-change alarms ARF | HT |
|---:|---:|---:|---:|---:|---:|---:|
| 8 | 0.0075 | 0.0080 | 264.4 | 250.0 | 133.9 | 112.0 |
| 15 (`R4_PHT_LAMBDA`) | 0.0154 | 0.0152 | 129.2 | 131.0 | 64.0 | 51.0 |
| 21 (≈ the ARF's `lambda_ref`) | 0.0251 | 0.0238 | 79.4 | 83.0 | 39.6 | 43.0 |
| 30 | 0.0435 | 0.0476 | 45.6 | 41.0 | 24.0 | 29.0 |
| 45 | 0.0161 | 0.0714 | 20.2 | 27.0 | 12.4 | 20.0 |
| 65 | 0.0384 | **0.0000** | 11.3 | 12.0 | 7.3 | 10.0 |
| 95 | **0.4025** | **0.0000** | 4.2 | 8.0 | 1.8 | 7.0 |
| 135 (≈ the HT's `lambda_ref`) | **0.5000** | 0.2857 | 3.0 | 6.0 | 1.0 | 4.0 |
| 200 | 0.5000 | 0.5000 | 3.0 | 3.0 | 1.0 | 1.0 |

**At no point on the ladder is the ARF pipeline worse than the HT pipeline.** They are
indistinguishable below `lambda = 30` (both flooding: 129 and 131 alarms at `lambda = 15`, of which
64 and 51 before the change), the ARF is strictly better at 65, 95 and 135, and they coincide at
200. The published contrast — ARF `F1 = 0.02` against HT `F1 = 0.25` — is the ARF read at `20.97`
against the HT read at `132.50`, two points on the same curve.

The HT column is a single deterministic trajectory repeated across 30 seeds (rule B10), which is
why it is non-monotone at 45-95; the ARF column is a mean over 30 genuinely distinct runs. That
asymmetry in the estimators is itself a reason not to read a ratio of the two as a pipeline
property.

### 2.4 Rule B4 — the decomposition

`ln rho(lambda_ref) = ln rho_eq + [threshold-attributable]`, both terms with seed-paired CIs.

| variant | `ln rho(lambda_ref)` | residual `ln rho_eq` | threshold-attributable | share reported? |
|---|---|---|---|---|
| **gradual_balanced** | **+2.3580** [2.2358, 2.4944] | **+0.2387** [0.1451, 0.3550] | **+2.1194** [1.9712, 2.2663] | **yes — 89.9 %** |
| abrupt_balanced | −0.3487 [−0.4691, −0.2089] | −0.5392 [−0.6559, −0.4121] | +0.1905 [−0.0135, +0.3925] | **no** — terms differ in sign |
| incremental_reoccurring | +0.4789 [0.4134, 0.5517] | −0.2468 [−0.3162, −0.1707] | +0.7257 [0.6304, 0.8246] | **no** — terms differ in sign |

On `gradual_balanced` both terms are strictly positive, so rule B4 permits the single percentage:
**89.9 % of the published log-ratio is threshold-attributable**, and the residual `+0.2387`
[0.1451, 0.3550] is the part that is not — a genuine but small coupling effect, `rho = 1.27`, whose
CI excludes 1. On the other two variants the residual and the threshold term have opposite signs and
**no percentage is reported**, exactly as the rule requires; the two signed terms are published
instead.

### 2.5 Rule B2: the analytic model is INAPPLICABLE on five cells of six

`lambda_eq^ARL` is the Siegmund inversion at `theta*(p_pre, p_true)`, with `p_pre = p_true` because
River's PageHinkley subtracts its own running mean, so the null drift is `PHT_DELTA` exactly.

| variant | pipeline | `lambda_eq^emp` | `lambda_eq^ARL` | ratio | B2 verdict |
|---|---|---:|---:|---:|---|
| gradual_balanced | `pht_arf_c1` | 92.96 | 27.40 | 3.39 | **INAPPLICABLE** |
| gradual_balanced | `pht_ht` | 185.71 | 36.36 | 5.11 | **INAPPLICABLE** |
| abrupt_balanced | `pht_arf_c1` | 71.80 | 31.03 | 2.31 | **INAPPLICABLE** |
| abrupt_balanced | `pht_ht` | 47.60 | 34.92 | 1.36 | CONCORDANT |
| incremental_reoccurring | `pht_arf_c1` | 233.63 | 38.02 | 6.15 | **INAPPLICABLE** |
| incremental_reoccurring | `pht_ht` | 191.29 | 46.02 | 4.16 | **INAPPLICABLE** |

Published as a finding, not tuned away, as rule B2 requires. The reason is visible in the measured
pre-change rates: the span's mean error rate is not the rate of a stationary null regime but of a
**learning curve** — on *gradual_balanced* the `pht_ht` warm-up mean is 0.4234 and the span mean
0.3138, still falling. Siegmund's `ARL_0` is derived for an i.i.d. Bernoulli null; a monotonically
decreasing error stream is a downward drift, which River's PageHinkley in its default `mode='both'`
also tests for. The analytic model is not wrong about its own hypotheses — the hypotheses do not
hold on the armed pre-change span of a real stream, and that is the publishable statement.

### 2.6 Rule B7 fired once

`incremental_reoccurring_balanced` / `pht_ht` at the `T_span` target is **NOT ATTAINABLE**:
`calibrate_lambda` falls back from `PHT_TARGET_FA = 1` to 3 and the attained count at the returned
threshold is 3, not 1. Reported with its bound; the cell is not silently read as a calibration.

### 2.7 ProteuS: the budget constrains nothing, and the collapse is a threshold

**Campaign.** 12 transitions x 30 seeds x 3 regimes = 1 080 streams; per stream, 6 PageHinkley
couples calibrated on the warm-up R4 never had (`[0, R4_T_DRIFT)`, external detector disabled) and
re-measured at `lambda_ref = 15` and at `lambda_eq`, plus an 8-point ladder on the two headline
couples and an EDDM arming diagnostic. `joblib.Parallel(n_jobs=-1)` over the (transition, seed)
grid with `exp_R4_main_table.process_transition_seed`'s per-worker PRNG lock reproduced verbatim.
**Non-regression: at `lambda = 15` the six couples reproduce R4's own `F1` and `ADD` on all 6 480
joined rows, `max_abs_F1_delta = 0.0`, `max_abs_ADD_delta = 0.0`, and the absent-`ADD` pattern
agrees exactly.** This is R4's pipeline, not a re-implementation.

**(i) The pre-drift error rate is exactly zero, on every one of the 1 080 streams.** Mean 0.0000 and
**maximum 0** — not a small number, the number zero, on every transition, regime and seed.
`simulate_stream:105` builds the target as `regime = (f_t > 0.5)` with `f_t = expit(4(t - tp)/w)`,
constant `0` for every `t < tp`, and `run_concept_drift:135`'s `y_pred = model.predict_one(x) or 0`
predicts that constant from the first step. The classifier has nothing to be wrong about before the
change.

**(ii) `lambda_eq` is therefore at the bracket floor for all six couples**: `1.000`, range
`[1.000, 1.000]` over 1 080 cells, `x15 = 0.07`. Verdict **NOT BINDING** (§5, item 5). No
false-alarm budget selects 15, or any other value: with `p_true = 0` there is no positive excursion,
no Cramér root and `ARL_0 = inf`.

**(iii) The floor is not merely uninformative, it is degenerate.** At `lambda_eq ~ 1` every couple
returns the same `F1 = 0.0148` and precision `0.0075`: the monitor floods, the classifier is reset
every few dozen steps and never learns, so all six pipelines become the same broken pipeline. An
equal-false-alarm-budget calibration is not a fairer comparison on this stream — it is no comparison
at all.

**(iv) The blind-spot collapse is a threshold, and the working threshold is measured.** The ladder on
the two headline couples, 1 080 runs per point:

| `lambda` | `F1` PHT+ARF(c=1) | runs with a detection | `ADD` | precision | `F1` PHT+HT | runs with a detection |
|---:|---:|---:|---:|---:|---:|---:|
| **5** | **1.0000** | **1080/1080** | **6.05** | **1.000** | 0.9269 | 1001/1080 |
| **8** | **0.9843** | 1063/1080 | 9.08 | 0.984 | 0.8972 | 969/1080 |
| 15 (`R4_PHT_LAMBDA`) | **0.0000** | **0/1080** | — | 0.000 | 0.8630 | 932/1080 |
| 25 | 0.0000 | 0/1080 | — | 0.000 | 0.8241 | 890/1080 |
| 40 | 0.0000 | 0/1080 | — | 0.000 | 0.7981 | 862/1080 |
| 60 | 0.0000 | 0/1080 | — | 0.000 | 0.7648 | 826/1080 |
| 90 | 0.0000 | 0/1080 | — | 0.000 | 0.7148 | 772/1080 |
| 130 | 0.0000 | 0/1080 | — | 0.000 | 0.6509 | 703/1080 |

**At `lambda = 5` the pipeline Table I prints in boldface as `F1 = 0.00` detects in 1 080 runs out of
1 080, with precision 1.000 and a mean delay of 6.05 steps.** It matches the KSWIN resolution's
`F1 = 1.00` and beats its raw `ADD` of 14 — with the PageHinkley monitor the manuscript says is
defeated, and with no architectural change at all. Precision 1.000 means **zero false alarms**, so
the threshold is not bought at any false-alarm cost; the budget, being vacuous, forbids nothing.

**(v) The evidence ceiling of the ARF at `c_int = 1` on ProteuS lies in `(8, 15]`.** The transition
is a cliff, not a slope: `0.9843` at 8 and `0.0000` at 15, with nothing in between on the declared
ladder. This is a direct measurement, on the stream where the collapse is reported, of the quantity
`A` the paper's whole framework is built on — and the paper measures `A` only on the S6 Bernoulli
traces. The bracket's resolution is the ladder's; a finer grid would narrow it and is left to a
stream that declares one.

The contrast with PHT+HT is the mechanism in one column: the non-adaptive learner degrades
**gracefully** across the whole ladder (0.9269 -> 0.6509, a factor 1.4 over a factor 26 in
`lambda`), because its error stream stays elevated and any threshold eventually accumulates. The
adaptive one has a cliff, because the evidence is erased before accumulation completes. That is
`prop:starvation`, confirmed — and it is a *ceiling*, not a collapse.

**(vi) Every couple at `lambda = 15`**, with the precision R4 computes and discards:

| couple | `F1` at 15 | precision at 15 | `F1` at `lambda_eq ~ 1` | precision at `lambda_eq` |
|---|---:|---:|---:|---:|
| PHT + HT | 0.8630 | 0.8630 | 0.0148 | 0.0075 |
| PHT + RF (Static) | 0.8454 | 0.8454 | 0.0148 | 0.0074 |
| PHT + ARF (`c = 32`) | 0.6241 | 0.6241 | 0.0148 | 0.0075 |
| SRP + PHT (`c = 32`) | 0.0870 | 0.0870 | 0.0148 | 0.0074 |
| **PHT + ARF (`c = 1`)** | **0.0000** | **0.0000** | 0.0148 | 0.0075 |
| **SRP + PHT (`c = 1`)** | **0.0000** | **0.0000** | 0.0148 | 0.0074 |

Precision equals `F1` at `lambda = 15` on every couple: there is exactly one true drift per stream
and no false alarms are raised at that threshold, so precision, recall and `F1` coincide. R4
discarded a column that was never going to disagree with the one it kept — which is itself worth
one sentence, since it means Table I's `F1` carries no false-alarm information at all.

### Patch T-A(ii) — `res:tension`, the `lambda_FA` provenance — **DEFERRED, do not apply before the v65 assembly**

Target: `docs/manuscript/articleA_blindspot_v64_camera_ready.tex` (`main` L416, pre-patch L397).
Two sites state that `lambda_FA = 15` was calibrated: the macro comment at `main` L55
(*"R4\_PHT\_LAMBDA, ProteuS pre-drift calibration"*) and `res:tension` in the body. The ProteuS
pre-change volatility is identically zero (§2.7), so neither is reproducible. `lambda_FA` is a
declared operating threshold, and `res:tension`'s conclusion does not depend on its provenance.

**Status: DEFERRED,** for the same reason as Patch T-B: `res:tension` sits at pre-patch L397, inside
`\subsection{The Decoupling Principle}\label{sec:decoupling}` (pre-patch L376-L411), the fourth of
the excluded subsections. The payload is recorded with its anchor and applied at assembly.

~~~~~~~~~
docs/manuscript/articleA_blindspot_v64_camera_ready.tex
<<<<<<< SEARCH
  With $\lambda_{\mathrm{FA}} = \LambdaFA$ calibrated on pre-change volatility and $\alpha = 0.05$, the measured ceiling gives $q_{0.05} = \QlowFloorLo$ at $\Delta e = \DeFloorLo$ and $\QlowFloorHi$ at $\Delta e = \DeFloorHi$. The admissible set $\{\lambda \ge \lambda_{\mathrm{FA}}\} \cap \{\lambda \le \lambda_{\mathrm{op}}\}$ is therefore empty for every envelope floored at or below $\DeFloorLo$ and non-empty for every envelope floored at or above $\DeFloorHi$. The detectability floor $\Delta e_c := \inf\{\Delta e : q_{0.05}(\Delta e) \ge \lambda_{\mathrm{FA}}\}$ lies strictly inside that interval, at $\Delta e_c = \DeCrit$ ($95\%$ bootstrap CI $\DeCritCI$, $n=300$). Standard synthetic benchmarks operate below it, which is why the failure mode does not surface on them.
=======
  With $\lambda_{\mathrm{FA}} = \LambdaFA$ as the declared false-alarm threshold of Section~\ref{sec:proteus} and $\alpha = 0.05$, the measured ceiling gives $q_{0.05} = \QlowFloorLo$ at $\Delta e = \DeFloorLo$ and $\QlowFloorHi$ at $\Delta e = \DeFloorHi$. The admissible set $\{\lambda \ge \lambda_{\mathrm{FA}}\} \cap \{\lambda \le \lambda_{\mathrm{op}}\}$ is therefore empty for every envelope floored at or below $\DeFloorLo$ and non-empty for every envelope floored at or above $\DeFloorHi$. The detectability floor $\Delta e_c := \inf\{\Delta e : q_{0.05}(\Delta e) \ge \lambda_{\mathrm{FA}}\}$ lies strictly inside that interval, at $\Delta e_c = \DeCrit$ ($95\%$ bootstrap CI $\DeCritCI$, $n=300$). Standard synthetic benchmarks operate below it, which is why the failure mode does not surface on them.
>>>>>>> REPLACE
~~~~~~~~~

The preamble comment at `main` L55 should read `% R4\_PHT\_LAMBDA, declared; see transfer\_S2bis
\S2.7` rather than `ProteuS pre-drift calibration`. That line is outside every excluded subsection
and can be changed now; it is a one-line edit and is not shipped as a payload.

### 2.8 Which of S2's patches this supersedes

**Patch A (12 macros) is not superseded**; S2-bis consumes it and extends it with Patch T-A(0)
below. **Patch B is superseded in its closing two sentences only** — the threshold-asymmetry coda of
its third paragraph. Everything else in Patch B stands: the starvation/flooding separation, the
`ARL_0` reading, the re-arm model and its declared caveat are unaffected by anything measured here.

S2 delivered Patch B with the threshold clause as a *coda*: an explanation appended after the
re-arm model. The measurement promotes it to the **claim**: 89.9 % of the published ratio is
threshold-attributable, the residual is `rho = 1.27` [1.16, 1.43], and the mechanism is a short
warm-up rather than bagging variance.

### Patch T-A(0) — preamble macros for S2-bis

Target: `docs/manuscript/articleA_blindspot_v64_camera_ready.tex`. Anchor: the closing line of the
S2 macro block installed by Patch A. Must be applied before Patch T-A(i), which consumes it.

~~~~~~~~~
docs/manuscript/articleA_blindspot_v64_camera_ready.tex
<<<<<<< SEARCH
\newcommand{\FloodArlGap}{3\times10^{4}}     % shortfall factor of the ARL\_0 model
=======
\newcommand{\FloodArlGap}{3\times10^{4}}     % shortfall factor of the ARL\_0 model

% ── Stream S2-bis, equal-false-alarm-budget calibration. Source: results/S2bis\_calibration/.
% Every value is read from a committed artifact; none is typed by hand.
\newcommand{\SpanOverWarm}{4.8}              % armed pre-change span / warm-up, gradual\_balanced
\newcommand{\LamEqArf}{93}                   % lambda\_eq at the span budget, PHT+ARF(c=1)
\newcommand{\LamEqHt}{186}                   % idem, PHT+HT
\newcommand{\FaSpanArf}{11.3}                % alarms over the span at the warm-up threshold, ARF
\newcommand{\FaSpanHt}{2.0}                  % idem, HT
\newcommand{\RhoRefMeas}{10.57}              % F1 ratio at the warm-up calibration (reproduced)
\newcommand{\RhoEqSpan}{1.27}                % F1 ratio at the span budget
\newcommand{\RhoEqSpanCI}{[1.16,\,1.43]}     % seed-paired bootstrap, 10\,000 resamples
\newcommand{\ThresholdShare}{90}             % \% of the log-ratio attributable to the threshold
>>>>>>> REPLACE
~~~~~~~~~

### Patch T-A(i) — `rem:flooding`, the asymmetry promoted from coda to claim

Target: `docs/manuscript/articleA_blindspot_v64_camera_ready.tex`, third paragraph of
`\begin{remark}[...]\label{rem:flooding}` in `sec:complexity` — **outside** the four-subsection
exclusion, so this one is applicable now. **Anchored on the text S2's Patch B put there**, which is
live on `main` since `688bcf5`, not on the pre-patch v64 sentence.

~~~~~~~~~
docs/manuscript/articleA_blindspot_v64_camera_ready.tex
<<<<<<< SEARCH
The asymmetry between the two pipelines is a threshold asymmetry: the one-false-alarm-per-warm-up calibration hands the ARF $\FloodLamArf$ and the HT $\FloodLamHt$, a factor of $6.3$, because bagging halves the ARF's pre-change error volatility (Section~\ref{sec:crossover}). The variance reduction that makes the ARF a good classifier buys it a low threshold, and a low threshold is what floods once the error stream stays elevated.
=======
The asymmetry between the two pipelines is a threshold asymmetry, and it is an artefact of where the false-alarm budget is measured. The one-false-alarm-per-warm-up calibration hands the ARF $\FloodLamArf$ and the HT $\FloodLamHt$, a factor of $6.3$; but the warm-up is $10\%$ of the stream while the detector then runs armed over a pre-change span $\SpanOverWarm$ times longer, and over that span the two nominally equal budgets buy $\FaSpanArf$ alarms for the ARF against $\FaSpanHt$ for the HT. Re-calibrating each pipeline to one expected false alarm over the span it actually runs gives $\LamEqArf$ and $\LamEqHt$, and the $F_1$ ratio falls from $\RhoRefMeas$ to $\RhoEqSpan$ $\RhoEqSpanCI$ (seed-paired bootstrap): $\ThresholdShare\%$ of the published log-ratio is threshold-attributable and the residual coupling effect is a factor $\RhoEqSpan$, small but with a confidence interval excluding $1$. Nor does the asymmetry reflect a variance property of bagging: it is largest exactly where the calibration window is shortest---the two classifiers have least converged there---and on the other two INSECTS variants, whose warm-ups are two and three times longer, the ordering reverses and the ARF receives the \emph{higher} threshold. What floods is not the adaptive classifier but a threshold set on a window too short to represent the regime the monitor will run in. Flooding remains parametrically controllable---alarms scale as $1/\lambda$ in the re-arm model---whereas starvation is structural: no CUSUM threshold escapes it (Section~\ref{sec:starvation_boundary}).
>>>>>>> REPLACE
~~~~~~~~~

The trailing sentence of the S2 paragraph (*"Flooding remains parametrically controllable..."*) is
carried into the replacement, so applying this patch after Patch B leaves exactly one copy of it.
The sentence *"The variance reduction that makes the ARF a good classifier buys it a low threshold"*
is **withdrawn**: the measurement contradicts it on two of three streams.

---

## 3. T-B — the R1 reference rate

**T-B(a). The source facts.** `exp_R1_generate_data.py:56` carries `0.05` as a bare literal in
`StrictCUSUM`'s first positional slot (AST-resolved, not grepped); `:81` carries the empirical
mean. On **R2**, `:90` reads `np.mean(errors_pre) if errors_pre else 0.05`, and the fallback is
**UNREACHABLE for any `T_DRIFT > 0`**: the buffer is appended at `:87-88` over
`t in [T_DRIFT - R2_WARMUP_WINDOW, T_DRIFT)` and read at `:89` when `t == T_DRIFT`, so it holds
1 000 entries (measured structurally, from the loop bounds alone — no classifier is instantiated).
**This is the opposite of what the brief expected.** R2's reference rate is the warm-up mean, like
R1's empirical arm. The literal is dead code, not a second instance of the R1 defect.

**T-B(b). The arithmetic and the within-run control.** The fixed arm runs at an effective
tolerance of `p_pre + delta_P - p_true = 0.036`, a factor **3.6** over the nominal `0.01`. Sourced
from `results/S2_theory/tables/s2_arl0_columns.csv`, row `R1 fixed arm`:

| quantity | calibrated arm | fixed arm | factor |
|---|---|---|---|
| Cramér root `theta*` | 0.6813 | **1.7001** | 2.50 |
| `ARL_0(lambda = 15)` | 4.02e6 | **1.94e12** | **4.83e5** |
| post-drift rate `mu` at `Delta_e = 0.10` | 0.090 | 0.064 | **−28.9 %** |
| idem at `Delta_e = 0.33` | 0.320 | 0.294 | −8.1 % |

The bias **inflates** the blind spot, and the slow-down is largest exactly in the weak-signal
regime the article claims.

**The effect on the two published numerals is exactly zero**, because neither routes through the
fixed arm. What S2-bis delivers instead is the paired within-run counterfactual the frozen parquet
already contains — both arms see the same post-drift error stream under the same seed and the same
`lambda`, so the fixed arm is a control, not a separate experiment
(`results/S2bis_calibration/tables/s2bis_r1_counterfactual.csv`, 200 seeds per `lambda`):

| `lambda` | `Share_Blind_Spot` published | fixed arm | `Detection_Rate` published | fixed arm |
|---:|---:|---:|---:|---:|
| 10 | 0.035 | 0.045 | 1.000 | 0.995 |
| 15 | 0.195 | **0.440** | 1.000 | 0.990 |
| 20 | 0.685 | 0.855 | 0.990 | 0.800 |
| **25** | **0.895** | **0.965** | **0.920** | **0.390** |
| 50 | 1.000 | 1.000 | 0.015 | 0.000 |

Had the fixed arm been the published one, the manuscript's headline pair at `lambda = 25` would
read `0.965 / 0.390` instead of `0.895 / 0.920`. **R1 is not re-run**; the decision belongs to the
orchestrator and rule B5 says it is not required.

**T-B(d). Actionable residue, outside the S2-bis perimeter.** `p_pre` is the one CUSUM parameter
with **no SSOT route and no guard**. `tests/test_S7_consistency.py:48-53` (`GUARDED_NAMES`) carries
no `p_pre`-shaped name; `GUARDED_PARAMS` (`:77`) carries none either; and the `StrictCUSUM` guard
added by A1 resolves the **`delta`** argument alone through the class's own `__init__` signature,
so a bare literal in the **first positional slot** passes every check the suite has. Two sites:
`exp_R1_generate_data.py:56` and `exp_R2_instrumented_blind_spot.py:90`. Recommendation: route the
reference rate through `config/experiment_ssot.py` and extend `cusum_delta_sites` to resolve the
`p_pre` slot the way it resolves `delta`. **No change applied** — both files are outside the
perimeter.

### Patch T-B — the sentence the manuscript owes — **DEFERRED, do not apply before the v65 assembly**

Target: `docs/manuscript/articleA_blindspot_v64_camera_ready.tex` (`main` L302). The single site
citing both `92\%` and `89.5\%`. `protocol_v2.tex` **does not exist** in
`docs/manuscript/sections/` and no file is invented to receive this.

**Status: DEFERRED.** `plans/PLAN_S2-bis.md` directs this payload at the inline site and that
direction is **not applicable**: `main` L302 falls inside `\subsection{The Starvation
Effect}\label{sec:starvation}`, which runs from L225 to L311 on `main` (L210 to L296 pre-patch) and
is one of the four subsections `CLAUDE.md` excludes until the v65 assembly. Patching it now means
the patch is lost at assembly or duplicated and divergent — the exact mechanism that had v63 being
edited while v64 was live.

The file that supersedes `sec:starvation`, `docs/manuscript/sections/framework_v2.tex`, is the
formal framework and carries **no** empirical Zombie-Alarm paragraph, so the replacement text has no
current home either; and `framework_v2.tex` is outside the S2-bis write perimeter in any case (S3
works there). The payload is therefore delivered with its anchor recorded, to be applied when
`sec:starvation` is assembled and not before. `tests/test_S2bis_calibration.py::`
`test_transfer_payloads_do_not_touch_the_excluded_subsections` enforces the marking.

~~~~~~~~~
docs/manuscript/articleA_blindspot_v64_camera_ready.tex
<<<<<<< SEARCH
In this regime, the CUSUM still triggers an alarm in most runs (Detection Rate $92\%$), but it does so \emph{after} the internal ARF has already swapped ($\tau_{\mathrm{ARF}} < \tau_{\mathrm{det}}$, or $\tau_{\mathrm{det}}$ censored, in $89.5\%$ of runs).
=======
In this regime, the CUSUM still triggers an alarm in most runs (Detection Rate $92\%$), but it does so \emph{after} the internal ARF has already swapped ($\tau_{\mathrm{ARF}} < \tau_{\mathrm{det}}$, or $\tau_{\mathrm{det}}$ censored, in $89.5\%$ of runs). Both figures are measured on the arm whose reference rate $p_{\mathrm{pre}}$ is estimated from the pre-drift warm-up. The same runs also carry a control arm holding $p_{\mathrm{pre}}$ at a nominal $0.05$ against a measured $\PzeroMeas$, hence an effective tolerance of $0.036$ rather than $\DeltaPtext$; on that arm the same threshold gives $39.0\%$ and $96.5\%$. We report the calibrated arm throughout, and note that a monitor whose reference rate is assumed rather than measured makes the blind spot look \emph{larger}, not smaller.
>>>>>>> REPLACE
~~~~~~~~~

---

## 4. T-E — rule B6, both tests, both failing

**VERDICT: REFUTED.** The hypothesis was that `transfer_S1.md` L73's `4.56` had been computed with
R1's effective tolerance `0.036` rather than with `delta_P`, making R1(b) a second symptom of the
same configuration defect instead of an independent reproduction failure.

| test | requirement | result |
|---|---|---|
| numeric | the floor at `p_0 <- 0.0360`, L73's other inputs held, rounds to `4.56` at the printed precision | **4.5688 → 4.57.** Fails |
| chronology | `0.036` was computable when the line was written | **Fails.** `transfer_S1.md` was introduced at `a3a481a` (2026-09-06) under the declared header *"`p_0 = 0.05`, `delta_P = 0.005`, `eps = 0.05`"*. `0.036` needs `CUSUM_DELTA_P = 0.01` (`8fb0875`, A1, 2026-09-12) and `P0_MEASURED = 0.024` (`a0009d4`, S2, 2026-09-12), both six days later. At `a3a481a` R1 carried `DELTA_P = 0.005`, so its effective tolerance then was **0.031**, not 0.036 |

**The competing explanation fits better.** `Delta_max = 0.137` with every other input at L73's
returns **4.56** exactly, at the printed precision, against the coincidence hypothesis's 4.57. And
the floor is a smooth, strictly increasing function of `p_0` on `[0.02, 0.06]`, so *some* `p_0`
below 0.05 recovers *any* value below 6.277: a numeric near-hit at 0.036 is guaranteed by
monotonicity and is not evidence on its own.

S2's R1(b) verdict stands as recorded: **UNREPRODUCED**, 6.277 against 4.56, both numbers carried
side by side and neither absorbed.

---

## 4 bis. T-D — EDDM: the `0/1080` is an arming failure

Measured on the streams that produce it, with `exp_R4_main_table.run_concept_drift` instrumented
for the error count; the instrumented loop reproduces R4's own detections exactly, so it is R4's
pipeline and not a re-implementation
(`results/S2bis_calibration/tables/s2bis_proteus_eddm_arming.csv`).

Full grid, 1 080 runs per couple:

| | EDDM + HT | EDDM + ARF (`c_int = 1`) |
|---|---:|---:|
| pre-change errors at `t = T_DRIFT` — mean / **max** | 0.0 / **0** | 0.0 / **0** |
| errors required (`warm_start`) | 30 | 30 |
| errors over the whole 8 000-step stream — median [min, max] | 32 [3, 32] | **9 [6, 12]** |
| runs in which the detector **never arms** | 17.7 % | **100 %** |
| runs raising at least one alarm | 885 / 1 080 | **0 / 1 080** |

The frozen Table I scores EDDM+HT at `882/1080`; the three-run difference is the alarms that fall
outside the scoring window `[d, d + tau]`, which the arming diagnostic counts and `F1` does not.
EDDM+ARF is `0/1080` under both readings.

**The pre-change error count is zero on every one of the 1 080 runs — mean and maximum both 0.**

**Both prior readings of the `0/1080` are wrong.** The brief transferred the S6 warm-start control
(24 errors against 30) from a 1 000-step Bernoulli trace to ProteuS. The plan corrected it with
`n_0_errors = 96.0` from `s2_eddm.json` — but that figure is `p_0(S6) = 0.024 x 4000`, the S6 base
rate applied to the ProteuS span *length*, and no ProteuS measurement of it existed before this
stream, because `exp_R4_main_table.py` records no error stream. The measured value is **0**.

The conclusion the brief reached is right and its reason is not: the `0/1080` **is** an unarmed
detector, because the ProteuS pre-change label is constant and the classifier is exact before the
change, and on the ARF arm the detector never arms at any point in the run. That is an *arming*
failure, not an accumulation failure: `prop:starvation`'s stopping-time argument never gets the
chance to apply. Full reading, and the site inventory, in
`docs/theory/S2bis_narrative_payload.md` (T-D). **No patch applied.**

This strengthens the phenomenon rather than weakening it — *nine errors in eight thousand steps* is
a sharper statement of evidence erasure than any alarm count — while withdrawing the mechanism
attributed to it.

---

## 5. Divergences from `plans/PLAN_S2-bis.md`, declared rather than silently absorbed

Four. In each case the plan's statement is contradicted by the repository's own arithmetic or by
measurement, and the code follows the arithmetic while this document records the divergence.

1. **`lambda_eq` is monotone INCREASING in `p_true`, not decreasing.** The plan's guard-rail list
   states *"`lambda_eq` monotone decreasing in `p_true` at fixed target"*. `theta*` solves
   `E[exp(theta (X - p - delta))] = 1` for `X ~ Bern(p)` and **shrinks** as `Var(X) = p(1-p)`
   grows; `ARL_0` is increasing in `theta` at fixed `lambda`; so a fixed false-alarm budget costs
   **more** threshold on a noisier pre-change stream. The frozen measurement agrees: `e_pre` 0.058
   → `lambda` 20.97 (ARF), `e_pre` 0.075 → `lambda` 132.50 (HT). Enforced in the corrected
   direction in `tests/test_S2bis_calibration.py` with the reason in the test docstring.
2. **`cor:split`'s crossing is not at `ln(1/alpha) ~ 13`.** Solved on the exact requirement curves
   (`s2bis_proteus_gate.json`, `cor_split_crossings`): `R_CUSUM` crosses `R_KSWIN` at
   `ln(1/alpha) = 16.34` (`lambda = 22.60`) and `R_ADWIN` at `18.97` (`lambda = 26.47`). The
   artifact's own ladder brackets it the same way — at `lambda = 25`, `ln(1/alpha) = 17.97` and
   `R_CUSUM = 34.27` has passed `R_KSWIN = 32.94` but not `R_ADWIN = 35.19`.
3. **Rule B10's "zero variance" must be read as exact distinctness.** `np.std` over 30
   bit-identical `float64` values returns `5.6e-17` on the reoccurring variant — cancellation in
   the two-pass formula, not dispersion. `nunique()` compares the stored values themselves and is
   the estimator the rule means.

4. **Both manuscript sites the plan directs T-A and T-B at are inside the excluded subsections.**
   `plans/PLAN_S2-bis.md` sends the T-B sentence to `.tex:287` and the `lambda_FA` provenance is
   carried by `res:tension` at `.tex:397`; the exclusion spans measured from the manuscript's own
   headings are `sec:race` L168-184, `sec:hydra` L185-209, **`sec:starvation` L210-295** and
   **`sec:decoupling` L376-411** (pre-patch numbering). L287 and L397 fall inside the last two.
   Neither is patched. Both payloads are delivered marked **DEFERRED** with their anchors recorded,
   and `tests/test_S2bis_calibration.py` fails on any SEARCH block anchored in excluded material
   that is not so marked. Two of the ten KSWIN immunity sites of T-C are in the same position and
   are flagged in `docs/theory/S2bis_narrative_payload.md`.

And one **undeclared degenerate case discovered in measurement**:

5. **Rule B7 declares the bisection CEILING terminal and says nothing about the FLOOR.** On ProteuS
   `lambda_eq` returns the lower end of `S2BIS_LAMBDA_BRACKET` for every couple, which means the
   budget is met at every admissible threshold and constrains nothing. That is a bound, exactly as
   `SATURATED` is, and must never be read as a calibrated value. The code reports it as
   **`NOT BINDING`**; `docs/prompts/s2bis-decision-rules.md` is **not** retro-edited. A future
   stream should add the floor case to B7 as written.

---

## 6. Open items handed forward

1. **`related_work_v2.tex` L108-109 and `.tex` L166** still carry the `R_EDDM` claim rule R5
   withdrew. S2 handed them forward; S2-bis hands them forward again, with the additional finding
   of §T-D that EDDM's failure on ProteuS is an arming failure and not an accumulation failure.
   Both are outside the S2-bis perimeter.
2. **`p_pre` has no SSOT route and no guard** (§3, T-B(d)). Two call sites, both outside the
   perimeter.
3. **R1's control arm has never been published.** The counterfactual table exists now
   (`s2bis_r1_counterfactual.csv`); whether the manuscript reports it is the orchestrator's call.
4. **The Table I/II caption's unit of statistical independence is wrong for every `*_ht` arm.**
   `exp_R5_common.build_model` and `exp_R4_main_table.make_ht` both return an unseeded
   `HoeffdingTreeClassifier`, so the HT arm has one effective replicate. Fixing it means seeding
   the tree, which changes frozen artifacts; S2-bis does not touch them.
5. **`s2_eddm.json`'s `n_0_errors = 96.0` for the `R4 ProteuS` history is `p_0(S6) x 4000`**, the
   S6 Bernoulli base rate applied to the ProteuS span length, not a ProteuS measurement.
   `s2bis_proteus_eddm_arming.csv` measures it. `results/S2_theory/` is outside the perimeter and
   is not rewritten.
