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

## Invariants

- `config/experiment_ssot.py` is the single source of truth for experimental constants.
  A registry constant re-bound to a local literal is a regression; `tests/test_S7_consistency.py`
  fails on it without importing any experiment.
- Artifacts under `results/` are bit-reproducible. `results/audit_S7/_baseline/artifacts_sha256_pre_ssot.txt`
  is the frozen reference; a re-run that changes a hash is a defect, not an update.
- Tabular ingestion of a float join key uses `float_precision='round_trip'`. The default
  pandas C parser loses 1 ULP and silently drops join rows.
- No `.pyc` and no `logs/` content is tracked; `tests/test_S7_consistency.py` enforces the former.
