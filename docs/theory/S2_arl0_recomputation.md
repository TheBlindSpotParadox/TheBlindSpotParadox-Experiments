# Stream S2 — T2.0: stopping-time theory at the measured base rate

Deliverable 2 of stream S2, Phase 1. Produced by
`experiments/S2_theory/s2_arl0.py` on committed artifacts; no stream is simulated.

```bash
PYTHONHASHSEED=0 python experiments/S2_theory/s2_arl0.py
PYTHONHASHSEED=0 python experiments/S2_theory/s2_arl0.py --check     # self-check, writes nothing
PYTHONHASHSEED=0 python -m pytest tests/test_S2_theory.py -v
```

Interpreter and package pins: `docs/ENVIRONMENT.md`. Run from the repository root.

Artifacts: `results/S2_theory/tables/s2_arl0_columns.csv`, `s2_lambda_starve.csv`,
`s2_gate_T20.json`.

---

## 0. Three objects are called `p_0`

They never share a column header, and `theta*` and `ARL_0` are properties of the **pair**
`(p_pre, p_true)`, never of a single rate.

| symbol | object | value | nature |
|---|---|---|---|
| `p_true` | the classifier's actual pre-drift error rate | **0.024** | measured — `ssot.P0_MEASURED`, median `e_pre` over the 2 000 runs of arm `full`; `p0_hat_median` is flat at 0.024 on all twenty magnitudes of `tables/cusum_delta001_quantiles.csv` |
| `p_pre` | the reference rate the CUSUM recursion subtracts, `S_t = max(0, S_{t-1} + (x_t - p_pre) - delta)` | per call site | a **detector parameter**, not a property of the stream |
| `p_0^S1` | the value stream S1 assumed | 0.05 | assumption under audit; deliberately not registered in the SSOT |

**Call-site census of `p_pre`**, established from source, not assumed:

| site | `p_pre` actually passed |
|---|---|
| `exp_R1_generate_data.py:56` — external fixed arm | `0.05` literal → **`p_pre != p_true`** |
| `exp_R1_generate_data.py:81` — external empirical arm | mean of the 1 000-step warm-up (`0.01` if that mean is 0) |
| `exp_R2_instrumented_blind_spot.py:90` | mean of the warm-up (`0.05` if the buffer is empty) |
| `s6_recompute_cusum_delta001.py::partition` | `p0_hat` per `(arm, seed)`, on that run's own warm-up |
| R3 / R4 / R5 | no `p_pre` at all — River PageHinkley tracks its own running mean at `delta = 0.005` |

The one site where `p_pre != p_true` is R1's **fixed** arm. There the recursion carries a built-in
drift of `p_true - p_pre = -0.026` per step under the null, on top of `-delta_P`. That is not a
detail: it moves the Siegmund denominator from `delta_P = 0.01` to `p_pre + delta_P - p_true =
0.036` and the Cramér root from `0.681` to `1.700`, and it multiplies `ARL_0` at `lambda = 15` by
**4.8 x 10^5**. R1's fixed arm runs a detector that is, under the null, effectively deaf; its
empirical arm is the one calibrated to the stream. Both are reported by R1 and the distinction is
already in the artifact — it is stated here because a single `p_0` column would have hidden it.

---

## 1. Old and new, side by side

Cramér root from `E[exp(theta (X - p_pre - delta_P))] = 1`, `X ~ Bern(p_true)`, solved with
`scipy.optimize.brentq` on a bracket strictly above the trivial root `theta = 0`. `ARL_0` from
Siegmund (1985), `(exp(theta* lambda) - theta* lambda - 1) / (theta* d)` with `d` the magnitude of
the mean increment under the null, which equals `delta_P` exactly when the detector is calibrated.

| setting | `delta_P` | `p_pre` | `p_true` | `theta*` | `transfer_S1` | approximation `2 delta_P / (p(1-p))` |
|---|---|---|---|---|---|---|
| superseded | 0.005 | 0.05 | 0.05 | **0.198260** | 0.1983 | 0.210526 (+6.2 %) |
| A1 | 0.01 | 0.05 | 0.05 | **0.375479** | 0.3755 | 0.421053 (+12.1 %) |
| **principal (S2)** | 0.01 | 0.024 | 0.024 | **0.681291** | 0.6813 | 0.853825 (+25.3 %) |
| R1 fixed arm | 0.01 | 0.05 | 0.024 | **1.700134** | — | 0.853825 (−49.8 %) |
| band `q0.025` | 0.01 | 0.015 | 0.015 | **0.968367** | — | 1.353638 (+39.8 %) |
| band `q0.975` | 0.01 | 0.032 | 0.032 | **0.542242** | — | 0.645661 (+19.1 %) |

| setting | `ARL_0(8)` | `ARL_0(15)` | `ARL_0(25)` | `ARL_0(50)` |
|---|---|---|---|---|
| superseded | 2.32e3 | 1.57e4 | 1.37e5 | 2.04e7 |
| A1 | 4.30e3 | 7.26e4 | 3.18e6 | 3.79e10 |
| **principal (S2)** | **3.32e4** | **4.02e6** | **3.66e9** | **9.13e16** |
| R1 fixed arm | 1.32e7 | 1.94e12 | 4.70e19 | 1.35e38 |
| band `q0.025` | 2.38e5 | 2.10e8 | 3.37e12 | 1.10e23 |
| band `q0.975` | 1.31e4 | 6.27e5 | 1.42e8 | 1.10e14 |

`transfer_S1` L29–31 gives 2.3e3 / 1.4e5 / 2.0e7, 4.3e3 / 3.2e6 / 3.8e10 and 3.3e4 / 3.7e9 / 9.1e16
at `lambda = 8 / 25 / 50`. All nine agree to one significant figure.

**R1(a) verdict: REPRODUCED, all three columns.** Relative error on `theta*`: 2.0e-4 (superseded),
5.5e-5 (A1), 1.4e-5 (principal) — each inside the `1e-3` tolerance. The `0.005 / 0.05` pair,
which `transfer_S1` L23 declares reproduces exactly, is the certification that licenses the other
two, and it is asserted in `s2_arl0.demo()` and again in
`tests/test_S2_theory.py::test_transfer_S1_column_reproduces_under_R1a`. The third column had no
code provenance anywhere in the repository; it now has one.

Moving from the A1 setting to the measured base rate multiplies `ARL_0` by 7.7 at `lambda = 8` and
by **2.4 x 10^6** at `lambda = 50`.

**The approximation is dropped.** `2 delta_P / (p_0(1-p_0))` degrades monotonically as the setting
approaches the measured one — +6.2 % → +12.1 % → **+25.3 %** — and reaches +39.8 % at the lower end
of the sensitivity band. Only the numerical root is carried forward. The approximation row is to be
removed from `transfer_S1.md` at the post-gate edit, and it does not enter `prop3_v2.tex`.

### 1.1 Sensitivity band, with its provenance

`transfer_S1` L39 asserts a range of `[0.012, 0.040]`. That range **is** in the artifact, but it is
the per-run **minimum and maximum** of `e_pre` over the 2 000 runs of arm `full` — not a quantile
band, and not the per-magnitude dispersion of the median, which is flat at 0.024 on all twenty
points. Reporting it as a band overstates the spread by using two order statistics of a
2 000-sample.

Named estimator, named quantiles: the empirical quantile function of `e_pre` over the 2 000 runs of
arm `full` (per-run pre-drift rate on the 1 000-step warm-up, resolution 1e-3).

| `min` | `q0.025` | `q0.25` | median | `q0.75` | `q0.975` | `max` |
|---|---|---|---|---|---|---|
| 0.012 | **0.015** | 0.021 | **0.024** | 0.027 | **0.032** | 0.040 |

**Band used: `[0.015, 0.032]`**, the central 95 % of the per-run distribution. Across that band
`ARL_0` at `lambda = 50` spans `1.10e14` to `1.10e23` — **nine orders of magnitude**. A single
pooled `p_0` is therefore adequate for a point calculation and inadequate for any statement whose
conclusion depends on the size of `ARL_0`; `transfer_S1` open question 1 (whether a single pooled
`p_0` is admissible at all) is answered in the negative for that class of statement, and the
question of a per-magnitude `p_0` is moot here because the per-magnitude medians do not move.

### 1.2 `eps` is assumed, and its assumption is not silent

`eps = 0.05` (`ssot.EPS_MISS`) is a design target, never a measurement. **`ARL_0` carries no `eps`
dependence at all** — reporting a sensitivity of `ARL_0` to `eps` would be inventing a move that
the formula does not contain. `eps` enters exactly two quantities, and both are reported here. At
`Delta_e = 0.3268`, `W = 57.4`, `lambda = 50`:

| `eps` | `thm:floor` RHS | `lambda_starve` |
|---|---|---|
| 0.01 | 1.906 | 33.94 |
| **0.05** | **1.795** | **32.40** |
| 0.10 | 1.661 | 31.69 |

Both are logarithmic in `eps`: a factor of ten on the miss level moves the floor by 13 % and the
starvation boundary by 7 %. Neither conclusion in this document turns on the value.

---

## 2. The gate — rule R2

Decision variable and thresholds were fixed in `docs/prompts/s2-decision-rules.md`, committed at
`671aa29` before this script was run.

| reading | value | provenance | verdict |
|---|---|---|---|
| **empirical** | `lambda_FA = 15` | `R4_PHT_LAMBDA`, ProteuS pre-drift calibration (`\LambdaFA`) | **NON-EMPTY** |
| theoretical | `lambda_FA^ARL = 9.1274` | `ARL_0^{-1}(7.261e4)` at `p_true = 0.024`, `delta_P = 0.01`; target is R4's implied `ARL_0(15)` at `p_0 = 0.05` | **NON-EMPTY** |
| theoretical, band `q0.025` | 6.78 | `p_true = 0.015` | NON-EMPTY |
| theoretical, band `q0.975` | 11.05 | `p_true = 0.032` | NON-EMPTY |

against `lambda_op` on the `[0.20, 0.40]` envelope: interval **`[19.876, 22.398]`**
(`envelope_stats.json`, `lambda_op_bootstrap./0.20_0.40`, 10 000 replicates, seed 12345). The point
estimate `21.9283` is recorded and is **not** the decision variable.

> ## VERDICT: **NON-EMPTY**
>
> Carried by the **empirical** reading. Both readings are concordant, and the theoretical reading is
> invariant over the whole `p_true` sensitivity band.

**Why the empirical reading carries it.** `lambda_FA` is a threshold calibrated on measured
pre-change volatility, annotated as such in the manuscript preamble. Recomputing `ARL_0` at the
measured base rate changes what a given threshold *buys* in expected false-alarm time; it does not
move a threshold that was *set by measurement*. No recomputation of `ARL_0` mechanically displaces
`\LambdaFA = 15`. The theoretical reading is reported as the consistency check it is, and it points
the same way.

**Consequence.** The admissible set `{lambda >= lambda_FA} ∩ {lambda <= lambda_op}` is non-empty on
`[0.20, 0.40]`. `res:tension` and `rem:envelope` hold unchanged; `res:tension` does not simplify and
the published result does not change.

The direction is worth stating because it is the opposite of the risk the gate was opened against.
At the measured base rate the Bernoulli variance is smaller, large deviations of the reflected walk
are dearer, `theta*` nearly doubles, and `ARL_0` grows faster in `lambda`. The same false-alarm
budget is therefore bought with a **lower** threshold, not a higher one: `9.13` against the `15`
that R4 calibrated empirically. Correcting `p_0` upward-biased at `0.05` was making the theoretical
threshold requirement *larger* than it is.

---

## 3. T2.0(d) — restitution of the three lines marked `NOT RECOMPUTED`

Each is stated in `transfer_S1` L55–63 through the rectangular surrogate
`A = q(tau_ARF)(Delta_e - delta_P)`, withdrawn at `.tex` L385. They are restated against the
measured evidence, not re-evaluated through the withdrawn estimator.

### (i) Budget invariance — the claimed plateau is not what was measured

`transfer_S1` L61 claims `K = 18.5`, `alpha_exp = 0.98`, `A in [16.8, 18.1]` for
`Delta_e in [0.10, 0.50]`.

Measured: median `max_t A_unrefl` on arm `full` (`runs.parquet:a_unrefl_peak`), over the twenty
canonical magnitudes falling in `[0.1409, 0.4977]`:

| `Delta_e` | 0.028 | 0.085 | 0.141 | **0.194** | 0.327 | 0.416 | 0.498 |
|---|---|---|---|---|---|---|---|
| median ceiling | 4.44 | 19.69 | 32.26 | **36.60** | 33.51 | 28.15 | 19.24 |

**19.24 to 36.60, factor 1.90, peaking at `Delta_e = 0.1936` and declining thereafter, and
non-monotone.** The constant sits above the claimed band at every magnitude of the envelope, and
the profile is a broad hump, not a plateau. This reproduces `S6_causal_evidence.md` §4 exactly and
is the same finding as S6 open item 2.

### (ii) `lambda_starve` — restated at `delta_P = 0.01`, with `W` from the artifact

`eq:starve_boundary`: `lambda >= s_0 + mu W + sqrt(W/2 ln(W/eps))`, `mu := Delta_e - delta_P`.

**`p_0` does not enter this boundary except through `s_0`.** `mu` is a function of `Delta_e` and
`delta_P` alone, and the fluctuation margin is a function of `W` and `eps` alone. `s_0`, the
pre-drift value of the reflected statistic at `tau*`, is the sole channel — and `alpha = W/ARL_0`
is the second `p_0` channel in the floor of (iii), not here. `transfer_S1` L62 evaluates at
`s_0 = 0` and that convention is kept, so the move against L62 is attributable to `W` and to
`delta_P` alone and to nothing else.

`transfer_S1` L62: *43.7 at `Delta_e = 0.10`, monotone down to 29.0 at `Delta_e = 0.50`*. Those
values are recoverable only from a mean `tau_ARF` of 177.0 and 36.4 steps — R8's window, which
fault F6 supersedes. `W` is now taken per magnitude from the S6 campaign (arm `full`, mean):

| `Delta_e` | `W = tau_swap^(1/M)` | `W = tau_erase` | `W = tau_err(0.10)` |
|---|---|---|---|
| 0.0854 | 81.1 | 156.7 | 142.7 |
| 0.1409 | **87.5** | 200.1 | 180.0 |
| 0.1936 | 61.2 | 251.5 | 199.2 |
| 0.3268 | 32.4 | 247.5 | 227.4 |
| 0.4160 | 28.4 | 222.5 | 250.1 |
| 0.4977 | 25.2 | 36.0 | 198.8 |

Three readings, all of them findings rather than nuisances.

1. Under the first-swap window the boundary is **non-monotone**: it rises from 29.5 at
   `Delta_e = 0.028` to a maximum of 87.5 at 0.141 before descending to 25.2. L62's *monotone*
   is false at the weak end. The cause is the same one S6 §2 documents — weak-band swaps are
   noise-driven, so `tau_swap^(1/M)` is large exactly where `mu` is small, and the two effects
   compound instead of cancelling.
2. Under either erasure window the boundary is an order of magnitude above L62 across the whole
   mid-band: 199 to 267 against 29 to 44. A `lambda` satisfying it does not exist in any deployed range.
3. The `tau_erase` column collapses at the top of the grid (36.0 at `Delta_e = 0.4977`) because the
   exploitable transient itself collapses there — 47.6 steps — while `tau_err(0.10)` stays near 200.
   The two erasure estimators agree in the mid-band and diverge by a factor of 5.5 at the ceiling.

Full grid: `results/S2_theory/tables/s2_lambda_starve.csv`.

### (iii) The universal floor, recomputed through `thm:floor`

`A >= p_0(1-p_0)/Delta_max * d(1-eps || alpha) - W delta_P`, with `alpha = W/ARL_0` at
`lambda = 50`.

| `Delta_e` | `W` | `transfer_S1` L63 | at L63's own inputs | at the S2 inputs | reproduces? |
|---|---|---|---|---|---|
| 0.33 | 55 | 1.45 | **1.450** | **1.799** | **yes** |
| 0.10 | 13 | 4.56 | **6.277** | **7.943** | **no** |

The first line reproduces to three decimals, which identifies L63's unstated inputs exactly:
`p_0 = 0.05`, `delta_P = 0.005`, `eps = 0.05`, `lambda = 50`, `Delta_max = Delta_e`,
`ARL_0 = 2.04e7`.

**R1(b) verdict on the second line: UNREPRODUCED.** Under those same identified inputs the
`Delta_e = 0.10`, `W = 13` line returns **6.277**, not the 4.56 stated. No `lambda` on the
tabulated ladder returns 4.56 (`lambda = 8` gives 2.18, `lambda = 25` gives 4.02,
`lambda = 50` gives 6.277), and recovering 4.56 at `lambda = 50` would require either
`Delta_max = 0.137` where 0.10 is stated, or `p_0 = 0.036` where 0.05 is stated. Both numbers are
printed side by side and neither is absorbed into a tolerance. This is the second S1 numeral
without code provenance and the first one that does not reproduce.

**The floor moves UP at the measured base rate, not down.** `p_0(1-p_0)` falls from 0.0475 to
0.0234, which halves the prefactor — but `ARL_0` at `lambda = 50` rises from `2.04e7` to `9.13e16`,
so `alpha = W/ARL_0` collapses from `2.70e-6` to `6.02e-16`, and `d(1-eps || alpha)` grows enough to
more than compensate: +24 % at `Delta_e = 0.33`, +27 % at 0.10.

**The floor is not the binding constraint at the canonical operating point.** At
`Delta_e = 0.3268` the measured budget ceiling is 33.5 and the floor is 1.80, a factor of 19
above it; yet the `lambda = 50` monitor detects on 0 of 100 runs. What binds is the requirement,
not the floor: `R_CUSUM = lambda + sqrt(W/2 ln(1/eps)) = 50 + 9.3 = 59.3 > 33.5`. By the
two-regime reading that follows `thm:floor` in `framework_v2.tex`, the blind spot at that operating
point is **a property of the monitor's calibration, not an information-theoretic floor** — which is
exactly the regime in which `cor:split` says a different monitor family escapes. That distinction is
carried into `prop3_v2.tex`.

---

## 4. Status of the open questions this phase touched

| item | status |
|---|---|
| `transfer_S1` L25–31, third column | **REPRODUCED** (R1a), now with code provenance |
| `transfer_S1` L61, budget invariance | restated on the measured ceiling: hump, not plateau; factor 1.90 |
| `transfer_S1` L62, `lambda_starve` | restated at `delta_P = 0.01` with `W` from the artifact; `p_0`-invariant except through `s_0`; L62's monotonicity is false at the weak end |
| `transfer_S1` L63, universal floor | line 1 reproduces; **line 2 UNREPRODUCED** (R1b); both recomputed at the new `ARL_0` |
| `transfer_S1` open question 1, single pooled `p_0` | inadmissible for any statement depending on the size of `ARL_0`: nine orders of magnitude across the central 95 % band |
| `transfer_S1` open question 2, `eps = 0.05` | stated as an assumed miss level; `ARL_0` has no `eps` dependence; the two quantities that do are tabulated |
| T2.0 gate | **NON-EMPTY**, carried by the empirical reading, concordant and band-invariant |

Pending edits, deliberately **not** applied in this phase: the removal of the approximation row and
the retirement of the superseded columns in `transfer_S1.md` are tied in the S2 write perimeter to
the closure of open items 1 and 4, which belong to Phases 5 and 2.
