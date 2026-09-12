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

| quantity | `delta_P = 0.005` (superseded) | `delta_P = 0.01` (A1) |
|---|---|---|
| Cramer root `theta*` | 0.1983 | 0.3755 |
| approximation `2 delta_P / (p_0(1-p_0))` | 0.2105 (+6.2 %) | 0.4211 (+12.1 %) |
| `ARL_0` at `lambda = 8` | 2.3e3 | 4.3e3 |
| `ARL_0` at `lambda = 25` | 1.4e5 | 3.2e6 |
| `ARL_0` at `lambda = 50` | 2.0e7 | 3.8e10 |

The closed-form approximation to `theta*` loses half its accuracy at the arbitrated tolerance
(6.2 % -> 12.1 %): S2 must carry the numerical root, not the approximation.

NOT RECOMPUTED, blocking for S2 — each of the three lines below is stated in terms of the
rectangular surrogate `A = q(tau_ARF) (Delta_e - delta_P)`, which the manuscript withdraws at
`articleA_blindspot_v64_camera_ready.tex` L385. Recomputing them at 0.01 would re-endorse a
withdrawn estimator; they are to be restated against the measured evidence ceiling `A_swap`
(`results/S6_synchronized_traces/envelope_stats.json`), not merely re-evaluated:

- Budget invariance with `K = 18.5`, `alpha_exp = 0.98`: `A` in [16.8, 18.1] for `Delta_e` in [0.10, 0.50] — at 0.01 the same surrogate gives [15.9, 17.9], stated for completeness only.
- `lambda_starve` at the mean window: 43.7 at `Delta_e = 0.10`, monotone down to 29.0 at `Delta_e = 0.50`.
- Universal floor at `Delta_e = 0.33`, `W = 55`, `alpha = W/ARL_0`: 1.45 against a budget of 17.8; at `Delta_e = 0.10`, `W = 13`: 4.56 against a budget of 1.24 — budget below floor. Both consume `ARL_0`, which moves by three orders of magnitude above.

## Open items

1. `R_EDDM` unresolved. The normal approximation on geometric inter-error distances predicts detection at `W = 155` where the experiment reports F1 = 0.00. Requires modelling of the running-maximum-with-reset dynamics. Do not publish the current form.
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
4. `W` treated as deterministic throughout. Must be handled as a random variable in S2, or the Proposition-9 defect is reproduced.

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

Stream S1 complete. Stream S2 not started — checkpoint pending user validation per the entry-point prompt.