# Stream S2-bis — calibration, comparison fairness, narrative payload

## Context

Stream S2 closed (`3f59b35`, phases 0–7) leaving one measurement unacted on: calibrating
PageHinkley to one false alarm per warm-up hands the ARF pipeline λ = 20.97 and the HT pipeline
λ = 132.50 (`results/S2_theory/tables/s2_flooding_retrodiction.json`), a factor 6.3 fixed by the
two classifiers' pre-change error volatility (`e_pre` 0.058 vs 0.075). The brief asks whether the
published flooding result — INSECTS *gradual_balanced*, 85.7 alarms / precision 0.0120 / F1 0.02
against 7.0 / 0.1429 / 0.25, F1 ratio **10.57×**, `p ≈ 2e-9` — is an artefact of comparing two
pipelines at a common threshold.

**Two premises of the brief are contradicted by the code, and both were verified directly.**

**(A) R5 does not run at λ = 15.** `exp_R5_common.py:121-123` calibrates per (variant, seed,
pipeline) with `calibrate_lambda` (`:59-85`): bisection on `[1, 500]` to ≤ 1 false alarm on that
pipeline's own warm-up error stream, detector re-armed after each alarm, `PHT_TARGET_FA = 1`. The
warm-up is 10 % of the stream and identical in length for both pipelines, so Table II's 10.57×
**is already an equal-false-alarm-budget comparison** and `lambda_calibrated` **is** the λ_eq of
T-A(a) at the target "one FA per warm-up". 20.97 / 132.50 are the seed means of that existing
column (`s2_arl0.py:467-484`), not a calibration S2 invented.
The site where λ = 15 is genuinely common is **R4**: `exp_R4_main_table.py:165`,
`PageHinkley(threshold=ssot.R4_PHT_LAMBDA)`, with **no warm-up at all** — the detector is armed at
`t = 0` (`:130-131`) — and `evaluate()` (`:109-124`) computes precision then discards it, so
`exp_R4_results_aligned_fusion.csv` carries only `F1` and `ADD`. Table I's `0/1080`, its
`p ≈ 2e-9` and every EDDM / ADWIN / KSWIN row sit on that uncalibrated comparison.
What survives of T-A on R5 is a real and measurable gap: the budget is set on a 2 414-step warm-up
while the armed pre-change span is 11 613 steps.

**(B) R1's mis-set `p_pre` does not touch the published numerals.**
`exp_R1_generate_data.py:56` is real, but it feeds `tau_det_fixed`, a column no aggregation reads.
`Share_Blind_Spot` and `Detection_Rate` are built at `:136-139` from `blind_spot_observed` and
`tau_det_emp_finite`, both functions of the **empirical** arm whose `p_pre` is the 1 000-step
warm-up mean (`:79-81`). R2 likewise uses the warm-up mean; its `else 0.05` at `:90` is
unreachable for any `T_DRIFT > 0`. R1 is a deliberate two-arm design whose control arm was never
published. T-B therefore reports a null effect on the published numbers plus the measured
counterfactual, and no re-run is warranted on this ground.

Three further facts established during planning, each of which fixes a decision rule:

1. **`R_KSWIN = 22.7` is not a common-α number.** `s2_gate_T20.json` →
   `floor_and_family.family_requirements.deployed_alphas.R_KSWIN_at_deployed_alpha = 22.679`, at
   KSWIN's *deployed* α = 0.005. At the common α of a λ = 50 CUSUM (α ≈ 6.3e-16) the same artifact
   gives `R_KSWIN = 41.997`, which does **not** clear the measured ceiling 33.51. T-C must state
   the α each requirement is read at.
2. **The T-E coincidence is chronologically impossible.** `transfer_S1`'s `4.56` appears at
   `a3a481a` under the declared header *"`p_0 = 0.05`, `delta_P = 0.005`, `eps = 0.05`"*. The
   claimed match 0.036 = `p_pre + delta_P − p_true` needs `delta_P = 0.01` (A1, `8fb0875`) and
   `p_true = 0.024` (`P0_MEASURED`, S2, `a0009d4`), both later; at the initial commit R1 carried
   `DELTA_P = 0.005`, so its effective tolerance then was 0.031. Expected verdict: REFUTED.
3. **The `pht_ht` arm is deterministic.** `build_model` returns `tree.HoeffdingTreeClassifier()`
   with no seed, and `lambda_calibrated` has std = 0 across the 30 seeds on all three INSECTS
   variants. The seed-level sign test compares 30 ARF runs against 30 identical HT runs, while the
   Table I caption claims the seed is *"the unit of statistical independence"*.

Stale anchors in the brief: `transfer_S1` L63 is now **L73**; `protocol_v2.tex` **does not exist**
in `docs/manuscript/sections/`. Every anchor is re-grepped by text.

## Perimeter

Created: `docs/prompts/s2bis-decision-rules.md`, `experiments/S2bis_calibration/**`,
`results/S2bis_calibration/**`, `docs/theory/S2bis_calibration.md`,
`docs/theory/S2bis_narrative_payload.md`, `docs/theory/transfer_S2bis.md`,
`tests/test_S2bis_calibration.py`.
Append-only: one `# S2-bis —` banner block at the end of `config/experiment_ssot.py` (the file ends
at L331 with the S2 block; same pattern, no existing line touched). One row appended to the
wall-clock table of `docs/ENVIRONMENT.md`.
Never patched: the manuscript of record, `docs/manuscript/sections/*.tex` (S3 works there),
`results/**` outside `results/S2bis_calibration/`, `experiments/R1..R9/**`, and the four excluded
inline subsections `sec:race` / `sec:hydra` / `sec:starvation` / `sec:decoupling`.
All manuscript fixes ship as SEARCH/REPLACE payloads in `transfer_S2bis.md`, 9 tildes, target file
named, anchored on verbatim text.

---

## Phase 0 — decision rules, committed before any measurement

`docs/prompts/s2bis-decision-rules.md`, own commit, following the shape of
`docs/prompts/s2-decision-rules.md` (both branches per rule, numeric thresholds, no point estimate
as decision variable).

**B0 — honesty declaration.** The planning phase has already read the λ = 15 baseline in full:
`s2_flooding_retrodiction.json` (20.97 / 132.50, 85.7 alarms, precision 0.0120, ratio 10.57×),
`s2_gate_T20.json` (the common-α ladder and `R_KSWIN_at_deployed_alpha`), `calibrate_lambda`'s
source, the seed-invariance of `pht_ht`, the R1 counterfactual's direction, and the `transfer_S1`
git chronology. The rules below are blind only with respect to the new measurements at λ_eq.

**B1 — the ARL_0 target.** Two targets, both reported, the first carrying:
`T_span` = the armed pre-change span of the stream (one expected FA over the span the detector
actually runs), and `T_warm` = the warm-up length (the target R5 already uses). Both are protocol-
defined, carry no free parameter, and are identical across pipelines on the same stream.

**B2 — λ_eq estimator.** `λ_eq^emp` (bisection to ≤ 1 FA on the target span, re-armed, i.e.
`calibrate_lambda` with the span substituted) carries the verdict. `λ_eq^ARL` = Siegmund inversion
at θ*(p_pre, p_true) measured per pipeline is the consistency check. If the two differ by more than
a factor 2, the analytic model is declared inapplicable to River's adaptive-mean PageHinkley and
the disagreement is published as a finding, never tuned away.

**B3 — the flooding gate (escalation criterion).** Decision variable
`ρ_eq = F1(PHT+HT at λ_eq) / F1(PHT+ARF c=1 at λ_eq)` on INSECTS *gradual_balanced*, with a
seed-paired bootstrap CI. Reference `ρ = 10.57` at the existing calibration.
CI upper bound < 2 → **COLLAPSE**, escalate before T-C. CI lower bound > 5 → **SURVIVES**.
Otherwise → **INTERMEDIATE**, publish the decomposition, never an average.
Degenerate handling fixed now: if either F1 is 0 the ratio is undefined and the verdict is read off
`ΔF1 = F1_HT − F1_ARF` with the same three bands scaled to [0, 1] — declared here, not after.

**B4 — decomposition (T-A d).** Four cells {ARF, HT} × {λ_ref, λ_eq}, read off a λ-sweep:
`ln ρ(λ_ref) = ln ρ_eq + [(ln F1_HT(λ_ref) − ln F1_HT(λ_eq)) − (ln F1_ARF(λ_ref) − ln F1_ARF(λ_eq))]`
— residual plus threshold-attributable, two numbers with CIs, no single "percentage explained"
unless both terms share a sign.

**B5 — R1 `p_pre` status (T-B d).** DEFECT if any published numeral routes through `tau_det_fixed`;
UNDOCUMENTED DELIBERATE CHOICE otherwise. Either way one sentence is owed to the manuscript; only
the first would require a re-run.

**B6 — R1(b) coincidence (T-E).** CONFIRMED requires both: the floor at `p_0 ← 0.0360` under L73's
identified inputs rounds to 4.56 at the printed precision, **and** 0.036 was computable when the
line was written. Either failing → REFUTED.

**B7 — saturation and arming.** A λ_eq returned at the bisection ceiling (500.0) is `SATURATED`,
never a value; a target unreachable on the available span is `NOT ATTAINABLE` with the bound
reported; a span shorter than the detector's arming time (`min_instances = 30` for PHT,
`warm_start = 30` errors for EDDM) is `NOT ARMED`. All three are terminal, publishable verdicts.

**B8 — bands.** Any statement consuming ARL_0 is written as an interval over the per-run `p_true`
band of **its own** stream and pipeline, measured from that campaign's seeds. `[0.015, 0.032]`
belongs to the S6 Bernoulli arm and is used only for S6-anchored statements.

---

## Phase 1 — T-A volet 1: R5 / INSECTS

`experiments/S2bis_calibration/s2bis_lambda_eq.py`.

1. **Establish the rule.** λ_eq(pipeline) = ARL_0⁻¹(target) with ARL_0 from Siegmund at
   θ*(p_pre, p_true). Reuse `cramer_root`, `arl0`, `arl0_inverse` from
   `experiments/S2_theory/s2_arl0.py:92-138` by `sys.path` import — the S2 precedent
   (`s2_w_random.py:42-48` imports from `s2_arl0` and `s6_predictive_power`). Do not re-derive.
2. **Verify it by simulation** on each stream's pre-drift span, per pipeline, over the 30 seeds.
3. **Prove the identity** `lambda_calibrated ≡ λ_eq(T_warm)` by re-deriving the frozen column from
   `results/R5_real_world_evaluation/data/insects_per_episode.parquet`, and report the
   budget/span mismatch: `T_warm` 2 414 vs `T_span` 11 613 on *gradual_balanced*, i.e. ≈ 4.8
   expected FAs over the span the detector actually runs.
4. **Re-measure at λ_eq(T_span)** on a λ-grid, both flooding pipelines, 30 seeds, priority
   *gradual_balanced*, then the other two INSECTS variants.

**No replay shortcut exists.** `run_evaluation:137-141` resets the classifier on every alarm
(`model.clone()` / fresh HT), so the error stream is a function of λ. Each grid point is a full
prequential run. Cost basis: the INSECTS stage is 270 runs in minutes; the grid is
~10 λ × 2 pipelines × 30 seeds on a 24 149-row stream ≈ the same order, ~10 min for
*gradual_balanced* and ~1 h for all three variants.

**Reuse, do not fork.** Import `exp_R5_common` and `exp_R5_config` by `sys.path` injection and call
`build_model`, `calibrate_lambda`, `evaluate_bipartite`, `valid_drifts`, `resolve_f1_drifts`,
`get_warmup_steps`, `get_tau_tol`, `make_seed_pool`. The single API gap is that `run_evaluation`
hard-couples calibration to execution (`:121-123`) and accepts no external λ; S2-bis carries a thin
local driver that reproduces that loop verbatim with λ injected, and a test asserting the two agree
bit-for-bit when λ is the calibrated one. Pick `[d, d+tau]` (the `evaluate_bipartite` convention)
and state the choice — `per_episode_match` uses `(d, d+tau]`.

INSECTS CSVs have no header row, so `pd.read_csv` consumes record #1 and `n_total` = lines − 1.
Reproduce that loader exactly or every drift index shifts.

**Pseudo-replication.** On the frozen artifacts, verify seed-invariance of `F1_bp`,
`lambda_calibrated` and `n_detections` for `pht_ht` across the three variants, and quantify what
one effective HT replicate does to the `p ≈ 2e-9`. Reads only; regenerates nothing.

## Phase 2 — T-A volet 2: R4 / ProteuS

`experiments/S2bis_calibration/s2bis_proteus_calibration.py`. This is where λ = 15 is common.

1. **Build the missing warm-up**: `[0, ssot.R4_T_DRIFT)`, the pre-drift span. A calibration pass
   runs each (classifier, transition, seed, regime) with the external detector disabled so no reset
   perturbs the pre-drift error stream — the same convention R5's warm-up uses, declared as such.
2. **Calibrate λ_eq** per (detector, classifier) couple with `calibrate_lambda` on that stream.
3. **Re-measure** at λ_ref = 15 and at λ_eq, recording what R4 never recorded: alarm counts,
   precision and recall alongside F1 and ADD. Report the deviation of each λ_eq from 15.
4. PHT couples only: PHT+HT, PHT+ARF(c=1), PHT+ARF(c=32), SRP+PHT(c=1), SRP+PHT(c=32),
   PHT+RF(static). λ-grid on the two headline couples.

R4 learns before cloning (`:136-140`) where R5 clones before learning (`:141-142`); the two loops
are not interchangeable — reproduce R4's ordering here. Cost basis: `exp_R4_main_table.py` is
16 200 rows inside a 54 min wrapper; 6 of 15 pipelines ≈ 17 min per threshold pass, so calibration
+ two thresholds + an 8-point grid on two couples ≈ 1 h 30. Add the row to `docs/ENVIRONMENT.md`.

**ADWIN / KSWIN, analytic only.** No new campaign. Extend the `deployed_alphas` hook at
`s2_arl0.py:393-402`: evaluate `R_CUSUM`, `R_ADWIN`, `R_KSWIN` at the common α implied by λ_eq, and
report the δ and α that would place ADWIN and KSWIN at the CUSUM's level. EDDM is declared out of
scope for the knob equalisation, with the reason: its level is a ratio against a running maximum
and carries no false-alarm parameter of the same kind.

## Phase 3 — T-B and T-E, analytic, no re-execution

`experiments/S2bis_calibration/s2bis_r1_ppre.py`.

- **T-B(a)** Confirm `exp_R1_generate_data.py:56` from source; establish the same point on R2 —
  `:86-90` fills the buffer over `t ∈ [3000, 3999]` so the `0.05` fallback is unreachable for any
  `T_DRIFT > 0`, which is the opposite of the brief's expectation and must be shown structurally.
- **T-B(b)** Both published numerals are built from `tau_det_emp`; the effect of `p_pre = 0.05` on
  them is exactly zero. Deliver instead the paired counterfactual from the frozen parquet — both
  arms see the same post-drift error stream, same seed, same λ, so `tau_det_fixed` is a within-run
  control — as a committed table across the full λ ladder, with the effective tolerance 0.036, the
  Cramér root 0.681 → 1.700 and the ARL_0(15) factor 4.8e5 sourced from
  `s2_arl0_columns.csv` row `R1 fixed arm`. Never re-run R1.
- **T-B(d)** Verdict under B5, plus the actionable residue: `p_pre` is the one CUSUM parameter with
  no SSOT route and no `test_S7_consistency` guard (`GUARDED_NAMES` at `:48-53` omits it) at both
  R1 `:56` and R2 `:90`. Recommendation only — both files are outside the perimeter.
- **T-E** Execute B6: the numeric test (floor at `p_0 ← 0.0360` against 4.56 at printed precision,
  the competing explanation `Delta_max = 0.137` reported beside it) and the chronology test
  (`git log` on `transfer_S1.md`, `CUSUM_DELTA_P`, `P0_MEASURED`). Render the verdict both ways.

The manuscript sentence T-B owes goes to `articleA_blindspot_v64_camera_ready.tex:287`, the single
site citing both 92 % and 89.5 %, as a SEARCH/REPLACE payload anchored on *"Detection Rate"* —
`protocol_v2.tex` does not exist and no file is invented to receive it.

## Phase 4 — T-C and T-D, payloads only, no section edited

`docs/theory/S2bis_narrative_payload.md`, in English, ready to integrate.

**T-C** (a) floor `[13.9, 18.3]` < measured ceiling 33.51 < `R_CUSUM(λ=50)` 59.27, each with its
band and its artifact key in `s2_gate_T20.json`; and `λ_op = 21.93 [19.876, 22.398]` giving
`R_CUSUM(λ_op) = 31.2 < 33.51` — the detector-side fix the repository has already measured.
(b) The KSWIN retraction, stated at both α: 22.68 at the deployed α = 0.005, 41.997 at the common
α. Ten sites assert immunity by construction — `.tex` L151, L278-280, L444, L447, L448, L466,
L534, L536, L409 and `related_work_v2.tex:110-112`; the abstract L88 and Discussion L521 are
already correctly hedged and are the phrasing model. (c) The contribution restated as a calibration
rule. (d) `cor:split` in one sentence: slope `1/θ* = 1.468` per unit `ln(1/α)`, square root for the
other two, crossing at `ln(1/α) ≈ 13`.

**T-D** The corrected reading, including a correction to the brief's own premise: the S6 warm-start
control (95 % of runs incomplete, 24 errors against a 30-error warm start) is a property of the
**S6 traces**, whose pre-drift span is 1 000 steps. ProteuS gives EDDM 4 000 pre-drift steps ≈ 96
errors (`s2_eddm.json`, `closed_form[].history == "R4 ProteuS"`, `n_0_errors = 96.0`), so the
unarmed-detector reading does **not** transfer to the `0/1080`. What transfers is `W_EDDM ∝ n_0`
(median 230.5 steps at the R4 history) and the T-A finding that EDDM runs at River defaults never
equalised against PHT's threshold. Deliver the reading the artifact supports, in both directions.
List the sites that read `0/1080` as a blind spot (`.tex` L441-442, L454, L463, L466, L507, the
Table I caption, `prop3_v2.tex:288-305`) and re-transmit the two out-of-perimeter `R_EDDM` sites
S2 already handed forward (`.tex:151`, `related_work_v2.tex:108`). No patch applied.

---

## Files and the traps they must clear

| file | note |
|---|---|
| `docs/prompts/s2bis-decision-rules.md` | committed alone, before any measurement |
| `experiments/S2bis_calibration/s2bis_lambda_eq.py` | Phase 1 |
| `experiments/S2bis_calibration/s2bis_proteus_calibration.py` | Phase 2 |
| `experiments/S2bis_calibration/s2bis_r1_ppre.py` | Phase 3 |
| `results/S2bis_calibration/tables/s2bis_*.{csv,json}` | new tree, `s2bis_`-prefixed basenames |
| `docs/theory/S2bis_calibration.md` | measurements, hashes, guard-rail matrix |
| `docs/theory/S2bis_narrative_payload.md` | T-C + T-D |
| `docs/theory/transfer_S2bis.md` | verdicts, SEARCH/REPLACE payloads, open items |
| `tests/test_S2bis_calibration.py` | plain `def test_*`, `pytest.skip` with an executable remedy |
| `config/experiment_ssot.py` | append-only `# S2-bis —` block below L331 |

Module skeleton, copied from `experiments/S2_theory/`: `ROOT_DIR = Path(__file__).resolve()
.parents[2]`, `OUT_DIR = ssot.RESULTS_DIR / "S2bis_calibration" / "tables"`, no argparse,
`demo()` + `main()`, and `if __name__ == "__main__": demo(); if "--check" not in sys.argv: main()`.
CSV via `to_csv(path, index=False)`; JSON via
`json.dumps(payload, indent=2, sort_keys=True, default=float) + "\n"`, `encoding="utf-8"`, with a
`reproduction` block carrying relative paths only. `float_precision='round_trip'` on any float join
key read. There is no `save_fair_csv` in this repository and none is to be written.

`tests/test_S7_consistency.py` walks `experiments/**/*.py` with `rglob`, so the new files are
scanned with no registration step. Four ways to fail it: a module-level bind of a `GUARDED_NAMES`
identifier whose RHS source lacks the substring `ssot.` (`:48-53`); a bare literal on
`n_steps|tp|t_drift|n_models|threshold` in a default or a call keyword (`:77`); a `StrictCUSUM`
construction without an explicit `delta=ssot.CUSUM_DELTA_P`; tracked bytecode. Name locals outside
the guarded set, as `s2_arl0.py:52-62` does.

New artifacts break nothing: `sha256sum -c` is a per-file, open-world check over 34 named paths, so
`results/S2bis_calibration/` adds no line and the verdict stays `29 OK, 5 FAILED`. **No entry is
added to `authorized_deviations.txt`** — the S2 precedent. Keep basenames `s2bis_`-prefixed so they
cannot collide with the basename glob in `test_manuscript_integrity.py:68-69`.

Statutory guard-rails in `tests/test_S2bis_calibration.py`, one assertion each: λ_eq at
`p_true → p_pre` (no positive Cramér root, `ValueError` propagates, never a silent
`ARL_0 = 0/0`); target unreachable on the available span (`NOT ATTAINABLE`, bound reported);
bisection ceiling reached (`SATURATED`, never returned as a value); span shorter than the arming
time (`NOT ARMED`); `F1 = 0` in one arm (ratio undefined, `ΔF1` path taken); λ_eq monotone
decreasing in `p_true` at fixed target.

## Verification

```bash
PYTHONHASHSEED=0 /home/m53/miniforge3/envs/Trading/bin/python \
    experiments/S2bis_calibration/s2bis_lambda_eq.py --check          # self-check, writes nothing
PYTHONHASHSEED=0 /home/m53/miniforge3/envs/Trading/bin/python \
    experiments/S2bis_calibration/s2bis_lambda_eq.py                  # and the two siblings
PYTHONHASHSEED=0 /home/m53/miniforge3/envs/Trading/bin/python -m pytest \
    tests/test_S2bis_calibration.py tests/test_S2_theory.py \
    tests/test_S7_consistency.py tests/test_manuscript_integrity.py -v
sha256sum -c results/audit_S7/_baseline/artifacts_sha256_pre_ssot.txt  # expect 29 OK, 5 FAILED
git status --short                                                     # no R1–R9 artifact modified
```

Each module is re-run twice and its outputs hashed to prove bit-reproducibility, and the hash table
goes into `docs/theory/S2bis_calibration.md` §2 the way `S2_numerical_validation.md:33-46` does.
The frozen-artifact check and `git status` together are the acceptance gate for "no R4 or R5
artifact regenerated".

## Escalation

B3 fires before T-C. If `ρ_eq` collapses on *gradual_balanced*, Phase 1 stops at its verdict and
reports; T-C's narrative payload is written against the new reading, not the old one. Note the
interaction with S2's pending patches: `transfer_S2.md` Patch B already restates `rem:flooding` and
its closing sentences attribute the asymmetry to the threshold. A collapse promotes that clause
from a coda to the claim, and `transfer_S2bis.md` must declare which of S2's two patches it
supersedes, since Patch B consumes Patch A's macros and both are still unapplied.
