# Stream S2-ter — the blind-spot predicate, the windowed requirement, the symbol `W`

Branch `stream-s2ter`, parent `19b9bde`. Decision rules E0–E4, the nomenclature of `W` and the
derivations of T1 and T2 were committed before any computation in
[`docs/prompts/s2ter-decision-rules.md`](../prompts/s2ter-decision-rules.md) (`7084027`). The T3
relabel is `6d4c703`. Payloads and charges: [`transfer_S2ter.md`](transfer_S2ter.md). Every numeral
below is printed by

```bash
PYTHONHASHSEED=0 python tests/test_S2ter_predicate.py
```

and pinned by `PYTHONHASHSEED=0 python -m pytest tests/test_S2ter_predicate.py`. No stream is
simulated and no artifact under `results/` is produced; every input is a committed S2, S2-bis, S6
or S9 artifact.

| rule | verdict | one line |
|---|---|---|
| E0 | **REPRODUCED**, 7/7 | every S9 numeral S2-ter reuses re-derives from the committed cells |
| E1 | **NOT RETAINED** | the generalised predicate equals the contrast predicate on all 3 960 cells, and misses the gate: pooled `3673/3960 = 0.9275` against `715/768 = 0.9310` |
| E2 | **CONFIRMED** / **REFUTED** / **CONFIRMED** | 91/91 false misses for `W <= n_stat`, 478/478 false detections for `W >= W_x`, 7 of 8 false detections between |
| E3 | **VERDICT-BEARING** | at the exploitable transient no requirement of `rem:split_measured` is met at any `lambda` |
| E4 | **REPRODUCED** | every numeral of the (C4) payload and of its `p_0` table re-derives |
| T3 | **APPLIED** | four artifacts relabelled in one commit; seven acceptions of `W` tabulated; eight carriers charged, S9-A superseded |

Base state before any S2-ter file: `pytest tests/ -q` returned **156 passed**, not the mandate's
154. The two extra tests are `tests/test_debt_register.py`, committed at `b106f83`. After this
stream the suite returns 166 passed.

---

## 1. T1 — generalisation argued, not retained

### 1.1 The arbitration (rules, Part B)

The common quantity is the **readable budget** `A_m`: the excess error that a statistic with memory
`m` can hold at once, on the expected trajectory of `def:budget`. It is non-decreasing in `m`, equal
to `A` for `m >= W`, and `(Delta_e - delta_D) min(W, m)` on a rectangular transient. The predicate
`A_{m_D} < R(D, eps, alpha)` reduces to the two known ones:
- to `def:budget` verbatim for the monitors that scan every window (CUSUM, PHT, ADWIN:
  `m_D = infinity`);
- to S9's contrast model identically for KSWIN (`m_D = n_stat`, `delta_D = 0`). On a binary stream
  the two-sample KS statistic is exactly a difference of error counts.

The split (b) was set aside on structure. A criterion by type of statistic misassigns ADWIN, a
two-sample contrast whose recent sub-window grows until it integrates. The only correct criterion is
`m_D`, and with it (b) is (a) restricted to two values. The rules declared in advance that (a) and
(b) predict KSWIN identically on every S9 cell, so the gate below tests the predicate they share.

### 1.2 The gate (rule E1)

Observation: a cell detects when its within-transient rate is `>= 1 - eps = 0.95`, the committed
definition of `s9_kswin_dilution.aggregate`. The agreements are exact rationals.

| grid | cells | generalised = contrast | B1 (`eq:Rkswin`), for reference |
|---|---|---|---|
| `G_ctrl`, T9.2 controlled transient | 3 840 | `715/768 = 0.9310` | `3263/3840 = 0.8497` |
| `G_can`, T9.1 canonical Bernoulli, arm `full` | 80 | `31/40 = 0.7750` | `69/80 = 0.8625` |
| `G_rot`, D7 rotation `eta = 0.05`, published and equalised | 40 | `9/10 = 0.9000` | `37/40 = 0.925` (17/20 and 20/20) |
| **union** | 3 960 | **`3673/3960 = 0.9275`** | — |

The relative condition holds on every grid: the two predicates are the same function of the cell,
asserted cell by cell. The global condition fails, `3673/3960 < 715/768`. **NOT RETAINED.** Per the
committed rule this is terminal: (b) is not substituted, because its windowed predicate is the same
and would fail identically. Neither form leaves this stream validated at the 93.1 % level the
mandate sets.

### 1.3 The failing cells

The rule publishes them. All 22 disagreements of the classifier-driven grids have the same sign.

| grid | `Delta_e` | `alpha` | `k*` | `30 Delta_e` | observed rate |
|---|---|---|---|---|---|
| G_can | 0.390998 | 0.05 | 11 | 11.73 | 0.8878 |
| G_can | 0.415743 | 0.05 | 11 | 12.47 | 0.9495 |
| G_can | 0.436013 | 0.01 | 13 | 13.08 | 0.7677 |
| G_can | 0.436013 | 0.05 | 11 | 13.08 | 0.9495 |
| G_can | 0.452271 | 0.01 | 13 | 13.57 | 0.8400 |
| G_can | 0.465040 | 0.01 | 13 | 13.95 | 0.8878 |
| G_can | 0.474860 | 0.005 | 14 | 14.25 | 0.7347 |
| G_can | 0.474860 | 0.01 | 13 | 14.25 | 0.8878 |
| G_can | 0.482255 | 0.005 | 14 | 14.47 | 0.8081 |
| G_can | 0.482255 | 0.01 | 13 | 14.47 | 0.9293 |
| G_can | 0.487707 | 0.005 | 14 | 14.63 | 0.8400 |
| G_can | 0.491644 | 0.005 | 14 | 14.75 | 0.7900 |
| G_can | 0.491644 | 0.01 | 13 | 14.75 | 0.9100 |
| G_can | 0.494428 | 0.005 | 14 | 14.83 | 0.8100 |
| G_can | 0.494428 | 0.01 | 13 | 14.83 | 0.9100 |
| G_can | 0.496355 | 0.005 | 14 | 14.89 | 0.8400 |
| G_can | 0.496355 | 0.01 | 13 | 14.89 | 0.9200 |
| G_can | 0.497661 | 0.005 | 14 | 14.93 | 0.8500 |
| G_rot | 0.474860 | 0.005 | 14 | 14.25 | 0.9375 |
| G_rot | 0.482255 | 0.005 | 14 | 14.47 | 0.9375 |
| G_rot | 0.491644 | 0.005 | 14 | 14.75 | 0.9403 |
| G_rot | 0.494428 | 0.005 | 14 | 14.83 | 0.9298 |

### 1.4 Reading — post hoc, and no verdict rests on it

Each of the 22 is a detection the predicate promises and the stream delivers in `73.5 %` to
`94.95 %` of runs, short of the `95 %` the observation requires. Each sits just above the boundary:
the contrast statistic exceeds `k*` by `0.08` to `2.08` excess errors.

The predicate places its boundary where the *expected* contrast equals the critical count, which is
the median run, not the `(1 - eps)` level. The rules left that gap open on purpose (Part C): they
validated the mean-field form and selected no margin constant.

The classifier grids expose the gap more than T9.2 does because of where their magnitudes fall. The
canonical magnitudes are `Phi(b / sqrt 2) - 0.5` and saturate: 8 of the 20 lie in
`[0.465, 0.498]`, within about two excess errors of `k*/30` at `alpha` in `{0.005, 0.01}`. T9.2's
magnitudes run evenly from `0.05` to `1.0`.

B1 does better than the contrast predicate on `G_can` (`0.8625`) only because it never promises
detection there: `W_fw` is large enough that, on every cell, the `eps` margin alone exceeds that
cell's budget. It is right on the 69 observed misses and wrong on all 11 detections.

### 1.5 What stands, and what would decide T1

The arbitration of Part B stands as a structural argument: (a) is the only form whose assignment
criterion places ADWIN correctly. The validation does not, and the transfer installs no generalised
`def:blindspot` (S2ter-A).

S9-F's contrast condition enters, if it does, with its measured scope: it governs the controlled
rectangular transient and locates the median run on the classifier-driven families (S2ter-B).

Two quantities would decide T1. Neither is computed here, and each is to be pre-registered by the
stream that takes it:
- a `(1 - eps)` margin for the windowed family, derived on the `n_stat` scale rather than fitted;
- the trace-level `A_{n_stat}` on the classifier-driven grids. It needs the S6 traces, which live
  outside this worktree, and a regeneration of the rotation traces, which exist nowhere.

---

## 2. T2 — the windowed requirement in `Delta_e`, against `eq:Rkswin`

The rules (Part C) derive both conditions in amplitude, on a rectangular transient:
- the windowed family requires `Delta_e >= k*(alpha, n) / min(W, n)`;
- `eq:Rkswin`, read on `A = (Delta_e - delta_P) W`, requires
  `Delta_e >= delta_P + [sqrt(n ln(2/alpha)) + sqrt((W/2) ln(1/eps))] / W`.

| regime | the two conditions | `eq:Rkswin` is |
|---|---|---|
| `W <= n_stat` | both scale as `1/W`; they differ only by the lattice (`-0.7 %` to `+4.6 %`), the `eps` margin (`<= 6.7`) and `delta_P W` (`<= 0.15`) | the stricter: it forbids detections that occur |
| `n_stat < W < W_x` | the windowed one saturates at `k*/n`; `eq:Rkswin` keeps falling | still the stricter |
| `W >= W_x` | they have crossed | anti-conservative: it promises amplitudes below `k*/n`, which no transient length makes detectable |

Two frontiers:
- **`W = n_stat`** is structural: past it, the contrast stops growing.
- **`W_x`** is where the sign of `eq:Rkswin`'s error flips:
  `W_x = [(b + sqrt(b^2 + 4 c R_fa)) / (2c)]^2`, with `b = sqrt(ln(1/eps)/2)`,
  `c = k*/n - delta_P` and `R_fa = sqrt(n ln(2/alpha))`.
  - At the deployed point (`alpha = 0.005`, `n = 30`), `W_x = 47.27`.
  - `W_x > n_stat` on all 16 cells of `S9_NSTAT_GRID x S9_KSWIN_ALPHA_GRID`, and `eq:Rkswin` is
    the stricter at every `W <= n_stat` on all 16 (asserted).

Both prices of `R_KSWIN` are set by `n_stat`, and neither depends on `W`:
- the `alpha`-price is `k*`;
- a `(1 - eps)` guarantee at one test adds `sqrt(n ln(1/eps))`.

The `sqrt((W/2) ln(1/eps))` of `eq:Rkswin` is the cumulative family's margin, transplanted.

**Rule E2**, on the 3 840 cells of `G_ctrl`, reads the direction of B1's errors against those
frontiers:

| regime | false misses | false detections | predicted | verdict |
|---|---|---|---|---|
| `W <= n_stat` | 91 | 0 | false misses | **CONFIRMED** (91/91) |
| `n_stat < W < W_x` | 1 | 7 | false misses | **REFUTED** (1/8) |
| `W >= W_x` | 0 | 478 | false detections | **CONFIRMED** (478/478) |

The closed form and the direct sign of `Delta_e_B1(W) - Delta_e_KS(W)` agree on every cell.

The middle regime is refuted by 8 cells:

| `Delta_e` | `W` | `n_stat` | `alpha` | `k*` | rate |
|---|---|---|---|---|---|
| 0.35 | 80 | 50 | 0.01 | 17 | 0.73 |
| 0.35 | 80 | 50 | 0.05 | 14 | 0.91 |
| 0.40 | 50 | 30 | 0.05 | 11 | 0.93 |
| 0.40 | 80 | 50 | 0.01 | 17 | 0.93 |
| 0.45 | 40 | 30 | 0.05 | 11 | 0.95 |
| 0.45 | 80 | 50 | 0.01 | 17 | 0.93 |
| 0.60 | 30 | 20 | 0.005 | 11 | 0.94 |
| 0.60 | 30 | 20 | 0.01 | 11 | 0.94 |

The prediction assumed that the observation follows the mean-field boundary. Near the threshold it
does not: seven of these cells lie above both mean-field boundaries and are detected in 73–94 % of
runs, the same offset as §1.4. The two outer regimes, where the cells lie far from the threshold,
confirm the frontier map without exception.

---

## 3. T3 — the symbol `W`

### 3.1 Seven acceptions, one convention

The table the mandate asks for is §A.1 of the rules. It carries **seven** acceptions, not the five
the mandate names; the two extra are declared, not absorbed.

| # | acception | symbol | value at the canonical point |
|---|---|---|---|
| 1 | exploitable transient `tau_erase - tau*` (`def:times`); also the horizon of `def:monitor`'s `alpha = W/ARL_0` | `W`, estimators `W_fw`, `W_argmax` | `W_fw`: median 1 995.5, mean 1 818.8; `W_argmax`: mean 611.87 |
| 2 | KSWIN sliding window | `W_win` | 100 |
| 3 | smoothing buffer upstream of KSWIN | `W_buf` (lag `W_buf / 2`) | 30 (15) |
| 4 | KSWIN statistic size | `n_stat` | 30 |
| 5 | first-swap time, a lower bound on `W` | `tau_swap^(1/M)`, never `W` | 57.38, published 57.4 |
| 6 | trailing window of the S6 `e_bar_t` estimator (SSOT comment `# W`) | `W_err` | 200 |
| 7 | ADWIN's two sub-windows (`.tex:481`) | `W_0`, `W_1` | adaptive |

The naming convention (rules §A.2) has four rules:
- `W` alone is acception 1.
- A value substituted into a `W` slot is written under its own name, followed by "in place of `W`".
- Acceptions 2–4, 6 and 7 always carry a subscript or their own name.
- A legacy JSON key `W` carrying acception 5 survives only as an alias, beside
  `tau_swap_1_over_M` and marked by `W_alias_of`.

The S9 gate's table A.1 received one appended erratum line pointing there. Its pre-registered rows
are untouched.

### 3.2 The pass (`6d4c703`)

The pass is one commit and changes labels only; no numeral moves.

| artifact | change |
|---|---|
| `framework_v2.tex` | `rem:floor_band` and `rem:split_measured`: `$W = 57.4$` → `$\tau_{\mathrm{swap}}^{(1/M)} = 57.4$ in place of $W$`. The statement covers every `W` slot of each remark, `alpha = W/ARL_0` included. S9-A's wording, "in the `eps` margin", was narrower than that |
| `transfer_S2.md` | L93, same change |
| `S2_arl0_recomputation.md` | L120, same change; L264, where the floor `1.80` and the margin `9.3` were evaluated at `57.4` under a bare `W` |
| `s2bis_proteus_gate.json` | both `at` blocks: `"W": 57.4` kept as alias, with `"tau_swap_1_over_M": 57.4` and `"W_alias_of": "tau_swap_1_over_M"` added. The file stays byte-identical to `json.dumps(indent=2, sort_keys=True)` of its content, and the value is checked against `s6_causal.json :: kappa_gate_transfer_S1.mean_tau_swap_1m = 57.38` |

The tests change minimally to keep the suite green:
- `test_transfer_S9_anchors_resolve_exactly_once` accepts S9-A's anchor only while the original
  line is gone and the relabelled line stands exactly once;
- `transfer_S9.md` is not edited;
- `at["W"]` still resolves for its two readers, `test_S9_coverage.py` and `s9_family_ordering.py`.

### 3.3 What the relabel implies (rule E3)

`s2_arl0.floor_and_family` was re-used unchanged, at `Delta_e = 0.326793`, ceiling `33.5115`, at
three readings of the `W` slot. At `57.4` it reproduces `s2_gate_T20.json`'s ladder and floor band to
`1e-9`.

| `lambda` | reading | `alpha` | `R_CUSUM` | `R_ADWIN` | `R_KSWIN` | met |
|---|---|---|---|---|---|---|
| 8 | `tau_swap^(1/M) = 57.4` | 1.73e-3 | 17.27 | 27.67 | 23.82 | all three |
| 15 | idem | 1.43e-5 | 24.27 | 31.10 | 28.13 | all three |
| 25 | idem | 1.57e-8 | 34.27 | 35.19 | 32.94 | KSWIN |
| 50 | idem | 6.28e-16 | 59.27 | 43.34 | 42.00 | none |
| 8 | `W_argmax = 611.87` | 1.84e-2 | 38.27 | 90.35 | 42.13 | none |
| 15 | idem | 1.52e-4 | 45.27 | 101.52 | 47.14 | none |
| 25 | idem | 1.67e-7 | 55.27 | 114.90 | 52.39 | none |
| 50 | idem | 6.70e-15 | 80.27 | 141.50 | 61.89 | none |
| 8 | `W_fw = 1 995.5` | 6.01e-2 | 62.67 | 163.17 | 64.93 | none |
| 15 | idem | 4.96e-4 | 69.67 | 183.35 | 70.45 | none |
| 25 | idem | 5.45e-7 | 79.67 | 207.49 | 75.97 | none |
| 50 | idem | 2.18e-14 | 104.67 | 255.54 | 85.73 | none |

`R_KSWIN` at the deployed `alpha = 0.005` is `22.68`, `43.68` and `68.08` at the three readings.
The chord floor band is:
- `[13.88, 18.29]` at `57.4`;
- `[7.11, 11.83]` at `W_argmax`;
- `[-7.33, -2.46]` at `W_fw`, where it is vacuous, because the term `-W delta_P` dominates.

**VERDICT-BEARING.** The relabel is not cosmetic:
- every requirement of the remark is unmet at the exploitable transient, under either estimator;
- yet StrictCUSUM and PHT at `lambda = 15` detect **1.000** of runs within `W` at this very point
  (`s9_family_ordering.json`).

The formulas, sufficient conditions "up to universal constants", carry the margin
`sqrt((W/2) ln(1/eps))` over the whole transient. Read at `W`, they are too loose to decide the
predicate; at `W_fw` the margin alone (`54.7`) exceeds the ceiling. The published table holds at the
first-swap horizon only. Charged against `rem:split_measured` and `rem:floor_band` (S2ter-D,
S2ter-E) and escalated to the theory streams (S2ter-K).

The equalising ADWIN level of S9 D5, `4 W exp(-2 lambda^2 / W)` at `lambda = 15`, is `0.0904` at
`57.4`, `1 173` at `W_argmax` and `6 371` at `W_fw`. At the exploitable transient no level in
`(0, 1]` equalises ADWIN with the CUSUM, so the equalised matrix of S9 is equalised at the
first-swap horizon, and the table of S2ter-I says so.

### 3.4 Charged, not edited

The orchestrator restricted the pass to the four named artifacts: stream S10 runs in parallel on
the SSOT and on the S9 code. The census's remaining carriers are charges in `transfer_S2ter.md`
§J:
- `s2_gate_T20.json` and `s2_arl0.py` — the source of `rem:split_measured`'s ladder, the carrier
  that matters most;
- `s2bis_proteus_calibration.py`;
- `S2bis_narrative_payload.md`;
- `S9_W_TRANSIENT_REF` and its comments in the SSOT;
- `s9_offline_detectors.py`, `s9_family_ordering.py` and their JSON;
- `PLAN_S9.md`;
- `.tex:481`.

---

## 4. T4 — (C4), rewritten

`thesis_v4.md` §T11a.4 stated (C4) on a scaling law, "square-root for the other two", and on
`cor:split`'s crossings. The first is refuted as KSWIN's governing condition (S9 D2); the second is
evaluated at a lower bound on `W` (§3.3). The replacement (S2ter-F, English, ready to insert) carries
the measured matrix and honours the three constraints of the mandate:

| constraint | carried by | reproduced (rule E4) |
|---|---|---|
| equalising lowers the fixed-window two-sample monitor and raises the adaptive-window one, both at zero pre-change alarms; D5 = LOST | "(KSWIN, `0.458 -> 0.337`) … (ADWIN, `0.885 -> 0.926`, median delay `28 -> 15`), both at zero pre-change alarms" | `0.458`, `0.33693`, `0.884765`, `0.92566`, `28.0`, `15.0`, pre-change `0.000` ×4 |
| EDDM's rank is a function of `p_0` | "never arms at `p_0 = 0`, is first at `p_0 = 0.024` (`0.974`, `0.020`) and last at `p_0 = 0.069` (`0.022`, `0.930`)" | ProteuS `0/1080`, never armed; `0.974015`, `0.020`; `0.022345`, `0.930` |
| any ordering table carries `p_0` in a column | S2ter-I, `tab:family_order`, long format with a `p_0` column, 19 rows over the three streams | generated by `family_table_latex()` and asserted verbatim in the payload |

S2ter-G replaces the "Tenable with" line and S2ter-H the rationale, which still stated that S9
"exists as a prompt and nothing else". S2ter-F supersedes S9-G and includes its third-class
statement: the input-space monitor is blind to a change of `P(Y|X)` at fixed `P(X)` (S9 D8).

---

## 5. Against the mandate's exit gate

| condition | state |
|---|---|
| T1 arbitration rendered, argued, one outcome retained | rendered and argued: **(a)**. Retained: **no**, by rule E1 |
| retained form validated at `>= 93.1 %` on the three S9 grids | **not met**: `0.9275` pooled; `0.775` canonical, `0.900` rotation |
| the four T3 artifacts corrected in one pass; table of acceptions delivered | **met**: `6d4c703`; seven acceptions |
| (C4) rewritten with `p_0` as a column | **met**, as payloads S2ter-F to S2ter-I |

## 6. Declared debt

- `s2bis_proteus_calibration.py` does not emit the two keys the committed JSON now carries. A re-run
  drops them without moving a numeral, and
  `test_gate_json_labels_the_first_swap_time_beside_its_W_alias` fails. Charged (S2ter-J).
- On the classifier-driven grids `A_{n_stat}` is its rectangular reduction at the nominal `Delta_e`.
  The trace-level estimator needs traces this worktree cannot reach. Declared in the rules before
  measurement.
- Two of the E0 targets rest only on S9's report, which had no committed code for them: B1 on
  `G_can` (`0.863`, `0.800`) and on `G_rot` (`0.850`). S2-ter's definitions reproduce them exactly;
  those definitions are now the code of record.
- `project_knowledge_search`, named by the mandate, does not exist in this environment. The
  repository, read through `docs/manuscript/CURRENT`, was the only source.
