# PLAN S2 — Proposition 3, ARL_0, flooding regime

## Context

Stream S1 delivered the v2 formal framework and handed forward four open items plus a
blocking gate. Stream S6 measured the campaign that was supposed to settle them and
instead invalidated two of the constants S1 computed with: the pre-drift error rate is
`p_0 = 0.024`, not the assumed `0.05`, and the rectangular surrogate `A = q(tau_ARF)
(Delta_e - delta_P)` changes sign above `Delta_e = 0.452`. Action A1 corrected the CUSUM
tolerance to `delta_P = 0.01` but left `p_0` at the assumed value, so every theoretical
numeral currently in `docs/theory/transfer_S1.md` sits on a base rate the same repository
contradicts.

S2 closes that: it recomputes the stopping-time theory at the measured base rate, repairs
Proposition 3 (which is sound but vacant at the measured window), treats `W` as the random
variable it is, restates the flooding remark through `ARL_0`, and either proves or withdraws
`R_EDDM`. The target is now a journal (action A9), so the three statements carried without
proof in `framework_v2.tex` are expected in the body.

The gate is T2.0: if the recomputed `lambda_FA` exceeds `21.93`, the admissible set is empty
again on `[0.20, 0.40]`, `res:tension` simplifies and the published result changes. That
verdict is reported before any other task proceeds.

---

## Write perimeter — declared, and not exceeded

**Writable.**

| path                                                      | action                                                         |
| --------------------------------------------------------- | -------------------------------------------------------------- |
| `docs/prompts/s2-decision-rules.md`                       | new — committed before any output is read                      |
| `experiments/S2_theory/s2_arl0.py`                        | new                                                            |
| `experiments/S2_theory/s2_w_random.py`                    | new                                                            |
| `experiments/S2_theory/s2_eddm.py`                        | new                                                            |
| `results/S2_theory/tables/*`                              | new artifacts                                                  |
| `docs/theory/S2_arl0_recomputation.md`                    | new                                                            |
| `docs/theory/S2_numerical_validation.md`                  | new                                                            |
| `docs/theory/transfer_S2.md`                              | new — state transfer                                           |
| `docs/manuscript/sections/prop3_v2.tex`                   | new — deliverable 1                                            |
| `docs/manuscript/sections/framework_v2.tex`               | edit — **STRICT PARTITION**, see below                         |
| `docs/theory/transfer_S1.md`                              | edit — close open items 1 and 4, retire the superseded columns |
| `config/experiment_ssot.py`                               | **APPEND-ONLY**, see below                                     |
| `tests/test_S2_theory.py`                                 | new                                                            |
| `docs/manuscript/articleA_blindspot_v64_camera_ready.tex` | **NOT WRITTEN**, see below                                     |

**Partition of `framework_v2.tex` — S2 and S3 run concurrently on this file.**
S2 owns, and writes only: `thm:floor`, `cor:split`, `prop:invariance`, the detector
requirement block (`eq:Rcusum` / `eq:Radwin` / `eq:Rkswin`), `prop:order`, `def:kappa`.
S3 owns, and S2 must not anchor on, contextual lines included:
`prop:starvation_boundary`, `cor:mcrit`, and every new statement on inter-tree
dependence. If a unique anchor forces a bite into S3's zone, **do not write**: report the
anchor collision to the orchestrator. Three-to-four lines of context count as writing.

**`config/experiment_ssot.py` — append-only, in a banner-delimited stream block.**
S7-ter edits this same file in the same wave (`R3_C_WARN`, `R3_WARN_DELTA`, `R4_C_WARN`,
`R4_WARN_DELTA`, and the false comment at `:108`). Never modify an existing line. Append
`P0_MEASURED` and `EPS_MISS` at end of file under a `# S2 —` banner, with their motive.
`tests/test_S7_consistency.py` compares resolved values against `constants_pre.json`: a
merge that silently drops one side of a mid-file edit breaks the registry guard without
failing loudly.

**The manuscript of record is NOT written by S2.** S7-ter Phase B-3 edits the same file in
the same wave (R3 prose numerals, the Table I `\input`), and both streams would add macros
to the same preamble block. S2 produces its two manuscript patches — the new preamble macro
declarations and the `rem:flooding` rewrite — as SEARCH/REPLACE payloads inside
`docs/theory/transfer_S2.md`, and **does not apply them**. The orchestrator applies both
streams' manuscript patches in one serialized pass on `main` after both transfers land.
Anchors are stated by label (`rem:flooding`, the `\newcommand` block opening), never by
line number: the preamble has already drifted once (`.tex:292 -> 297`).

**Forbidden — the four superseded inline subsections.** `sec:race` (L168), `sec:hydra`
(L185), `sec:starvation` (L210), `sec:decoupling` (L376). This bites harder than it reads:
`prop:starvation`, `rem:transient_length`, `prop:certificate` and `rem:shortwindow` all live
inside `sec:starvation`, and `res:tension` / `rem:envelope` inside `sec:decoupling`. Every
T2.1 and T2.0 consequence therefore lands in `prop3_v2.tex`, never as an inline patch.
`rem:flooding` (L329) sits in `sec:complexity`, outside the exclusion, and is writable.

The preamble macro block is the one clean channel into the live document: `\LambdaFA`,
`\LambdaOpNarrow`, `\DeltaPtext` and the twenty `\Six*` macros already route every S6
numeral. New S2 numerals enter the same way, with the same provenance comment.

---

## Premises of `PROMPT_S2.md` that the repository has moved past

Verified against `HEAD = 638ce54`, not the `ba01fc7` the prompt anchors.

1. **`docs/sections/` does not exist.** Action A5 made `docs/manuscript/sections/`
   definitive. Deliverable 1 lands at `docs/manuscript/sections/prop3_v2.tex`.
   `tests/test_manuscript_integrity.py::main_tex_documents` discriminates on
   `\documentclass`, so a fragment there trips no guard.
2. **`envelope_stats.json` is at `results/S6_synchronized_traces/tables/`**, not at the
   directory root the prompt names.
3. **T2.0(a) is already pre-computed.** `transfer_S1.md` L25–31 carries the third column:
   `theta* = 0.6813`, approximation `0.8538 (+25.3 %)`, `ARL_0` = `3.3e4` / `3.7e9` /
   `9.1e16`. No script in the repository produces them — a graph query over 1,947 nodes
   returns no `theta*`, `ARL_0` or Cramér node. T2.0(a) is therefore an **independent
   reproduction with a committed script**, and a mismatch is a finding, not a nuisance.
   `lambda_starve` at the measured base rate is genuinely absent.
4. **T2.6 is already applied to the abstract.** The live abstract no longer says "a single
   root cause"; it separates onset (ADWIN), erasure (`\LearnShare = 99.3\%`, incremental
   learning) and lock (subsequent replacements). What still carries the revoked claim is
   `rem:flooding` L330: *"two faces of one root cause---the hyper-reactive internal ADWIN"*.
   That is a live internal contradiction, inside T2.3's writable scope.
5. **"permanently erased" is already gone.** `rem:sufficient` L275 states the opposite
   ("does not assert permanent erasure"). T2.3's third bullet is a verification, closed.
6. **`lambda_starve` has no `p_0` dependence as S1 defines it.** `transfer_S1` L62 states it
   through `eq:starve_boundary`: `lambda >= s_0 + mu W + sqrt(W/2 ln(W/eps))` with
   `mu := Delta_e - delta_P`. `p_0` enters only through `s_0` and through
   `alpha = W/ARL_0` in the floor of L63. S2 states that explicitly rather than reporting a
   spurious move.

---

## Phase 0 — decision rules, committed before any output is read

`docs/prompts/s2-decision-rules.md`, then `git commit` **before** running anything. This is
the discipline that kept S6 from publishing a knife edge at `15.219` against `15.00` — the
CSV shows that value verbatim at five grid points.

Rules to fix in advance, each with its numeric threshold and its verdict on both sides:

- **R1 — reproduction tolerance.** S2's `theta*` matches `transfer_S1` if
  `|theta*_S2 - 0.6813| / 0.6813 <= 1e-3`; `ARL_0` if within one significant figure at each
  `lambda`. Beyond that, the `transfer_S1` column is declared unreproduced and withdrawn.
- **R2 — `lambda_FA` gate.** Two readings, both reported, per the arbitration below.
  Empirical: `lambda_FA = R4_PHT_LAMBDA = 15`, invariant by construction. Theoretical:
  `lambda_FA^ARL := ARL_0^{-1}(target)` at `p_0 = 0.024`, `delta_P = 0.01`, where `target`
  is R4's implied `ARL_0` recovered from `lambda = 15` at `p_0 = 0.05`. Verdict `EMPTY` if
  `lambda_FA^ARL > 22.398` (the bootstrap upper bound, not the point estimate),
  `NON-EMPTY` if `< 19.876` (the lower bound), `UNDECIDED` in between — and `UNDECIDED` is
  a publishable verdict, not a retry.
- **R3 — vacancy of Eq. (4).** The bound is declared vacant at a given `W` when
  `mu W >= lambda`, so the positive part is zero and `W e^0 >= 1`. Reported per `lambda` in
  `{8, 15, 25, 50}` and per `W` in `{tau_swap^(1/M), tau_erase, tau_err(0.10)}`.
- **R4 — integrated bound.** The deterministic-`W` bound and the `W`-integrated bound are
  reported side by side. Censored runs (`W >= T_h = 2500`) contribute exactly `1` to the
  integrand, so the integrated bound is bounded below by the censoring fraction alone: fix
  that fraction from the artifact before computing anything, and declare the bound vacant
  if it exceeds 1.
- **R5 — `R_EDDM`.** Withdrawal is the default outcome unless a closed form reproduces the
  measured `F1 = 0.00` at `c_int = 1`, i.e. predicts no detection where the current normal
  approximation predicts `W = 155`. Agreement is declared on sign and order of magnitude,
  not on a fitted constant.
- **R6 — proof obligations.** Each of `thm:floor`, `cor:split`, `prop:invariance` is marked
  `PROVED`, `PROVED UNDER STATED CONDITION`, or `NOT PRODUCED`. The third is a legitimate
  terminal state and is declared, never silently left out.

---

## Phase 1 — T2.0, the gate

**`experiments/S2_theory/s2_arl0.py`.** Pure theory on committed artifacts, no simulation.

- Cramér root from `E[exp(theta (X - p_0 - delta_P))] = 1`, `X ~ Bern(p_0)`, i.e.
  `(1-p_0) e^{-theta(p_0+delta_P)} + p_0 e^{theta(1-p_0-delta_P)} = 1`, solved with
  `scipy.optimize.brentq` — already a repository dependency (`scipy 1.16.2`), no new one.
  The trivial root `theta = 0` is excluded by bracketing strictly above it.
- `ARL_0` from Siegmund (1985):
  `(exp(theta* lambda) - theta* lambda - 1) / (theta* delta_P)`.
- `lambda_starve` from `eq:starve_boundary` at `delta_P = CUSUM_DELTA_P`, over the same
  `Delta_e` grid as `transfer_S1` L62, with `W` taken from the S6 artifact rather than
  assumed.
- Tolerance read from `ssot.CUSUM_DELTA_P`, never a literal —
  `tests/test_S7_consistency.py::test_ssot_registry_and_no_value_drift` scans every
  `experiments/**/*.py` for registry constants re-bound to literals.

**Disambiguation of `p_0`, before any table is produced.** Three distinct objects carry this
name and the plan must never let them share a column header:
  (i)  `p_true` — the classifier's actual pre-drift error rate. Measured:
       `p0_hat_median = 0.023`-`0.024`, flat across the twenty magnitudes of
       `tables/cusum_delta001_quantiles.csv`.
  (ii) `p_pre` — the reference rate the CUSUM recursion subtracts,
       `S_t = max(0, S_{t-1} + (x_t - p_pre) - delta)` (`s6_detectors.py`). This is a
       DETECTOR PARAMETER, not a property of the stream. Establish from the call sites what
       value the published campaign actually passed, per experiment. If `p_pre != p_true`,
       the recursion carries a built-in drift of `p_true - p_pre` per step under the null and
       every `ARL_0` computed at `p_true` is the wrong quantity.
  (iii) `p_0^S1` — the value S1 assumed, `0.05`.
Report which of the three enters each formula. `theta*` and `ARL_0` are properties of the
pair `(p_pre, p_true)`, not of a single rate.

**Output table.** Columns, per the arbitration: `0.005 / p_0^S1 = 0.05` (superseded),
`0.01 / p_0^S1 = 0.05` (A1), `0.01 / p_true = 0.024` (principal), plus a sensitivity band.
The band's endpoints are NOT stated in advance: derive them from a named estimator and a
named quantile of the measured pre-drift rate, and print the estimator with the band. The
`0.012`-`0.040` range asserted here has no provenance in the artifact — `p0_hat_median` is
flat at `0.023`-`0.024`; if the spread is the per-seed dispersion rather than the
per-magnitude median, say so and quote the quantiles used. `eps = 0.05` is never measured
either; S2 states it as an assumed miss level and reports `ARL_0` sensitivity to it in the
same table rather than leaving the assumption silent.

**Carry the numerical root, drop the approximation.** `2 delta_P / (p_0(1-p_0))` degrades
`+6.2 % -> +12.1 % -> +25.3 %` across the three settings. It is removed from
`transfer_S1.md`, and never enters `prop3_v2.tex`.

**T2.0(d) — restitution, not re-evaluation.** The three lines marked
`NOT RECOMPUTED, blocking for S2` are stated through the withdrawn rectangular surrogate.
They are restated against the measured ceiling `A_swap`
(`tables/envelope_stats.json`, `tables/cusum_delta001_quantiles.csv`), not recomputed at
`0.01`:
- budget invariance `K = 18.5`, `A in [16.8, 18.1]` -> measured ceiling `19.2` to `36.6`,
  factor `1.90`, non-monotone with a hump at `Delta_e ~ 0.19` (S6 §4). The claimed plateau
  is not what was measured.
- `lambda_starve` at the mean window -> restated at `delta_P = 0.01` with `W` from the
  artifact, and declared `p_0`-invariant under `eq:starve_boundary`.
- universal floor -> recomputed through `thm:floor` with `alpha = W/ARL_0` at the new
  `ARL_0`, which moves by up to six orders of magnitude.

**Gate verdict, reported before Phase 2 starts.** Both readings of `lambda_FA` against
`lambda_op = 21.9283`, CI `[19.876, 22.398]` — and the rule that `\LambdaFA = 15` is
annotated `R4_PHT_LAMBDA, ProteuS pre-drift calibration`, an empirical quantity that no
recomputation of `ARL_0` mechanically displaces. If the empirical reading stands alone,
`res:tension` and `rem:envelope` hold unchanged and that is the verdict.

Deliverable: `docs/theory/S2_arl0_recomputation.md` — old/new side by side, the
`lambda_FA` verdict, and the reproduction command.

**GATE CHECKPOINT T2.0 — HARD STOP, HANDOVER TO S3.**
On completion of Phase 1, and before Phase 2 begins:
1. Commit `docs/prompts/s2-decision-rules.md`, `experiments/S2_theory/s2_arl0.py` and
   `docs/theory/S2_arl0_recomputation.md` on the stream branch.
2. Print, in the terminal, the column table and the `lambda_FA` verdict.
3. STOP. Wait for the operator. Do not begin Phase 2.
The verdict is emitted **through rule R2 and only through it**: `EMPTY` above `22.398`,
`NON-EMPTY` below `19.876`, `UNDECIDED` in between. The point estimate `21.9283` is NEVER
the decision variable. `UNDECIDED` is a terminal, publishable verdict — never a reason to
resample until the interval separates. That is the knife edge S6 avoided at `15.219`
against `15.00`, and it would be reintroduced here by any rule that reads the point estimate.
Report both readings of `lambda_FA` — the empirical `R4_PHT_LAMBDA = 15`, invariant by
construction, and the theoretical `ARL_0^{-1}(target)` — and say which one carries the
verdict and why.

---

## Phase 2 — T2.2, `W` as a random variable

Proposition 9 is faulted by reviewer #1 for exactly this; reproducing it in Proposition 3 is
disqualifying.

**`experiments/S2_theory/s2_w_random.py`.** Reads `results/S6_synchronized_traces/data/`
`runs.parquet` (8,000 rows, arm `full` = 2,000; columns `tau_erase`, `tau_erase_fw`,
`w_fw`, `kappa`, `e_pre`). Integrates

`E_W[ W exp(-2/W (lambda - s_0 - mu W)_+^2) ]`

over the empirical distribution of `W` per magnitude, with right censoring at
`T_h = ssot.S6_T_HORIZON = 2500` handled explicitly, not dropped.

**Reuse, do not rebuild.** `experiments/S6_synchronized_traces/s6_predictive_power.py`
already carries a hand-rolled right-censored log-normal MLE — `neg_log_likelihood` (L74)
and `aft_lognormal` (L85), `scipy.optimize.minimize`, deterministic start at the OLS
solution on the uncensored subset. Import that rather than adding `lifelines` (installed at
0.30.3, and unnecessary). Report both estimators: the plug-in empirical integral treating
censored runs at their censoring time, and the parametric log-normal integral extrapolating
past the horizon. They bracket the answer.

Verify the censoring fraction on the arm actually used before quoting it: `S6_causal_evidence.md`
§2 reports `8.2 %` on `n = 1974`, which is the AFT's complete-case subset, not the 2,000-run
arm.

Report the gap between the deterministic-`W` bound and the integrated bound, per
`lambda in {8, 15, 25, 50}`.

---

## Phase 3 — T2.1, the domain where Eq. (4) bites

`prop:starvation` is sound after the v64 repair (Azuma–Hoeffding + Doob + union bound, the
`sqrt(W/2 ln(W/eps))` margin kept, `s_0` explicit). The defect is the window.

- **(a) Domain.** At `Delta_e = 0.3268`, `delta_P = 0.01`, `mu = 0.3168`:
  `W = tau_swap^(1/M) = 57.4` gives `mu W = 18.2` and a bound near `3e-16`;
  `W = tau_erase = 611.9` gives `mu W = 193.8`, positive part zero, bound `>= 1`. Vacant.
  `rem:transient_length` (L236) already records this with macros `\SixMuWfirst = 18.2` and
  `\SixMuWerase = 194`. **Verify it is correct and sufficient** — it is, and the finding is
  that the failing hypothesis is the constant accumulation rate `mu`, not the fluctuation
  term. Formalise the domain as `{(W, lambda) : mu W < lambda}` with the `lambda` ladder of
  `{8, 15, 25, 50}` tabulated against the three `W` estimators.
- **(b) Load-bearing statement.** `prop:certificate` (L240) is deterministic, uses no
  distributional assumption, and its chain `S_max(H) >= A_swap >= A_sig(H) - H delta_P`
  carries the published result — `def:decoupling` (i-bis) and `res:tension` both route
  through `A_swap`, and S6 §6 states outright that `W*` is the wrong sufficient statistic.
  `prop:certificate` is load-bearing; `prop:starvation` is a scope statement about where a
  fluctuation argument can still say anything. Say so in the text, with the reason.
- **(c) The removal branch, arbitrated explicitly.** Argue both sides in
  `prop3_v2.tex`: keeping Eq. (4) costs a proposition that is vacant at the measured
  operating point and invites the reviewer to ask why it is there; removing it costs the
  only statement that quantifies the fluctuation margin and the only bridge to
  `rem:sufficient`'s post-transient reading. Recommendation to be fixed by R3 of the
  decision rules **before** the domain table is read, not after.

---

## Phase 4 — T2.3, flooding restated through `ARL_0`

`notation_map_v63_to_v2.md` marks `rem:flooding` *modified, stream S2, restated through
`ARL_0`*. Rewrite it in place at L329–331 (outside the exclusion):

- after recovery every alarm is a false alarm at rate `~ 1/ARL_0`;
- **retrodiction test.** INSECTS `gradual_balanced`, `Delta e ~ 0.45`, single transition:
  PHT+ARF(`c=1`) 86 alarms / precision 0.012 / F1 0.02 against PHT+HT 7 alarms / precision
  0.14 / F1 0.25, ratio `10.57x`, sign test `p ~ 2e-9` (L497). The `ARL_0` model must
  recover `86` from stream length and the recomputed `ARL_0` at `p_0 = 0.024`,
  `delta_P = 0.01`, `lambda = R4_PHT_LAMBDA = 15` — or the gap is explained. A stated
  caveat applies and is declared, not hidden: R4/R5 run River's adaptive mean-tracking PHT
  at `DELTA_P = 0.005`, not the fixed-`p_0` StrictCUSUM of `eq:cusum`; the manuscript
  already flags that distinction at L489. The retrodiction is therefore an order-of-magnitude
  consistency check on a different estimator, and is labelled as such.
- **the causal contradiction.** L330 still attributes both regimes to "one root cause --- the
  hyper-reactive internal ADWIN". The abstract, S6 §5 and `\LearnShare` say the opposite.
  Rewrite to the measured decomposition. This is the same correction T2.6 asks for, at the
  one site that still carries the error.
- "permanent erasure": already absent (L275). Record as verified.

---

## Phase 5 — T2.4, `R_EDDM`

The normal approximation on geometric inter-error distances predicts detection at `W = 155`;
the experiment reports `F1 = 0.00` (L455). `experiments/S2_theory/s2_eddm.py` models the
running-maximum-with-reset dynamics: EDDM tracks `p_i + 2 s_i` against its running maximum
`p_max + 2 s_max`, and the reset on warning is what the normal approximation omits.

Two admissible exits, fixed by R5. If no closed form reproduces the measured collapse,
**withdraw `R_EDDM` from the instantiation of `R`** in `framework_v2.tex`'s family block
(`eq:Rcusum` / `eq:Radwin` / `eq:Rkswin` — EDDM is currently absent from that block, and the
claim lives in `related_work_v2.tex` L108 and the live `.tex` L151). Withdrawing the
*requirement* `R_EDDM` does not withdraw the *empirical* EDDM result at L454–455, which
stands on its own measurement; the text must separate the two explicitly.

---

## Phase 6 — T2.5, `ass:repair` verification and the three proofs

Action A7 withdrew the assumption. **Do not withdraw it a second time.** Verify:

- **(a)** sweep `framework_v2.tex` for statements still leaning on "no recovery without
  replacement". `rem:order` (L93–119) documents the withdrawal explicitly and
  `prop:order` (L84–91) is restated on the measured condition. Confirm nothing else does.
- **(b)** `prop:order` and `def:kappa` are now backed by a measured condition
  (`tau_erase >= tau_swap^(1/M)` in 1,835/1,836 estimable runs, 2,000/2,000 under the
  hysteresis estimator; `kappa >= 1` at median 14.6). Check they remain provable **under that
  condition** and not under the withdrawn assumption — `tau_err` quantifies over all
  `s >= t`, which is what makes transient dips immaterial. Write the argument out.
- **(c)** proof status, journal target:
  - `thm:floor` — **already proved** in `framework_v2.tex` L196–209. Audit the chain-rule
    step and the `d(x||y) <= (x-y)^2/(y(1-y))` bound at `p_0 = 0.024` rather than `0.05`.
  - `prop:invariance` (L148–153) — **no proof**. Deliver it, and reconcile with the
    measurement: S6 §4 measures the constant at `19.2`–`36.6` with a hump, against the
    claimed `[16.8, 18.1]` plateau. The proof assumes `alpha = 1` exactly; measured
    `alpha_ARF ~ 0.98`. State the condition the proposition holds under.
  - `cor:split` (L233–240) — **no proof environment**. Deliver it.
  Any of the three that cannot be produced is declared explicitly under R6.

---

## Phase 7 — T2.6, the causal statement

One sentence, sourced on the arms, handed to the writing stream. Do **not** edit the
abstract — it is out of perimeter, and it already carries the corrected statement.

> Internal ADWIN hyper-reactivity fixes the onset of adaptation, not the erasure mechanism:
> 99.3 % of the evidence erased (`E_learn` 819.2 / `E_total` 826.7, n = 1979, IQR
> [0.987, 0.998]) is the work of ordinary incremental learning by the `M-1` surviving
> trees — the `frozen` arm, which stops learning, does not erase; the `no_swap` arm, which
> stops replacing but keeps learning, does.

Deliver it in `docs/theory/transfer_S2.md` with the three-arm sourcing, and note that the
one site still contradicting it (`rem:flooding` L330) is repaired in Phase 4.

---

## Statutory guard-rail — run before any hypothesis is declared destroyed

Two input classes, both in `tests/test_S2_theory.py`:

- **Degenerate.** `W = 0`, `W = 1`, `lambda = 0`, `Delta_e = delta_P` (so `mu = 0`),
  `sigma = 0`, and both `p_0 -> 0` and `p_0 -> 1` in `thm:floor`, where `p_0(1-p_0)` sits in
  the DENOMINATOR of the KL bound `Delta_max (A + W delta_P) / (p_0(1-p_0))`. The expected
  behaviour is therefore that the KL bound diverges and the floor becomes vacuous at both
  ends, not that it tightens. A test asserting the opposite sign passes on a wrong premise.
- **Specific matrix.** `W` at powers of two; `Delta_e` approaching `delta_P` from above;
  `lambda` near `mu W`; and `Delta_e >= 0.452`, where S6 §3 measures `A/A_rect` at `-0.15`
  and `-14.12` — **the budget is negative**, because the adapted ensemble ends the window
  below its pre-drift error rate (`err_post_mean` 0.010 against `e_pre` 0.024 at
  `Delta_e = 0.498`). Any bound assuming `A > 0` must state that it is void there.

---

## Deliverables

| #   | path                                     | content                                                                            |
| --- | ---------------------------------------- | ---------------------------------------------------------------------------------- |
| 1   | `docs/manuscript/sections/prop3_v2.tex`  | Prop. 3 domain, load-bearing arbitration, `W` as random variable, the three proofs |
| 2   | `docs/theory/S2_arl0_recomputation.md`   | old/new tables, `lambda_FA` verdict, T2.0(d) restitution                           |
| 3   | `docs/theory/S2_numerical_validation.md` | guard-rail matrix, reproduction commands, artifact hashes                          |
| 4   | `docs/prompts/s2-decision-rules.md`      | R1–R6, committed before measurement                                                |
| 5   | `docs/theory/transfer_S2.md`             | state transfer, causal statement, open items forward                               |

Patches to existing `.tex` / `.md` / `.py` are emitted as SEARCH/REPLACE diffs, nine tildes,
target file named, three to four lines of context, anchors re-grepped — never a line number
carried across a version.

---

## Verification

```bash
cd /home/m53/TheBlindSpotParadox-Experiments
P=/home/m53/miniforge3/envs/Trading/bin/python

# 1. theory recomputation, self-checking
PYTHONHASHSEED=0 $P experiments/S2_theory/s2_arl0.py
PYTHONHASHSEED=0 $P experiments/S2_theory/s2_w_random.py
PYTHONHASHSEED=0 $P experiments/S2_theory/s2_eddm.py

# 2. registry and non-regression
PYTHONHASHSEED=0 $P -m pytest tests/test_S2_theory.py tests/test_S7_consistency.py \
                              tests/test_manuscript_integrity.py -v

# 3. committed artifacts unchanged
sha256sum -c results/audit_S7/_baseline/artifacts_sha256_pre_ssot.txt

# 4. the manuscript still compiles
tectonic docs/manuscript/$(cat docs/manuscript/CURRENT)
```

Every new module carries an `assert`-based self-check under `__main__`, matching the S6
convention (`s6_defs.py`, `s6_detectors.py`, `s6_writer.py` each run one). The Cramér solver
is certified against the `0.005 / p_0 = 0.05` pair, which `transfer_S1` states reproduces
exactly — that reproduction is what licenses the other columns.

Any change to an artifact under `results/` is declared in
`results/audit_S7/_baseline/authorized_deviations.txt` with motive and measured effect.
S2 writes only new artifacts under `results/S2_theory/`, so the frozen reference should
verify untouched; if it does not, that is a defect and execution halts.

---

## Residual risks

1. **`lambda_FA` may come back `UNDECIDED`.** The bootstrap interval `[19.876, 22.398]`
   straddles plausible re-derivations. R2 makes that a publishable verdict rather than a
   loop; the alternative — narrowing the interval by resampling until it separates — is the
   knife-edge failure S6 avoided.
2. **The integrated Prop.-3 bound is expected to be vacant.** Censored runs contribute `1`
   to the integrand, so the bound exceeds the censoring fraction by construction. That is a
   result about the bound, not a bug, and it strengthens the case for `prop:certificate` as
   load-bearing. It should not be presented as a repair of Eq. (4).
3. **`prop:invariance` may not survive its own proof at the measured constant.** The
   proposition claims `A -> K` under an exact `alpha = 1` power law; measurement gives
   `alpha ~ 0.98`, a hump rather than a plateau, and a constant `1.0x` to `2.0x` above the
   claimed band. The honest outcome may be a conditional statement, not the clean asymptotic.
4. **The flooding retrodiction crosses estimators.** R5's PHT is River's adaptive
   mean-tracking variant at `DELTA_P = 0.005`; `eq:cusum` is fixed-`p_0` StrictCUSUM at
   `0.01`. An order-of-magnitude agreement is the most that can be claimed, and the claim
   must say so.
5. **`transfer_S1`'s third column may not reproduce.** It has no code provenance anywhere in
   the repository. R1 fixes the tolerance in advance so that a mismatch is reported rather
   than absorbed.
