# Stream S9 — decision rules, fixed before measurement

Committed before any S9 script is run and before any S9 output is read. Every rule carries its
numeric threshold and its verdict on **both** sides, so no outcome of the stream can be arbitrated
after the fact. Parts A and B below are the *quantitative prediction* the prompt orders written
first: the failure region of KSWIN is derived from `eq:Rkswin` and from River's own source, and is
therefore computable before a single trace is replayed.

Stream branch `stream-s9`, parent `346fe89`. Plan of record: `docs/plans/PLAN_S9.md`.

Scope reminder, binding on every rule below: S9 **measures**. It writes no section of
`docs/manuscript/articleA_blindspot_v64_camera_ready.tex`. Manuscript charges are delivered as
unapplied SEARCH/REPLACE blocks in `docs/theory/transfer_S9.md`; charges landing on `sec:race`,
`sec:hydra`, `sec:starvation` or `sec:decoupling` — which includes `rem:agnostic` at `.tex:306` —
are routed to `docs/manuscript/sections/framework_v2.tex` per `CLAUDE.md`.

One correction to `PROMPT_S9.md` is recorded here rather than silently absorbed. `PROMPT_S9.md:56`
places the `alpha`-price of `R_KSWIN` "under a square root of `W`". `framework_v2.tex:363-369`
contradicts that formulation explicitly — "that term carries no `W`" — and `cor:split` states the
`alpha`-price of `R_KSWIN` as "free of `W` and set by `n_stat` alone". The `.tex` is the document of
record; the failure region below is derived from `n_stat`, not from `W`.

---

## Part A — `R(KSWIN, eps, alpha)`, derived

### A.1 Four quantities, one symbol

`W` denotes four distinct quantities across the live text and the R4 code, and the confusion is
active in the published claim. The nomenclature is fixed once, here, and every later rule uses it.

| quantity | meaning | value | where |
|---|---|---|---|
| `W_transient` | `tau_erase - tau^*`, the exploitable transient; the `W` of `def:times` and of the `eps` term of `eq:Rkswin` | `57.4` | `framework_v2.tex` `def:times`, `rem:split_measured` |
| `W_win` | KSWIN sliding window | `100` | `exp_R4_main_table.py:167` |
| `W_buf` | smoothing buffer on the error stream, upstream of KSWIN | `30` | `exp_R4_main_table.py:147` |
| `n_stat` | KSWIN statistic size, the size of each of the two compared samples | `30` | `exp_R4_main_table.py:167` |

The "structural lag `W/2 = 15`" of `.tex:500`, and `KSWIN_LAG = 15` at `exp_R4_main_table.py:52`,
are `W_buf / 2`. They are **not** `W_transient / 2 = 28.7`. Any statement that reads the ProteuS
`ADD = 14` as "half the exploitable transient" is reading the wrong `W`.

### A.2 Derivation

River 0.23.0 (`river/drift/kswin.py`, `update`) draws `n_stat` points uniformly without replacement
from the first `W_win - n_stat` entries of the window (`self._rng.sample`) and compares them to the
`n_stat` most recent entries with `scipy.stats.ks_2samp`. It is a two-sample test with
`n = m = n_stat`, so the effective sample size is

```
n_eff = n m / (n + m) = n_stat / 2 .
```

The asymptotic critical distance at level `alpha` is

```
D_alpha = sqrt( -ln(alpha/2) / (2 n_eff) ) = sqrt( ln(2/alpha) / n_stat ) .
```

Converted into units of excess errors carried by the recent sample — the unit of `def:budget` — the
false-alarm price is `R_fa = n_stat * D_alpha`, that is

```
R_fa = sqrt( n_stat * ln(2/alpha) ) ,
```

which is the first term of `eq:Rkswin` exactly. Adding the shared `eps` margin
`sqrt( (W_transient/2) * ln(1/eps) )` returns `eq:Rkswin` verbatim. The derivation carries no `W` in
its `alpha` term, confirming `cor:split` against `PROMPT_S9.md:56`.

Numerical identity against the two existing implementations — `s2bis_proteus_calibration.py:344`
and `s2_arl0.py:387` — is an **identity check**, not a re-implementation: S9 calls the committed
code path and asserts equality.

### A.3 Two terms `eq:Rkswin` omits, both present in River and both measurable without simulation

1. **`alpha`-free guard.** `river/drift/kswin.py` fires only when `p_value <= alpha` **and**
   `st > 0.1`. The second conjunct is a hard floor on the KS distance that no choice of `alpha`
   relaxes: `0.1 * n_stat = 3.0` excess errors at `n_stat = 30`. `eq:Rkswin` has no such term, so
   `R_KSWIN` understates the requirement whenever `sqrt(n_stat ln(2/alpha)) < 0.1 * n_stat`, i.e.
   whenever `ln(2/alpha) < 0.01 * n_stat = 0.3` — outside the deployed range, but the guard remains
   the binding constraint on any `n_stat` large enough, and it is the term that makes the
   requirement non-monotone in `n_stat`.
2. **Discrete lattice.** `method="auto"` with `n*m = 900` selects the **exact** two-sample
   distribution, whose attainable statistics live on the lattice `k / n_stat`, `k` integer. The
   requirement is therefore a step function of `alpha`, not the smooth `sqrt(ln(2/alpha))` of
   `eq:Rkswin`. Declared before measurement, carried verbatim from `docs/plans/PLAN_S9.md` §A.3
   (scipy 1.16.2, `n_stat = 30`):

   | `alpha` | `k*` exact | `R_fa` exact | `R_fa` asymptotic | deviation |
   |---|---|---|---|---|
   | `0.05` | 11 | 11.00 | 10.52 | `+4.6 %` |
   | `0.01` | 13 | 13.00 | 12.61 | `+3.1 %` |
   | `0.005` | 14 | 14.00 | 13.41 | `+4.4 %` |
   | `0.001` | 15 | 15.00 | 15.10 | `-0.7 %` |

   `eq:Rkswin` is therefore **not a uniform bound**: anti-conservative at three of the four levels,
   conservative at the fourth. This is a pre-registered statement about the formula, not a post-hoc
   reading of a measurement; D1 re-derives the whole table mechanically.
3. **Declared gap, not repaired in S9.** KSWIN's input in the R4 protocol is a `W_buf = 30`-step
   moving average of a binary stream (`exp_R4_main_table.py:147-154`). Two consequences: massive
   ties, and a `29/30` overlap between consecutive draws. `ks_2samp`'s exact p-value is not valid
   under ties, and the i.i.d. hypothesis under which the lattice above is computed does not hold on
   the smoothed arm. This is declared as a gap, at the same rank as ADWIN's absence of a scalar test
   quantity. It is not repaired, and no verdict below is allowed to depend on the exact p-value
   being correct on the smoothed arm — which is why both input arms (raw `err`, smoothed) are
   carried separately and never merged.

---

## Part B — the failure region `F(KSWIN)`

The predicate is `def:blindspot`: a blind spot exists at `(Delta_e, W_transient)` when
`A < R(KSWIN, eps, alpha)`, with `A` given by `def:budget`,

```
A = sum_{t = tau^*+1}^{tau_erase} ( e_bar_t - p_0 - delta_P )^+ ,
```

and, in rectangular form, `A = (Delta_e - delta_P) * W_transient`. Three branches follow, each with
its analytic boundary and its quantitative prediction on the S9 grid.

### B1 — budget branch (captured by `eq:Rkswin`)

```
(Delta_e - delta_P) * W_transient  <  sqrt( n_stat * ln(2/alpha) ) + sqrt( (W_transient/2) * ln(1/eps) )
```

Increasing in `n_stat` and in `ln(1/alpha)`, free of `W_win`. Truth table pre-written over the
canonical Bernoulli grid (20 magnitudes, `BOUNDARY_SHIFTS`) x `S9_NSTAT_GRID` x `S9_KSWIN_ALPHA_GRID`.
`delta_P` is `ssot.DELTA_P = 0.005` for KSWIN (arbitrage A1: only the StrictCUSUM family reads
`CUSUM_DELTA_P`).

### B2 — dilution branch (**not** captured by `eq:Rkswin`; this is the falsification test of the formula)

When `W_transient < n_stat`, the recent sample of `n_stat` points is never composed of post-drift
observations alone: at most `j = min(W_transient, n_stat)` of its entries carry the elevated error.
The ECDF sup-distance is then bounded by a count,

```
D  <=  j / n_stat  <=  W_transient / n_stat ,
```

and, pre-registered in the magnitude-weighted form of `docs/plans/PLAN_S9.md`,

```
D_max  <=  (W_transient / n_stat) * Delta_e .
```

Whenever `D_max < k*/n_stat` at the deployed `alpha`, KSWIN **cannot** fire inside the transient,
**even where `A >= R_KSWIN`**. That region is the reviewer #3 objection put into numbers, and
`eq:Rkswin` does not predict it: the formula is free of `W` in its `alpha` term and therefore cannot
express a constraint whose whole content is `W_transient` measured against `n_stat`.

### B3 — reservoir contamination branch

The reference sample is drawn from the first `W_win - n_stat = 70` entries of the sliding window.
Once more than `70` steps of transient have elapsed, those entries are themselves post-drift, both
samples share one law, and `D` collapses. Upper horizon bound: KSWIN must draw within approximately
`W_win` steps of `tau^*` or it does not fire at all. This is the clause `rem:agnostic` (`.tex:306`)
already carries — *"immune to starvation while its reference window holds pre-drift data"* — and
never instantiates. B3 instantiates it.

### B4 — pre-registered consequence for the manuscript's `alpha` sweep

On ProteuS the label is constant `0` before `T_DRIFT` and constant `1` after:
`exp_R4_main_table.py:105` sets `regime = 1[f_t > 0.5]` with `f_t = expit(4(t - tp)/w)` monotone in
`t` and independent of `X`. Hence `Delta_e = 1.0`, `D = 1.0` is reached within `W_buf` steps, and all
four levels of `{0.001, 0.005, 0.01, 0.05}` are cleared by an order of magnitude.

**Prediction, written before reading.** The `alpha` sweep of `.tex:500` is invariant *because the
operating point never approaches `R_KSWIN`*, at a magnitude roughly `2x` the largest point of the
canonical Bernoulli grid (`Delta_e_max = 0.498`). The claimed "hyper-parameter robustness" is
**vacuous, not false**: it is a measurement taken far outside the region where any `alpha`
dependence exists.

---

## D0 — declaration of prior reading, and the verification rule it forces

The planning phase of this stream **already read** committed artifacts and manuscript numerals.
Presenting the rules below as blind arbitration would be false. Rules bearing on those numerals are
therefore **two-branch verification rules**, not blind arbitration rules.

Read before this file was written:

| source | what was read | value |
|---|---|---|
| `s2bis_proteus_gate.json :: family_requirements_at_lambda_eq.per_couple["R4 deployed lambda_ref (c=0)"]` | the two equalising levels at the Table I operating point `lambda = 15` | `equalising_alpha_KSWIN = 1.1061687e-3` against a deployed `0.005` (`4.52x` more permissive); `equalising_alpha_ADWIN = 9.041161e-2` against a deployed `delta = 0.002` (`45x` tighter) |
| idem, `family_requirements_at_lambda_eq` | the requirement at the deployed level, and the ceiling it is read against | `R_KSWIN_at_deployed_alpha = 22.679`; `measured_ceiling_median_A_unrefl = 33.5115` at `W = 57.4`, `Delta_e = 0.326793`, `eps = 0.05`, `n_stat = 30` |
| `docs/theory/S2bis_narrative_payload.md:74-75`, `transfer_S2bis.md:574` | the two measured crossings of `R_CUSUM` | `ln(1/alpha) = 16.34` (`lambda = 22.60`) against KSWIN; `18.97` (`lambda = 26.47`) against ADWIN. **Not** the `~13` of `rem:split_measured` |
| `docs/theory/transfer_S2bis.md` §2.7 (iv) | the threshold-equalised counter-example on ProteuS | PHT+ARF(`c=1`) at `lambda = 5`: `1080/1080`, `F1 = 1.0000`, `ADD = 6.05`, precision `1.000`, against `ADD = 14` for KSWIN |
| idem §2.7 (v) | the ProteuS evidence ceiling | `A` in `(8, 15]`, a cliff between `F1 = 0.9843` at `lambda = 8` and `0.0000` at `lambda = 15` |
| `framework_v2.tex` `eq:Rkswin`, `cor:split`, `.tex:306`, `.tex:500` | the requirement, the family split, the immunity clause and the immunity claim | as quoted in Parts A and B |
| `river/drift/kswin.py`, `exp_R4_main_table.py:52,101-107,144-167` | the sampling scheme, the `st > 0.1` guard, and the four `W` | as tabulated in A.1 |

**Verification rule.** Every numeral above that S9 re-uses is re-derived mechanically by an S9
script from the artifact, never carried on the strength of the prior reading.

| condition | verdict |
|---|---|
| the script reproduces the numeral at the precision printed in the artifact | **REPRODUCED**; carried forward as an input, with the script named |
| it does not | **UNREPRODUCED**; both numbers are printed side by side, the stream halts on that numeral, and no parameter is adjusted to recover it |

`UNREPRODUCED` is a terminal, publishable state. It is never absorbed into a tolerance.

---

## D1 — is `eq:Rkswin` exact against River plus scipy?

Comparison of `sqrt(n_stat ln(2/alpha))` against the exact requirement `k*(alpha, n_stat)`, where
`k*` is the smallest integer with `P(D >= k*/n_stat) <= alpha` under scipy's exact two-sample
distribution at `n = m = n_stat`, and against the `alpha`-free floor `0.1 * n_stat` of the
`st > 0.1` guard. Computed over `S9_KSWIN_ALPHA_GRID` x `S9_NSTAT_GRID`, no simulation.

Effective requirement, per cell: `R_exact = max( k*(alpha, n_stat), 0.1 * n_stat )`.

| condition | verdict |
|---|---|
| `\|sqrt(n_stat ln(2/alpha)) - R_exact\| <= 0.5` (half a lattice step) at every cell | `eq:Rkswin` **CONFIRMED** as an operational bound at the tested resolution |
| `sqrt(n_stat ln(2/alpha)) < R_exact - 0.5` at any cell | **ANTI-CONSERVATIVE**: the formula understates the requirement; the cells and the deficits are published, and the manuscript statement is qualified, not the grid |
| `sqrt(n_stat ln(2/alpha)) > R_exact + 0.5` at any cell | **CONSERVATIVE**: the formula overstates it; same publication rule |

Both verdicts can hold simultaneously over different cells; the prediction of A.3 is exactly that,
and a result of "CONFIRMED everywhere" refutes A.3. The `0.5` tolerance is declared here, before
reading, and is half the lattice spacing `1` in the `R_fa` unit at every `n_stat` — it is not
widened afterwards.

---

## D2 — budget branch B1, prediction against measurement

Per cell `(Delta_e, n_stat, alpha, input arm)`: predicted miss from B1, measured miss from the
offline replay on the committed S6 traces at `T9.1`, extended by the simulation grid at `T9.2`.
A "miss" is: no alarm in `[tau^*, tau^* + W_transient]`, `W_transient` read per run from the trace's
own `tau_erase`, never from a grid-level median.

| condition | verdict |
|---|---|
| the sign of `A - R_KSWIN` predicts the observed miss/hit on at least `90 %` of cells, with disagreements confined to the band `\|A - R_KSWIN\| <= 2` | B1 **AGREED** |
| below `90 %`, or a disagreement outside that band | B1 **REFUTED**; the disagreeing cells are published with both quantities, and neither `eps` nor `delta_P` is re-tuned to recover agreement |

`90 %` and the `2`-unit band are declared here and are not moved.

---

## D3 — dilution branch B2: is there a miss region `eq:Rkswin` does not predict?

The discriminating rule of the stream. Cells with `W_transient < n_stat` **and** `A >= R_KSWIN` —
where `eq:Rkswin` says detection is required to succeed.

| condition | verdict |
|---|---|
| such cells exist and KSWIN misses on them at a rate `> eps = 0.05` | **PREDICTED-AND-OBSERVED**: `eq:Rkswin` is incomplete, B2 is the missing term, and the charge is a new clause in `framework_v2.tex`, not an erratum |
| such cells exist and KSWIN's miss rate on them is `<= eps` | **PREDICTED-AND-ABSENT**: the derivation of B2 is **wrong**, `R(KSWIN)` as published is not falsified by it, and the result escalates to S1/S2 as a defect of this stream's theory, published as such |
| the grid produces no cell with `W_transient < n_stat` and `A >= R_KSWIN` | **NOT PRODUCED**: the grid does not reach the region; the grid extension needed is named and the stream does not claim the branch either way |

No third reading. A miss rate between `0.05` and the B1 prediction is still `PREDICTED-AND-OBSERVED`;
the magnitude of the effect is reported, the verdict is on its existence.

---

## D4 — reservoir contamination branch B3

Cells where the transient exceeds `W_win - n_stat = 70` steps. Diagnostic: the per-step KS distance
trace, and the first step at which the reservoir draw contains a post-drift entry.

| condition | verdict |
|---|---|
| the alarm rate falls monotonically once `W_transient > W_win - n_stat`, and `D` collapses toward `0` on the traces that miss | B3 **OBSERVED**; `rem:agnostic`'s subordinate clause is instantiated with its numeric boundary |
| no such degradation over the grid | B3 **ABSENT**; the contamination argument is withdrawn from the stream and is not carried into the text |

---

## D5 — at equalised `alpha`, does KSWIN keep its advantage?

Both arms reported side by side, always: **published settings** (`alpha = 0.005`, `delta = 0.002`,
`lambda = 15`) and **equalised `alpha`** (the `equalising_alpha_*` of `s2bis_proteus_gate.json` at
the same `lambda_eq`). Decision variable: detection rate and `ADD` of KSWIN against PHT+ARF(`c=1`)
over the grid, `ADD` reported raw, with the `KSWIN_LAG = W_buf/2 = 15` correction shown as a
separate column and never folded in.

| condition | verdict |
|---|---|
| at equalised `alpha`, KSWIN's detection rate is at least that of the best cumulative couple at every grid point, and its raw `ADD` is no larger | advantage **KEPT** |
| any grid point where an equalised-`alpha` cumulative couple matches or beats it | advantage **LOST**; the Table I column comparison is published as a comparison of calibrations, and the word "immune" leaves the text under D10 |

The `lambda = 5` ProteuS counter-example of §2.7 (iv) is already in hand and is `LOST` on that
stream unless S9 fails to reproduce it, which is D0's business.

---

## D6 — the ProteuS null, established on the generator

Not a conjecture: `simulate_stream` is readable. Establish on the source, then confirm on the
stream: pre-drift error identically `0`, hence `Delta_e = 1.0`, hence no false-alarm arbitrage.

| condition | verdict |
|---|---|
| `max` pre-drift error over all 1 080 streams is `0`, and `f_t < 0.5` for every `t < tp` by construction | null **DEGENERATE**; every false-alarm-budget statement measured on ProteuS is void, including the `alpha` sweep of `.tex:500` |
| any stream carries a strictly positive pre-drift error | **NOT DEGENERATE**; §2.7 (i) is UNREPRODUCED and D0's halt applies |

`DEGENERATE` is the expected outcome and is a publishable terminal state.

**Anchor correction, recorded before measurement.** `PROMPT_S9.md` and the `R4_PHT_LAMBDA` comment of
`config/experiment_ssot.py` both attack the phrase *"calibrated on ProteuS pre-drift volatility"* at
`.tex L362`. That line number is v63 and does not transfer: the phrase is **absent from the v64
body**. What v64 carries is (i) the trailing comment of `.tex:55`,
`\newcommand{\LambdaFA}{15}  % R4_PHT_LAMBDA, ProteuS pre-drift calibration`, and (ii) the footnote
of `.tex:505`, which already states the opposite — `lambda = 15` is *"the fixed ProteuS operating
threshold, applied with the monitor armed from `t=0` and no warm-up window"*, and *"the
one-false-alarm-per-warm-up calibration procedure is used for the real-world streams [...] not on
ProteuS"*. D10 therefore acts on `.tex:55` only; the body claim S2-bis refuted has already been
withdrawn, and re-charging it would be an erratum against a text that no longer says it.

---

## D7 — the same grid on a non-degenerate null

The rotation generator of S8 at `eta = 0.05` (`S8_MECH_ETA`), whose pre-drift Bayes error is `eta`
rather than `0` and whose class prior stays `50/50`. Coordinated with S8, nothing re-developed: the
generator is `experiments/S8_generality/s8_rotation.py`.

| condition | verdict |
|---|---|
| the B1/B2/B3 verdicts of D2-D4 are unchanged in sign on the `eta = 0.05` stream | the failure region **HOLDS** off the degenerate null, and is a property of the monitor, not of ProteuS |
| any verdict flips | it **FAILS** to transfer; the domain of validity is restricted to the generator on which it was measured, and that restriction is the published result |

---

## D8 — input-space degradation against `tau_erase`

The third falsification criterion of the S5 reframing, quoted: *"a detector operating on `P(X)`
suffers a degradation correlated with `tau_erase`, although it does not read `e_t`"*. Measured on
the synthetic generator, where `P(X)` is fixed by construction and the drift moves `P(Y|X)` alone.
Statistic: Spearman `rho` between the input-space detector's degradation and per-run `tau_erase`,
seed-paired, with a `10 000`-draw bootstrap CI at `S9_BOOTSTRAP_SEED`.

| condition | verdict |
|---|---|
| the `95 %` CI of `rho` contains `0` | **ABSENT** (expected): the closed-loop reframing survives its most discriminating test; the arm's structural blindness to a `P(Y|X)` drift at fixed `P(X)` is published as a design-space boundary, not as a failure |
| the CI excludes `0` | **PRESENT**: the closed-loop reframing is **FALSE** as stated. Immediate escalation, before any further S9 task, and no re-run at other settings |

Declared cost, established before implementing: the Bernoulli and rotation generators move the
decision boundary at fixed `P(X)`, so an input-space monitor is structurally blind to the drift
under study. BAF and INSECTS are excluded as terrain by S7-ter's measurement (frozen-tree error
`0.0110` equals the BAF fraud rate; `Delta_e_oracle ~ 0` on INSECTS means "nothing left to lose").
If the blindness is confirmed, `rho` is undefined rather than zero, and the rule returns
**NOT PRODUCED** with that reason named — never a silent `ABSENT`.

---

## D9 — EDDM in the family ordering

`R_EDDM` was withdrawn by S2 (rule R5, `WITHDRAWN`) and `framework_v2.tex` declares no
`R_EDDM`. S2-bis measured why the `0/1080` collapse happens: `0` pre-drift errors and `9` errors
over the whole `8 000`-step stream, so the `warm_start = 30` is never reached.

| condition | verdict |
|---|---|
| EDDM is removed from the (C4) ordering table | **WITHDRAWN**, with the arming measurement cited as the reason |
| EDDM is retained | it carries an explicit **armed / not armed** column and a stream on which it can arm; it never appears as a defeated family |

Either branch is acceptable; what is proscribed is a table row that reads as a defeat of a detector
that was never armed.

---

## D10 — what replaces the immunity claims in the text

Every occurrence of structural immunity — `.tex:500` ("structurally immune to transient signal
erasure", "hyper-parameter robust"), `.tex:306` (`rem:agnostic`), `.tex:178`, `.tex:482`, `.tex:555`,
`.tex:570`, `.tex:55` and the abstract's (`.tex:115`) "avoids the constraint on the settings we test" — is replaced by a
**measured domain of validity** carrying the three boundaries of Part B: the budget boundary B1, the
dilution boundary `W_transient >= n_stat`, and the horizon boundary `W_transient <~ W_win - n_stat`.

| condition | verdict |
|---|---|
| the three boundaries are measured, each with its grid and its verdict | the claim is replaced by its domain; charges written to `docs/theory/transfer_S9.md`, those inside the four excluded subsections routed to `framework_v2.tex` |
| any boundary returns `NOT PRODUCED` | the corresponding clause is **withdrawn** from the text rather than restated with a weaker adverb; a claim without a measured boundary does not survive in a softened form |

`.tex:306` sits inside `sec:starvation`, which `CLAUDE.md` excludes from inline patching. Its
correction goes to `framework_v2.tex` and nowhere else.

---

## Terminal states

`NOT PRODUCED`, `UNREPRODUCED`, `REFUTED`, `DEGENERATE`, `BLIND` and `LOST` are legitimate terminal
states of this stream. None is replaced by a re-run at different settings, a widened tolerance, or a
derivation presented as a measurement. `PREDICTED-AND-ABSENT` at D3 is a defect of this stream's own
theory and is published as one, not quietly dropped.

---

## Files to inspect on the next turn

Required by `PROMPT_S9.md` §"Mode opératoire".

| file | why |
|---|---|
| `docs/manuscript/sections/framework_v2.tex` | `def:times`, `def:budget`, `def:requirement`, `def:blindspot`, `eq:Rkswin`, `cor:split`, `rem:split_measured`; the destination of every D10 charge |
| `docs/manuscript/articleA_blindspot_v64_camera_ready.tex` | `:55`, `:115` (abstract), `:178`, `:306`, `:482`, `:500`, `:505`, `:555`, `:570` — the immunity surface D10 acts on; **read only**, never patched inside the four excluded subsections |
| `docs/manuscript/sections/intro_v2.tex:101-105` | the exact wording of (C4), the contribution this stream carries |
| `docs/manuscript/sections/related_work_v2.tex` | the existing ordering of monitor families, which T9.4's table must extend rather than contradict |
| `experiments/R4_proteus_evaluation/exp_R4_main_table.py` | `:52` `KSWIN_LAG`, `:101-107` the degenerate label, `:144-167` the smoothing buffer and the four `W` |
| `experiments/S6_synchronized_traces/s6_detectors.py` | the `update / drift_detected / statistic() / threshold / alarm_sense` contract; not to be rewritten |
| `experiments/S6_synchronized_traces/s6_recompute_cusum_delta001.py:128-150` | the partition-by-partition read template of the offline pass |
| `experiments/S6_synchronized_traces/s6_writer.py` | the deterministic Parquet contract every S9 artifact must satisfy |
| `experiments/S8_generality/s8_rotation.py` | the non-degenerate-null generator of D7 |
| `results/S2bis_calibration/tables/s2bis_proteus_gate.json` | every numeral of D0 |
| `docs/theory/transfer_S2bis.md` §2.7 | the threshold-equalised counter-example of D5 and the `(8, 15]` ceiling |
| `config/experiment_ssot.py` | the `S9_*` block; no S9 grid may carry a local literal |
| `tests/test_S7_consistency.py` | `test_ssot_registry_and_no_value_drift`, `test_strict_cusum_runs_at_the_cusum_tolerance`, `test_no_foreign_experiment_directory_under_results` |
