# Transfer document — stream S3 (inter-tree dependence, Proposition 9, `M_crit`)

Parent `d7c5238`, on `stream-s2` HEAD `3f59b35`, branch `stream-s3`. Decision rules D0–D8 fixed
before any measurement in `docs/prompts/s3-decision-rules.md` (`cd443f4`).

## Faults and open items addressed

| item | source | status |
|---|---|---|
| `eq:pmiss` states an **equality** under an undemonstrated conditional independence | reviewer #3 | **closed** — replaced by a two-sided distribution-free envelope; the independence form is kept as the conditional case with its hypothesis named |
| *Correlation disclaimer* asserts the direction of the bias without proof | reviewer #3 | **closed, and the stated reason corrected** — positive correlation does not license the bound; an explicit exchangeable counterexample at `Corr = +0.51` violates it |
| **F24** — `cor:mcrit` `void` in the notation map, live in the manuscript | plan S3 | **closed by withdrawal** under rule D5(b); the label is retained carrying the negative statement |
| **F22** — `sec:hydra` L194 vs the KS rejection at the *Numerical example* | plan S3 | **closed** — the exponential identity is a calibration reference; re-verified, 20/20 magnitudes reject |
| `tau_det*` deterministic where `tau_det` is a stopping time | `notation_map` L17 | **closed** — replaced by a competing-risks race under administrative censoring |
| `F = F_HAT` assimilated silently | plan S3, T3.4 | **closed by refutation** — measured false on 10 of 80 testable cells |
| equal-false-alarm-budget form of the Hydra factor | `transfer_S2` §4 | **NOT PRODUCED** — the committed artifacts do not carry the inputs (D4-bis branch 2) |

## Deliverables

- `docs/theory/S3_dependence_bounds.md` — both bounds with complete proofs, the D1 gate and its
  recorded scope gap, the numerical vacancy, the plug-in refutation, the guard-rail matrix.
- `docs/theory/S3_competing_risks.md` — the race as competing risks, the D3 re-verification, the
  measured incidence, the two `M_eff` routes, P4-bis.
- `docs/manuscript/sections/dependence_v2.tex` — the companion section, pending the v65 assembly.
- `docs/manuscript/articleA_blindspot_v64_camera_ready.tex` — patched **in the S3 zone only**
  (every hunk inside L338–378): the disclaimer, `eq:pmiss`, its proof, `cor:mcrit` and the numerical
  example. Compiles under `tectonic` with no undefined reference and no overfull box introduced.
- `docs/theory/notation_map_v63_to_v2.md` — two lines, `prop:starvation_boundary` and `cor:mcrit`.
- `experiments/S3_dependence/{s3_gate_rng_factorization.py, s3_bounds.py, s3_competing_risks.py}`,
  `tests/test_S3_dependence.py` (21 guards).
- `results/S3/` — nine tables and one figure, all bit-reproducible on a second pass.
- `docs/prompts/s3-pmiss-sweep-prompt.md` — gated, **not executed**.

---

## 1. The headline result: the single-tree plug-in is refuted, not merely undeclared

One sentence for the writing stream:

> `prop:starvation_boundary` evaluates its bound with `F_HAT`, the delay law of a standalone
> HAT, in place of `F`, the delay law of a tree inside the ARF. Over the 80 testable cells of the
> instrumented grid (20 magnitudes × `lambda in {8, 15, 25, 50}`, `M = 10`, `n = 100`) the plug-in
> upper end falls **below** the Wilson 95 % lower end of the measured `P_miss` in **10** of them
> (11 for the independence form) — always at `lambda <= 25`, always anti-conservative.

Mechanism, both tails, measured: at `Delta_e = 0.3268` the fastest of 100 HAT runs adapts at step
**33**, so `F_HAT(25.25) = 0` exactly, while **4 of 100** ARF runs have already adapted by then;
and `E[tau_(10)]` measured against `E[max of 10 draws from F_HAT]` falls from `1.09` at
`Delta_e = 0.028` to `0.49` at `Delta_e = 0.498`. The ARF member's law is **more dispersed** than
the HAT's at both ends, which is what Poisson weighting and `max_features = 1` produce.

This is a refutation of the **substitution**, not of either inequality. Both bounds remain
unconditionally valid for the true `F`, which no committed artifact carries.

## 2. What replaces the v63 apparatus

| v63 object | replacement |
|---|---|
| `P_miss = 1 - [1-F]^M` | `F(s) <= P_miss(s) <= min(1, M F(s))`, both ends attained (Fréchet–Hoeffding), no dependence hypothesis |
| the independence formula | retained as the **conditional** case, proved by Jensen on `x -> x^M`, hypothesis named |
| *Correlation disclaimer* | proved as a corollary of the common-factor structure; the "positive correlation" reason is withdrawn with a counterexample |
| `tau_det*` | competing-risks race, administrative censoring at `t_c = 4000` |
| `M_crit` | withdrawn: the envelope saturates at `M F >= 1` and is constant in `M` there |
| the numerical example | retracted; the ensemble claim rests on the measured incidence |

## 3. Verdicts, one line each

| rule | object | verdict |
|---|---|---|
| D0 | the four pre-read R9 numerals, the two Hydra factors | **REPRODUCED** (`tau_det* = 157.83`, `F_emp = 0.49`, `E[tau_HAT] = 463.15`, `M_crit = 0`; `4.12x [3.45, 4.96]` and `7.99x [6.40, 9.72]`, medians `5.32x` / `3.10x`) |
| D1 | draw-stream factorisation | **DOES NOT FACTORISE** — `residue_ok` false (1–16 draws per tree and step, mean 7.07), `n_shift = 9839`, first displacement at position 34 |
| D2 | carrying bound | **Boole**, alone; the Jensen form enters no published numeral |
| D3 | RMST identity | **REPRODUCED** — worst `9.095e-13` over 40 cells against a `1e-9` tolerance; zero gap to the committed `hydra_survival.csv` |
| D4 | the two `M_eff` routes | **DISAGREE** — 13 of 20 magnitudes inside the declared factor 1.5; both published, neither averaged. At `Delta_e = 0.3268`: `M_eff in [6.99, 9.16]` |
| D4-bis | equal-budget Hydra factor | **NOT PRODUCED**, with the missing measurement named |
| D5 | `cor:mcrit` | **(b) WITHDRAWAL** |
| D6 | F22 | **the L194 half gives** — 20/20 magnitudes reject exponentiality, largest `p = 0.0030` |
| D7 | bound vs measurement | canonical anchors **HOLD**; on the full grid **BOUND REFUTED**, census 10 / 11 |
| D8 | `prop:starvation_boundary` | **REPAIRED / RETAINED**, as written and under the restricted reading |

## 4. Three results the writing stream should not lose

1. **The race is uncensored, and the monitor never wins at `lambda = 50`.** `tau_ARF` is observed
   on every one of the 2000 runs at every magnitude, so a `NaN` `tau_det` is the monitor *losing*,
   not a missing observation. `P(tau_ARF < tau_det) = 1` with a paired bootstrap band `[1.00, 1.00]`
   at all twenty magnitudes. The five alarms scenario A does raise (0.25 %) all fire **after** the
   ensemble has adapted — every one is a Zombie alarm.
2. **The race is not monotone in `Delta_e`.** At `lambda = 25` the monitor's win probability is
   `0.00` at `Delta_e = 0.028`, peaks at **0.32** at `Delta_e = 0.141`, and returns to `0.00` from
   `Delta_e = 0.361` upward. `tau_det*` is monotone in `Delta_e` by construction and cannot show
   this. That is a substantive reason to drop the scalar, beyond its being the wrong object.
3. **The shortfall from `10x` is mostly non-exponentiality, not inter-tree correlation.**
   `sec:hydra` attributes it to correlation. Measured: the order statistics of `F_HAT` alone give
   `9.22x` at `Delta_e = 0.3268` and `4.83x` at `Delta_e = 0.141` against observed `7.99x` and
   `4.12x`, so the residual left for dependence **and** the marginal mismatch together is `0.87`
   and `0.85`. The measured within-run correlation is indistinguishable from zero
   (`rho_hat in [-0.021, 0.053]`). The attribution in `sec:hydra` does not survive.

## 5. Sites outside the S3 write perimeter, handed forward

None is patched by this stream. The perimeter is the one declared in the S3 plan — the manuscript
zone from the disclaimer paragraph to the numerical example — and `CLAUDE.md` excludes the four
inline subsections superseded by `framework_v2.tex`.

1. **`.tex` L336**, the lead-in of `sec:starvation_boundary`: *"We derive an upper bound on the
   probability of missed detection and a critical ensemble size `M_crit` beyond which external
   detection fails with probability exceeding `1 - r`"*. `M_crit` is withdrawn one paragraph
   below. The sentence must be restated on the envelope.
2. **`.tex` L463** (`sec:proteus`, SRP): *"This definitively confirms Corollary~\ref{cor:mcrit}"*.
   The corollary now states that no ensemble size is certifiable; the SRP result (0/1080
   detections) is *consistent* with it but does not "confirm" a critical size. The label was kept
   alive precisely so this reference does not dangle; the prose still needs correcting.
3. **`sec:hydra` L194–L196** (excluded zone): the `M`-fold sentence should be marked as a
   calibration reference, and the sentence attributing the shortfall to *"the measured cost of the
   positive inter-tree correlation"* is refuted by §4.3. The resolution is written in
   `dependence_v2.tex` §`sec:dep_exponential` and referenced from the S3 zone.
4. **`.tex` L421**: *"The adaptation-time fits provide direct empirical support for the Starvation
   Boundary derivation"* — the derivation it supports no longer contains `tau_det*`.

## 6. Open items handed forward

1. **The member marginal `F` is never measured.** No artifact records a per-tree `tau_i` inside the
   ARF. This is now the binding gap: every bound in the section is stated on `F`, and the only
   available estimate of it has been refuted. Recording per-tree adaptation times on the existing
   R2 configuration would close it at the cost of one campaign.
2. **The equal-budget Hydra factor.** Record the per-step pre-drift error stream of (i) a
   standalone HAT and (ii) one tree inside the ARF, on matched seeds and magnitudes; calibrate both
   to one false alarm per warm-up; re-derive the factor. Until then the decomposition into a
   threshold part and an ensemble part is `NOT PRODUCED` and the factor is published undecomposed.
3. **D1's criterion is sufficient, not necessary.** A displacement of draw positions proves the
   allocation is state-dependent; it does not prove the per-tree draw blocks are probabilistically
   dependent, because a sequential allocation by adapted stopping times preserves independence on
   an idealised i.i.d. source. Reopening the Jensen path requires *proving* that factorisation as a
   theorem about the allocation, not measuring it — and note that conditional independence given
   the stream is not a measurable property of a deterministic generator at all. The rule was
   applied as committed and the gap is recorded rather than used to move it.
4. **D8's criterion fires on refuted cells.** It was committed on the plug-in evaluation and
   applied as committed; the restricted reading — the same computation with every refuted
   `(Delta_e, lambda)` pair removed — also returns RETAINED, at `(0.4823, 8, M = 2)`. Both readings
   are in `results/S3/s3_verdicts.json::D8`.
5. **The `P_miss(M)` sweep is gated**, `docs/prompts/s3-pmiss-sweep-prompt.md`, with its acceptance
   gate and its ≈ 53 min estimated cost. T3.5 is declared closed at the two anchors without it.
6. **`s_0` is still never measured** (`transfer_S2` open item 4). Nothing in S3 depends on it.

## State

Stream S3 complete, phases P0–P7. Manuscript of record patched inside the S3 zone and compiling;
`dependence_v2.tex` produced and pending the v65 assembly. No entry added to
`results/audit_S7/_baseline/authorized_deviations.txt`; no constant added to
`config/experiment_ssot.py`; `docs/manuscript/sections/framework_v2.tex` untouched.
