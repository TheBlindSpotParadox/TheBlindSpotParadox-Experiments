# Transfer document — stream S1 (formal framework)

## Faults addressed

- F6 (adaptation metric): `tau_erase` replaces the first swap; `tau_swap^(1/M)` retained as a measured lower bound with ratio `kappa`.
- F9 (incoherent cross-family condition): removed. Detectors are reparameterised by the windowed false-alarm level `alpha`; the family split is derived as `cor:split`.
- F14 (operational semantics): drift state unobservable, error observable under a label protocol; label-clock invariance lemma proved.
- F24 (implicit independence): not addressed here. `prop:starvation_boundary` and `cor:mcrit` are marked void pending stream S3.

## Exit gate

- `R` instantiated for CUSUM, ADWIN, KSWIN with no implementation parameter. EDDM NOT delivered — see open item 1.
- Every quantity measurable on existing artifacts (R1, R2, R6, R8) or on S6 deliverables.
- Competing branch instantiated and arbitrated: keeping `tau_swap^(1/M)` was rejected on validity, keeping `tau_erase` alone rejected on risk; the two-level construction with a measured `kappa` was retained.

## Verified numerical results

Settings `p_0 = 0.05`, `eps = 0.05`. **Restated at `delta_P = 0.01` by action A1** (StrictCUSUM
tolerance; see open item 2). The 0.005 column is retained as the superseded value, not as an
alternative: every line below is a property of the fixed-`p_0` CUSUM of `eq:cusum`, whose tolerance
is now `CUSUM_DELTA_P`. Cramer root from `E[exp(theta (X - p_0 - delta_P))] = 1`, `X ~ Bern(p_0)`;
`ARL_0` from Siegmund (1985), `(exp(theta* lambda) - theta* lambda - 1) / (theta* delta_P)`. The
0.005 column reproduces exactly under that pair, which is what licenses the 0.01 column.

**RETIRED BY S2.** The two `p_0 = 0.05` columns are superseded: the base rate is measured at
`0.024` and the assumed value is not an alternative setting but an error. The approximation row
is removed — `2 delta_P / (p_0(1-p_0))` degrades +6.2 % -> +12.1 % -> +25.3 % across the three
settings and reaches +39.8 % at the lower end of the measured band, and only the numerical root is
carried forward. The single live column, independently reproduced with a committed script
(`experiments/S2_theory/s2_arl0.py`, rule R1(a) REPRODUCED, relative error 1.4e-5 on `theta*`):

| quantity | **`p_0 = 0.024`, `delta_P = 0.01` (live)** |
|---|---|
| Cramer root `theta*` | **0.681291** |
| `ARL_0` at `lambda = 8` | **3.32e4** |
| `ARL_0` at `lambda = 15` | **4.02e6** |
| `ARL_0` at `lambda = 25` | **3.66e9** |
| `ARL_0` at `lambda = 50` | **9.13e16** |

`ARL_0` is not a determined quantity at this dispersion. Over the central 95 % of the measured
per-run pre-drift rate, `p_true in [0.015, 0.032]`, `ARL_0` at `lambda = 50` spans `1.10e14` to
`1.10e23`. No statement whose conclusion depends on its size may be evaluated at a scalar; see
`transfer_S2.md` section 3. The retired columns and the full band are tabulated in
`results/S2_theory/tables/s2_arl0_columns.csv` and read in
`docs/theory/S2_arl0_recomputation.md`.

**`p_0 = 0.05` IS NOT MEASURED, AND THE MEASUREMENT CONTRADICTS IT (item M3).** Action A1 corrected
`delta_P` while leaving `p_0` at the assumed 0.05. The S6 campaign measures the pre-drift error rate
over 2,000 runs of the nominal arm at **median 0.0240**, mean 0.0239, range [0.012, 0.040]
(`results/S6_synchronized_traces/data/runs.parquet`, column `e_pre`); `S6_causal_evidence.md`
section 8 point 4 records the same. The third column above is therefore not an alternative but the
correction still owed: at the measured base rate `theta*` nearly doubles again and `ARL_0` at
`lambda = 50` gains six further orders of magnitude. **The first two columns are wrong by a factor
larger than the one A1 fixed.**

It is given here so that S2 does not have to rediscover the formula, not as an arbitration. Two
questions stay open and belong to S2, not to this note:

1. Whether a single pooled `p_0` is admissible at all. `e_pre` spans [0.012, 0.040] across the
   magnitude grid — a factor of 3.3 — because a far-shifted boundary makes the classes more
   separable (`S6_causal_evidence.md` L94). A per-magnitude `p_0`, or an interval, may be the
   honest object.
2. Whether `eps = 0.05` survives the same scrutiny. It was never measured either.

NOT RECOMPUTED, blocking for S2 — each of the three lines below is stated in terms of the
rectangular surrogate `A = q(tau_ARF) (Delta_e - delta_P)`, which the manuscript withdraws at
`articleA_blindspot_v64_camera_ready.tex` L385. Recomputing them at 0.01 would re-endorse a
withdrawn estimator; they are to be restated against the measured evidence ceiling `A_swap`
(`results/S6_synchronized_traces/envelope_stats.json`), not merely re-evaluated:

- Budget invariance with `K = 18.5`, `alpha_exp = 0.98`: `A` in [16.8, 18.1] for `Delta_e` in [0.10, 0.50] — at 0.01 the same surrogate gives [15.9, 17.9], stated for completeness only.
- `lambda_starve` at the mean window: 43.7 at `Delta_e = 0.10`, monotone down to 29.0 at `Delta_e = 0.50`.
- Universal floor at `Delta_e = 0.33`, `W = 55`, `alpha = W/ARL_0`: 1.45 against a budget of 17.8; at `Delta_e = 0.10`, `W = 13`: 4.56 against a budget of 1.24 — budget below floor. Both consume `ARL_0`, which moves by three orders of magnitude above.

**RESTITUTION BY S2 (T2.0(d)).** The three lines above are superseded; they are kept verbatim as
the claim under audit, not as live values.

1. *Budget invariance.* Restated on the measured threshold-free ceiling `max_t A_unrefl` instead
   of the withdrawn surrogate: **19.24 to 36.60** over the canonical grid points in
   `[0.10, 0.50]`, a factor **1.90**, peaking at `Delta_e = 0.1936` and declining thereafter. The
   claimed plateau is a broad hump, and the constant exceeds `[16.8, 18.1]` at every magnitude of
   the envelope.
2. *`lambda_starve`.* Restated at `delta_P = 0.01` with `W` taken per magnitude from the S6
   campaign rather than from R8's `tau_ARF`: 29.5 at `Delta_e = 0.028`, rising to **87.5** at
   0.141, descending to 25.2 at 0.498 under the first-swap window — **not monotone**, because
   weak-band swaps are noise-driven and `W` is largest exactly where `mu` is smallest. Under
   either erasure window the boundary sits at 199–267 across the mid-band. `p_0` does not enter
   `eq:starve_boundary` except through `s_0`, which both S1 and S2 evaluate at 0, so the move is
   attributable to `W` and `delta_P` alone.
3. *Universal floor.* **Line 1 reproduces**: 1.450 against 1.45, which identifies the inputs this
   line never declares (`p_0 = 0.05`, `delta_P = 0.005`, `eps = 0.05`, `lambda = 50`,
   `Delta_max = Delta_e`). **Line 2 does NOT reproduce**: under those same inputs
   `Delta_e = 0.10`, `W = 13` returns **6.277**, not 4.56; no `lambda` on the ladder returns 4.56,
   and recovering it would require `Delta_max = 0.137` or `p_0 = 0.0359`. Verdict R1(b):
   **UNREPRODUCED** (`transfer_S2.md` section 2). Recomputed at the measured inputs the floor
   *rises* — `alpha = W/ARL_0` collapses faster than `p_0(1-p_0)` shrinks — and S2 further
   replaces the `chi^2` step of `thm:floor` by a chord bound, which tightens it by `6.74x` to a
   band of **[13.9, 18.3]** at the canonical point.

## Open items

1. ~~`R_EDDM` unresolved~~ **CLOSED by S2: withdrawn under rule R5.** The running-maximum
   dynamics were modelled (`experiments/S2_theory/s2_eddm.py`): EDDM's level is a ratio of the
   cumulative mean and standard deviation of inter-error distances to the running maximum of that
   same path, and the closed form gives `W_EDDM = (n_0/p_1) f*/(1-f*)` post-change steps, growing
   with the pre-change error count `n_0` — a term the normal approximation does not contain. It
   does not reproduce the collapse: at the ProteuS pre-change history it returns 168–281 steps
   against the approximation's 155, the same order of magnitude rather than "no detection", and it
   cannot be evaluated where the collapse is measured because R4's artifacts record `F1`, `ADD` and
   seed but no error stream. On the one stream where the inputs exist, the S6 traces, the detector
   has not completed its 30-error warm start at `tau*` in 95 % of runs and the three adaptive arms
   return the same alarm rate to within 0.08 — a statistic that cannot separate `full` from
   `frozen` is not reporting on drift. Withdrawal is R5's default outcome and it stands. The
   **empirical** EDDM result (0 detections in 1,080 runs against 882 for EDDM+HT) is untouched.
2. ~~`delta_P` discrepancy~~ **CLOSED by A1.** Not one contested value but one registry name,
   `DELTA_P`, covering two detector families that the manuscript already states separately:
   the fixed-`p_0` StrictCUSUM of `eq:cusum` at `\DeltaPtext = 0.01` (L277) and River's
   adaptive mean-tracking PageHinkley at 0.005 (L480, named there as explicitly distinct).
   `config/experiment_ssot.py` now carries `CUSUM_DELTA_P = 0.01` (R1, R2, R9, S6 audit) and
   `DELTA_P = 0.005` (R3, R4, R5). R1 and R9 were on the wrong one and are regenerated;
   R3/R4/R5 were correct and are untouched. The quantified consequence — factor 1.89 on
   `theta*`, 3.3 orders of magnitude on `ARL_0` at `lambda = 50` — is confirmed and tabulated
   above. `R8_DELTA_P` was frozen at 0.005 pending action A2 and is now **removed**: R8 simulates
   no CUSUM, and the tolerance had exactly one consumer, the withdrawn rectangular surrogate.
3. ~~Assumption `ass:repair` (no recovery without replacement) is refutable and unverified~~
   **CLOSED by A7: refuted and withdrawn.** Tested on the committed S6 traces
   (`experiments/S6_synchronized_traces/s6_audit_ass_repair.py`, 100 seeds x 20 magnitudes of
   the nominal arm, `delta_P = 0.01`). The pointwise statement holds in 31.0 % of 2,000 runs
   under a cumulative mean from `tau*`, 83.1 % under a 20-step trailing mean, and is not
   evaluable at all on the 89.7 % of intervals shorter than the 200-step window `bar_e_t`
   denotes. The prediction this item anticipated — that transient data-driven recovery falsifies
   it — is exactly what happens.
   The ordering it supported survives without it: `tau_err` quantifies over all `s >= t`, so a
   transient dip does not move `tau_erase`, and `tau_erase >= tau_swap^(1/M)` holds in
   1,835/1,836 estimable runs. `prop:order` is restated on that measured fact and the assumption
   is removed from `framework_v2.tex`. The converse half of the ordering,
   `tau_erase <= tau_swap^(1)`, never followed from the assumption and is withdrawn on its own
   evidence: 55.3 % where defined, with `tau_swap^(1)` undefined in 11.3 % of runs. `def:kappa`
   no longer asserts `kappa >= 1` inside the definition; it is measured at 1,835/1,836.
4. ~~`W` treated as deterministic throughout~~ **CLOSED by S2 (T2.2).** Eq. (4) is restated as
   `E_W[min(1, W exp(-2/W (lambda - s_0 - mu W)_+^2))]` over the empirical law of `W` per
   magnitude, with right censoring at `T_h = 2500` handled explicitly and the log-normal AFT of
   `s6_predictive_power.py` reused rather than a new dependency added. The outcome is not a
   repair: the bound is **vacant at every magnitude and every `lambda in {8,15,25,50}`** under both
   the deterministic-`W` and the plug-in readings, and the parametric reading's best value over the
   whole grid is 0.753. A censored run contributes exactly 1 to the capped integrand, so the bound
   is at least the censoring fraction (8.21 % on the 1,974-run complete case) before the drift
   magnitude is consulted. Eq. (4) is retained, restricted to `{(W, lambda) : mu W < lambda}` and
   demoted to a scope statement; `prop:certificate` is the load-bearing claim
   (`docs/manuscript/sections/prop3_v2.tex`).

## Blocking gate for stream S6

Measure `kappa = (tau_erase - tau*) / (tau_swap^(1/M) - tau*)` at `Delta_e = 0.33`, `M = 10`, `c_int = 1`.

- Maximum admissible window preserving the `lambda = 50` starvation certificate: `W* = 95` steps.
- Mean first swap: 54.8 steps. Critical ratio `kappa* = 1.73` on the mean, 3.18 on the `q05 = 30` basis.
- `kappa > kappa*` falsifies the starvation certificate at the claimed operating point.

S6 must also deliver, per magnitude and per seed: the trajectory `bar_e_t` over `[tau*, tau* + 3 W]`, the swap counter `N_swap(t)`, and the external detector statistic `S_t` on a shared timeline. Reviewers #1 and #4 both demand exactly these synchronised trajectories.

## Deliverables

- `docs/manuscript/sections/framework_v2.tex`
- `docs/theory/notation_map_v63_to_v2.md`
- `docs/theory/transfer_S1.md`

## State

Stream S1 complete. **Stream S2 complete**; its state transfer is `docs/theory/transfer_S2.md`,
which supersedes the retired columns and the three restituted lines above. Open items 1 and 4 are
closed there; items 2 and 3 were already closed by A1 and A7.