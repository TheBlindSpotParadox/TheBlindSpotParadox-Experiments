# Stream S8 — decision rules, fixed before measurement

Committed before any S8 script is run and before any S8 output is read. Every rule carries its
numeric threshold and its verdict on **both** sides, so no outcome of the stream can be arbitrated
after the fact.

Stream branch `stream-s8`, parent `a03380f`. Plan of record: `docs/plans/PLAN_S8.md`.

Scope reminder, binding on every rule below: S8 **measures**. It writes no section of
`docs/manuscript/articleA_blindspot_v64_camera_ready.tex`. Manuscript charges are delivered as
unapplied SEARCH/REPLACE blocks in `docs/theory/transfer_S8.md`; charges landing on `sec:race`,
`sec:hydra`, `sec:starvation` or `sec:decoupling` are routed to
`docs/manuscript/sections/framework_v2.tex` per `CLAUDE.md`.

---

## D0 — declaration of prior reading, and the verification rule it forces

The planning phase of this stream **already read** committed artifacts and manuscript numerals.
Presenting the rules below as blind arbitration would be false. Rules bearing on those numerals are
therefore **two-branch verification rules**, not blind arbitration rules.

Read before this file was written:

| source | what was read | value |
|---|---|---|
| `docs/theory/S6_causal_evidence.md` §5, §8 | the erasure share and the decision flip | `share_learn = 0.993` `[0.987, 0.998]`; detection at `lambda = 50` goes `0/100` (`full`) to `18/100` (`no_swap`) at `Delta_e = 0.327` |
| idem §3 | the high-magnitude sign change | `A / A_rect = -14.12` at the top of the canonical grid; median sign turns negative from `Delta_e = 0.452` |
| `docs/theory/transfer_S3.md` §4.3 | the shortfall against the `10x` reference | `9.22x` predicted against `7.99x` measured, residue `0.87`; `rho_hat in [-0.021, 0.053]` |
| `results/audit_S7/hydra_survival.csv` (via `transfer_S3.md`) | the two Hydra anchors | `4.12x` at `Delta_e = 0.14`, `7.99x` at `Delta_e = 0.33`, both on ARF(`M = 1`) |
| `.tex:234` (`rem:cf_scope`) | the arm the manuscript declares missing | *"an arm with replacement suppressed from `tau^*` onward"* |
| `config/experiment_ssot.py`, `s6_runner.py`, `_gate_common.py` | harness constants and the canonical generator | `y = 1[x0 + x1 > b]`, `b = sqrt(2) Phi^-1(0.5 + Delta_e)`, two `rng.normal()` per step |

**Verification rule.** Every numeral above that S8 re-uses is re-derived mechanically by an S8
script from the artifact, never carried on the strength of the prior reading.

| condition | verdict |
|---|---|
| the script reproduces the numeral at the precision printed in the artifact | **REPRODUCED**; carried forward as an input, with the script named |
| it does not | **UNREPRODUCED**; both numbers are printed side by side, the stream halts on that numeral, and no parameter is adjusted to recover it |

`UNREPRODUCED` is a terminal, publishable state. It is never absorbed into a tolerance.

---

## D1 — is the replacement mechanism inert?

Arms, all on one stream and one seed: `full` (nominal), `no_swap` and `frozen` (deepcopy forks at
`tau_swap^(1/M)`), `no_swap_ab_initio` and `frozen_ab_initio` (deepcopy forks at `tau^*`, i.e. the
drift instant, with both internal detector paths made inert; the second additionally stops
`learn_one`).

Budget statistic: `A := a_pos_common`, the positive-part budget of `def:budget` integrated over the
**same** window `[0, T_h)` for every arm. `a_signed_common` and `a` are reported beside it; the
verdict is read on `a_pos_common`.

Decision variable, per `(Delta_e, seed)` and aggregated as a median:

```
share_swap_all = (A_abinit - A_full) / (A_frozen_abinit - A_full)
```

with `A_abinit := A(no_swap_ab_initio)` and `A_frozen_abinit := A(frozen_ab_initio)`.

| condition | verdict |
|---|---|
| the 95 % bootstrap CI of the median `share_swap_all` is **included in `[0, 0.05]`** **and** the paired sign test on `A_abinit - A_full` does not reject at `alpha = 0.01` | replacement declared **INERT** |
| otherwise | replacement declared **NOT INERT**; the measured share and its CI are published as the number |

Bootstrap: 10 000 seed-paired resamples, `SeedSequence` seeded at `S8_BOOTSTRAP_SEED`. Runs whose
`A_frozen_abinit - A_full <= 0` are dropped and counted, never clipped into the numerator.

**INERT is a publishable terminal state and it is expensive**: it retires the Hydra clause of the
abstract, contribution (C1) of `intro_v2.tex` and the single-root-cause claim. It is escalated
before P2 is reconceived (gate P1), never absorbed.

---

## D2 — own contribution of the FIRST replacement

`full` and `no_swap` fork **after** the `learn_one` that produced the first replacement and
therefore share it. The contrast `A_abinit - A_full` measures **every** replacement; the
contribution of the **first** is `A_abinit - A_no_swap`. Both are reported, neither substitutes for
the other.

```
share_swap_first = (A_abinit - A_no_swap) / (A_frozen_abinit - A_full)
```

| condition | verdict |
|---|---|
| the 95 % bootstrap CI of the median is **strictly positive** | first-swap contribution **MEASURED**, published with its CI |
| the CI contains 0 | first-swap contribution **NOT SEPARABLE** at this sample size, declared as such; no re-run at a larger `n` to recover a sign |

The decomposition published is the exact four-term identity, anchored on the single `tau^*`-forked
reference:

```
E_total      = A_frozen_abinit - A_full          all post-tau* adaptation
E_learn_pure = A_frozen_abinit - A_abinit        learning alone, no tree ever replaced
E_swap_first = A_abinit        - A_no_swap       the first replacement, isolated
E_swap_rest  = A_no_swap       - A_full          every later replacement
E_total = E_learn_pure + E_swap_first + E_swap_rest      exactly
```

`\LearnShare = 99.3` is `E_learn / E_total` with an `E_learn` that **contains** the first swap. If
`E_swap_first` is non-negligible, the numeral is **reattributed**, not defended. The charge goes to
`framework_v2.tex`.

---

## D3 — decisional reading

Per arm, at the canonical grid point nearest `Delta_e = 0.33` (`0.3268`): the detection count at
`lambda = 50` of the external StrictCUSUM accumulated at `CUSUM_DELTA_P`, over the common window
`[0, T_h)`, `n = 100` seeds.

Published as integer counts against the two prior numerals, `0/100` (`full`) and `18/100`
(`no_swap`). A count is never converted into a rate with a normal-approximation interval at these
frequencies; Clopper-Pearson is used where an interval is given.

| condition | verdict |
|---|---|
| the S8 campaign reproduces `0/100` and `18/100` on the trunk arms | trunk **IDENTICAL**, the two new counts are read against them |
| it does not | **TRUNK BREACH** under the acceptance gate below; the stream halts on the arm contrast |

---

## D3-bis — trunk acceptance gate (blocking, read before any causal output)

The `full`, `no_swap` and `frozen` rows of `results/S8_ab_initio/data/runs.parquet` must be
**identical column by column** to the homonymous rows of
`results/S6_synchronized_traces/data/runs.parquet`, joined on `(seed, delta_e, arm)`.

| condition | verdict |
|---|---|
| every shared column identical on every shared row | trunk **PRESERVED**; the causal reading proceeds |
| any divergence | the extra `deepcopy` perturbed the trunk: **HALT**. The arm is not corrected to recover the trunk, and no causal number is read from that campaign |

---

## D4 — identity of the rotation generator

Post-drift labelling becomes `y = 1[cos(phi) x0 + sin(phi) x1 > 0]` with
`phi = pi/4 + pi Delta_e / (1 - 2 eta)`; pre-drift labelling is the canonical `1[x0 + x1 > 0]`,
unchanged and bit-identical. Declared label noise `eta` is applied to both phases.

Predicted identity: `Delta_e = (1 - 2 eta) * theta / pi`, `theta = |phi - pi/4|`.

| condition | verdict |
|---|---|
| `abs(Delta_e_measured - (1 - 2 eta) theta / pi) <= 3 SE` at **all** 20 grid points, on both `eta` arms | generator identity **HELD** |
| any point outside | identity **REFUTED**; the point and its deviation are published, and neither `phi` nor the grid is adjusted to recover it |

`SE` is the standard error over seeds of the per-run empirical `Delta_e` at that grid point.

**CONSTRAINT 1 (verbatim).** `x = rng.normal(size=(N_STEPS, 2))` is unchanged: two normal draws per
step, same order, same consumption. The label-noise draws come from a **separate** generator spawned
from `SeedSequence(safe_seed)`, never from the feature `rng`. The triple per-worker lock is
reproduced verbatim. A violation of this is an infrastructure fault, not a result.

---

## D5 — the null must not be degenerate

`eta = 0` gives a zero Bayes error and an asymptotically degenerate null. Two arms are run,
`eta in {0, 0.05}`; `e_pre` and its dispersion are reported at all 20 grid points on both.

| condition | verdict |
|---|---|
| `e_pre > 0` on both arms **and**, at `eta = 0.05`, at least one `lambda` of the ladder produces a pre-drift false-alarm rate strictly inside `(0, 1)` | the null is **NON-DEGENERATE**; the `eta = 0.05` arm carries the false-alarm budget |
| otherwise | the null is **DEGENERATE** on that arm; every false-alarm-budget statement measured on it is declared void, and the arm is reported as a comparability control only |

---

## D6 — high-magnitude switch point

Switch point `:= inf{Delta_e : median(A / A_rect) < 0}`, computed on three datasets: the canonical
family (already measured: sign turns negative from `Delta_e = 0.452`), rotation `eta = 0`, rotation
`eta = 0.05`.

**Prediction written before reading.** Under rotation, both rules are half-planes through the
origin with identical difficulty and a constant 50/50 class prior, so the majority-class predictor
can no longer beat `e_pre`. The switch must **DISAPPEAR**.

| condition | verdict |
|---|---|
| no grid point of a rotation arm has a negative median `A / A_rect` | switch **ABSENT** on that arm: the high-magnitude regime of the canonical family is a **prior artefact**, and the validity domain of the published claim is restated accordingly |
| some grid point does | switch **SURVIVES**: it is not the prior artefact. This is the stronger result — the high-magnitude limit is then a fact of adaptation, not of the generator — and it is escalated, not filed |

---

## D7 — collapse of the S5 closed-loop reframing

Internal mechanisms `D in {ADWIN, DDM, EDDM, PageHinkley, KSWIN}` inside
`ARFClassifier(drift_detector=D, warning_detector=D)`; ensemble families `SRPClassifier`,
`LeveragingBaggingClassifier`, `ADWINBaggingClassifier`, `HoeffdingAdaptiveTreeClassifier`. The
external monitor is calibrated **per pipeline** on that pipeline's own pre-drift stream
(`lambda_eq`), never shared. A common-threshold control arm (`lambda = 50` and `lambda = 25`) is
reported beside it.

Decision variable: the miss-rate curve against `A` (`a_unrefl_peak`) on a common axis.

| condition | verdict |
|---|---|
| at matched `A`, the between-mechanism spread stays inside the within-mechanism 95 % CI | curves **COLLAPSE**; the closed-loop reframing is upheld as a mechanism-independent statement |
| a non-ADWIN mechanism with comparable `tau_erase`, at `lambda_eq`, produces no comparable blind spot | closed-loop reframing **FALSE** as stated; the mechanism dependence is published as the result |

Calibration verdicts are reported in the union of the five terminal states the repository already
uses — `OK`, `SATURATED`, `NOT ATTAINABLE`, `NOT ARMED`, `NOT BINDING`. On a low-`e_pre` stream
`NOT BINDING` is an expected and informative outcome, never a failure to be re-run away.

---

## D8 — Hydra factor at equal evidence budget

The `4.12x` / `7.99x` anchors are measured on **ARF(`M = 1`)**, which the manuscript names a HAT.
The paired arm of the re-derivation stays ARF(`M = 1`); the true
`river.tree.HoeffdingAdaptiveTreeClassifier` enters D7 as a distinct family and never as a
substitute.

| condition | verdict |
|---|---|
| the per-tree pre-drift error streams and the per-tree `tau_i` are both available, and both arms calibrate to one false alarm per warm-up | the factor is published as a **decomposition** — threshold part, ensemble-size part — never as a single number |
| either measurement is missing | **`NOT PRODUCED`**, with the missing measurement named. The gap is never absorbed into a single factor |

---

## D9 — replication outside River

MOA is declared infeasible with the measurement that proves it (`java: command not found`, no MOA
jar on the host, `skmultiflow` absent and incompatible with py3.12/numpy 1.26). The fallback is
`s8_minimal_arf.py`: a minimal ARF in pure NumPy with a re-implemented ADWIN, sharing **no line**
with River. The result sought is **qualitative**: same stream, same protocol, the blind spot appears
or it does not. Bit-identity is neither aimed at nor possible.

| condition | verdict |
|---|---|
| the blind spot reproduces qualitatively | the phenomenon is **not an implementation artefact** of River |
| it does not | the phenomenon is an **implementation artefact**. The continuation decision is escalated to the user; no article-level pivot is decided unilaterally, and no parameter of either implementation is tuned to recover agreement |

---

## Terminal states

`NOT PRODUCED`, `UNREPRODUCED`, `INERT`, `REFUTED`, `DEGENERATE` and `FALSE` are legitimate terminal
states of this stream. None is replaced by a re-run at different settings, a widened tolerance, or a
proof sketch presented as a proof.
