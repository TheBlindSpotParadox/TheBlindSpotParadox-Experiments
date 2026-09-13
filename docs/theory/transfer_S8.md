# Transfer document — stream S8 (mechanistic generality, rotation generator, ab initio arms)

Parent `a03380f`, branch `stream-s8`. Decision rules D0–D9 fixed before any measurement in
[`docs/prompts/s8-decision-rules.md`](../prompts/s8-decision-rules.md) (`eee494c`). Measurement
report: [`S8_generality.md`](S8_generality.md).

**Nothing below is applied.** `stream-s11a` works in parallel on the v65 skeleton of the same
document, so every charge is delivered as a SEARCH/REPLACE payload with a verbatim anchor and a
named target file. Anchors are quoted by text; line numbers are a convenience.

Routing rule, from `CLAUDE.md`. `sec:race` (L168), `sec:hydra` (L185), `sec:starvation` (L210) and
`sec:decoupling` (L376) of `articleA_blindspot_v64_camera_ready.tex` are superseded by
`docs/manuscript/sections/framework_v2.tex` and **must not be patched**. Every S8 charge landing
inside one of the four is routed to the `sections/` fragment instead;
`tests/test_S8_generality.py::test_transfer_S8_payloads_avoid_the_excluded_subsections` checks that
by character offset rather than by eye.

| charge | lands on | target | status |
|---|---|---|---|
| **S8-A** | preamble macro block | `articleA_blindspot_v64_camera_ready.tex` | payload, outside the excluded zone |
| **S8-B** | `rem:cf_scope` (.tex:233, inside `sec:hydra`) | `sections/framework_v2.tex` | payload, **routed** |
| **S8-C** | `% Figure 4 merged …` (.tex:327, `sec:hardware`) | `articleA_blindspot_v64_camera_ready.tex` | payload, deferred by `space_constraints_audit.md` §4 |
| **S8-D** | `\LearnShare` at .tex:115, :357, :568 | assembly decision | **charge, no payload** — see §A.2 |
| **S8-E** | ARF(M=1) called a HAT (.tex:224, inside `sec:hydra`) | assembly decision | **charge, no payload** — no v2 home exists yet |
| **S8-F** | `rem:invariance_measured`, the `A/A_rect` sign change | `sections/framework_v2.tex` | payload, scope of a measurement it keeps |
| **S8-G** | the protocol's single generator | `sections/protocol_v2.tex` | payload, declares the second family |
| **S8-H** | the sentence after `def:blindspot` | `sections/framework_v2.tex` | payload, budget vs erasure time |
| **S8-I** | `sec:dep_mcrit`'s two unmeasured quantities | `sections/dependence_v2.tex` | payload, both now measured |

---

## A. S8-A — preamble macros for stream S8

Append-style payload on the S2 macro block. **`\LearnShare` is deliberately NOT mutated**: it is
consumed at .tex:357, inside `sec:starvation`, and silently changing what an excluded subsection
renders is the same divergence the exclusion exists to prevent. The new macros stand beside it and
the assembly decides which site takes which (charge S8-D).

~~~~~~~~~
docs/manuscript/articleA_blindspot_v64_camera_ready.tex
<<<<<<< SEARCH
\newcommand{\DeCritCI}{[0.114, 0.127]}       % 95% bootstrap CI (10,000 draws)
=======
\newcommand{\DeCritCI}{[0.114, 0.127]}       % 95% bootstrap CI (10,000 draws)

% ── Stream S8, ab initio arms. Source: results/S8\_ab\_initio/data/s8\_causal.json,
% decomposition\_ab\_initio.a\_pos\_common. Reference arm forked at tau*, not at the first swap.
% Every value is read from a committed artifact; none is typed by hand.
\newcommand{\LearnSharePure}{98.6}           % E\_learn\_pure / E\_total, learning with no tree
                                             % EVER replaced. 0.98637, n = 1999
\newcommand{\LearnSharePureCI}{[98.5,\,98.8]}% seed-paired bootstrap, 10\,000 resamples
\newcommand{\SwapFirstShare}{0.71}           % E\_swap\_first / E\_total, the FIRST replacement alone
\newcommand{\SwapFirstShareCI}{[0.63,\,0.78]}
\newcommand{\SwapRestShare}{0.56}            % E\_swap\_rest / E\_total, every later replacement
\newcommand{\SwapRestShareCI}{[0.47,\,0.67]}
\newcommand{\AbInitDetect}{49}               % detections out of 100 at lambda = 50, Delta\_e = 0.3268,
                                             % replacement suppressed from tau* onward (18 when
                                             % suppressed only after the first, 0 nominal)
>>>>>>> REPLACE
~~~~~~~~~

### A.2 Charge S8-D — `\LearnShare` is not what its three call sites say it is

`\LearnShare = 99.3` is `E_learn / E_total` on a decomposition whose three arms **all fork after the
first replacement** and therefore all carry it. The tau\*-anchored campaign separates it:
`E_learn_pure = 98.64 %` `[98.48, 98.82]` and `E_swap_first = 0.71 %` `[0.63, 0.78]`, with
`E_swap_rest = 0.56 %` `[0.47, 0.67]` and an additivity residual of `2.3e-13` over 1 999 cells.

Three sites read the macro and each needs a different decision, which is why this is a charge and
not a payload:

| site | current reading | what the measurement says |
|---|---|---|
| abstract, .tex:115 | *"ordinary incremental learning of the surviving trees performs $\LearnShare\%$ of the erasure"* | `98.6` is the number for that sentence: it names learning alone |
| `sec:starvation`, .tex:357 | *"assigns $\LearnShare\%$ of that erasure to ordinary incremental learning … rather than to the internal clock"* | same, **but the line is inside an excluded subsection**; the sentence's home at assembly is `framework_v2.tex` |
| conclusion, .tex:568 | *"incremental learning of the surviving trees performs $\LearnShare\%$ of the erasure, and the replacements after the first act as a terminal lock"* | `98.6` for the first clause; the second clause is now **measurably wrong in its ordering** — the first replacement carries more erasure (`0.71 %`) than all the later ones combined (`0.56 %`), and `49/100` against `18/100` says the lock is set by the first, not by the rest |

The conclusion's "replacements *after the first*" is the clause S8 contradicts. It is recorded here
and not patched: the sentence appears in the conclusion (outside the exclusion) and in
`sec:starvation` (inside it) in near-identical form, and splitting them at this stage is exactly how
the two copies diverge.

---

## B. S8-B — `rem:cf_scope` is answered, and the answer is routed

`rem:cf_scope` (.tex:233) states the gap in the manuscript's own words:

> Both counterfactual arms fork *at* the first replacement and therefore share it with the nominal
> arm. […] they do not isolate the contribution of the first replacement itself, which would require
> an arm with replacement suppressed from $\tau^*$ onward. No claim is made about that quantity.

That remark is at .tex:233, **inside `sec:hydra`**. The answer therefore goes to `framework_v2.tex`,
appended after `rem:invariance_measured`, which is where the v2 draft already discusses the
`no_swap` / `frozen` counterfactual.

~~~~~~~~~
docs/manuscript/sections/framework_v2.tex
<<<<<<< SEARCH
  Invariance is therefore an \emph{effect of adaptation}, demonstrated by
  removing it, and not a consequence of an exponent equal to one.
\end{remark}
=======
  Invariance is therefore an \emph{effect of adaptation}, demonstrated by
  removing it, and not a consequence of an exponent equal to one.
\end{remark}

\begin{remark}[The first replacement, isolated]\label{rem:first_swap}
  The two counterfactual arms of the synchronised campaign fork \emph{at}
  $\tau_{\mathrm{swap}}^{(1/M)}$ and therefore share the first replacement with
  the nominal arm; no contrast among them can attribute anything to it. Two
  further arms fork at $\tau^*$ instead --- an instant fixed by the protocol
  rather than by the trajectory --- with both internal detector paths made
  inert, the second additionally stopping \texttt{learn\_one}. With the
  $\tau^*$-frozen arm as the single reference the decomposition closes
  identically,
  \[
    E_{\mathrm{total}} = E_{\mathrm{learn}} + E_{\mathrm{swap}}^{(1)}
                       + E_{\mathrm{swap}}^{(>1)} ,
  \]
  measured additivity residual $2.3\times10^{-13}$ over $1{,}999$ cells. Over
  $100$ seeds and $20$ magnitudes, incremental learning with \emph{no} tree ever
  replaced accounts for $98.64\%$ of the erasure ($95\%$ seed-paired bootstrap
  $[98.48, 98.82]$), the first replacement alone for $0.71\%$
  $[0.63, 0.78]$, and every later replacement together for $0.56\%$
  $[0.47, 0.67]$. The first replacement therefore carries \emph{more} of the
  erasure than all its successors combined.

  The volumetric share understates it at the threshold. At $\Delta e = 0.3268$
  and $\lambda = 50$ the external CUSUM fires in $0$ of $100$ nominal runs, $18$
  of $100$ when replacement is suppressed after the first, and $49$ of $100$
  when it is suppressed from $\tau^*$ onward. Isolating the first replacement is
  worth $31$ points of detection rate --- more than suppressing every
  replacement after it.
\end{remark}
>>>>>>> REPLACE
~~~~~~~~~

When the v65 assembly consumes `framework_v2.tex`, `rem:cf_scope` and its closing sentence *"No
claim is made about that quantity"* are superseded by `rem:first_swap` and must not survive
alongside it.

---

## C. S8-C — the standalone Figure 4

`space_constraints_audit.md` §2.1 reserves this; §4 defers the loosening to the M8 arbitration on
the target venue, so the payload is **recorded, not applied**: inserting a figure changes the
pagination.

The asset exists and is pipeline-produced: `results/S8_r7_figure/figures/Fig_R7_clock_mismatch.png`,
rendered by `experiments/S8_generality/s8_figure_r7.py` from the committed
`results/R7_clock_mismatch/tables/exp_R7_regime1_miss_curve.csv`. R7 is not re-executed and its band
means reproduce `exp_R7_regime1_miss_summary.tex` exactly. When the copy lands in
`docs/manuscript/figures/`, `tests/test_manuscript_integrity.py` finds its twin by the
`results/*/figures/<name>` glob with no change to the test.

~~~~~~~~~
docs/manuscript/articleA_blindspot_v64_camera_ready.tex
<<<<<<< SEARCH
% Figure 4 merged with Figure 2 above to respect ICDM page limits.
=======
\begin{figure}[t]
  \centering
  \includegraphics[width=\columnwidth]{figures/Fig_R7_clock_mismatch.png}
  \caption{Regime 1, the clock-mismatch artefact. Miss rate
    $P(\tau_{\mathrm{ARF}} < \tau_{\mathrm{det}})$ against drift magnitude for the three clock
    configurations, $100$ seeds $\times$ $20$ magnitudes. Under mismatched clocks the miss rate
    \emph{increases} with magnitude above $\Delta e \approx 0.2$; under matched and decoupled clocks
    it decays monotonically. Band means in the legend are those of
    Table~\ref{tab:r7_regime1}.}
  \label{fig:clock_mismatch}
\end{figure}
>>>>>>> REPLACE
~~~~~~~~~

The caption references `tab:r7_regime1`. `exp_R7_regime1_miss_summary.tex` carries the tabular but
no `\label`; the assembly must either add one or drop the cross-reference. Recorded, not decided
here.

---

## E. S8-E — what the repository calls a HAT is not a HAT

Measured, not inferred. `exp_R6_generate_data.py:44-47` builds
`ARFClassifier(n_models=1, drift_detector=ADWIN(clock=1), warning_detector=ADWIN(clock=1))`, and
`grep -rn "HoeffdingAdaptiveTree\|HATClassifier" experiments/ tests/ config/` returns nothing. The
base learner of that object is `BaseTreeClassifier(HoeffdingTreeClassifier)`
(`river/forest/adaptive_random_forest.py:251`) — a Hoeffding **Tree** with feature subsampling,
replaced wholesale by an external ADWIN. It is not the Bifet–Gavaldà HAT (one ADWIN per node,
alternate subtrees, no global reset) that .tex:224 cites.

Consequences, all operational:

- `tau_HAT`, `4.12x` and `7.99x` are measured on **ARF(M = 1)**. They are not wrong; they are
  mislabelled. Any re-derivation must keep that object as the paired arm, which is what T8.3-bis
  does.
- `river.tree.HoeffdingAdaptiveTreeClassifier` **exists** in the pinned build and had never been
  executed in this repository. T8.3 runs it as a distinct family, never as a substitute.
- The charge has **no payload**: .tex:224 is inside `sec:hydra`, and no v2 fragment carries the
  Hydra section yet. The terminology correction belongs to whoever writes it. `protocol_v2.tex:32`
  and `dependence_v2.tex:122–140` carry `\tau_{\mathrm{HAT}}` and inherit the same correction.

---

## F. S8-F — the high-magnitude sign change is a property of the generator

`rem:invariance_measured` in `framework_v2.tex` reports `A/A_rect` spanning `2.70` to `-14.12` and
changing sign at `Delta_e >= 0.452`. The measurement is correct and S8 reproduces it exactly
(`-14.1161`, switch at `0.452271`). What S8 adds is its **scope**: on a generator whose post-drift
class prior does not collapse, the descent does not exist. Under rotation at `eta = 0.05` the ratio
is monotone increasing from `0.115` to `8.03` and negative on **no** run at the top magnitude,
against `100 %` of runs negative on the canonical family.

~~~~~~~~~
docs/manuscript/sections/framework_v2.tex
<<<<<<< SEARCH
  Hypothesis~(i) is the rectangular surrogate that synchronised instrumentation
  withdraws: $A/A_{\mathrm{rect}}$ spans $2.70$ to $-14.12$ over the magnitude
  grid and \emph{changes sign} at $\Delta e \ge 0.452$, where the adapted
  ensemble ends the window below its pre-change error rate.
=======
  Hypothesis~(i) is the rectangular surrogate that synchronised instrumentation
  withdraws: $A/A_{\mathrm{rect}}$ spans $2.70$ to $-14.12$ over the magnitude
  grid and \emph{changes sign} at $\Delta e \ge 0.452$, where the adapted
  ensemble ends the window below its pre-change error rate. That sign change is
  a property of the \emph{generator} and is reported as such: the boundary-shift
  family carries a post-drift class prior $P(y{=}1) = 0.5 - \Delta e$, which
  falls under $2.5\%$ over the last seven magnitudes, so the drift makes the
  problem easier and the integrated excess turns negative. On a rotation family
  with the same $\Delta e$ but a class balance held at $50/50$ --- the post-drift
  half-plane turned by $\theta = \pi \Delta e / (1 - 2\eta)$, label noise $\eta$
  giving a Bayes error that does not vanish --- the same ratio is monotone
  increasing to $+8.0$ at the top magnitude and negative on no run, against
  $100\%$ of runs negative on the boundary-shift family. The withdrawal of
  hypothesis~(i) does not depend on the generator; the sign change does.
>>>>>>> REPLACE
~~~~~~~~~

---

## G. S8-G — a second stream family exists, and two published readings depend on which is used

The protocol section describes one generator. S8 measures a second on the identical covariate
stream, and the article now carries two families until the assembly decides which is of record.
Declared here rather than left implicit.

~~~~~~~~~
docs/manuscript/sections/protocol_v2.tex
<<<<<<< SEARCH
the monitor, which is exactly the contrast the paired resampling estimates.
=======
the monitor, which is exactly the contrast the paired resampling estimates.

\paragraph{A second label rule on the same covariates.} The boundary-shift rule
$y_t = \mathbf{1}[x_{0,t} + x_{1,t} > b]$ moves the class prior as it moves the
magnitude: $P(y{=}1) = 0.5 - \Delta e$ post-drift, under $2.5\%$ over the last
seven magnitudes of the grid. A rotation rule
$y_t = \mathbf{1}[\cos\phi\, x_{0,t} + \sin\phi\, x_{1,t} > 0]$, with
$\phi = \pi/4 + \pi \Delta e / (1 - 2\eta)$ and declared label noise $\eta$
applied to both phases, holds the balance at $50/50$ at every magnitude and
keeps $\Delta e = (1-2\eta)\,|\phi - \pi/4| / \pi$ exact --- verified at all
twenty magnitudes and both $\eta$ arms within $3$ standard errors. The
pre-drift phase is the canonical one written differently
($x_0 + x_1 > 0$ \emph{is} the rotation at $\phi = \pi/4$), so at $\eta = 0$ the
covariates, the pre-drift labels, the warm-up and the ensemble state at $\tau^*$
are bit-identical and the two families are paired by seed rather than only in
distribution. The noise draws come from a generator spawned separately from the
covariate one, so the two-draws-per-step invariant above is untouched.

Two published readings depend on which family is used, and both are reported
with the family named. The high-magnitude sign change of $A/A_{\mathrm{rect}}$
exists only on the boundary-shift family. The miss rate of an external CUSUM at
$\lambda = 50$ is $0.99$--$1.00$ at every boundary-shift magnitude and
$0.33$--$0.77$ under rotation at $\eta = 0.05$: the blind spot persists on a
balanced generator with a non-zero Bayes error, and is markedly less extreme
there than on the family the published figures use.
>>>>>>> REPLACE
~~~~~~~~~

The assembly must decide which family is of record. S8 delivers the measurement and takes no
editorial position: R2, R6 and R7 are published on the boundary-shift family and are not
regenerated by this stream.

---

## H. S8-H — the closed-loop statement is true on the budget and false on the erasure time

`framework_v2.tex` states, immediately after `def:blindspot`, that the definition *"supersedes any
condition coupling an ADWIN clock to a CUSUM threshold"*. T8.3 tests exactly that on nine pipelines
and finds it **true in the form the definition uses and false in the form the prose invites**.

- At matched evidence budget `A`, the miss-rate curves collapse: in the one A-bin whose outcome is
  not saturated, the miss rate is monotone in the median `A` across all four mechanisms measured
  there (`DDM` 54.3 → 0.375, `ADWIN` 43.4 → 0.727, `KSWIN` 38.8 → 0.714, `PageHinkley` 35.1 →
  0.954).
- At matched **erasure time**, they do not. `ARF_DDM` erases at `Delta_e = 0.327` over `836` steps
  against `ARF_ADWIN`'s `808` — within `3.4 %` — and leaves `A = 75.4` against `43.9`. The first is
  never missed at `lambda = 50`; the second is missed 77 times in 100. Six such cells across `DDM`
  and `EDDM`.

~~~~~~~~~
docs/manuscript/sections/framework_v2.tex
<<<<<<< SEARCH
Definition~\ref{def:blindspot} compares two quantities in the same unit and
contains no implementation constant. It supersedes any condition coupling an
ADWIN clock to a CUSUM threshold.
=======
Definition~\ref{def:blindspot} compares two quantities in the same unit and
contains no implementation constant. It supersedes any condition coupling an
ADWIN clock to a CUSUM threshold.

\begin{empresult}[The budget is the sufficient statistic; the erasure time is
not]\label{res:budget_sufficient}
  Nine pipelines --- an ARF driven by each of ADWIN, DDM, EDDM, PageHinkley and
  KSWIN, plus SRP, leveraging bagging, ADWIN bagging and a Hoeffding adaptive
  tree --- were run over six magnitudes with the external monitor calibrated to
  one false alarm per warm-up \emph{per pipeline}. Grouped by $A$, the miss-rate
  curves collapse: in the single budget band whose outcome is not saturated at
  $0$ or $1$, the miss rate is monotone in the band's median $A$ across every
  mechanism present. Grouped by $\tau_{\mathrm{erase}}$ they do not. At
  $\Delta e = 0.327$ the DDM-driven forest erases over $836$ steps against the
  ADWIN-driven forest's $808$ --- within $3.4\%$ --- and leaves $A = 75.4$
  against $43.9$; at $\lambda = 50$ the first is never missed in $30$ runs and
  the second is missed in $77\%$ of $30$. Erasing over the same window does not
  mean leaving the same evidence, and only the second decides.
\end{empresult}

The blind spot is therefore a statement about the budget, not about the
mechanism and not about the erasure time. The internal detector enters only
through the $A$ it leaves, which is what makes
Definition~\ref{def:blindspot} implementation-free rather than merely
implementation-agnostic.
>>>>>>> REPLACE
~~~~~~~~~

---

## I. S8-I — the two quantities `dependence_v2.tex` names as unmeasured are measured

The closing paragraph of `sec:dep_mcrit` names them and refuses to approximate them. T8.3-bis
measures both.

~~~~~~~~~
docs/manuscript/sections/dependence_v2.tex
<<<<<<< SEARCH
Two quantities remain unmeasured and are named rather than estimated: the member marginal $F$
itself, and the false-alarm-budget-equalised form of the Hydra factor, which would require
recording the per-step pre-drift error stream of a single tree standalone and inside the ensemble.
Neither is approximated here.
=======
Both quantities named here as unmeasured have since been measured, by recording the per-step
pre-drift error stream of each member inside the ensemble alongside the standalone arm, over $100$
seeds at the two canonical anchors.

The member marginal and the standalone arm share a \emph{rate} and differ by averaging. One member
of the $M=10$ forest errs on $0.0912 \pm 0.0288$ of the pre-drift window against $0.0895$ for the
standalone $M=1$ arm --- a gap of $0.0017$ against a between-tree standard deviation of $0.0288$ ---
while the ensemble errs on $0.0240$. The measured per-step variance ratio is $3.51$, and the
one-false-alarm-per-warm-up threshold it buys is $\lambda_{\mathrm{eq}} = 2.45$ for the ensemble
against $6.84$ for the single tree. Emp.~Res.~\ref{res:plugin_refuted} refutes the substitution
through the tails; this locates the difference in the dispersion rather than in the level.

The equalised form of the Hydra factor is then a decomposition, not a number. Writing
$R = \lambda + \sqrt{(W/2)\ln(1/\varepsilon)}$ for the requirement and $A$ for the measured
ceiling, $\log(A/R)$ is additive, so the $M=1$ against $M=10$ contrast splits exactly into an
ensemble-size part $\log(A_1/A_{10})$ and a threshold part $-\log(R_1/R_{10})$. The split is
magnitude-dependent and is published as such: the threshold carries $9.5\%$ of the contrast at
$\Delta e = 0.141$ and $76.5\%$ at $\Delta e = 0.327$. No single equalised factor is quoted, because
either value would be false at the other anchor.
>>>>>>> REPLACE
~~~~~~~~~

The arm paired against the ensemble is ARF($M = 1$), the object the `4.12x` / `7.99x` anchors are
measured on, **not** a HAT — charge S8-E. The wording above says "the standalone $M=1$ arm" rather
than "the HAT" for that reason, and the assembly must make the surrounding text agree.
