# Transfer document — stream S2 (stopping-time theory at the measured base rate)

Parent `638ce54`, branch `stream-s2`. Decision rules fixed before measurement in
`docs/prompts/s2-decision-rules.md` (`671aa29`).

## Faults and open items addressed

| item | source | status |
|---|---|---|
| `p_0 = 0.05` assumed, `0.024` measured | S6 divergence 4, `transfer_S1` M3 | **closed** — every stopping-time numeral recomputed at `p_true`; three objects named `p_0` separated by a call-site census |
| open item 1, `R_EDDM` | `transfer_S1` | **closed by withdrawal** under rule R5 |
| open item 4, `W` deterministic | `transfer_S1` | **closed** — Eq. (4) restated as a `W`-integrated bound; the result is that it is vacant, not that it is repaired |
| T2.0 gate, `lambda_FA` | plan S2 Phase 1 | **NON-EMPTY**, carried by the empirical reading, concordant and band-invariant |
| `prop:invariance` unproved | S6 open item 2 | **PROVED UNDER STATED CONDITION**; both hypotheses measured false |
| `cor:split` no proof environment | S1 | **PROVED**, and corrected: its KSWIN clause contradicted `eq:Rkswin` |
| `thm:floor` proof audit | plan S2 Phase 6 | **PROVED**; chain rule read conditionally, `chi^2` step replaced by a chord bound, floor tightened by `6.74x` |
| `ass:repair` | A7 | **verified withdrawn**, not withdrawn a second time; `prop:order` now carries a proof on the measured condition |

## Deliverables

- `docs/manuscript/sections/prop3_v2.tex` — domain of Eq. (4), `W` as a random variable,
  load-bearing arbitration, the three proofs, the EDDM withdrawal, the proof-status table.
- `docs/manuscript/sections/framework_v2.tex` — edited inside the S2 partition only.
- `docs/theory/S2_arl0_recomputation.md`, `docs/theory/S2_numerical_validation.md`.
- `experiments/S2_theory/{s2_arl0.py, s2_w_random.py, s2_eddm.py}`, `tests/test_S2_theory.py`.
- `results/S2_theory/tables/` — nine artifacts, hashes in `S2_numerical_validation.md`.

---

## 1. The causal statement (T2.6)

One sentence, sourced on the arms, handed to the writing stream:

> Internal ADWIN hyper-reactivity fixes the onset of adaptation, not the erasure mechanism:
> 99.3 % of the evidence erased (`E_learn` 819.2 / `E_total` 826.7, n = 1979, IQR
> [0.987, 0.998]) is the work of ordinary incremental learning by the `M-1` surviving
> trees — the `frozen` arm, which stops learning, does not erase; the `no_swap` arm, which
> stops replacing but keeps learning, does.

**Three-arm sourcing** (`results/S6_synchronized_traces/data/s6_causal.json`,
`erasure_share_post_fork.a_pos_common.pooled`):

| arm | what it suppresses | median `max_t A_unrefl` at `Delta_e = 0.327` |
|---|---|---|
| `full` | nothing (nominal ARF) | 33.5 |
| `no_swap` | replacements after the first; keeps learning | 43.5 |
| `frozen` | learning entirely; forked at the same instant | 1063.6 |

`E_total = A_frozen - A_full` (median 826.7) is the erasure by all adaptation;
`E_learn = A_frozen - A_no_swap` (median 819.2) is the erasure by incremental learning alone;
their ratio is `share_learn` = 0.993, IQR [0.987, 0.998], n = 1979. Both counterfactual arms fork
**at** the first replacement and share it with `full`, so the contrast identifies post-fork
learning and not the first swap; the first swap's own contribution is not identified by this
design.

The abstract already carries this decomposition. **The one site still contradicting it is
`rem:flooding` L330** — *"two faces of one root cause---the hyper-reactive internal ADWIN"* — and
it is repaired by patch B below.

## 2. Rule R1(b): a `transfer_S1` numeral that does not reproduce

Recorded here on delivery, per the orchestrator's instruction; the corresponding edit to
`transfer_S1.md` lands in this stream's Phase 6 pass over that file.

`transfer_S1.md` L63 states the universal floor at two operating points. The first,
`Delta_e = 0.33`, `W = 55`, reproduces to three decimals — **1.450 against 1.45 stated** — which
is what identifies the inputs L63 never declares: `p_0 = 0.05`, `delta_P = 0.005`, `eps = 0.05`,
`lambda = 50`, `Delta_max = Delta_e`, `ARL_0 = 2.04e7`.

The second, **`Delta_e = 0.10`, `W = 13`, stated at 4.56, returns 6.277** under those same
identified inputs. The discrepancy is not a tolerance question:

- no `lambda` on the tabulated ladder returns 4.56 — `lambda = 8` gives 2.180, `lambda = 25` gives
  4.022, `lambda = 50` gives 6.277;
- recovering 4.56 at `lambda = 50` requires either `Delta_max = 0.137` where 0.10 is stated, or
  `p_0 = 0.0359` where 0.05 is stated.

S1 documents no parameters for this line — no `lambda`, no `Delta_max` convention, no `alpha`
basis — and no script in the repository produces it. **Verdict R1(b): UNREPRODUCED.** Both numbers
are carried side by side and neither is absorbed. This is the second `transfer_S1` numeral without
code provenance and the first that does not reproduce; the tabulated column L25–31 does reproduce
(R1(a) REPRODUCED, all three settings).

## 3. `ARL_0` is an interval, never a scalar

Over the central 95 % of the measured per-run pre-drift rate, `p_true in [0.015, 0.032]`, the
Cramér root moves `0.968 -> 0.542` and `ARL_0` at `lambda = 50` spans `1.10e14` to `1.10e23` —
**nine orders of magnitude**. No statement whose conclusion depends on the size of `ARL_0` may be
evaluated at a scalar.

The floor is the one quantity that survives this, because `ARL_0` enters it only through
`alpha = W/ARL_0` inside `d(1-eps || alpha)`, hence only through `ln(1/alpha)`. Over the same band
the tightened floor `eq:floor_chord` at `Delta_e = 0.3268`, `W = 57.4`, `lambda = 50` evaluates to
**[13.9, 18.3]**, a ±14 % interval. Every floor in the manuscript is stated as that interval.
`rem:floor_band` in `framework_v2.tex` carries the rule; `prop3_v2.tex` §proofs carries the
derivation.

## 4. Manuscript patches — **PRODUCED, NOT APPLIED**

S7-ter edits the same file in the same wave and both streams add to the same preamble block. The
orchestrator applies both streams' patches in one serialized pass on `main` after both transfers
land. Anchors are by label and by verbatim text, never by line number.

### Patch A — preamble macro declarations

Target: `docs/manuscript/articleA_blindspot_v64_camera_ready.tex`.
Anchor: the closing line of the S6 macro block, immediately before the `\DeCrit` pair.

~~~~~~~~~
docs/manuscript/articleA_blindspot_v64_camera_ready.tex
<<<<<<< SEARCH
\newcommand{\DeCrit}{0.120}                  % measured Action 4: 0.1197, n=300
\newcommand{\DeCritCI}{[0.114, 0.127]}       % 95% bootstrap CI (10,000 draws)
=======
\newcommand{\DeCrit}{0.120}                  % measured Action 4: 0.1197, n=300
\newcommand{\DeCritCI}{[0.114, 0.127]}       % 95% bootstrap CI (10,000 draws)

% ── Stream S2 recomputation at the MEASURED base rate. Source: results/S2_theory/tables/.
% Every value is read from a committed artifact; none is typed by hand.
\newcommand{\PzeroMeas}{0.024}               % ssot.P0\_MEASURED; median e\_pre, arm full, n = 2000
\newcommand{\PzeroBand}{[0.015,\,0.032]}     % central 95 \% of per-run e\_pre, s2\_gate\_T20.json
\newcommand{\ThetaStar}{0.6813}              % Cramer root at PzeroMeas, delta\_P = DeltaPtext
\newcommand{\ArlFifteen}{4.0\times10^{6}}    % ARL\_0(lambda = 15), s2\_arl0\_columns.csv
\newcommand{\ArlFifty}{9.1\times10^{16}}     % ARL\_0(lambda = 50), idem
\newcommand{\FloorBand}{[13.9,\,18.3]}       % eq:floor\_chord over PzeroBand, s2\_gate\_T20.json
\newcommand{\ChiLoose}{6.74}                 % chi\^{}2 looseness factor at PzeroMeas
\newcommand{\FloodLamArf}{20.97}             % mean lambda\_calibrated, pht\_arf\_c1
\newcommand{\FloodLamHt}{132.50}             % idem, pht\_ht (insects\_per\_episode.parquet)
\newcommand{\FloodPredArf}{210}              % re-arm model, s2\_flooding\_retrodiction.json
\newcommand{\FloodPredHt}{28}                % idem
\newcommand{\FloodArlGap}{3\times10^{4}}     % shortfall factor of the ARL\_0 model
>>>>>>> REPLACE
~~~~~~~~~

### Patch B — `rem:flooding`, restated through `ARL_0` and on the measured decomposition

Target: `docs/manuscript/articleA_blindspot_v64_camera_ready.tex`.
Anchor: the body of `\begin{remark}[...]\label{rem:flooding}`, in `sec:complexity`, outside the
four-subsection exclusion. Patch A must be applied first — B consumes its macros.

~~~~~~~~~
docs/manuscript/articleA_blindspot_v64_camera_ready.tex
<<<<<<< SEARCH
  Starvation and flooding are two faces of one root cause---the hyper-reactive internal ADWIN at $c_{\mathrm{int}}{=}1$. A \emph{large, abrupt} change is absorbed one-shot before the external CUSUM accumulates (starvation, recall $\to 0$; Prop.~\ref{prop:starvation}). Under a \emph{weak per-step} signal (low SNR or a gradual onset, even at large aggregate $\Delta e$) it instead swaps continuously on noise (Remark~\ref{rem:bgswap}), injecting spurious post-reset transients read as alarms (precision $\to 0$): on \emph{gradual\_balanced} the $c_{\mathrm{int}}{=}1$ clock inflates the external alarm count to $86$ for a single true drift, against $7$ for the HT baseline (Section~\ref{sec:crossover}). Both deform the error stream---tracking a \emph{genuine} change (starvation) or a \emph{phantom} one (flooding). Crucially, flooding is parametrically controllable (raising $\lambda$ suppresses it), whereas starvation is structural: no CUSUM threshold escapes it (Section~\ref{sec:starvation_boundary}).
=======
  Starvation and flooding are duals in their effect on $F_1$, not two faces of one cause. Starvation is the erasure of a genuine transient, and the synchronised decomposition assigns $\LearnShare\%$ of that erasure to ordinary incremental learning by the $M{-}1$ surviving trees rather than to the internal clock: the hyper-reactive ADWIN at $c_{\mathrm{int}}{=}1$ fixes \emph{when} adaptation starts, not \emph{what} removes the evidence. Flooding has a different mechanism, and the two should not be attributed to one root cause.

  Read through $\mathrm{ARL}_0$, an alarm raised after the transient is uninformative and arrives under the no-change law at rate $1/\mathrm{ARL}_0$ (Remark~\ref{rem:sufficient}). At the measured base rate $p_0 = \PzeroMeas$ with $\delta_P = \DeltaPtext$ that rate is negligible---$\mathrm{ARL}_0 = \ArlFifteen$ steps at $\lambda = \LambdaFA$---and it accounts for essentially none of the alarms observed: on \emph{gradual\_balanced} it predicts $3\times10^{-3}$ alarms over the armed pre-change span against $86$ measured, short by a factor $\FloodArlGap$. The flooding alarms are not null-regime false alarms, and no recalibration of $\mathrm{ARL}_0$ explains them.

  What produces them is the post-change regime itself. The error rate does not return to its pre-change level on that stream ($0.50$ against $0.058$ for the ARF pipeline), so a monitor re-armed after each alarm crosses $\lambda$ again roughly every $\lambda / (\bar e_{\mathrm{post}} - p_{\mathrm{pre}} - \delta_P)$ steps. That re-arm model, with no fitted constant, returns $\FloodPredArf$ alarms for PHT$+$ARF($c{=}1$) against $86$ measured and $\FloodPredHt$ for PHT$+$HT against $7$, and their ratio $7.6\times$ against a measured $12.2\times$. We claim order-of-magnitude agreement only: Sections~\ref{sec:proteus} and~\ref{sec:crossover} run River's adaptive mean-tracking PageHinkley at $\delta_P = 0.005$, not the fixed-$p_0$ recursion of Eq.~\eqref{eq:cusum}, so this is a consistency check across estimators and is labelled as one. The asymmetry between the two pipelines is a threshold asymmetry: the one-false-alarm-per-warm-up calibration hands the ARF $\FloodLamArf$ and the HT $\FloodLamHt$, a factor of $6.3$, because bagging halves the ARF's pre-change error volatility (Section~\ref{sec:crossover}). The variance reduction that makes the ARF a good classifier buys it a low threshold, and a low threshold is what floods once the error stream stays elevated. Flooding remains parametrically controllable---alarms scale as $1/\lambda$ in the re-arm model---whereas starvation is structural: no CUSUM threshold escapes it (Section~\ref{sec:starvation_boundary}).
>>>>>>> REPLACE
~~~~~~~~~

### Sites outside the S2 write perimeter, handed forward

Both carry the `R_EDDM` claim that rule R5 withdraws. Neither is in S2's writable set and neither
is patched here.

1. `docs/manuscript/articleA_blindspot_v64_camera_ready.tex` L151 (`sec:related`): *"any monitor
   that requires a persistent deviation with a stopping time scaling as `Omega(lambda / Delta e)`
   --- DDM, EDDM, ECDD --- is defeated"*. EDDM's stopping structure is not
   `Omega(lambda / Delta e)`: it is a level test on a cumulative ratio against a running maximum,
   whose requirement grows with the pre-change history and does **not** shorten with `Delta e`
   (`prop3_v2.tex` §EDDM). The sentence should be narrowed to the detectors for which the
   accumulation argument is actually instantiated, or marked as a conjecture.
2. `docs/manuscript/sections/related_work_v2.tex` L108: *"DDM, EDDM and ECDD share the
   accumulation structure and inherit its window sensitivity."* Same correction.

The **empirical** EDDM result (`sec:proteus`, 0 detections in 1080 runs against 882 for EDDM+HT,
sign test `p ~ 1.9e-9`) is untouched by either correction and must be kept.

---

## 5. Verdicts, one line each

| rule | object | verdict |
|---|---|---|
| R1(a) | `transfer_S1` L25–31 | **REPRODUCED** (3/3 columns, `theta*` within 1.4e-5 to 2.0e-4) |
| R1(b) | `transfer_S1` L63 | **line 1 REPRODUCED, line 2 UNREPRODUCED** (6.277 against 4.56) |
| R2 | `lambda_FA` gate | **NON-EMPTY**, empirical reading, concordant, band-invariant |
| R3 | Eq. (4) domain | **RETAIN**, restricted to `{(W, lambda) : mu W < lambda}` and demoted to a scope statement — 52 of 240 pairs inside the domain, 32 with a bound below 1 |
| R4 | `W`-integrated bound | **VACANT** at every `lambda` under the deterministic and plug-in readings; parametric reading formally INFORMATIVE with a best value of 0.753 |
| R5 | `R_EDDM` | **WITHDRAWN** |
| R6 | proofs | `thm:floor` PROVED (and tightened) · `cor:split` PROVED (and corrected) · `prop:invariance` PROVED UNDER STATED CONDITION · `prop:order` PROVED · `R_EDDM` NOT PRODUCED |

**R3's criterion is necessary, not sufficient.** `mu W < lambda` admits 52 pairs, but only 32 of
them give `W exp(-2/W (lambda - mu W)^2) < 1`. The rule was written on the positive-part criterion
and is applied as written; the gap is recorded rather than used to move the rule after the fact.

**R4's censoring floor is structural.** A censored run contributes exactly 1 to the capped
integrand, so the integrated bound is at least the censoring fraction — 8.21 % on the 1,974-run
complete case, 8.20 % on the 2,000-run arm — before any drift magnitude is consulted. That is a
result about the bound, not a defect of the campaign, and it strengthens the case for
`prop:certificate` as load-bearing rather than repairing Eq. (4).

## 6. Open items handed forward

1. **`related_work_v2.tex` L108 and `.tex` L151** carry the withdrawn `R_EDDM` claim and are
   outside the S2 perimeter (§4).
2. **`prop:invariance` is a true statement about a withdrawn model.** It explains a factor 1.03 of
   a measured factor 1.90 and predicts monotonicity where the measurement shows a hump. The
   writing stream must decide whether to keep it as a stylised statement with
   `rem:invariance_measured` attached, or to promote the counterfactual (`no_swap` / `frozen`,
   factor 124, monotone) to the primary formulation. S2 recommends the second and does not make
   the change.
3. **`lambda_starve` (`transfer_S1` L62) is non-monotone at the weak end** — 29.5 at
   `Delta_e = 0.028`, peaking at 87.5 at 0.141, descending to 25.2 — because weak-band swaps are
   noise-driven, so `W` is large exactly where `mu` is small. L62's *"monotone"* is false.
4. **`s_0` is never measured.** It is the sole channel through which `p_0` enters
   `eq:starve_boundary`, and both S1 and S2 evaluate at `s_0 = 0`. The traces can supply it — the
   reflected statistic at `tau*` accumulated over the 1,000-step warm-up — and S2 did not compute
   it because the plan did not ask for it. Any stream tightening the starvation boundary should.
5. **EDDM is not testable on any committed artifact.** ProteuS records no error stream, and the S6
   traces do not warm the detector before `tau*` (95 % of runs). Testing `R_EDDM` empirically
   requires a campaign that records the error stream on the stream where the collapse occurs.
6. **S3 partition.** `prop:starvation_boundary`, `cor:mcrit` and every inter-tree-dependence
   statement are untouched and absent from `framework_v2.tex`; no anchor collision arose.

## State

Stream S2 complete, Phases 0–7. Manuscript of record not written; patches A and B produced and
pending the orchestrator's serialized pass.
