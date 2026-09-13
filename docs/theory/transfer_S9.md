# Transfer document — stream S9 (detector coverage, the KSWIN failure region, the input-space arm)

Parent `346fe89`, branch `stream-s9`. Decision rules D0–D10 fixed before any measurement in
[`docs/prompts/s9-decision-rules.md`](../prompts/s9-decision-rules.md) (`581b232`). Measurement
report: [`S9_detector_coverage.md`](S9_detector_coverage.md).

**Nothing below is applied.** Every charge is delivered as a SEARCH/REPLACE payload with a verbatim
anchor and a named target file, or as a charge with no payload where no v2 home exists.

Routing rule, from `CLAUDE.md`. `sec:race` (L195), `sec:hydra` (L212), `sec:starvation` (L237) and
`sec:decoupling` (L410) of `articleA_blindspot_v64_camera_ready.tex` are superseded by
`docs/manuscript/sections/framework_v2.tex` and **must not be patched**. Charges landing inside one
of the four are routed to the `sections/` fragment. Verified by subsection boundary, not by eye:
`.tex:500` falls in `sec:proteus` (457–501) and is patchable in place; `.tex:306` falls in
`sec:starvation` (237–322) and is not.

| charge | lands on | target | status |
|---|---|---|---|
| **S9-A** | `rem:split_measured`, the symbol `W` | `sections/framework_v2.tex` | payload — reattribution, not a numeral fix |
| **S9-B** | `cor:split` discussion, KSWIN's scope | `sections/framework_v2.tex` | payload, **routed** from `rem:agnostic` (.tex:306) |
| **S9-C** | `.tex:500`, the immunity claim | `articleA_blindspot_v64_camera_ready.tex` | payload, outside the excluded zone |
| **S9-D** | `.tex:55`, the `\LambdaFA` comment | `articleA_blindspot_v64_camera_ready.tex` | payload, one comment line |
| **S9-E** | `.tex:115`, the abstract's KSWIN sentence | `articleA_blindspot_v64_camera_ready.tex` | payload |
| **S9-F** | `eq:Rkswin`, the governing condition | `sections/framework_v2.tex` | payload — adds the contrast requirement beside it |
| **S9-G** | (C4), the third exposure class | `sections/intro_v2.tex` | payload |
| **S9-H** | the EDDM paragraph | `sections/framework_v2.tex` | payload, D9's arming column |
| **S9-I** | B2's refutation | S1/S2 | **charge, no payload** — escalation, §I |

---

## A. S9-A — the symbol `W` in `rem:split_measured`

`W = 57.4` is `tau_swap^(1/M)`, the mean first-swap time (`prop3_v2.tex:41`,
`S6_causal_evidence.md:199`; re-measured at `57.38`). It is **not** `W := tau_erase - tau*` of
`def:times`, which is what the `eps` term of every requirement is defined over and which measures
`1 995.5` at the same operating point. At `def:times`' own `W`, `R_KSWIN` is `68.08` rather than
`22.68` and the measured ceiling `33.5115` stops meeting it. The numeral reproduces; the label does
not. This is a reattribution and it changes a verdict.

~~~~~~~~~
docs/manuscript/sections/framework_v2.tex
<<<<<<< SEARCH
\begin{remark}[The split, at the measured operating point]\label{rem:split_measured}
  At $\Delta e = 0.3268$, $W = 57.4$, $\varepsilon = 0.05$,
=======
\begin{remark}[The split, at the measured operating point]\label{rem:split_measured}
  At $\Delta e = 0.3268$, $\varepsilon = 0.05$,
  $\tau_{\mathrm{swap}}^{(1/M)} = 57.4$ used in place of $W$ in the
  $\varepsilon$ margin---the substitution is deliberate and is stated because
  the two differ by a factor of $35$ here: the exploitable transient of
  Definition~\ref{def:times} measures $W = 1{,}995.5$ at this operating point,
  at which $R_{\mathrm{KSWIN}} = 68.1$ and the measured ceiling $33.5$ no
  longer meets it---
>>>>>>> REPLACE
~~~~~~~~~

## B. S9-B — KSWIN's scope, routed out of `rem:agnostic`

`rem:agnostic` (.tex:306) asserts KSWIN is *"immune to starvation while its reference window holds
pre-drift data"*. S9 instantiated the subordinate clause and it does **not** bind: detection rises
with the transient and then plateaus, and never falls past `W_win - n_stat` (rule D4, **ABSENT**).
A long transient gives KSWIN its test opportunities early, while the reservoir is still clean. The
clause is withdrawn rather than restated in a weaker form; what replaces it is the measured
condition of S9-F. `.tex:306` is inside `sec:starvation`, so the charge lands here.

~~~~~~~~~
docs/manuscript/sections/framework_v2.tex
<<<<<<< SEARCH
operative axis is $\alpha$, which the practitioner sets, rather than $W$, which
the classifier does.
=======
operative axis is $\alpha$, which the practitioner sets, rather than $W$, which
the classifier does.

Neither statement makes $R_{\mathrm{KSWIN}}$ a sufficient condition. Measured
over a controlled-transient grid of $192{,}000$ runs, the sign of
$A - R_{\mathrm{KSWIN}}$ predicts detection on $85.0\%$ of cells against
$93.1\%$ for the contrast condition of~\eqref{eq:Rkswin_contrast}, and the
deficit is concentrated where the transient outlasts the window that reads it:
$79.8\%$ for $W \ge n_{\mathrm{stat}}$ and $73.0\%$ for
$W > W_{\mathrm{win}} - n_{\mathrm{stat}}$. The reservoir-contamination regime
is not a failure regime: the alarm rate rises with $W$ and then plateaus,
because a long transient is tested early, while the reference window is still
clean.
>>>>>>> REPLACE
~~~~~~~~~

## C. S9-C — the immunity claim at `.tex:500`

Three claims in one paragraph, each contradicted by measurement on a stream with a non-degenerate
null: *"structurally immune to transient signal erasure"*, *"hyper-parameter robust"* and *"without
false-alarm flooding"*. On the canonical Bernoulli family KSWIN detects `0.458` of runs at the
deployed `alpha` against `0.928` for the PHT it is said to resolve; the `alpha` sweep moves
detection by a factor of `23` at the canonical operating point; and on the smoothing convention R4
actually deploys, the pre-drift false-alarm rate is `1.000` at every `alpha`, on three independent
streams.

~~~~~~~~~
docs/manuscript/articleA_blindspot_v64_camera_ready.tex
<<<<<<< SEARCH
KSWIN evaluates a \emph{distributional divergence} (Kolmogorov-Smirnov distance) between sliding windows rather than accumulating continuous binary evidence, rendering it structurally immune to transient signal erasure. The measured ADD${=}14$ stems entirely from the smoothing window's structural lag ($W/2=15$), yielding a lag-corrected true delay of $[0]$. Crucially, this resolution is hyper-parameter robust: an $\alpha$-sensitivity sweep ($\alpha \in [0.001, 0.05]$) maintains F1${=}1.00$ uniformly across all GARCH regimes without false-alarm flooding.
=======
KSWIN evaluates a \emph{distributional divergence} (Kolmogorov-Smirnov distance) between sliding windows rather than accumulating continuous binary evidence. The measured ADD${=}14$ stems from the smoothing buffer's lag ($W_{\mathrm{buf}}/2=15$, not $W/2$ of Definition~\ref{def:times}), yielding a lag-corrected delay of $[0]$. This result does not generalise beyond ProteuS, and the reason is the stream rather than the monitor: ProteuS carries an identically zero pre-drift error (Section~\ref{sec:limitations}), so $\Delta e = 1$, no false alarm is possible, and the operating point sits an order of magnitude above $R_{\mathrm{KSWIN}}$---which is why the $\alpha$ sweep is flat. On the instrumented Bernoulli family, where the null is not degenerate, the same monitor at the same settings detects $45.8\%$ of runs against $92.8\%$ for PHT at $\lambda{=}15$, its detection moves from $3\%$ to $69\%$ across the same $\alpha \in [0.001, 0.05]$, and on the $W_{\mathrm{buf}}{=}30$ smoothed error stream it actually consumes it raises a pre-drift alarm in every run at every $\alpha$.
>>>>>>> REPLACE
~~~~~~~~~

## D. S9-D — the `\LambdaFA` comment

The body phrase *"calibrated on ProteuS pre-drift volatility"* that S2-bis refuted is **absent from
v64**; `PROMPT_S9.md` attacks it at `.tex L362`, a v63 line number. What survives is this trailing
comment, and the footnote at `.tex:505` already states the opposite. One comment line, corrected so
an index or a later reader does not reinstate the claim from it.

~~~~~~~~~
docs/manuscript/articleA_blindspot_v64_camera_ready.tex
<<<<<<< SEARCH
\newcommand{\LambdaFA}{15}                   % R4\_PHT\_LAMBDA, ProteuS pre-drift calibration
=======
\newcommand{\LambdaFA}{15}                   % R4\_PHT\_LAMBDA. FIXED operating threshold, NOT a
                                             % calibration: ProteuS carries an identically zero
                                             % pre-drift error, so no false-alarm budget selects
                                             % 15 or any other value. Cf. the footnote at
                                             % \ref{sec:crossover} and Section~\ref{sec:limitations}.
>>>>>>> REPLACE
~~~~~~~~~

## E. S9-E — the abstract

The abstract already hedges (*"on the settings we test---a regime-restricted observation rather than
an immunity"*), which S2-bis obtained. The hedge is no longer sufficient: on the one family where
the null is not degenerate, KSWIN is not merely unhedged, it is the **weakest** of the five monitors
measured, at equal false-alarm cost.

~~~~~~~~~
docs/manuscript/articleA_blindspot_v64_camera_ready.tex
<<<<<<< SEARCH
A distribution-based KSWIN monitor avoids the constraint on the settings we test---a regime-restricted observation rather than an immunity---recovering reliable detection at no predictive cost.
=======
A distribution-based KSWIN monitor avoids the constraint on the ARMA--GARCH stream, whose pre-drift error is identically zero; on the instrumented Bernoulli family, where a false-alarm budget binds, it is the weakest of the five monitors we measure at equal false-alarm cost, and its requirement is governed by the contrast the drift presents inside its statistic window rather than by the evidence budget the stream delivers.
>>>>>>> REPLACE
~~~~~~~~~

## F. S9-F — the condition that governs KSWIN

`eq:Rkswin` charges the whole integrated budget `A`. The monitor can only ever read
`min(W, n_stat)` steps of it, which is why its agreement with the measurement collapses exactly
where `W` exceeds `n_stat`. The contrast condition is stated beside `eq:Rkswin`, not in place of it:
`eq:Rkswin` remains the false-alarm price, and what it is compared against changes.

~~~~~~~~~
docs/manuscript/sections/framework_v2.tex
<<<<<<< SEARCH
  R_{\mathrm{KSWIN}} &= \sqrt{n_{\mathrm{stat}} \ln \tfrac{2}{\alpha}}
     + \sqrt{\tfrac{W}{2}\ln \tfrac{1}{\varepsilon}} .
     \label{eq:Rkswin}
\end{align}
=======
  R_{\mathrm{KSWIN}} &= \sqrt{n_{\mathrm{stat}} \ln \tfrac{2}{\alpha}}
     + \sqrt{\tfrac{W}{2}\ln \tfrac{1}{\varepsilon}} .
     \label{eq:Rkswin}
\end{align}

For $R_{\mathrm{CUSUM}}$ and $R_{\mathrm{ADWIN}}$ the quantity compared against
the requirement is the budget $A$ of Definition~\ref{def:budget}. For
$R_{\mathrm{KSWIN}}$ it is not, and the difference is structural rather than a
constant: a two-sample test reads a fixed window of $n_{\mathrm{stat}}$
observations, so at most $\min(W, n_{\mathrm{stat}})$ steps of the transient
are ever in evidence at once. Writing $k^*(\alpha, n_{\mathrm{stat}})$ for the
smallest integer with
$\mathbb{P}(D \ge k^*/n_{\mathrm{stat}}) \le \alpha$ under the exact
two-sample null,
\begin{equation}\label{eq:Rkswin_contrast}
  \min(W,\, n_{\mathrm{stat}})\,\Delta e \;\ge\; k^*(\alpha, n_{\mathrm{stat}})
\end{equation}
is the condition that governs detection. Two consequences separate it
from~\eqref{eq:Rkswin}. It is not monotone in the evidence budget: over the
magnitude grid of Section~\ref{sec:experiments}, $A$ falls from $24.0$ to $1.2$
while KSWIN's detection rate rises from $0$ to $1$. And $k^*$ lives on the
lattice $k/n_{\mathrm{stat}}$, so the requirement is a step function of
$\alpha$ rather than the smooth $\sqrt{n_{\mathrm{stat}}\ln(2/\alpha)}$;
at $n_{\mathrm{stat}} = 30$ the asymptotic form understates it by $4.4\%$ at
$\alpha = 0.005$, which is the level deployed.
>>>>>>> REPLACE
~~~~~~~~~

## G. S9-G — contribution (C4), third exposure class

(C4) promises an ordering of monitor families by exposure to the loop, each row carrying the cost it
pays. S9 measured all three rows. The third does not pay a detection cost — it pays a *scope* cost,
and on the generators this paper uses it cannot see the drift at all.

~~~~~~~~~
docs/manuscript/sections/intro_v2.tex
<<<<<<< SEARCH
  \item \textbf{An architectural consequence.} We order monitor families by their
  exposure to the loop---cumulative on the error stream, windowed on the error
  stream, distributional on the input space---and state the cost each pays
  (Section~\ref{sec:related} and Section~\ref{sec:discussion}).
=======
  \item \textbf{An architectural consequence.} We order monitor families by their
  exposure to the loop---cumulative on the error stream, windowed on the error
  stream, distributional on the input space---and state the cost each pays, at a
  common false-alarm level rather than at the levels each is conventionally
  deployed at, which is what separates a family from a calibration. The third
  class pays a cost of scope rather than of delay: it does not close the loop,
  and on a drift that moves $P(Y|X)$ at fixed $P(X)$ it does not see the drift
  either (Section~\ref{sec:related} and Section~\ref{sec:discussion}).
>>>>>>> REPLACE
~~~~~~~~~

## H. S9-H — the EDDM paragraph and its arming column

`framework_v2.tex` already declines to instantiate `R_EDDM` and cites the empirical collapse as
standing on its own. S9 measured that the collapse is stream-dependent in both directions, which the
current wording does not admit: never armed on ProteuS, best-in-table on the canonical family,
worst-in-table on a non-degenerate null.

~~~~~~~~~
docs/manuscript/sections/framework_v2.tex
<<<<<<< SEARCH
(Appendix~\ref{sec:prop3}); the \emph{empirical} EDDM collapse of
Section~\ref{sec:proteus} is a measurement and stands independently of any
requirement being assigned to it.
=======
(Appendix~\ref{sec:prop3}); the \emph{empirical} EDDM collapse of
Section~\ref{sec:proteus} is a measurement and stands independently of any
requirement being assigned to it. It is also not a property of the detector
alone. On the ProteuS stream EDDM never arms---its warm-up counts monitored
\emph{errors}, and the stream delivers nine in eight thousand steps---so the
$0/1080$ is a warm-up that never completed rather than an accumulation that
failed. Armed, its standing inverts with the pre-change error rate: at
$p_0 = 0.024$ it detects $97.4\%$ of runs at a $2\%$ pre-drift alarm rate, and
at $p_0 = 0.069$, armed $554$ steps before the change, it detects $2.2\%$ at a
$93\%$ pre-drift alarm rate. Any ordering that assigns EDDM a rank must carry
its arming state and its $p_0$ alongside.
>>>>>>> REPLACE
~~~~~~~~~

## I. S9-I — escalation to S1/S2, no payload

Rule D3 returned **PREDICTED-AND-ABSENT**: over 93 cells satisfying `W < n_stat` **and**
`A >= R_KSWIN` — the region where `eq:Rkswin` requires detection and this stream's dilution argument
forbade it — KSWIN detected at a mean rate of `0.9998` and missed none above `eps`. The dilution
derivation of `docs/prompts/s9-decision-rules.md` §B2 is **wrong**, and it is wrong for a stated
reason: its two boundaries coincide rather than cross, so the dilution ceiling never binds where
`eq:Rkswin` demands detection.

Per the committed rule this is a defect of S9's own theory, published as one and escalated. It does
**not** falsify `R(KSWIN)`, and the correction that does bear on `R(KSWIN)` is S9-F, which comes
from D2 and D4 rather than from D3. No payload: there is nothing in the manuscript that asserts B2.

---

## What is deliberately not charged

- **`prop:starvation` and the cumulative family.** Nothing S9 measured touches them; the
  `lambda = 50` starvation certificate reproduces on both streams (`0.001` and `0.448` detection).
- **The Hydra and race sections.** Out of scope and inside the exclusion.
- **`thm:floor` and `eq:floor_chord`.** The contrast condition of S9-F is a requirement, not a
  floor; the information-theoretic floor is untouched by it.
- **A replacement for `rem:agnostic` in v64.** The remark sits inside `sec:starvation` and the
  assembly decides whether the subsection survives at all; S9-B carries the content to the v2
  fragment and does not patch the inline copy.
