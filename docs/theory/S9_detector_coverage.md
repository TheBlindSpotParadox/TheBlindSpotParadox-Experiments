# Stream S9 — detector coverage, the KSWIN failure region, the input-space arm

Branch `stream-s9`, parent `346fe89`. Decision rules D0–D10 fixed before any measurement in
[`docs/prompts/s9-decision-rules.md`](../prompts/s9-decision-rules.md) (`581b232`), committed before
the first line of computation was executed. Plan of record: `docs/plans/PLAN_S9.md`. Transfer
payloads: [`transfer_S9.md`](transfer_S9.md).

Scope: S9 **measures**. It writes no section of the manuscript. Every charge is delivered unapplied
in `transfer_S9.md`, and charges landing inside `sec:race`, `sec:hydra`, `sec:starvation` or
`sec:decoupling` — which includes `rem:agnostic` at `.tex:306` — are routed to
`docs/manuscript/sections/framework_v2.tex` per `CLAUDE.md`.

## What the stream was asked to settle, and what it returned

Reviewer #3 refuses the scope of `.tex:500`: KSWIN is called *"structurally immune to transient
signal erasure"* and *"hyper-parameter robust"* on the strength of an `alpha` sweep on ProteuS. The
prompt ordered the failure region derived and committed **before** measurement. It was. The
measurement then refuted three of this stream's own predictions and confirmed the fourth, and it
refuted the manuscript's claim by a wider margin than the pre-registration anticipated.

| rule | verdict | one line |
|---|---|---|
| D0 | **REPRODUCED**, with one reattribution | every numeral re-derived; `W = 57.4` is **not** the `W` of `def:times` |
| D1 | **CONFIRMED** ×3, **ANTI-CONSERVATIVE** at `alpha = 0.005` | the deployed level is the one `eq:Rkswin` understates |
| D2 | **REFUTED** on two independent corpora | `0.863` and `0.850` against a declared `0.90` |
| D3 | **PREDICTED-AND-ABSENT** | B2's derivation is wrong; escalates to S1/S2 |
| D4 | **ABSENT** | B3 withdrawn, not carried into the text |
| D5 | **LOST** | equalising `alpha` moves KSWIN down and ADWIN up |
| D6 | **DEGENERATE** | proved on the generator, not conjectured |
| D7 | **HOLDS** | every verdict transfers to a binding-false-alarm null — except EDDM's rank |
| D8 | **NOT PRODUCED** | structural blindness, on a validated instrument |
| D9 | **ARMED-COLUMN** | with the arming instant beside the delay |
| D10 | domain of validity, §10 | three boundaries, two measured, one withdrawn |

---

## 0. D0 — the numerals, and the symbol that carries two quantities

Every numeral the planning phase read was re-derived mechanically. All reproduce. One reproduces
**and is mislabelled**, which is the finding.

`s2bis_proteus_gate.json :: R_KSWIN_at_deployed_alpha = 22.679` is reproduced to `1e-12` from its
stated inputs by `tests/test_S9_coverage.py::test_eq_Rkswin_reproduces_the_committed_requirement_numeral`,
against the same expression `s2_arl0.py:387` and `s2bis_proteus_calibration.py:344` evaluate. The
`epsilon_margin = 9.27240617375013` likewise.

The input labelled `W = 57.4` is **`tau_swap^(1/M)`**, the mean first-swap time — not
`W := tau_erase - tau*` of `def:times`, which is what `eq:Rkswin`'s `eps` term is defined over.
Measured on the committed S6 corpus at the canonical operating point `Delta_e = 0.326793`, arm
`full`, `n = 100`:

| quantity | value |
|---|---|
| `tau_swap^(1/M)`, mean | **57.38** — this is the published `57.4` |
| `W = tau_erase - tau*` of `def:times`, median (`w_fw`) | **1 995.5** (94/100 finite) |
| measured ceiling, median `max_t A_unrefl` | 33.5115 |
| `R_KSWIN` at the published `W = 57.4` | **22.679** — ceiling **meets** it |
| `R_KSWIN` at `def:times`' own `W` | **68.079** — ceiling **fails** it |

The requirement and the verdict at the operating point both flip. `prop3_v2.tex:41` and
`S6_causal_evidence.md:199` both name `57.4` as `tau_swap^(1/M)`; `framework_v2.tex`
`rem:split_measured` reads it as `W`. This is a **fifth** quantity carrying the symbol `W`, beyond
the four the gate's §A.1 tabulated, and it is the one every published requirement numeral is
evaluated at. Charge **S9-A**.

## 1. D1 — `eq:Rkswin` against the exact lattice

`river/drift/kswin.py` calls `scipy.stats.ks_2samp(..., method="auto")` at `n = m = n_stat`, so the
attainable statistics live on the lattice `k / n_stat` and the requirement is a step function of
`alpha`, not the smooth `sqrt(n_stat ln(2/alpha))`. Computed over `S9_NSTAT_GRID x
S9_KSWIN_ALPHA_GRID`, no simulation; the `n_stat = 30` row reproduces the table pre-registered in
§A.3 exactly.

| `alpha` | `k*` exact | `R_fa` asymptotic | deviation | verdict at the declared `0.5` tolerance |
|---|---|---|---|---|
| 0.001 | 15 | 15.101 | `-0.67 %` | CONFIRMED |
| **0.005** | **14** | **13.407** | **`+4.42 %`** | **ANTI-CONSERVATIVE** |
| 0.01 | 13 | 12.608 | `+3.11 %` | CONFIRMED |
| 0.05 | 11 | 10.520 | `+4.56 %` | CONFIRMED |

The one level at which the formula understates the requirement by more than half a lattice step is
`alpha = 0.005`, the level R4 deploys. The `st > 0.1` guard is slack at all 16 cells, which is the
precondition the offline alarm derivation depends on and is asserted rather than assumed
(`test_the_st_guard_is_slack_at_every_declared_cell`).

## 2. D2 — the budget model, refuted on two corpora

D2 declared, before reading: agreement on at least `90 %` of cells, with every disagreement inside
`|A - R| <= 2`.

| corpus | cells | agreement | disagreements outside the 2-unit band |
|---|---|---|---|
| canonical Bernoulli (T9.1), `W` from `def:times` | 80 | **0.863** | 11/11, `|A - R|` in `[27.8, 42.1]` |
| canonical Bernoulli, `W = 57.4` as published | 80 | **0.800** | 14/16 |
| controlled transient (T9.2), raw arm | 3 840 | **0.850** | — |

**REFUTED** under both readings of `W` and on both corpora. The direction is the content: B1
predicts a miss on every cell of the canonical corpus, and KSWIN detects 85–100 % of runs at the top
of the magnitude grid, where the budget `A_fw` is *smallest* (`24.0` at `Delta_e = 0.14` falling to
`1.2` at `0.498`, while detection rises from `0.00` to `1.00`). A monitor that detects more as its
evidence budget shrinks is not spending that budget. No parameter was re-tuned to recover agreement;
the rule forbids it and the refutation is the result.

## 3. D3 — the dilution branch, and this stream's own error

T9.2 drives the error stream directly — a rectangular transient of declared height and duration on a
Bernoulli(`p_0 = 0.024`) background, no classifier in the loop, `A = (Delta_e - delta_P) W` exact by
construction. 20 magnitudes × 12 transients × 4 `n_stat` × 100 seeds × 2 input arms = **192 000
runs**. The magnitude axis runs to `Delta_e = 1.0` because the B2 region is **empty below
`Delta_e = 0.457`** at every cell of the declared grid, so a grid stopping at the canonical `0.498`
would have returned `NOT PRODUCED` by construction; `Delta_e = 1.0` is the ProteuS operating point,
not an extrapolation. `test_t92_grid_reaches_the_region_D3_is_decided_on` enforces that.

**Result: 93 cells in the B2 region, 0 missed above `eps`, mean detection rate 0.9998.**

Verdict **PREDICTED-AND-ABSENT**. B2's derivation is wrong, and the reason is that its two
boundaries coincide rather than cross: wherever `W < n_stat` **and** `A >= R_KSWIN`, the magnitude
required to satisfy the second condition is already large enough that
`min(W, n_stat) * Delta_e >= k*`, so the dilution ceiling never binds where `eq:Rkswin` demands
detection. Per the committed rule this is a defect of **this stream's theory**, published as one and
escalated to S1/S2. It is not dropped, and `R(KSWIN)` is not falsified by it.

## 4. D4 — the contamination branch, withdrawn

B3 predicted the alarm rate would fall once the transient exceeds `W_win - n_stat`, the point past
which the reference reservoir is itself post-drift. Measured at `alpha = 0.005`, raw arm, detection
rate against `W` at fixed `(Delta_e, n_stat)`: the rate **rises and then plateaus**. It does not
fall. The two candidate declines found over the whole grid — `0.95 -> 0.89` at `n_stat = 30,
Delta_e = 0.50` and `0.95 -> 0.90` at `n_stat = 50, Delta_e = 0.45` — are inside two standard errors
at `n = 100` and are not monotone.

**ABSENT.** The mechanism is visible in the same table: a long transient gives KSWIN many test
opportunities *early*, while the reservoir still holds pre-drift data, so the alarm fires before
contamination can bind. `rem:agnostic`'s subordinate clause — *"while its reference window holds
pre-drift data"* — is therefore **not a binding constraint on detection**, and the contamination
argument is withdrawn from the stream rather than carried into the text.

## 5. What does govern KSWIN — the contrast requirement

The model that survives is the one B2 was a special case of, stated without the budget:

```
detection  <=>  min(W, n_stat) * Delta_e  >=  k*(alpha, n_stat)
```

Only the part of the transient that fits inside the statistic window is spendable. `eq:Rkswin`
charges the whole integrated budget `A`; the monitor can only ever see `min(W, n_stat)` steps of it.

| scope (raw arm) | cells | B1 agreement | contrast agreement |
|---|---|---|---|
| whole grid | 3 840 | 0.850 | **0.931** |
| `W < n_stat` | 1 280 | **0.954** | 0.932 |
| `W >= n_stat` | 2 560 | 0.798 | **0.931** |
| `W > W_win - n_stat` | 880 | 0.730 | **0.932** |

B1's agreement collapses exactly where it integrates a transient longer than the window that reads
it. The contrast model is stable across every regime. Its boundary is quantitatively right: at
`n_stat = 30, alpha = 0.005, k* = 14` it places the transition at `W ~ 20` for `Delta_e = 0.70`
(measured `0.53` at `W = 20`, `0.95` at `W = 25`) and at `W ~ 14` for `Delta_e = 1.0` (measured
`0.86` at `W = 15`, `1.00` at `W = 20`), and it predicts no detection at all at `Delta_e = 0.30`
for any `W`, where the measured rate never exceeds `0.37`. Charge **S9-F**.

## 6. D5 — at equalised `alpha`, the advantage is lost

Canonical family, arm `full`, 20 magnitudes × 100 seeds, raw error stream. Equalising levels read
from `s2bis_proteus_gate.json`, couple `R4 deployed lambda_ref (c=0)`, `lambda_eq = 15`: ADWIN
`delta` `45.2x` looser, KSWIN `alpha` `4.52x` tighter than deployed.

| family | exposure | setting | pre-drift FA | detect within `W` | ADD |
|---|---|---|---|---|---|
| StrictCUSUM `lambda = 15` | cumulative | published | 0.000 | 0.928 | 35.0 |
| StrictCUSUM `lambda = 50` | cumulative | published | 0.000 | **0.001** | 1089.0 |
| PHT `lambda = 15` | cumulative | published | 0.000 | 0.928 | 33.5 |
| PHT `lambda = 50` | cumulative | published | 0.000 | **0.000** | — |
| EDDM (armed) | cumulative | published | 0.020 | 0.974 | 17.5 |
| ADWIN | windowed | published | 0.000 | 0.885 | 28.0 |
| ADWIN | windowed | **equalised** | 0.000 | **0.926** | **15.0** |
| KSWIN | windowed | published | 0.000 | **0.458** | 27.0 |
| KSWIN | windowed | **equalised** | 0.000 | **0.337** | 28.0 |

**LOST.** KSWIN is last at both settings, and equalisation moves it *down* (`0.458 -> 0.337`) while
moving ADWIN *up* (`0.885 -> 0.926`, ADD `28 -> 15`) — both at zero pre-drift false alarms. The
Table I comparison orders calibrations: read at a common level, the monitor the manuscript calls a
resolution is the weakest of the five on this family. The `lambda = 50` rows reproduce the published
starvation certificate exactly.

**The `alpha` sweep is not invariant off ProteuS.** At the canonical operating point
`Delta_e = 0.327`, detection within `W` runs `0.03 / 0.15 / 0.69` across
`alpha in {0.001, 0.005, 0.05}` — a factor **23** over the range `.tex:500` calls uniform. Prediction
B4 held: the ProteuS invariance is an artefact of an operating point that never approaches
`R_KSWIN`.

**The deployed smoothing convention floods.** On the `W_buf = 30` moving average of the error stream
— the input `run_concept_drift_kswin` actually feeds KSWIN — the pre-drift false-alarm rate is
**1.000 at every `alpha`**, on the canonical family (T9.1) and independently at **0.9996** on the
synthetic controlled stream (T9.2), against **0.000** on the raw error stream. Confirmed against a
live re-armed `drift.KSWIN`: 8–9 alarms per 1 000-step pre-drift window, the first at `t ~ 99`. This
is the `ks_2samp`-under-ties gap declared in §A.3 item 3 of the gate, now measured, and it is the
mechanism by which the ProteuS result fails to transfer: there the pre-drift error is identically
zero, the buffer is constant, and `D = 0`.

## 7. D7 — the same grid on a non-degenerate null

ProteuS has no false-alarm arbitrage at all (§8) and the canonical Bernoulli family has
`p_0 = 0.024`, low enough that every family below prices its threshold at zero measured cost. The
S8 rotation generator at `eta = 0.05` has a Bayes error of `eta`, a 50/50 class prior at every
magnitude and a measured `e_pre` of **0.069** (min 0.048) — a null on which a false-alarm budget
actually binds. S8's trace corpus is gitignored and absent everywhere, so the `eta = 0.05` arm was
re-simulated into S9's own tree and checked against S8's committed `runs.parquet`: **trunk identity
PRESERVED**, 2 000 records, every shared column of every shared row.

The same matrix, same detectors, same equalising levels, arm `full`, 20 magnitudes × 100 seeds:

| family | setting | pre-drift FA | detect within `W` | ADD | canonical-family comparison |
|---|---|---|---|---|---|
| StrictCUSUM `lambda = 15` | published | 0.000 | 0.958 | 31.5 | 0.928 |
| StrictCUSUM `lambda = 50` | published | 0.000 | 0.448 | 440.0 | 0.001 |
| PHT `lambda = 15` | published | **0.030** | 0.942 | 28.0 | 0.928 at FA 0.000 |
| ADWIN | published | 0.000 | 0.891 | 32.0 | 0.885 |
| ADWIN | equalised | 0.000 | **0.933** | 18.5 | 0.926 |
| KSWIN | published | 0.000 | **0.572** | 27.2 | 0.458 |
| KSWIN | equalised | 0.000 | **0.478** | 28.8 | 0.337 |
| EDDM (armed at `t_rel = -554`) | published | **0.930** | **0.022** | 40.0 | 0.020 / 0.974 |

**HOLDS**, on every verdict D7 names:

- D2's sign is unchanged. B1's agreement against the measurement is **0.850** at the published
  `alpha` (0.863 on the canonical family), still under the declared `0.90`; at the equalised
  `alpha` both models reach 1.000 on this grid.
- D3 stays undecidable on any classifier-driven stream: `w_fw` has a median of **2 306** and
  **zero** cells with `W < n_stat`, exactly as on the S6 corpus. This is the second independent
  confirmation that only the controlled-transient grid of T9.2 can decide the dilution branch.
- The KSWIN ordering is unchanged: last among the windowed and cumulative families at both settings,
  and equalising `alpha` moves it **down** (`0.572 -> 0.478`) while moving ADWIN **up**
  (`0.891 -> 0.933`). D5's verdict transfers.
- The smoothed-arm flood transfers: pre-drift false-alarm rate **1.000** at every `alpha` on this
  stream too — a third independent stream after T9.1 and T9.2.
- The false-alarm budget now binds and the calibration rule survives it: PHT at `lambda = 15` pays
  a measured `0.030` pre-drift false-alarm rate and still detects `0.942`, and ADWIN at the
  equalised `delta` pays `0.780` on the smoothed arm. On ProteuS none of these costs is observable
  at all.

**One row does not transfer, and it is EDDM.** On the canonical family EDDM is the best detector in
the table (`0.974` detection at `0.020` false alarms). On the non-degenerate null it collapses to
**`0.022` detection at `0.930` false alarms** — and not through a warm-up artefact: it arms at a
median `t_rel = -554`, well before `tau*`. Its canonical-family standing was a property of a stream
with so few errors that its inter-error-distance ratio stayed quiet, not a property of the detector.
A family whose rank inverts between two streams cannot carry a fixed row in an ordering table, which
is what D9's arming column exists to prevent being hidden.

## 8. D6 — the ProteuS null is degenerate, established on the generator

Not a conjecture. `simulate_stream` builds the target as `regime = 1[f_t > 0.5]` with
`f_t = expit(4(t - tp)/w)`, which is `< 0.5` for every `t < tp`, so the pre-drift label is
identically `0`; with `run_concept_drift`'s `y_pred = predict_one(x) or 0` predicting that constant
from the first step, the pre-drift error is exactly zero. Verified mechanically on all 24
(transition, regime) combinations by
`tests/test_S9_coverage.py::test_proteus_pre_drift_label_is_constant_zero_by_construction`, and
consistent with S2-bis's measurement of `max = 0` over 1 080 streams.

**DEGENERATE.** Every false-alarm-budget statement measured on ProteuS is void, including the
`alpha` sweep of `.tex:500`. Note the anchor correction recorded in the gate: the phrase
*"calibrated on ProteuS pre-drift volatility"* that `PROMPT_S9.md` attacks at `.tex L362` is **absent
from the v64 body** — that line number is v63. What v64 carries is the trailing comment of
`.tex:55` and a footnote at `.tex:505` that already states the opposite. D10 acts on `.tex:55` only.

## 9. D8 — the input-space arm returns a design-space boundary

`s8_rotation.make_rotation_stream` draws `x = rng.normal(size=(N_STEPS, 2))` **once per seed**, with
no dependence on `t`, on `Delta_e` or on `eta`; only the labelling half-plane turns. `P(X)` is
therefore invariant by construction, and an input-space monitor is structurally blind to the drift
under study.

Three measurements, in the order that makes the null interpretable:

1. **The instrument, first.** HDDDM (Ditzler & Polikar 2011, NumPy only) on streams whose `P(X)`
   does move — a mean shift on both features from `tau*`. Detection rate `0.35 / 0.55 / 1.00` at
   `0.25 / 0.5 / 1.0` sigma. **SENSITIVE** at the gate rung. The threshold coefficient is
   **calibrated, not chosen**: at the `gamma = 1` first declared, `beta` sits near the 84th
   percentile of `|eps|` and fires on `2.8` of 40 stationary batches per run; each firing resets the
   reference and blinds the detector for `MIN_HISTORY + 1` batches, and the control came out
   **non-monotone in the shift** (`1.00 / 0.90 / 0.60`) because a large shift landing in a blind
   window is missed outright. `gamma = 3` gives `0.60` false alarms per run — the
   one-per-warm-up convention of `S8_PHT_TARGET_FA` — and a monotone control. The whole sweep is
   published in `s9_input_space.json :: gamma_calibration`.
2. **`P(X)` invariance, measured.** Two-sample KS per feature, 4 000 pre-drift rows against 4 000
   post-drift, over the **100 independent** feature streams: rejection rate `0.12` against a null
   reference of `1 - 0.95^2 = 0.0975`, `+0.76 SE`. **HELD.**
3. **`Delta_e` invariance, as an equality.** At fixed seed, **100/100** seeds give one and the same
   `peak_excess` and one and the same detection count across the whole 20-magnitude grid. The
   detector's output is not a function of the drift at all.

**NOT PRODUCED**, per the rule, which forbids reporting a blind detector's noise as `ABSENT`. The
correlations are reported because D8 asks for them, on a **cluster bootstrap over seeds**: all four
contain zero.

| statistic | `rho` | CI95 (cluster) | CI95 (row, **wrong**) |
|---|---|---|---|
| `peak_excess` vs `tau_erase_fw` | 0.066 | `[-0.096, 0.222]` | — |
| `peak_excess` vs `tau_erase` | 0.074 | `[-0.070, 0.211]` | — |
| `detection_delay` vs `tau_erase_fw` | 0.017 | `[-0.233, 0.274]` | — |
| `detection_delay` vs `tau_erase` | 0.185 | `[-0.076, 0.415]` | — |

**The design effect decides this rule.** The 2 000 rows are 100 independent `X` streams counted 20
times each, `deff = 20` by construction. Under the `gamma = 1` instrument a row-level bootstrap
returned `rho = 0.111`, CI95 `[0.0575, 0.1634]` for `detection_delay` vs `tau_erase_fw` — an interval
excluding zero, hence verdict `PRESENT`, hence *the closed-loop reframing of the article declared
FALSE*. The cluster bootstrap on the same data returned `[-0.033, 0.242]`. The verdict rested
entirely on whether the design effect was integrated, which is why `CLAUDE.md` requires it and why
`test_cluster_bootstrap_does_not_understate_the_interval` now guards it.

**Declared cost, and it is the result.** The canonical Bernoulli family and the rotation family both
move the decision boundary at fixed `P(X)`; BAF and INSECTS are excluded as terrain by S7-ter's
measurement. There is no stream in this repository on which the third exposure class can see the
drift under study. That delimits the design space rather than populating it, and it is what (C4)'s
third row must say.

## 10. D9 — EDDM, with its arming column

S2-bis measured why the `0/1080` collapse happens on ProteuS: `0` pre-drift errors, `9` over the
whole 8 000-step stream, `warm_start = 30` never reached. It is a detector that never armed, not a
family that was defeated. On the canonical family `p_0 = 0.024` arms it, and its row is a
measurement of the detector.

**ARMED-COLUMN.** On the canonical family, armed on `100 %` of runs, median at `t_rel = +16`. That
instant is **inside the transient**, and the reason is the corpus, not the detector: S6 traces the
last `1 000` pre-drift steps, not the campaign's `4 000`. Those 1 000 steps carry about 24 errors
against a `warm_start` of 30. In the deployed pipeline the same `p_0` arms it near `t_rel = -2750`,
which is derived from `p_0` and **not observed here**. EDDM's row therefore carries the arming
instant beside the delay, never the delay alone.

The column earns its keep on the second stream (§7). At `p_0 = 0.069` EDDM arms at a median
`t_rel = -554`, comfortably before `tau*` — so its collapse there to `0.022` detection at `0.930`
pre-drift false alarms is a measurement of the detector and not of its warm-up, and it inverts its
canonical-family rank from first to last. Three streams, three different states:

| stream | `p_0` | armed | detect within `W` | pre-drift FA |
|---|---|---|---|---|
| ProteuS (S2-bis) | 0 | **never** (`9` errors in 8 000 steps) | `0/1080` | — |
| canonical Bernoulli | 0.024 | at `t_rel = +16` on the traced window | 0.974 | 0.020 |
| rotation `eta = 0.05` | 0.069 | at `t_rel = -554` | **0.022** | **0.930** |

EDDM is neither a defeated family nor a resolution: its behaviour is a function of the stream's
error rate, and the table says so in a column instead of ranking it.

## 11. D10 — what replaces the immunity claims

Three boundaries were put to measurement. Two are measured and one is withdrawn.

| boundary | state | replaces |
|---|---|---|
| contrast requirement `min(W, n_stat) Delta_e >= k*` | **measured**, §5 | `eq:Rkswin` as the governing condition for KSWIN |
| smoothing-convention false-alarm flood | **measured**, §6 | *"without false-alarm flooding"*, `.tex:500` |
| reservoir contamination (B3) | **withdrawn**, §4 | nothing — the clause is not restated in a weaker form |
| ordering stability across nulls | **measured**, §7 | the ordering claim of (C4), now qualified by the EDDM inversion |

Per D10's second branch, a boundary that returns `NOT PRODUCED` is withdrawn from the text rather
than restated with a weaker adverb. B3 is withdrawn. The charges are in `transfer_S9.md`.

## 12. Artifacts, reproduction, declared debt

| artifact | content |
|---|---|
| `results/S9_detector_coverage/data/traces.parquet` | T9.1, 32.4 M rows, 20 hive partitions, gitignored |
| `tables/s9_offline_summary.json` | T9.1, 1 200 cells, `W_provenance` |
| `tables/s9_requirement_lattice.json` | D1, 16 cells, no simulation |
| `tables/s9_kswin_dilution.json` | T9.2, 7 680 cells over 192 000 runs |
| `tables/s9_input_space.json` | T9.3, 2 000 runs, `gamma_calibration`, `positive_control` |
| `tables/s9_family_ordering*.json` | T9.4 / T9.5, both sources |
| `tables/s9_rotation_regeneration.json` | trunk identity of the regenerated rotation campaign |

Determinism: T9.1 verified byte-identical on two full passes (20/20 partitions, 2 JSON). T9.3
verified byte-identical on two passes. T9.2 verified on the smoke grid; the full grid costs ~35 min
per pass and its mechanism is the same cell-level replay guarded by
`test_replay_of_one_cell_is_bit_identical`. `sha256sum -c` against
`artifacts_sha256_pre_ssot.txt` stays at **27 OK / 7 FAILED**, the seven being exactly the declared
deviations; **no entry added to `authorized_deviations.txt`** and no S8 or S6 artifact regenerated
in place.

Debt, declared and not masked: the S6 trace corpus is reached through a symlink to an artifact
outside this repository and is not versioned anywhere, so no S9 output is reproducible from a fresh
clone until that corpus is regenerated. The rotation traces S8 produced are gitignored and absent
everywhere; S9 regenerated the `eta = 0.05` arm into its own tree and checked it against S8's
committed `runs.parquet` — **trunk identity PRESERVED**. `ks_2samp`'s exact p-value is not valid
under the ties the smoothed arm produces; that gap is declared, measured in its consequence, and not
repaired.
