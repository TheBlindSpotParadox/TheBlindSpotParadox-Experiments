# PLAN S7-ter — Experimental Protocol, warning_detector unification, frozen Delta_e oracle

Target path in repository: `docs/plans/PLAN_S7-ter.md`.
Specification: `docs/prompts/PROMPT_S7-ter.md`. Manuscript of record: read from
`docs/manuscript/CURRENT` (currently `articleA_blindspot_v64_camera_ready.tex`), never hard-coded,
never read from the PDF.

---

## Context

S7 closed on its plan, not on its specification. Three specified items were never carried to an
execution plan, one of them a rejection cause named by reviewer #3 and open since the first round.
This plan closes all five lots of `PROMPT_S7-ter.md` in a phase order that front-loads the
zero-computation deliverable and defers the two expensive re-runs.

Four facts established by measurement during planning change what the specification assumed. They
are stated here because they alter the work, not as commentary:

1. **The `warning_detector` default moves two parameters, not one.** River 0.23.0's
   `ARFClassifier` resolves an unset `warning_detector` to `ADWIN(delta=0.01, clock=32)`, and an
   unset `drift_detector` to `ADWIN(delta=0.001, clock=32)`. A bare `drift.ADWIN()` is
   `delta=0.002, clock=32`. So every site that pins `warning_detector=drift.ADWIN(clock=c)` runs
   the warning at `delta=0.002`, and R3/R4 currently run it at `delta=0.01`. The unification is
   `0.01 → 0.002` **and** `32 → c`, and it collapses the warning detector into an exact clone of
   the drift detector — destroying the warning-before-drift ordering that River's ARF default
   provides. `results/audit_S7/config_matrix.md:44-54` records "river default 0.002" for the ARF
   internal detector column, which conflates two distinct River defaults; `README.md:296` names the
   warning default as `ADWIN(clock=32)`, omitting the delta. Both are corrected by this plan.

2. **Table I's confidence intervals resample the run, not the seed.**
   `exp_R4_main_table.py:232-237` calls `np.random.choice` over the 360 rows of a
   `(Detector, Clock, Calibration)` group — 12 transitions × 30 seeds — off the **global** NumPy
   state seeded once at `:413`. The Table I caption simultaneously asserts the seed as "the unit of
   statistical independence". This is precisely the reviewer's question, and the two statements are
   incompatible: the 36 streams a seed produces are not independent of one another. Same defect in
   `exp_R4_kswin_sweep.py:169,258`. The global `np.random.seed` for a bootstrap also violates the
   repository's own PRNG-isolation rule (unlike the per-worker triple lock, which River's Cython
   tree-spawn path genuinely requires).

3. **LOT E is two-thirds already discharged.** Action M7 (commit `d6fafd9`) added the
   `expires_on` table to `docs/editorial/source_verification.md:84-88` and the guard
   `tests/test_manuscript_integrity.py::test_source_reservations_have_not_expired:290`. Only the
   online re-verification of the three reservations remains.

4. **The suite is 25 tests, not 24,** and the bit-freeze is at 29 OK / 5 FAILED exactly as
   `authorized_deviations.txt:43-45` predicts. `results/audit_S7/reconciliation_report.md:523`
   still claims "all 34 artifacts unchanged", true when written, false now.

**Measured risk signal for LOT B.** A 5-seed in-memory probe reproducing `run_single_seed` of
`exp_R3_regime_crossover.py` under the three candidate warning configurations: at Δe = 0.155 the
binary metrics are invariant (`miss` 0.0 %, `fp` 1.00 under all three) while `acc` moves at the
third decimal (0.9387 baseline / 0.9377 U1 / 0.9395 U2); at Δe = 0.50, `acc(ARF)` moves
0.9848 → 0.9802 under U1. The manuscript's **23.4 percentage-point** accuracy gap
(`.tex:511` and `:522`, `acc(RF) ≈ 0.750` vs `acc(ARF) ≈ 0.984`) is therefore exposed to the
unification and must be re-measured, not asserted.

---

## Arbitrations settled before execution

| decision                       | ruling                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | consequence                                                                                                                                                               |
| ------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Section file path              | `docs/manuscript/sections/protocol_v2.tex`. `docs/sections/` is stale since action A5 (`PROMPT_S2.md:21-23`), and the prompt's own path is one of the stale references A5 declares obsolete.                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | joins `intro_v2.tex`, `related_work_v2.tex`, `framework_v2.tex` as a deliberately orphan section until the v65 assembly                                                   |
| LOT B target                   | **U1 — clone**, for comparability: `warning_detector = ADWIN(delta=0.002, clock=c)`, aligning R3 and R4's `make_arf` on R1/R2/R5–R9 and on `make_srp` (`exp_R4_main_table.py:178-181`). **Mandatory third arm U0 — River defaults**: `warning_detector = ADWIN(delta=0.01, clock=32)`, the configuration a practitioner actually deploys.                                                                                                                                                                                                                                                                                                                        | R3 and R4 re-run under U1; R3 additionally re-run under U0, see B-3                                                                                                       |
| Why U0 is not optional         | U1 makes the warning detector an exact clone of the drift detector, so the warning fires at the same step and the background tree is always untrained — S6/G2 measures 47/47 and 36/36 replacements installing a tree that has learned nothing. Publishing the phenomenon **only** under U1 means publishing it on a forest whose background-tree mechanism is structurally inert. A reviewer who knows River 0.23.0 will say the blind spot was measured on a crippled ARF, and the paper has no answer. U0 is the control that answers it.                                                                                                                     | either the phenomenon survives a functioning warning mechanism — a far stronger result — or it does not, and the scope statement is a measurement rather than an omission |
| Table I bootstrap              | **Document and correct**: seed-paired resampling on a local `default_rng`, R6's scheme (`exp_R6_hydra_survival.py:76,105`)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | Table I and KSWIN-sweep CIs move; R4 is re-run anyway under LOT B, so the two changes land in one regeneration                                                            |
| LOT C oracle                   | Frozen fork of the **existing reference HT** of `exp_R5_compute_delta_e.py`, written to a **separate** artifact                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | no hash deviation on `delta_e.parquet`; the published value stays reproducible as its own control                                                                         |
| Scope                          | All five lots. Order: A → D+E → B → C, **strictly sequential**. "B ∥ C" is withdrawn: one agent, one worktree, and both phases write `authorized_deviations.txt` and `docs/ENVIRONMENT.md`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | no intra-stream write collision                                                                                                                                           |
| Concurrency                    | **Dedicated worktree, mandatory.** Execution runs exclusively in `../worktree-S7ter` on branch `stream-s7-ter`, created from an **explicitly pinned commit SHA** — the same SHA from which `stream-s2` is created, recorded in both plans before either worktree exists. Branching from `HEAD` is forbidden: a peer session is live on this checkout and `HEAD` may advance between the two `worktree add` calls, leaving the two streams on different bases with non-comparable baseline hashes and test counts. Absolute prohibition on writing or running tests in `/home/m53/TheBlindSpotParadox-Experiments` directly.                                      | isolated index, identical base, comparable baselines                                                                                                                      |
| Shared-file discipline with S2 | `config/experiment_ssot.py`: **append-only**, in a `# S7-ter —` banner block at end of file. Never modify an existing line — the false comment at `:108` is **escalated to the orchestrator**, not rewritten here, because S2 appends to the same file in the same wave and a mid-file edit merges silently wrong past `test_S7_consistency.py`. Manuscript of record: S7-ter produces its patches as SEARCH/REPLACE payloads in its transfer document and **does not apply them**; the orchestrator applies both streams' manuscript patches in one serialized pass on `main`. S7-ter must not write the preamble macro block — it belongs to S2's payload set. | zero content collision between the two wave-1 streams                                                                                                                     |
| Lot E network fallback         | If WAN is reachable, re-verify and date. If not: run the local syntax check, **do not push `expires_on` forward**, and mark each unverified reservation `status: unverified-this-session` with the date of the attempt. Preserving the current expiry after a failed verification is how a stale citation survives — and Art. 15(4) is the strongest citation in the file.                                                                                                                                                                                                                                                                                       | the guard keeps failing until a real verification happens                                                                                                                 |

**Escalated, not decided (repository policy).** `results/audit_S7/_baseline/sha256_pre.txt` is
deprecated and has no consumer — verified below. Deleting it versus retaining it as lineage is a
repository policy call; this plan verifies and records, it does not delete.

---

## Phase A — `docs/manuscript/sections/protocol_v2.tex` (no computation)

Reviewer #3's nominative demand. Every element already exists in the repository; this phase reads
and writes, it runs nothing.

**Deliverable**: `docs/manuscript/sections/protocol_v2.tex`, English, IEEEtran-compatible.

**Hard constraints imposed by the existing suite** — a violation of any of these fails
`tests/test_manuscript_integrity.py` immediately:
- every `\begin{env}` must be in `STANDARD_ENVIRONMENTS` (`:194-201`) or carry a `\newtheorem` in
  the main document (`test_sections_assemble_into_the_main_document:215`);
- every `\ref`/`\eqref`/`\hyperref` target must be defined somewhere under `docs/manuscript/`;
- every `\cite` key must resolve in `docs/manuscript/articleA_biblio_v64.bib`
  (`test_every_cited_key_resolves_in_the_bibliography:167`);
- no key from `PROSCRIBED_KEYS` (`:261`).

**The eight mandatory rubrics.** (The prompt's exit gate says "six rubriques"; the LOT A body lists
eight bullets. All eight are covered; the discrepancy is declared, not silently reduced.)

| #   | rubric                                                                   | source of truth to quote                                                                                                                                                                                               |
| --- | ------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A-1 | exact resampling unit of every confidence interval                       | see the inventory table below                                                                                                                                                                                          |
| A-2 | inter-seed aggregation procedure                                         | `per_seed_detections` (`exp_R4_main_table.py:260-265`), `analyze_pair` (`:267-283`)                                                                                                                                    |
| A-3 | treatment of the 12 ProteuS transitions                                  | `itertools.product(TRANSITIONS, SEEDS)` (`exp_R4_main_table.py:383-385`); 1080 = 30 seeds × 36 streams = 30 × (12 transitions × 3 widths); transitions pooled **within** a seed, seeds never pooled across transitions |
| A-4 | complete detector and forest hyper-parameters                            | `results/audit_S7/config_matrix.md` §1–§3, `config/experiment_ssot.py`, and the factories at `exp_R4_main_table.py:162-185`                                                                                            |
| A-5 | multiple-comparison correction, or explicit justification of its absence | see below                                                                                                                                                                                                              |
| A-6 | complete separations                                                     | see below                                                                                                                                                                                                              |
| A-7 | legitimacy of the paired bootstrap                                       | `x0, x1 = rng.normal(), rng.normal()` at `exp_R2:78`, `exp_R6:51`, `exp_R7:60`, `exp_R9:60` — one source line, two draws, inside the step loop                                                                         |
| A-8 | triple per-worker PRNG lock, verbatim, with its motive                   | `exp_R2_instrumented_blind_spot.py:63-68`, motive at `config/experiment_ssot.py:19-23`                                                                                                                                 |

**A-1, the inventory to state honestly** (this is the rubric the reviewer asked for; the answer is
not uniform across the paper and must not be presented as if it were):

| statistic                                                                              | resampling unit                                           | n_boot | seed                   | PRNG                                         |
| -------------------------------------------------------------------------------------- | --------------------------------------------------------- | ------ | ---------------------- | -------------------------------------------- |
| Table I / KSWIN-sweep CI (`exp_R4_main_table.py:232-237`, `exp_R4_kswin_sweep.py:169`) | **run** (360 per cell), unpaired                          | 1000   | `12345 % (2**31-1)`    | **global** `np.random.seed` (`:413`, `:258`) |
| Hydra ratio CI (`exp_R6_hydra_survival.py:105-111`)                                    | **seed index, paired**                                    | 10000  | `BOOT_SEED = 20260906` | local `default_rng`                          |
| S6 envelope / λ_op / Δe_c (`s6_envelope_stats.py:131-157,227-232`)                     | seed, paired and unpaired variants                        | 10000  | `BOOTSTRAP_SEED`       | local `default_rng`                          |
| R5 Δe CI (`exp_R5_common.py:226-229`)                                                  | **the per-drift jump** — K = 7 (BAF), 5 / 1 / 2 (INSECTS) | 1000   | `DELTA_E_RNG = 42`     | local `default_rng`                          |
| R9 exponential-fit KS (`exp_R9_compute_mcrit.py:80-95`)                                | parametric                                                | 2000   | `int(target*1000)`     | local `default_rng`                          |

The K = 1 case (`insects/gradual_balanced`) yields a degenerate interval — `delta_e.parquet`
carries `ci_lo == ci_hi == mean == 0.450341`. State it as a degeneracy, not as a tight interval.

**A-5, multiplicity.** State the family explicitly (7 seed-level pairs in
`exp_R4_seed_level_tests.csv`, 1 in the α-sweep, 6 INSECTS/BAF rows in `table2_values.csv`), then
either apply a Holm–Bonferroni correction over the declared family, or justify its absence on the
ground that every reported p-value sits at the test's resolution floor and no correction over a
family of ~14 can lift `2^-29 · 14 ≈ 2.6e-8` above any conventional α. Prefer the second, written
as a justification with its arithmetic, since it is true and the prompt allows it explicitly.

**A-6, complete separations.** `p = 1.86e-9` is **not an estimate**: it is
`2 · 2^-30 = 2^-29 = 1.8626451e-9`, the two-sided sign test's resolution floor at n_eff = 30
(verified numerically; `binomtest(30, 30, 0.5, alternative='two-sided')`, `exp_R4_main_table.py:272`).
Report it as `p ≤ 2^-29` and pair it with an effect size. Every cell at `F1 = 0.00` against
`F1 = 1.00` takes the same treatment. Named instances to cover: `PHT+ARF c=1` 0/1080 vs `PHT+HT`
932/1080; `EDDM+ARF c=1` 0/1080 vs 882/1080; `SRP+PHT c=1` 0/1080 vs 932/1080; `KSWIN+ARF c=1`
1080/1080 vs 0/1080; `PHT+RF` 913/1080; `ADWIN+RF` 959/1080 vs `ADWIN+ARF c=1` 1063/1080
(`results/R4_proteus_evaluation/data/exp_R4_seed_level_tests.csv`). Effect size to report: the
run-level detection-rate difference with a Wilson or Agresti–Caffo interval, computed at the seed
level so it is commensurable with the test.

**A-7.** State that R2, R6, R7 and R9 consume exactly two `rng.normal()` per step from
`default_rng(safe_seed)` and that the covariate streams are therefore bit-identical for a given
`(boundary_shift, seed)` — which is what licenses seed-paired resampling across arms. Record the
two deviations found: R3 deliberately uses legacy `RandomState(MT19937)` ("AE Visual Match",
`exp_R3_regime_crossover.py:67-69`) and R8 has only `default_rng`, no global lock
(`exp_R8_lambda_op_sweep.py:68`).

**A-8.** Reproduce the lock verbatim with its motive: River's Cython tree-spawn path reads the
global NumPy singleton, so the lock is required and must not be "cleaned up"
(`config/experiment_ssot.py:19-23`). Name the R4 variant explicitly — `exp_R4_main_table.py:189-191`
locks `random.seed` + `np.random.seed` but holds no local generator.

**Also written in Phase A**, because U1 is already ruled: the two-parameter statement of the
warning-detector change (`0.01 → 0.002`, `32 → c`) and its mechanical corollary — strict
warning/drift synchronisation, which is what accounts for replacement trees that have learned
nothing. Both facts must coexist in the text: the warning configuration is mechanically
determining (it gates replacement-tree availability, hence transient duration) **and** currently
inert in the tested configuration (S6/G2: 47/47 and 36/36 replacements install an untrained tree;
the two ADWINs of a member are identically-fed clones firing at the same step).

---

## Phase D+E — guards and freeze, before any re-run

Installed first so that Phases B and C are judged by tests that already exist.

### D-1 — the five missing non-regression tests (`regeneration_spec.md` §G3)

Inventory established: **none of the five exist**; the suite's 25 tests give R1, R3, R4 and R5
**zero** coverage. R2 artifacts are read at `tests/test_R6_hydra.py:14-15` (Hydra power-law fit) and
`tests/test_S7_consistency.py:298-308` (τ_ARF invariance across scenarios), neither of which
asserts any §G3 claim. The balance to implement is therefore all five files.

Write them against the committed artifacts only, no re-run, each skipping with an explicit motive
when its artifact is absent (reuse the `_read` / `pytest.skip` idiom of
`tests/test_S7_consistency.py:280-284`, which already carries the mandatory
`float_precision='round_trip'`).

| file                              | artifacts                                                                                                  | note                                                                                                                                                                                |
| --------------------------------- | ---------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `tests/test_R1_race_condition.py` | `R1_race_condition.parquet`                                                                                | post-A1 values: `Share_Blind_Spot(25) = 0.895`, `Detection_Rate(25) = 0.920` (`authorized_deviations.txt:18-20`), **not** the 0.88 / 0.965 of the spec                              |
| `tests/test_R2_starvation.py`     | `R2_instrumented_{A,B,C}_PHT_ARF.parquet`                                                                  | spec values stand; artifacts verify against the baseline                                                                                                                            |
| `tests/test_R3_crossover.py`      | `R3_regime_crossover_metrics.parquet`                                                                      | the spec's "`~24 pp` will fail" note is **stale**: the manuscript already reads `23.4` at `.tex:511` and `:522`. Assert 23.41 pp ± 0.5. Correct the note in `regeneration_spec.md`. |
| `tests/test_R4_table1.py`         | `exp_R4_results_aligned_fusion.csv`, `exp_R4_seed_level_tests.csv`, `exp_R4_results_KSWIN_alpha_sweep.csv` | **pin the pre-unification values**. This test is the instrument that measures LOT B: it must fail after the re-run if and only if a numeral moved.                                  |
| `tests/test_R5_table2.py`         | `table2_values.csv`, `flooding_decomposition.parquet`, `delta_e.parquet`                                   | spec values verified present in the artifacts                                                                                                                                       |

Line anchors in `regeneration_spec.md` (`.tex L332–L357`, `L373`, `L388`, `L402`…) predate the
A1–A10 and M1–M8 edits and are off by 100–150 lines. Re-grep before anchoring; never quote them.

### D-2 — bit-freeze coverage: state what is actually covered

`artifacts_sha256_pre_ssot.txt` holds 34 entries: R1 ×1, R2 ×3, R3 ×1, R4 ×4, R5 ×15, R6 ×1,
R7 ×2, R8 ×4, R9 ×2, audit_S7 ×1. `sha256sum -c` gives **29 OK, 5 FAILED**, exactly the five
declared in `authorized_deviations.txt`.

The specification asks to "extend to R2, R3 and R7". Measured finding: `docs/ENVIRONMENT.md:66-73`
already records a full re-execution of R1–R4 and R6–R9 with a per-stage hash verdict, R2, R3 and
R7 among them, each "identical". **The extension the specification names is already discharged.**
The real residual is elsewhere and is declared as such:

- **R5** — `docs/ENVIRONMENT.md:76` says "not re-measured in this stream". 15 of the 34 frozen
  hashes are R5's and none has ever been empirically re-verified. Phase C re-runs part of R5, which
  is the opportunity to close this.
- **S6** — **zero entries** in the manifest. The S6 Parquet corpus is guarded only by
  `tests/test_S6_traces.py::test_parquet_replay_is_byte_identical`, not by the frozen list.

Action: record both gaps in `docs/ENVIRONMENT.md`; do not silently claim the extension is done.

### D-3 — authorized-deviation audit

Five declared of 34. Each traces to a dated commit: R1 and R9 to A1 (`8fb0875`), the two R8
aggregations to A2 (`70ca9ae`), `hydra_survival.csv` to S7-bis §4a. Verification is a
`git log --follow` per file plus a diff of the declared measured effect against the artifact.

Also correct the stale claim at `results/audit_S7/reconciliation_report.md:523` ("all 34 artifacts
unchanged"), true when written, false since `8fb0875`. A reader of that report alone is misled.

Phases B and C each add deviations; they are written with their motive and measured effect at the
moment they are produced, never retrofitted.

### D-4 — float-join guard

Census measured, and it does not match the specification's figure. There are **6** `.merge`/`.join`
call sites in the repository, of which 4 join on a float key; exactly **one** of those reads a CSV
(`tests/test_S7_consistency.py:292`, R6 parquet ⋈ R9 CSV on `boundary_shift`), and it is already
hardened at `:293` and regression-locked by `len(m) == len(r6) == len(r9)`. The other three are
parquet-only (binary, no text round-trip). The specification's "18 jointures flottantes recensées"
is not reproducible by any grep tried and its methodology is stated nowhere. **Declared as
unreconciled**, not silently dropped.

The guard is still worth installing, because the hazard is a future `read_csv`, not a present one.
Add to `tests/test_S7_consistency.py` an AST walk in the style of the existing
`cusum_delta_sites` (`:178`): every `pd.read_csv` under `experiments/` and `tests/` must pass
`float_precision='round_trip'`, with a declared exemption dict keyed by `file:line` and carrying a
motive — the same "option B applied to the remainder, not silence" pattern the module already uses.
Current exemptions to declare: the six raw-source readers in `exp_R5_*` (no merge anywhere in those
files) and `tests/test_R8_lambda_op.py:68` (`nrows=0`, header only).

### D-5 — `sha256_pre.txt`

**Verified: no test and no script reads it.** Repo-wide grep over `.py`, `.sh`, `.md` finds only
prose references — its own deprecation banner (`:1-5`), a narrative line in
`reconciliation_report.md:524`, and the prompt itself. No CI, no Makefile exists. It covers 11
manuscript/editorial artifacts, of which 3 fail and 2 no longer resolve
(`articleA_blindspot_v63_camera_ready.tex` absent, `docs/sections/framework_v2.tex` moved by A5) —
consistent with its own banner. Record the verification. Deletion is escalated, not performed.

### E — source freshness

The `expires_on` column (`source_verification.md:84-88`) and its guard
(`tests/test_manuscript_integrity.py:290`) already exist (action M7). The three reservations expire
2027-03-06 and are current as of today. **Residual: the online re-verification only.**

Re-verify in session, with network access, and date the re-verification:
1. Digital Omnibus on AI — amendments to AI Act Art. 15 and Art. 72;
2. the Art. 72 implementing act (post-market monitoring plan template) — legal deadline
   2026-02-02, adoption unconfirmed;
3. AWS SageMaker Model Monitor commercial status.

Then either push `expires_on` out with the new session date, or downgrade the source to status
**X**. Art. 15(4) is the strongest citation in the file; treat it accordingly.

---

## Phase B — `warning_detector` unification, R3 and R4 (~63 min compute)

### B-1 — declare in the SSOT, then change three call sites

Add to `config/experiment_ssot.py`, each with its motive as an inline comment (no local literal
anywhere, on pain of `test_S7_consistency.py`):

```
R3_C_WARN     = C_INT    # was river default clock=32
R3_WARN_DELTA = 0.002    # was river ARF default 0.01
R4_C_WARN     = <c>      # follows the drift clock per pipeline
R4_WARN_DELTA = 0.002
```

Replace the now-false comment at `config/experiment_ssot.py:108`
(`R3_C_INT = C_INT  # warning_detector left at river default`).

Three sites, one added keyword each:
- `experiments/R3_regime_crossover/exp_R3_regime_crossover.py:78`
- `experiments/R4_proteus_evaluation/exp_R4_main_table.py:176-177` (`make_arf`, and its stale
  comment "warning kept at default")
- `experiments/R4_proteus_evaluation/exp_R4_kswin_sweep.py:139` (`make_arf`)

`make_srp` (`exp_R4_main_table.py:178-181`) already pins both and is the pattern to copy.

### B-2 — correct the Table I bootstrap in the same regeneration

`bootstrap_ci_half_width` (`exp_R4_main_table.py:232-237`, `exp_R4_kswin_sweep.py:169`) resamples
seed indices instead of rows, on a locally injected `default_rng(BOOTSTRAP_SEED)`, and the global
`np.random.seed` at `:413` / `:258` is removed. Scheme to reuse verbatim:
`exp_R6_hydra_survival.py:105-111` (`idx = rng.integers(0, n, size=(N_BOOT, n))`, then percentiles
of the per-replicate mean). The caption's claim of seed-level independence then matches the
computation.

Landing this with B-1 means one regeneration produces both effects. The before/after report must
therefore attribute each moved numeral to one cause or the other, which requires **two** R4 runs:
one with B-1 only, one with B-1 + B-2. At 54 min each this is affordable and is the only way the
attribution is honest.

### B-3 — re-run and reconcile

Three runs, not two. Under `PYTHONHASHSEED=0`, set by the wrappers.

| run   | configuration      | script                   | measured cost | purpose                                                                |
| ----- | ------------------ | ------------------------ | ------------- | ---------------------------------------------------------------------- |
| B-3.1 | U1 only            | `./run_experiment_R4.sh` | 3241 s        | isolates the `warning_detector` effect                                 |
| B-3.2 | U1 + B-2 bootstrap | `./run_experiment_R4.sh` | 3241 s        | isolates the resampling-unit effect; the pair makes attribution honest |
| B-3.3 | U1 **and** U0      | `./run_experiment_R3.sh` | 539 s each    | the control arm                                                        |

U0 is carried on R3 rather than R4 for cost: 539 s against 3241 s, and R3 is where the
exposed numerals sit (the 23.4 pp accuracy gap at `.tex:511` and `:522`, the monotone miss
band at `:476` and `:482`, the false-alarm halving at `:484`). The 5-seed probe already
moves `acc(ARF)` from 0.9848 to 0.9802 under U1 at Δe = 0.50; U0 is what says whether that
move is the warning mechanism doing its job or the absence of one.

**Report the three arms side by side for every R3 numeral at risk**, and state in
`protocol_v2.tex` which arm the published figures come from. If the blind spot is materially
weaker under U0, that is a scope statement the paper must carry in `sec:limitations` — not a
reason to suppress the arm. If it is invariant, the paper gains its strongest generality
result at a cost of nine minutes.

`tests/test_R3_crossover.py` and `tests/test_R4_table1.py` from Phase D-1 are the instruments. Any
failure is the measurement, not a defect to silence.

Reconciliation surface:
- `docs/manuscript/tables/table1_proteus_summary.tex` is **byte-identical** to
  `results/R4_proteus_evaluation/tables/table1_proteus_summary.tex` and is `\input` at `.tex:438`.
  `test_manuscript_assets_match_the_pipeline` enforces the identity, so the manuscript copy is
  refreshed from the pipeline render, never hand-edited.
- R3 prose numerals at risk, re-grep before anchoring: the accuracy gap **23.4 pp** and the pair
  `RF ≈ 0.750` / `ARF ≈ 0.984` (`.tex:511`, repeated `:522`); the monotone miss band
  1 % at Δe = 0.26 → 100 % at Δe = 0.50 and the HT's 77 % artefactual miss (`.tex:476`, `:482`);
  the qualitative "halving pre-drift False Alarms" (`.tex:484`, ratio 1.98 in the artifact).
- `README.md:296` — rewrite: the warning default is `ADWIN(delta=0.01, clock=32)` not
  `ADWIN(clock=32)`; R6–R9 also pin both; `make_srp` pins both. After unification the heterogeneity
  it documents no longer exists.
- `results/audit_S7/config_matrix.md` §3 and §7 — same corrections, plus the delta column.
- `authorized_deviations.txt` — one entry per changed artifact, motive and measured effect.
- `docs/ENVIRONMENT.md:68-69` — new hash verdicts for R3 and R4.

Output format for every manuscript edit: SEARCH/REPLACE diff, 9 tildes, anchors re-grepped from the
live file, never quoted from a report.

**Excluded from patching** (`CLAUDE.md`, the one exclusion): `sec:race` (L168), `sec:hydra` (L185),
`sec:starvation` (L210), `sec:decoupling` (L376). Fixes belonging to that material go to
`docs/manuscript/sections/framework_v2.tex`. None of the R3/R4 numerals above fall in those four
subsections — verified: they sit in `sec:crossover` (L468) and `sec:solution_rf` (L501).

---

## Phase C — frozen-classifier Δe oracle

### The defect, precisely

`exp_R5_compute_delta_e.py:15-48` builds the reference error stream from a single
`HoeffdingTreeClassifier` that calls `learn_one` at every step from t = 0, is never reset and is
never forked. `estimate_delta_e_adaptive` (`exp_R5_common.py:204-233`) then reads pre/post windowed
error means around each canonical drift. The estimator is therefore measured on a model that is
already absorbing the change it is meant to reveal — the exact contamination the manuscript itself
invokes to justify using a *theoretical* Δe on the synthetic arm ("at b = 4.0, empirical Δe ≈ 0.02
vs theoretical ≈ 0.50"). The three BAF values come out at −0.0009, −0.0000, +0.0001 with intervals
covering zero: what an estimator blind to the drift it measures would produce.

### Design — reuse, do not reinvent

S6's `frozen` arm is `s6_runner.py:198-261`: `copy.deepcopy(arf)` fork, then `segment(..., learn=False)`
(`:89-127`) which keeps calling `predict_one` and never calls `learn_one` again. Its fidelity is
certified by gate G1 (`gates/g1_deepcopy_fidelity.py:74-84`) and its immobility asserted by
`tests/test_S6_traces.py::test_frozen_arm_is_immobile:123-132`. Its oracle usage is
`erasure_share` (`s6_causal.py:144-182`): `e_total = A_frozen − A_full`.

Transplant exactly that onto R5's streams. The specification says "adaptation disabled after the
warm-up", so the fork is taken **once**, at end of warm-up, not per drift:

- BAF: fork at `cfg.BAF_WARMUP = 100_000`; every canonical drift (125000 … 875000) is downstream.
- INSECTS: fork at `get_warmup_steps(n)` = `min(100_000, 0.10·n)` (`exp_R5_common.py:22-29`) —
  5284 / 2414 / 7998, all strictly before the first drift (14352 / 14028 / 26568).

Then feed the frozen error stream to the **same** `estimate_delta_e_adaptive`, with the **same**
`INSECTS_DRIFTS_DELTA_E` / `BAF_DRIFTS` positions and the same adaptive windows, so the oracle and
the published value differ in exactly one input.

Written to a **new** artifact `results/R5_real_world_evaluation/data/delta_e_oracle.parquet`, not
into `delta_e.parquet` — which is one of the 34 frozen hashes. Zero authorized deviation is then
needed, and the published adaptive value remains reproducible as its own control.

Cost: the Δe stage is single-pass and seed-free (the HT is deterministic; `error_stream_baf` takes
no seed). The oracle runs the frozen shadow inside the same pass, so the added cost is one
`predict_one` per step per stream — a fraction of step 5 of `run_experiment_R5.sh`, nothing like
the 4.5 h BAF evaluation stage.

**Deliberately deferred, declared**: an ARF-based oracle arm. The pipelines under test are
ARF-based, but the decision tree below turns only on whether a non-adapting model sees an error
jump at the canonical BAF positions; a frozen HT settles that, and an ARF pass over 3 × 10⁶ BAF
rows costs roughly an order of magnitude more. Mark it `# ponytail:` with this upgrade path.

### Decision tree — do not pre-judge

Run first, then rule:
- **Δe_oracle ≈ 0 on all three BAF variants** → BAF becomes an explicit negative control in the
  manuscript, which strengthens the article. Corroborating evidence already available: Table II
  shows F1 ≈ 0.10 / 0.09 / 0.00 including for the **non-adaptive** `PHT + HT`
  (`table2_values.csv:2-4`, `F1_PHT_HT = 0.0952, 0.087, 0.0`); a non-adaptive baseline that also
  fails means there is no blind spot to demonstrate on BAF.
- **Δe_oracle ≫ 0** → BAF is a stream whose drift is *masked* by adaptation, and that is the
  paper's strongest demonstration, currently invisible.

Report the verdict with its measurement. Manuscript consequences (`.tex:494-499`, Table II caption,
`sec:limitations`) are drafted only after the numbers exist.

---

## Verification

Run in this order; each gate is a command, not a judgement.

```
sha256sum -c results/audit_S7/_baseline/artifacts_sha256_pre_ssot.txt
    # gate: 29 OK / 5 FAILED before Phases B and C; after, exactly the newly declared entries
/home/m53/miniforge3/envs/Trading/bin/python -m pytest tests/ -q
    # gate: 25 tests before Phase D, 30 after; zero failures outside the declared LOT B instruments
./run_experiment_R3.sh                       # 539 s reference
./run_experiment_R4.sh                       # 3241 s reference
/home/m53/miniforge3/envs/Trading/bin/python experiments/R5_real_world_evaluation/exp_R5_compute_delta_e.py
tectonic docs/manuscript/$(cat docs/manuscript/CURRENT)    # compile check only
```

Per-phase gates:
- **A**: `pytest tests/test_manuscript_integrity.py -q` passes with `protocol_v2.tex` present —
  proves no undeclared environment, no dangling `\ref`, no unresolved `\cite`.
- **D**: the five new tests pass against the pre-B artifacts; the float-join guard fails on a
  deliberately introduced bare `read_csv` and passes once reverted.
- **B**: `test_R4_table1.py` and `test_R3_crossover.py` state exactly which numerals moved;
  `test_manuscript_assets_match_the_pipeline` passes after the Table I copy is refreshed;
  `sha256sum -c` shows only declared deviations.
- **C**: `delta_e.parquet` still verifies byte-for-byte; `delta_e_oracle.parquet` carries six rows
  with the same window vectors as the adaptive run — equal windows is the proof the two estimates
  differ in the error stream and nothing else.
- **E**: `test_source_reservations_have_not_expired` passes with the new re-verification date.

Circuit breakers, per `CLAUDE.md`: three remediation attempts on any infrastructure or test failure,
then a declared freeze and halt. A D3 scientific deviation — a re-run that fails to reproduce —
halts immediately; parameters are never adjusted to force convergence.

---

## Files touched

| phase | files                                                                                                                                                                                                                                                                                                                                                                                                   |
| ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A     | `docs/manuscript/sections/protocol_v2.tex` (new)                                                                                                                                                                                                                                                                                                                                                        |
| D     | `tests/test_R{1,2,3,4,5}_*.py` (5 new), `tests/test_S7_consistency.py`, `results/audit_S7/regeneration_spec.md`, `results/audit_S7/reconciliation_report.md`, `docs/ENVIRONMENT.md`                                                                                                                                                                                                                     |
| E     | `docs/editorial/source_verification.md`                                                                                                                                                                                                                                                                                                                                                                 |
| B     | `config/experiment_ssot.py`, `experiments/R3_regime_crossover/exp_R3_regime_crossover.py`, `experiments/R4_proteus_evaluation/exp_R4_main_table.py`, `experiments/R4_proteus_evaluation/exp_R4_kswin_sweep.py`, `README.md`, `results/audit_S7/config_matrix.md`, `results/audit_S7/_baseline/authorized_deviations.txt`, `docs/manuscript/tables/table1_proteus_summary.tex`, the manuscript of record |
| C     | `experiments/R5_real_world_evaluation/exp_R5_compute_delta_e.py`, `experiments/R5_real_world_evaluation/exp_R5_config.py`, `run_experiment_R5.sh`, the manuscript of record (after measurement)                                                                                                                                                                                                         |

---

## SPECIFICATION → PHASE correspondence (anti-drift rule, mandatory)

Every element of `PROMPT_S7-ter.md` appears below. Nothing is left to be discovered after
execution.

| spec element                                                             | phase   | status                                                                                                                                      |
| ------------------------------------------------------------------------ | ------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| LOT A — resampling unit of the CIs                                       | A-1     | covered; per-experiment inventory, non-uniform, stated as such                                                                              |
| LOT A — inter-seed aggregation                                           | A-2     | covered                                                                                                                                     |
| LOT A — 12 ProteuS transitions                                           | A-3     | covered                                                                                                                                     |
| LOT A — full detector/forest hyper-parameters                            | A-4     | covered                                                                                                                                     |
| LOT A — multiple-comparison correction or justified absence              | A-5     | covered; justified absence, with arithmetic                                                                                                 |
| LOT A — complete separations, `p ≤ 2^-29` + effect size                  | A-6     | covered                                                                                                                                     |
| LOT A — legitimacy of the paired bootstrap                               | A-7     | covered; two deviations (R3, R8) declared                                                                                                   |
| LOT A — triple PRNG lock verbatim + motive                               | A-8     | covered; R4 variant declared                                                                                                                |
| LOT A — deliverable at `docs/sections/protocol_v2.tex`                   | A       | **path corrected** to `docs/manuscript/sections/` (A5); declared                                                                            |
| LOT B a — unify on the SSOT                                              | B-1     | covered; U1, and the change is two parameters, not one                                                                                      |
| LOT B b — re-run R3 and R4                                               | B-3     | covered; two R4 runs to separate B-1 from B-2                                                                                               |
| LOT B c — before/after on every R3/R4 manuscript value, Table I included | B-3     | covered                                                                                                                                     |
| LOT B d — anchored DIFF if a numeral moves                               | B-3     | covered; anchors re-grepped, never quoted from a report                                                                                     |
| LOT B — the two coexisting facts (determining **and** inert)             | A + B-3 | covered in the protocol text and in the reconciliation                                                                                      |
| LOT C — frozen classifier in parallel on the same stream                 | C       | covered; fork at end of warm-up, per the spec's wording                                                                                     |
| LOT C — reuse S6's `frozen` mechanics, do not reinvent                   | C       | covered; `s6_runner.py:198-261` transplanted                                                                                                |
| LOT C — recompute Δe on 3 BAF + 3 INSECTS                                | C       | covered                                                                                                                                     |
| LOT C — decision tree, ruled on measurement                              | C       | covered; verdict deferred to the numbers                                                                                                    |
| LOT D — inventory then implement the balance of the five tests           | D-1     | covered; measured balance = all five                                                                                                        |
| LOT D — bit-freeze, extend to R2, R3, R7                                 | D-2     | **already discharged** (`ENVIRONMENT.md:66-73`); real gap is R5 and S6, declared                                                            |
| LOT D — audit the 5 authorized deviations of 34                          | D-3     | covered; plus a stale claim corrected                                                                                                       |
| LOT D — 18 float joins, `float_precision`, static guard                  | D-4     | guard covered; **the figure 18 is unreconciled and declared**; measured census is 6 merges / 4 float keys / 1 CSV-sourced, already hardened |
| LOT D — `sha256_pre.txt` has no reader                                   | D-5     | verified; deletion **escalated**, not performed                                                                                             |
| LOT E — `expires_on` column                                              | E       | **already done** (M7)                                                                                                                       |
| LOT E — test that fails past the date                                    | E       | **already done** (M7)                                                                                                                       |
| LOT E — re-verify the three reservations and date it                     | E       | covered; requires network access                                                                                                            |
| Mode — one agent per worktree, never two on one checkout                 | —       | **open**: a peer session is live on this checkout; resolve at launch                                                                        |
| Mode — an agent never rules repository policy, it escalates              | D-5     | applied                                                                                                                                     |
| Mode — no constant re-declared as a local literal                        | B-1     | applied                                                                                                                                     |
| Format — SEARCH/REPLACE, 9 tildes, anchors never guessed                 | B, C    | applied                                                                                                                                     |
| Format — English for deliverables, French for exchanges                  | all     | applied                                                                                                                                     |

**Not in the specification, found during planning, carried anyway** (each is a defect the phases
above already touch, declared rather than smuggled): `config_matrix.md` conflating two River
defaults in its delta column; `README.md:296` omitting the warning delta; `reconciliation_report.md:523`
asserting a freeze state that no longer holds; `regeneration_spec.md` line anchors stale by
100–150 lines and its "~24 pp" note superseded by the manuscript's own correction to 23.4.

---

## Exit gate

1. `protocol_v2.tex` delivered, eight rubrics covered, integrity suite green.
2. `warning_detector` unified, R3 and R4 re-run, every deviation reported and declared.
3. BAF status ruled **on the oracle measurement**, not before it.
4. Five missing tests implemented; freeze coverage stated truthfully, including what it does not
   cover.
