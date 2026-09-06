# tests/test_S7_consistency.py
"""
Stream S7 consistency suite.

1. SSOT drift guard (unconditional, source-only). Walks every module-level assignment in
   `experiments/**/*.py`, resolves it without importing or executing the experiment, and fails if
   (a) a registry constant is re-bound to a local literal instead of `config.experiment_ssot`, or
   (b) any resolved value drifts from the Phase-0 oracle
   `results/audit_S7/_baseline/constants_pre.json`. This is the non-regression proof that the SSOT
   refactor changed no value, obtained without running an experiment.
2. tau_HAT is identical between R6 and R9 per (boundary_shift, seed): same M = 1, same seeds, same
   stream, two independent instrumentation scripts.
3. tau_arf is identical across the R2 scenarios A/B/C per (boundary_shift, seed): the external
   CUSUM threshold lambda does not feed back into the ARF.
4. The R6 <-> R2 Delta_e join retains its 20 magnitude points.

Assertions 2-4 read committed artifacts; each skips with an explicit motive when the artifact is
absent, so the suite is green on a fresh clone and enforcing after a full reproduction.

Usage:  PYTHONHASHSEED=0 python -m pytest tests/test_S7_consistency.py -v
"""
import ast
import builtins
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
from config import experiment_ssot as ssot  # noqa: E402

BASELINE = ROOT_DIR / "results" / "audit_S7" / "_baseline" / "constants_pre.json"

# Registry names of CONFIG §6, expanded to the local aliases the experiment scripts actually bind.
GUARDED_NAMES = {
    "N_STEPS", "T_DRIFT", "DRIFT_TIME", "TOLERANCE", "N_MODELS", "SEEDS", "N_SEEDS",
    "BOUNDARY_SHIFTS", "DELTA_E_GRID", "DELTA_E_VALUES", "C_INT", "C_EXT", "EXT_DELTA",
    "DELTA_P", "LAMBDAS", "LAMBDAS_TO_TEST", "WARMUP", "DELTA_E_WINDOW",
    "BAF_TAU_TOL", "INSECTS_TAU_CAP",
}

# The only value changes stream S7 is authorised to make. Anything else is a regression.
AUTHORIZED_DELTAS = {
    ("experiments/R1_race_condition/exp_R1_generate_data.py", "LAMBDAS_TO_TEST"):
        "S7/G2: 15 and 20 added so lambda* is measured, not interpolated across [10, 25]",
    ("experiments/R9_mcrit/exp_R9_compute_mcrit.py", "BETAS"):
        "S7/TASK 3: reliability letter beta -> r; BETAS replaced by RELIABILITY_TARGETS",
}

SAFE_BUILTINS = {n: getattr(builtins, n)
                 for n in ("list", "range", "dict", "tuple", "set", "int", "float", "str",
                           "len", "min", "max", "sorted", "sum", "abs", "round", "bool", "frozenset")}
UNRESOLVED = object()


def canon(v):
    if isinstance(v, np.ndarray):
        return repr([float(x) for x in v.ravel()])
    if isinstance(v, (np.floating, np.integer)):
        return repr(v.item())
    return repr(v)


def module_constants(path, ns_extra=None):
    """{name: {"expr": source, "value": canonical repr or None}} for every module-level Assign."""
    ns = {"np": np, "numpy": np}
    ns.update(ns_extra or {})
    out = {}

    def record(name, expr, value):
        out[name] = {"expr": expr, "value": None if value is UNRESOLVED else canon(value)}
        if value is not UNRESOLVED:
            ns[name] = value

    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        if not isinstance(node, ast.Assign):
            continue
        src = ast.unparse(node.value)
        try:
            val = eval(src, {"__builtins__": SAFE_BUILTINS}, ns)
        except Exception:
            val = UNRESOLVED
        for tgt in node.targets:
            if isinstance(tgt, ast.Tuple):
                for i, elt in enumerate(tgt.elts):
                    if not isinstance(elt, ast.Name):
                        continue
                    sub_src = (ast.unparse(node.value.elts[i])
                               if isinstance(node.value, ast.Tuple) else f"({src})[{i}]")
                    try:
                        sub = val[i] if val is not UNRESOLVED else UNRESOLVED
                    except Exception:
                        sub = UNRESOLVED
                    record(elt.id, sub_src, sub)
            elif isinstance(tgt, ast.Name):
                record(tgt.id, src, val)
    return out


def census():
    return {str(p.relative_to(ROOT_DIR)): module_constants(p, {"ssot": ssot})
            for p in sorted((ROOT_DIR / "experiments").rglob("*.py"))}


def test_ssot_registry_and_no_value_drift():
    pre = json.loads(BASELINE.read_text(encoding="utf-8"))
    post = census()

    local_literals, drift, missing = [], [], []
    for rel, names in post.items():
        for name, entry in names.items():
            if name in GUARDED_NAMES and "ssot." not in entry["expr"]:
                local_literals.append(f"{rel}:{name} = {entry['expr']}")

    for rel, names in pre.items():
        for name, entry in names.items():
            if entry["value"] is None:
                continue                                  # path / runtime object, not a constant
            if (rel, name) in AUTHORIZED_DELTAS:
                continue
            if name not in post.get(rel, {}):
                missing.append(f"{rel}:{name}")
            elif post[rel][name]["value"] != entry["value"]:
                drift.append(f"{rel}:{name}  {entry['value']}  ->  {post[rel][name]['value']}")

    assert not local_literals, "registry constants re-bound to local literals:\n  " + "\n  ".join(local_literals)
    assert not missing, "module-level constants removed without authorisation:\n  " + "\n  ".join(missing)
    assert not drift, "resolved values drifted from the Phase-0 oracle:\n  " + "\n  ".join(drift)


def _read(path, **kw):
    if not path.exists():
        pytest.skip(f"artifact absent -- run ./run_experiment_R{path.parts[-3][1]}.sh")
    return pd.read_parquet(path) if path.suffix == ".parquet" else pd.read_csv(path, **kw)


def test_tau_hat_identical_between_R6_and_R9():
    r6 = _read(ROOT_DIR / "results" / "R6_hydra_factor" / "data" / "R6_hat_instrumented.parquet")
    # float_precision='round_trip' is mandatory: the default C parser loses 1 ULP on 4 of the 20
    # boundary_shift values, which silently drops 400 of the 2000 join keys.
    r9 = _read(ROOT_DIR / "results" / "R9_mcrit" / "data" / "results_instrumented_A_ADWIN_HAT.csv",
               float_precision="round_trip")
    m = r6[["boundary_shift", "seed", "tau_hat"]].merge(
        r9[["boundary_shift", "seed", "tau_hat"]], on=["boundary_shift", "seed"], suffixes=("_r6", "_r9"))
    assert len(m) == len(r6) == len(r9), f"join lost rows: {len(m)} of {len(r6)}"
    same = (m.tau_hat_r6.isna() & m.tau_hat_r9.isna()) | (m.tau_hat_r6 == m.tau_hat_r9)
    assert same.all(), m[~same].head().to_string(index=False)


def test_tau_arf_invariant_across_R2_scenarios():
    d = ROOT_DIR / "results" / "R2_instrumented_blind_spot" / "data"
    ref = _read(d / "R2_instrumented_A_PHT_ARF.parquet")[["boundary_shift", "seed", "tau_arf"]]
    for sc in ("B", "C"):
        other = _read(d / f"R2_instrumented_{sc}_PHT_ARF.parquet")[["boundary_shift", "seed", "tau_arf"]]
        m = ref.merge(other, on=["boundary_shift", "seed"], suffixes=("_A", f"_{sc}"))
        assert len(m) == len(ref), f"scenario {sc} join lost rows"
        same = (m["tau_arf_A"].isna() & m[f"tau_arf_{sc}"].isna()) | (m["tau_arf_A"] == m[f"tau_arf_{sc}"])
        assert same.all(), f"lambda fed back into the ARF (A vs {sc}):\n" + m[~same].head().to_string(index=False)


def test_R6_R2_delta_e_join_retains_20_points():
    from scipy.stats import norm
    hat = _read(ROOT_DIR / "results" / "R6_hydra_factor" / "data" / "R6_hat_instrumented.parquet")
    arf = _read(ROOT_DIR / "results" / "R2_instrumented_blind_spot" / "data" / "R2_instrumented_A_PHT_ARF.parquet")
    arf["delta_e"] = norm.cdf(arf["boundary_shift"] / np.sqrt(2)) - 0.5
    merged = pd.concat([hat.dropna(subset=["tau_hat"]).groupby("delta_e")["tau_hat"].mean(),
                        arf.dropna(subset=["tau_arf"]).groupby("delta_e")["tau_arf"].mean()],
                       axis=1).dropna()
    assert len(merged) == 20, f"R6/R2 Delta_e join retains {len(merged)} of 20 points"
