# Stream S3 — decision rules, fixed before measurement

Committed before any S3 script is run and before any S3 output is read. Every rule below carries
its numeric threshold and its verdict on **both** sides, so that no outcome of the stream can be
arbitrated after the fact.

Stream branch `stream-s3`, parent `d7c5238` (on `stream-s2` HEAD `3f59b35`, not on the T2.0 gate
commit `a0009d4`: S2 phases 2–7 tightened `thm:floor` by `6.74x`, corrected `cor:split` and
withdrew `R_EDDM`, and all three are read-only inputs to S3).

---

## D0 — declaration of prior reading, and the verification rule it forces

The planning phase of this stream **already read** two artifacts. Concealing that and presenting
the rules below as blind arbitration would be false. The rules that bear on those numerals are
therefore written as **two-branch verification rules**, not as blind arbitration rules.

Read before this file was written:

| artifact | what was read | value |
|---|---|---|
| `results/R9_mcrit/data/exp_R9_mcrit_comparison.csv` | the `delta_e = 0.33` rows | `delta_e_eff = 0.3268`, `tau_det_star = 157.83`, `F_emp = 0.49`, `Mcrit_emp = 0` at `r = 0.95`, `E[tau_HAT] = 463` |
| `results/audit_S7/hydra_survival.csv` | the header, and the two magnitudes quoted in the manuscript | Hydra factor `4.12x [3.45, 4.96]` at `Delta_e = 0.14`, `7.99x [6.40, 9.72]` at `Delta_e = 0.33`; median ratios `5.32x` and `3.10x` |

**Verification rule (applies to every numeral above and to every published numeral S3 re-uses).**
Each is re-derived mechanically by an S3 script from the artifact, not carried on the strength of
the prior reading.

| condition | verdict |
|---|---|
| the script reproduces the numeral at the precision printed in the artifact | **REPRODUCED**; carried forward as an input, with the script named |
| it does not | **UNREPRODUCED**; both numbers are printed side by side, the stream halts on that numeral, and no parameter is adjusted to recover it |

`UNREPRODUCED` is a terminal, publishable state. It is never absorbed into a tolerance.

---

## D1 — does the shared River PRNG factorise across trees?

`experiments/S6_synchronized_traces/gates/g2_river_introspection.py` already records
`model.data[i].rng is model._rng`, `True` on all ten trees: one generator is threaded through the
whole forest. Object sharing alone neither establishes nor refutes conditional independence. What
decides is whether the **draw positions** consumed by tree `i` on the shared stream are a
deterministic set, independent of the internal state of the other trees.

Two channels, measured separately:

- the Oza/Poisson weight, drawn once per tree per instance in index order — if that were the only
  consumer, tree `i` would own exactly the residue class `{i, M+i, 2M+i, \dots}`, deterministic and
  disjoint, and disjoint deterministic index sets on an i.i.d. stream are independent;
- the `max_features='sqrt'` feature subsampling and its tie-breaks, drawn at split time — their
  *number* and *position* depend on the drawing tree's own state, and therefore displace every
  later tree's positions.

**Decision variable.** `n_shift` := the number of draw positions, among those consumed by trees
`i != j`, whose index on the shared draw sequence differs between a baseline replay and a replay of
the identical data stream in which the internal state of tree `j` alone was perturbed.
Secondary variable: `residue_ok` := whether every tree's recorded position set equals its residue
class `{i, M+i, 2M+i, \dots}` on the baseline replay.

| condition | verdict | consequence |
|---|---|---|
| `n_shift == 0` **and** `residue_ok` true | **FACTORISES** | conditional independence tenable; the Jensen/exchangeability path of T3.1 is open |
| `n_shift > 0` **or** `residue_ok` false | **DOES NOT FACTORISE** | the Jensen path **falls**; the Boole bound of T3.2 carries alone, and the Jensen bound is stated only with its hypothesis named and **measured false**, and is used in no published numeral |

No tolerance is attached. The decision variable is an integer count of index displacements on a
deterministic replay, not a statistic. One displacement is a proof of state coupling.

The gate also records whether the ensemble vote feeds back into per-tree learning; a feedback path
would couple the trees independently of the PRNG and is reported as a separate binary.

---

## D2 — which bound carries the published claim

Fixed here, before the numerical gap between the two bounds is read, and **not** by which is
tighter.

- **Jensen / exchangeability.** With `G_S(s) := P(tau_i > s | S)`, exchangeability and conditional
  independence give `P(min_i tau_i > s | S) = E_S[G_S(s)^M] >= (E_S[G_S(s)])^M`, hence
  `P(min_i tau_i <= s) <= 1 - [1 - F(s)]^M`. Requires D1 = FACTORISES.
- **Boole.** `P(min_i tau_i <= s) <= min(1, M F(s))`, valid under **any** dependence structure.

| condition | verdict |
|---|---|
| D1 = FACTORISES | **Jensen carries the claim**; Boole is printed alongside as the distribution-free envelope |
| D1 = DOES NOT FACTORISE | **Boole carries the claim alone**; Jensen appears only as a statement under a hypothesis named and measured false, and enters no published numeral |

Numerical vacancy of the carrying bound is **reported**, never used to switch carriers. A bound
that evaluates to `1` at the operating point is published as such, together with the statement of
what the bound is for (the inversion of the monotone-in-`M` bound, not the value of `P_miss`).

---

## D3 — reproduction tolerance for the RMST identity

Under a single administrative censoring at a common horizon, Kaplan–Meier reduces to the empirical
survival and `RMST(t_c) = mean(min(tau, t_c))` exactly. S7 verified the identity on 40 cells,
column `rmst_identity_dev` of `results/audit_S7/hydra_survival.csv`, worst deviation `9.1e-13`.

Tolerance, fixed now: **`1e-9`** on `|RMST_KM(t_c) - mean(min(tau, t_c))|`, three orders of
magnitude looser than the measured deviation.

| condition | verdict |
|---|---|
| every reproduced cell within `1e-9` | the S7 competing-risks framework is **re-used as is**; S3 introduces no second framework |
| any cell outside `1e-9` | **infrastructure fault**: halt, print both values, alert. No estimator is substituted and no tolerance is widened to recover the identity |

---

## D4 — agreement between the two `M_eff` estimators

No committed artifact carries per-tree `tau_i`. `M_eff` is therefore estimated by two bracketing
routes with no re-execution and no new authorized deviation:

- **(a) moments under exchangeability** — `Var(mean) = sigma^2 (1 + (M-1) rho) / M`, with the four
  order statistics `tau_swap^(q)`, `q in {0.10, 0.25, 0.50, 1.00}` per run separating the
  within-run from the between-run variance, giving `rho_hat` and `M_eff^(a) = M / (1 + (M-1) rho_hat)`;
- **(b) direct order-statistic matching** — `M_eff^(b) := argmin_m | E[tau_(1:M)] measured − E[min of m draws from F_hat] |`, which never passes through `rho`.

Declared agreement factor: **1.5**.

| condition | verdict |
|---|---|
| `max(M_eff^(a), M_eff^(b)) / min(M_eff^(a), M_eff^(b)) <= 1.5` | **AGREE**; the interval `[min, max]` is published, and the pair is cited. The mean of the two is never formed |
| ratio `> 1.5` | **DISAGREE**; both values are carried side by side as published model uncertainty, and **no single `M_eff` enters the manuscript**. The disagreement is never averaged away, and neither estimator is preferred after the fact |

A third gap is declared, not repaired, on either branch: `F_hat` is the marginal of the **HAT**
(`M = 1`), not of a tree **inside** the ARF (`max_features='sqrt'`, Poisson weighting, different
capacity). The manuscript already makes this assimilation silently at `prop:starvation_boundary`;
S3 states it as a named hypothesis.

### D4-bis — is the Hydra factor an equal-budget comparison?

S2 measured that one-false-alarm-per-warm-up calibration hands the ARF `lambda = 20.97` and the HT
`lambda = 132.50`: variance reduction by bagging buys a low threshold. The Hydra factor compares
`tau_HAT` (`M = 1`) against `tau_ARF` (`M = 10`) at a **common nominal threshold**. Part of the
measured factor may therefore be a calibration difference rather than an ensemble acceleration.

| condition | verdict |
|---|---|
| the committed artifacts supply matched pre-drift error rate and window variance for both arms, and the equal-false-alarm-budget threshold is computable from them | the Hydra factor is **re-derived at equal budget** and published as a **decomposition** — threshold part, ensemble-size part — never as a single factor |
| they do not | the gap is **DECLARED**, the sensitivity is bounded by the measured variance ratio of (a), and the missing measurement is handed to the orchestrator in `transfer_S3.md` |

Equality of budget is never assumed, and the two parts are never merged into one number.

---

## D5 — status of `cor:mcrit`

`cor:mcrit` is `void` in `docs/theory/notation_map_v63_to_v2.md` L34 and live in the manuscript of
record. The status is settled by the **validity of D1 and D2**, not by whether the resulting number
is agreeable. `M_crit = 0` is a reason neither to keep nor to withdraw.

| condition | verdict |
|---|---|
| D1 = FACTORISES (hence D2 = Jensen carries) | **(a) RECONSTRUCTION** — `cor:mcrit` is restated as a *sufficient design certificate* obtained by inverting the `<=` bound, with the distribution-free Boole envelope printed beside it, and leaves `void` in the notation map |
| D1 = DOES NOT FACTORISE (hence D2 = Boole carries alone) | **(b) WITHDRAWAL** — Boole saturates as soon as `M F(s) >= 1`, i.e. `F >= 0.10` at `M = 10`, which is everywhere the article operates; in the saturated region `min(1, M F)` does not depend on `M` and cannot be inverted. `cor:mcrit` leaves the manuscript, replaced by the measured `P_miss(M)` at the two anchors and by the Boole envelope declared saturated |

The whole `M_crit` apparatus rests on D1. Branch (b) is a verdict, not a failure of the stream, and
is preferable to a corollary surviving on a hypothesis measured false.

---

## D6 — resolution of F22 (exponentiality)

`sec:hydra` L194 states *"the `M`-fold acceleration is exact for exponential `F`"*; the *Numerical
example* reports a bootstrap KS test rejecting an exponential fit of `tau_HAT` at every magnitude
(`p < 0.05`). Which half gives is fixed here.

The KS measurement is re-verified from `results/R6_hydra_factor/data/R6_hat_instrumented.parquet`
with a local `SeedSequence` and a declared seed, `N = 2000` bootstrap replicates, Lilliefors-style
(rate fitted on each replicate).

| condition | verdict |
|---|---|
| the re-verification rejects exponentiality (`p < 0.05`) at the canonical magnitudes | **the L194 half gives**: the `M`-fold statement is a property of the exponential family and is restated as an explicitly named **calibration reference** (the multichart null), never as a property of `F` or of the ARF. The measured factor `4.1–8.0x` at `M = 10` is reported as strictly below the `10x` reference, and the shortfall is decomposed into non-exponentiality of `F` and residual dependence |
| it fails to reject at the canonical magnitudes | **the L372 half gives**: the *Numerical example* sentence is restated with the re-verified `p`-values, and the exponential reference is retained as an approximation with its measured support |

The KS result is never softened, never re-run at a different `N`, and never re-tested until
`p >= 0.05`. A failure to reproduce the direction of the published test is an `UNREPRODUCED` under
D0 and halts the stream on that numeral.

---

## D7 — model-versus-measurement tolerance for `P_miss(M)` at the anchors

Two anchors are measurable on committed artifacts: `M = 1` from `tau_HAT` (R6) and `M = 10` from
`tau_ARF` (R2, scenario A). Declared before any computation:

**The `M = 1` anchor is tautological and is declared so.** The model at `M = 1` is `F_hat(s)`, and
the measurement is the empirical fraction of the *same* sample below `s`. They coincide by
construction; the anchor is a pipeline identity check at tolerance **`1e-12`**, not a test of the
model. Presenting it as corroboration would be false.

**The `M = 10` anchor carries the actual test**, because the model is built on the R6 `tau_HAT`
sample and the measurement comes from the independent R2 `tau_ARF` sample.

| test | condition | verdict |
|---|---|---|
| bound validity (directional; this is the test that matters) | published bound `B(10) >= p_hat - w`, with `w` the half-width of the Wilson 95 % interval of the measured proportion `p_hat` | bound **HOLDS** at the anchor |
| idem | `B(10) < p_hat - w` | bound **REFUTED** by the measurement: halt, print both, publish the refutation. No `F_hat`, no `s` and no `M` is adjusted to recover it |
| model fidelity (descriptive) | `abs(model − p_hat) <= 0.05` | model **REPRODUCES** the anchor |
| idem | `abs(model − p_hat) > 0.05` | model **DEPARTS** at the anchor; the departure is published as a number and never repaired by fitting |

Right censoring is reported, never removed by `dropna`. A run whose `tau` is `NaN` at the horizon
is censored, and the censored fraction is printed with every proportion.

---

## D8 — repair or withdraw `prop:starvation_boundary`

S2 rendered R3 = `RETAIN, restricted and demoted` on Eq. (4), and `prop:certificate` — deterministic,
with no distributional hypothesis — now carries the published result: `def:decoupling` (i-bis) and
`res:tension` both route through `A_swap`. The question S3 must settle **before** repairing is what
`prop:starvation_boundary` is still for once the certificate is load-bearing. Both sides are argued
in `dependence_v2.tex` on either branch, exactly as S2 argued Eq. (4).

The criterion is fixed here, before P2, and is about **use**, not about validity — Boole is
unconditionally valid, so a validity criterion would decide nothing.

Operative grid: `Delta_e >= 0.24` (the grid on which the manuscript claims the verdict persists),
`lambda in {8, 15, 25, 50}`, `M >= 2`. `M = 1` is excluded: there the bound is `F(s)` itself, which
is the probability and not a bound on an ensemble.

| condition | verdict |
|---|---|
| D5 = (a) **or** the D2-carrying bound is `<= 0.5` at at least one operative grid point | **REPAIRED / RETAINED**: `=` becomes `<=`, the hypothesis is named in the statement, the proof becomes the Jensen argument (plus complementation under postulated independence as the special case), and the *Correlation disclaimer* is promoted from assertion to proved corollary — or replaced by the Boole envelope if D1 fell |
| D5 = (b) **and** the carrying bound exceeds `0.5` at every operative grid point | **WITHDRAWN**: the proposition leaves the manuscript, `prop:certificate` stays load-bearing, and the section keeps only the measured `P_miss(M)` anchors and the envelope declared saturated |

Threshold `0.5` is declared now and is not moved after the table is read: a bound that certifies
nothing better than "detection succeeds less than half the time" at an operating point whose
measured detection rate is below 1 % is not a usable statement, whatever its formal validity.

`NOT PRODUCED` and `WITHDRAWN` are legitimate terminal states of this stream. Neither is ever
replaced by a proof sketch presented as a proof.
