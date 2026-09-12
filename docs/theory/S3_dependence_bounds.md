# Stream S3 — the two bounds on `P_miss`, and what the measurement does to them

Deliverable 2 of stream S3, phases P1–P2. Every number below is produced by a committed script on
a committed artifact; none is typed by hand.

```bash
PYTHONHASHSEED=0 python experiments/S3_dependence/s3_gate_rng_factorization.py   # D1
PYTHONHASHSEED=0 python experiments/S3_dependence/s3_bounds.py                   # D2, D5-D8
PYTHONHASHSEED=0 python experiments/S3_dependence/s3_bounds.py --check           # self-check, writes nothing
PYTHONHASHSEED=0 python -m pytest tests/test_S3_dependence.py -v
```

Artifacts: `results/S3/rng_factorization.json`, `results/S3/bounds_grid.csv`,
`results/S3/pmiss_vs_M.csv`, `results/S3/ks_exponentiality.csv`, `results/S3/s3_verdicts.json`,
`results/S3/figures/Fig_S3_pmiss_vs_M.png`. Decision rules: `docs/prompts/s3-decision-rules.md`,
committed at `cd443f4` before any S3 script was run.

---

## 1. What the v63 statement asserts, and what is wrong with it

`prop:starvation_boundary` states

```
P_miss = P(tau_ARF < tau_det*) = 1 - [1 - F(tau_det*)]^M
```

with an **equality**, under a conditional independence of the per-tree delays that is never
demonstrated, against a **deterministic** `tau_det* := lambda / (Delta_e - delta_P)`. The
*Correlation disclaimer* asserts the direction of the error — the formula *overestimates*
`P_miss` — without proving it. Reviewer #3's objection is that *"positive pairwise correlation
alone does not generally establish the claimed independence upper bound"*.

**The objection is correct, and §3.3 gives an explicit counterexample.** The repair is not to argue
harder for positive correlation; it is to name the mechanism that actually delivers the inequality
(conditional independence given the common data stream, which is strictly stronger than positive
correlation), and to carry a second bound that needs no dependence hypothesis at all.

Three defects are settled here; the random-`tau_det` defect is settled in
`docs/theory/S3_competing_risks.md`.

---

## 2. D1 — the shared River generator does not factorise

`gates/g2_river_introspection.py` records `model.data[i].rng is model._rng`, `True` on all ten
trees: River threads one `random.Random` through the whole forest. That fact alone neither
establishes nor refutes conditional independence. Rule D1 fixes the decisive variable as the
factorisation of the **draw stream**.

Measured by `s3_gate_rng_factorization.py` on one short trajectory (300 warm-up steps, 200 probe
steps, `N_MODELS = 10`, `c_int = 1`, seed from `common.seed_pool(1)`):

| decision variable | value |
|---|---|
| `residue_ok` — every (step, tree) pair consumes exactly one draw | **false** |
| draws per (step, tree) | 1 … 16, mean **7.07**, 200 steps censused, 0 untagged |
| `n_shift` — positions consumed by trees `i != j` that move when tree `j` alone is perturbed | **9839** |
| first shifted position | 34 |
| all trees alias the forest generator | true |
| ensemble vote feeds back into per-tree learning | **absent** (`ARFClassifier._drift_detector_input` is `int(not y_true == y_pred)` on the per-tree prediction) |

Both channels are visible in that one line. `river.utils.random.poisson` is a rejection loop that
consumes `k + 1` uniforms to return a weight `k`, so the Oza channel alone already costs a random
number of draws — the residue class `{i, M+i, 2M+i, …}` is not the set tree `i` owns. On top of
that, `max_features = 1` (two features, `'sqrt'`) makes `RandomLeaf._sample_features` draw through
`rng.sample` at every leaf creation, which is why the gate traces `getrandbits` as well as
`random`: tracing `random()` alone would miss that channel entirely.

**Verdict D1: DOES NOT FACTORISE.** By D2 the Boole bound carries the claim alone; by D5 the
`cor:mcrit` branch is (b), withdrawal.

### 2.1 The recorded gap: D1's criterion is sufficient, not necessary

Written down because the rule is applied as committed and the gap is reported rather than used to
move the rule after the measurement — the same discipline S2 applied to R3's vacancy criterion.

D1 is a criterion on **positions**. A measured displacement proves that the consumed positions are
state-dependent. It does **not** by itself prove that the per-tree draw *blocks* are
probabilistically dependent: a sequential allocation by adapted stopping times preserves
independence on an idealised i.i.d. source, because the post-stopping-time stream is i.i.d. and
independent of the pre-stopping-time sigma-field, and each tree's consumption rule reads only its
own state (the gate confirms the absence of any vote feedback). Under that idealisation the blocks
would factorise despite the displacement.

Two things keep this from being a reason to overturn the verdict:

1. **Conditional independence given the stream is not a measurable property of a deterministic
   PRNG.** Condition on the data stream *and* the seed and every delay is a constant. The
   hypothesis has content only under an idealisation of the generator as an i.i.d. source, and an
   idealisation is not something a gate can certify. What a gate *can* measure is positional
   coupling, and it is present.
2. The consequence of the verdict is **conservative**: it moves the published claim onto the
   distribution-free bound. No published statement becomes wrong because of it; one becomes weaker.

Handed forward in `docs/theory/transfer_S3.md` as an open item, with the recommendation that any
stream wishing to reopen the Jensen path prove the stopping-time factorisation as a theorem about
the allocation, not measure it.

---

## 3. The two bounds

Throughout: `tau_1, …, tau_M` are the internal detection delays of the `M` trees,
`tau_ARF = min_i tau_i` by `eq:hydra`, `F` is the **marginal CDF of one tree inside the ARF**, `s`
is a deterministic level, and `S` denotes the sigma-field of the common data stream.

### 3.1 Jensen / exchangeability bound

> **Statement.** If `(tau_1, …, tau_M)` are exchangeable and **conditionally independent given
> `S`**, then for every `s`
> ```
> P(min_i tau_i <= s)  <=  1 - [1 - F(s)]^M .
> ```

**Proof.** Write `G_S(s) := P(tau_i > s | S)`, which does not depend on `i` by exchangeability.
Conditional independence gives
`P(min_i tau_i > s | S) = prod_i P(tau_i > s | S) = G_S(s)^M`. The map `x -> x^M` is convex on
`[0, 1]`, so by Jensen's inequality

```
P(min_i tau_i > s) = E[ G_S(s)^M ] >= ( E[G_S(s)] )^M = [1 - F(s)]^M ,
```

since `E[G_S(s)] = P(tau_i > s) = 1 - F(s)` by the tower property. Complementing gives the claim. ∎

This **proves the direction the *Correlation disclaimer* asserts**: the independence formula is an
upper bound on `P_miss`, not an approximation of unknown sign. The disclaimer is therefore promoted
from assertion to corollary — but only under the hypothesis just named, and D1 measures that
hypothesis's positional precondition to fail.

### 3.2 Boole bound, and the two-sided distribution-free envelope

> **Statement.** For every `s` and **any** dependence structure whatever,
> ```
> F(s)  <=  P(min_i tau_i <= s)  <=  min(1, M F(s)) .
> ```

**Proof.** With `A_i := {tau_i <= s}`, `{min_i tau_i <= s} = union_i A_i`. Sub-additivity gives
`P(union A_i) <= sum_i P(A_i) = M F(s)`, and a probability is at most `1`. Monotonicity gives
`P(union A_i) >= P(A_1) = F(s)`. ∎

Both ends are **attained** — they are the Fréchet–Hoeffding bounds on a union of equiprobable
events — so the envelope is sharp and cannot be tightened without a dependence hypothesis. This is
the two-sided bracket T3.2 asks for; in `results/S3/bounds_grid.csv` the lower end is the `F_hat`
column and the upper end is `bound_boole`.

### 3.3 Why positive correlation is not enough — an explicit counterexample

The bound of §3.1 needs `P(A_i ∩ A_j) >= F(s)^2`, i.e. **positive association of the indicators at
the level `s`**. Pearson correlation of the delays does not deliver that at every level. Take
`M = 2` and the exchangeable law on `{1, 2, 100, 200}^2`

| `(tau_1, tau_2)` | probability |
|---|---|
| `(1, 100)` | 0.3 |
| `(100, 1)` | 0.3 |
| `(2, 2)` | 0.2 |
| `(200, 200)` | 0.2 |

At `s = 2`: `F(2) = 0.5`, `P(A_1 ∩ A_2) = 0.2 < 0.25 = F(2)^2`, hence
`P(min <= 2) = 0.8 > 0.75 = 1 - [1 - F(2)]^2` — **the independence bound is violated** — while
`Corr(tau_1, tau_2) = +0.5102`. Positive correlation, exchangeability, violated bound.

Reviewer #3 is right as a matter of logic. What rescues the inequality in *this* application is not
correlation but the **common-factor structure**: the `M` trees see one data stream, and conditioning
on it is exactly the hypothesis of §3.1. The manuscript must say that, not "positively correlated".
The counterexample is asserted in `s3_bounds.demo()` and in `tests/test_S3_dependence.py`.

---

## 4. D2 — which bound carries the claim

Fixed before the numerical gap was read, and keyed to D1 rather than to tightness:

**D1 = DOES NOT FACTORISE ⇒ Boole carries the claim alone.** The Jensen bound is stated in §3.1
with its hypothesis named and its positional precondition measured to fail, and it enters **no
published numeral**. It stays in `results/S3/bounds_grid.csv` as the `bound_jensen` column, labelled
as the retired v63 model.

---

## 5. Numerical vacancy at the canonical point — and what the bounds are actually for

At the manuscript's own numerical example, `Delta_e = 0.3268`, `lambda = 50`, so
`tau_det* = 157.83` and `F_hat(tau_det*) = 0.49` on the `n = 100` R6 `tau_HAT` sample
(`E[tau_HAT] = 463.15`; all four numerals reproduce the committed
`results/R9_mcrit/data/exp_R9_mcrit_comparison.csv` under D0):

| `M` | lower Fréchet `F_hat` | **Boole** `min(1, M F_hat)` | Jensen `1-(1-F_hat)^M` | measured |
|---|---|---|---|---|
| 1 | 0.49 | 0.49 | 0.49 | 0.49 *(identity)* |
| 2 | 0.49 | 0.98 | 0.7399 | — |
| 3 | 0.49 | 1.00 | 0.8673 | — |
| 5 | 0.49 | 1.00 | 0.9655 | — |
| 10 | 0.49 | **1.00** | 0.9988 | **1.00** `[0.963, 1.000]` |
| 20 | 0.49 | 1.00 | 1.0000 | — |
| 50 | 0.49 | 1.00 | 1.0000 | — |

At `M = 10` both bounds say *"`P_miss` is at most 100 %"*. A reviewer computes those two numbers in
thirty seconds. **Neither bound is published without the statement of what it is for.**

What the bounds buy is not the value of `P_miss` but the **inversion**
`M_crit = floor(ln r / ln[1 - F])`, which returns `0` at `r = 0.95` — no ensemble size, not even
`M = 1`, meets the target. And the inversion exists only for the Jensen form: **Boole saturates**
as soon as `M F(s) >= 1`, and in the saturated region `min(1, M F)` does not depend on `M` at all.
At `M = 10` saturation begins at `F >= 0.10`; at the canonical point, `F_hat = 0.49` saturates from
`M = 3` upward (`lambda = 25`: from `M = 4`; `lambda = 15`: from `M = 15`; `lambda = 8`: never,
because `F_hat = 0.00` there).

**The whole `M_crit` apparatus therefore rests on D1, and D1 failed.** That is the content of D5
branch (b): `cor:mcrit` is withdrawn, not because its number is unpalatable but because the
inversion it performs is unavailable on the bound that survives.

---

## 6. D7 grid — the plug-in `F = F_HAT` is refuted by the measurement

Both bounds are statements about the marginal `F` of a tree **inside** the ARF. **No committed
artifact carries that marginal.** The manuscript silently substitutes `F_HAT`, the law of a
standalone HAT at `M = 1` (`prop:starvation_boundary`, *"empirically estimated from the HAT
configuration"*). S3 does not merely declare the substitution as a hypothesis: at `M = 10` the
substitution is **testable**, because R2 scenario A measures `P(tau_ARF <= s)` directly on the same
seeds and the same twenty magnitudes.

Rule D7's directional test, applied to all 80 testable cells (20 magnitudes × 4 thresholds, `M = 10`,
`n = 100` each), with `w` the Wilson 95 % lower end of the measured proportion:

**10 of 80 cells refute the Boole plug-in, 11 refute the Jensen plug-in.**

| `Delta_e` | `lambda` | `tau_det*` | `F_hat` | Boole bound | measured | Wilson lo | `min tau_HAT` | `min tau_ARF` |
|---|---|---|---|---|---|---|---|---|
| 0.1409 | 25 | 190.91 | 0.02 | 0.20 | 0.29 | 0.2101 | 4 | 5 |
| 0.2426 | 8 | 34.40 | 0.00 | 0.00 | 0.02 | 0.0055 | 46 | 5 |
| 0.2871 | 8 | 28.87 | 0.00 | 0.00 | 0.02 | 0.0055 | 42 | 25 |
| 0.3268 | 8 | 25.25 | 0.00 | 0.00 | 0.04 | 0.0157 | 33 | 24 |
| 0.3614 | 8 | 22.76 | 0.00 | 0.00 | 0.01 | 0.0018 | 33 | 20 |
| 0.4157 | 8 | 19.72 | 0.00 | 0.00 | 0.01 | 0.0018 | 20 | 17 |
| 0.4360 | 8 | 18.78 | 0.00 | 0.00 | 0.01 | 0.0018 | 20 | 17 |
| 0.4523 | 8 | 18.09 | 0.00 | 0.00 | 0.02 | 0.0055 | 20 | 17 |
| 0.4650 | 8 | 17.58 | 0.00 | 0.00 | 0.01 | 0.0018 | 20 | 17 |
| 0.4749 | 8 | 17.21 | 0.00 | 0.00 | 0.01 | 0.0018 | 20 | 17 |

**The refutation is of the substitution, not of either inequality.** Boole is unconditionally valid
for the true member marginal; what the measurement shows is that `F_HAT` is not that marginal. The
mechanism is visible in the last two columns: the ARF member's **left tail is strictly faster than
any HAT run**. At `Delta_e = 0.3268` the fastest of 100 HAT runs adapts at step 33, while 4 of 100
ARF runs have already adapted by step 25.25 — so `F_HAT(25.25) = 0` exactly, while the ARF's own
`F` is at least 0.04 there. The plug-in is **anti-conservative** in precisely the low-`lambda`
corner where the bound was the only thing that could have been informative.

Per D7 no `F_hat`, no `s` and no `M` is adjusted to recover the bound. The consequence for the
manuscript is stated in `docs/manuscript/sections/dependence_v2.tex`: the proposition is published
in terms of the member marginal `F`, and the numerical instantiation through `F_HAT` is retracted.

At the canonical point (`Delta_e = 0.3268`, `lambda = 50`) the bound **holds**: `1.00 >= 0.963`, and
the retired v63 model reproduces the measurement to `0.0012`. The refutation lives elsewhere on the
grid, which is why the canonical point alone was never a sufficient test.

`tests/test_S3_dependence.py` asserts the census exactly (10 and 11), so a later change that
silently repairs the refutation fails the suite instead of passing it.

---

## 7. D8 — `prop:starvation_boundary` is repaired, not withdrawn

D8's criterion, committed before P2: retained iff D5 = (a), **or** the D2-carrying bound is `<= 0.5`
at at least one point of the operative grid (`Delta_e >= 0.24`, `lambda in {8, 15, 25, 50}`,
`M >= 2`; 384 points). D5 is (b), so the second clause decides.

**Verdict: REPAIRED / RETAINED.** 132 of the 384 operative points have `Boole <= 0.5` (140 for
Jensen); the minimum is `0.00`. The restricted reading — the same computation with every
`(Delta_e, lambda)` pair refuted in §6 removed — returns **RETAINED as well**, at
`(Delta_e = 0.4823, lambda = 8, M = 2)` where the bound is `0.00` and the measured `P_miss` is
`0.00`, so the verdict does not hang on the refuted corner.

**Recorded gap.** The criterion as written fires on cells where the plug-in is refuted; it was
committed on the plug-in evaluation and is applied as committed, with the restricted reading printed
beside it rather than substituted for it. Both readings are in
`results/S3/s3_verdicts.json::D8`.

The retained proposition is not the v63 one. It is the distribution-free envelope of §3.2, stated
on the member marginal `F`, with `=` replaced by `<=`, with the hypothesis of the Jensen form named
where it appears, and with `tau_det*` gone (`docs/theory/S3_competing_risks.md`).

**The case for withdrawal, argued rather than dismissed.** S2 rendered R3 = `RETAIN, restricted and
demoted` on Eq. (4), and `prop:certificate` — deterministic, hypothesis-free — now carries the
published result; `def:decoupling` (i-bis) and `res:tension` both route through `A_swap`. Keeping
`prop:starvation_boundary` costs a proposition whose two bounds are numerically vacant at the
operating point and whose only publishable use, the inversion in `M_crit`, is gone with D5(b).
Withdrawing it costs the only statement that ties ensemble size to miss probability — the only
formal support for the Hydra effect — at a moment when S6 has already established that replacements
account for 0.7 % of the erasure. The criterion decided for retention; the surviving statement is
weaker than the v63 one and is published as such.

---

## 8. D6 — the F22 contradiction, re-verified

`sec:hydra` grounds the acceleration on *"the `M`-fold acceleration is exact for exponential `F`"*;
the *Numerical example* reports a bootstrap KS test rejecting an exponential fit of `tau_HAT` at
every magnitude. Re-verified here rather than carried on the manuscript's word, Lilliefors-style
(rate refitted on every replicate), `N = 2000`, generator
`np.random.SeedSequence(ssot.SEED_SCHEME_SEEDSEQ_ENTROPY).spawn(20)`:

**20 of 20 magnitudes reject exponentiality, largest `p` = 0.0030**
(`results/S3/ks_exponentiality.csv`). The published measurement **REPRODUCES**.

Verdict D6, fixed in advance: **the L194 half gives.** The `M`-fold statement is a property of the
exponential family and is restated as an explicitly named calibration reference, never as a
property of `F` or of the ARF. The resolution is written in
`docs/manuscript/sections/dependence_v2.tex`; nothing is anchored in `sec:hydra`, which
`CLAUDE.md` excludes from the S3 write perimeter.

---

## 9. Statutory guard-rail — degenerate inputs

`tests/test_S3_dependence.py` and `s3_bounds.demo()`. Each row states why the opposite expectation
would pass on a wrong premise.

| input | expected | why the opposite would pass on a wrong reading |
|---|---|---|
| `F = 0` | both bounds `0` at every `M`; `M_crit = inf` | `M_crit = 0` here would read `ln(1-F) = 0` as a division that "fails safe"; it is the case where no ensemble is too large |
| `F = 1` | both bounds `1`; `M_crit = 0` | a single tree already starves the monitor; a finite positive `M_crit` would certify an ensemble that cannot work |
| `M = 1` | Boole and Jensen **coincide** and both equal `F` | they are not two bounds at `M = 1`; a test showing one strictly tighter there is testing a bug |
| `M >= 2`, `F` small | Boole `>=` Jensen | Boole is the looser of the two off the saturated region; an inversion of that order means the union bound was mis-signed |
| `M F >= 1` | Boole is **constant in `M`** | this is why the inversion is unavailable under D2; a `M_crit` computed from Boole in that region would be reading noise |
| exchangeable, `Corr = +0.51`, §3.3 | Jensen bound **violated** | asserts reviewer #3's objection as arithmetic, so a future "positive correlation suffices" edit fails the suite |
| `s >= t_c` | `F_hat` **raises** | a censored run is not orderable against a level beyond the horizon; returning a number there would silently bias `F` downward |
| censored run, `s < t_c` | counted in the **denominator** | dropping it (R9's convention) inflates `F`; at the canonical magnitude nothing is censored, so the published numeral is unaffected either way |
| `k = 0` or `k = n` | Wilson interval touches `0` / `1` | a Wald interval degenerates to a point there and would declare a refutation that is a sampling artifact |

---

## 10. What this document does not cover

- **The member marginal `F` is never measured.** §6 refutes the `F_HAT` plug-in but produces no
  replacement: no committed artifact records a per-tree `tau_i` inside the ARF. The nearest
  observable is the order-statistic set of `runs.parquet`, used in
  `docs/theory/S3_competing_risks.md` §4.
- **The Jensen bound is proved but not used.** Its hypothesis is named and its positional
  precondition measured to fail; §2.1 records why the failure is a conservative reading rather than
  a theorem.
- **`s` is deterministic here.** Replacing it by the random `tau_det` is P3's object, not this
  document's; both bounds are stated at a fixed level and are not claimed at a stopping time.
- **`eps` and the reliability targets are design choices.** `R9_RELIABILITY_TARGETS = [0.99, 0.95,
  0.50]` is read from the registry; `r = 1 - P_miss` throughout and the letter `beta` is not used.
