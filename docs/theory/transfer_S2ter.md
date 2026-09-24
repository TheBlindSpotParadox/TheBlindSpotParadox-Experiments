# Transfer document — stream S2-ter (the blind-spot predicate, the windowed requirement, the symbol `W`, contribution (C4))

Parent `19b9bde`, branch `stream-s2ter`. Decision rules E0–E4 fixed before any computation in
[`docs/prompts/s2ter-decision-rules.md`](../prompts/s2ter-decision-rules.md) (`7084027`).
Report: [`S2ter_blindspot_predicate.md`](S2ter_blindspot_predicate.md).

**Applied by this stream, and only this:** the T3 relabel of `tau_swap^(1/M) = 57.4` used in place
of `W`, in the four artifacts the mandate names (`6d4c703`). Every payload below is **unapplied**.
Anchors are verbatim text, never line numbers; `tests/test_S2ter_predicate.py` asserts that each
resolves exactly once in its target, overlaps no pending S8 or S9 anchor, and that none lands in
the four inline subsections `CLAUDE.md` excludes.

| charge | lands on | target | status |
|---|---|---|---|
| **S2ter-A** | T1: the arbitration and its gate | — | charge, no payload: (a) argued, **NOT RETAINED** by rule E1 |
| **S2ter-B** | S9-F's "the condition that governs detection" | `transfer_S9.md` S9-F, pending | charge with replacement text; no anchor exists in the tree yet |
| **S2ter-C** | T2: the windowed requirement in amplitude | `sections/framework_v2.tex` | payload, before `cor:split` |
| **S2ter-D** | `rem:split_measured`, what the relabel implies | `sections/framework_v2.tex` | payload |
| **S2ter-E** | `rem:floor_band`, what the relabel implies | `sections/framework_v2.tex` | payload |
| **S2ter-F** | (C4), the contribution | `docs/editorial/thesis_v4.md` | payload; supersedes S9-G |
| **S2ter-G** | (C4), "Tenable with" | `docs/editorial/thesis_v4.md` | payload |
| **S2ter-H** | (C4), the rationale | `docs/editorial/thesis_v4.md` | payload |
| **S2ter-I** | the family ordering, with `p_0` as a column | `articleA_blindspot_v64_camera_ready.tex`, `sec:discussion` | payload, outside the excluded zone |
| **S2ter-J** | carriers of `W = 57.4` outside the perimeter | code, artifacts, documents | charge, no payload |
| **S2ter-K** | requirement margins read at `W` | S1 / S2 theory | charge, escalation |
| **S2ter-L** | S9-A and S9-G | `transfer_S9.md` | record of supersession |

---

## A. S2ter-A — T1, the arbitration, not retained

Part B of the rules argues **(a) GENERALISATION**: one predicate, `A_{m_D} < R(D, eps, alpha)`,
on the budget readable within the monitor's memory `m_D`, which reduces to `def:blindspot` verbatim
for `m_D = infinity` (CUSUM, PHT, ADWIN) and to S9's contrast model identically for KSWIN
(`m_D = n_stat`). The split (b) is not retained on structure: the only assignment criterion that
places ADWIN correctly is `m_D` itself, and with it (b) is (a) restricted to two values.

Rule E1 then refused it. The generalised and the contrast predicates coincide on all 3 960 cells, so
the relative condition holds on each grid, but the pooled agreement is `3673/3960 = 0.9275`, under
the threshold `715/768 = 0.9310` that S9 publishes as `0.931`. The deficit is on the two
classifier-driven grids: `62/80` canonical and `36/40` rotation. **NOT RETAINED**, terminal:
(b) is not substituted, since its windowed predicate is the same and fails identically.

Consequences for the assembly:

- no payload installs `A_{m_D}` or a generalised `def:blindspot`. `def:blindspot` stays as written,
  and S9-F's contrast condition enters, if it does, with the scope S2ter-B gives it;
- what would decide T1, each to be pre-registered by the stream that takes it, neither computed
  here: (i) a `(1 - eps)` margin for the windowed family derived on the `n_stat` scale, not fitted
  (the Hoeffding term `sqrt(n_stat ln(1/eps))` of Part C is the one derived candidate stated); (ii)
  the trace-level `A_{n_stat}` on the classifier-driven grids, which needs the S6 traces and a
  regeneration of the rotation traces, neither reachable from this worktree.

## B. S2ter-B — the scope of S9-F's contrast condition

S9-F (pending, `transfer_S9.md` §F) calls `eq:Rkswin_contrast` "the condition that governs
detection". That rests on the controlled-transient grid alone. On the classifier-driven grids the
condition promises every one of its 22 disagreements: a contrast statistic above `k*` by `0.08` to
`2.08` excess errors, and a detection rate of `73.5 %` to `94.95 %`, short of the `1 - eps` level.
It locates the median run, not the `(1 - eps)` requirement.

Replacement text for S9-F's REPLACE block, to be substituted when S9-F is applied. The SEARCH side
does not exist in the tree yet, so no anchor is given:

```latex
is the condition that governs detection on a controlled rectangular transient, where it agrees
with the measurement on $93.1\%$ of $3{,}840$ cells. It is a mean-field boundary: on the two
classifier-driven families it agrees on $62$ of $80$ and $36$ of $40$ cells, and every disagreement
is a detection it promises, within about two excess errors of $k^*$, that occurs in fewer than the
$1-\varepsilon$ share of runs. Two consequences separate it from~\eqref{eq:Rkswin}.
```

## C. S2ter-C — T2, the windowed requirement in amplitude

Self-contained: it does not reference S9-F's equation, so its application does not depend on S9-F.

~~~~~~~~~
docs/manuscript/sections/framework_v2.tex
<<<<<<< SEARCH
\begin{corollary}[Family split]\label{cor:split}
=======
\begin{remark}[The windowed requirement in amplitude]\label{rem:window_requirement}
  On a binary error stream the two-sample statistic of KSWIN is a difference of error counts
  between its two samples of size $n_{\mathrm{stat}}$, so a rectangular transient of height
  $\Delta e$ and length $W$ offers it at most $\Delta e \min(W, n_{\mathrm{stat}})$ excess errors
  at once. Against the exact lattice level $k^*(\alpha, n_{\mathrm{stat}})$ the windowed family
  requires, in amplitude, $\Delta e \ge k^*/\min(W, n_{\mathrm{stat}})$, while~\eqref{eq:Rkswin}
  read on $A = (\Delta e - \delta_P) W$ requires
  $\Delta e \ge \delta_P + \bigl[\sqrt{n_{\mathrm{stat}} \ln(2/\alpha)}
  + \sqrt{(W/2)\ln(1/\varepsilon)}\bigr]/W$. For $W \le n_{\mathrm{stat}}$ both scale as $1/W$
  and~\eqref{eq:Rkswin} is the stricter. For $W > n_{\mathrm{stat}}$ the first saturates at the
  lattice distance $k^*/n_{\mathrm{stat}}$ while the second keeps falling toward $\delta_P$; they
  cross at $W_\times = \bigl[(b + \sqrt{b^2 + 4 c R_{\mathrm{fa}}})/(2c)\bigr]^2$, with
  $b = \sqrt{\ln(1/\varepsilon)/2}$, $c = k^*/n_{\mathrm{stat}} - \delta_P$ and
  $R_{\mathrm{fa}} = \sqrt{n_{\mathrm{stat}}\ln(2/\alpha)}$, which is $47.3$ at the deployed
  $(\alpha, n_{\mathrm{stat}}) = (0.005, 30)$. Past $W_\times$,~\eqref{eq:Rkswin} promises the
  detection of amplitudes below $k^*/n_{\mathrm{stat}}$, which no transient length makes
  detectable. Over the $3{,}840$ cells of a controlled-transient grid its errors follow these
  frontiers away from the threshold: all $91$ of its errors with $W \le n_{\mathrm{stat}}$ forbid a
  detection that occurs, all $478$ with $W \ge W_\times$ promise one that does not, and between
  the two $7$ of $8$ are broken promises, because near the threshold the rate observed at level
  $1 - \varepsilon$ sits above the mean-field boundary both conditions use. On the two
  classifier-driven families that boundary agrees with the observation on $62$ of $80$ and $36$ of
  $40$ cells, each disagreement a detection it promises; it locates the median run, not a
  $(1 - \varepsilon)$ requirement. Both prices of $R_{\mathrm{KSWIN}}$ are set by
  $n_{\mathrm{stat}}$: a $(1 - \varepsilon)$ guarantee at one test adds
  $\sqrt{n_{\mathrm{stat}} \ln(1/\varepsilon)}$ to the critical count and carries no $W$.
\end{remark}

\begin{corollary}[Family split]\label{cor:split}
>>>>>>> REPLACE
~~~~~~~~~

## D. S2ter-D — `rem:split_measured` at the exploitable transient

The relabel (`6d4c703`) states that `57.4` is `tau_swap^(1/M)`. It does not state what follows from
that, which rule E3 measured as **VERDICT-BEARING**. This payload adds it. It carries the whole
content of S9-A's consequence clause, extended from `R_KSWIN` to the three requirements.

~~~~~~~~~
docs/manuscript/sections/framework_v2.tex
<<<<<<< SEARCH
  it is why a detector-side resolution exists at all.
\end{remark}
=======
  it is why a detector-side resolution exists at all.

  The operating point is a lower bound on $W$: $\tau_{\mathrm{swap}}^{(1/M)} \le
  \tau_{\mathrm{erase}}$ by Proposition~\ref{prop:order}, and every $W$-slot of the table,
  $\alpha = W/\mathrm{ARL}_0$ included, is read there. At the exploitable transient itself,
  $W = 611.9$ by the argmax of $A_{\mathrm{unrefl}}$ and $W = 1{,}995.5$ by the last crossing of
  Definition~\ref{def:times}, none of the three requirements is met at any $\lambda$ of the table,
  and $R_{\mathrm{KSWIN}}$ at the deployed $\alpha = 0.005$ rises from $22.7$ to $43.7$ and $68.1$.
  At the same point the cumulative monitor at $\lambda = 15$ detects every run within $W$: read at
  $W$, the margin $\sqrt{(W/2)\ln(1/\varepsilon)}$ that~\eqref{eq:Rcusum} to~\eqref{eq:Rkswin}
  share makes them too loose to decide the blind spot, and the table above holds at the first-swap
  horizon only.
\end{remark}
>>>>>>> REPLACE
~~~~~~~~~

## E. S2ter-E — `rem:floor_band` at the exploitable transient

~~~~~~~~~
docs/manuscript/sections/framework_v2.tex
<<<<<<< SEARCH
  as that interval, never as its midpoint.
\end{remark}
=======
  as that interval, never as its midpoint.

  The interval is evaluated at $\tau_{\mathrm{swap}}^{(1/M)}$, a lower bound on $W$, through both
  $\alpha = W/\mathrm{ARL}_0$ and the term $-W\delta_P$. At the exploitable transient it is
  $[7.1,\, 11.8]$ for $W = 611.9$ (argmax of $A_{\mathrm{unrefl}}$) and $[-7.3,\, -2.5]$, vacuous,
  for $W = 1{,}995.5$ (Definition~\ref{def:times}): the floor weakens as $W$ grows, because the
  tolerance $\delta_P$ is charged on every step of the window.
\end{remark}
>>>>>>> REPLACE
~~~~~~~~~

## F. S2ter-F — contribution (C4), rewritten

`thesis_v4.md` §T11a.4 states (C4) on a scaling law, "square-root for the other two", and on
`cor:split`'s crossings. S9 refuted the first as the governing condition of KSWIN (D2), and rule E3
places the crossings at a lower bound on `W`. The replacement carries the measured matrix with `p_0`
as a coordinate. It honours the three measured constraints of the mandate: equalisation lowers KSWIN
and raises ADWIN, both at zero pre-change alarms; EDDM's rank is a function of `p_0`; the ordering
table carries `p_0` as a column (S2ter-I). It supersedes S9-G, whose third-class statement it
includes.

~~~~~~~~~
docs/editorial/thesis_v4.md
<<<<<<< SEARCH
  \item \textbf{An ordering of monitor families, and the level at which it reverses.} We order
  cumulative, windowed and distributional monitors by the evidence each requires at a
  \emph{common} false-alarm level, show that the ordering follows a scaling law rather than a
  taxonomy---linear in $\ln(1/\alpha)$ for the cumulative monitor, square-root for the other
  two---and locate the crossings. The threshold this paper recommends lies on the side where the
  cumulative monitor is the cheaper of the three (Section~\ref{sec:related} and
  Section~\ref{sec:discussion}).
=======
  \item \textbf{An ordering of monitor families, indexed by the stream.} We compare cumulative,
  adaptive-window and fixed-window two-sample monitors on the error stream at their deployed
  levels and at a common false-alarm level, on two streams whose pre-change error rate $p_0$ is
  not zero. Equalising the level lowers the fixed-window two-sample monitor (KSWIN, $0.458 \to
  0.337$ of runs detected) and raises the adaptive-window one (ADWIN, $0.885 \to 0.926$, median
  delay $28 \to 15$ steps), both at zero pre-change alarms: the deployed comparison orders
  calibrations, not families. EDDM has no rank of its own---it never arms at $p_0 = 0$, is first
  at $p_0 = 0.024$ ($0.974$ detected, $0.020$ pre-change alarms) and last at $p_0 = 0.069$
  ($0.022$ detected, $0.930$)---so the ordering is a table with $p_0$ as a column
  (Table~\ref{tab:family_order}), not a ranking. A monitor on the input distribution does not
  enter it: on a change of $P(Y \mid X)$ at fixed $P(X)$ it does not see the drift
  (Section~\ref{sec:related} and Section~\ref{sec:discussion}).
>>>>>>> REPLACE
~~~~~~~~~

## G. S2ter-G — (C4), what carries it

~~~~~~~~~
docs/editorial/thesis_v4.md
<<<<<<< SEARCH
- **(C4)** — `framework_v2.tex` `cor:split` and `rem:split_measured`;
  `results/S2bis_calibration/tables/s2bis_proteus_gate.json :: cor_split_crossings` (KSWIN at
  `ln(1/α) = 16.34`, `λ = 22.605`; ADWIN at `18.97`, `λ = 26.466`; CUSUM slope `1.468 = 1/θ*`);
  `envelope_stats.json` for `λ_op = 21.93 [19.876, 22.398]`, which lies entirely below the KSWIN
  crossing.
=======
- **(C4)** — `results/S9_detector_coverage/tables/s9_family_ordering.json` (`p_0 = 0.024`) and
  `s9_family_ordering_rotation.json` (`p_0 = 0.069`), grid means over 20 magnitudes of 100 runs,
  raw error stream, arm `full`; `s2bis_proteus_gate.json :: eddm_arming_T_D` (`p_0 = 0`, EDDM never
  armed, `0/1080`); verdicts D5 = LOST, D7 = HOLDS, D8 = NOT PRODUCED and D9 = ARMED-COLUMN in
  `docs/theory/S9_detector_coverage.md`. The equalised levels are those of
  `s2bis_proteus_gate.json`, derived with `tau_swap^(1/M) = 57.4` in place of `W`. Every numeral
  reproduced by rule E4 of `docs/prompts/s2ter-decision-rules.md`.
>>>>>>> REPLACE
~~~~~~~~~

## H. S2ter-H — (C4), why it was rewritten

~~~~~~~~~
docs/editorial/thesis_v4.md
<<<<<<< SEARCH
**Decision: reformulate.** S9 exists as a prompt and nothing else. `git log --all` shows no
branch, `results/` no directory, `docs/theory/` no transfer. An arm that is not delivered cannot
carry a contribution.

The reformulation is not a retreat to a weaker claim; it moves (C4) onto a result that is derived
and instantiated rather than promised. `cor:split` derives the ordering from a scaling law, and
`rem:split_measured` instantiates it at the measured operating point with a crossing point. That
is strictly more than the v2 (C4) offered, which ordered three families by exposure and stated a
cost per family without a number.

The input-space promise descends to future work and is declared there with its structural cost,
which the paper already states: `related_work_v2.tex` L92-95 records that an input-space monitor is
blind to a change in `P(Y|X)` at fixed `P(X)`, and the controlled generator of this paper moves the
decision boundary at fixed `P(X)`. The arm would therefore be blind to the drift the paper studies
by construction. Declaring that is a result about the design space, and it is the honest form of
the sentence at `related_work_v2.tex` L97-99 — *which is why we evaluate an input-space arm
alongside the error-stream arms* — which currently promises an experiment the repository does not
contain. That sentence is in the register.
=======
**Decision: rewrite.** The version above rested on `cor:split`'s crossings, read at
`tau_swap^(1/M) = 57.4` in place of `W`, and on `eq:Rkswin` as KSWIN's governing condition. S9
refuted the second (D2). S2-ter traced the first to a lower bound on `W`: at the exploitable
transient no requirement of the ladder is met at any `lambda` (rule E3). The crossings therefore
cannot carry the contribution.

What carries it is measured: S9's family matrix at the deployed and at a common false-alarm level,
on two streams whose null is not degenerate, with `p_0` as a column, because the one family whose
rank inverts between the two, EDDM, inverts with `p_0`. The input-space class is the third row and a
result about the design space: S9 measured the instrument sensitive to a covariate shift and blind,
by construction of both generators, to the drift this paper studies (D8, NOT PRODUCED). That
replaces the promise of `related_work_v2.tex` L97-99.
>>>>>>> REPLACE
~~~~~~~~~

## I. S2ter-I — the family ordering, with `p_0` as a column

`sec:discussion` of the live manuscript lies outside the four excluded subsections. The rows are
generated by `tests/test_S2ter_predicate.py::family_table_latex` from the committed artifacts, and
the test asserts that this block contains them verbatim.

~~~~~~~~~
docs/manuscript/articleA_blindspot_v64_camera_ready.tex
<<<<<<< SEARCH
\section{Discussion}\label{sec:discussion}
=======
\section{Discussion}\label{sec:discussion}

\begin{table*}[t]
  \centering
  \small
  \caption{Monitor families on the error stream at their deployed and equalised false-alarm
  levels, indexed by the pre-change error rate $p_0$ of the stream. Detection inside the
  exploitable transient and the pre-change alarm rate are means over $20$ magnitudes of $100$
  runs on the raw error stream; the delay is the median over magnitudes of the per-magnitude
  median. The equalised levels place ADWIN and KSWIN at the requirement of a CUSUM at
  $\lambda = 15$, derived with $\tau_{\mathrm{swap}}^{(1/M)} = 57.4$ in place of $W$; at the
  exploitable transient itself no ADWIN level in $(0, 1]$ matches that requirement. At $p_0 = 0$
  the null is degenerate and no false-alarm level is defined; only EDDM's arming state is reported
  there. EDDM carries its arming rate and median arming instant beside its delay.}
  \label{tab:family_order}
  \begin{tabular}{llrlrrr}
    \toprule
    family & setting & $p_0$ & armed & pre-change alarms & detected in $W$ & median delay \\
    \midrule
    EDDM & published & $0.000$ & never, $0/1080$ & --- & $0.000$ & --- \\
    \midrule
    StrictCUSUM, $\lambda = 15$ & published & $0.024$ & --- & $0.000$ & $0.928$ & $35.0$ \\
    StrictCUSUM, $\lambda = 50$ & published & $0.024$ & --- & $0.000$ & $0.001$ & $1089.0$ \\
    PHT, $\lambda = 15$ & published & $0.024$ & --- & $0.000$ & $0.928$ & $33.5$ \\
    PHT, $\lambda = 50$ & published & $0.024$ & --- & $0.000$ & $0.000$ & --- \\
    ADWIN & published & $0.024$ & --- & $0.000$ & $0.885$ & $28.0$ \\
    ADWIN & equalised & $0.024$ & --- & $0.000$ & $0.926$ & $15.0$ \\
    KSWIN & published & $0.024$ & --- & $0.000$ & $0.458$ & $27.0$ \\
    KSWIN & equalised & $0.024$ & --- & $0.000$ & $0.337$ & $28.0$ \\
    EDDM & published & $0.024$ & $1.000$ at $t_{\mathrm{rel}} = +16$ & $0.020$ & $0.974$ & $17.5$ \\
    \midrule
    StrictCUSUM, $\lambda = 15$ & published & $0.069$ & --- & $0.000$ & $0.958$ & $31.5$ \\
    StrictCUSUM, $\lambda = 50$ & published & $0.069$ & --- & $0.000$ & $0.448$ & $440.0$ \\
    PHT, $\lambda = 15$ & published & $0.069$ & --- & $0.030$ & $0.942$ & $28.0$ \\
    PHT, $\lambda = 50$ & published & $0.069$ & --- & $0.000$ & $0.090$ & $391.0$ \\
    ADWIN & published & $0.069$ & --- & $0.000$ & $0.891$ & $32.0$ \\
    ADWIN & equalised & $0.069$ & --- & $0.000$ & $0.933$ & $18.5$ \\
    KSWIN & published & $0.069$ & --- & $0.000$ & $0.572$ & $27.2$ \\
    KSWIN & equalised & $0.069$ & --- & $0.000$ & $0.478$ & $28.8$ \\
    EDDM & published & $0.069$ & $1.000$ at $t_{\mathrm{rel}} = -554$ & $0.930$ & $0.022$ & $40.0$ \\
    \bottomrule
  \end{tabular}
\end{table*}
>>>>>>> REPLACE
~~~~~~~~~

## J. S2ter-J — carriers of `W = 57.4` outside the perimeter

The census of rule A.4, charged and not edited. The orchestrator restricted T3 to the four named
artifacts; stream S10 runs in parallel on the SSOT and the S9 code.

| site | change owed |
|---|---|
| `results/S2_theory/tables/s2_gate_T20.json` `eps_sensitivity.at.W`, `floor_and_family.at.W`; generator `experiments/S2_theory/s2_arl0.py:336,352` | emit `"tau_swap_1_over_M": 57.4` and `"W_alias_of": "tau_swap_1_over_M"` beside `W`, then regenerate. This artifact is the source of `rem:split_measured`'s ladder and of the floor band `[13.88, 18.29]`, so it is the carrier that matters most |
| `experiments/S2bis_calibration/s2bis_proteus_calibration.py:311,352,368,390,600` | emit the same two keys in `family_requirements()["at"]` and `cor_split_crossings()["at"]`. The committed JSON already carries them and the generator does not: **declared debt**. A re-run drops them without moving a numeral, and `test_gate_json_labels_the_first_swap_time_beside_its_W_alias` fails |
| `docs/theory/S2bis_narrative_payload.md:20,227` | L20: `` `W = 57.4` `` → `` `tau_swap^(1/M) = 57.4` in place of `W` ``; L227, in the LaTeX quote: `$(W = 57.4, p_0 = \PzeroMeas)$` → `$(\tau_{\mathrm{swap}}^{(1/M)} = 57.4$ in place of $W$, $p_0 = \PzeroMeas)$` |
| `config/experiment_ssot.py:536,541,566` | rename `S9_W_TRANSIENT_REF` → `S9_TAU_SWAP_REF`, value unchanged; L536 "the exploitable transient is 57.4" → "`tau_swap^(1/M) = 57.4` is a lower bound on `W`"; L541 "the measured transient W = 57.4" → "`tau_swap^(1/M) = 57.4`"; update the users `s9_offline_detectors.py` and `tests/test_S9_coverage.py` |
| `experiments/S9_detector_coverage/s9_offline_detectors.py:121,151`; `s9_requirement_lattice{,_smoke}.json` | key `W_used_for_margin` → `tau_swap_1_over_M_used_for_margin`, or the alias pattern |
| `experiments/S9_detector_coverage/s9_family_ordering.py:17,232,276`; `s9_family_ordering{,_rotation,_smoke}.json` | "(W = 57.4, ...)" → "(tau_swap^(1/M) = 57.4 in place of W, ...)"; `levels.anchor` is copied from the gate, so a re-run inherits the new keys |
| `docs/plans/PLAN_S9.md:54` | plan of record: an erratum line, as for the gate |
| `articleA_blindspot_v64_camera_ready.tex:481` | `$W_0$`, ADWIN's older sub-window (acception 7), in a section that also uses `W` (acception 1): keep the subscript and say "ADWIN's reference sub-window" if the sentence survives the assembly |

## K. S2ter-K — escalation: the requirement margins, read at `W`

Rule E3, **VERDICT-BEARING**. `s2_arl0.floor_and_family` was re-used as it stands, at the
canonical point, ceiling `33.5115`. The table gives the `met` flags for
`(R_CUSUM, R_ADWIN, R_KSWIN)` at `lambda = 8, 15, 25, 50`, and the chord floor band:

| reading of the `W` slot | `met` at `lambda = 8, 15, 25, 50` | `R_KSWIN(0.005)` | chord floor band |
|---|---|---|---|
| `tau_swap^(1/M) = 57.4` (published) | all / all / KSWIN / none | `22.68`, met | `[13.88, 18.29]` |
| `W_argmax = 611.87` | none at every `lambda` | `43.68` | `[7.11, 11.83]` |
| `W_fw = 1 995.5` | none at every `lambda` | `68.08` | `[-7.33, -2.46]`, vacuous |

At `Delta_e = 0.326793`, StrictCUSUM and PHT at `lambda = 15` detect **1.000** of runs within `W`
(`s9_family_ordering.json`). A requirement that is not met where detection is certain is a
sufficient condition too loose to decide the predicate. The margin `sqrt((W/2) ln(1/eps))` that
`eq:Rcusum`, `eq:Radwin` and `eq:Rkswin` share is charged over the whole transient, and at `W_fw`
it alone (`54.7`) exceeds the ceiling. The published numerals were in range because
`tau_swap^(1/M)` stood in for `W`.

This is escalated to the theory streams, not repaired here: the margin should be charged over the
window the statistic actually reads. Part C of the rules gives the windowed case, `n_stat`.

The equalised ADWIN level of S9 D5, `4 W exp(-2 lambda^2 / W)` at `lambda = 15`, is `0.0904` at
`57.4`, `1 173` at `611.87` and `6 371` at `1 995.5`. At the exploitable transient no ADWIN level in
`(0, 1]` equalises the CUSUM's requirement, so "equalised" in S9's matrix and in S2ter-I means
equalised at the first-swap horizon, and the table caption says so.

## L. S2ter-L — supersessions

- **S9-A** (`transfer_S9.md` §A). Its label is applied by `6d4c703`, with a scope wider than S9-A's
  own wording: `57.4` fills every `W` slot of the remark, not only the `eps` margin. Its
  consequence clause is carried, extended to the three requirements, by S2ter-D.
  `tests/test_S9_coverage.py` accepts the S9-A anchor only while the relabelled line stands exactly
  once in `framework_v2.tex`.
- **S9-G** (`transfer_S9.md` §G, `intro_v2.tex`). Superseded by S2ter-F. The assembly applies one
  (C4), and S2ter-F includes S9-G's third-class statement.

## What is deliberately not charged

- `thm:floor`, `eq:floor_chord` and `cor:split`'s `alpha`-price statements. Rule E3 moves the
  *evaluation* of the floor; it does not touch the bound.
- A replacement for `def:blindspot`. T1 is NOT RETAINED; S2ter-A names what would decide it.
- `prop3_v2.tex:41`, which names `tau_swap^(1/M)` as a reading of `W` in its own column and is not
  a carrier (rule A.3).
