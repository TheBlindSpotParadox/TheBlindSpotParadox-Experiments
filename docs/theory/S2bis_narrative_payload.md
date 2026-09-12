# S2-bis narrative payload — T-C and T-D

Ready to integrate. **No manuscript section is edited by this stream.** Every block below is
English prose with its numbers sourced to a committed artifact, for the writing stream to place.
Patches with SEARCH/REPLACE anchors live in `docs/theory/transfer_S2bis.md`; this file carries the
content and the site inventory.

Line numbers quote `docs/manuscript/articleA_blindspot_v64_camera_ready.tex` **as it stands on
`main` after `688bcf5`** (S2 patches A and B applied). The pre-patch numbering used by
`plans/PLAN_S2-bis.md` is lower by 15 before `rem:flooding` and by 19 after it. Every anchor below
is quoted by text; the line number is a convenience, not the anchor.

---

## T-C — the canonical blind spot is a fact of calibration

### (a) The statement, with its three numbers and their bands

Source: `results/S2_theory/tables/s2_gate_T20.json`, key `floor_and_family`, evaluated at the
canonical operating point `Delta_e = 0.326793`, `W = 57.4`, `eps = 0.05`, `lambda = 50`.

| quantity | value | band | artifact key |
|---|---|---|---|
| detectability floor (chord bound) | 15.40 at `p_true = 0.024` | **[13.88, 18.29]** over `p_true in [0.015, 0.032]` | `floor_and_family.floor_chord_interval` |
| measured evidence ceiling | **33.51** | median `max_t A_unrefl`, arm `full` | `floor_and_family.family_requirements.measured_ceiling_median_A_unrefl` |
| `R_CUSUM` at `lambda = 50` | **59.27** | `lambda + sqrt(W/2 ln(1/eps))`, margin 9.2724 | `floor_and_family.family_requirements.common_alpha_ladder[lambda_cusum=50]` |
| `R_CUSUM` at `lambda_op` | **31.20** | **[29.15, 31.67]** over the `lambda_op` bootstrap CI `[19.876, 22.398]` | derived from the same margin |

> **Integrable statement.** At the canonical operating point the information is present and the
> monitor does not take it. The evidence the ensemble makes available before the transient is
> erased, measured on 8 000 synchronised runs, is $A = 33.5$; the detectability floor that
> `thm:floor` places under any monitor at this magnitude is $\FloorBand$, so the stream clears the
> information-theoretic limit with room to spare. What the stream does not clear is the
> *requirement the monitor imposes on itself*: a PageHinkley run at $\lambda = 50$ asks
> $R_{\mathrm{CUSUM}} = 59.3$, nearly twice the evidence available. The gap is not a property of
> the classifier, of the drift, or of the bound --- it is the threshold. At the operational
> threshold the repository has already measured, $\lambda_{\mathrm{op}} = \LambdaOpNarrow$
> $\LambdaOpNarrowCI$, the same requirement is $R_{\mathrm{CUSUM}} = 31.2\,[29.1, 31.7]$, which the
> measured ceiling clears at every point of the interval. The article carries the corrective for
> its own phenomenon, measured, in its own artifacts.

Three statement-level rules this block must keep:

1. The floor is quoted as an **interval**, never as a scalar. `ARL_0` moves nine orders of
   magnitude across `p_true in [0.015, 0.032]` (`1.1e14` to `1.1e23` at `lambda = 50`); the floor
   survives that only because `ARL_0` enters it through `ln(1/alpha)` alone. Rule B8.
2. The chord bound, not the chi-square relaxation, is the one quoted. At `p_true = 0.024` the
   chi-square step is loose by a factor `\ChiLoose` on the KL term and returns a floor of **1.80**
   where the chord bound returns **15.40**. Quoting 1.80 would put the clearance under the measured
   ceiling at `33.51 - 1.80 = 31.7` instead of `33.51 - 15.40 = 18.1`, overstating it by a factor
   1.75 — and it is the clearance, not the floor, that the blind-spot claim rests on.
3. `lambda_op` is quoted as its bootstrap interval. The point estimate 21.9283 is never the
   decision variable — the S6 near-miss at `q05(S_max) = 15.219` against a threshold of 15.00 is
   why.

### (b) The KSWIN retraction, stated at both alphas

**The requirement `R_KSWIN` has two readings and the manuscript currently quotes neither with its
`alpha`.** Rule B9 makes the disclosure mandatory.

| reading | `alpha` | `R_KSWIN` | clears the ceiling 33.51? |
|---|---|---|---|
| KSWIN at its **deployed** level | `R4_KSWIN_ALPHA = 0.005` | **22.68** | yes |
| KSWIN at the **common** level of a `lambda = 50` CUSUM | `6.28e-16` | **41.997** | **no** |

At a common false-alarm level the distributional monitor does not clear the ceiling either. The
`22.68` that makes KSWIN look structurally immune is KSWIN evaluated at a false-alarm level
**thirteen orders of magnitude looser** than the CUSUM it is compared against.

**The crossing, solved on the exact requirement curves** (`results/S2bis_calibration/tables/`
`s2bis_proteus_gate.json`, key `cor_split_crossings`): the three requirements share the `eps`
margin, so it cancels, and

- `R_CUSUM` crosses `R_KSWIN` at `lambda = 22.60`, `ln(1/alpha) = 16.34`;
- `R_CUSUM` crosses `R_ADWIN` at `lambda = 26.47`, `ln(1/alpha) = 18.97`.

The measured `lambda_op` interval `[19.876, 22.398]` lies **entirely below the KSWIN crossing**,
though its upper bound sits only `0.21` short of it. At the threshold the repository actually
recommends, the cumulative monitor asks *less* evidence than the distributional one at the same
false-alarm level — by `1.46` at the lower bound of the interval and by `0.11` at the upper. The
margin is real and it is narrow, and the statement is made over the interval, never at the point
estimate.

| `lambda` | `ln(1/alpha)` | `R_CUSUM` | `R_KSWIN` | `R_ADWIN` | `R_CUSUM - R_KSWIN` | ceiling 33.51 clears `R_CUSUM`? |
|---:|---:|---:|---:|---:|---:|:--|
| 15 (`R4_PHT_LAMBDA`) | 11.16 | 24.27 | 28.13 | 31.10 | −3.86 | yes |
| 19.876 (`lambda_op` lo) | 14.48 | 29.15 | 30.61 | 33.18 | −1.46 | yes |
| 21.928 (`lambda_op`) | 15.88 | 31.20 | 31.57 | 34.01 | −0.37 | yes |
| 22.398 (`lambda_op` hi) | 16.20 | 31.67 | 31.78 | 34.19 | −0.11 | yes |
| **22.605 (crossing)** | **16.34** | **31.88** | **31.88** | 34.27 | **0.00** | yes |
| 25 | 17.97 | 34.27 | 32.94 | 35.19 | +1.34 | **no** |
| 50 (the published point) | 35.00 | **59.27** | 42.00 | 43.34 | **+17.28** | **no** |

KSWIN's measured advantage at `lambda = 50` is what a monitor gets for being read at a looser
`alpha` and for being compared against a CUSUM run seventeen units of evidence above the crossing —
not a property of its family. Two further readings the table makes available and the manuscript
does not currently state: the measured ceiling clears `R_CUSUM` at every point of the `lambda_op`
interval and fails to clear it from `lambda = 25` upward, which locates the blind spot's boundary
on the threshold axis; and `R_ADWIN` is **not** cleared across most of that interval (33.18 at the
lower bound, 34.19 at the upper, against a ceiling of 33.51), so the windowed monitor is the one
whose requirement the stream does not reliably meet at the operating point.

**Ten sites assert immunity by construction and must be rewritten.** Two sites are already
correctly hedged and are the phrasing model.

**Two of the ten are inside the excluded subsections and must not be edited before the v65
assembly.** The exclusion spans, measured from the manuscript's own headings (pre-patch numbering):
`sec:race` L168-184, `sec:hydra` L185-209, `sec:starvation` **L210-295**, `sec:decoupling`
**L376-411**. The column below states the status of each site rather than leaving the writing
stream to rediscover it.

| site (`main` / pre-patch) | current claim | action | status |
|---|---|---|---|
| L166 / 151 (`sec:related`) | *"Windowed and distributional monitors (ADWIN, KSWIN) escape by construction"* | replace *escape by construction* with *escape on the settings we test, at the false-alarm levels we deploy* | editable |
| L294 / **279** (`prop:starvation` remark) | *"immune to starvation while its reference window holds pre-drift data"* | conditional already there; add the `alpha` disclosure | **inside `sec:starvation` — DEFERRED** |
| L428 / **409** | *"the Decoupling Principle is satisfied by construction"* | the same *by construction* reflex; narrow to the tested settings | **inside `sec:decoupling` — DEFERRED** |
| L463 / 444 | heading *"windowed immunity, not a clock artefact"* | *windowed robustness on the tested settings* | editable |
| L466 / 447 | *"ADWIN remains immune to starvation as long as `W_0` spans that transient"* | conditional already present; keep, add the `alpha` | editable |
| L467 / 448 | *"survives only because it is a windowed rather than cumulative monitor"* | add: *and because it is deployed at `delta = 0.002`, a level the CUSUM is not read at* | editable |
| L485 / 466 | *"rendering it structurally immune to transient signal erasure"* | **retract `structurally`**. The measured resolution stands; the mechanism claim does not | editable |
| L540 / 521 (Discussion) | *"on the settings we test they restore detection at no predictive cost"* | **already correct — the phrasing model** | — |
| L553-555 / 534-536 (Conclusion) | *"substituting cumulative-evidence monitors with distribution-based tests like KSWIN escapes the starvation regime entirely"* | *escapes it at the false-alarm levels we deploy*; drop *entirely* | editable |
| L103 / 88 (Abstract) | *"avoids the constraint on the settings we test---a regime-restricted observation rather than an immunity"* | **already correct — the phrasing model** | — |
| `sections/related_work_v2.tex` L110-112 | KSWIN's two-sample test presented without its level | add the deployed `alpha` | outside the S2-bis perimeter (S3) |

### (c) The contribution restated as a calibration rule

Four measurements, none of which depends on the flooding gate's outcome, converge on the same
restatement.

1. **The canonical blind spot is a threshold fact.** The evidence is present (ceiling 33.5) and
   clears the information-theoretic floor (`\FloorBand`); what it does not clear is
   `R_CUSUM(\lambda = 50) = 59.3`. At `lambda_op` the same requirement is 31.2 and the ceiling
   clears it. §(a).
2. **`lambda = 15` on ProteuS is calibrated on nothing measurable.** The pre-change error rate of
   that stream is **identically zero** — the target is a deterministic step function of `t` and the
   classifier predicts the constant majority class perfectly before the change — so every
   `lambda > 0` meets every false-alarm budget over the pre-change span and no measurement selects
   15. `transfer_S2bis.md` §2.7.
3. **The INSECTS threshold asymmetry is an artefact of where the budget is measured.** The factor
   `6.3` that `rem:flooding` attributes to bagging holds on one of three streams and **inverts** on
   the other two once the budget is set over the span the detector actually runs.
   `transfer_S2bis.md` §2.2.
4. **KSWIN's immunity is an `alpha` disclosure away from vanishing.** §(b).

> **Integrable statement.** Read together, the results of this paper are a **calibration rule**
> rather than a paradox. The blind spot is not a barrier the architecture erects: at every
> operating point we measure, the evidence the ensemble leaves on the stream exceeds the
> information-theoretic floor, and what the monitor misses it misses because its threshold demands
> more evidence than the transient can supply. The rule the measurements support is explicit and
> operational: *set the monitor's threshold from the false-alarm budget of the span it will
> actually run armed over, on the error stream of the classifier it will actually be paired with,
> and check that the resulting requirement lies below the measured evidence ceiling.* Each clause
> is load-bearing, and each is violated somewhere in the experiments this paper itself reports ---
> a budget set on a warm-up $\SpanOverWarm$ times shorter than the armed span (Section~\ref{sec:crossover}),
> one threshold shared across classifiers whose pre-change error volatility differs by a factor of
> three (Section~\ref{sec:proteus}), and detector families compared at false-alarm levels thirteen
> orders of magnitude apart (Section~\ref{sec:discussion}). We do not claim the literature does
> better; we claim we can now say what \emph{better} would mean.

**The flooding half, restated.** Rule B3 returned **COLLAPSE**: the `F1` ratio of
`10.57` on *gradual\_balanced* — reproduced here to four figures from the raw CSVs — falls to
`1.27` `[1.16, 1.43]` once each pipeline's false-alarm budget is set over the pre-change span its
detector actually runs armed, and `89.9 %` of the published log-ratio is threshold-attributable.

> **Integrable statement.** The flooding result is not *"adaptation floods the monitor"*. It is
> *"an operator who calibrates the monitor on the quiet warm-up of an adaptive classifier picks a
> threshold that will flood once that classifier has adapted"* --- and the quieter the warm-up, the
> worse the choice. That is a stronger claim than the one it replaces: it is mechanical, it names
> the operator error, it predicts the sign and it is falsifiable. It also explains the two INSECTS
> variants on which the published ordering **reverses**: their warm-ups are two and three times
> longer, the two classifiers have converged by the end of them, and the asymmetry disappears. What
> survives at an equal budget is a residual coupling effect of a factor $\RhoEqSpan$
> $\RhoEqSpanCI$ --- real, its interval excluding $1$, and an order of magnitude smaller than the
> figure the comparison at the warm-up budget reports.

**What this does *not* retract.** Every measurement stands: the separation at `c_int = 1`, the
`0/1080`, the Hydra factor, the erasure decomposition. What changes is the *claim* attached to
them. The paper is stronger for it: a paradox invites the reader to accept a limit, a calibration
rule tells them what to do, and the repository has already measured the number they need
(`lambda_op = \LambdaOpNarrow` `\LambdaOpNarrowCI`).

### (d) `cor:split` in one sentence, for `sec:discussion`

> Because $R_{\mathrm{CUSUM}}(\alpha) = \lambda(\alpha) + \varepsilon$-margin grows **linearly** in
> $\ln(1/\alpha)$ with slope $1/\theta^\star = 1.468$ while $R_{\mathrm{ADWIN}}$ and
> $R_{\mathrm{KSWIN}}$ grow as its **square root**, the three families cross: the cumulative monitor
> asks the least evidence at loose false-alarm levels and the most at tight ones, the crossings
> falling at $\ln(1/\alpha) = 16.3$ against KSWIN and $18.97$ against ADWIN at the canonical
> $(W = 57.4, p_0 = \PzeroMeas)$. The detector-side resolution the paper reports is that crossing
> read at one point, not a family property --- and the operational threshold
> $\lambda_{\mathrm{op}}$ sits on the side of it where the CUSUM is the cheaper monitor.

This is the only detector-side resolution mechanism the paper possesses, and it currently lives in
an appendix.

---

## T-D — EDDM: the empirical reading changes, and so do both prior readings of it

### Three readings, and why the first two are wrong

**The brief's reading.** *The S2 control shows the detector had not finished its 30-error warm start
at `tau*` in 95 % of runs, so the `0/1080` is an unarmed detector.* That control
(`s2_eddm.json`, `rule_R5.traces_are_not_a_recall_test`) is a property of the **S6 traces**, whose
pre-change span is 1 000 steps at `p_0 = 0.024`, furnishing about 24 errors against a `warm_start`
of 30. It is a statement about a different stream.

**The plan's correction of the brief.** *ProteuS gives the detector 4 000 pre-drift steps ≈ 96
errors (`s2_eddm.json`, `closed_form[].history == "R4 ProteuS"`, `n_0_errors = 96.0`), so the
unarmed-detector reading does not transfer.* **This is also wrong, and the artifact says so about
itself:** `n_0_errors = 96.0` is `p_0(S6) = 0.024 x 4000`, the S6 Bernoulli base rate applied to the
ProteuS span *length*. It is not a ProteuS measurement, and no ProteuS measurement of it existed
before this stream — `exp_R4_main_table.py` records no error stream.

**What the measurement says.** S2-bis instruments `exp_R4_main_table.run_concept_drift` with the
error count and runs it on the streams that produce the `0/1080`
(`results/S2bis_calibration/tables/s2bis_proteus_eddm_arming.csv`). The instrumented loop reproduces
R4's own detections exactly, so it is R4's pipeline and not a re-implementation.

| measured on ProteuS | EDDM + HT | EDDM + ARF (`c_int = 1`) |
|---|---:|---:|
| pre-change errors at `t = T_DRIFT` | **0** | **0** |
| errors required (`warm_start`) | 30 | 30 |
| errors over the **whole** 8 000-step stream | 32 | **9** |
| step at which the 30th error occurs | ~4 030 (30 steps **after** the change) | **never** |
| detections | 1 (at ~4 031) | **0** |

The `0/1080` **is** an unarmed detector — the brief's conclusion — but for a mechanism neither the
brief nor the plan identified. The ProteuS pre-change error rate is **exactly zero**: the target is
a deterministic step function of the time index (`simulate_stream:105`,
`regime = (f_t > 0.5)` with `f_t = expit(4(t - tp)/w)`), constant before the change, and
`run_concept_drift:135`'s `y_pred = model.predict_one(x) or 0` predicts that constant from the first
step. The detector therefore enters the change point with **zero** of its thirty required errors,
not twenty-four of thirty. And on the ARF arm it never arms at all: the ensemble adapts so fast that
the whole 8 000-step run produces **nine** errors, fewer than the warm start requires.

### What this means for the claim, in both directions

> **What the measurement establishes.** EDDM paired with an ARF at $c_{\mathrm{int}} = 1$ raises
> zero alarms in $1{,}080$ runs where the same detector on a non-adaptive learner raises $882$
> (sign test $p \approx 1.9\times10^{-9}$). The ADD column is empty on all $1{,}080$ runs: these
> are absent alarms, not late ones. The separation is real and is reproduced here.
>
> **What produces it.** EDDM signals on the distance between consecutive errors and cannot signal
> before it has seen $30$ of them. On these streams the classifier is exact before the change ---
> the pre-change label is constant --- so the detector enters the change point with no error history
> at all, and the adaptive ensemble then commits so few errors over the entire run ($9$ on median)
> that the warm start is never reached. The collapse is an *arming* failure, not an accumulation
> failure: the stopping-time argument of Prop.~\ref{prop:starvation}, which requires a monitor that
> accumulates a persistent deviation, never gets the chance to apply.
>
> **What it does not establish.** It is not evidence that a requirement $R_{\mathrm{EDDM}}$ of the
> form of Eqs.~\eqref{eq:Rcusum}--\eqref{eq:Rkswin} governs the collapse --- that requirement is
> withdrawn --- nor is it a like-for-like family comparison: every ProteuS pipeline runs at one
> common PageHinkley threshold $\lambda = \LambdaFA$ with the detector armed at $t = 0$, and EDDM
> runs at River's defaults, so the detectors compared share no false-alarm level.

**This strengthens the blind-spot thesis rather than weakening it.** *Nine errors in eight thousand
steps* is a sharper statement of evidence erasure than any alarm count: the adaptation does not
merely outrun the monitor's accumulator, it removes the monitor's raw material. The claim that has
to change is the *mechanism* attributed to it, not the phenomenon.

### What transfers from the closed form

`W_EDDM` is proportional to `n_0`, the pre-change error count since the last reset, and the normal
approximation instantiated in the manuscript (`W = 155`) contains no such term. At the `R4 ProteuS`
history the closed form gives a median `W_EDDM = 230.5` steps (min 168.2, max 3 657.6 over the
twenty magnitudes) — but that closed form is evaluated at `n_0 = 96`, and the measured `n_0` is
**0**, at which the window is not merely large but undefined. The requirement the manuscript
instantiated is the wrong shape; rule R5's withdrawal stands and is reinforced.

**EDDM is declared OUT OF SCOPE for the knob equalisation of Phase 2**, with the reason: its level
is a ratio against a running maximum and carries no false-alarm parameter of the same kind as
`lambda`, `delta` or `alpha`, so there is no knob to set to a common `alpha`. That is a property of
the detector, not an omission of this stream.

### Sites that read `0/1080` as a blind spot

| site (`main`) | content |
|---|---|
| `.tex` L460-461 | the EDDM row of the Table I discussion |
| `.tex` L473 | the EDDM/ARF collapse restated |
| `.tex` L482 | the SRP paragraph, which cites the same `0/1080` shape |
| `.tex` L485 | the KSWIN resolution, quoted against `0/1080` for PHT+ARF |
| `.tex` L526 | the static-RF validation paragraph |
| Table I caption (`tables/table1_proteus_summary.tex`, generated by `exp_R4_main_table.build_caption`) | *"EDDM+ARF c=1 detects 0/1080 runs vs 882/1080 for EDDM+HT"*, and *"the seed level (the unit of statistical independence of the synthetic generator)"* |
| `sections/prop3_v2.tex` L286-305 | already carries the corrected reading; it is the model for the others |

### Two out-of-perimeter `R_EDDM` sites, re-transmitted unchanged from S2

Both still carry the requirement rule R5 withdrew. Neither is in the S2-bis writable set and
neither is patched here. S2 handed them forward; S2-bis hands them forward again rather than
letting them lapse.

1. `docs/manuscript/articleA_blindspot_v64_camera_ready.tex` L166 (`sec:related`): *"any monitor
   that requires a persistent deviation with a stopping time scaling as `Omega(lambda / Delta e)`
   --- DDM, EDDM, ECDD --- is defeated"*. EDDM's stopping structure is not `Omega(lambda/Delta e)`:
   it is a level test on a cumulative ratio against a running maximum, whose requirement grows with
   the pre-change history and does **not** shorten with `Delta e`.
2. `docs/manuscript/sections/related_work_v2.tex` L108-109: *"DDM, EDDM and ECDD share the
   accumulation structure and inherit its window sensitivity."* Same correction.

The **empirical** EDDM result is untouched by either correction and must be kept.
