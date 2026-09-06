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

Settings `p_0 = 0.05`, `delta_P = 0.005`, `eps = 0.05`.

- CUSUM Cramer root `theta* = 0.1983`; approximation `2 delta_P / (p_0(1-p_0))` accurate to 6 %.
- `ARL_0`: 2.3e3 at `lambda = 8`; 1.4e5 at `lambda = 25`; 2.0e7 at `lambda = 50`.
- Budget invariance with `K = 18.5`, `alpha_exp = 0.98`: `A` in [16.8, 18.1] for `Delta_e` in [0.10, 0.50].
- `lambda_starve` at the mean window: 43.7 at `Delta_e = 0.10`, monotone down to 29.0 at `Delta_e = 0.50`.
- Universal floor at `Delta_e = 0.33`, `W = 55`, `alpha = W/ARL_0`: 1.45 against a budget of 17.8.
- Universal floor at `Delta_e = 0.10`, `W = 13`: 4.56 against a budget of 1.24 — budget below floor.

## Open items

1. `R_EDDM` unresolved. The normal approximation on geometric inter-error distances predicts detection at `W = 155` where the experiment reports F1 = 0.00. Requires modelling of the running-maximum-with-reset dynamics. Do not publish the current form.
2. `delta_P` discrepancy: 0.005 in `exp_R8_lambda_op_sweep.py`, 0.01 in the manuscript text. Factor 2 on `theta*`, three orders of magnitude on `ARL_0` at `lambda = 50`.
3. Assumption `ass:repair` (no recovery without replacement) is refutable and unverified. Falsified by any transient recovery driven by data rather than by swaps.
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