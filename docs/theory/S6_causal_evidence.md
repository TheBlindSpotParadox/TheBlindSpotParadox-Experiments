# Stream S6 — causal evidence report

Verdicts of the synchronised-trace campaign on the three faults S6 was opened to close (F6, F7,
F25), on the Hydra question, and on the blocking gate stated in
[`transfer_S1.md`](transfer_S1.md). Every number below is read from a committed artifact; the
commands that regenerate them are at the end.

## 1. Campaign

| item       | value                                                                          |
| ---------- | ------------------------------------------------------------------------------ |
| grid       | 100 seeds x 20 canonical magnitudes x 4 causal arms = 8 000 run records        |
| stream     | canonical family, `N_STEPS = 8000`, drift at `t = 4000`, `M = 10`, `c_int = 1` |
| traces     | 40 000 000 rows, `[tau* - 1000, tau* + 4000)`, hive-partitioned by `delta_e`   |
| wall clock | 1 218.6 s on 24 physical cores (48 logical), `PYTHONHASHSEED=0`                |
| artifacts  | `results/S6_synchronized_traces/data/` (403 MB), `tables/`, `figures/`         |

Arms. `full` is the nominal ARF. `no_swap` and `frozen` are `copy.deepcopy` forks taken at
`tau_swap^(1/M)`, the instant of the first post-drift replacement, on the same materialised stream:
`no_swap` keeps learning with both internal detector paths made inert, `frozen` stops learning
entirely. `static` is R3's non-adaptive `BaggingClassifier`. Gate G1 certified the fork as
state-equivalent and memory-disjoint over 150 forks; gate G0 certified that returning `predict_one()`
to the loop changes no swap chronology and consumes no entropy, which is what allows the ensemble
error and the internal statistics to be read off one trajectory.

Forks were taken on 2 000 / 2 000 cells; `tau_swap^(1/M)` is censored on none.

## 2. Verdict on F6 — the first swap is not ensemble adaptation

`tau_swap^(1/M) = min_i tau_i` understates the adaptation of the ensemble by roughly one order of
magnitude, at every magnitude on the grid.

| Delta_e | tau_swap^(1/M) | tau_swap^(1/2) | tau_swap^(1) | ratio (1)/(1/M) | N_swap | distinct trees |
| ------: | -------------: | -------------: | -----------: | --------------: | -----: | -------------: |
|   0.085 |          417.5 |         1556.0 |       3362.0 |             7.3 |     21 |             10 |
|   0.194 |          150.0 |          976.0 |       2289.5 |            14.6 |     24 |             10 |
|   0.327 |           53.0 |          130.5 |       1221.5 |            23.4 |     20 |             10 |
|   0.416 |           38.5 |           74.0 |        819.0 |            21.1 |     14 |             10 |
|   0.498 |           29.0 |           49.5 |        482.0 |            15.0 |     10 |             10 |

Pooled median ratio `tau_swap^(1) / tau_swap^(1/M) = 17.9`. The full ensemble has still not
completed its turnover at the censoring horizon in 43 % of runs at `Delta_e = 0.085`.

Two further readings.

- **The Hydra is a weak-drift phenomenon.** `N_swap / distinct trees` falls monotonically from 2.7
  at `Delta_e = 0.028` to exactly 1.0 for every `Delta_e >= 0.465`: above that magnitude each tree is
  replaced once and never again inside the horizon. Any claim that repeated replacement is the
  mechanism of the paradox is therefore bounded to the weak band.
- **Distinct trees must be counted by tracker-key INCREMENT, not by key appearance.** At the drift
  instant the median number of trees already carrying a `_drift_tracker` key is 10 of 10 — warm-up
  noise has replaced every tree at least once. A `tau_swap` defined on the first appearance of a key
  returns `NaN` on every run of this campaign. This is recorded because the Phase-1 mandate specified
  "the diff of `_drift_tracker` keys"; the literal reading is unmeasurable and the implementation
  diverges from it deliberately (`s6_defs.distinct_trees_cum`).

**Rank correlation.** `tau_swap^(1/M)` does retain predictive content once the magnitude is held
fixed, but unevenly (Spearman, arm `full`, `n = 2000`):

| target             | pooled | weak (`<=0.15`) |   mid | strong (`>0.35`) |
| ------------------ | -----: | --------------: | ----: | ---------------: |
| `A` (framework)    |  0.713 |           0.404 | 0.447 |            0.569 |
| `tau_err(0.50)`    |  0.850 |           0.059 | 0.726 |            0.775 |
| `tau_err(0.10)`    |  0.694 |           0.097 | 0.345 |            0.531 |
| `tau_erase^argmax` |  0.640 |           0.348 | 0.105 |            0.427 |

In the weak band the first swap carries essentially no information about the recovery times
(0.06 / 0.10): those replacements are noise-driven and are not the adaptation event.

**Accelerated failure time.** Log-normal AFT for `tau_erase` with exact right censoring at
`T_h = 2500` (`n = 1974`, 8.2 % censored, converged):

```
log tau_erase = 4.661 + 0.659 log tau_swap^(1/M) + 0.206 log Delta_e + 0.851 eps
                (0.115)  (0.023), z = 28.8         (0.035), z = 5.8
```

The elasticity is 0.66, significantly below 1 (`z = (0.659 - 1)/0.0229 = -14.9`): doubling the first
swap time multiplies the erasure time by 1.58, not by 2. `tau_swap^(1/M)` is a compressed, biased
scale for the quantity it is used to stand for. **F6 confirmed.**

## 3. Verdict on F7 — the rectangle is not an approximation

`A_rect = Delta_e x tau_swap^(1/M)`, the rectangle R8's reasoning implies, is not a bounded proxy in
either direction:

| Delta_e      | 0.028 | 0.085 | 0.141 | 0.194 | 0.327 | 0.436 |     0.452 |      0.498 |
| ------------ | ----: | ----: | ----: | ----: | ----: | ----: | --------: | ---------: |
| `A / A_rect` |  2.05 |  0.74 |  1.09 |  1.79 |  2.70 |  1.06 | **-0.15** | **-14.12** |

The ratio is non-monotone, spans 2.7 to -14.1, and **changes sign**: for `Delta_e >= 0.452` the
integrated budget `A = sum (e_t - p_0)` over `T_h` is negative, because the adapted ensemble ends the
window with a LOWER error rate than it had before the drift (`err_post_mean` 0.010 against
`e_pre = 0.024` at `Delta_e = 0.498`). A far-shifted boundary makes the classes more separable; the
ARF exploits it. A rectangle of positive height cannot approximate a negative area. **F7 confirmed,
and more strongly than stated: the defect is not calibration, it is sign.**

The same holds for the framework rectangle `(Delta_e - delta_P) * W` of `def:budget`, but that
comparison is contaminated — see section 6, `W` is not estimable on this stream.

## 4. Budget invariance — the formal content of the paradox, measured

The threshold-free evidence ceiling `max_t A_unrefl(t)` is the maximum accumulation any CUSUM-class
monitor can hold. It needs no smoothing window, no `tau_erase` and no rectangle, so it is the one
budget statistic free of every definitional dispute above.

| Delta_e   | 0.028 | 0.085 | 0.141 |    0.194 |  0.327 |  0.416 |      0.498 |
| --------- | ----: | ----: | ----: | -------: | -----: | -----: | ---------: |
| `full`    |   4.4 |  19.7 |  32.3 | **36.6** |   33.5 |   28.2 |       19.2 |
| `no_swap` |   3.0 |  19.3 |  32.4 |     38.0 |   43.5 |   44.1 |       36.0 |
| `frozen`  |  14.6 |  78.6 | 166.7 |    393.9 | 1063.6 | 1443.0 | **1809.0** |
| `static`  |   2.0 |  11.8 |  28.7 |     47.4 |  104.7 |  139.5 |      190.7 |

Over `Delta_e` in [0.10, 0.50] the ceiling on the adaptive ensemble varies by a factor of **1.90**
(19.2 to 36.6) and is non-monotone, peaking at `Delta_e ~ 0.19` and then DECLINING as the drift grows.
On the counterfactual branch where adaptation stops, the same quantity varies by a factor of **124**
(14.6 to 1809) and is monotone increasing.

That contrast is `prop:invariance` demonstrated, with its mechanism isolated rather than assumed:
increasing the magnitude of a drift does not increase the evidence delivered to an external monitor,
and the reason is adaptation, because removing adaptation restores the scaling.

Operationally, at `lambda = 50`:

| arm      | `P(max A_unrefl >= 50)` | `P(>= 25)` |
| -------- | ----------------------: | ---------: |
| `full`   |               **0.009** |      0.456 |
| `frozen` |               **0.927** |      0.959 |

The adaptive ensemble starves a `lambda = 50` monitor in 99.1 % of runs; the same stream, same seeds,
same fork, with adaptation suppressed, feeds it in 92.7 %.

Two calibration remarks against the S1 numbers. The claimed band was `A` in [16.8, 18.1] with
`K = 18.5`; measured is 19.2 to 36.6, so the constant is 1.0x to 2.0x above the band and the profile
is a broad hump rather than a plateau. And `p_0` is measured at **0.024**, not the 0.05 at which
`transfer_S1` computes `theta*`, `ARL_0` and `lambda_starve`; every one of those figures should be
recomputed at the measured base rate before being carried into the manuscript.

## 5. Causal verdict on the Hydra — real, significant, and marginal

`full` and `no_swap` share one stream, one history and one fork, and differ only by the replacements
suppressed after the first. Paired sign test at the seed level, arm difference `full - no_swap`:

| quantity                       |    n | positive | median difference |        p |
| ------------------------------ | ---: | -------: | ----------------: | -------: |
| `A` (framework, common window) | 1996 |      417 |         **-5.15** | 1.6e-158 |
| `A` (Phase-1, signed)          | 1981 |      629 |             -9.00 |  1.6e-60 |
| `tau_erase^argmax`             | 1741 |      550 |             -74.0 |  2.6e-54 |

The replacements after the first do erase further evidence, and the effect is not marginal
statistically: `p ~ 1e-158`. It is marginal **in magnitude**. Decomposing against the `frozen`
branch, which never adapts again:

```
E_total  = A_frozen - A_full       median 826.7      evidence erased by all adaptation
E_learn  = A_frozen - A_no_swap    median 819.2      erased by INCREMENTAL LEARNING alone
share_learn = E_learn / E_total    median 0.993      IQR [0.987, 0.998]   n = 1979
```

**99.3 % of the erasure is done by incremental learning of the M-1 surviving trees.** Both
counterfactual arms fork AT the first replacement and share it with `full`, so this contrast
identifies post-fork learning, not the first swap. The first swap's own contribution is NOT
identified by this design; an arm with replacement suppressed from `tau*` onward would be required.
Section 8 point 6 bounds it mechanically: 100 % of replacements install a tree that has learned
nothing, and one member in ten alters one vote in ten.

Replacements after the first account for 0.7 %, about 5 units of budget. Volumetrically marginal,
decisively not: at `Delta_e = 0.327` suppressing them raises the median ceiling from 31.3 to 41.1
and lifts detection at `lambda = 50` from 0/100 to 18/100. The residue flips decisions because the
threshold sits in the upper tail of the ceiling distribution, not because it carries energy.

**Verdict: the Hydra is not the volumetric mechanism of the blind spot.** It is an onset
accelerator — the forest reacts on `min_i tau_i`, so the learning phase that erases the residual
starts 4.1x to 8.0x sooner — and a terminal decision lock, removing up to 23 % of residual
detection (max at `Delta_e = 0.361`). Erasure itself is ordinary incremental learning.

**Where the erasure actually happens.** Segmented regression of `A_unrefl(t)`, one continuous
one-knot least-squares fit per run on the `full` arm (`n = 2000`, median `R^2 = 0.968`, slopes
+0.118 -> -0.015):

```
median knot            222.5
median tau_swap^(1/M)   40.0
median knot / tau_swap   2.64
sign test knot > tau_swap:  1913 / 2000,  p < 1e-300
```

The slope break of the evidence curve is **not** at the first swap; it is 2.6x later. The first swap
opens the erasure, it does not complete it — which is the same statement the AFT elasticity of 0.66
makes, arrived at from the trajectory instead of from the summary times.

## 6. transfer_S1 blocking gate — the criterion is not estimable as written

`transfer_S1.md` fixes the gate: measure `kappa = (tau_erase - tau*) / (tau_swap^(1/M) - tau*)` at
`Delta_e = 0.33`, `M = 10`, `c_int = 1`; `kappa > kappa*` falsifies the `lambda = 50` starvation
certificate, with `kappa* = 1.73` on the mean basis (`W* = 95`, mean first swap 54.8) and 3.18 on the
`q05 = 30` basis. Nearest canonical grid point: `Delta_e = 0.3268`, `n = 100`.

**The first-swap figures reproduce.** Measured mean `tau_swap^(1/M) = 57.4` against the asserted 54.8
(+4.7 %); measured `q05 = 33.0` against 30.0 (+10 %). The S1 denominators are sound.

**The numerator is not measurable.** `tau_erase := tau_err(delta_P)` reads the last crossing of the
smoothed error over `p_0 + delta_P`. At the measured `p_0 = 0.024` and `W = 200`, the standard error
of the smoothed rate is 0.0108, so `delta_P = 0.005` sits **0.46 standard errors** above the base
rate. Reaching 3 standard errors would require `W >= 8433` steps, twice the whole post-drift window.
The null control settles it: run the same statistic on the 1 000 pre-drift steps, which contain no
drift at all, and it returns a mean of **791.9 — 79 % of its own horizon**, against 73 % post-drift.
The statistic reports the horizon, not the erasure.

`s6_causal.erasure_estimability` performs this control and stores it in
`results/S6_synchronized_traces/data/s6_causal.json`.

**The gate answered on estimable surrogates.** Direction is robust even though the value is not:

| erasure definition            |   mean | censored | `kappa` (mean basis) | vs `kappa* = 1.73`        |
| ----------------------------- | -----: | -------: | -------------------: | ------------------------- |
| `tau_err(delta_P)` as written | 1818.8 |      6 % |                31.70 | FALSIFIED (not estimable) |
| argmax `A_unrefl`             |  611.9 |      0 % |            **10.66** | FALSIFIED                 |
| `tau_err(rho = 0.10)`         |  557.0 |      0 % |             **9.71** | FALSIFIED                 |

`kappa > kappa*` under every definition, by a factor of 6 to 18, on 100 % of runs.

**And yet the certificate it guards holds.** At the same operating point, `lambda = 50`, 100 seeds:
`P(detect before erasure) = 0.000`, `tau_det` censored on 100 / 100 runs over the full 2 500-step
horizon, pre-drift false-alarm rate 0.000. The monitor never fires. Starvation is complete.

The two statements are not in conflict; they show that `W*` is the wrong sufficient statistic.
Starvation is governed by the **budget ceiling**, not by the window length: the `full` arm's
`max A_unrefl` is 33.5 at this magnitude and `lambda = 50` is simply out of reach, however long the
transient lasts. The certificate should be restated on `A`, which S6 measures directly, and `W*`
retired.

## 7. The three regimes, measured

`results/S6_synchronized_traces/figures/Fig_S6_synchronized.png`. Three columns, one per external
CUSUM threshold, three stacked panels on a shared time axis — `N_swap(t)` against the distinct-tree
count, the smoothed ensemble error for all four arms, and the detector statistic against its
threshold — with `tau*`, `tau_swap^(1/M)`, `tau_erase` and `tau_det` marked. `Delta_e = 0.3268`,
100 seeds, medians with IQR.

Regime labels are assigned from the measurement, not by decree. Ladder at this magnitude:

| lambda | pre-drift false alarms | `P(det <= erase)` | median `tau_det` | regime     |
| -----: | ---------------------: | ----------------: | ---------------: | ---------- |
|     50 |                   0.00 |              0.00 |         censored | starvation |
|     25 |                   0.00 |              0.97 |               97 | safe zone  |
|      8 |                   0.01 |              1.00 |               22 | safe zone  |
|      4 |                   0.60 |              1.00 |                7 | flooding   |
|      2 |                   0.98 |              1.00 |                2 | flooding   |

R2's three scenarios do not span the three regimes: `lambda = 8`, which R2's own figure labels
"SAFE ZONE", is indeed a safe zone here, and no threshold in `R2_LAMBDAS` floods. The ladder is
extended downward so the third regime can be exhibited at all. The columns of the figure show the
boundary case of each regime: 50, 8 and 4.

## 8. Protocol divergences recorded

1. **R8's stated speed-up is not reproduced.** `exp_R8_lambda_op_sweep.py` justifies dropping
   `predict_one()` by "doubling speed". Gate G0 measures the cost ratio with/without at **1.14x**,
   and gate G3 measures the full instrumentation overhead at 1.19x. The RNG-neutrality half of the
   argument is confirmed exactly (150/150 pairs identical on the swap chronology, the per-tree
   chronology, the final counters and all three generator states); the cost half is not. The
   docstring should be corrected — it is cited as a methodological justification and is contradicted
   by a committed artifact of the same repository.
2. **Weak-band `q05` depends on the warm-up.** S6 measures `q05(tau_ARF)` = 20.6 / 49.5 / 27.0 at
   `Delta_e` = 0.10 / 0.25 / 0.40 against R8's `OVERLAP_REF` of 12.95 / 48.90 / 26.95. The two strong
   anchors reproduce within 1.2 %; the weak anchor diverges by +59 %. S6 uses `T_DRIFT = 4000`, R8
   used 2000. This is consistent with R8's own thesis that weak-band swaps are noise-driven and
   therefore magnitude-independent — but they are not warm-up-independent, and R8 reports `q05` as
   if they were.
3. **`tau_err(delta_P)` is not estimable** on the canonical stream at any window shorter than the
   post-drift horizon (section 6). `def:times` should either raise `delta_P`, fix a much wider
   smoothing window, or define `tau_erase` on a threshold-free statistic.
4. **`p_0 = 0.024` measured, 0.05 assumed.** `transfer_S1`'s `theta*`, `ARL_0` and `lambda_starve`
   are all computed at `p_0 = 0.05`. Every one of them moves at the measured base rate.
5. **The `static` arm is not capacity-matched.** Retained from R3 for continuity, as instructed, but
   the bias must be read with it: at the horizon the static bagging ensemble carries **7.8 nodes and
   4.4 active leaves per tree**, against 47.9 / 24.4 for `full` and 150.8 / 75.9 for `no_swap`.
   `river.tree.HoeffdingTreeClassifier` defaults to `grace_period = 200` while the ARF's base tree
   uses 50 with `max_features = 'sqrt'`. The gap between `static` and `full` therefore mixes
   non-adaptivity with a six-fold capacity deficit and is **not a clean control**. `no_swap` is the
   clean control and every causal claim in this report rests on it, never on `static`.
6. **Background trees are structurally unobservable in this configuration** (gate G2). Both ADWINs
   are identical clones fed the same input, so they fire on the same step: the background tree is
   created and promoted inside one `learn_one` call. 100 % of replacements install a tree that has
   learned nothing — 47/47 and 36/36 in the two project configurations, against 24/28 warmed under
   River's own default pair. This is why the post-swap error does not resume from a partially
   adapted state, and it is the mechanism behind the `no_swap` forest growing to 150.8 nodes while
   `full` stays at 47.9: `full` keeps discarding its own reconstruction.
7. **Implementation defect found and corrected during this stream.** The first implementation of
   `budget_framework` applied the positive part of `def:budget` to the raw 0/1 error indicator
   instead of the smoothed rate `bar_e_t`. On a binary indicator the clip is inert — it returns
   0.945 on every error step and 0 elsewhere — so the "budget" degenerated into 0.945 x the error
   count. The definition was corrected (`s6_defs.budget_framework`), the campaign was re-run in full,
   and every other column reproduced bit-for-bit; only `a_fw` and `a_rect_fw` changed. The
   reproduction is recorded here because it doubles as a determinism check on the harness.

## 9. Falsification criteria

Section 10 of the architecture specification is not present in this repository, so criteria (a), (b)
and (c) are operationalised from the Phase-2 task list and named as such. The one falsification
criterion that IS committed — the `transfer_S1` blocking gate — is reported in section 6.

| criterion                                | operational form                                                                                           | status                                                                                                                                                                                                                                                          |
| ---------------------------------------- | ---------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| (a) F6 — first swap as adaptation metric | falsified if `tau_swap^(1/M)` tracks the erasure quantities with elasticity 1 and uniform rank correlation | **F6 upheld**: elasticity 0.66 (`z = -14.9` against 1), `tau_swap^(1)/tau_swap^(1/M) = 17.9`, rank correlation collapses to 0.06 in the weak band                                                                                                               |
| (b) F7 — rectangular transient           | falsified if `A / A_rect` is bounded and of constant sign                                                  | **F7 upheld**: ratio spans 2.70 to -14.12 and changes sign at `Delta_e >= 0.452`                                                                                                                                                                                |
| (c) Hydra as causal mechanism            | falsified if suppressing every swap after the first leaves the erasure essentially unchanged               | **Hydra falsified as the volumetric mechanism, upheld as a decision mechanism**: `share_learn = 0.993` [0.987, 0.998] — suppressing every replacement after the first leaves 99.3 % of the post-fork erasure in place, the work of incremental learning by the surviving trees. The 0.7 % residue is nonetheless real (`p = 1.6e-158`) and lifts detection at `lambda = 50` from 0/100 to 18/100 at `Delta_e = 0.327` (section 5)                                                                                                          |
| transfer_S1 gate                         | `kappa > kappa*` falsifies the `lambda = 50` starvation certificate                                        | **gate fails, certificate holds**: `kappa` = 9.7 to 31.7 against `kappa* = 1.73` on 100 % of runs, yet `P(det) = 0.000` on 100/100 runs. `W*` is the wrong sufficient statistic; the binding quantity is the budget ceiling `max A_unrefl = 33.5 < lambda = 50` |

## 10. Reproduction

```bash
PYTHONHASHSEED=0 python experiments/S6_synchronized_traces/gates/g0_predict_one_neutrality.py
PYTHONHASHSEED=0 python experiments/S6_synchronized_traces/gates/g1_deepcopy_fidelity.py
PYTHONHASHSEED=0 python experiments/S6_synchronized_traces/gates/g2_river_introspection.py
PYTHONHASHSEED=0 python experiments/S6_synchronized_traces/gates/g3_throughput.py
PYTHONHASHSEED=0 python experiments/S6_synchronized_traces/s6_runner.py smoke    #  45 s
PYTHONHASHSEED=0 python experiments/S6_synchronized_traces/s6_runner.py full     #  20 min
PYTHONHASHSEED=0 python experiments/S6_synchronized_traces/s6_predictive_power.py data
PYTHONHASHSEED=0 python experiments/S6_synchronized_traces/s6_causal.py data
PYTHONHASHSEED=0 MPLBACKEND=Agg python experiments/S6_synchronized_traces/s6_figure.py data
PYTHONHASHSEED=0 python -m pytest tests/test_S6_traces.py tests/test_S7_consistency.py -v
```

Interpreter `/home/m53/miniforge3/envs/Trading/bin/python`, `river == 0.23.0`. Each module also runs
its own assertion self-check when invoked directly (`python s6_defs.py`, `s6_detectors.py`,
`s6_writer.py`, `s6_runner.py demo`).

## 11. State

Stream S6 Phases 0, 1 and 2 complete. Open items handed forward:

1. `def:times` — `tau_erase` is not estimable as written (section 6, divergence 3).
2. `prop:invariance` — the constant is measured at 19.2 to 36.6, not the claimed [16.8, 18.1], and
   the profile is a hump, not a plateau (section 4).
3. `transfer_S1` — the starvation certificate should be restated on the budget ceiling and `W*`
   retired (section 6).
4. `ass:repair` ("no recovery without replacement") remains unverified here and is directly testable
   on the committed traces: it predicts `bar_e_t > p_0 + delta_P` on `[tau*, tau_swap^(1/M))` for
   every run.
5. The `static` arm needs a capacity-matched variant before any `static`-versus-`full` claim is
   published (section 8, divergence 5).
