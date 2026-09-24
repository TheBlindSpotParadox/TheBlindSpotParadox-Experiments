# Stream S2-ter — decision rules, fixed before any computation

Committed before any S2-ter test is run and before any S2-ter output is read. Every rule carries its
threshold and its verdict on both sides, so no outcome can be arbitrated after the fact. Parts A to
C are what the mandate orders rendered first: the nomenclature of `W` (T3), the arbitration of the
blind-spot predicate (T1), and the requirement of the windowed family in `Delta_e` (T2).

Stream branch `stream-s2ter`, parent `19b9bde`. Mandate: `docs/prompts/PROMPT_S2-ter.md`.

Base state, measured before this file was written. `PYTHONHASHSEED=0 pytest tests/ -q` returns
**156 passed**, not the 154 the mandate names: the difference is the two tests of
`tests/test_debt_register.py`, committed at `b106f83` after the S9 / S11-a / S8 merge pass the
mandate refers to. No test fails. `sha256sum -c results/audit_S7/_baseline/artifacts_sha256_pre_ssot.txt`
returns 27 OK and 7 FAILED, the seven being the declared deviations.

Write perimeter, as arbitrated by the orchestrator for this stream:

- written: this file, `docs/theory/S2ter_*.md`, `docs/theory/transfer_S2ter.md`,
  `tests/test_S2ter_*.py`;
- T3, label correction only, in exactly four files: `results/S2bis_calibration/tables/s2bis_proteus_gate.json`,
  `docs/theory/transfer_S2.md`, `docs/theory/S2_arl0_recomputation.md`,
  `docs/manuscript/sections/framework_v2.tex`. "All or none" binds inside these four files;
- the minimal change to `tests/test_S9_coverage.py` that keeps the suite green once
  `rem:split_measured` is relabelled (§A.4);
- one appended erratum line under table A.1 of `docs/prompts/s9-decision-rules.md`, the
  pre-registered rows untouched;
- forbidden: the four inline subsections `CLAUDE.md` excludes; `results/S2_theory/tables/s2_gate_T20.json`,
  `config/experiment_ssot.py`, `experiments/S9_detector_coverage/s9_family_ordering.py` (stream
  S10 runs in parallel) and every other frozen artifact. A carrier outside the four files is a
  charge in `docs/theory/transfer_S2ter.md`, never an edit.

The live manuscript and every section fragment are read-only except the two relabelled lines of
`framework_v2.tex`. T1, T2 and T4 are delivered as unapplied payloads.

---

## Part A — the symbol `W`: seven acceptions, one naming convention (T3)

### A.1 Correspondence table

S9's gate tabulated four quantities under `W` (`docs/prompts/s9-decision-rules.md` §A.1) and S9's
D0 found a fifth. A census of the live text, the section fragments, the SSOT and the S6 / S9 code
finds seven. The two beyond the mandate's five are declared here rather than absorbed.

| # | acception | symbol under the convention | code / JSON name | value at the canonical point (`Delta_e = 0.326793`, arm `full`) | carried by |
|---|---|---|---|---|---|
| 1 | exploitable transient `tau_erase - tau*` of `def:times`; also the horizon of the windowed false-alarm level of `def:monitor` (`alpha = W / ARL_0`), which `def:requirement` sets to the same `W` | `W` alone; estimators `W_fw`, `W_argmax` | `w_fw` / `tau_erase_fw`; `tau_erase` (argmax surrogate), `runs.parquet` | `W_fw`: median `1 995.5`, mean `1 818.8`, 94/100 finite; `W_argmax`: mean `611.87` (`\SixTauErase = 612`) | `framework_v2.tex` `def:times`, `def:monitor`, `def:requirement`, `eq:Rcusum`–`eq:Rkswin`; `prop3_v2.tex` |
| 2 | KSWIN sliding window | `W_win` | `window_size`, `S9_KSWIN_WINDOW` | `100` | `exp_R4_main_table.py:167` |
| 3 | smoothing buffer upstream of KSWIN (R4) | `W_buf` | `S9_KSWIN_BUFFER`; lag `W_buf / 2` = `KSWIN_LAG` | `30`; lag `15` | `exp_R4_main_table.py:147`, `:52`; `.tex:500` (`W/2=15`) |
| 4 | KSWIN statistic size, each of the two samples | `n_stat` | `stat_size`, `S9_KSWIN_STAT` | `30` | `exp_R4_main_table.py:167` |
| 5 | first-swap time `tau_swap^(1/M) - tau*`, a lower bound on `W` (`prop:order`) | `tau_swap^(1/M)`, never `W` | `tau_swap_1_over_M` (`tau_swap_q010` in `runs.parquet`) | mean `57.38`, published `57.4` | every published requirement numeral: `rem:split_measured`, `rem:floor_band`, `s2bis_proteus_gate.json`, `s2_gate_T20.json` |
| 6 | trailing window of the `e_bar_t` estimator in S6 | `W_err` | `S6_ERR_WINDOW` (commented `# W`); hysteresis `W_err / 2` | `200`; hysteresis `100` | `config/experiment_ssot.py:237`; `s6_defs.py`; `rem:order` ("the 200-step window") |
| 7 | ADWIN's two sub-windows | `W_0`, `W_1`, ADWIN's own notation, always subscripted | internal to River | adaptive | `.tex:481` |

### A.2 Naming convention

1. `W` alone denotes acception 1 and nothing else.
2. A numeral of acception 1 names its estimator (`W_fw`, `W_argmax`). A bare `W` with a value is
   admissible only where the estimator is stated in the same sentence or table header.
3. A quantity that is not an estimator of acception 1 and is substituted into a `W` slot of a
   formula is written under its own symbol, with the substitution stated:
   `tau_swap^(1/M) = 57.4 in place of W`. Acception 5 is a lower bound on `W` (`prop:order`), so a
   requirement evaluated there is evaluated at a lower bound of its own `W`.
4. Acceptions 2, 3, 4, 6 and 7 always carry their subscript or their own name; none is written `W`.
5. In JSON and code, `W` is reserved for acception 1; the other names are those of the table. A
   legacy key `W` carrying acception 5 survives only as a backward-compatible alias beside the
   explicit key, marked by `"W_alias_of": "tau_swap_1_over_M"`.

### A.3 What counts as a carrier

A carrier is a site that presents the numeral of acception 5 (`57.4`), or a numeral evaluated at it,
under a bare `W`, without stating the substitution. A site that names `tau_swap^(1/M)` in the same
sentence or header is not a carrier (`prop3_v2.tex:41`; `s2_w_random.json`
`"W_estimator": "tau_swap^(1/M)"`; `S2_arl0_recomputation.md:212`, header `W = tau_swap^(1/M)`).
Other streams' historical inputs quoted as such (S1's `W = 55`, `W = 13`) are not acception 5 and
are out of scope.

### A.4 Census and disposition, fixed before the pass

Established by `git grep` over tracked files, CSV and Parquet excluded.

**Corrected** by S2-ter, one pass, one commit, labels only, no numeral changed:

| file | site | label change |
|---|---|---|
| `docs/manuscript/sections/framework_v2.tex` | `rem:floor_band`, L308 | `$W = 57.4$` → `$\tau_{\mathrm{swap}}^{(1/M)} = 57.4$ in place of $W$` |
| idem | `rem:split_measured`, L372 | idem; the statement covers every `W` slot of the remark: `alpha = W/ARL_0`, `R_ADWIN` and the `eps` margin |
| `docs/theory/transfer_S2.md` | L93 | `` `W = 57.4` `` → `` `tau_swap^(1/M) = 57.4` in place of `W` `` |
| `docs/theory/S2_arl0_recomputation.md` | L120 | idem |
| idem | L263–266: the floor `1.80` and `sqrt(W/2 ln(1/eps)) = 9.3`, both evaluated at `57.4` under a bare `W` | the substitution stated once in that sentence |
| `results/S2bis_calibration/tables/s2bis_proteus_gate.json` | `cor_split_crossings.at`, `family_requirements_at_lambda_eq.at` | `"W": 57.4` kept as alias; `"W_alias_of": "tau_swap_1_over_M"` and `"tau_swap_1_over_M": 57.4` added at their sorted positions, the file byte-identical to `json.dumps(indent=2, sort_keys=True)` of its content |

Consequence for the tests, decided here. `transfer_S9.md` S9-A anchors on the line
`rem:split_measured` relabels, and `test_transfer_S9_anchors_resolve_exactly_once` requires every S9
anchor exactly once. The test is changed minimally: an S9 anchor that S2-ter relabels is accepted
only when the original line is absent **and** the relabelled line stands exactly once.
`transfer_S9.md` is not edited; the part of S9-A the label does not cover is re-issued as an S2-ter
charge, anchored on the relabelled line. S9-A's own wording, "used in place of `W` in the `eps`
margin", is narrower than the fact: `57.4` fills every `W` slot of the remark.

The generator of the gate JSON (`s2bis_proteus_calibration.py`) is outside the perimeter and does not
emit the two added keys. A re-run drops them without changing a numeral, and
`tests/test_S2ter_predicate.py` then fails, which is the intended alarm. Declared debt.

**Charged**, not edited (`docs/theory/transfer_S2ter.md`):

| site | carrier |
|---|---|
| `results/S2_theory/tables/s2_gate_T20.json` `eps_sensitivity.at.W`, `floor_and_family.at.W`; generator `experiments/S2_theory/s2_arl0.py:336,352` | the source of `rem:split_measured`'s table (`common_alpha_ladder`) and of the floor band `[13.88, 18.29]` |
| `experiments/S2bis_calibration/s2bis_proteus_calibration.py:311,352,368,390,600` | emits `"W"` for acception 5 |
| `docs/theory/S2bis_narrative_payload.md:20,227` | `W = 57.4` |
| `config/experiment_ssot.py:536,541,566` | `S9_W_TRANSIENT_REF = 57.4`; "the exploitable transient is 57.4"; "the measured transient W = 57.4" |
| `experiments/S9_detector_coverage/s9_offline_detectors.py:121,151`; `s9_requirement_lattice{,_smoke}.json` | acception 5 in the key `W_used_for_margin` |
| `experiments/S9_detector_coverage/s9_family_ordering.py:17,232,276`; `s9_family_ordering{,_rotation,_smoke}.json` | `levels.anchor.W` (a copy of the gate's `at` block) and `equalisation_transposition` "(W = 57.4, ...)" |
| `docs/plans/PLAN_S9.md:54`; `docs/prompts/s9-decision-rules.md:34,190` | plan and pre-registration: not rewritten; the gate receives one appended erratum line |
| `docs/theory/transfer_S9.md` S9-A | superseded by the relabel; its consequence clause re-issued by S2-ter |
| `articleA_blindspot_v64_camera_ready.tex:481` | acception 7 written `W_0` in the section that also uses acception 1 |

**Not carriers** (acception 5 named): `prop3_v2.tex:41`, `.tex:36` (`\SixTauFirst`),
`thesis_v4.md:172`, `S6_causal_evidence.md:199`, `PLAN_S2.md:274`, `s2_w_random.json`,
`s6_causal.json`, `s9_offline_summary.json` (`W_published_in_requirements` beside
`tau_swap_1_over_M_mean`), the formula test points of `tests/test_S2_theory.py` and
`tests/test_S2bis_calibration.py`, and every S9 document that describes the reattribution.

---

## Part B — T1: the blind-spot predicate generalises

### B.1 The common quantity

**Memory of a monitor.** `m_D` is the largest number of consecutive observed errors whose excess the
statistic of `D` can hold at once. A statistic that scans every window ending at `t` has
`m_D = infinity`: the CUSUM, `S_t = max_{s < t} sum_{u=s+1}^{t} (e_u - p_0 - delta)`, PHT, and
ADWIN, whose recent sub-window grows until a cut. KSWIN compares a reservoir draw with its `n_stat`
most recent observations: `m_D = n_stat`.

**Readable budget.** For `m` in `N ∪ {infinity}`,

```
A_m := max_{tau* < t <= tau_erase}  sum_{s = max(tau*+1, t-m+1)}^{t}  ( e_bar_s - p_0 - delta_D )^+
```

with `delta_D` the monitor's drift tolerance: `delta_P` for PHT and the CUSUM, `0` for KSWIN, which
has none. Properties: (i) `m -> A_m` is non-decreasing; (ii) `A_m <= A`, with equality for
`m >= W`, so `A_infinity = A` of `def:budget`; (iii) for a rectangular transient of height `Delta_e`
and duration `W`, `A_m = (Delta_e - delta_D) min(W, m)`.

**Predicate.** `(C, D)` exhibits a blind spot at `(Delta_e, W)` when `A_{m_D} < R(D, eps, alpha)`,
with `def:requirement` read on `A_{m_D}` in place of `A`.

### B.2 Reduction in both cases

- `m_D = infinity` (CUSUM, PHT, ADWIN): `A_infinity = A`, and the predicate is `def:blindspot`
  verbatim, with `eq:Rcusum` and `eq:Radwin` unchanged.
- KSWIN, `m_D = n_stat`, `delta_D = 0`. On a binary error stream the empirical CDF of a sample is
  constant on `[0, 1)`, so the two-sample KS statistic is exactly `|X_R - X_Q| / n_stat`, the
  difference of error counts between the recent sample and the reservoir draw. At its best test
  instant the recent sample holds `min(W, n_stat)` transient steps against a pre-change reservoir,
  so `A_{n_stat} = Delta_e min(W, n_stat)`. The requirement in the same unit is the exact lattice
  level, `R = max(k*(alpha, n_stat), 0.1 n_stat)`, the second term being River's `st > 0.1` guard,
  slack on every declared cell (S9, asserted). The predicate reads `min(W, n_stat) Delta_e < k*`:
  S9's contrast model, identically.

### B.3 Why the split (b) is not retained

1. An assignment by type of statistic ("integrated accumulation" against "two-sample contrast")
   misassigns ADWIN. ADWIN is a two-sample contrast between two sub-window means, but its recent
   sub-window grows to the length of the transient, so its evidence integrates, and `eq:Radwin`
   charges it against `A` with a `sqrt(W)` price. A contrast predicate at a fixed window cannot
   express that.
2. The only criterion that assigns CUSUM, PHT, ADWIN and KSWIN correctly is `m_D` itself. With it,
   (b) is (a) restricted to `m_D in {n_stat, infinity}`.
3. (a) covers every finite-memory statistic (a sliding-window CUSUM, a fixed-window two-proportion
   test) without a third predicate.
4. The loop produces the whole profile `m -> A_m`, a property of classifier and stream; the monitor
   only selects its argument, as it already selects `delta_P`. `def:blindspot` stays
   implementation-free in the sense of S8-H. `thm:floor` bounds every monitor through `A` and is
   unchanged; `cor:split` is a statement about the `alpha`-price of `R` and is unchanged.

**Decision: (a) GENERALISATION**, subject to rule E1.

### B.4 Declared before measurement

- **Predictive equivalence.** (a) and (b) make the same KSWIN prediction on every S9 cell, because
  both reduce to the contrast predicate. The three grids validate that shared predicate; they cannot
  discriminate (a) from (b). The arbitration rests on B.3.
- What (a) adds that is testable on committed data and has not been examined: the direction of B1's
  errors as a function of `W` (rule E2), derived in Part C.
- What changes in the text if (a) is retained: the gloss of `def:budget`, "never on the monitor beyond
  the scalar `delta_P`", becomes "beyond the pair `(delta_D, m_D)`"; `eq:Rkswin` remains KSWIN's
  false-alarm price and what it is compared with becomes `A_{n_stat}` instead of `A`.

---

## Part C — T2: the requirement of the windowed family in `Delta_e`

Rectangular transient, binary errors, pre-change rate `p_0`.

- Windowed family (Part B): detection iff `Delta_e >= Delta_e_KS(W) := k*(alpha, n) / min(W, n)`.
- `eq:Rkswin` read as a condition on `A = (Delta_e - delta_P) W`: detection iff
  `Delta_e >= Delta_e_B1(W) := delta_P + [R_fa + sqrt((W/2) ln(1/eps))] / W`, with
  `R_fa = sqrt(n ln(2/alpha))`.

Regimes:

1. **`W <= n`, coincidence.** Both thresholds scale as `1/W`: both read an integrated count against a
   critical count. They differ by the lattice (`k*` against `R_fa`, `-0.7 %` to `+4.6 %` at
   `n = 30`), by `eq:Rkswin`'s `eps` margin (at most `sqrt((n/2) ln(1/eps)) = 6.7` at `n = 30`)
   and by `delta_P W` (at most `0.15`). `eq:Rkswin` is the stricter.
2. **`W > n`, divergence.** `Delta_e_KS` saturates at `k*/n`, the lattice critical distance (`0.467`
   at `alpha = 0.005`, `n = 30`), while `Delta_e_B1` keeps falling toward `delta_P`. In budget units
   the windowed requirement is `(k*/n - delta_P) W`, linear in `W`; `eq:Rkswin` grows as
   `sqrt(W)`.
3. **Crossing `W_x(alpha, n, eps, delta_P)`**, where the two thresholds are equal for `W > n`. With
   `u = sqrt(W_x)`, `b = sqrt(ln(1/eps) / 2)` and `c = k*/n - delta_P`, `c u^2 - b u - R_fa = 0`, so
   `W_x = [(b + sqrt(b^2 + 4 c R_fa)) / (2c)]^2`. At `(alpha, n, eps, delta_P) = (0.005, 30, 0.05,
   0.005)`, `W_x = 47.3`. For `W < W_x`, `eq:Rkswin` is conservative: it predicts a miss where the
   windowed family detects. For `W > W_x` it is anti-conservative: it predicts detection of
   amplitudes below `k*/n`, which no transient length makes detectable.

Two frontiers, therefore: `W = n_stat` is structural, where the contrast stops growing; `W = W_x` is
where the sign of `eq:Rkswin`'s error flips.

Both prices of `R_KSWIN` are set by `n_stat`. The `alpha`-price is `k*(alpha, n)`. A `(1 - eps)`
guarantee at one test instant adds a Hoeffding margin on `2 n` bounded terms, `sqrt(n ln(1/eps))`,
free of `W`. The term `sqrt((W/2) ln(1/eps))` of `eq:Rkswin` is the cumulative family's margin,
transplanted onto a statistic that never integrates over `W`. The mean-field form, without an `eps`
margin, is the one S9 measured at `0.931`; the rules below validate that form and select no margin
constant.

Closed-form checks, identities rather than measurements: `k*/Delta_e` places the transition at
`W = 20` for `Delta_e = 0.70` and `W = 14` for `Delta_e = 1.0` (`n = 30`, `alpha = 0.005`), and
`30 x 0.30 = 9 < 14` excludes detection at `Delta_e = 0.30` for every `W`, as S9 §5 states.

---

## D0 — declaration of prior reading

The planning phase read the following before this file was written. Presenting any rule below as
blind to them would be false.

| source | read |
|---|---|
| `docs/prompts/PROMPT_S2-ter.md` | whole |
| `docs/theory/S9_detector_coverage.md`, `docs/theory/transfer_S9.md`, `docs/prompts/s9-decision-rules.md` | whole: every aggregate S9 publishes (`0.863`, `0.800`, `0.850`, `0.931`, `0.954`, `0.932`, `0.798`, `0.730`, the D5 / D7 / D9 tables) |
| `docs/manuscript/sections/framework_v2.tex` | whole |
| `docs/theory/transfer_S2.md`, `docs/theory/S2_arl0_recomputation.md` | whole |
| `docs/theory/transfer_S8.md` | §H, the `res:budget_sufficient` payload |
| `docs/editorial/thesis_v4.md` | §T11a.4 |
| `docs/theory/notation_map_v63_to_v2.md`; `docs/plans/PLAN_S9.md` §P0; `intro_v2.tex` L96–104; `related_work_v2.tex` L80–112; `prop3_v2.tex` L30–52; `S2bis_narrative_payload.md` L15–24, L222–230; `docs/prompts/PROMPT_S10.md` | as listed |
| `results/S2bis_calibration/tables/s2bis_proteus_gate.json` | whole |
| `results/S2_theory/tables/s2_gate_T20.json` | L80–203, which includes the median ceiling at the four largest canonical magnitudes and the `common_alpha_ladder` with its `met_by` flags |
| `results/S2_theory/tables/s2_w_random.json` | L355–385 |
| `results/S9_detector_coverage/tables/s9_offline_summary.json` | L1–60: `W_provenance` and two cells (arm `frozen`, `Delta_e = 0.028186`, ADWIN and KSWIN, detection `0.0`) |
| `results/S6_synchronized_traces/data/s6_causal.json` | the paths of `57.38`, `611.87` and `1 818.79` |
| `runs.parquet`, S6 and S9 rotation | schemas only |
| code | `s9_kswin_dilution.py`, `s9_offline_detectors.py`, `s9_family_ordering.py`, `s6_defs.py` L1–230, `s2_arl0.py` L330–425, `s2bis_proteus_calibration.py` L305–395 and L560–570, `tests/test_S9_coverage.py`, `tests/test_debt_register.py`, parts of `tests/test_S7_consistency.py` and `tests/test_S2bis_calibration.py`, `config/experiment_ssot.py` L515–643 |
| hand computations | `W_x = 47.27` (Part C); `R_KSWIN` at `alpha = 0.005`: `22.679` at `57.4`, `43.68` at `611.87`, `68.08` at `1 995.5` |

Never computed and never read: the agreement of the contrast predicate on the canonical and rotation
grids (no committed code computes it), and any per-cell KSWIN detection rate of those two grids or of
`s9_kswin_dilution.json`.

---

## Common definitions for E0–E4

Input arm `raw` only, S9's model-comparison scope. A cell is **observed to detect** when its
within-transient detection rate is `>= 1 - S9_EPS = 0.95`, the committed definition of
`s9_kswin_dilution.aggregate`. Agreements are exact rationals `agreeing cells / cells`; a displayed
decimal is a rounding of that rational.

| grid | source | cells | `W` per cell | `k*` |
|---|---|---|---|---|
| `G_ctrl` (T9.2) | `s9_kswin_dilution.json`, `input_arm = raw` | 3 840 | declared | the cell's `k_star` |
| `G_can` (T9.1) | `s9_offline_summary.json`, `detector = KSWIN`, `arm = full`, `input_arm = raw`, `threshold` in `S9_KSWIN_ALPHA_GRID` | 80 | `w_median` | `s9_requirement_lattice.json` at `n_stat = 30` |
| `G_rot` (D7) | `s9_family_ordering_rotation.json`, `family = KSWIN`, `setting` in {published, equalised}, `input_arm = raw` | 40 | median finite `w_fw` of the magnitude, rotation `runs.parquet`, arm `full` | exact lattice, `s9_offline_detectors._ks_lattice(30)`, at the file's own `levels.KSWIN` |

On `G_can` and `G_rot` every cell has `W > n_stat` (asserted), so `min(W, n_stat) = n_stat`. There
`A_{n_stat}` is evaluated through its rectangular reduction with the nominal `Delta_e` of the cell:
the trace-level estimator needs the S6 and rotation traces, neither reachable from this worktree.
Declared debt, not a choice made to fit.

B1 on `G_can` and `G_rot`, for E0 only: predicted detection iff
`A >= sqrt(n_stat ln(2/alpha)) + sqrt((W/2) ln(1/eps))`, with `A` the median `a_fw` of the magnitude
(`a_fw_median` on `G_can`) and `W` as above; the published-`W` reading of `G_can` substitutes `57.4`,
the gate's `at.W`.

---

## E0 — reproduction of the numerals S2-ter reuses

| numeral | target | grid, reading |
|---|---|---|
| contrast agreement | `0.931` (`verdicts.model_comparison.contrast_agreement`, 4 d.p.) | `G_ctrl` |
| B1 agreement | `0.850` | `G_ctrl` |
| B1 agreement | `0.863` | `G_can`, `W = w_median` |
| B1 agreement | `0.800` | `G_can`, `W = 57.4` |
| B1 agreement | `0.850` | `G_rot`, published setting |
| B1 and contrast agreement | `1.000` each | `G_rot`, equalised setting |

| condition | verdict |
|---|---|
| the recomputed rational rounds to the target at the printed precision | **REPRODUCED** |
| it does not | **UNREPRODUCED**: both numbers printed side by side; no definition above is altered to recover the target |

`UNREPRODUCED` on a B1 row is published and does not stop the stream, since E1 does not read B1.
`UNREPRODUCED` on the contrast row of `G_ctrl` halts E1, whose threshold is that number.

## E1 — T1: is the generalised predicate retained?

Per grid `G`, `acc_a(G)` is the agreement of `A_{n_stat} >= R` and `acc_c(G)` that of
`min(W, n_stat) Delta_e >= k*`, on the same cells, against the same observation.

| condition | verdict |
|---|---|
| `acc_a(G) >= acc_c(G)` on each of the three grids, **and** the agreement of (a) over the union of the three grids' cells is `>= acc_c(G_ctrl)`, the exact rational S9 publishes as `0.931` | **RETAINED** |
| either fails | **NOT RETAINED** |

The global threshold is the exact rational, not the decimal `0.931`: a rational such as
`3575 / 3840 = 0.93099` displays as `0.931`, and comparing it with `0.931` would fail the rule by
rounding alone. `NOT RETAINED` is terminal: (b) is not substituted, because its windowed predicate is
the same contrast predicate and would fail identically; the failing grid and its cells are
published.

## E2 — T2: does the sign of `eq:Rkswin`'s error follow the `W_x` frontier?

On `G_ctrl`, each cell is placed by its `W` against `n` and against `W_x(alpha, n, S9_EPS, DELTA_P)`
(Part C, `R_fa` asymptotic as in `eq:Rkswin`, `k*` exact). Among the cells where B1 disagrees with
the observation, a **false miss** is "B1 predicts a miss, the cell detects", a **false detection**
the converse.

| regime | prediction | verdict |
|---|---|---|
| `W <= n` | `>= 90 %` of B1's disagreements are false misses | **CONFIRMED** / **REFUTED** |
| `n < W < W_x` | `>= 90 %` false misses | **CONFIRMED** / **REFUTED** |
| `W >= W_x` | `>= 90 %` false detections | **CONFIRMED** / **REFUTED** |
| a regime with no B1 disagreement | — | **NOT PRODUCED** for that regime |

The closed form is also checked against the direct sign of `Delta_e_B1(W) - Delta_e_KS(W)` on every
cell; a cell where the two disagree is a defect of Part C and is published as one.

## E3 — T3: is the relabel label-only, or does it bear a verdict?

`s2_arl0.floor_and_family` is re-used as it stands, at `Delta_e = 0.326793`, band `[0.015, 0.032]`,
`lambda = 50`, `n_stat = 30` and the ceiling `33.5115` (the gate's
`measured_ceiling_median_A_unrefl`). For each `lambda` of `s2_arl0.LAMBDA_LADDER` it returns
`alpha = W / ARL_0(lambda)`, `R_CUSUM`, `R_ADWIN`, `R_KSWIN` and their `met` flags, `R_KSWIN` at the
deployed `alpha`, and the chord floor band. It is evaluated at three readings of the `W` slot:

- `57.4`, acception 5 (the gate's `at.W`);
- `611.87`, `W_argmax` (`s6_causal.json :: kappa_gate_transfer_S1.erasure_surrogates.argmax_A_unrefl.mean`);
- `1 995.5`, `W_fw` (`s9_offline_summary.json :: W_provenance.w_def_times_median`).

At `57.4` the call must reproduce `s2_gate_T20.json :: floor_and_family.family_requirements.common_alpha_ladder`
and `floor_chord_interval` to `1e-9`; otherwise **UNREPRODUCED**, and E3 halts.

| condition | verdict |
|---|---|
| every `met` flag, the deployed-`alpha` `R_KSWIN` flag included, is the same at the three readings | **LABEL-ONLY** |
| at least one flag differs | **VERDICT-BEARING**: the flags are published per reading and charged against `rem:split_measured` and `rem:floor_band`, whose text S2-ter changes by the label only |

## E4 — T4: do the (C4) payload and its table reproduce from the artifacts?

Every numeral of the (C4) payload and of its ordering table is recomputed: per family and setting,
raw arm, the mean over the 20 magnitudes of `detect_within_W_rate` and of `pre_drift_alarm_rate`,
and the median of `add_median`, from `s9_family_ordering.json` (`p_0` its `D9.p0_median`) and
`s9_family_ordering_rotation.json`; EDDM's arming state at `p_0 = 0` from
`s2bis_proteus_gate.json :: eddm_arming_T_D`.

| condition | verdict |
|---|---|
| every numeral equals its recomputation at the printed precision, and the table carries a `p_0` column | **REPRODUCED** |
| a numeral does not, or the column is absent | **UNREPRODUCED**: the payload is corrected to the artifact, never the converse |

---

## Terminal states

`NOT RETAINED`, `UNREPRODUCED`, `REFUTED`, `NOT PRODUCED` and `VERDICT-BEARING` are legitimate
terminal states of this stream. None is replaced by a re-run at other settings, a widened tolerance,
a different observation threshold, or a derivation presented as a measurement.
