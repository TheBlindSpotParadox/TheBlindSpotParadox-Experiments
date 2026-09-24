# Transfer document — stream S10 (external validity, the dual mode, label latency)

Parent `19b9bde`, branch `stream-s10`. Decision rules fixed before any measurement in
[`S10_decision_rules.md`](S10_decision_rules.md) (`22252da`, erratum E1 `88add36`). Measurement
report: [`S10_external_validity.md`](S10_external_validity.md).

**Nothing below is applied.** Every charge is either a SEARCH/REPLACE payload with a verbatim
anchor and a named target file, re-grepped on the live file when this document was written, or a
charge with no payload where the decision belongs to the assembly. None lands inside `sec:race`,
`sec:hydra`, `sec:starvation` or `sec:decoupling`; `tests/test_S10_external_validity.py` checks
that by character offset and checks that every anchor resolves exactly once.

| charge | lands on | target | status |
|---|---|---|---|
| **S10-A** | section Multiplicity, the whole body | `sections/protocol_v2.tex` | payload: enlarged family, census, withdrawals |
| **S10-B** | `.tex:531`, the footnote on excluded INSECTS variants | `articleA_blindspot_v64_camera_ready.tex` | **charge, no payload**: scope wording belongs to the assembly |
| **S10-C** | `sec:limitations`, after the Limitations paragraph | `articleA_blindspot_v64_camera_ready.tex` | payload: label latency |
| **S10-D** | before "The Fundamental Tension" (`sec:discussion`) | `articleA_blindspot_v64_camera_ready.tex` | payload **recorded, not applied**: a `figure*` changes the pagination (`space_constraints_audit.md`) |
| **S10-E** | Table II and its `\input` | assembly decision | **charge, no payload**: `p0` columns |

---

## A. S10-A — the multiplicity statement

`protocol_v2.tex` states the family "in full" as ten tests. S10 adds eight latency contrasts, and the
live manuscript carries twenty-one further `p`-values the declared ten omit (twenty KS
exponentiality tests at `.tex:408` and `dependence_v2.tex:228`, one Fisher test at `.tex:298`). Holm
over both families: `results/S10_external_validity/tables/s10_holm.json`.

~~~~~~~~~
docs/manuscript/sections/protocol_v2.tex
<<<<<<< SEARCH
The family of hypothesis tests reported in this paper is stated in full: six seed-level pipeline
contrasts on ProteuS, one contrast in the KSWIN $\alpha$-sweep, and three seed-level contrasts on
the INSECTS variants of Table~\ref{tab:real_data_summary} --- ten tests. The three BAF rows carry
no test, their $\Delta e$ being indistinguishable from zero (Section~\ref{sec:protocol_ci}).

Eight of the ten $p$-values sit exactly at the resolution floor of the two-sided sign test at
$n_{\mathrm{eff}} = 30$, derived in Section~\ref{sec:protocol_separation}. No correction over a
family of this size can lift them: Holm--Bonferroni at $\alpha = 0.05$ compares the smallest
against $\alpha/10 = 5 \times 10^{-3}$, and $2^{-29} \approx 1.86 \times 10^{-9}$ clears that by six
orders of magnitude, as it clears every subsequent step. Bonferroni over the whole family gives
$10 \cdot 2^{-29} \approx 1.86 \times 10^{-8}$, still far below any conventional level. For these
eight the correction is not applied because it is arithmetically incapable of changing a decision,
which is a justification and not an omission.

The two remaining tests are reported with the opposite verdict, and it is the honest one. The
KSWIN $\alpha$-sweep contrast is degenerate ($p = 1$: both arms detect 1080 of 1080 runs), and the
INSECTS \emph{abrupt\_balanced} contrast has $p = 0.043$, which under Holm is compared against
$\alpha/2 = 0.025$ and \textbf{does not survive}. We therefore do not claim a seed-level effect on
\emph{abrupt\_balanced}. That is consistent with how Section~\ref{sec:proteus} already treats that
variant --- a weak witness whose five canonical jumps are heterogeneous and partly negative, and
whose marginal advantage is explicitly not attributed to the mechanism. The multiplicity correction
removes a claim the paper had already declined to make.
=======
The family of hypothesis tests reported in this paper is stated in full. Eighteen tests carry its
claims: six seed-level pipeline contrasts on ProteuS, one contrast in the KSWIN $\alpha$-sweep,
three seed-level contrasts on the INSECTS variants of Table~\ref{tab:real_data_summary}, and eight
seed-level contrasts of the label-latency analysis (Section~\ref{sec:limitations}). The three BAF
rows carry no test, their $\Delta e$ being indistinguishable from zero
(Section~\ref{sec:protocol_ci}). The paper reports twenty-one further $p$-values---twenty
Kolmogorov--Smirnov tests of exponentiality and one Fisher test of homogeneity---and the
correction is also run over all thirty-nine; no verdict differs between the two families.

Holm--Bonferroni at $\alpha = 0.05$ over the eighteen retains fifteen. Eight of the ten tests
declared before the latency analysis sit exactly at the resolution floor of the two-sided sign test
at $n_{\mathrm{eff}} = 30$, derived in Section~\ref{sec:protocol_separation}; $2^{-29} \approx 1.86
\times 10^{-9}$ clears the first Holm threshold, $\alpha/18 \approx 2.8 \times 10^{-3}$, by six
orders of magnitude, as it clears every subsequent step. Seven of the eight latency contrasts are
retained, at $p \le 2.4 \times 10^{-10}$ over one hundred seeds.

Three tests are not retained, and the paper claims none of them. The KSWIN $\alpha$-sweep contrast
is degenerate ($p = 1$: both arms detect 1080 of 1080 runs). The INSECTS \emph{abrupt\_balanced}
contrast has $p = 0.043$, which under Holm is compared against $\alpha/3 \approx 0.017$ and
\textbf{does not survive}. We therefore do not claim a seed-level effect on
\emph{abrupt\_balanced}, consistently with how Section~\ref{sec:proteus} already treats that
variant---a weak witness whose five canonical jumps are heterogeneous and partly negative, and whose
marginal advantage is explicitly not attributed to the mechanism. The rise of detection under a
shared label latency on the rotation family ($p = 0.16$) is withdrawn; its canonical counterpart is
retained. Over the thirty-nine, the Fisher homogeneity test ($p = 1$) joins the non-retained set; it
licenses pooling as a non-rejection, which no correction alters. Every Kolmogorov--Smirnov test is
retained, the largest ($p = 0.003$) against $\alpha/5$.
>>>>>>> REPLACE
~~~~~~~~~

## B. S10-B — the INSECTS footnote (no payload)

`.tex:531` declares two balanced variants excluded (*incremental\_balanced*,
*incremental\_abrupt\_balanced*). Table 2 of Souza et al. (2020) lists eleven datasets. The five
imbalanced variants and *out-of-control* are absent without a word. By operator arbitration S10
evaluated the three balanced variants the repository holds, and no more; the eight others are not
in the repository and River's download URL answers 404. The footnote should say the evaluated set is
the three balanced variants with discrete change points held in the repository, and name the others
as not evaluated. The wording is the assembly's; the motive is recorded in the S10 report, §5.

## C. S10-C — label latency, a limitation measured

~~~~~~~~~
docs/manuscript/articleA_blindspot_v64_camera_ready.tex
<<<<<<< SEARCH
masking the starvation condition and shielding standard pipelines from the blind spot.
=======
masking the starvation condition and shielding standard pipelines from the blind spot.

\textbf{Label latency.} The external monitor reads an error stream, and every error waits for its label. We measured delays of $l \in \{10, 50, 100, 500\}$ steps on the canonical and rotation families ($100$ seeds $\times$ $20$ magnitudes). The outcome depends on who waits. If only the monitor waits, erasure stays where it was and the alarm moves by $l$: detection before erasure at $\lambda = 15$ falls from $0.92$ to $0.24$ at $l = 500$ on the canonical family, with the evidence itself unchanged. If the classifier learns from the same delayed labels, adaptation recedes with them: the erasure instant moves by $0.998\,l$ at $l = 500$, the evidence read before it grows $2.5$-fold, and the starvation threshold $\lambda = 50$ detects $90\%$ of drifts instead of $5\%$. Latency penalises a monitor through the delay it adds \emph{beyond} the classifier's; a shared latency trades detection delay for a longer, larger transient.
>>>>>>> REPLACE
~~~~~~~~~

Numbers: `s10_latency.json` (M1 and M2 rates at `lambda` = 15 and 50, `T` shifts, budgets); verdicts
closed in `s10_holm.json :: T10_1_verdicts`. The rotation family's M2 rise is **not** cited: it did
not survive Holm.

## D. S10-D — the dual-mode figure (recorded, not applied)

The asset is `results/S10_external_validity/figures/Fig_S10_dual_mode.png`, produced by
`experiments/S10_external_validity/s10_dual_mode.py`. When it is copied to
`docs/manuscript/figures/`, `tests/test_manuscript_integrity.py` finds its twin by the
`results/*/figures/<name>` glob.

~~~~~~~~~
docs/manuscript/articleA_blindspot_v64_camera_ready.tex
<<<<<<< SEARCH
\textbf{The Fundamental Tension.} The tension is an envelope property, not a universal one.
=======
\begin{figure*}[t]
  \centering
  \includegraphics[width=\textwidth]{figures/Fig_S10_dual_mode.png}
  \caption{Starvation and flooding on one axis. Recall (solid) and precision (dashed) against the
    PageHinkley threshold on six streams; shaded: thresholds with recall $\ge 0.95$ and precision
    $\ge 0.5$, at the grid's resolution. Dotted: the threshold buying one false alarm over the armed
    pre-change span; dash-dot: the $5\%$ quantile of the post-drift statistic peak. (a,~b)~canonical
    and rotation families at $\Delta e = 0.327$, passive monitor; (c)~ProteuS; (d--f)~INSECTS,
    monitor and classifier reset on each alarm. Every published failure fails by one criterion:
    starvation by recall, flooding by precision. No threshold is admissible on INSECTS with the ARF
    at $c = 1$.}
  \label{fig:dual_mode}
\end{figure*}

\textbf{The Fundamental Tension.} Figure~\ref{fig:dual_mode} places starvation and flooding on one threshold axis. The tension is an envelope property, not a universal one.
>>>>>>> REPLACE
~~~~~~~~~

## E. S10-E — `p0` in Table II (no payload)

S9 D9 and S2-ter T4: a table that ranks detectors across streams must carry each stream's error
floor. `results/S10_external_validity/tables/s10_table2_p0.tex` is Table II's committed body plus
`p0_span` for PHT+HT and PHT+ARF(`c` = 1) (BAF 0.011–0.012; INSECTS 0.164–0.400); nothing else is
recomputed. The manuscript inputs `tables/table2_real_data_summary.tex`, which R5's
`exp_R5_make_table2.py` generates. Adopting the columns means either regenerating that table through
R5 (outside S10's perimeter) or substituting S10's tabular. The choice belongs to the assembly.

---

## What is deliberately not charged

- **The Table I and Table II numerals.** S10 reproduces them (P0-2, P0-3, L0) and moves none.
- **`def:times` and the symbol `W`.** Erratum E1 and the rotation measurement show that the
  last-crossing W is pinned to the horizon at a noisy base rate. Which quantity `W` names is under
  arbitration in S2-ter T3; S10 supplies the evidence (report §1.2) and no wording.
- **The "admissible set" sentence of the Fundamental Tension paragraph.** It is stated for the
  StrictCUSUM envelope; S10 measured the PageHinkley monitor at one magnitude per family and does not
  overwrite it.
