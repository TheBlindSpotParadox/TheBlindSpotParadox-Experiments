# Debt register — sites carrying a statement the measurements refute

Stream S11-a. One row per site. No section of the manuscript is edited by this stream; the register
is the list the v65 assembly purges.

## How to read it

**Textual anchors, never line numbers.** The three transfer documents cite line numbers that have
all moved; `sync_pass_report.md` §3c tabulates the drifts, and `CLAUDE.md` records the same for
v63 → v64. Every anchor below was re-grepped on the live file with `grep -c -F` returning exactly
`1` before being inscribed. An anchor that did not resolve uniquely was extended until it did,
never approximated.

The anchor column is the single source for the uniqueness gate: it is wrapped in backticks, it is
verbatim, and no anchor contains a backtick or a pipe. The gate is

```sh
# every row of every table below, file = column 1, anchor = column 2
grep -c -F "<anchor>" <file>   # must be exactly 1
```

**The `zone` column has three values.**

- `editable` — the site can be patched today.
- `EXCLUDED (<label>)` — inside one of the four inline subsections `CLAUDE.md` freezes until the
  v65 assembly: `sec:race` (L195-211), `sec:hydra` (L212-236), `sec:starvation` (L237-322),
  `sec:decoupling` (L410-445), line ranges measured on the live 576-line document. The fix belongs
  in `docs/manuscript/sections/framework_v2.tex`, not in the inline copy.
- `GENERATED` — the text is not editable in the `.tex`: it is produced by a Python function and
  copied into `docs/manuscript/tables/`. Correcting it is a source edit **plus** an artifact
  regeneration, therefore an authorised deviation to declare in
  `results/audit_S7/_baseline/authorized_deviations.txt` and a hash to move. The register says so
  rather than leaving the assembler to discover it.

`M` below abbreviates `docs/manuscript/articleA_blindspot_v64_camera_ready.tex`.

---

## 1. Abstract, Introduction, contributions

| file | textual anchor (verbatim) | refuted claim | refuting source | zone |
|---|---|---|---|---|
| `docs/manuscript/articleA_blindspot_v64_camera_ready.tex` | `harbors a fundamental race condition` | Named term withdrawn; `fundamental` is not demonstrated and `race condition` imports a software-concurrency metaphor with no formal counterpart. | `docs/editorial/terminology_map.md`, table *Termes supprimés* | editable |
| `docs/manuscript/articleA_blindspot_v64_camera_ready.tex` | `A Starvation Effect renders the transient signal too brief for CUSUM accumulation` | The transient is not too brief. At the canonical point the exploitable window is `tau_erase = 612` steps, so `mu W = 194` exceeds every threshold considered and the finite-horizon bound degenerates. What binds is the evidence ceiling, not the window length. | `rem:transient_length` and `rem:shortwindow` in the same document; `results/S2_theory/tables/s2_gate_T20.json :: budget_restitution.measured` | editable |
| `docs/manuscript/articleA_blindspot_v64_camera_ready.tex` | `an ensemble-level Hydra Effect accelerates this adaptation by at least 4.1 to 8.0 times over a single tree` | The factor reproduces; the name and its causal attribution do not. Order statistics of the single-tree delay law alone predict `9.22x` at the canonical point against `7.99x` measured, and the within-run inter-tree correlation is `rho_hat` in `[-0.021, 0.053]`. | `docs/theory/transfer_S3.md` §4 item 3; `results/S3/rho_meff.csv` | editable |
| `docs/manuscript/articleA_blindspot_v64_camera_ready.tex` | `the stronger the drift, the \emph{less} likely the external monitor is to detect it` | Not monotone. The measured evidence ceiling rises to a peak at `Delta_e = 0.1936` and declines thereafter (`36.60` down to `19.24`), and the published R3 miss curve under U0 falls from `100 %` at `Delta_e = 0.02` to `0 %` at `0.19` before rising again. | `s2_gate_T20.json :: budget_restitution.measured`; `results/R3_regime_crossover/data/R3_regime_crossover_metrics.parquet` | editable |
| `docs/manuscript/articleA_blindspot_v64_camera_ready.tex` | `render an external monitoring pipeline \emph{entirely inoperative}` | Superlative withdrawn. The measured statement is a null recall on the configurations tested. | `terminology_map.md`, superlatives table | editable |
| `docs/manuscript/articleA_blindspot_v64_camera_ready.tex` | `We derive the critical ensemble size $M_{\mathrm{crit}}$ inducing structural failure.` | `cor:mcrit` is withdrawn thirty lines below, in the same document: the distribution-free upper end saturates as soon as `M F(s) >= 1`, and in the saturated region it does not depend on `M`, so no ensemble size is certified at any target. | `cor:mcrit` in the same document; `docs/theory/transfer_S3.md`, rule D5(b) | editable |
| `docs/manuscript/articleA_blindspot_v64_camera_ready.tex` | `whose stationary \emph{Starvation Effect} defeats CUSUM and is amplified by the ensemble-level \emph{Hydra Effect}` | `defeats` belongs to the withdrawn verb family; the amplification attribution is retired with the Hydra mechanism. | `terminology_map.md`; `s6_causal.json :: erasure_share_post_fork.a_pos_common.pooled` | editable |
| `docs/manuscript/sections/related_work_v2.tex` | `which is why we evaluate an` | Announces an input-space arm alongside the error-stream arms. No such arm exists: S9 has no branch in `git log --all`, no directory under `results/`, no transfer under `docs/theory/`. | absence measured on the repository; see (C4) in `docs/editorial/thesis_v4.md` | editable |

## 2. Background and related work — the EDDM instantiation

| file | textual anchor (verbatim) | refuted claim | refuting source | zone |
|---|---|---|---|---|
| `docs/manuscript/articleA_blindspot_v64_camera_ready.tex` | `is defeated by an adaptation time $\tau_{\mathrm{ARF}} = \mathcal{O}((\Delta e)^{-\alpha})$ with $\alpha \approx 1$` | Assigns EDDM a stopping time scaling as `lambda / Delta_e`. EDDM is explicitly **not** instantiated and no `R_EDDM` is claimed: its statistic is a ratio of the cumulative mean and standard deviation of inter-error distances against the running maximum of that same path, so the post-change evidence it requires grows with the length of the stationary history. | `docs/manuscript/sections/framework_v2.tex`, paragraph *Family instantiations* | editable |
| `docs/manuscript/sections/related_work_v2.tex` | `share the accumulation structure and inherit its window sensitivity.` | Same assignment, in the section that replaces the above. DDM, EDDM and ECDD are grouped with the CUSUM family on an accumulation structure EDDM does not have. | idem | editable |
| `docs/manuscript/sections/related_work_v2.tex` | `applies a two-sample test between a` | KSWIN's evidence requirement is presented without its false-alarm level. Deployed at `alpha = 0.005` its requirement is `22.68`; at the common level of a `lambda = 50` CUSUM it is `42.00`, above the measured ceiling `33.51`. Rule B9 makes the disclosure mandatory. | `docs/theory/S2bis_narrative_payload.md` §(b); `s2_gate_T20.json :: floor_and_family.family_requirements` | editable |

## 3. The ten KSWIN / ADWIN immunity sites

Enumerated in `S2bis_narrative_payload.md` §(b). Two of the ten are already correctly hedged and are
the phrasing model; they are listed with no action so the assembly does not re-open them.

| file | textual anchor (verbatim) | refuted claim | refuting source | zone |
|---|---|---|---|---|
| `docs/manuscript/articleA_blindspot_v64_camera_ready.tex` | `Windowed and distributional monitors (ADWIN~\cite{bifet_adwin_2007}, KSWIN~\cite{raab_kswin_2020}) escape by construction` | At a common false-alarm level neither clears the measured ceiling: `R_ADWIN = 43.34` and `R_KSWIN = 42.00` against `33.51` at `lambda = 50`. `escape by construction` is a family property the arithmetic does not support. | `S2bis_narrative_payload.md` §(b); `s2_gate_T20.json :: floor_and_family.family_requirements.common_alpha_ladder[3]` | editable |
| `docs/manuscript/articleA_blindspot_v64_camera_ready.tex` | `immune to starvation while its reference window holds pre-drift data` | Conditional already present; the missing element is the `alpha` disclosure. The site is inside a frozen subsection. | idem | EXCLUDED (`sec:starvation`) |
| `docs/manuscript/articleA_blindspot_v64_camera_ready.tex` | `the Decoupling Principle is satisfied by construction` | Same `by construction` reflex, applied to the non-adaptive classifier. The HT arm is measured (`932/1080`), not certified. | idem | EXCLUDED (`sec:decoupling`) |
| `docs/manuscript/articleA_blindspot_v64_camera_ready.tex` | `ADWIN + ARF: windowed immunity, not a clock artefact` | Immunity claim in a heading. The measured statement is robustness on the tested settings, at the level actually deployed. | idem | editable |
| `docs/manuscript/articleA_blindspot_v64_camera_ready.tex` | `ADWIN remains immune to starvation as long as $W_0$ spans that transient` | Conditional present, level undisclosed: ADWIN runs at `delta = 0.002`, `45x` tighter than a common requirement asks at `lambda = 15`. | `s2bis_proteus_gate.json :: family_requirements_at_lambda_eq.per_couple["R4 deployed lambda_ref (c=0)"]` | editable |
| `docs/manuscript/articleA_blindspot_v64_camera_ready.tex` | `survives only because it is a windowed rather than cumulative monitor` | Incomplete: it also survives because it is deployed at a level the CUSUM it is compared against is not read at. | idem | editable |
| `docs/manuscript/articleA_blindspot_v64_camera_ready.tex` | `rendering it structurally immune to transient signal erasure` | `structurally` is retracted. The measured resolution stands; the mechanism claim does not, since at a common level KSWIN does not clear the ceiling and the same PHT reaches `F1 = 1.0000` at `lambda = 5`. | `S2bis_narrative_payload.md` §(b); `results/S2bis_calibration/tables/s2bis_proteus_sweep.csv` | editable |
| `docs/manuscript/articleA_blindspot_v64_camera_ready.tex` | `escapes the starvation regime entirely, restoring perfect detection` | Two superlatives, and a family attribution the threshold ladder contradicts. | `terminology_map.md`; `s2bis_proteus_sweep.csv` | editable |
| `docs/manuscript/articleA_blindspot_v64_camera_ready.tex` | `A distribution-based KSWIN monitor avoids the constraint on the settings we test` | **No action — phrasing model.** Already scoped to the tested settings and already declared a regime-restricted observation rather than an immunity. | `S2bis_narrative_payload.md` §(b) | editable |
| `docs/manuscript/articleA_blindspot_v64_camera_ready.tex` | `on the settings we test they restore detection at no predictive cost` | **No action — phrasing model.** | idem | editable |

## 4. `M_crit` and the starvation boundary

| file | textual anchor (verbatim) | refuted claim | refuting source | zone |
|---|---|---|---|---|
| `docs/manuscript/articleA_blindspot_v64_camera_ready.tex` | `We derive an upper bound on the probability of missed detection and a critical ensemble size` | Announces `M_crit` as a deliverable immediately above the corollary that withdraws it as a design rule. | `cor:mcrit` in the same document; `transfer_S3.md` D5(b) | editable |
| `docs/manuscript/articleA_blindspot_v64_camera_ready.tex` | `provide direct empirical support for the Starvation Boundary derivation` | The derivation's only instantiation is retracted in the same document: the plug-in upper end falls below the Wilson 95 % lower end of the measured `P_miss` in `10` of `80` testable cells. The fits support the measured race, not the boundary. | *Retraction of the single-tree instantiation* in the same document; `results/S3/bounds_grid.csv` | editable |
| `docs/manuscript/articleA_blindspot_v64_camera_ready.tex` | `This definitively confirms Corollary~\ref{cor:mcrit}` | Cites a withdrawn corollary as confirmed, and `definitively` is a superlative. The SRP measurement stands on its own (`0/1080` against `932/1080`). | `cor:mcrit`; `transfer_S3.md` D5(b); `results/R4_proteus_evaluation/data/exp_R4_seed_level_tests.csv` row 1 | editable |
| `docs/manuscript/articleA_blindspot_v64_camera_ready.tex` | `We derived the critical size $M_{\mathrm{crit}}$ beyond which cumulative monitors structurally fail.` | Same withdrawn corollary, plus `structurally fail`, in the Conclusion. | idem; `terminology_map.md` | editable |

## 5. The Hydra attribution

| file | textual anchor (verbatim) | refuted claim | refuting source | zone |
|---|---|---|---|---|
| `docs/manuscript/articleA_blindspot_v64_camera_ready.tex` | `the shortfall is the measured cost of the positive inter-tree correlation induced by shared training data` | The shortfall from the `10x` parallel-chart reference is non-exponentiality of the delay law: order statistics of the single-tree law alone give `9.22x` at `Delta_e = 0.3268` and `4.83x` at `0.1409`, against `7.99x` and `4.12x` measured, leaving `0.87` and `0.85` for dependence **and** marginal mismatch together. Measured correlation `rho_hat` in `[-0.021, 0.053]`. | `transfer_S3.md` §4 item 3; `results/S3/rho_meff.csv`; `results/S3/ks_exponentiality.csv` | EXCLUDED (`sec:hydra`) |
| `docs/manuscript/articleA_blindspot_v64_camera_ready.tex` | `explaining why empirical acceleration ($4$--$8\times$) falls short of the $M$-fold reference rate` | Same attribution, restated in `sec:limitations` as an assumption of the derivation. | idem | editable |
| `docs/manuscript/articleA_blindspot_v64_camera_ready.tex` | `The Hydra Effect thus operates as a \emph{constant-factor} acceleration` | The statement is correct; it is listed because the surrounding paragraph attributes the factor to correlation and because the name is withdrawn. Carried so the two are resolved together at assembly. | `terminology_map.md`; `transfer_S3.md` §4 item 3 | EXCLUDED (`sec:hydra`) |

## 6. `rem:bgswap` and its contradiction inside the same document

| file | textual anchor (verbatim) | refuted claim | refuting source | zone |
|---|---|---|---|---|
| `docs/manuscript/articleA_blindspot_v64_camera_ready.tex` | `provide \emph{additional} evidence that the ARF's continuous self-cleaning erases drift signals` | Noise swaps carry essentially no information about recovery in the weak band: Spearman `0.06` against `tau_err(0.50)` and `0.10` against `tau_err(0.10)` for `Delta_e <= 0.15`, against pooled `0.850` and `0.694`. They are not the adaptation event and are not evidence of erasure. | `docs/theory/S6_causal_evidence.md` §2 | editable |
| `docs/manuscript/articleA_blindspot_v64_camera_ready.tex` | `not, as we previously argued, a signature of noise-driven swaps` | **Correct statement, listed for pairing.** `rem:envelope` already withdraws the noise-swap reading that `rem:bgswap` still asserts, and the two remarks sit in the same document contradicting each other. The pair must be resolved in one edit; this half is inside a frozen subsection. | same document, `rem:envelope` against `rem:bgswap`; `S6_causal_evidence.md` §2 | EXCLUDED (`sec:decoupling`) |

## 7. Mechanism and root-cause attributions

| file | textual anchor (verbatim) | refuted claim | refuting source | zone |
|---|---|---|---|---|
| `docs/manuscript/articleA_blindspot_v64_camera_ready.tex` | `the root cause of the Starvation Effect is not the ensemble itself (Bagging), but its auto-adaptive mechanics (tree-swapping)` | Counterfactual arms sharing one stream, one history and one fork assign `99.3 %` of the post-fork erasure to ordinary incremental learning by the surviving trees (IQR `[0.987, 0.998]`, `n = 1979`) and `0.7 %` to the replacement sequence. | `results/S6_synchronized_traces/data/s6_causal.json :: erasure_share_post_fork.a_pos_common.pooled` | editable |
| `docs/manuscript/articleA_blindspot_v64_camera_ready.tex` | `Windowed and distributional monitors are spared by construction.` | Immunity claim in the Conclusion, contradicted at a common false-alarm level (`43.34` and `42.00` against a ceiling of `33.51`). | `S2bis_narrative_payload.md` §(b); `s2_gate_T20.json` | editable |
| `docs/manuscript/articleA_blindspot_v64_camera_ready.tex` | `The blind spot is most devastating when the external detector is a CUSUM/PHT, due to the Starvation Effect` | `most devastating` is a superlative and the ranking is level-dependent: the cumulative monitor asks the **least** evidence of the three below `ln(1/alpha) ~ 16.3` and the most above it. | `framework_v2.tex` `cor:split`; `s2bis_proteus_gate.json :: cor_split_crossings` | editable |
| `docs/manuscript/articleA_blindspot_v64_camera_ready.tex` | `EDDM confirms family-agnostic starvation` | EDDM never arms on these streams: `0` pre-drift errors, `9` errors over the whole 8,000 steps (range `[6, 12]`) against a `warm_start` of `30`, and `100 %` of the 1,080 runs unarmed. The `F1 = 0.00` row is an arming failure, not an accumulation failure, and `prop:starvation` never applies to it. | `s2bis_proteus_gate.json :: eddm_arming_T_D`; `results/S2bis_calibration/tables/s2bis_proteus_eddm_arming.csv` | editable |

## 8. The p-value form

`S7ter_state_transfer.md` §3 item 6 establishes that `1.86e-9` is not an estimate: it is
`2 * 2^-30 = 2^-29 = 1.8626451e-9`, the resolution floor of the two-sided sign test at `n = 30`,
attained as soon as the separation is complete and independent of its magnitude. It is to be
reported as `p <= 2^-29`, paired with an effect size. Four sites in the manuscript and one in the
generated caption.

| file | textual anchor (verbatim) | refuted claim | refuting source | zone |
|---|---|---|---|---|
| `docs/manuscript/articleA_blindspot_v64_camera_ready.tex` | `a $10.57\times$ F1 gap (sign test $p \approx 2 \times 10^{-9}$) driven entirely by precision` | `\approx` presents a resolution floor as an estimate. | `S7ter_state_transfer.md` §3 item 6; `results/R5_real_world_evaluation/tables/table2_values.csv` | editable |
| `docs/manuscript/articleA_blindspot_v64_camera_ready.tex` | `confirms the same mode more moderately ($1.61\times$, $p \approx 2 \times 10^{-9}$)` | idem | idem | editable |
| `docs/manuscript/articleA_blindspot_v64_camera_ready.tex` | `all $30$ seeds favouring the RF, $p \approx 2 \times 10^{-9}$` | idem | `exp_R4_seed_level_tests.csv` row 3 | editable |
| `docs/manuscript/articleA_blindspot_v64_camera_ready.tex` | `all $30$ seeds favouring the ARF, $p \approx 2 \times 10^{-9}$` | idem | idem row 4 | editable |
| `docs/manuscript/tables/table1_proteus_summary.tex` | `All 30 seeds separate completely (paired sign test $p \approx 2\times10^{-9}$); Wilcoxon is deprecated.` | idem. **Not editable in the `.tex`**: produced by `exp_R4_main_table.build_caption` (`experiments/R4_proteus_evaluation/exp_R4_main_table.py:338-363`) through `fmt_p`. | idem | GENERATED (`exp_R4_main_table.build_caption`) |

## 9. The Table I caption — the generated zone

| file | textual anchor (verbatim) | refuted claim | refuting source | zone |
|---|---|---|---|---|
| `docs/manuscript/tables/table1_proteus_summary.tex` | `Significance is assessed at the seed level (the unit of statistical independence of the synthetic generator)` | Under-disclosure, not a refutation on this artifact. The claim holds for R4: `simulate_stream(..., seed=seed)` produces 30 distinct streams and the HT arm's per-seed mean `F1` takes 6 distinct values, sd `0.0317`. What the caption does not record is that the arms carry unequal variation sources — `make_arf(seed, c)` and `make_rf(seed)` consume the seed, `make_ht()` does not — so the paired interval is not symmetric between arms. On the R5 INSECTS artifacts the identical caption claim **is** refuted: rule B10 returns `PSEUDO-REPLICATED`, one effective independent replicate. | `experiments/R4_proteus_evaluation/exp_R4_main_table.py:174`, `:178-180`, `:202`; `results/R4_proteus_evaluation/data/exp_R4_results_aligned_fusion.csv`; `results/S2bis_calibration/tables/s2bis_flooding_gate.json :: pseudo_replication_B10` | GENERATED (`exp_R4_main_table.build_caption`) |
| `docs/manuscript/tables/table1_proteus_summary.tex` | `1000 bootstrap resamples of the 30 SEED indices, paired across arms, not of the individual runs` | **Correct as printed, listed as lineage.** The caption already records the corrected scheme; the superseded run-level resample off the global NumPy state is what the register documents in §11 below. No edit. | `exp_R4_main_table.py:234-250`; `S7ter_state_transfer.md` §3 | GENERATED |

**What a `GENERATED` correction costs.** Editing `build_caption` and re-running R4 changes
`docs/manuscript/tables/table1_proteus_summary.tex` and its `results/` counterpart. That is a
declared entry in `results/audit_S7/_baseline/authorized_deviations.txt` with its motive and
measured effect, and a hash that moves against
`results/audit_S7/_baseline/artifacts_sha256_pre_ssot.txt`. `tests/test_manuscript_integrity.py::`
`test_manuscript_assets_match_the_pipeline` compares the two copies by SHA-256, so both must be
regenerated in the same pass or the gate fails.

## 10. Statements that survive and must not be re-opened

Listed so the assembly does not spend a pass rediscovering that they are already v3 or v4.

| file | textual anchor (verbatim) | status |
|---|---|---|
| `docs/manuscript/articleA_blindspot_v64_camera_ready.tex` | `The result is a measured bound, not an impossibility.` | Already v3. Survives; the v4 strengthens it from *bound* to *calibration*. |
| `docs/manuscript/articleA_blindspot_v64_camera_ready.tex` | `Both anchors are lower bounds, not point estimates` | Correct and already censoring-aware. |
| `docs/manuscript/articleA_blindspot_v64_camera_ready.tex` | `the ARF adapts \emph{faster} than such a monitor accumulates evidence` | Correct as a description of the race; the erasure attribution that follows it is what changes. |

---

## 11. Audit debt — three items, none closed by this stream

### 11.1 Confidence-interval width factors `5x` / `3x` — OPEN

**Status.** No committed source. Zero occurrences in the repository. Operator arbitration: no
estimator is recomputed by this stream, and the Table I framing of `thesis_v4.md` §T11a.5 treats the
bootstrap defect qualitatively and quotes no factor.

**What is established without them.** `S7ter_state_transfer.md` §3 establishes the defect itself:
the submitted version resampled the 360 rows of a cell with `np.random.choice` drawn from the
**global** NumPy state, while the caption asserted the seed as the unit of statistical
independence. The 36 streams a seed produces share that seed's forest initialisation, so a
run-level resample does not estimate the dispersion the caption reports. The correction is
committed at `experiments/R4_proteus_evaluation/exp_R4_main_table.py:234-250`: a paired resample of
the seed index on a locally injected `default_rng`, scheme reused from
`experiments/R6_hydra_factor/exp_R6_hydra_survival.py:105-111`.

**The command that would close it**, to formalise only if the v65 assembly requires a figure:

```
recompute both estimators cell by cell on
  results/R4_proteus_evaluation/data/exp_R4_results_aligned_fusion.csv   (16,200 rows)
read with float_precision='round_trip'
  estimator A — resample the 360 run indices of the cell   (the superseded scheme)
  estimator B — resample the 30 seed indices, paired        (exp_R4_main_table.py:234-250)
both on a locally injected default_rng, 1000 resamples, the campaign's bootstrap seed
report the ratio of half-widths per cell, and its distribution over the 14 rendered rows
```

Not executed here, by operator arbitration.

### 11.2 BAF `0.0110` — CLOSED, REPRODUCED

`PROMPT_S9.md:115` carries the claim without a committed source. Read-only verification by this
stream closes it, on a stronger reading than the one claimed.

`err_mean_post_fork` in `results/R5_real_world_evaluation/data/delta_e_oracle.parquet` is the mean
error of a Hoeffding tree forked at `BAF_WARMUP = 100_000` and never retrained, over
`[BAF_WARMUP:]` (`experiments/R5_real_world_evaluation/exp_R5_compute_delta_e.py:112`). The BAF
fraud rate over the identical slice of `data/baf/<variant>.csv.gz`, column `fraud_bool`:

| variant | frozen model error | fraud rate, same window | equal |
|---|---|---|---|
| Base | `0.010985555555555556` | `0.010985555555555556` | exact |
| VariantI | `0.011005555555555555` | `0.011005555555555555` | exact |
| VariantII | `0.010981111111111112` | `0.010981111111111112` | exact |

`0.0110` is the four-decimal rounding of all three. The equality is exact rather than to rounding,
because a frozen Hoeffding tree on these streams is a pure majority-class predictor and its error
rate *is* the positive-class rate. No write under `results/`, no campaign re-run, no hash touched.

**One numeral of the same source does not reproduce and is recorded rather than absorbed.**
`PROMPT_S9.md:115` states the adaptive tree at `0.0111`. Measured on
`err_mean_post_fork_adaptive`: `0.011142` (Base) and `0.011112` (VariantII) round to `0.0111`;
`0.011179` (VariantI) rounds to `0.0112`. Both values are carried side by side here, per rule R1(b)
of `docs/theory/transfer_S2.md` §2. It does not touch the negative-control argument.

### 11.3 Global PRNG mutation in `simulate_stream` — OPEN

`experiments/R4_proteus_evaluation/exp_R4_main_table.py:76` calls `np.random.seed(seed)` inside
`simulate_stream` (defined at `:75`). The repository's determinism rule requires stochastic
operations to run on locally injected generators (`SeedSequence`, `default_rng`); a global state
mutation is proscribed.

Discovered while verifying the HT replication grievance of `thesis_v4.md` §T11a.5 item 4 — the same
call is what makes that grievance false, since it is what gives the 30 seeds 30 distinct streams.

**Why it is not fixed here.** The call is load-bearing for the frozen artifacts: R4's outputs are
bit-reproducible against `results/audit_S7/_baseline/artifacts_sha256_pre_ssot.txt` under exactly
this seeding, and `process_transition_seed:189-199` reproduces the same lock verbatim in
`experiments/S2bis_calibration/s2bis_proteus_calibration.py`. Converting it to an injected generator
changes the draw sequence, therefore every R4 and S2-bis artifact, therefore every hash — a full
regeneration with declared deviations, not a local fix. It is recorded as debt with that cost
stated.

---

## 12. Anchor uniqueness — how the gate is run

Every anchor in every table above was verified at `1` before inscription. To re-run the gate after
any edit to the manuscript:

```sh
# extract (file, anchor) from the register's tables and check each one
awk -F'|' 'NF>=5 && $2 ~ /`/ {
    f=$2; a=$3; gsub(/^[ \t`]+|[ \t`]+$/,"",f); gsub(/^[ \t`]+|[ \t`]+$/,"",a);
    print f "\t" a }' docs/editorial/debt_register.md |
while IFS=$'\t' read -r f a; do
  n=$(grep -c -F "$a" "$f")
  [ "$n" = 1 ] || echo "FAIL $n  $f  $a"
done
```

A site whose anchor stops resolving at `1` has been edited or moved: extend the anchor on the live
file and re-measure. Three consecutive failures on the same site freeze the state and escalate,
rather than producing an approximate anchor.
