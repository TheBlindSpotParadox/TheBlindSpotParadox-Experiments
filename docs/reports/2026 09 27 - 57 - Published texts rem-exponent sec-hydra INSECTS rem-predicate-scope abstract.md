# Textes publiés — `articleA_blindspot_v65_mlj.tex`

Extraction des cinq textes demandés au prompt K7/K8 (ligne 143 : « Le texte publié de `rem:exponent`, de `sec:hydra`, du paragraphe INSECTS, de `rem:predicate_scope` et du résumé — aucun n'est dans mon contexte »).

**Source.** Version courante du manuscrit : `docs/manuscript/articleA_blindspot_v65_mlj.tex` (pointée par `docs/manuscript/CURRENT`). `rem:predicate_scope` vit dans le fragment `sections/framework_v2.tex`, inclus par `\input` à la ligne 167. Les numéros de ligne renvoient à ces deux fichiers.

---

## 1. `rem:exponent` — Remark « Exponent revision » (.tex:350–355)

```latex
\begin{remark}[Exponent revision]\label{rem:exponent}
  Over the full grid the instrumented experiments yield $\hat\alpha_{\mathrm{ARF}} \approx 0.98$ and
  $\hat\alpha_{\mathrm{HAT}} \approx 1.02$; both fits run through the noise-swap band ($\Delta e < 0.10$,
  Remark~\ref{rem:bgswap}), whose non-monotone left end flattens them toward $\mathcal{O}(1/\Delta e)$.
  Restricted to the valid domain ($\Delta e \ge 0.10$), a single power law fitted to the eighteen median
  first-replacement times gives an exponent of $-1.77$ (seed-bootstrap $95\%$ CI $[-1.90, -1.67]$), which
  excludes both $\mathcal{O}(1/\Delta e)$ and the Hoeffding bound $\mathcal{O}((\Delta e)^{-2})$. That
  interval carries the sampling noise of the medians, not the adequacy of the law, and the law does not
  describe the curve: a quadratic term in $\ln \Delta e$, fitted afterwards to the same medians, is $0.50$
  (seed-bootstrap $95\%$ CI $[0.30, 0.76]$), so the log--log slope flattens as the magnitude grows and
  $-1.77$ summarises a varying slope rather than measuring a scaling law. The slope cannot be read point
  to point: the medians of one hundred seeds move in half-steps, and across the six largest magnitudes
  they span four half-steps in all, from $31$ to $29$ steps, too few to carry a slope of their own in
  either direction. A two-piece model --- a power law up to an estimated breakpoint, a constant beyond ---
  was pre-registered against the single law and is selected by no penalised criterion (nested $F$ test,
  AIC and BIC); its parameters remain in the artifact rather than in this remark. The distance of the
  onset to the Hoeffding bound is therefore not established on this grid.
  Whether that distance would persist in the single-tree limit is open as well. The min-of-ten onset of
  Eq.~\eqref{eq:hydra} would move only the constant if the members' delays formed a scale family in the
  magnitude --- $\tau_i = K (\Delta e)^{\alpha}\xi_i$ with i.i.d.\ $\xi_i$ of a fixed law, the magnitude
  then factoring out of the minimum --- but the measured delays do not form one: the ratio of
  single-member to ensemble Kaplan--Meier medians falls from $5.32\times$ at $\Delta e = 0.14$ to
  $3.10\times$ at $\Delta e = 0.33$ (Section~\ref{sec:hydra}). The minimum can therefore move the fitted
  exponent as well, and it remains a candidate beside the warning phase, which trips earlier the stronger
  the drift, and the pre-trained background tree, whose head start grows with it. A single-tree refit was
  pre-registered to discriminate between a per-member and an ensemble origin and was run; it
  discriminates neither, the single-member median being itself not a power law over the valid domain.
  The ordering $\tau_{\mathrm{ARF}} < \tau_{\mathrm{det}}$ survives either exponent: onset acceleration
  reduces $K_{\mathrm{ARF}}$ by at least $4.1$--$8.0\times$ relative to a single tree (censoring-aware
  lower bounds, $95\%$ CIs $[3.45, 4.96]$ and $[6.40, 9.72]$; Section~\ref{sec:hydra}), compensating for
  the shared full-grid exponent.
\end{remark}
```

---

## 2. `sec:hydra` — Subsection « Ensemble Onset Acceleration » (.tex:199–218)

```latex
\subsection{Ensemble Onset Acceleration}\label{sec:hydra}

The ARF maintains $M$ trees, each equipped with an internal ADWIN detector.
Upon drift, tree $i$ detects and swaps at time $\tau_i$; the trees share one stream and one random
generator, so the $\tau_i$ are not independent (Appendix~\ref{sec:dependence}). The first replacement of
the ensemble is the first of the $M$:
\begin{equation}\label{eq:hydra}
  \tau_{\mathrm{ARF}} = \min_{1 \le i \le M} \tau_i\,,
\end{equation}
the onset of its adaptation, not its completion (Section~\ref{sec:race}).
By order statistics~\cite{david_order_2003}, were the $\tau_i$ independent with CDF $F$, the expected
minimum would be $\mathbb{E}[\tau_{(1:M)}] = \int_0^{\infty} \bigl(1 - F(t)\bigr)^M \, dt$.
The $M$-fold acceleration is exact for exponential $F$
($\mathbb{E}[\tau_{(1:M)}] = \mathbb{E}[\tau_1]/M$), and the asymptotic scaling
$\mathbb{E}[\tau_{(1:M)}] \sim 1/(M f(0))$ holds if the density $f(0)>0$. For heavy-tailed
distributions, acceleration can exceed $M$-fold, as the minimum selects aggressively from the left tail.

\textbf{Empirical validation.}
Comparing a single-member forest (an ARF with $M = 1$, whose one Hoeffding tree is replaced wholesale
when its ADWIN fires; the subscript HAT below names this arm, not the Hoeffding Adaptive Tree
of~\cite{bifet_hat_2009}, which Empirical Result~\ref{res:budget_sufficient} measures as a pipeline of
its own) against the full ARF ($M = 10$), our instrumentation reveals an onset acceleration
$\gamma_M := \mathbb{E}[\tau_{\mathrm{HAT}}] / \mathbb{E}[\tau_{\mathrm{ARF}}]$, a ratio of restricted
means of first-replacement delays, of \emph{at least} $4.12\times$ ($\Delta e = 0.14$; $95\%$ CI
$[3.45, 4.96]$) and $7.99\times$ ($\Delta e = 0.33$; $[6.40, 9.72]$), with a grid maximum of
$8.04\times$ at $\Delta e = 0.028$. Both anchors are lower bounds, not point estimates: runs whose
internal swap does not occur within the common administrative horizon $t_c = 4000$ post-drift steps are
censored, and censoring truncates the numerator only---the HAT arm loses $0$--$13\%$ of runs,
concentrated at low $\Delta e$, while the ARF arm is censoring-free at every magnitude---so the
restricted-mean ratio understates the true factor. The claim is one about \emph{expectations}:
$\tau_{\mathrm{HAT}}$ is strongly right-skewed, and the ratio of Kaplan--Meier medians moves the other
way, from $5.32\times$ at $\Delta e = 0.14$ to $3.10\times$ at $\Delta e = 0.33$. The ratio of means
rises while the ratio of medians falls because the delay laws of the two arms do not keep their shape
across magnitudes (Remark~\ref{rem:exponent}), so no single factor describes both, and the anchors above
are statements about means. The power-law fits over the full grid (Figure~\ref{fig:pht_scenarios})
reveal that HAT and ARF share the \emph{same} complexity exponent
($\hat\alpha_{\mathrm{HAT}} \approx 1.02$, $\hat\alpha_{\mathrm{ARF}} \approx 0.98$), while the prefactor
drops from $K_{\mathrm{HAT}} \approx 102$ to $K_{\mathrm{ARF}} \approx 18.5$. Over the full grid, onset
acceleration thus reads as a change of prefactor, not of complexity class; it is not a constant factor
across magnitudes --- the two anchors above differ by a factor of two --- and Remark~\ref{rem:exponent}
bounds what the full-grid fits can carry.

This phenomenon is structurally analogous to the multichart CUSUM
of Tartakovsky~\cite{tartakovsky_2005_multichart}, where running $M$ parallel CUSUM charts and alarming
on the first exceedance reduces detection delay by a factor approaching $M$. Read as a quantitative
null, that analogy predicts $10\times$ at $M = 10$; the measured $4.1$--$8.0\times$ sits strictly below
it. The shortfall is not the cost of inter-tree correlation: the order statistics of the single-tree
delay law alone predict $9.22\times$ at $\Delta e = 0.3268$ and $4.83\times$ at $\Delta e = 0.1409$,
against $7.99\times$ and $4.12\times$ measured, which leaves factors of $0.87$ and $0.85$ for dependence
and marginal mismatch together, and the measured within-run correlation of the swap times is
$\hat\rho \in [-0.021, 0.053]$ (Appendix~\ref{sec:dep_exponential}). Non-exponentiality of the delay law
carries most of the departure from the parallel-chart reference.

\paragraph{What the first replacement does, and what it does not.}
Counterfactual arms sharing one stream, one history and one fork separate two mechanisms that earlier
versions of this work conflated. Suspending adaptation entirely at the first replacement leaves the
error excess in place and the evidence ceiling rises to $\SixCeilingFrozen$ at $\Delta e =
\SixCanonDeltaE$; suspending every \emph{subsequent} replacement while the surviving trees keep learning
gives $\SixCeilingNoSwap$; the nominal arm reaches $\SixCeilingFull$. Volumetric erasure is therefore the
work of ordinary incremental learning by the $M-1$ trees that were not replaced. The mechanism is
direct: instrumentation shows that the two ADWIN instances guarding a member are identical clones fed
identical input, so they fire on the same step and the promoted background tree has learned nothing at
the instant it replaces an active one. A tree with no training cannot restore an ensemble's error rate,
and one member in ten alters one vote in ten.

The replacement sequence keeps a narrower and better-identified role. First, it accelerates onset: the
forest reacts on $\min_i \tau_i$, so the learning phase that erases the residual begins
$4.1$--$8.0\times$ sooner than a single adaptive tree's would. Second, it locks the
\emph{thresholded} decision: suppressing the replacements after the first raises the median ceiling from
$\SixCeilingFull$ to $\SixCeilingNoSwap$ and lifts detection at $\lambda = 50$ from zero to
$\NoSwapLeak\%$; a residue worth under one percent of the erased evidence flips nearly a fifth of the
decisions, because the threshold sits in the upper tail of the ceiling distribution. The first
replacement weighs more than all its successors together: suppressing replacement from $\tau^*$ onward
lifts detection to $\AbInitDetect$ runs in $100$ (Remark~\ref{rem:first_swap}). We report
$\tau_{\mathrm{swap}}^{(1)}/\tau_{\mathrm{swap}}^{(1/M)} = \SwapRatio$ and an elasticity of
$\SwapElasticity$ ($z = \SwapElasticityZ$ against unity) so that the first replacement is read as the
onset of adaptation and not as its completion, and we no longer describe the replacement sequence as an
avalanche.
```

---

## 3. Paragraphe INSECTS — validation monde réel, dans `sec:crossover` (.tex:540)

C'est le paragraphe analysé par H10/K7 (« quatre corrections », rejet de l'axe p₀). Un second passage INSECTS existe en `sec:limitations` (.tex:635, « The empty calibration window on INSECTS ») ; signalé sans reproduction — préciser si c'est lui qui est visé.

```latex
The six streams populate the regime-crossover boundary of Section~\ref{sec:crossover} continuously
(Table~\ref{tab:real_data_summary}); all INSECTS positions follow Souza et
al.~\cite{souza_insects_2020}, Table~2. The three BAF variants sit at $\Delta e \approx 0$ (Weak Signal
zone), where the blind spot is dormant and the HT/ARF F1 ratio is indistinguishable from unity. This
reading is not an artefact of the estimator being measured on an adapting model: a reference tree forked
at the end of the warm-up and never retrained reports the same $\Delta e \approx 0$ at the same
canonical positions ($|\Delta e| < 0.001$, every interval covering zero). A frozen model cannot absorb a
change, so a jump it does not see is not one adaptation has erased. Both trees in fact sit at the
majority-class error rate, which on these streams is the fraud rate itself: no Hoeffding-tree pipeline
acquires discriminative signal on BAF, so no error transient exists for any monitor to miss. BAF is
therefore an explicit \emph{negative control} for the phenomenon, and the demonstration rests on the two
high-magnitude INSECTS variants. INSECTS \emph{abrupt\_balanced} ($\Delta e \approx 0.07$) is a
\emph{weak witness}: its five canonical jumps are heterogeneous and partly negative
($\Delta e \in \{0.68, -0.15, 0.24, -0.27, -0.13\}$) and both detectors fire near their false-alarm rate,
so its marginal ARF advantage is not mechanistically attributable. The effect appears on the two
high-magnitude variants, and through \emph{false-alarm flooding}, not starvation. On
\emph{gradual\_balanced} ($\Delta e \approx 0.45$, single transition) PHT+HT detects genuinely ($7$
alarms, precision $0.14$, F1 $0.25$) whereas PHT+ARF($c{=}1$) sprays $86$ alarms (precision $0.012$, F1
$0.02$)---a $10.57\times$ F1 gap (sign test $p \le 2^{-29}$, the resolution floor of the two-sided test
at $30$ seeds) driven entirely by precision; \emph{incremental\_reoccurring\_balanced}
($\Delta e \approx 0.39$) confirms the same mode more moderately ($1.61\times$, $p \le 2^{-29}$). We
state this plainly: the predicted \emph{starvation} (recall $\to 0$) is observed only on the synthetic
stationary streams (Bernoulli, ProteuS), while the real non-stationary streams exhibit its dual,
\emph{flooding} (precision $\to 0$; Remark~\ref{rem:flooding}).\footnote{The evaluated set is the three
balanced INSECTS variants with discrete change points held in the artifact repository. Table~2 of Souza
et al.~\cite{souza_insects_2020} lists eleven streams, and the other eight are not evaluated:
\emph{incremental\_balanced}, which has no discrete drift positions and so admits no tolerance
matching, \emph{incremental\_abrupt\_balanced}, the five imbalanced variants, and \emph{out-of-control}.
No $\Delta e$ is computed or reported for them.}
```

---

## 4. `rem:predicate_scope` — Remark « Scope of the predicate » (`sections/framework_v2.tex`:324–334)

```latex
\begin{remark}[Scope of the predicate]\label{rem:predicate_scope}
  The budget $A$ of Definition~\ref{def:blindspot} is the evidence a monitor
  spends when its window can span the whole transient, as for the cumulative
  statistics and ADWIN. A fixed-window two-sample monitor reads at most
  $\min(W, n_{\mathrm{stat}})$ steps of the transient at once, so the budget is
  not the quantity its detection tracks: its condition is the contrast
  of~\eqref{eq:Rkswin_contrast}, a mean-field boundary whose scope
  Remark~\ref{rem:window_requirement} measures. We state the two conditions
  separately; a single predicate covering both was pre-registered and not
  retained (Section~\ref{sec:limitations}).
\end{remark}
```

---

## 5. Résumé — Abstract (.tex:135–154)

Macros résolues (définitions en préambule, .tex:67–85) : `\CeilingCanon` = 33.5, `\RcusumFifty` = 59.3, `\RcusumOp` = 31.2, `\LearnSharePure` = 98.6.

```latex
\begin{abstract}
  Concept-drift monitoring pairs an adaptive classifier with an external detector reading its
  error stream, a residual the classifier reacts to: fault detection on an endogenous residual,
  where the monitor's evidence is bounded by adaptation, not the horizon. We size the pipeline with
  two quantities in one unit---the evidence an adaptation leaves inside the window, and the
  evidence a monitor requires at a stated false-alarm level---so a missed detection is attributed
  to a calibration, not a detector family. Synchronised instrumentation measures the first: the
  median evidence ceiling at the canonical operating point, $\CeilingCanon$, clears the
  information-theoretic floor binding every monitor at that level. A cumulative monitor
  nonetheless detects nothing: its requirement is $\RcusumFifty$ at $\lambda = 50$ and
  $\RcusumOp$, which the ceiling clears, at the threshold the same certificate returns. The
  published collapses are threshold facts: on heteroscedastic streams the same monitor that misses
  all $1{,}080$ drifts at the deployed threshold detects each at $\lambda = 5$; counterfactual arms
  sharing one stream and fork assign $\LearnSharePure\%$ of the erasure to ordinary incremental
  learning with no tree replaced, not to any internal detector. The rule is operational: set the
  threshold from the false-alarm budget of the armed span, on the paired classifier's error stream,
  and check it against the measured ceiling. Validation spans instrumented Bernoulli streams,
  ProteuS and six real-world streams, reporting recall and precision collapse separately.
\keywords{Concept drift \and Adaptive blind spot \and ADWIN \and Page-Hinkley \and Adaptive Random Forest}
\end{abstract}
```

---

## Bornes de l'extraction

1. Les textes sont cités depuis la source LaTeX de la v65 MLJ, non depuis le PDF rendu ; les macros non résolues des passages 2 et 3 (`\SixCeilingFrozen`, `\NoSwapLeak`, `\SwapRatio`, etc.) sont définies en préambule du même fichier.
2. Le « paragraphe INSECTS » retenu est celui de `sec:crossover` (.tex:540), celui que H10 §« Paragraphe INSECTS » audite ; le passage jumeau de `sec:limitations` (.tex:635) traite de la fenêtre de calibration vide.
3. La v64 camera-ready diverge sur `sec:hydra` (intitulé « The Hydra Effect », .tex:215) ; l'extraction suit CURRENT, qui désigne la v65.
