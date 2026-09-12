# CLAUDE.md — repository conventions

## Manuscript of record

**`docs/manuscript/articleA_blindspot_v64_camera_ready.tex`** (bibliography
`docs/manuscript/articleA_biblio_v64.bib`) is the living manuscript of record. Every
reconciliation against `results/`, every numeral correction, and every compile check
targets this file and no other.

`docs/manuscript/articleA_blindspot_v63_camera_ready.tex` is **archived**: retained for
lineage only. It is not edited, not compiled and not cited by any audit artifact. Line
numbers quoted in reports predating stream S7-bis refer to v63 and do not transfer to
v64 (the theory rewrite of Section III shifts every line after 164 by +3); re-grep
before anchoring an edit.

## Execution

- Interpreter: `/home/m53/miniforge3/envs/Trading/bin/python` (Python 3.12.9).
- Every experiment runs with `PYTHONHASHSEED=0`; the `run_experiment_R*.sh` wrappers set it.
- Host specification, package pins and measured wall-clock times: `docs/ENVIRONMENT.md`.

## Write perimeter

Action A3 settles this, and it is settled for every later stream: the agent has full write
authority over every file of this repository without exception — `run_all.sh`, the
`run_experiment_R*.sh` wrappers, `README.md`, `config/`, `tests/`, `docs/` — whenever coherence
with the active specification requires it. No file is immutable by category.

The reason is empirical. Actions A1 and A2 each found a file left stale precisely because it was
treated as untouchable or simply unowned: `README.md` still described R8 as a `lambda_op`
calibration three streams after the manuscript withdrew the estimator, and
`docs/manuscript/figures/Fig_R1_race_condition.png` had drifted from its pipeline render without
any run reproducing it. Immutability did not protect those files, it exempted them from
reconciliation.

Integrity is carried by the test suite and by traced baseline deviations, not by immutability.
Every change to an artifact under `results/` is declared in
`results/audit_S7/_baseline/authorized_deviations.txt` with its motive and measured effect, and
`sha256sum -c` against the frozen reference is the acceptance gate.

## Invariants

- `config/experiment_ssot.py` is the single source of truth for experimental constants.
  A registry constant re-bound to a local literal is a regression; `tests/test_S7_consistency.py`
  fails on it without importing any experiment.
- Artifacts under `results/` are bit-reproducible. `results/audit_S7/_baseline/artifacts_sha256_pre_ssot.txt`
  is the frozen reference; a re-run that changes a hash is a defect, not an update.
- Tabular ingestion of a float join key uses `float_precision='round_trip'`. The default
  pandas C parser loses 1 ULP and silently drops join rows.
- No `.pyc` and no `logs/` content is tracked; `tests/test_S7_consistency.py` enforces the former.
