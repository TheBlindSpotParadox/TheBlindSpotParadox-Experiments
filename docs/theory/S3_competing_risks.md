# Stream S3 — the race as competing risks, and the effective ensemble size

Deliverable 3 of stream S3, phases P3, P4 and P4-bis. Every number is produced by a committed
script on a committed artifact.

```bash
PYTHONHASHSEED=0 python experiments/S3_dependence/s3_competing_risks.py
PYTHONHASHSEED=0 python experiments/S3_dependence/s3_competing_risks.py --check   # writes nothing
PYTHONHASHSEED=0 python -m pytest tests/test_S3_dependence.py -v
```

Artifacts: `results/S3/cif_bands.csv`, `results/S3/rho_meff.csv`,
`results/S3/hydra_equal_budget.json`, `results/S3/s3_competing_risks.json`.
Decision rules: `docs/prompts/s3-decision-rules.md` (`cd443f4`).

---

## 1. `tau_det*` is deleted from the reasoning

`prop:starvation_boundary` races `tau_ARF` against the scalar
`tau_det* := lambda / (Delta_e - delta_P)`. `tau_det` is a stopping time: it has a distribution, it
is right-censored when the monitor never crosses `lambda` inside the window, and it is measured —
`notation_map_v63_to_v2.md` already records `tau_det^*` as *removed, replaced by the random
tau_det*, and the manuscript had not followed.

The object S3 estimates instead is the **cumulative incidence of the two causes** of the race, under
a single administrative censoring at the common horizon `t_c = CENSORING_HORIZON = 4000` post-drift
steps:

```
cause 1  the ARF adapts first     { tau_ARF <  tau_det }
cause 2  the monitor fires first  { tau_det <= tau_ARF }
```

**No framework is introduced.** Under one administrative censoring at a common horizon,
Kaplan--Meier reduces to the empirical survival, the Aalen--Johansen estimator reduces to the
sub-distribution proportion, and `RMST(t_c) = mean(min(tau, t_c))` exactly.
`experiments/R6_hydra_factor/exp_R6_hydra_survival.py` already carries `km_curve`, `rmst` and
`km_median`; `s3_competing_risks.py` imports them.

### 1.1 D3 — the identity, re-verified rather than trusted

Tolerance fixed at `1e-9` before the measurement (S7 reports `9.1e-13`).

| quantity | value |
|---|---|
| cells re-verified (20 magnitudes × {HAT, ARF}) | **40** |
| worst `abs(RMST_KM(t_c) - mean(min(tau, t_c)))` | **9.095e-13** |
| tolerance D3 | `1e-9` |
| worst gap to the committed `rmst_hat` / `rmst_arf` of `results/audit_S7/hydra_survival.csv` | **0.00e+00** |

**Verdict D3: REPRODUCED.** The framework is re-used as is.

### 1.2 The censoring in this race is not what the plan expected

The plan records `tau_det` in R2 scenario A as *"entirely NaN"*. It is not: **5 of the 2000 runs
carry a finite `tau_det`** (0.25 %, which is the `<1 %` detection rate the manuscript reports for
Figure `fig:pht_scenarios`(A)). All five fire **after** the ARF has already adapted — they are
Zombie alarms, not detector wins. The exact counts are reported rather than rounded to zero.

More important, and structural: **the race carries no censored unit at all.** `tau_ARF` is observed
on every run at every magnitude (`censored_frac_arf = 0.0` on all 20 magnitudes of
`hydra_survival.csv`, re-derived here), so every run has a first event. A `NaN` `tau_det` is the
monitor **losing the race**, not a missing observation; it is never dropped, and the competing-risks
estimator needs no censoring correction. `censored_frac = 0.000000` across the whole table.

---

## 2. The measured race

`results/S3/cif_bands.csv`: 480 rows, 20 magnitudes × 3 thresholds × 8 time points, cumulative
incidence of each cause with a paired-on-seed percentile bootstrap (`N_BOOT = 10000`, seed
`20260906`, both imported from `exp_R6_hydra_survival` so the S3 bands and the S7 Hydra bands share
one convention). Incidences at the horizon:

| scenario | `lambda` | monitor fires at all | **monitor wins** | ARF wins | censored |
|---|---|---|---|---|---|
| A | 50 | 0.0025 | **0.0000** | **1.0000** | 0.0000 |
| B | 25 | 0.3925 | 0.0420 | 0.9580 | 0.0000 |
| C | 8 | 0.9615 | 0.9335 | 0.0665 | 0.0000 |

(means over the twenty magnitudes; per-magnitude rows with 95 % bands are in the artifact.)

**At `lambda = 50` the monitor never wins, at any magnitude, in any of the 2000 runs.**
`CIF_det(t_c) = 0.00` with bootstrap band `[0.00, 0.00]` on all twenty magnitudes, and
`CIF_ARF(t_c) = 1.00` with band `[1.00, 1.00]`. `P(tau_ARF < tau_det) = 1` is therefore a
*measurement*, not a bound — and it is what makes both bounds of `S3_dependence_bounds.md` vacant
at that operating point rather than merely loose.

**The race is not monotone in `Delta_e`.** At `lambda = 25` the monitor's win probability rises from
0.00 at `Delta_e = 0.028` to a maximum of **0.32** at `Delta_e = 0.141`, then falls back to 0.00
from `Delta_e = 0.361` upward. The monitor does best at *intermediate* magnitudes: a weak drift does
not move the error stream enough to cross `lambda` before the horizon, and a strong one is erased by
the ARF before the accumulation completes. The hump is the starvation effect stated as a
probability instead of as a threshold comparison, and it is not visible at all through `tau_det*`,
which is monotone in `Delta_e` by construction.

At `lambda = 8` the monitor wins 0.93 on average and 1.00 from `Delta_e = 0.287` upward — the
regime where `F_hat(tau_det*) = 0.00` and where §6 of `S3_dependence_bounds.md` finds the `F_HAT`
plug-in refuted.

### 2.1 `p_pre != p_true` at the R2 site — checked before the race was used

S2 established that `exp_R1_generate_data.py:56` passes a literal `p_pre = 0.05` against a measured
`p_true = 0.024`, an effective tolerance of 0.036 instead of 0.01. The same check on R2, from
source: `exp_R2_instrumented_blind_spot.py:90` passes **the mean of the 1000-step warm-up**, with
`0.05` used only if the buffer is empty (`docs/theory/S2_arl0_recomputation.md` §0, call-site
census). R2's `tau_det` is therefore calibrated on the stream, and the R1 defect does not transfer
to it. The `tau_det` used above is R2's, not R1's, and no R1 `tau_det` enters this document.

---

## 3. Effective ensemble size — the data constraint first

**No committed artifact carries the per-tree `tau_i` of the ARF.** `runs.parquet` carries four
order statistics per run — `tau_swap^(q)` for `q in {0.10, 0.25, 0.50, 1.00}`, which at `M = 10`
are `tau_(1)`, `tau_(3)`, `tau_(5)`, `tau_(10)` — on 2000 runs of arm `full`, with `tau_swap_q100`
censored on **227** of them (the full sweep of all ten trees does not complete inside the horizon).
R2 scenario A gives the minimum only. The `rho_hat` of T3.4 is therefore **not directly estimable**,
and is bracketed by two routes instead, with no re-execution and no new authorized deviation.

**(a) Moments under exchangeability.** With `tau_{r,i} = mu + a_r + e_{r,i}` exchangeable,
`Var(run mean) = sigma^2 (1 + (M-1) rho) / M = sigma^2 / M_eff`, so `M_eff = sigma^2 / Var(run mean)`
directly and `rho = ((M / M_eff) - 1) / (M - 1)`. The run mean is the average of **all ten** order
statistics and only four are committed; it is estimated by the trapezoidal quantile L-estimator on
the available indices, weights `(1, 2, 3.5, 2.5)/9`. **The approximation is declared, and
calibrated**: on 4000 synthetic runs of ten *independent* exponential draws the same estimator
returns `M_eff = 10.48` against the true 10, a `+4.8 %` bias (asserted in
`s3_competing_risks.demo()`). Complete cases only; the censored variant, substituting the horizon
for a censored `tau_(10)`, is reported beside it as the slow-side bracket.

**(b) Direct order-statistic matching.** `M_eff^(b) := the m for which E[min of m draws from F_hat]
equals the measured E[tau_(1:M)]`, solved by bisection on a continuous `m`, never passing through
`rho`. `E[min of m] = int_0^{t_c} (1 - F_hat(t))^m dt` is evaluated exactly on the empirical step
function, with censored runs entering at `t_c`, so it is a lower bound wherever the sample carries
censoring.

### 3.1 D4 — the two routes DISAGREE

Declared agreement factor: **1.5**. Measured: **13 of 20 magnitudes agree, 7 do not**.

| `Delta_e` | `rho_hat` (a) | `M_eff` (a) | `M_eff` (b) | ratio | agrees |
|---|---|---|---|---|---|
| 0.0282 | 0.0090 | 9.25 | 11.28 | 1.22 | yes |
| 0.0854 | −0.0206 | 12.28 | 9.81 | 1.25 | yes |
| 0.1409 | 0.0188 | 8.55 | 8.38 | 1.02 | yes |
| 0.1936 | 0.0268 | 8.06 | 7.77 | 1.04 | yes |
| 0.2426 | 0.0119 | 9.03 | 7.43 | 1.22 | yes |
| 0.2871 | 0.0173 | 8.65 | 7.13 | 1.21 | yes |
| **0.3268** | **0.0102** | **9.16** | **6.99** | **1.31** | yes |
| 0.3614 | 0.0348 | 7.62 | 6.64 | 1.15 | yes |
| 0.3910 | 0.0125 | 8.99 | 5.87 | 1.53 | **no** |
| 0.4157 | 0.0348 | 7.62 | 5.27 | 1.45 | yes |
| 0.4360 | 0.0204 | 8.45 | 5.26 | 1.60 | **no** |
| 0.4523 | 0.0526 | 6.79 | 5.76 | 1.18 | yes |
| 0.4650 | 0.0359 | 7.56 | 5.51 | 1.37 | yes |
| 0.4749 | −0.0070 | 10.68 | 5.14 | 2.08 | **no** |
| 0.4823 | 0.0335 | 7.69 | 5.02 | 1.53 | **no** |
| 0.4877 | 0.0383 | 7.44 | 5.12 | 1.45 | yes |
| 0.4916 | 0.0369 | 7.51 | 5.26 | 1.43 | yes |
| 0.4944 | −0.0203 | 12.23 | 5.31 | 2.30 | **no** |
| 0.4964 | −0.0085 | 10.83 | 5.25 | 2.06 | **no** |
| 0.4977 | −0.0101 | 11.00 | 5.29 | 2.08 | **no** |

**Verdict D4: DISAGREE.** Both values are carried side by side as published model uncertainty. **No
single `M_eff` enters the manuscript, and the two are never averaged.** The disagreement is
structured, not noise: route (a) hovers near `M_eff = M = 10` (`rho_hat` within `[-0.021, 0.053]`,
i.e. *no measurable within-run correlation of the swap times*), while route (b) falls monotonically
from 11.3 to 5.1 as the drift strengthens. The two are not measuring the same thing, and §4 says
why.

At the canonical magnitude `Delta_e = 0.3268` the interval is **`M_eff in [6.99, 9.16]`** against a
nominal `M = 10`, and the measured Hydra factor at that magnitude is `7.99x [6.40, 9.72]`.

---

## 4. P4-bis — the Hydra factor is not an equal-budget comparison, and cannot be made one here

S2 measured that one-false-alarm-per-warm-up calibration hands the ARF `lambda = 20.97` and the HT
`lambda = 132.50`: variance reduction by bagging buys a low threshold. The Hydra factor compares
`tau_HAT` (`M = 1`) against `tau_ARF` (`M = 10`) at a common nominal internal-clock setting, so part
of the measured factor may be a difference of learner, not an acceleration of ensemble.

### 4.1 D4-bis, branch 2: NOT PRODUCED, and why

**No committed artifact records the pre-drift error *stream* of a single tree**, standalone or
inside the ARF. `R6_hat_instrumented.parquet` commits four columns (`boundary_shift`, `seed`,
`tau_hat`, `delta_e`) and no `e_pre`; `runs.parquet` commits `e_pre` for **ensemble arms at
`n_models = 10` only** (`full`, `no_swap`, `frozen`, `static`); no `traces.parquet` is committed.
The equal-false-alarm-budget threshold is therefore not computable without a new campaign.
**Equality of budget is not assumed, and the factor is not corrected by a guess.**

Sensitivity bound from what *is* committed, reported as a bound of the wrong contrast rather than as
a substitute for the missing one:

| arm | `n_models` | mean `e_pre` | s.d. `e_pre` |
|---|---|---|---|
| `full` (adaptive ARF) | 10 | 0.023880 | 0.004589 |
| `no_swap`, `frozen` | 10 | 0.023880 | 0.004589 |
| `static` (non-adaptive bagged HT) | 10 | 0.034030 | 0.009168 |

Variance ratio `static / full` = **3.99**. That contrast isolates the effect of **adaptation** on
the pre-drift error stream, at fixed `M = 10`; it does not isolate the effect of **ensemble size**,
which is the one P4-bis needs.

### 4.2 The measurable substitute: the slowest member

The assimilation the manuscript makes silently — `F_HAT`, the law of a standalone HAT, used as the
law of a tree *inside* the ARF — is testable on committed data through the **slowest** member,
because `tau_swap_q100` is `tau_(10)`:

| `Delta_e` | `E[tau_(10)]` measured | `E[max of 10 draws from F_hat]` | mismatch (model / measured) | Hydra RMST | Hydra median |
|---|---|---|---|---|---|
| 0.1409 | 3063.78 | 3112.84 | **1.016** | 4.12x | 5.32x |
| 0.3268 | 1458.72 | 1326.71 | **0.910** | 7.99x | 3.10x |
| 0.4977 | 981.10 | 482.32 | **0.492** | 4.65x | 1.79x |

(full column in `results/S3/rho_meff.csv`; the mismatch falls monotonically from ≈1.09 at the
weakest magnitude to 0.49 at the strongest.)

**Both tails of the ARF member's marginal are wrong under the plug-in, and in opposite directions.**
The slowest member is up to twice as slow as `F_HAT` predicts (mismatch 0.49), while
`S3_dependence_bounds.md` §6 shows the fastest member is strictly faster than *any* HAT run. The
member marginal is **more dispersed** than `F_HAT`, which is what Poisson weighting and
`max_features = 1` would produce. That is the structural reason route (a) and route (b) of §3.1
disagree: (b) absorbs the marginal mismatch into `M_eff`, (a) does not.

**Consequence, published rather than resolved.** The Hydra factor is reported as what it is
measured to be — `tau_HAT` against `tau_ARF` at a common nominal setting, `4.12x [3.45, 4.96]` at
`Delta_e = 0.14` and `7.99x [6.40, 9.72]` at `Delta_e = 0.33`, censoring-aware lower bounds — and it
is **not** decomposed into a threshold part and an ensemble part, because the committed data do not
support the decomposition. The manuscript must not present it as a pure ensemble-size effect. The
divergence between the expectation ratios and the median ratios (`5.32x` and `3.10x`, crossing
between the two magnitudes) is reported alongside, per D4: a typical run at `Delta_e = 0.33` shows
`3.1x`, and the claim is on expectations.

### 4.3 Handed to the orchestrator

Record the per-step pre-drift error stream of (i) a standalone HAT and (ii) one tree inside the ARF,
on matched seeds and magnitudes; calibrate both to one false alarm per warm-up; re-derive the factor
at equal budget. Until then the decomposition is `NOT PRODUCED` and is declared so.

---

## 5. Statutory guard-rail — degenerate inputs

`tests/test_S3_dependence.py` and `s3_competing_risks.demo()`.

| input | expected | why the opposite would pass on a wrong reading |
|---|---|---|
| `tau = NaN` | restricted to **`t_c`**, never dropped | dropping a censored run removes the slowest adaptations and biases every mean downward — the defect `exp_R6_hydra_survival` was written to fix |
| censored exactly at `t_c` | RMST identity still holds to `1e-9` | if it did not, the censoring would not be purely administrative and no estimator here would apply |
| `tau_det = NaN`, `tau_ARF` observed | cause = **ARF wins** | coding it as censored would silently discard the blind-spot events, which are the whole phenomenon |
| degenerate sample (all draws equal) | `E[min of m] = E[max of m] =` that value, any `m` | a formula that moved with `m` on a point mass would be integrating the wrong survival |
| `m = 1` | `E[min] = E[max] =` restricted sample mean | the two integrals are the same object at `m = 1`; a discrepancy is an off-by-one in the step function |
| `m` increasing | `E[min]` strictly decreasing, `E[max]` strictly increasing | an inversion means `(1-F)^m` and `1-F^m` were swapped |
| ten **independent** synthetic draws | L-estimator returns `M_eff` in `[6, 14]` | outside that band the four-order-statistic approximation is not fit for its declared purpose and the `rho_hat` column is meaningless |

---

## 6. What this document does not cover

- **`rho` is never measured, only bracketed.** The per-tree `tau_i` do not exist in any committed
  artifact; §3 produces an interval, and D4 forbids collapsing it.
- **The member marginal `F` is not estimated.** §4.2 measures that `F_HAT` is not it, in both tails,
  and stops there.
- **The equal-budget Hydra factor is NOT PRODUCED**, with the missing measurement named in §4.3.
- **`s_0` is still never measured** (`transfer_S2` open item 4); nothing here changes that, and no
  statement below depends on it.
- **R1 is not used.** Its fixed arm carries `p_pre != p_true` (S2 §0); §2.1 checks R2 instead of
  inheriting the defect.
