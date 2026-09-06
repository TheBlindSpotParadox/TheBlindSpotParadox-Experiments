# S7 — Manuscript / artifact reconciliation report

Scope: `docs/manuscript/articleA_blindspot_v63_camera_ready.tex` against the restored `results/` tree.
No numeric result was modified. Every value below was **re-measured** from the committed artifacts by
this audit; nothing is carried over on trust.

Environment: Python 3.12.9, River 0.23.0, numpy 1.26.4, pandas 2.3.2, `PYTHONHASHSEED=0`,
the pinned `Trading` conda environment interpreter.

---

## 0. Residues that survive artifact restoration — READ FIRST

Amendment C requires every Phase-1 `non_traçable` residue to be discharged now that `results/` is
restored. Nine were carried into Phase 1. **Eight are discharged** — seven by direct measurement on
the restored artifacts (`88 %` zombie share, `>95 %` detection rate, `<1 %` detection rate,
`≈11 %` residual at $\Delta e{\approx}0.19$, the five per-jump INSECTS $\Delta e$ values, the
`RF ≈ 0.745 / ARF ≈ 0.985` accuracy pair, and the seven `x/1080` seed-level counts) and one by the
Phase −1 R1 re-run (`λ* ≈ 15–25`, §4.2). Note that discharging is not the same as agreeing: the
`RF ≈ 0.745` pair became traceable and, once traced, **did not reproduce** (finding D-4).

**One does not discharge** (R-1 below), for a structural reason. This audit additionally identified
**two further claims** that are not traceable to any artifact (R-2, R-3) and were not on the Phase-1
list. All three are recorded here, at the top of the report.

| # | claim | line | why it does not discharge |
|---|-------|------|---------------------------|
| R-1 | *"the single-tree HAT stays at ${\approx}40\%$ miss under the same clock"* | L201 | **No artifact runs the claimed configuration.** The sentence is about MATCHED clocks ($c_{\mathrm{int}}=c_{\mathrm{ext}}=1$) with $M=1$. R6 runs $M=1$ with **no** external detector; R7 runs matched clocks with $M=10$; R9 runs $M=1$ but **mismatched** ($c_{\mathrm{int}}=1$, $c_{\mathrm{ext}}=32$). The nearest artifact (R9) gives **68.1 %** overall and **71.6 %** for $\Delta e > 0.30$ — neither the claimed value nor the claimed configuration. Discharging this requires a new run (M=1, `ADWIN(delta=0.002, clock=1)` external), not a re-read. |
| R-2 | *"$\mathrm{ADD} \sim \mathcal{U}\{\tau_{\mathrm{stat}}, \tau_{\mathrm{stat}}+c-1\}$ (mean ${\approx}23$ at $c{=}32$)"* | L119 | Analytic statement with an unstated $\tau_{\mathrm{stat}}$, and the artifact contradicts the implied value. ProteuS drift onset is $\tau^{*}=4000$ and $4000 \bmod 32 = 0$, so Eq. (1) gives $\mathrm{ADD} = 31 + \tau_{\mathrm{stat}}$; Table I measures **exactly 31 with zero variance**, hence $\tau_{\mathrm{stat}} = 0$ and the uniform-phase mean is $15.5$, not $23$. |
| R-3 | *"AMD EPYC 8224P (24 cores, 48 threads) with 192 GB RAM in ${\approx}5$ h total"* | L306 | `/logs/` is in `.gitignore`; no runtime or hardware record is committed. Unverifiable from the repository by construction. (For the record, this audit ran on a 48-core / 187 GB host.) |

A fourth item, the footnote value *"`incremental_abrupt_balanced` has a negative aggregate
$\Delta e$ ($-0.094$)"* (L388), is likewise not traceable: that variant is excluded from
`INSECTS_VARIANTS` (`exp_R5_config.py:42-43`) and is therefore never computed by the pipeline. It is
an excluded-variant justification, not a reported result, so it is listed here for completeness
rather than as a reconciliation failure.

## 1. Incident record — ICDM artifact-repository reproducibility defect (escalate out of S7)

Commit `8debd1c` ("Added documentation"), pushed to `origin/main`, **deleted** `results/R1..R9` and
**added** `results/R01..R18` (a different manuscript, v87) in a single operation. This is an
accidental cross-project overwrite of the ICDM 2026 artifact tree, not a shared architecture.
Recovery, executed before this stream started:

```bash
git restore --source=8debd1c^ --staged --worktree -- results/
```

**Prerequisite verification (executed, gate passed).** `results/` holds `R1_race_condition …
R9_mcrit`, 31 `*.parquet` / `*.csv` artifacts, and

```
PYTHONHASHSEED=0 python -m pytest tests/ -v   ->   4 passed in 0.77s
```

The restored tree matches the manuscript's lineage. Independent confirmation obtained later in this
stream: re-running `./run_experiment_R9.sh` regenerated
`results/R9_mcrit/data/results_instrumented_A_ADWIN_HAT.csv` **bit-for-bit identical**
(`sha256 d8bff453640e6434ccbf45fa8b9d841dd8a944614cbb69c04e489ea898bac309`), and
`exp_R6_compute_hydra.py` regenerated its `.tex` snippet bit-for-bit identical
(`sha256 4d9fde8b69cf8677510b02936fc523dfb53320847e7321f70366c40d5b24c817`).

This defect is a repository-governance failure and is escalated out of S7.

## 2. TASK 1 — numeral reconciliation

Evidence tier: **D** = direct measurement re-computed by this audit on a restored artifact;
**T** = generated table artifact; **S** = source constant (AST, no execution); **X** = analytic.

### 2.1 Concordant (re-measured, tier D unless noted)

| value | § / line | artifact source | measured | status |
|-------|----------|-----------------|----------|--------|
| Hydra $4.1\times$ / $8.0\times$ | L150 | R6 + R2-A parquets | 4.0501 @ $\Delta e{=}0.140949$; 7.9909 @ $0.326793$ | concordant |
| $K_{\mathrm{HAT}} \approx 102$ | L150, L217, L312 | idem, `np.polyfit` on log means | **101.9903** | concordant |
| $K_{\mathrm{ARF}} \approx 18.5$ | L150, L217, L312 | idem | **18.4774** | concordant |
| $\hat\alpha_{\mathrm{HAT}} \approx 1.02$ | L150, L217, L222 | idem | **−1.0155** | concordant |
| $\hat\alpha_{\mathrm{ARF}} \approx 0.98$ | L150, L217, L222 | idem | **−0.9773** | concordant |
| $K_{\mathrm{HAT}}/K_{\mathrm{ARF}} \approx 5.5$ | L312 | idem | **5.5197** | concordant (was tier E, now **D**) |
| $K_{\mathrm{ARF}}$ reduced by $4$–$8\times$ | L224 | idem | 5.52 | concordant |
| Zombie Alarm in $88\%$ of runs | L190 | `R1_race_condition.parquet`, $\lambda{=}25$ | **0.880** | concordant (was `non_traçable`, now **D**) |
| Detection Rate $>95\%$ at $\lambda{=}25$ | L190 | idem | **0.965** | concordant (was `non_traçable`, now **D**) |
| PHT detects in $<1\%$ of runs ($\lambda{=}50$) | L210, L277 | `R2_instrumented_A_PHT_ARF.parquet` | **0.0025** (5 / 2000) | concordant (was `non_traçable`, now **D**) |
| $\lambda{=}50$: $100\%$ miss | L217 | idem | miss = 1.000 at all 20 magnitudes | concordant |
| $\lambda{=}8$: safe zone $\Delta e > 0.15$ | L210, L217 | `R2_instrumented_C_*.parquet` | miss $\le 0.02$ for $\Delta e \ge 0.19$ | concordant |
| $\lambda{=}50$, F1 $< 0.05$ | L312 | R2-A | detection rate 0.0025 bounds F1 $\le 0.005$ | concordant (by bound) |
| miss $>50\%$ for $\Delta e > 0.35$ (mismatched) | L201 | `R7_clock_mismatch.parquet` | band mean **63.3 %**, pointwise min 51 % | concordant |
| matched clocks win for $\Delta e>0.30$, miss $<5\%$ | L201 | idem | mean **2.4 %**, pointwise max 4 % | concordant |
| residual ${\approx}11\%$ at $\Delta e{\approx}0.19$ | L201 | `exp_R7_regime1_miss_curve.csv` | **0.11** at $\Delta e = 0.1936$ | concordant (was `non_traçable`, now **D**) |
| decoupled: detection before adaptation, $\Delta e>0.30$ | L201 | R7 | miss **3.2 %** | concordant |
| $\mathbb{E}[\tau_{\mathrm{HAT}}] = 463$ | L276 | `results_instrumented_A_ADWIN_HAT.csv` @ $\Delta e_{\mathrm{eff}}{=}0.326793$ | **463.15** | concordant (was tier E, now **D**) |
| $\tau_{\mathrm{det}}^{*} = 155$ | L276 | $50/(0.326793-0.005)$ | **155.3793** | concordant |
| $\widehat F(\tau^{*}_{\mathrm{det}}) = 0.49$ | L276 | empirical CDF of $\tau_{\mathrm{HAT}}$, $n{=}100$ | **0.4900** | concordant |
| $M_{\mathrm{crit}} = 0$ at $r = 0.95$ | L276 | $\lfloor \ln 0.95 / \ln 0.51 \rfloor$ | **0** | concordant (was tier E, now **D**) |
| $q_{0.05}$ constant ${\approx}13$ for $\Delta e \le 0.16$ | L295 | `exp_R8_lambda_op_sweep.csv` | **12.95** at 0.10/0.12/0.14/0.16 | concordant |
| $\lambda_{\mathrm{op}} \approx 4.2$ at the contaminated edge | L295 | idem, $\Delta e = 0.20$ | **4.202** | concordant |
| $12$ transitions, $w \in \{100,500,1000\}$, $n{=}8000$, $\tau^{*}{=}4000$ | L318-319 | `exp_R4_main_table.py:67-72` | S | concordant |
| GARCH $\alpha+\beta \approx 0.95$ / $0.99$ | L320 | `ETF_PARAMS_A/B` | A: 0.94–0.96; B: 0.983–0.995 | concordant |
| $30$ seeds, $360$ runs per cell | L322, L327 | `exp_R4_results_aligned_fusion.csv` | 360 rows per (Detector, Clock, Calibration) | concordant |
| $\tau = \max(1000, w)$ | L324 | `exp_R4_main_table.py:195` | S | concordant |
| $14$ configurations | L327 | `table1_proteus_summary.tex` | 14 rendered rows (**15 computed** — §5) | concordant |
| PHT+ARF $c{=}1$: ADD $=\infty$, F1 $=0.00$ | L332 | R4 raw CSV | F1 0.0000, ADD NaN, all 3 regimes | concordant |
| $c{=}32$: ADD ${\approx}19{\pm}1$, F1 ${\approx}0.56$–$0.68$ | L333 | idem | ADD 19.38 / 19.81 / 19.47 ($\pm0.61$); F1 0.681 / 0.628 / 0.564 | concordant |
| ADWIN+ARF $c{=}1$: ADD $=9$, near-perfect F1 | L336 | idem | ADD 9.09 / 9.10 / 9.04; F1 0.961 / 0.994 / 0.997 | concordant |
| $c{=}32$: ADD $=31$, zero variance over 360 runs | L336, L339 | idem | ADD 31.0000, bootstrap CI 0.0000 | concordant |
| KSWIN ADD $= 14\,[0]$ | L339, L357 | idem | 14.0000, zero variance; $\max(0, 14-15) = 0$ | concordant |
| PHT+HT F1 $\ge 0.75$, ADD ${\approx}23{\pm}3$ | L342, L350 | idem | F1 0.753 / 0.858 / 0.978; ADD 23.16 / 21.61 / 22.54 | concordant |
| ADWIN+HT F1 $\ge 0.80$, ADD $13$–$18$ | L342 | idem | F1 0.803 / 0.894 / 0.992; ADD 17.96 / 14.17 / 12.68 | concordant |
| EDDM+ARF $c{=}1$: F1 $\to 0.00$ | L346 | idem | 0.0000 in all 3 regimes | concordant |
| $0/1080$ vs $932/1080$ (SRP, PHT) | L354, caption | `exp_R4_seed_level_tests.csv` | exact | concordant (was `non_traçable`, now **D**) |
| $0/1080$ vs $882/1080$ (EDDM) | caption | idem | exact | concordant (was `non_traçable`, now **D**) |
| $1080/1080$ vs $0/1080$ (KSWIN) | L357, caption | idem | exact | concordant (was `non_traçable`, now **D**) |
| $913/1080$ vs $0/1080$ (PHT+RF) | L398 | idem | exact, 30/0 seeds | concordant (was `non_traçable`, now **D**) |
| $1063/1080$ vs $959/1080$ (ADWIN) | L398 | idem | exact, 0/30 seeds | concordant (was `non_traçable`, now **D**) |
| $p \approx 2\times10^{-9}$ | L354, L388, L398, caption | idem | **1.862645e-09** | concordant |
| KSWIN $\alpha$-sweep keeps F1 $=1.00$ | L357 | `exp_R4_table_KSWIN_alpha_sweep.tex` | 1.00 for $\alpha \in \{0.001,0.005,0.01,0.05\}$ × 3 regimes | concordant |
| halving pre-drift false alarms (ARF vs HT) | L375 | `R3_regime_crossover_metrics.parquet` | FP 2.00 (HT) → 1.01 (ARF), ratio 1.98 | concordant (was `non_traçable`, now **D**) |
| RF $0\%$ missed at $\Delta e = 0.50$ | L396 | idem | **0.00 %** | concordant (was `non_traçable`, now **D**) |
| BAF $\Delta e \approx 0$ | L388 | `delta_e.parquet` | −0.0009 / −0.0000 / +0.0001 | concordant |
| abrupt $\Delta e \approx 0.07$ | L388 | idem | **0.0743** | concordant |
| per-jump $\{0.68, -0.15, 0.24, -0.27, -0.13\}$ | L388 | idem | **[0.6801, −0.1474, 0.2448, −0.2717, −0.1341]** | concordant (was `non_traçable`, now **D**) |
| gradual $\Delta e \approx 0.45$; reoccurring $\approx 0.39$ | L388 | idem | 0.4503; 0.3914 | concordant |
| $7$ alarms, precision $0.14$, F1 $0.25$ | L388 | `flooding_decomposition.parquet`, `table2_values.csv` | 7.0000, 0.1429, 0.2500 | concordant |
| $86$ alarms, precision $0.012$, F1 $0.02$ | L233, L388, caption | idem | **85.6667 → 86**, 0.0120, 0.0237 → 0.02 | concordant |
| $10.57\times$ and $1.61\times$ | L388 | `table2_values.csv` | 10.5703; 1.6143 | concordant |
| PHT+RF F1 $0.73{\pm}0.05$ → $0.96{\pm}0.02$ | L398 | R4 raw CSV | 0.7306 ± 0.0472 (IID); 0.9611 ± 0.0194 (Cal. B) | concordant |
| RF ADD ${\approx}19$–$20$ (PHT), ${\approx}12$–$14$ (ADWIN) | L400 | idem | 19.40 / 19.76 / 20.18; 13.53 / 12.70 / 11.63 | concordant |
| $200$ seeds/panel, horizon $50{,}000$ | L195 | `exp_R1_generate_data.py:21-23` | S | concordant |
| $100$ seeds × $20$ magnitudes = $2000$ runs | L201, L310 | R2/R6/R7/R9 parquets | 2000 rows each | concordant |
| $\lambda = 25$ is the median of $\{8,25,50\}$ | L362 | `exp_R9_compute_mcrit.py:21` | S | concordant |
| $100$ streams of $8000$ steps, drift $t{=}4000$, tolerance $1000$ | L362, L367 | `exp_R3_regime_crossover.py:35-38` | S | concordant |
| $w_k = \min(5000, \min(\Delta t_{\rm l}, \Delta t_{\rm r})/3)$ | L385 | `exp_R5_config.py:71-72` | S | concordant |
| acceleration $4$–$8\times$ below the $M$-fold rate ($10\times$) | L245, L417 | R6/R2 + theory | 4.05–7.99 measured | concordant |

### 2.2 Divergent — re-measured and NOT reproduced at the stated precision

| # | claim | line | artifact value | assessment |
|---|-------|------|----------------|------------|
| D-1 | *"the external detector achieves **exactly $0\%$** detection rate across 100 seeds for $\Delta e > 0.24$"* | L190 | **1 detection in 1600 runs = 0.0625 %** (`boundary_shift 1.331579`, $\Delta e = 0.326793$, seed 6, $\tau_{\mathrm{arf}}=54$, $\tau_{\mathrm{det}}=649$) | "exactly $0\%$" is false. The run is still a blind spot ($\tau_{\mathrm{ARF}} \ll \tau_{\mathrm{det}}$), so the conclusion holds; the word *exactly* does not. Minimal fix: "${<}0.1\%$". |
| D-2 | *"miss rates rise from $60\%$ to $100\%$ as $\Delta e$ increases"* ($\lambda{=}25$) | L210 | minimum measured miss = **68 %** at $\Delta e = 0.141$, rising monotonically to 100 % for $\Delta e \ge 0.361$ | the $100\%$ endpoint reproduces; the $60\%$ endpoint does not. Nearest artifact value 68 %. |
| D-3 | *"$\lambda_{\mathrm{op}}$ never exceeds $12.4$"* / *"$\lambda_{\mathrm{op}} \le 12.4$"* | L295, L411 | $\max(\lambda_{\rm limit})$ over $[0.20,0.50]$ = **12.438** at $\Delta e = 0.22$ | true at one decimal, false at full precision. `tests/test_R8_lambda_op.py:27` already encodes the looser `<= 12.5`. |
| D-4 | *"RF ${\approx}0.745$ vs ARF ${\approx}0.985$"*, *"${\sim}24$ percentage points"*, *"${\sim}24\%$ penalty"* | L402, L413 | RF **0.7498**, ARF **0.9840**, gap **23.41 pp** | all three digits are off: 0.745→0.750, 0.985→0.984, 24→23.4. Direction and magnitude of the claim are unaffected. |
| D-5 | *"The HT exhibits an artifactual $80\%$ miss rate"* ($\Delta e < 0.09$) | L373 | 77 % / 73 % / 71 % at the three sub-0.09 grid points (max **77 %**) | $80\%$ is not attained anywhere in the band. |
| D-6 | Fig. 3 caption *"Right (Blind Spot, $\Delta e{\ge}0.25$): … ($100\%$ missed)"* | L367 | ARF miss over $\Delta e \ge 0.25$: 1, 2, 8, 17, 32, 68, 98, **100** % | $100\%$ is reached only at the last grid point $\Delta e = 0.50$, not across the band. |
| D-7 | *"at $b = 4.0$, empirical $\Delta e \approx 0.02$"* | L136 | mean empirical $\Delta e$ at $b{=}4.0$ = **−0.0235** (theoretical 0.4977) | magnitude concordant, **sign wrong**: the measured jump is negative. The rhetorical point (measurement blindness) is strengthened, not weakened. |
| D-8 | *"$\lambda = 15$ … calibrated against ProteuS pre-drift volatility to allow at most one false alarm per warm-up window"* | L362 fn | `exp_R4_main_table.py:162` hard-codes `PageHinkley(threshold=15.0)`; R4 arms the detector at $t=0$ and has **no warm-up window**. The described calibration procedure is implemented in **R5** (`calibrate_lambda`, `PHT_TARGET_FA = 1`, `exp_R5_common.py:59-85`), not in R4 | provenance defect; feeds the CRITICAL F17 finding (§5). |
| D-9 | *"theoretical $\Delta e \in [0.02, 0.50]$"* for the instrumented panels | L310 | the R2/R6/R7/R9 grid spans **[0.028186, 0.497661]** | rounded envelope; the exact endpoints are 0.028 and 0.498. Cosmetic, listed for completeness. |

None of D-1 … D-9 changes a sign, a direction, or a conclusion. All are precision or wording
defects in the prose; every table and figure value reproduces exactly.

## 3. TASK 2 — the 93-alarm figure: a no-op, with proof

`grep '93'` over `articleA_blindspot_v63_camera_ready.tex` returns exactly **two** hits, both
legitimate:

* L94 — `\cite{basseville_1993}`, a bibkey.
* L354 — `932/1080`, a run count (re-measured above, exact).

The v63 camera-ready **already carries 86 alarms / precision 0.012**, at L233, at L388 and in the
Table II caption (`docs/manuscript/tables/table2_real_data_summary.tex`). Nothing to correct in the
`.tex`. Cross-check of the whole L388 sentence against `table2_real_data_summary.tex` and the
`flooding_decomposition.parquet` R5 block: `7 / 0.14 / F1 0.25`, `86 / 0.012 / F1 0.02`,
`10.57×`, `1.61×`, `Δe ≈ 0.45 / 0.39 / 0.07 / ≈ 0`, `p ≈ 2·10⁻⁹` — all concordant.

**Sole residue, now closed.** `README.md:227` described the 93-alarm figure as present in "the
submitted manuscript", which is true of the submission but reads as a live divergence. Patched under
the arbitrated perimeter; diff in §7.

**Incidental finding.** `docs/manuscript/tables/table2_real_data_summary.tex` and
`results/R5_real_world_evaluation/tables/table2_real_data_summary.tex` differ
(`sha256 20220a33…` vs `4aa60efa…`, 1723 vs 1743 bytes). The difference is presentational only —
the manuscript copy uses `` `...' `` quotes where the generated copy uses `\emph{...}` — and no
numeral differs. `README.md:221` already documents the two as deliberately parallel copies kept in
sync by hand rather than by `\input`. Recorded, not corrected.

## 4. Phase −1 — targeted re-runs (executed)

Full regeneration was cancelled. Three targeted re-runs were executed on top of the restored
artifacts; `run_all.sh` was **not** executed and R2, R3, R4, R5, R6, R7 were **not** re-run.

### 4.1 R9 under `RELIABILITY_TARGETS = [0.99, 0.95, 0.50]`

`./run_experiment_R9.sh`, 52.9 s wall. Stage 1 (`exp_R9_generate_data.py`) regenerated
`results_instrumented_A_ADWIN_HAT.csv` **bit-for-bit identical**
(`sha256 d8bff453…`) — an unplanned but decisive determinism check on the restored tree. Stage 2
produced the new comparison table: **63 rows** (3 targets × 21 cells) with column `reliability_r`
∈ {0.5, 0.95, 0.99}; the `beta` column is gone, as declared.

The declared mine (§6) is defused: `tests/test_R9_mcrit.py` moves from *skipped with motive* to
**passed**.

### 4.2 R1 with the extended λ grid — G2 closed, claim **measured**

`./run_experiment_R1.sh`, 16 min 19 s wall, 1600 runs.
`LAMBDAS_TO_TEST = [2.5, 5, 10, 15, 20, 25, 50, 100]`.

**Non-regression, verified at row level.** The 1200 rows at the six pre-existing λ values are
**bit-identical** to the pre-rerun artifact (`pandas.DataFrame.equals` → `True` after sorting on
`(lambda_val, seed)`), confirming that `run_diff_test(seed, λ)` re-seeds per call and that extending
the grid perturbs nothing.

| $\lambda$ | Share Blind Spot | Detection Rate | status |
|---|---|---|---|
| 2.5 | 0.035 | 1.000 | pre-existing, identical |
| 5 | 0.035 | 1.000 | pre-existing, identical |
| 10 | 0.035 | 1.000 | pre-existing, identical |
| **15** | **0.170** | **1.000** | **new (G2)** |
| **20** | **0.640** | **1.000** | **new (G2)** |
| 25 | 0.880 | 0.965 | pre-existing, identical |
| 50 | 1.000 | 0.065 | pre-existing, identical |
| 100 | 1.000 | 0.010 | pre-existing, identical |

**Verdict: the manuscript claim `λ* ≈ 15–25` (L195 caption, L419) is confirmed by measurement and
is no longer an interpolation.** The blind-spot share is flat at 0.035 for λ ≤ 10, then climbs
0.17 → 0.64 → 0.88 across λ ∈ {15, 20, 25}, and saturates at 1.00 for λ ≥ 50. The transition band is
exactly [15, 25]; the previously missing interior of the factor-2.5 gap [10, 25] now contains two
measured points and both sit inside the transition. Figure 1 is unaffected — `exp_R1_plot_figure.py`
renders the fixed panel set `λ ∈ {5, 10, 25, 100}`, whose rows are bit-identical.

### 4.3 R8 second sweep at `T_DRIFT = 4000` — G1 measured, conclusion **robust**

`python experiments/R8_lambda_op_sweep/exp_R8_lambda_op_sweep.py 4000`, 7 min 46 s wall, 4200 runs.
Written alongside the published 2000-step output, never replacing it:
`exp_R8_lambda_op_sweep_tdrift4000.csv`, `exp_R8_fine_grid_raw_tdrift4000.csv`.

| $\Delta e$ | $q_{0.05}$ @2000 | $\lambda_{\rm limit}$ @2000 | $q_{0.05}$ @4000 | $\lambda_{\rm limit}$ @4000 |
|---|---|---|---|---|
| 0.10 | 12.95 | 1.230 | 25.70 | 2.442 |
| 0.12 | 12.95 | 1.489 | 30.95 | 3.559 |
| 0.14 | 12.95 | 1.748 | 54.70 | 7.385 |
| 0.16 | 12.95 | 2.007 | 54.70 | 8.479 |
| 0.18 | 17.75 | 3.106 | 41.40 | 7.245 |
| 0.20 | 21.55 | 4.202 | 46.90 | 9.146 |
| 0.22 | 57.85 | 12.438 | 48.80 | 10.492 |
| 0.24 | 48.90 | 11.492 | 40.85 | 9.600 |
| 0.26 | 47.00 | 11.985 | 38.95 | 9.932 |
| 0.28 | 41.95 | 11.536 | 38.00 | 10.450 |
| 0.30 | 38.95 | 11.490 | 33.85 | 9.986 |
| 0.32 | 34.00 | 10.710 | 30.95 | 9.749 |
| 0.34 | 31.95 | 10.703 | 30.00 | 10.050 |
| 0.36 | 30.00 | 10.650 | 28.00 | 9.940 |
| 0.38 | 28.95 | 10.856 | 27.00 | 10.125 |
| 0.40 | 26.95 | 10.645 | 26.00 | 10.270 |
| 0.42 | 25.00 | 10.375 | 25.00 | 10.375 |
| 0.44 | 24.00 | 10.440 | 23.00 | 10.005 |
| 0.46 | 23.00 | 10.465 | 22.00 | 10.010 |
| 0.48 | 22.00 | 10.450 | 21.95 | 10.426 |
| 0.50 | 21.00 | 10.395 | 20.95 | 10.370 |

| quantity | `T_DRIFT = 2000` (published) | `T_DRIFT = 4000` (parity) |
|---|---|---|
| $\max \lambda_{\rm limit}$ over $[0.20, 0.50]$ | **12.438** @ $\Delta e = 0.22$ | **10.492** @ $\Delta e = 0.22$ |
| $\min \lambda_{\rm limit}$ over $[0.20, 0.50]$ | 4.202 @ 0.20 | 9.146 @ 0.20 |
| global $\min$ over $[0.10, 0.50]$ | 1.230 @ 0.10 | 2.442 @ 0.10 |
| $q_{0.05}$ for $\Delta e \le 0.16$ | **12.95, constant** | **25.70 / 30.95 / 54.70 / 54.70 — not constant** |
| $\tau_{\mathrm{ARF}}$ finite | 200/200 at every magnitude | 200/200 at every magnitude |

**Two findings.**

1. **The Fundamental Tension survives the parity correction, and widens.** At a ProteuS-comparable
   warm-up the ceiling drops from $\lambda_{\mathrm{op}} \le 12.4$ to
   $\boldsymbol{\lambda_{\mathrm{op}} \le 10.5}$, so the admissible set
   $\{\lambda \le \lambda_{\mathrm{op}}\} \cap \{\lambda \ge 15\}$ is **still empty**, and the gap
   grows from 2.6 to 4.5. **L411's conclusion is robust to F17**; only its stated numeral is
   warm-up-specific. Recommended prose fix: state the bound with its warm-up
   ("$\lambda_{\mathrm{op}} \le 12.4$ at $T_{\mathrm{drift}} = 2000$, $\le 10.5$ at 4000").
2. **The mechanistic explanation at L295 is warm-up-specific and does not survive.** L295 attributes
   the flat $q_{0.05} \approx 13$ below $\Delta e = 0.16$ to *"noise-driven swaps rather than genuine
   adaptation"*. At `T_DRIFT = 4000` that plateau **disappears**: $q_{0.05}$ rises 25.70 → 30.95 →
   54.70 → 54.70 over the same magnitudes, i.e. the mature forest does not swap on noise the way the
   2000-step forest does. The claim that the envelope *"must be floored above this noise-dominated
   band"* is therefore a property of the short warm-up, not of the ARF. The floor is also
   quantitatively different: $\lambda_{\mathrm{op}}$ at the "contaminated lower edge" $\Delta e = 0.20$
   moves from 4.202 to **9.146**, so the edge is not meaningfully contaminated at parity.

Neither finding changes a conclusion of the manuscript; both change a stated numeral and one stated
mechanism. Both are reported for user arbitration and are **not** corrected in the `.tex` — the
correction would require choosing which warm-up the paper standardises on, which is a Section III-E
authoring decision, not an audit action.

## 5. CRITICAL — R1/R8 warm-up parity (F17, amendment G1)

Recorded in full in `results/audit_S7/config_matrix.md` §5. Summary of the defect, quoting the
manuscript sentence in full:

> **L411.** *"On heteroscedastic streams, guaranteeing reliable detection caps the CUSUM threshold
> ($\lambda_{\mathrm{op}} \le 12.4$), whereas controlling GARCH-induced false alarms requires
> $\lambda \ge 15$. This empty admissible set ($\{\lambda \le 12.4\} \cap \{\lambda \ge 15\}$) forces
> a choice among three architectural fixes:"*

The two members come from experiments with different pre-drift warm-up and, worse, from two
different stream families:

* `λ_op ≤ 12.4` ← **R8**, Bernoulli boundary-shift stream, `T_DRIFT = 2000` (`WARMUP 1000` +
  `DRIFT_GAP 1000`, `exp_R8_lambda_op_sweep.py:34-37`). Measured maximum 12.438 at $\Delta e = 0.22$.
* `λ ≥ 15` ← **not an R1 measurement**. It is the operating threshold `PageHinkley(threshold=15.0)`
  hard-coded at `exp_R4_main_table.py:162`, applied to ProteuS streams of 8000 steps with drift at
  4000 and the detector armed from $t = 0$ (finding D-8: the "one false alarm per warm-up window"
  calibration described at L362 is implemented in **R5**, not R4).

$\tau_{\mathrm{ARF}}$ depends on forest maturity at drift onset, so $q_{0.05}(\tau_{\mathrm{ARF}})$
and $\lambda_{\mathrm{limit}}$ do too. The "empty admissible set" is therefore asserted across two
non-commensurable calibrations. Phase −1 measured the warm-up sensitivity directly (§4.3); the
remaining stream-family mismatch is specified in `regeneration_spec.md` §G1 and is out of S7 scope.

## 6. TASK 3 — the reliability letter: $\beta \rightarrow r$

`\beta` was overloaded in the v63 camera-ready: the reliability target of Corollary 2 (L239, L267,
L269, L276) and the GARCH persistence parameter $\alpha + \beta$ (L320) shared one letter, and L291
uses yet another reliability notion $1-\alpha$. The corollary occurrences are renamed to $r$; the
GARCH and $1-\alpha$ occurrences are untouched.

Applied with one line-anchored edit per occurrence — never `replace_all` — and verified against the
Phase-0 census. Post-edit `\beta` census over `articleA_blindspot_v63_camera_ready.tex`:

```
320:Three GARCH regimes are tested: IID (autocorrelation parameter $\alpha + \beta = 0$), ...
```

Exactly one surviving occurrence, the GARCH one. L267 / L269 / L276 are clear. L291 (`1-\alpha`)
untouched.

Source, test and README were realigned in the same operation (diffs in §10):

* `exp_R9_compute_mcrit.py` — `BETAS = [0.50, 0.05]` → `RELIABILITY_TARGETS = [0.99, 0.95, 0.50]`;
  `mcrit_from_F(F, beta)` → `(F, r)` with the formula `floor(ln r / ln(1-F))` **unchanged**; CSV
  column `beta` → `reliability_r`; print label and figure y-label realigned.
* **Declared consequence.** The target-list change alters the CSV row set to **3 × 21 = 63 rows**
  (from 2 × 21 = 42) and drops the `beta = 0.05` column entirely. Verified after regeneration:
  63 rows, `reliability_r ∈ {0.5, 0.95, 0.99}`.
* `README.md:274` — rewritten around $r \in \{0.99, 0.95, 0.50\}$, $r = 1 - P_{\mathrm{miss}}$;
  `M_crit = 1` (L285) and `M_crit ≤ 3` (L274) removed; the inverted "conservative complement"
  wording corrected — under $\lfloor \ln r / \ln(1-F)\rfloor$ a **larger** $M_{\mathrm{crit}}$ is
  **permissive**, so the low-$r$ column is the permissive end, not a conservative one.
  $P_{\mathrm{miss}}(M{=}10)$ is kept, stated as $r$-independent.
* **`M_crit ≤ 3` is absent from the `.tex`** (grep confirmed over the full file). It was a
  README-only claim, and it does not hold on the artifact either: `Mcrit_emp` reaches `inf` on the
  $r = 0.50$ grid wherever $F_{\mathrm{emp}} = 0$ (e.g. $\Delta e \approx 0.243$, $\lambda = 8$).
  The pre-S7 test survived only by restricting to `lambda in [25, 50]`. Removed from both.

### DECLARED MINE — after Phase 3 the R9 test is false by construction (amendment E)

> Reproduced verbatim from the plan.
>
> After (a) and (b), `tests/test_R9_mcrit.py` targets `reliability_r == 0.95` — **a column and a row
> present in no existing CSV.** Every pre-Phase-3 artifact carries the column `beta` with values
> `{0.50, 0.05}` only, and 0.95 is in neither. The test is therefore **false by construction, not
> merely blocked by a missing artifact**: even a fully restored pre-Phase-3 CSV (branch H2) would
> fail it.
>
> It becomes valid only after R9 is regenerated under `RELIABILITY_TARGETS = [0.99, 0.95, 0.50]`.
> Guard it with this exact motive — never a silent pass, never a bare `xfail`:
>
> ```python
> pytest.skip("R9 artifact predates RELIABILITY_TARGETS=[0.99,0.95,0.50]; "
>             "test is false by construction until R9 is regenerated")
> ```

**Status: armed, then defused.** The guard was implemented with exactly that motive, conditioned on
the artifact rather than unconditional, so it can never silently pass:

```python
if "reliability_r" not in df.columns or not np.isclose(df["reliability_r"], 0.95).any():
    pytest.skip("R9 artifact predates RELIABILITY_TARGETS=[0.99,0.95,0.50]; "
                "test is false by construction until R9 is regenerated")
```

Against the pre-regeneration CSV the test **skipped** with that motive. After the Phase −1 R9
re-run it **passes**: at $\Delta e = 0.33$, $\lambda = 50$, $r = 0.95$ the artifact gives
`E_tau_HAT = 463.15`, `tau_det_star = 155.38`, `F_emp = 0.49`, `Mcrit_emp = 0`, `Pmiss_M10 = 0.9988`
— the `.tex` L276 example, exactly.

## 7. Phase 6 (F23) — the Hydra factor under administrative censoring

`exp_R6_compute_hydra.py` computes a **complete-case** ratio: runs whose internal swap never occurs
inside the post-drift window contribute NaN and are dropped. That drop is informative — it removes
precisely the slowest adaptations — so the published factor is biased **downwards**.

New script `experiments/R6_hydra_factor/exp_R6_hydra_survival.py` treats the NaNs as what they are:
administrative censoring at the common horizon $t_c = N\_STEPS - T\_DRIFT = 4000$ post-drift steps,
identical for both arms, no loss to follow-up. `observed = notna(tau)`, `time = min(tau, 4000)`.

**Validity check (step 2), passed.** Under a single administrative censoring time the Kaplan-Meier
RMST must equal the plain restricted mean. Measured over all 40 (arm, $\Delta e$) cells:

```
max |RMST(4000) - mean(min(tau, 4000))| = 9.095e-13     (tolerance 1e-9)
```

Structurally this difference is zero; the residual is the float accumulation of the KM product
(≈1e-13 on a magnitude of ~2000, i.e. machine precision). A censoring pattern that was **not**
purely administrative would produce an O(1) discrepancy, not 1e-13. The script raises and halts on
any deviation above the tolerance.

**Step 5 verdict.** The ARF arm is **censoring-free at every magnitude** (max censored fraction
0.0000); the HAT arm is censored at 0–13 %, concentrated at low $\Delta e$. Only the numerator is
truncated, so the RMST ratio is a **LOWER BOUND** on the true acceleration factor, not a point
estimate. The script emits that verdict and states it in the generated LaTeX caption.

**Result at the two magnitudes the manuscript anchors (L150):**

| $\Delta e$ (grid) | label | censored HAT | complete-case (published) | RMST ratio | 95 % CI (10 000 paired draws) | KM median ratio |
|---|---|---|---|---|---|---|
| 0.140949 | "0.14" | 1 % | **4.05×** | **4.12×** | [3.45, 4.96] | 5.32× |
| 0.326793 | "0.33" | 0 % | **7.99×** | **7.99×** | [6.40, 9.72] | 3.10× |

Over the full 20-point grid the RMST ratio spans **4.12× … 8.04×** (complete-case: 4.05× … 7.99×).
Bootstrap: 10 000 percentile draws, **paired on the seed index** — both arms share `range(1, 101)`
and the same two-draws-per-step covariate stream, so seeds are resampled, never observations.

**PIVOT CRITERION — not triggered.** The corrected factor at the two magnitudes the manuscript
states is 4.12× and 7.99×, both inside $[4.0\times, 8.0\times]$. Section III-C does not require a
rewrite. Two qualifications the user should see:

1. The grid **maximum** is 8.0397× at $\Delta e = 0.0282$, marginally (0.5 %) above 8.0×. That point
   lies in the noise-swap band the manuscript itself excludes from the claim
   (Remark `rem:bgswap`, $\Delta e < 0.10$), and the manuscript's range is anchored at 0.14 and 0.33,
   not at the grid extremes. Reported, not treated as a pivot.
2. The **KM median ratio** diverges sharply from the mean ratio at high magnitude (3.10× at
   $\Delta e = 0.33$ against 7.99× for RMST): $\tau_{\mathrm{HAT}}$ is strongly right-skewed, so the
   published factor is a statement about means, not about typical runs. Both are now tabulated.

Outputs: `results/audit_S7/hydra_survival.csv` (20 rows × 17 columns) and
`results/audit_S7/hydra_survival.tex` (old vs new factor side by side per $\Delta e$).

### `exp_R6_compute_hydra.py` corrections

`at(de)` selected the endpoint magnitudes with a bare `idxmin` and no tolerance: it would silently
accept any nearest point, including one from a different grid. Corrected with an explicit anchor
resolution plus a 1e-6 assertion, and a join guard.

**Interpretation recorded (the instruction is not applicable verbatim).** The plan specifies
*"Raise `AssertionError` if `abs(Delta_e_found - target) > 1e-6`"*. Applied literally to the existing
targets it fails immediately and breaks the R6 pipeline: 0.14 and 0.33 are **rounded labels**, not
grid points — the swept grid is `norm.cdf(linspace(0.1, 4.0, 20)/sqrt(2)) - 0.5`, whose points 2 and
6 are 0.140949 and 0.326793 (gaps 9.5e-4 and 3.2e-3, both ≫ 1e-6). The correction therefore resolves
each manuscript label to its grid point first and then asserts the 1e-6 tolerance, so the guard bites
exactly when it should (the R6/R2 magnitude grid changing) without breaking a working pipeline.
The label-vs-grid gap is itself recorded here as a finding.

Verified non-regression: the corrected script regenerates
`results/R6_hydra_factor/tables/exp_R6_hydra_empirical_validation.tex` **bit-for-bit identical**
(`sha256 4d9fde8b…`), printing `4.1x at Delta_e=0.14 -> 8.0x at Delta_e=0.33`,
`K_HAT=102.0 a=-1.02`, `K_ARF=18.5 a=-0.98`.

## 8. Phase 4 — SSOT freeze and the consistency suite

`config/experiment_ssot.py` generalises the form of `exp_R5_config.py`: dynamic `ROOT_DIR`, named
module-level constants, no experiment logic. Every registry name of CONFIG §6 is declared, and every
intentional per-experiment divergence is a **derived constant** with an `R<n>_` prefix and a motive,
never a local literal — e.g.

```python
R1_CENSORING_HORIZON = 50_000                  # starvation bounds, cf. Fig. 1
R1_N_STEPS = R1_T_DRIFT + R1_CENSORING_HORIZON # 54000
R8_PREQUENTIAL_PREDICT = False                 # tau_ARF only; predict_one intentionally omitted
R2_CUSUM_DELTA = 0.01                          # NOT DELTA_P: R2's StrictCUSUM tolerance is 0.01
```

**Value-preserving by construction.** No RNG call site, no draw ordering and no
`predict_one`/`learn_one` ordering was touched; the two-`rng.normal()`-per-step invariant lives in
the experiment loops and is what makes the artifacts bit-comparable. The triple per-worker lock
(`random.seed` + `np.random.seed` + `default_rng`) is preserved verbatim in every worker function —
this overrides the global `CLAUDE.md` ban on `np.random.seed()`, which does not apply to this
repository's Cython-path requirement.

The River private-attribute guard, previously a single inline `hasattr(model, '_drift_tracker')`
check in `exp_R8_lambda_op_sweep.py:60-63`, is generalised to **one shared helper**
`ssot.require_drift_tracker(model, warning=False)` and applied at the five other instrumentation
sites (R1, R2, R6, R7, R9 — R9 with `warning=True`, since it also reads `_warning_tracker`). Five
copies were not created. The helper returns the model unchanged and consumes no RNG.

Scope note: R4's registry values live in function defaults (`simulate_stream(n_steps=8000, tp=4000)`,
`forest.ARFClassifier(n_models=10, …)`, `PageHinkley(threshold=15.0)`) rather than at module level.
They are **declared** in the SSOT as the audited reference (`R4_N_STEPS`, `R4_T_DRIFT`,
`R4_N_MODELS`, `R4_PHT_LAMBDA`, `R4_ADWIN_DELTA`, `R4_KSWIN_ALPHA`, `R4_TAU_TOL_FLOOR`) and R4's two
module-level registry names (`N_SEEDS`, `SEEDS`) are routed through it. Rewriting call-site defaults
was judged a larger risk than the guard it would buy, and is not required by the AST drift guard,
which walks module-level assignments.

### `tests/test_S7_consistency.py`

1. **SSOT drift guard** (unconditional, source-only). AST-walks every module-level `Assign` in
   `experiments/**/*.py` without importing or executing the experiment, and fails if a registry
   constant is re-bound to a local literal, or if any resolved value drifts from the Phase-0 oracle
   `results/audit_S7/_baseline/constants_pre.json` (200 assignments across 21 modules, 124 of which
   resolve to a value; the rest are `Path` objects and runtime frames). Exactly two value changes are
   whitelisted, each with its S7 motive: `LAMBDAS_TO_TEST` (G2) and `BETAS` → `RELIABILITY_TARGETS`
   (TASK 3). This is the non-regression proof that the refactor changed no value, obtained without
   running an experiment.
2. `tau_HAT` identical between R6 and R9 per `(boundary_shift, seed)` — same $M = 1$, same seeds,
   same stream, two independent instrumentation scripts. **2000/2000 rows, zero mismatches.**
3. `tau_arf` identical across the R2 scenarios A/B/C per `(boundary_shift, seed)` — $\lambda$ does
   not feed back into the ARF. **2000/2000 rows each, zero mismatches.**
4. The R6 ↔ R2 `Δe` join retains its 20 points. **20/20.**

Assertions 2–4 skip with an explicit motive when the artifact is absent, never silently pass.

**FAIR defect found and fixed while writing assertion 2.** `results_instrumented_A_ADWIN_HAT.csv` is
a CSV; read with pandas' default float parser it loses 1 ULP on **4 of the 20** `boundary_shift`
values, so the join against R6's parquet silently drops 400 of 2000 rows:

```
parquet 0.30526315789473685  vs csv 0.3052631578947368    diff  5.551e-17
parquet 0.9210526315789473   vs csv 0.9210526315789472    diff  1.110e-16
parquet 1.9473684210526316   vs csv 1.947368421052632     diff -4.441e-16
parquet 2.3578947368421055   vs csv 2.357894736842105     diff  4.441e-16
```

With `float_precision='round_trip'` (mandated by `CLAUDE.md` §3) the join is exact at 2000 rows. The
test pins that reader option and the assertion `len(m) == len(r6) == len(r9)` makes a silent
re-introduction impossible.

## 9. Phase 5 — final audit gate (all items executed)

| # | check | result |
|---|-------|--------|
| 1 | `python -m py_compile` on every touched `.py` (16 files, incl. `exp_R6_hydra_survival.py` and `exp_R6_compute_hydra.py`) | **all OK** |
| 2 | AST registry diff `constants_pre.json` vs post-refactor resolved values | **124 resolved constants compared, 2 differ, both authorised** (`LAMBDAS_TO_TEST` / G2, `BETAS` removed / TASK 3). Registry names still bound to local literals: **NONE** |
| 3 | `PYTHONHASHSEED=0 pytest tests/test_S7_consistency.py -v` | **4 passed.** Assertion 1 (source-only gate) passes; assertions 2–4 do not skip — the artifacts are present, so they ran and passed on real data |
| 4 | `PYTHONHASHSEED=0 pytest tests/ -v` | **8 passed** (R6, R7, R8, R9 + the four S7 assertions). No error, no skip. The pre-existing four match `logs/pytest/pytest_20260615_012716.log`'s "4 passed" |
| 4bis | bit-for-bit parquet/CSV identity of R6 and R9 after the SSOT refactor, against `artifacts_sha256_pre_ssot.txt` | **`R6_hat_instrumented.parquet: OK`, `results_instrumented_A_ADWIN_HAT.csv: OK`, `exp_R9_mcrit_comparison.csv: OK`.** Full freeze re-verified: **all 34 artifacts unchanged.** This is the empirical proof of the CONFIG §3 two-draws-per-step invariant and supersedes item 2 as the strongest available evidence |
| 5 | `sha256sum docs/manuscript/tables/*.tex` vs `sha256_pre.txt` | **unchanged** — `table1_proteus_summary.tex` OK, `table2_real_data_summary.tex` OK. Every generated `results/**/*.tex` also OK. The two FAILED lines are the two files S7 deliberately edits (`…v63_camera_ready.tex`, `README.md`); no generated numeric artifact was touched |
| 6 | `\beta` census | **exactly one surviving occurrence**, L320 (`$\alpha + \beta$`, GARCH). L267 / L269 / L276 beta-free. L291 (`1-\alpha`) preserved verbatim |
| 7 | LaTeX compile | **no TeX toolchain on this host** (`pdflatex`, `latexmk`, `xelatex`, `lualatex`, `tectonic` all absent). Structural check performed instead and passed: braces 872/872 balanced; `\begin`/`\end` 27/27 balanced with matching environment names; unescaped `$` count even (858); each of the five edited lines independently brace-balanced with an even `$` count |
| 8 | every `.tex`/`.md`/`.py` patch reproduced as a unified diff | §10 below |
| 9 | `git status --short` at close | `README.md` and `run_all.sh` both show modifications |

Residual risk, stated plainly:

* Item 7 is a structural check, not a compile. A TeX toolchain would be required to prove the
  document still typesets. The five edits are single-token substitutions inside existing math mode
  plus two short prose clauses, so the risk is low, but it is not zero and it is not verified.
* R2, R3, R4, R5 and R7 were not re-run. Their bit-reproducibility after the SSOT refactor rests on
  the static AST oracle (item 2), not on execution. The refactor is value-preserving by construction
  and R6/R9 prove it empirically on two of the seven touched scripts.
* The three residues of §0 (R-1, R-2, R-3) are not discharged and require new runs or new records.

## 10. Unified diffs — every applied patch

### `docs/manuscript/articleA_blindspot_v63_camera_ready.tex`

```diff
diff --git a/docs/manuscript/articleA_blindspot_v63_camera_ready.tex b/docs/manuscript/articleA_blindspot_v63_camera_ready.tex
index a5b691d..3cb60fd 100644
--- a/docs/manuscript/articleA_blindspot_v63_camera_ready.tex
+++ b/docs/manuscript/articleA_blindspot_v63_camera_ready.tex
@@ -236,7 +236,7 @@ A high threshold ($\lambda = 50$) produces \emph{complete} starvation: the PHT d
 \subsection{Theoretical Bounds: The Starvation Boundary}\label{sec:starvation_boundary}
 
 The Hydra Effect (Section~\ref{sec:hydra}) and the Starvation Effect (Section~\ref{sec:starvation}) combine to define a \emph{structural} boundary---in expectation---on the viability of external monitoring.
-We derive an upper bound on the probability of missed detection and a critical ensemble size $M_{\mathrm{crit}}$ beyond which external detection fails with probability exceeding $1 - \beta$.
+We derive an upper bound on the probability of missed detection and a critical ensemble size $M_{\mathrm{crit}}$ beyond which external detection fails with probability exceeding $1 - r$, where $r$ denotes the reliability target.
 
 \paragraph{Correlation disclaimer.}
 The $M$ trees in the ARF are trained on the \emph{same} data stream via Poisson-weighted bootstrap (Oza bagging with $\lambda = 6$~\cite{gomes_arf_2017}).
@@ -264,16 +264,16 @@ Under conditional independence, $\tau_{\mathrm{ARF}} = \min_i \tau_i$ is stochas
 \end{proof}
 
 \begin{corollary}[Critical Ensemble Size]\label{cor:mcrit}
-  For a target detection guarantee $P_{\mathrm{miss}} \le 1 - \beta$, the ensemble size must not exceed:
+  For a reliability target $r$, i.e.\ a detection guarantee $P_{\mathrm{miss}} \le 1 - r$, the ensemble size must not exceed:
   \begin{equation}\label{eq:mcrit}
-    M_{\mathrm{crit}} = \left\lfloor \frac{\ln \beta}{\ln\!\bigl[1 - F(\tau_{\mathrm{det}}^*)\bigr]} \right\rfloor\,.
+    M_{\mathrm{crit}} = \left\lfloor \frac{\ln r}{\ln\!\bigl[1 - F(\tau_{\mathrm{det}}^*)\bigr]} \right\rfloor\,.
   \end{equation}
-  For $M > M_{\mathrm{crit}}$ this (conservative) certificate no longer holds, and reliability must be settled empirically rather than inferred from the bound.
+  For $M > M_{\mathrm{crit}}$ this (conservative) certificate no longer holds, and the reliability $r$ must be settled empirically rather than inferred from the bound.
 \end{corollary}
 
 \paragraph{Numerical example (distribution-free).}
 Corollary~\ref{cor:mcrit} requires the scalar $F(\tau_{\mathrm{det}}^*)$. A Kolmogorov--Smirnov test ($N{=}2000$ bootstrap) rejects an exponential fit of the single-tree delays $\tau_{\mathrm{HAT}}$ at every tested magnitude ($p<0.05$), so we evaluate $M_{\mathrm{crit}}$ directly from the empirical CDF $\widehat{F}$ of $\tau_{\mathrm{HAT}}$.
-At $\Delta e = 0.33$ ($\lambda=50$), instrumentation yields $\mathbb{E}[\tau_{\mathrm{HAT}}] = 463$, $\tau_{\mathrm{det}}^* = 155$, and $\widehat{F}(\tau_{\mathrm{det}}^*) = 0.49$, so the (conservative) independence bound~\eqref{eq:mcrit} yields $M_{\mathrm{crit}} = 0$ at the reliability target $\beta = 0.95$---it cannot certify reliable detection even for a single tree, a verdict that persists across the operative grid ($\Delta e \ge 0.24$).
+At $\Delta e = 0.33$ ($\lambda=50$), instrumentation yields $\mathbb{E}[\tau_{\mathrm{HAT}}] = 463$, $\tau_{\mathrm{det}}^* = 155$, and $\widehat{F}(\tau_{\mathrm{det}}^*) = 0.49$, so the (conservative) independence bound~\eqref{eq:mcrit} yields $M_{\mathrm{crit}} = 0$ at the reliability target $r = 0.95$---it cannot certify reliable detection even for a single tree, a verdict that persists across the operative grid ($\Delta e \ge 0.24$).
 River's default ($M=10$) therefore starves the external CUSUM, as confirmed directly by the measured ${<}1\%$ detection rate in Figure~\ref{fig:pht_scenarios}(A).
 
 \subsection{The Decoupling Principle}\label{sec:decoupling}
```

### `README.md`

```diff
diff --git a/README.md b/README.md
index 2806158..d80da90 100644
--- a/README.md
+++ b/README.md
@@ -224,7 +224,7 @@ The orchestrator pins `PYTHONHASHSEED=0`, and every cell pins its `random`/`nump
 - **Manuscript mapping:** Table II (`tab:real_data_summary`) and the flooding analysis of Section IV-C (genuine detection vs false-alarm flooding) are derived directly from these artifacts.
 
 > 💡 **Reviewer Transparency Note regarding Table II (Flooding Alarm Count):**
-> The Section IV-C flooding discussion in the submitted manuscript quotes **93 alarms** (precision $0.011$) for the `PHT+ARF(c=1)` pipeline on the `gradual_balanced` stream, whereas this artifact and the finalized Table II report the reproducible value of **86 alarms** (precision $0.012$). The discrepancy is a stale in-line figure in the manuscript text: the Table II body and all conclusions were finalized against this pipeline's deterministic output, but the alarm count quoted in the prose was not updated in lockstep. The repository value (**86 alarms**, reproduced bit-for-bit on every run) is authoritative. The scientific conclusion — massive false-alarm flooding by `PHT+ARF(c=1)` against only **7 alarms** for the `PHT+HT` baseline — is entirely unchanged.
+> The Section IV-C flooding discussion in the **submitted** manuscript quoted **93 alarms** (precision $0.011$) for the `PHT+ARF(c=1)` pipeline on the `gradual_balanced` stream, whereas this artifact and the finalized Table II report the reproducible value of **86 alarms** (precision $0.012$). **This divergence is closed: the v63 camera-ready `.tex` already carries 86 alarms / precision $0.012$ at L233, at L388 and in the Table II caption; no stale 93 remains in the manuscript.** The note is retained as a historical record of the submitted version. The repository value (**86 alarms**, reproduced bit-for-bit on every run) is authoritative. The scientific conclusion — massive false-alarm flooding by `PHT+ARF(c=1)` against only **7 alarms** for the `PHT+HT` baseline — is entirely unchanged.
 
 ### Experiment R6: The Hydra Effect (Ensemble Acceleration)
 This experiment isolates the adaptation delay of a single Hoeffding Adaptive Tree ($M=1$) against the full Adaptive Random Forest ($M=10$). It computes the empirical Hydra acceleration factor ($4.1\times$--$8.0\times$) and verifies the structural power-law constants ($K_{\mathrm{HAT}} \approx 102$) discussed in **Section III-C (The Hydra Effect: Ensemble Acceleration)**.
@@ -271,7 +271,7 @@ chmod +x run_experiment_R8.sh
 > **Reproducibility:** `tests/test_R8_lambda_op.py` re-derives the artifact and asserts the three numerical claims of Definition 11.
 
 ### Experiment R9: The Critical Ensemble Size ($M_{\mathrm{crit}}$)
-Records, per drift magnitude and seed, the internal adaptation delay $\tau_{\mathrm{HAT}}$ of a single Hoeffding Adaptive Tree. The empirical CDF of $\tau_{\mathrm{HAT}}$ is consumed to derive the distribution-free critical ensemble size $M_{\mathrm{crit}}$. The comparison table reports $M_{\mathrm{crit}}$ at $\beta \in \{0.50, 0.05\}$; the manuscript's worked example and the "$M_{\mathrm{crit}} \le 3$" claim use $\beta = 0.50$ (the $\beta = 0.05$ column is a conservative complement and is expectedly larger). The operational quantity $P_{\mathrm{miss}}(M{=}10)$ is $\beta$-independent.
+Records, per drift magnitude and seed, the internal adaptation delay $\tau_{\mathrm{HAT}}$ of a single Hoeffding Adaptive Tree. The empirical CDF of $\tau_{\mathrm{HAT}}$ is consumed to derive the distribution-free critical ensemble size $M_{\mathrm{crit}}$. The comparison table reports $M_{\mathrm{crit}}$ at the reliability targets $r \in \{0.99, 0.95, 0.50\}$, where $r = 1 - P_{\mathrm{miss}}$ is the target detection guarantee of Corollary 2 ($M_{\mathrm{crit}} = \lfloor \ln r / \ln(1 - F) \rfloor$). Under this formula a **larger** $M_{\mathrm{crit}}$ is **permissive** (it certifies a larger ensemble), so the low-$r$ column is the permissive end, not a conservative one. The manuscript's worked example is stated at $r = 0.95$. The operational quantity $P_{\mathrm{miss}}(M{=}10)$ is $r$-independent.
 
 ```bash
 chmod +x run_experiment_R9.sh
@@ -282,7 +282,7 @@ chmod +x run_experiment_R9.sh
 - **Data:** `results/R9_mcrit/data/exp_R9_mcrit_comparison.csv`
 - **Figure:** `results/R9_mcrit/figures/Fig_R9_Mcrit_empirical_vs_exp.png`
 
-> **Reproducibility:** `tests/test_R9_mcrit.py` asserts that the regenerated artifact reproduces the exact numerical example of the manuscript Corollary ($M_{\mathrm{crit}}=1$).
+> **Reproducibility:** `tests/test_R9_mcrit.py` asserts that the regenerated artifact reproduces the numerical example of the manuscript Corollary at the reliability target $r = 0.95$.
 
 ## 5. Artifact Scope & Configuration Notes
 
```

### `run_all.sh`

```diff
diff --git a/run_all.sh b/run_all.sh
index 8166c3c..21f516e 100755
--- a/run_all.sh
+++ b/run_all.sh
@@ -13,9 +13,14 @@ echo "======================================================================"
 echo " ICDM 2026 Artifact Evaluation: FULL REPRODUCTION PIPELINE"
 echo "======================================================================"
 
-# S1: Execute all experiments sequentially
-for i in {1..9}; do
-    script="./run_experiment_R${i}.sh"
+# S1: Execute all experiments in dependency order.
+# R6 (Hydra factor) joins its own tau_HAT against the tau_ARF produced by R2, so R2 MUST complete
+# before R6. The order below encodes that dependency explicitly instead of leaning on the numeric
+# order of a {1..9} loop, which expressed the constraint only by accident.
+EXPERIMENTS=(R1 R2 R3 R4 R5 R6 R7 R8 R9)   # R6 depends on R2
+
+for exp in "${EXPERIMENTS[@]}"; do
+    script="./run_experiment_${exp}.sh"
     echo -e "\n>>> Executing ${script}..."
     $script
 done
```

### `config/experiment_ssot.py` — NEW FILE (188 lines)

Created by stream S7; no diff (the file is its own content). Purpose:
single source of truth for the experimental constants (CONFIG §6 registry + the shared River guard).

### `tests/test_S7_consistency.py` — NEW FILE (173 lines)

Created by stream S7; no diff (the file is its own content). Purpose:
S7 consistency suite: SSOT drift guard + three cross-experiment invariants.

### `tests/test_R9_mcrit.py`

```diff
diff --git a/tests/test_R9_mcrit.py b/tests/test_R9_mcrit.py
index d6dff69..a79488f 100644
--- a/tests/test_R9_mcrit.py
+++ b/tests/test_R9_mcrit.py
@@ -1,11 +1,13 @@
 # tests/test_R9_mcrit.py
 """
 Non-regression test for Experiment R9 (worked M_crit example, distribution-free).
-Asserts that the regenerated artifact reproduces the numerical example of the manuscript Corollary.
+Asserts that the regenerated artifact reproduces the numerical example of the manuscript Corollary
+at the reliability target r = 0.95 (r = 1 - P_miss; the manuscript's eq:mcrit uses ln r).
 Run after run_experiment_R9.sh.   Usage:  python -m pytest tests/test_R9_mcrit.py
 """
 import numpy as np
 import pandas as pd
+import pytest
 from pathlib import Path
 from pytest import approx
 
@@ -14,16 +16,13 @@ CSV = ROOT_DIR / "results" / "R9_mcrit" / "data" / "exp_R9_mcrit_comparison.csv"
 
 def test_mcrit_numerical_example():
     df = pd.read_csv(CSV)
-    # The worked example and the "M_crit <= 3" claim are stated at beta = 0.50. The CSV also
-    # tabulates a conservative beta = 0.05 (necessarily larger M_crit), which is NOT the claim.
-    b50 = np.isclose(df["beta"], 0.50)
-    row = df[b50 & np.isclose(df["delta_e"], 0.33) & (df["lambda"] == 50)].iloc[0]
+    if "reliability_r" not in df.columns or not np.isclose(df["reliability_r"], 0.95).any():
+        pytest.skip("R9 artifact predates RELIABILITY_TARGETS=[0.99,0.95,0.50]; "
+                    "test is false by construction until R9 is regenerated")
+    r95 = np.isclose(df["reliability_r"], 0.95)
+    row = df[r95 & np.isclose(df["delta_e"], 0.33) & (df["lambda"] == 50)].iloc[0]
     assert row["E_tau_HAT"]      == approx(463, rel=0.05), row["E_tau_HAT"]
     assert row["tau_det_star"]   == approx(155, rel=0.05), row["tau_det_star"]
     assert row["F_emp"]          == approx(0.49, abs=0.03), row["F_emp"]
-    assert int(row["Mcrit_emp"]) == 1, row["Mcrit_emp"]
+    assert int(row["Mcrit_emp"]) == 0, row["Mcrit_emp"]
     assert row["Pmiss_M10"]      == approx(0.999, abs=0.003), row["Pmiss_M10"]
-    # Operative blind-spot magnitudes (Delta_e in {0.24,0.33,0.39,0.50}), lambda in {25,50}, beta=0.50:
-    # the empirical critical size never exceeds 3 (<< River's default M=10).
-    grid = df[b50 & (df["delta_e"] >= 0.24) & (df["lambda"].isin([25, 50]))]
-    assert grid["Mcrit_emp"].max() <= 3, grid["Mcrit_emp"].max()
\ No newline at end of file
```

### `experiments/R1_race_condition/exp_R1_generate_data.py`

```diff
diff --git a/experiments/R1_race_condition/exp_R1_generate_data.py b/experiments/R1_race_condition/exp_R1_generate_data.py
index 7473750..ef3096c 100644
--- a/experiments/R1_race_condition/exp_R1_generate_data.py
+++ b/experiments/R1_race_condition/exp_R1_generate_data.py
@@ -4,6 +4,7 @@ Extended Diagnostic 3: Isolate the evolution of P(tau_arf < tau_det) over a lamb
 with truncation bias correction for the Share Blind Spot computation.
 """
 import random
+import sys
 import numpy as np
 import pandas as pd
 from joblib import Parallel, delayed
@@ -15,15 +16,18 @@ from river import forest, drift
 # [IEEE/ICDM FAIR Compliance] Dynamic path resolution based on script location
 # The script is in experiments/R1_race_condition/. We target the root centralized results folder.
 ROOT_DIR = Path(__file__).resolve().parent.parent.parent
+sys.path.insert(0, str(ROOT_DIR))
+from config import experiment_ssot as ssot
+
 RESULTS_DIR = ROOT_DIR / "results" / "R1_race_condition" / "data"
 RESULTS_DIR.mkdir(parents=True, exist_ok=True)
 
-N_STEPS = 54000  # Warmup 4000 + Tolerance 50000 (harmonized)
-T_DRIFT = 4000
-N_SEEDS = 200
-DELTA_E = 0.25
-LAMBDAS_TO_TEST = [2.5, 5.0, 10.0, 25.0, 50.0, 100.0]
-DELTA_P = 0.005
+N_STEPS = ssot.R1_N_STEPS      # Warmup 4000 + Tolerance 50000 (harmonized)
+T_DRIFT = ssot.R1_T_DRIFT
+N_SEEDS = ssot.R1_N_SEEDS
+DELTA_E = ssot.R1_DELTA_E
+LAMBDAS_TO_TEST = ssot.R1_LAMBDAS
+DELTA_P = ssot.R1_DELTA_P
 
 class StrictCUSUM:
     def __init__(self, p_pre, delta, threshold):
@@ -47,7 +51,8 @@ def run_diff_test(seed, lambda_val):
     
     b_shift = np.sqrt(2) * norm.ppf(0.5 + DELTA_E)
     
-    arf = forest.ARFClassifier(n_models=10, seed=seed, drift_detector=drift.ADWIN(clock=1), warning_detector=drift.ADWIN(clock=1))
+    arf = ssot.require_drift_tracker(
+        forest.ARFClassifier(n_models=10, seed=seed, drift_detector=drift.ADWIN(clock=ssot.R1_C_INT), warning_detector=drift.ADWIN(clock=ssot.R1_C_INT)))
     cusum_external_fixed = StrictCUSUM(0.05, DELTA_P, lambda_val)
     
     errors_warmup = []
@@ -118,7 +123,7 @@ def run_diff_test(seed, lambda_val):
 
 if __name__ == "__main__":
     print("[INFO] Launching Extended Diagnostic 3 (Share Blind Spot Cartography)...")
-    seq = np.random.SeedSequence(42)
+    seq = np.random.SeedSequence(ssot.SEED_SCHEME_SEEDSEQ_ENTROPY)
     seeds = [int(s.generate_state(1)[0]) for s in seq.spawn(N_SEEDS)]
     
     grid = [(s, l) for s in seeds for l in LAMBDAS_TO_TEST]
```

### `experiments/R2_instrumented_blind_spot/exp_R2_instrumented_blind_spot.py`

```diff
diff --git a/experiments/R2_instrumented_blind_spot/exp_R2_instrumented_blind_spot.py b/experiments/R2_instrumented_blind_spot/exp_R2_instrumented_blind_spot.py
index c4e059e..3edec09 100644
--- a/experiments/R2_instrumented_blind_spot/exp_R2_instrumented_blind_spot.py
+++ b/experiments/R2_instrumented_blind_spot/exp_R2_instrumented_blind_spot.py
@@ -24,6 +24,9 @@ warnings.filterwarnings('ignore')
 
 # Dynamic Path Resolution (IEEE/ICDM FAIR Compliance)
 ROOT_DIR = Path(__file__).resolve().parent.parent.parent
+sys.path.insert(0, str(ROOT_DIR))
+from config import experiment_ssot as ssot
+
 RESULTS_DIR = ROOT_DIR / "results" / "R2_instrumented_blind_spot"
 DATA_DIR = RESULTS_DIR / "data"
 FIGURES_DIR = RESULTS_DIR / "figures"
@@ -31,12 +34,12 @@ FIGURES_DIR = RESULTS_DIR / "figures"
 DATA_DIR.mkdir(parents=True, exist_ok=True)
 FIGURES_DIR.mkdir(parents=True, exist_ok=True)
 
-N_STEPS, T_DRIFT, N_MODELS = 8000, 4000, 10
-BOUNDARY_SHIFTS = np.linspace(0.1, 4.0, 20)
+N_STEPS, T_DRIFT, N_MODELS = ssot.R2_N_STEPS, ssot.R2_T_DRIFT, ssot.R2_N_MODELS
+BOUNDARY_SHIFTS = ssot.R2_BOUNDARY_SHIFTS
 
 # IEEE/ICDM FAIR Determinism: Controlled Rollback to original seed space
 # Restoring the naive sequence to match the submitted PDF's exact fitted coefficients (e.g., 18.5)
-SEEDS = list(range(1, 101))
+SEEDS = ssot.R2_SEEDS
 
 BLUE, ORANGE, RED, GREEN, GRAY = '#04617b', '#E8A000', '#C62828', '#2E7D32', '#546E7A'
 plt.rcParams.update({'figure.dpi': 300, 'font.family': 'sans-serif', 'font.size': 11,
@@ -64,7 +67,8 @@ def run_instrumented_arf_pht(boundary_shift, seed, cfg):
     np.random.seed(safe_seed)
     rng = np.random.default_rng(safe_seed)
     
-    arf = ARFClassifier(n_models=N_MODELS, seed=safe_seed, drift_detector=drift.ADWIN(clock=cfg['c_int']), warning_detector=drift.ADWIN(clock=cfg['c_int']))
+    arf = ssot.require_drift_tracker(
+        ARFClassifier(n_models=N_MODELS, seed=safe_seed, drift_detector=drift.ADWIN(clock=cfg['c_int']), warning_detector=drift.ADWIN(clock=cfg['c_int'])))
     
     tau_arf, tau_det = np.nan, np.nan
     errors_pre =[]
```

### `experiments/R3_regime_crossover/exp_R3_regime_crossover.py`

```diff
diff --git a/experiments/R3_regime_crossover/exp_R3_regime_crossover.py b/experiments/R3_regime_crossover/exp_R3_regime_crossover.py
index a0227b1..dfc8f8f 100644
--- a/experiments/R3_regime_crossover/exp_R3_regime_crossover.py
+++ b/experiments/R3_regime_crossover/exp_R3_regime_crossover.py
@@ -6,6 +6,7 @@ Reproduces Figure 3 of the manuscript "The Blind Spot Paradox".
 Strictly adheres to IEEE/ICDM FAIR reproducibility standards.
 """
 import random
+import sys
 import numpy as np
 import pandas as pd
 from scipy.stats import norm
@@ -25,6 +26,9 @@ warnings.filterwarnings('ignore')
 # Assumes script is located in experiments/R3_regime_crossover/
 # ------------------------------------------------------------------------------
 ROOT_DIR = Path(__file__).resolve().parent.parent.parent
+sys.path.insert(0, str(ROOT_DIR))
+from config import experiment_ssot as ssot
+
 RESULTS_DIR = ROOT_DIR / "results" / "R3_regime_crossover"
 DATA_DIR = RESULTS_DIR / "data"
 FIG_DIR = RESULTS_DIR / "figures"
@@ -32,11 +36,11 @@ FIG_DIR = RESULTS_DIR / "figures"
 DATA_DIR.mkdir(parents=True, exist_ok=True)
 FIG_DIR.mkdir(parents=True, exist_ok=True)
 
-N_STEPS = 8000
-DRIFT_TIME = 4000
-TOLERANCE = 1000
-N_SEEDS = 100
-DELTA_E_VALUES = np.linspace(0.02, 0.50, 15)
+N_STEPS = ssot.R3_N_STEPS
+DRIFT_TIME = ssot.R3_T_DRIFT
+TOLERANCE = ssot.R3_TAU_TOL
+N_SEEDS = ssot.R3_N_SEEDS
+DELTA_E_VALUES = ssot.R3_DELTA_E_GRID
 
 def compute_boundary_shift(delta_e):
     r"""
```

### `experiments/R4_proteus_evaluation/exp_R4_main_table.py`

```diff
diff --git a/experiments/R4_proteus_evaluation/exp_R4_main_table.py b/experiments/R4_proteus_evaluation/exp_R4_main_table.py
index f97b922..5dd9882 100644
--- a/experiments/R4_proteus_evaluation/exp_R4_main_table.py
+++ b/experiments/R4_proteus_evaluation/exp_R4_main_table.py
@@ -14,6 +14,7 @@
 
 import collections
 import itertools
+import sys
 import warnings
 from pathlib import Path
 
@@ -32,6 +33,8 @@ warnings.filterwarnings("ignore")
 
 # ─── Configuration & Paths (FAIR Compliance) ─────────────────────────────────
 ROOT_DIR    = Path(__file__).resolve().parent.parent.parent
+sys.path.insert(0, str(ROOT_DIR))
+from config import experiment_ssot as ssot
 RESULTS_DIR = ROOT_DIR / "results" / "R4_proteus_evaluation" / "data"
 TABLES_DIR  = ROOT_DIR / "results" / "R4_proteus_evaluation" / "tables"
 LOGS_DIR    = ROOT_DIR / "logs" / "R4_proteus_evaluation"
@@ -43,8 +46,8 @@ RAW_CSV   = RESULTS_DIR / "exp_R4_results_aligned_fusion.csv"
 OUT_TEX   = TABLES_DIR / "table1_proteus_summary.tex"
 SIGN_CSV  = RESULTS_DIR / "exp_R4_seed_level_tests.csv"
 
-N_SEEDS        = 30
-SEEDS          = list(range(1, N_SEEDS + 1))    # Strict alignment: seeds 1..30
+N_SEEDS        = ssot.R4_N_SEEDS
+SEEDS          = ssot.R4_SEEDS    # Strict alignment: seeds 1..30
 BOOTSTRAP_SEED = 12345                          # Determinism for bootstrap CI
 KSWIN_LAG      = 15                             # W/2 (Structural smoothing lag)
 KSWIN_RESET_MODEL = True   # True = legacy protocol alignment (reset model on detection).
@@ -180,7 +183,9 @@ def make_rf(seed):
     return ensemble.BaggingClassifier(model=tree.HoeffdingTreeClassifier(),
                                       n_models=10, seed=seed)
 
-# ─── 14 Pipelines per (transition, seed) ──────────────────────────────────────
+# ─── 15 Pipelines per (transition, seed) ──────────────────────────────────────
+# 15 are computed, 14 are rendered: EDDM + ARF (c=32) is produced here but has no row in
+# ROW_SPECS, so Table I shows 14 configurations while the raw CSV holds 15.
 def process_transition_seed(trans, seed):
     # Strict RNG isolation per worker (Bit-wise reproducibility).
     # C-Level Overflow Prevention: apply modulo for Cython-compiled extensions
@@ -375,7 +380,7 @@ def build_table(agg, sign_df):
 # ─── Main ─────────────────────────────────────────────────────────────────────
 def main():
     grid = list(itertools.product(TRANSITIONS, SEEDS))
-    print(f"[run] {len(TRANSITIONS)} transitions x {N_SEEDS} seeds x 14 pipelines x 3 regimes")
+    print(f"[run] {len(TRANSITIONS)} transitions x {N_SEEDS} seeds x 15 pipelines x 3 regimes (14 rendered)")
     print("[run] Parallel execution (Joblib) - Please wait...")
     nested = Parallel(n_jobs=-1)(delayed(process_transition_seed)(t, s) for t, s in tqdm(grid, desc="R4 Main Table"))
     df = pd.DataFrame([row for sub in nested for row in sub],
```

### `experiments/R4_proteus_evaluation/exp_R4_kswin_sweep.py`

```diff
diff --git a/experiments/R4_proteus_evaluation/exp_R4_kswin_sweep.py b/experiments/R4_proteus_evaluation/exp_R4_kswin_sweep.py
index 9bac2e6..c5aa451 100644
--- a/experiments/R4_proteus_evaluation/exp_R4_kswin_sweep.py
+++ b/experiments/R4_proteus_evaluation/exp_R4_kswin_sweep.py
@@ -10,6 +10,7 @@ import itertools
 import warnings
 from pathlib import Path
 
+import sys
 import numpy as np
 import pandas as pd
 from scipy.special import expit, gammaln
@@ -24,6 +25,8 @@ warnings.filterwarnings("ignore")
 
 # ─── Configuration & Paths (FAIR Compliance) ─────────────────────────────────
 ROOT_DIR    = Path(__file__).resolve().parent.parent.parent
+sys.path.insert(0, str(ROOT_DIR))
+from config import experiment_ssot as ssot
 RESULTS_DIR = ROOT_DIR / "results" / "R4_proteus_evaluation" / "data"
 TABLES_DIR  = ROOT_DIR / "results" / "R4_proteus_evaluation" / "tables"
 LOGS_DIR    = ROOT_DIR / "logs" / "R4_proteus_evaluation"
@@ -35,8 +38,8 @@ RAW_CSV   = RESULTS_DIR / "exp_R4_results_KSWIN_alpha_sweep.csv"
 OUT_TEX   = TABLES_DIR / "exp_R4_table_KSWIN_alpha_sweep.tex"
 SIGN_CSV  = RESULTS_DIR / "exp_R4_seed_level_tests_KSWIN_alpha_sweep.csv"
 
-N_SEEDS        = 30
-SEEDS          = list(range(1, N_SEEDS + 1))
+N_SEEDS        = ssot.R4_N_SEEDS
+SEEDS          = ssot.R4_SEEDS
 BOOTSTRAP_SEED = 12345
 KSWIN_LAG      = 15
 KSWIN_RESET_MODEL = True
```

### `experiments/R5_real_world_evaluation/exp_R5_config.py`

```diff
diff --git a/experiments/R5_real_world_evaluation/exp_R5_config.py b/experiments/R5_real_world_evaluation/exp_R5_config.py
index bb3f781..b9a9f0f 100644
--- a/experiments/R5_real_world_evaluation/exp_R5_config.py
+++ b/experiments/R5_real_world_evaluation/exp_R5_config.py
@@ -5,10 +5,13 @@ of "The Blind Spot Paradox" (ICDM 2026).
 All paths are resolved dynamically from this file's location, so the repository is
 fully portable (no hard-coded absolute path). River is pinned to 0.23.0 because the
 internal ADWIN clock artifact studied in the paper is version-sensitive."""
+import sys
 from pathlib import Path
 
 # --- Dynamic, portable paths (mandated FAIR layout) ---
 ROOT_DIR    = Path(__file__).resolve().parent.parent.parent
+sys.path.insert(0, str(ROOT_DIR))
+from config import experiment_ssot as ssot
 DATA_DIR    = ROOT_DIR / "data"
 RESULTS_DIR = ROOT_DIR / "results" / "R5_real_world_evaluation" / "data"
 TABLES_DIR  = ROOT_DIR / "results" / "R5_real_world_evaluation" / "tables"
@@ -24,7 +27,7 @@ CHECKPOINTS_DIR.mkdir(parents=True, exist_ok=True)
 
 # --- Reproducibility ---
 SEED_MASTER       = 42
-N_SEEDS           = 30
+N_SEEDS           = ssot.N_SEEDS_REAL
 RIVER_VERSION_PIN = "0.23.0"
 
 # --- Pipelines (G4: only the three columns shown in Table II) ---
@@ -35,7 +38,7 @@ PIPELINES_FLOODING = ["pht_ht", "pht_arf_c1"]   # per-episode decomposition (Sec
 BAF_VARIANTS  = ["Base", "VariantI", "VariantII"]
 BAF_DRIFTS    = [125000, 250000, 375000, 500000, 625000, 750000, 875000]
 BAF_WARMUP    = 100_000
-BAF_TAU_TOL   = 5_000
+BAF_TAU_TOL   = ssot.TAU_TOL
 BAF_NONE_FILL = 0     # default label used when the classifier abstains
 
 # --- INSECTS (Souza et al., 2020, Table 2) ---
@@ -44,7 +47,7 @@ INSECTS_VARIANTS = ["abrupt_balanced", "gradual_balanced",
 INSECTS_WARMUP_FRACTION = 0.10
 INSECTS_WARMUP_CAP      = 100_000
 INSECTS_TAU_FRACTION    = 0.05
-INSECTS_TAU_CAP         = 5_000
+INSECTS_TAU_CAP         = ssot.TAU_TOL
 INSECTS_NONE_FILL       = -1
 
 # Canonical drift positions (Souza 2020, Table 2). The reoccurring stream stops at
```

### `experiments/R6_hydra_factor/exp_R6_compute_hydra.py`

```diff
diff --git a/experiments/R6_hydra_factor/exp_R6_compute_hydra.py b/experiments/R6_hydra_factor/exp_R6_compute_hydra.py
index dd17be5..7ff5e81 100644
--- a/experiments/R6_hydra_factor/exp_R6_compute_hydra.py
+++ b/experiments/R6_hydra_factor/exp_R6_compute_hydra.py
@@ -7,11 +7,17 @@ power-law prefactors/exponents (K_HAT, K_ARF, alpha_HAT, alpha_ARF).
 Inputs : R6_hat_instrumented.parquet (tau_hat)  +  R2_instrumented_A_PHT_ARF.parquet (tau_arf).
 Output : a small .tex snippet + console report. No figure.
 """
+import sys
+
 import numpy as np
 import pandas as pd
 from pathlib import Path
+from scipy.stats import norm
 
 ROOT_DIR = Path(__file__).resolve().parent.parent.parent
+sys.path.insert(0, str(ROOT_DIR))
+from config import experiment_ssot as ssot
+
 R6 = ROOT_DIR / "results" / "R6_hydra_factor" / "data" / "R6_hat_instrumented.parquet"
 R2 = ROOT_DIR / "results" / "R2_instrumented_blind_spot" / "data" / "R2_instrumented_A_PHT_ARF.parquet"
 OUT = ROOT_DIR / "results" / "R6_hydra_factor" / "tables" / "exp_R6_hydra_empirical_validation.tex"
@@ -26,21 +32,32 @@ hat = pd.read_parquet(R6).dropna(subset=['tau_hat'])
 arf = pd.read_parquet(R2).dropna(subset=['tau_arf'])
 # R2 stores boundary_shift; map to the same Delta_e transform if 'delta_e' absent
 if 'delta_e' not in arf.columns:
-    from scipy.stats import norm
     arf['delta_e'] = norm.cdf(arf['boundary_shift'] / np.sqrt(2)) - 0.5
 
 hat_m = hat.groupby('delta_e')['tau_hat'].mean()
 arf_m = arf.groupby('delta_e')['tau_arf'].mean()
 
 merged = pd.concat([hat_m.rename('tau_hat'), arf_m.rename('tau_arf')], axis=1).dropna()
+assert len(merged) == 20, f"R6/R2 Delta_e join dropped points: {len(merged)} of 20 retained"
 merged['hydra'] = merged['tau_hat'] / merged['tau_arf']
 
 K_hat, a_hat = powerlaw(hat_m)
 K_arf, a_arf = powerlaw(arf_m)
 
-# Hydra endpoints near the magnitudes cited in the paper
-def at(de):
+# Hydra endpoints at the magnitudes cited in the paper. 0.14 and 0.33 are ROUNDED LABELS: the
+# swept grid is norm.cdf(linspace(0.1, 4.0, 20)/sqrt(2)) - 0.5, whose points 2 and 6 are 0.140949
+# and 0.326793. Resolve the label to its grid point, then assert the selection is exact -- the bare
+# idxmin silently accepted any nearest point, including one from a different grid.
+DELTA_E_GRID = norm.cdf(ssot.R6_BOUNDARY_SHIFTS / np.sqrt(2)) - 0.5
+HYDRA_ANCHORS = {0.14: 2, 0.33: 6}       # manuscript label -> index in DELTA_E_GRID
+GRID_TOL = 1e-6
+
+def at(label):
+    de = DELTA_E_GRID[HYDRA_ANCHORS[label]]
     i = (merged.index.to_series() - de).abs().idxmin()
+    assert abs(i - de) <= GRID_TOL, (
+        f"Delta_e {i} is {abs(i - de):.2e} from the grid anchor {de} for label {label} "
+        f"(tolerance {GRID_TOL:g}): the R6/R2 magnitude grid has changed")
     return merged.loc[i, 'hydra'], i
 h_lo, de_lo = at(0.14)
 h_hi, de_hi = at(0.33)
```

### `experiments/R6_hydra_factor/exp_R6_generate_data.py`

```diff
diff --git a/experiments/R6_hydra_factor/exp_R6_generate_data.py b/experiments/R6_hydra_factor/exp_R6_generate_data.py
index da5644a..fc0d9e7 100644
--- a/experiments/R6_hydra_factor/exp_R6_generate_data.py
+++ b/experiments/R6_hydra_factor/exp_R6_generate_data.py
@@ -8,6 +8,7 @@ locking so the run is bit-wise reproducible. The Hydra factor tau_HAT / tau_ARF
 power-law fits (K_HAT, alpha_HAT) are assembled downstream by exp_R6_compute_hydra.py.
 """
 import random
+import sys
 import numpy as np
 import pandas as pd
 from joblib import Parallel, delayed
@@ -21,13 +22,16 @@ warnings.filterwarnings('ignore')
 
 # [IEEE/ICDM FAIR Compliance] Dynamic path resolution; script lives in experiments/R6_hydra_factor/
 ROOT_DIR = Path(__file__).resolve().parent.parent.parent
+sys.path.insert(0, str(ROOT_DIR))
+from config import experiment_ssot as ssot
+
 DATA_DIR = ROOT_DIR / "results" / "R6_hydra_factor" / "data"
 DATA_DIR.mkdir(parents=True, exist_ok=True)
 
 # M=1 => single Hoeffding Adaptive Tree; internal clock c_int=1 (hyper-reactive)
-N_STEPS, T_DRIFT, N_MODELS, C_INT = 8000, 4000, 1, 1
-BOUNDARY_SHIFTS = np.linspace(0.1, 4.0, 20)
-SEEDS = list(range(1, 101))
+N_STEPS, T_DRIFT, N_MODELS, C_INT = ssot.R6_N_STEPS, ssot.R6_T_DRIFT, ssot.R6_N_MODELS, ssot.R6_C_INT
+BOUNDARY_SHIFTS = ssot.R6_BOUNDARY_SHIFTS
+SEEDS = ssot.R6_SEEDS
 
 def run_instrumented_hat(boundary_shift, seed):
     # Worker-Level Global Locking (CRITICAL): identical to the validated R2 scheme,
@@ -37,9 +41,10 @@ def run_instrumented_hat(boundary_shift, seed):
     np.random.seed(safe_seed)
     rng = np.random.default_rng(safe_seed)
 
-    hat = ARFClassifier(n_models=N_MODELS, seed=safe_seed,
-                        drift_detector=drift.ADWIN(clock=C_INT),
-                        warning_detector=drift.ADWIN(clock=C_INT))
+    hat = ssot.require_drift_tracker(
+        ARFClassifier(n_models=N_MODELS, seed=safe_seed,
+                      drift_detector=drift.ADWIN(clock=C_INT),
+                      warning_detector=drift.ADWIN(clock=C_INT)))
 
     tau_hat = np.nan
     for t in range(N_STEPS):
```

### `experiments/R6_hydra_factor/exp_R6_hydra_survival.py` — NEW FILE (168 lines)

Created by stream S7; no diff (the file is its own content). Purpose:
Hydra acceleration factor under administrative censoring (F23): Kaplan-Meier / RMST with seed-paired bootstrap.

### `experiments/R7_clock_mismatch/exp_R7_generate_data.py`

```diff
diff --git a/experiments/R7_clock_mismatch/exp_R7_generate_data.py b/experiments/R7_clock_mismatch/exp_R7_generate_data.py
index f5e1e6e..a80e98d 100644
--- a/experiments/R7_clock_mismatch/exp_R7_generate_data.py
+++ b/experiments/R7_clock_mismatch/exp_R7_generate_data.py
@@ -10,6 +10,7 @@ exact R2/R6 worker-level RNG locking. The Regime-1 miss-rate summary is assemble
 downstream by exp_R7_compute_regime1.py; reproduction checks live in tests/test_R7_regime1.py.
 """
 import random
+import sys
 import warnings
 import numpy as np
 import pandas as pd
@@ -23,13 +24,16 @@ warnings.filterwarnings('ignore')
 
 # Script lives in experiments/R7_clock_mismatch/ ; target the centralized results root.
 ROOT_DIR = Path(__file__).resolve().parent.parent.parent
+sys.path.insert(0, str(ROOT_DIR))
+from config import experiment_ssot as ssot
+
 DATA_DIR = ROOT_DIR / "results" / "R7_clock_mismatch" / "data"
 DATA_DIR.mkdir(parents=True, exist_ok=True)
 
-N_STEPS, T_DRIFT, N_MODELS = 8000, 4000, 10
-BOUNDARY_SHIFTS = np.linspace(0.1, 4.0, 20)
-SEEDS = list(range(1, 101))
-EXT_DELTA = 0.002  # external ADWIN sensitivity (matches the submitted Fig. 2ter setup)
+N_STEPS, T_DRIFT, N_MODELS = ssot.R7_N_STEPS, ssot.R7_T_DRIFT, ssot.R7_N_MODELS
+BOUNDARY_SHIFTS = ssot.R7_BOUNDARY_SHIFTS
+SEEDS = ssot.R7_SEEDS
+EXT_DELTA = ssot.R7_EXT_DELTA  # external ADWIN sensitivity (matches the submitted Fig. 2ter setup)
 
 SCENARIOS = [
     {"id": "A_mismatched", "c_int": 1,  "c_ext": 32},  # River's default external clock
@@ -45,9 +49,10 @@ def run_clock_mismatch(boundary_shift, seed, cfg):
     np.random.seed(safe_seed)
     rng = np.random.default_rng(safe_seed)
 
-    arf = ARFClassifier(n_models=N_MODELS, seed=safe_seed,
-                        drift_detector=drift.ADWIN(clock=cfg['c_int']),
-                        warning_detector=drift.ADWIN(clock=cfg['c_int']))
+    arf = ssot.require_drift_tracker(
+        ARFClassifier(n_models=N_MODELS, seed=safe_seed,
+                      drift_detector=drift.ADWIN(clock=cfg['c_int']),
+                      warning_detector=drift.ADWIN(clock=cfg['c_int'])))
     ext = drift.ADWIN(delta=EXT_DELTA, clock=cfg['c_ext'])
 
     tau_arf, tau_det = np.nan, np.nan
```

### `experiments/R8_lambda_op_sweep/exp_R8_lambda_op_sweep.py`

```diff
diff --git a/experiments/R8_lambda_op_sweep/exp_R8_lambda_op_sweep.py b/experiments/R8_lambda_op_sweep/exp_R8_lambda_op_sweep.py
index e99b35b..2e0509a 100644
--- a/experiments/R8_lambda_op_sweep/exp_R8_lambda_op_sweep.py
+++ b/experiments/R8_lambda_op_sweep/exp_R8_lambda_op_sweep.py
@@ -17,6 +17,8 @@ Methodological alignments:
   3. Early-break upon the first captured post-drift swap (identical logic to R1).
   4. Seed pooling matches the established R1 pipeline (SeedSequence(42).spawn(N_SEEDS)).
 """
+import sys
+
 import numpy as np
 import pandas as pd
 from pathlib import Path
@@ -27,70 +29,72 @@ from river import drift, forest
 
 # --- Configuration -----------------------------------------------------------
 ROOT_DIR    = Path(__file__).resolve().parent.parent.parent
+sys.path.insert(0, str(ROOT_DIR))
+from config import experiment_ssot as ssot
 RESULTS_DIR = ROOT_DIR / "results" / "R8_lambda_op_sweep" / "data"
 RESULTS_DIR.mkdir(parents=True, exist_ok=True)
 OUT_CSV     = RESULTS_DIR / "exp_R8_lambda_op_sweep.csv"
 
-WARMUP        = 1000            # Warmup steps (matches R1)
-DRIFT_GAP     = 1000            # t_drift_eff = WARMUP + DRIFT_GAP = 2000 (matches R1)
-TOLERANCE     = 50000           # Post-drift tracking tolerance (matches R1)
-T_DRIFT       = WARMUP + DRIFT_GAP
-N_STEPS       = T_DRIFT + TOLERANCE
-
-N_MODELS      = 10              # M = 10
-C_INT         = 1               # Blind spot configuration
-N_SEEDS       = 200
-DELTA_E_GRID  = np.linspace(0.10, 0.50, 21)
-DELTA_P       = 0.005           # PH/CUSUM tolerance
-Q_LEVEL       = 0.05
+WARMUP        = ssot.R8_WARMUP_WINDOW      # Warmup steps (matches R1)
+DRIFT_GAP     = ssot.R8_DRIFT_GAP          # t_drift_eff = WARMUP + DRIFT_GAP = 2000 (matches R1)
+TOLERANCE     = ssot.R8_CENSORING_HORIZON  # Post-drift tracking tolerance (matches R1)
+T_DRIFT       = ssot.R8_T_DRIFT
+N_STEPS       = ssot.R8_N_STEPS
+
+N_MODELS      = ssot.R8_N_MODELS           # M = 10
+C_INT         = ssot.R8_C_INT              # Blind spot configuration
+N_SEEDS       = ssot.R8_N_SEEDS
+DELTA_E_GRID  = ssot.R8_DELTA_E_GRID
+DELTA_P       = ssot.R8_DELTA_P            # PH/CUSUM tolerance
+Q_LEVEL       = ssot.R8_Q_LEVEL
 OVERLAP_REF   = {0.10: 12.95, 0.25: 48.90, 0.40: 26.95}  # Reference q05 to reproduce from R1
 
 
-def run_tau_arf(seed: int, delta_e: float):
-    """Returns the timestamp of the first internal post-drift swap (NaN if none < TOLERANCE)."""
+def run_tau_arf(seed: int, delta_e: float, t_drift: int = T_DRIFT, n_steps: int = N_STEPS):
+    """Returns the timestamp of the first internal post-drift swap (NaN if none < TOLERANCE).
+    t_drift/n_steps are overridable for the warm-up parity sweep (S7/G1); the defaults reproduce
+    the published T_DRIFT=2000 configuration bit-for-bit."""
     rng = np.random.default_rng(seed)
     b_shift = np.sqrt(2.0) * norm.ppf(0.5 + delta_e)   # Shifted boundary matching target Delta_e
 
-    model = forest.ARFClassifier(
+    model = ssot.require_drift_tracker(forest.ARFClassifier(
         n_models=N_MODELS, seed=seed,
         drift_detector=drift.ADWIN(clock=C_INT),
         warning_detector=drift.ADWIN(clock=C_INT),
-    )
-
-    if not hasattr(model, "_drift_tracker"):
-        raise RuntimeError(
-            "ARFClassifier missing '_drift_tracker' attribute: incompatible River version. "
-            "Ensure River 0.23.0 is installed for proper internal tree swap tracking."
-        )
+    ))
 
     tau_arf = np.nan
-    for t in range(1, N_STEPS + 1):
+    for t in range(1, n_steps + 1):
         x0, x1 = rng.normal(), rng.normal()
         x_dict = {0: x0, 1: x1}
-        y = int(x0 + x1 > 0.0) if t <= T_DRIFT else int(x0 + x1 > b_shift)
+        y = int(x0 + x1 > 0.0) if t <= t_drift else int(x0 + x1 > b_shift)
 
         before = sum(model._drift_tracker.values())
         model.learn_one(x_dict, y)          # predict_one omitted: unnecessary for tau_ARF tracking
         after = sum(model._drift_tracker.values())
 
-        if t > T_DRIFT and after > before:
-            tau_arf = t - T_DRIFT
+        if t > t_drift and after > before:
+            tau_arf = t - t_drift
             break                            # First post-drift swap captured -> stop
     return {"seed": seed, "delta_e": float(delta_e), "tau_arf": tau_arf}
 
 
-def main():
-    seq = np.random.SeedSequence(42)
+def main(t_drift: int = T_DRIFT):
+    n_steps = t_drift + TOLERANCE
+    suffix = "" if t_drift == T_DRIFT else f"_tdrift{t_drift}"
+    out_csv = RESULTS_DIR / f"exp_R8_lambda_op_sweep{suffix}.csv"
+
+    seq = np.random.SeedSequence(ssot.SEED_SCHEME_SEEDSEQ_ENTROPY)
     seed_pool = [int(s.generate_state(1)[0]) for s in seq.spawn(N_SEEDS)]
     grid = [(s, de) for de in DELTA_E_GRID for s in seed_pool]
 
     print(f"[INFO] {len(grid)} ARF runs (c_int={C_INT}, M={N_MODELS}) "
-          f"| drift@t={T_DRIFT} tol={TOLERANCE}")
+          f"| drift@t={t_drift} tol={TOLERANCE}")
     res = Parallel(n_jobs=-1)(
-        delayed(run_tau_arf)(s, de) for s, de in tqdm(grid, desc="R8 Lambda Sweep")
+        delayed(run_tau_arf)(s, de, t_drift, n_steps) for s, de in tqdm(grid, desc="R8 Lambda Sweep")
     )
     df = pd.DataFrame(res)
-    df.to_csv(RESULTS_DIR / "exp_R8_fine_grid_raw.csv", index=False)
+    df.to_csv(RESULTS_DIR / f"exp_R8_fine_grid_raw{suffix}.csv", index=False)
 
     # --- Per-magnitude aggregation ----------------------------------------------
     records = []
@@ -108,7 +112,7 @@ def main():
             "lambda_limit": round(lam_limit, 3),
         })
     table = pd.DataFrame.from_records(records)
-    table.to_csv(OUT_CSV, index=False)
+    table.to_csv(out_csv, index=False)
 
     # --- Global minimum search --------------------------------------------------
     valid = table.dropna(subset=["lambda_limit"])
@@ -131,4 +135,4 @@ def main():
 
 
 if __name__ == "__main__":
-    main()
\ No newline at end of file
+    main(int(sys.argv[1]) if len(sys.argv) > 1 else T_DRIFT)
\ No newline at end of file
```

### `experiments/R9_mcrit/exp_R9_compute_mcrit.py`

```diff
diff --git a/experiments/R9_mcrit/exp_R9_compute_mcrit.py b/experiments/R9_mcrit/exp_R9_compute_mcrit.py
index 3dd45b4..45c3cfc 100644
--- a/experiments/R9_mcrit/exp_R9_compute_mcrit.py
+++ b/experiments/R9_mcrit/exp_R9_compute_mcrit.py
@@ -1,3 +1,4 @@
+import sys
 import warnings
 import numpy as np
 import pandas as pd
@@ -13,25 +14,30 @@ warnings.filterwarnings("ignore", category=RuntimeWarning)
 # Parameters
 # --------------------------------------------------------------------
 ROOT_DIR = Path(__file__).resolve().parent.parent.parent
+sys.path.insert(0, str(ROOT_DIR))
+from config import experiment_ssot as ssot
+
 RESULTS_DIR = ROOT_DIR / "results" / "R9_mcrit" / "data"
 FIG_DIR = ROOT_DIR / "results" / "R9_mcrit" / "figures"
 RESULTS_DIR.mkdir(parents=True, exist_ok=True)
 FIG_DIR.mkdir(parents=True, exist_ok=True)
 
-LAMBDAS = [8, 25, 50]                 # Three calibrations from the paper
-DELTA_P = 0.005                       # CUSUM tolerance
-BETAS = [0.50, 0.05]                  # Main beta + complement
-DKW_ALPHA = 0.05                      # 95% DKW confidence band
-TARGET_DELTAS = [0.10, 0.15, 0.20, 0.25, 0.33, 0.40, 0.50]
+LAMBDAS = ssot.R9_LAMBDAS             # Three calibrations from the paper
+DELTA_P = ssot.R9_DELTA_P             # CUSUM tolerance
+RELIABILITY_TARGETS = ssot.R9_RELIABILITY_TARGETS   # r = 1 - P_miss target
+DKW_ALPHA = ssot.R9_DKW_ALPHA         # 95% DKW confidence band
+TARGET_DELTAS = ssot.R9_TARGET_DELTAS
 PALETTE = {8: "#00748C", 25: "#E08000", 50: "#3B6FA0"}  # teal / orange / navy
 
 
 # --------------------------------------------------------------------
 # Helpers
 # --------------------------------------------------------------------
-def mcrit_from_F(F, beta):
+def mcrit_from_F(F, r):
     """
-    M_crit = floor( ln(beta) / ln(1-F) ), STRICTLY DECREASING with respect to F.
+    M_crit = floor( ln(r) / ln(1-F) ), STRICTLY DECREASING with respect to F.
+    r is the reliability target of Corollary 2: r = 1 - P_miss. A LARGER M_crit is
+    PERMISSIVE (it certifies a larger ensemble), so a smaller r is the permissive end.
     F <= 0: no adaptation observed before tau_det* -> no finite M
             starves the detector -> +inf.
     F >= 1: a single tree is already sufficient to starve the detector -> 0.
@@ -42,7 +48,7 @@ def mcrit_from_F(F, beta):
         return np.inf
     if F >= 1.0:
         return 0.0
-    return float(np.floor(np.log(beta) / np.log(1.0 - F)))
+    return float(np.floor(np.log(r) / np.log(1.0 - F)))
 
 
 def empirical_cdf_at(data, x):
@@ -152,18 +158,18 @@ def main():
             F_emp_low = max(0.0, F_emp - eps_dkw)  # borne basse -> M_crit max (defensif)
             pmiss_m10 = 1.0 - (1.0 - F_emp) ** 10
 
-            for beta in BETAS:
-                m_emp = mcrit_from_F(F_emp, beta)
-                m_exp = mcrit_from_F(F_exp, beta)
-                m_alt = mcrit_from_F(F_alt, beta) if np.isfinite(F_alt) else np.nan
-                m_emp_dkw_up = mcrit_from_F(F_emp_low, beta)  # Lower bound -> M_crit max (defensive)
+            for r in RELIABILITY_TARGETS:
+                m_emp = mcrit_from_F(F_emp, r)
+                m_exp = mcrit_from_F(F_exp, r)
+                m_alt = mcrit_from_F(F_alt, r) if np.isfinite(F_alt) else np.nan
+                m_emp_dkw_up = mcrit_from_F(F_emp_low, r)  # Lower bound -> M_crit max (defensive)
                 coherent = (m_exp >= m_emp) == (F_exp <= F_emp)
 
                 rows.append({
                     "delta_e": round(target, 3),
                     "delta_e_eff": round(de_eff, 4),
                     "lambda": lam,
-                    "beta": beta,
+                    "reliability_r": r,
                     "n_samples": n,
                     "E_tau_HAT": round(mean_tau, 2),
                     "tau_det_star": round(tau_det_star, 2),
@@ -182,7 +188,7 @@ def main():
 
             print(f"  De~{de_eff:.3f} | lam={lam:>2} | tau*={tau_det_star:8.1f} | "
                   f"F_emp={F_emp:.3f} F_exp={F_exp:.3f} | "
-                  f"Mcrit(.50) emp={mcrit_from_F(F_emp,0.5)} exp={mcrit_from_F(F_exp,0.5)} | "
+                  f"Mcrit(r=.50) emp={mcrit_from_F(F_emp,0.5)} exp={mcrit_from_F(F_exp,0.5)} | "
                   f"{verdict}")
 
     res = pd.DataFrame(rows)
@@ -198,7 +204,7 @@ def main():
     # large/volatile (up to +inf when F_emp=0 at N=100). These points are NOT relevant
     # to the structural claim. Restricting the DOMAIN cleanly removes out-of-scale
     # peaks, inf values, and prevents matplotlib from connecting points over gaps.
-    sub = res[(res["beta"] == 0.50) & (res["delta_e_eff"] > 0.20)].copy()
+    sub = res[(res["reliability_r"] == 0.50) & (res["delta_e_eff"] > 0.20)].copy()
     FIG_LAMBDAS = [25, 50]
     CAP = 10
     fig, ax = plt.subplots(figsize=(7.0, 4.3), dpi=300)
@@ -219,7 +225,7 @@ def main():
     ax.text(0.015, 0.9, "River default $M=10$", transform=ax.transAxes,
             ha="left", va="top", fontsize=8, color="0.35")
     ax.set_xlabel(r"Effective error jump $\Delta e$")
-    ax.set_ylabel(r"Critical ensemble size $M_{\rm crit}$  ($\beta=0.50$)")
+    ax.set_ylabel(r"Critical ensemble size $M_{\rm crit}$  ($r=0.50$)")
     ax.set_ylim(-0.5, CAP + 0.8)
     ax.set_title(r"Empirical vs exponential $M_{\rm crit}$ (blind-spot regime, real $\tau_{\rm HAT}$)",
                  fontweight="bold", pad=10)
```

### `experiments/R9_mcrit/exp_R9_generate_data.py`

```diff
diff --git a/experiments/R9_mcrit/exp_R9_generate_data.py b/experiments/R9_mcrit/exp_R9_generate_data.py
index b835f7b..e2b5fe6 100644
--- a/experiments/R9_mcrit/exp_R9_generate_data.py
+++ b/experiments/R9_mcrit/exp_R9_generate_data.py
@@ -8,6 +8,7 @@ The empirical CDF of tau_HAT is consumed by exp_R9_compute_mcrit.py to derive th
 critical ensemble size M_crit. Determinized with the exact R2/R6/R7 worker-level RNG locking.
 """
 import random
+import sys
 import warnings
 import numpy as np
 import pandas as pd
@@ -19,14 +20,17 @@ from river.forest import ARFClassifier
 warnings.filterwarnings('ignore')
 
 ROOT_DIR = Path(__file__).resolve().parent.parent.parent
+sys.path.insert(0, str(ROOT_DIR))
+from config import experiment_ssot as ssot
+
 DATA_DIR = ROOT_DIR / "results" / "R9_mcrit" / "data"
 DATA_DIR.mkdir(parents=True, exist_ok=True)
 
-N_STEPS, T_DRIFT, N_MODELS = 8000, 4000, 1   # M=1 single Hoeffding Adaptive Tree
-DELTA_E_WINDOW = 500
-C_INT, C_EXT = 1, 32
-BOUNDARY_SHIFTS = np.linspace(0.1, 4.0, 20)
-SEEDS = list(range(1, 101))                  # 100 seeds per magnitude
+N_STEPS, T_DRIFT, N_MODELS = ssot.R9_N_STEPS, ssot.R9_T_DRIFT, ssot.R9_N_MODELS   # M=1 single Hoeffding Adaptive Tree
+DELTA_E_WINDOW = ssot.R9_DELTA_E_WINDOW
+C_INT, C_EXT = ssot.R9_C_INT, ssot.R9_C_EXT
+BOUNDARY_SHIFTS = ssot.R9_BOUNDARY_SHIFTS
+SEEDS = ssot.R9_SEEDS                        # 100 seeds per magnitude
 
 def run_instrumented_hat(boundary_shift, seed):
     safe_seed = int(seed % (2**31 - 1))
@@ -34,10 +38,11 @@ def run_instrumented_hat(boundary_shift, seed):
     np.random.seed(safe_seed)
     rng = np.random.default_rng(safe_seed)
 
-    hat = ARFClassifier(n_models=N_MODELS, seed=safe_seed,
-                        drift_detector=drift.ADWIN(clock=C_INT),
-                        warning_detector=drift.ADWIN(clock=C_INT))
-    ext = drift.ADWIN(delta=0.002, clock=C_EXT)
+    hat = ssot.require_drift_tracker(
+        ARFClassifier(n_models=N_MODELS, seed=safe_seed,
+                      drift_detector=drift.ADWIN(clock=C_INT),
+                      warning_detector=drift.ADWIN(clock=C_INT)), warning=True)
+    ext = drift.ADWIN(delta=ssot.R9_EXT_DELTA, clock=C_EXT)
 
     tau_hat, tau_det = np.nan, np.nan
     errors_pre, errors_post = [], []
```


---

# S7-bis — stream closure

Scope: `docs/manuscript/articleA_blindspot_v64_camera_ready.tex` (the manuscript of record; v63 is
archived) against the `results/` tree. Every value below was **re-measured in S7-bis** from the
committed artifacts; nothing is carried on trust from the S7 report above.

## B0. Manuscript of record

`CLAUDE.md` was created at the repository root and declares
`docs/manuscript/articleA_blindspot_v64_camera_ready.tex` (bibliography `articleA_biblio_v64.bib`)
as the living manuscript, and v63 as archived. `README.md:227` was repointed from "the v63
camera-ready" to the manuscript of record, with the v64 line numbers (L236, L391).

**Phase 3 replayed on v64.** v64 carries the Section III theory rewrite, which shifts every line
after 164 by +3; the v63 anchors are therefore invalid and were re-grepped. Pre-edit `\beta` census
over v64: **L242, L270, L272, L279, L323**. The first four are the reliability target of Corollary 2
and were renamed to $r$; **L323 is the GARCH persistence $\alpha + \beta$ and was not touched**.
L274 (no `\beta`, but "reliability must be settled empirically") was aligned to "the reliability $r$",
reproducing the v63 edit exactly. Post-edit census: **exactly one occurrence, L323, the GARCH one.**

## B1. Divergences D-1 … D-10 — applied to v64, each anchored to its line

Every substitution below is exact-match and was asserted unique before application (the patch script
aborts without writing if any anchor misses or matches twice). Every artifact value was re-measured
in S7-bis from the file named in the "source" column.

| # | v64 line | manuscript before | manuscript after | re-measured value | source artifact |
|---|---------|-------------------|------------------|-------------------|-----------------|
| D-1 | 192 | "achieves exactly $0\%$ detection rate … for $\Delta e > 0.24$" | "achieves a ${<}0.1\%$ detection rate … ($1$ detection in $1{,}600$ runs, itself a blind spot: $\tau_{\mathrm{ARF}} = 54 \ll \tau_{\mathrm{det}} = 649$)" | **1/1600 = 0.0625 %**; `boundary_shift 1.331579`, $\Delta e = 0.326793$, seed 6, $\tau_{\mathrm{arf}} = 54$, $\tau_{\mathrm{det}} = 649$ | `results/R2_instrumented_blind_spot/data/R2_instrumented_A_PHT_ARF.parquet` |
| D-2 | 213 | "miss rates rise from 60\% to 100\%" | "miss rates rise from 68\% to 100\%" | min miss **0.6800** at $\Delta e = 0.140949$, max **1.0000** | `…/R2_instrumented_B_PHT_ARF.parquet` |
| D-3 | 298, 414 | "$\lambda_{\mathrm{op}}$ never exceeds $12.4$" / "$\lambda_{\mathrm{op}} \le 12.4$" | "$\le 12.44$ at $T_{\mathrm{drift}} = 2000$" (and $\le 10.5$ at $4000$ — see M1) | $\max \lambda_{\mathrm{limit}}$ over $[0.20, 0.50]$ = **12.4380** @ $\Delta e = 0.22$; **10.4920** @ $T_{\mathrm{drift}}{=}4000$ | `results/R8_lambda_op_sweep/data/exp_R8_lambda_op_sweep{,_tdrift4000}.csv` |
| D-4 | 405, 416 | "$\sim 24$ percentage points (RF $\approx 0.745$ vs ARF $\approx 0.985$)"; "${\sim}24\%$ … cost" | "$23.4$ percentage points (RF $\approx 0.750$ vs ARF $\approx 0.984$)"; "$23.4$ percentage-point … cost" | RF **0.7498**, ARF **0.9840**, gap **23.41 pp** at $\Delta e = 0.50$ | `results/R3_regime_crossover/data/R3_regime_crossover_metrics.parquet` |
| D-5 | 376 | "an artifactual $80\%$ miss rate" | "an artifactual miss rate reaching $77\%$" | HT miss at the three sub-$0.09$ grid points: **77 / 73 / 71 %** | idem |
| D-6 | 370 | Fig. 3 caption "($100\%$ missed)" | "(missed detections climb monotonically across the band, from $1\%$ at its first grid point $\Delta e{=}0.26$ to $100\%$ at $\Delta e{=}0.50$)" | ARF miss over $\Delta e \ge 0.25$: **1, 2, 8, 17, 32, 68, 98, 100 %** | idem |
| D-7 | 136 | "at $b = 4.0$, empirical $\Delta e \approx 0.02$" | "the empirical $\Delta e$ measures $-0.02$---not merely attenuated but \emph{negative}" | mean over 100 seeds = **−0.0235** (median −0.0230) | `results/R9_mcrit/data/results_instrumented_A_ADWIN_HAT.csv` |
| D-8 | 365 fn | "$\lambda = 15$ … calibrated against ProteuS pre-drift volatility to allow at most one false alarm per warm-up window" | "$\lambda = 15$ … is the fixed ProteuS operating threshold, applied with the monitor armed from $t{=}0$ and no warm-up window; the one-false-alarm-per-warm-up calibration procedure is used for the real-world streams of Section~\ref{sec:crossover}, not on ProteuS" | `PageHinkley(threshold=15.0)` hard-coded in R4; the calibration routine (`calibrate_lambda`, `PHT_TARGET_FA = 1`) exists only in R5 | `experiments/R4_proteus_evaluation/exp_R4_main_table.py`, `experiments/R5_real_world_evaluation/exp_R5_common.py:59-85` |
| D-9 | 313 | "theoretical $\Delta e \in [0.02, 0.50]$" | "theoretical $\Delta e \in [0.028, 0.498]$" | grid endpoints **0.028186 … 0.497661** | `results/audit_S7/hydra_survival.csv` (20-point grid) |
| D-10 | 119 | "(mean ${\approx}23$ at $c{=}32$)" | "(mean $\tau_{\mathrm{stat}} + 15.5$ at $c{=}32$)" + the derivation sentence | Table I measures $\mathrm{ADD} = 31.0$ with $\sigma = 0.0$ over **360 runs × 3 regimes** (ADWIN+ARF, $c{=}32$); $\tau^{*} \bmod c = 4000 \bmod 32 = 0$, so Eq. (1) gives $31 = 31 + \tau_{\mathrm{stat}} \Rightarrow \tau_{\mathrm{stat}} = 0$, and the uniform-phase mean is $(c-1)/2 = 15.5$ | `results/R4_proteus_evaluation/data/exp_R4_results_aligned_fusion.csv` |

**R-2 reclassified as D-10, as instructed.** It is not an untraceable residue: Table I pins
$\tau_{\mathrm{stat}} = 0$ by measurement, which determines the uniform-phase mean exactly. The
manuscript's $23$ was a wrong value, and is corrected.

### Two further divergences, found by S7-bis itself

| # | v64 line | claim | measurement | resolution |
|---|---------|-------|-------------|------------|
| D-11 | 204 | *"the single-tree HAT stays at ${\approx}40\%$ miss under the same clock"* | the R-1 run (below) gives **29.7 %** over $\Delta e > 0.30$ — the band the sentence is comparing against — and **35.2 %** over the full grid. $40\%$ is attained at no band | rewritten to "$30\%$ miss over that band, and $35\%$ across the full magnitude grid". The rhetorical point is **strengthened**: the $M{=}10$ ensemble scores $2.4\%$ on the same band, a $12\times$ gap rather than the $8\times$ the old numerals implied |
| D-12 | 309 | *"in ${\approx}5$\,h total"* | not reproducible from any committed record, and not supported by measurement: eight of the nine stages sum to **1 h 58 min 15 s** and R5 is additionally long-running | replaced by the measured figure for R1--R4 and R6--R9, with a pointer to `docs/ENVIRONMENT.md`. This is what actually discharges residue R-3: the runtime claim is now a measurement in a versioned file, not an assertion |

**Arbitration recorded — D-3 versus M1.** The plan asks to keep $12.4$ as the $T_{\mathrm{drift}} =
2000$ value (M1) while D-3 establishes that $\max \lambda_{\mathrm{limit}} = 12.438 > 12.4$, so
"never exceeds 12.4" is false at full precision. Both are satisfied by writing
$\lambda_{\mathrm{op}} \le 12.44$: it is true of the measurement, and it is the plan's numeral to one
decimal. The measured maximum is recorded here and in `config_matrix.md` §5.

## B2. Manuscript writings M1 … M4

**M1 — the envelope-floor mechanism is refuted, the floor survives (L298, L414).** The manuscript
attributed the flat $q_{0.05} \approx 13$ below $\Delta e = 0.16$ to noise-driven swaps. Re-measured
at warm-up parity the plateau does not exist: $q_{0.05} = 25.70,\ 30.95,\ 54.70,\ 54.70$ at
$T_{\mathrm{drift}} = 4000$ against $12.95,\ 12.95,\ 12.95,\ 12.95$ at $2000$. The passage now states
the plateau as a property of the short warm-up and the floor as a guard against an immature
ensemble. Both ceilings are written with their warm-up: $\lambda_{\mathrm{op}} \le 12.44$ at
$T_{\mathrm{drift}} = 2000$ (the published configuration) and $\le 10.5$ at $4000$ (ProteuS parity).
The Fundamental Tension paragraph now **names** the parity gap rather than assuming it away: the
$\lambda \ge 15$ member is the R4 operating threshold, armed from $t = 0$, with no warm-up, on a
different stream family (finding D-8). The conclusion is unchanged — the admissible set is empty
under either calibration and the gap widens from $2.6$ to $4.5$ at parity.

**M2 — the Hydra factor carries its interval and its qualifier on all three announcing sites.**
Abstract (L41), Hydra section (L150) and the $K_{\mathrm{ARF}}$ remark (L227) now read *at least*
$4.1$–$8.0\times$, never *from … to*. The two anchors are $4.12\times$ $[3.45, 4.96]$ and
$7.99\times$ $[6.40, 9.72]$, stated as **lower bounds**: the ARF arm is censoring-free at every
magnitude (max censored fraction $0.0000$) while the HAT arm is censored at $0$–$13\%$, so only the
numerator is truncated at $t_c = 4000$. The grid maximum $8.04\times$ at $\Delta e = 0.028$ is
reported in the same sentence.

**M3 — the ratio of medians is now tabulated in the prose.** Kaplan--Meier median ratio
$5.32\times$ at $\Delta e = 0.14$ against $3.10\times$ at $\Delta e = 0.33$, versus $7.99\times$ for
the restricted mean at the latter. The manuscript states explicitly that the claim is one about
expectations, not about the typical run.

**M4 — the parallel-chart null is stated (L152).** Tartakovsky's multichart result is already cited;
it is now used quantitatively: $M = 10$ predicts $10\times$, the measured $4.1$–$8.0\times$ sits
strictly below it, and the shortfall is attributed to positive inter-tree correlation. One sentence,
which forecloses the "you rediscovered the minimum of ten draws" objection.

Every M2/M3 figure was regenerated by `experiments/R6_hydra_factor/exp_R6_hydra_survival.py` in this
stream; outputs in `results/audit_S7/hydra_survival.{csv,tex}`.

## B3. Residues

**R-1 — the missing configuration, now run.** The manuscript (v64 L204) claims *"the single-tree HAT
stays at ${\approx}40\%$ miss under the same clock"*, i.e. $M = 1$ with MATCHED clocks
($c_{\mathrm{int}} = c_{\mathrm{ext}} = 1$). No artifact ran it: R6 is $M = 1$ with no external
detector, R7 is matched clocks at $M = 10$, R9 is $M = 1$ but mismatched ($c_{\mathrm{ext}} = 32$).
`exp_R9_generate_data.py` gained an optional external-clock argument — the same shape as R8's
`T_DRIFT` parity argument — writing to a separate file so the published $c_{\mathrm{ext}} = 32$
artifact is never overwritten. `c_ext` feeds only the external detector, so `tau_hat` is unaffected;
the early break needs both delays resolved before it can fire.

**R-3 — host and runtime become traceable.** `docs/ENVIRONMENT.md` was created and committed: host
specification, pinned package versions, the LaTeX toolchain, and a measured wall-clock table for
every stage re-executed in this stream. The manuscript sentence at L309 now points at it. The host
is confirmed to be exactly the one the manuscript names (AMD EPYC 8224P, 24 cores / 48 threads,
`MemTotal` 196 426 176 kB = 192 GB nominal); the S7 report's "48-core / 187 GB" was the same machine
counted in logical threads and GiB.

**Footnote `incremental_abrupt_balanced` ($\Delta e = -0.094$) — figure withdrawn.** The variant is
excluded from `INSECTS_VARIANTS` (`exp_R5_config.py:42-43`), so no pipeline computes it; and
`data/insects/` holds only the three evaluated variants, so it cannot be recomputed here either. Of
the two options the plan allows, recomputation is not available, so the numeral is removed. The
footnote now states the exclusion and its motive, and says explicitly that no $\Delta e$ is computed
or reported for that variant — an assertion the repository can back.

**R-1 — measured.** `python experiments/R9_mcrit/exp_R9_generate_data.py 1`, 46 s wall,
$20$ magnitudes $\times$ $100$ seeds $= 2000$ runs, output
`results/R9_mcrit/data/results_instrumented_matched_cext1_ADWIN_HAT.csv`
(`sha256 b357e2cefd491411cc9ae9d1ded33030ddfa3479dc1d315785818636db0d68c4`). `miss` is defined
exactly as in `exp_R7_compute_regime1.py` — `miss = tau_internal < tau_det`, NaN mapped to $+\infty$
— and the bands use the theoretical $\Delta e = \Phi(b/\sqrt2) - 0.5$, so they are commensurable
with R7's.

| band | $M = 1$, $c_{\mathrm{int}} = c_{\mathrm{ext}} = 1$ (R-1) | $M = 10$, matched (R7 `B_matched`) |
|------|---:|---:|
| $\Delta e \le 0.15$ | 57.3 % | — |
| $0.15 < \Delta e \le 0.35$ | 36.8 % | — |
| $\Delta e > 0.35$ | 29.6 % | — |
| $\Delta e > 0.30$ | **29.7 %** | **2.4 %** |
| full grid | **35.2 %** | 13.6 % |

The published $M{=}10$ figure reproduces exactly (2.4 % for $\Delta e > 0.30$, matching the S7
measurement). The claimed ${\approx}40\%$ for the single tree does not: the miss rate is monotone
decreasing in $\Delta e$, from 64 % at the smallest magnitude to 27--32 % across the upper half of
the grid, and never sits at 40 % in the band the sentence compares. Recorded as **D-11** and
corrected in the manuscript. **The residue is discharged by measurement, not by re-reading**, and
the argument it supports is strengthened rather than weakened: the ensemble's SNR advantage under
matched clocks is a factor $12$, not a factor $8$.


## B4. Code — the four corrections

**4a. `exp_R6_hydra_survival.py` — the two estimators are now compared at equal arms.** The table
opposed an RMST ratio carrying a bootstrap CI against a bare complete-case point estimate. The
complete-case ratio now receives the *same* paired bootstrap: same `idx` matrix, same
`N_BOOT = 10000`, same seed pairing, resampled on the seed index rather than on observations. Two
columns (`complete_case_ci_lo`, `complete_case_ci_hi`) were added to `hydra_survival.csv` and a
`$95\%$ CI` column to `hydra_survival.tex`. `np.nanpercentile` over `np.nanmean(raw[idx], axis=1)` is
used, because a complete-case resample can legitimately contain NaN.

Measured at the two manuscript anchors: complete-case $4.05\times$ $[3.40, 4.87]$ vs RMST
$4.12\times$ $[3.45, 4.96]$ at $\Delta e = 0.14$; both $7.99\times$ $[6.40, 9.72]$ at
$\Delta e = 0.33$ (that magnitude is censoring-free, so the two estimators coincide exactly — which
is itself the check that the censoring correction does nothing where there is no censoring).

**4b. `arm()` returned `time` twice.** The third element was the same array object as the first.
Removed; the two call sites and the KM loop unpack two values, and `r_mean` reads `t` directly.

**4c. `median_ratio` treated NaN as truthy.** `round(med_h / med_a, 4) if med_a else np.nan` is taken
when `med_a` is NaN (`bool(nan) is True`), silently producing NaN through a division rather than
through the guard. Replaced by `np.isfinite(med_a) and med_a > 0`.

**4d. Class audit — floating-point join keys, whole repository.** The 1-ULP defect found in S7 is a
*join-key* defect, not a one-off. Census of every `merge` / `join` / `concat(axis=1)` / `groupby` /
`reindex` / row-selection whose key is a float, across `experiments/`, `tests/` and `config/`:

| # | site | float key | operation | verdict |
|---|------|-----------|-----------|---------|
| 1 | `experiments/R6_hydra_factor/exp_R6_compute_hydra.py:37-41` | `delta_e` | two `groupby` + `pd.concat(axis=1)` **across two files** | guarded — `assert len(merged) == 20` (cardinality); both sources parquet, so float64 is exact |
| 2 | `experiments/R6_hydra_factor/exp_R6_hydra_survival.py:80-84` | `delta_e` | `np.isclose` selection across two files | guarded — tolerance join, plus a seed-pairing assertion and `assert len(grid) == 20` |
| 3 | `tests/test_S7_consistency.py:147-149` | `boundary_shift` | `merge` parquet × **CSV** | guarded — `float_precision='round_trip'` **and** `assert len(m) == len(r6) == len(r9)`. This is the site where the defect was found |
| 4 | `tests/test_S7_consistency.py:159-160` | `boundary_shift` | `merge` parquet × parquet | guarded — cardinality assertion |
| 5 | `tests/test_S7_consistency.py:170-173` | `delta_e` | `concat(axis=1)` parquet × parquet | guarded — `assert len(merged) == 20` |
| 6 | `experiments/R9_mcrit/exp_R9_compute_mcrit.py:118, 135-137` | `boundary_shift`, `delta_e_eff` | `.loc[df[col] == value]`, `value` drawn from the *same* frame | exact by construction (same object, no cross-file key). **Corrected anyway**: the read now pins `float_precision='round_trip'` per `CLAUDE.md` §3, so this frame's key matches the parquet family if it is ever joined. Verified artifact-neutral by re-running R9 and comparing the SHA-256 |
| 7 | `tests/test_R6_hydra.py:33-34` | `delta_e` | two `groupby`, **never joined** — each series is fitted independently | no key crosses a file boundary; no action |
| 8 | `experiments/R7_clock_mismatch/exp_R7_compute_regime1.py:34` | `delta_e` | single-source `groupby` | no action |
| 9 | `experiments/R2_instrumented_blind_spot/exp_R2_instrumented_blind_spot.py:110` | `boundary_shift` | single-source `groupby` | no action |
| 10 | `experiments/R6_hydra_factor/exp_R6_generate_data.py:79` | `delta_e` | single-source `groupby` | no action |
| 11 | `experiments/R1_race_condition/exp_R1_generate_data.py:136` | `lambda_val` | single-source `groupby` | no action |
| 12 | `tests/test_R7_regime1.py:18` | `delta_e` | single-source `groupby` | no action |
| 13 | `tests/test_R9_mcrit.py:19-23` | `reliability_r`, `delta_e` | row selection by `np.isclose` | tolerance selection; the values are the exact targets written by the producer. No action |
| 14 | `tests/test_R8_lambda_op.py:16` | — | column-wise max, no join | no action |
| 15 | `exp_R4_main_table.py:264-270`, `exp_R4_kswin_sweep.py:185-191` | — | `groupby('Seed')` + `merge(on='Seed')` | integer key; immune |
| 16 | `exp_R4_main_table.py:414`, `exp_R4_kswin_sweep.py:259` | — | `groupby(['Detector','Clock','Calibration'])` | str/int key; immune |
| 17 | `experiments/R5_real_world_evaluation/exp_R5_make_table2.py:35-39` | — | `groupby(['variant','pipeline','seed'])`; the four artifacts are never merged | str/str/int key; immune |
| 18 | `exp_R5_compute_{baf,insects,delta_e}.py`, `exp_R5_smoke_test.py` | — | `read_csv` of raw streams, no float join | no action |

**One correction applied (site 6); every other site already carries one of the three required
guards, or has no float key crossing a file boundary.** The class is closed: after this audit, every
cross-file float join in the repository is protected either by `float_precision='round_trip'`, by a
tolerance comparison, or by a cardinality assertion — in three cases by two of the three.

## B5. The R4 hole — closed by option A

R4's registry values lived in `simulate_stream` argument defaults and in the detector/model
factories, i.e. outside the module-level `Assign` walk of the SSOT drift guard — and R4 produces
Table I. The diff needed to close it is one token per site, so option A was taken rather than
option B. Full site table, the two new derived constants, the guard extension and the **declared
unguarded remainder** (`clock`, `delta`, `alpha`, `seed` literals, named one by one) are in
`results/audit_S7/config_matrix.md` §7 and in the `tests/test_S7_consistency.py` docstring.

The guard now walks function-argument defaults and call keywords in addition to module-level
assignments, and fails when `n_steps`, `tp`, `t_drift`, `n_models` or `threshold` is bound to a bare
literal. Only an `ast.Constant` is a violation, so `run_tau_arf(t_drift=T_DRIFT)` (R8) — a name that
resolves to a module-level constant already covered by the first walk — is not a false positive.

## B6. Bit-for-bit proof, extended past the requested perimeter

Section 6 of the plan asks for R2, R3 and R7. Because option A (§B5) touches R1, R3 and R4 sources
and because residue R-3 needs measured runtimes, the freeze was re-verified over **every stage except
R5**: R1, R2, R3, R4, R6, R7, R8, R9. Each was re-executed end to end through its
`run_experiment_R*.sh` wrapper with `PYTHONHASHSEED=0`, one stage at a time.

**Result: 33 of the 34 baseline hashes are byte-identical.** The one deviation is
`results/audit_S7/hydra_survival.csv`, the declared §4a change, recorded in
`results/audit_S7/_baseline/authorized_deviations.txt`. `git status` shows no churn anywhere else
under `results/` — including the eight committed PNG figures, which regenerate byte-for-byte.

This converts the S7 static AST oracle into an empirical proof over the whole refactored perimeter,
and it settles three questions that the static argument could only assert:

1. **Option A is value-preserving.** R1, R3 and R4 had their `n_models` / `threshold` / `n_steps` /
   `tp` literals routed to the SSOT, and all three reproduce bit-for-bit. R4 in particular — the
   stage that produces Table I, and the whole motive for closing the hole — is identical across its
   four CSVs and its generated `.tex`.
2. **The §4d `float_precision='round_trip'` correction to `exp_R9_compute_mcrit.py` is
   artifact-neutral.** `exp_R9_mcrit_comparison.csv` is unchanged, so pinning the reader's precision
   removed a latent join-key defect without moving a single published value.
3. **The §4a/4b/4c rewrite of `exp_R6_hydra_survival.py` changed nothing it should not have.**
   Column-wise diff against the pre-S7-bis output: two columns added, **0 of the 17 pre-existing
   columns differ on any of the 20 rows**.

Wall-clock cost of the proof, and the per-stage table, are in `docs/ENVIRONMENT.md`.

**R5 was not re-executed** and its runtime is therefore unmeasured; its artifacts are untouched and
its numerals were reconciled in the S7 report above. This is stated as a residual, not hidden.

## B7. Hygiene, and the LaTeX compile that is now a compile

**Compiled bytecode.** `experiments/R5_real_world_evaluation/__pycache__/exp_R5_common.cpython-312.pyc`
was tracked. `git rm --cached` removed it from the index. `.gitignore` already carried
`__pycache__/` and `*.pyc`, so no rule was added — the file predated them. The regression is now
tested: `tests/test_S7_consistency.py::test_no_compiled_bytecode_tracked` runs `git ls-files` and
fails on any `.pyc` or `__pycache__/` path. It failed against the tracked file before the removal and
passes after, so it is not a test that can only pass.

**LaTeX.** Item 7 of the S7 phase-5 gate was a brace-balance check, because no TeX toolchain existed
on the host. Tectonic 0.17.0 was installed from `conda-forge` into a dedicated `tex` environment
(never into the pinned `Trading` environment, whose solve is already constrained). The manuscript of
record now **compiles**.

```
$ conda run -n tex tectonic -X compile docs/manuscript/articleA_blindspot_v64_camera_ready.tex
Output written on articleA_blindspot_v64_camera_ready.xdv (11 pages)
Writing articleA_blindspot_v64_camera_ready.pdf (1.53 MiB)
```

| check | result |
|-------|--------|
| TeX errors (`!`) | **0** |
| Overfull boxes | **0** |
| Undefined references / citations | **0** |
| Pages | 11 |
| BibTeX warnings | 1 — `empty booktitle in hopcroft_karp_1973`, pre-existing, not introduced here |
| Font warnings | 4 — `TU/ptm/...` undefined; XeTeX substituting for the Type 1 Times faces, a toolchain artefact |

Underfull-hbox warnings (9) are typographic, not structural. The committed camera-ready PDF was
**not** overwritten: a XeTeX build with substituted fonts is a compile proof, not a camera-ready
replacement. Item 7 of the S7 gate is now a compile; the brace-balance check it replaced is
superseded.

## B8. Exit gate — the four S7 criteria

Stated first, in the plan's own words, with the state of each. This is the stream's exit gate, not
the phase-5 checklist.

| # | criterion | state | evidence |
|---|-----------|-------|----------|
| 1 | zero untraceable value | **met** | The three S7 residues are discharged: R-1 by a new 2000-run measurement (§B3), R-2 by reclassification to D-10 and correction (§B1), R-3 by `docs/ENVIRONMENT.md` plus the D-12 correction of the runtime claim. The `incremental_abrupt_balanced` footnote figure is withdrawn — the variant is excluded from `INSECTS_VARIANTS` and its stream is not in `data/insects/`, so it cannot be computed, and the manuscript now says so instead of quoting $-0.094$. Every numeral introduced by S7-bis was measured in S7-bis and carries its source file in the tables above |
| 2 | zero manuscript / artifact / test divergence | **met** | D-1 … D-10 applied to v64, each line-anchored and asserted unique; D-11 and D-12, found by S7-bis itself, applied likewise. Every value re-measured on the restored artifacts. `pytest tests/` → 9 passed, 0 skipped |
| 3 | old and new Hydra factor both reported | **met** | `results/audit_S7/hydra_survival.{csv,tex}` tabulate the published complete-case ratio and the censoring-aware RMST ratio side by side, both now with a seed-paired bootstrap CI (§4a). The manuscript carries the new figures as lower bounds with their intervals on all three announcing sites, plus the median ratio (M3) |
| 4 | single reliability convention across the three supports | **met** | `.tex`: one surviving `\beta`, L323, the GARCH persistence parameter. Code: `R9_RELIABILITY_TARGETS`, artifact column `reliability_r`; every remaining `beta` in the tree is a GARCH parameter of the ProteuS generator. `README.md`: no `beta`. `tests/test_R9_mcrit.py` targets `reliability_r == 0.95` |

### Residual risks, stated rather than annexed

1. **R5 was not re-executed.** Its artifacts are untouched and its numerals were reconciled in S7,
   but its bit-reproducibility after the SSOT refactor rests on the static AST oracle, not on
   execution — R5 is the one stage of nine without an empirical freeze. Its runtime is likewise
   unmeasured, which is why the manuscript no longer asserts a full-pipeline total.
2. **The committed camera-ready PDF is now stale** with respect to the edited `.tex`. It was not
   regenerated: Tectonic runs XeTeX and substitutes for the Type 1 `ptm` faces, so its output is a
   compile proof, not a drop-in replacement for a pdfTeX camera-ready. Regenerating the PDF needs a
   pdfTeX toolchain and is an authoring decision, not an audit action.
3. **`hopcroft_karp_1973` has an empty `booktitle`** in `articleA_biblio_v64.bib` — the single
   BibTeX warning of the compile. Pre-existing, not introduced here, not corrected (touching the
   `.bib` would move the rendered bibliography).
4. **The declared unguarded perimeter** of the AST gate (`clock`, `delta`, `alpha`, `seed` literals)
   is named in `config_matrix.md` §7 and in the test docstring. It is a deliberate scope boundary,
   not an oversight.
5. **The warm-up parity defect is now written into the paper rather than resolved.** M1 states both
   ceilings with their warm-up and names the stream-family mismatch; standardising the paper on one
   warm-up remains a Section III-E authoring decision.
