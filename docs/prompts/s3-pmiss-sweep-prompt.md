# GATED — ARF ensemble-size sweep for the `P_miss(M)` curve (stream S3, T3.5)

**Status: written, NOT executed.** This prompt exists because the two anchors `M = 1` and
`M = 10` are free — they read committed artifacts — and the five remaining points of the
`P_miss(M)` curve are not: they are a **new experiment**. The registry knows exactly two ensemble
sizes, `N_MODELS = 10` and `R6_N_MODELS = 1`; every other `M` requires a campaign that does not
exist. Per the stream S3 specification the sweep is gated on explicit validation and is not run by
this stream.

Read `docs/prompts/s3-decision-rules.md` and `docs/theory/S3_dependence_bounds.md` before running
anything below.

---

## 1. What is already closed without this sweep

`results/S3/pmiss_vs_M.csv` carries the full `M`-grid `{1, 2, 3, 5, 10, 20, 50}` with the **model**
column at every point and the **measured** column at `M = 1` (R6 `tau_HAT`) and `M = 10` (R2
scenario A `tau_ARF`). Rule D7 declares the `M = 1` anchor tautological — the model there is
`F_hat` on the same sample — so the single measured test is at `M = 10`, and it is the one that
**refutes** the `F = F_HAT` plug-in on 10 of the 80 testable cells
(`S3_dependence_bounds.md` §6).

**The sweep is therefore not needed to close T3.5**, which is declared closed at the two anchors.
It is needed to answer a different question the refutation raises: *how does the ARF member's
marginal move with `M`?* That question did not exist before the refutation.

## 2. What to run, if and only if this is validated

Reuse `experiments/R2_instrumented_blind_spot/exp_R2_instrumented_blind_spot.py` unchanged in
substance; parameterise the ensemble size instead of reading `R2_N_MODELS`.

1. **Registry first.** Add one name to `config/experiment_ssot.py`, in an append-only block:
   `S3_M_GRID = [2, 3, 5, 20, 50]`. Do **not** re-bind `N_MODELS` or `R2_N_MODELS`; do not carry
   the grid as a local literal in any script — `tests/test_S7_consistency.py` fails on that.
2. **Same everything else.** `R2_BOUNDARY_SHIFTS` (20 magnitudes), `R2_SEEDS` (1..100),
   `R2_N_STEPS = 8000`, `R2_T_DRIFT = 4000`, `R2_CUSUM_DELTA = CUSUM_DELTA_P`, `PYTHONHASHSEED=0`,
   `MPLBACKEND=Agg`. The seeds must be the **same** 100, so the new arms are seed-paired with R6
   and with R2 scenario A and the comparison stays matched.
3. **Scenario A only** (`lambda = 50`) is enough for the curve; running B and C multiplies the cost
   by three for a question the curve does not ask. `tau_arf` is threshold-free — asserted in
   `s3_bounds.demo()` — so one scenario fixes it for every `lambda`.
4. **Write to a new directory**: `results/S3/sweep/`. Nothing under `results/R2_*` moves, and
   `results/audit_S7/_baseline/authorized_deviations.txt` gains **no** entry.

```bash
PYTHONHASHSEED=0 MPLBACKEND=Agg /home/m53/miniforge3/envs/Trading/bin/python \
    experiments/S3_dependence/s3_pmiss_sweep.py           # to be written; see §2
PYTHONHASHSEED=0 /home/m53/miniforge3/envs/Trading/bin/python \
    experiments/S3_dependence/s3_bounds.py                # re-reads the sweep if present
sha256sum -c results/audit_S7/_baseline/artifacts_sha256_pre_ssot.txt
PYTHONHASHSEED=0 /home/m53/miniforge3/envs/Trading/bin/python -m pytest tests/ -q
```

## 3. Cost, measured basis

`docs/ENVIRONMENT.md` records `./run_experiment_R2.sh` at **1 186 s** for three scenarios at
`M = 10`, i.e. ≈ 395 s for one scenario. Per-step cost is close to linear in `M` (the forest loops
over members), so scenario A alone over `S3_M_GRID = [2, 3, 5, 20, 50]` costs roughly
`395 s x (2 + 3 + 5 + 20 + 50) / 10` ≈ **3 160 s ≈ 53 min** on the host of `docs/ENVIRONMENT.md`.
The `M = 50` arm alone is ≈ 33 min of that. This is an estimate from a measured baseline, not a
measurement.

## 4. Acceptance gate, fixed here and not after the run

| condition | verdict |
|---|---|
| the `M = 10` arm of the sweep reproduces `results/R2_instrumented_blind_spot/data/R2_instrumented_A_PHT_ARF.parquet` **byte for byte** on the same seeds | the harness is certified; the other arms are interpretable |
| it does not | **halt**. The sweep is measuring a different pipeline from the one the manuscript reports, and no arm of it is published |

Run the `M = 10` arm **first** and check it before spending the other 50 minutes.

Two further conditions, declared now:

- the curve is published only with the censoring fraction of each arm printed beside it; a `NaN`
  `tau_arf` is a censored adaptation, never a dropped row;
- if the measured `P_miss(M)` crosses the `min(1, M F_hat(s))` envelope at additional `M`, that is
  **more** evidence for the refutation of §6 and is reported as such. It is never used to
  re-fit `F_hat`, to re-choose `s`, or to restore `cor:mcrit`.

## 5. What this sweep cannot settle

It measures `P_miss(M)`, the probability that the ensemble minimum falls below a level. It does
**not** recover the member marginal `F`, which would require per-tree `tau_i` and is the open item
handed forward in `docs/theory/transfer_S3.md`. Fitting `F` from the `P_miss(M)` curve by inverting
`1 - (1-F)^M` would assume exactly the conditional independence that rule D1 measured to fail.
