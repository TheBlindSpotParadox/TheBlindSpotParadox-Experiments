# tests/test_S7_consistency.py
"""
Stream S7 consistency suite.

1. SSOT drift guard (unconditional, source-only). Walks every module-level assignment in
   `experiments/**/*.py`, resolves it without importing or executing the experiment, and fails if
   (a) a registry constant is re-bound to a local literal instead of `config.experiment_ssot`, or
   (b) any resolved value drifts from the Phase-0 oracle
   `results/audit_S7/_baseline/constants_pre.json`. This is the non-regression proof that the SSOT
   refactor changed no value, obtained without running an experiment.
   S7-bis extends (a) beyond module scope: a guarded registry name bound to a bare literal in a
   function-argument default or a call keyword now fails too -- this is what closed the R4 hole,
   whose n_steps / tp / n_models / threshold lived in `simulate_stream` defaults and in the detector
   factories. DECLARED UNGUARDED PERIMETER: the literals `clock=1` (R3), `delta=0.005` (R3),
   `delta=0.002` / `alpha=0.005` (R4) and `seed=42` (R4, R9). Their parameter names are generic
   enough that guarding them would fire on River's own API surface; they are named here rather than
   left silent, and are declared in `results/audit_S7/config_matrix.md`.
2. tau_HAT is identical between R6 and R9 per (boundary_shift, seed): same M = 1, same seeds, same
   stream, two independent instrumentation scripts.
3. tau_arf is identical across the R2 scenarios A/B/C per (boundary_shift, seed): the external
   CUSUM threshold lambda does not feed back into the ARF.
4. The R6 <-> R2 Delta_e join retains its 20 magnitude points.
5. No compiled bytecode is tracked by git (S7-bis/section 7).

Assertions 2-4 read committed artifacts; each skips with an explicit motive when the artifact is
absent, so the suite is green on a fresh clone and enforcing after a full reproduction.

Usage:  PYTHONHASHSEED=0 python -m pytest tests/test_S7_consistency.py -v
"""
import ast
import builtins
import json
import subprocess
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
    ("experiments/R1_race_condition/exp_R1_generate_data.py", "DELTA_P"):
        "A1: 0.005 -> 0.01. R1 runs StrictCUSUM, whose tolerance the manuscript states at "
        "\\DeltaPtext in Eq. (cusum) and L277. 0.005 is River's PageHinkley tolerance (R3/R4/R5, "
        ".tex L480) and was inherited from the single pre-A1 registry name",
    ("experiments/R9_mcrit/exp_R9_compute_mcrit.py", "DELTA_P"):
        "A1: 0.005 -> 0.01. tau_det* = lambda/(Delta_e - delta_P) of cor:mcrit is the Eq. (cusum) "
        "accumulation time, same StrictCUSUM family as R1 and R2",
    ("experiments/R8_lambda_op_sweep/exp_R8_lambda_op_sweep.py", "DELTA_P"):
        "A2: removed, with the registry constant R8_DELTA_P it aliased. R8 simulates no CUSUM and "
        "accumulates nothing; the tolerance had exactly one consumer, the rectangular surrogate "
        "q05(tau_ARF)*(Delta_e - delta_P) withdrawn at .tex L385 and purged from the artifacts",
}

# Registry names carried in function-argument defaults or call keywords instead of at module level
# (S7-bis/section 5, option A). Only a bare literal is a violation: a Name/Attribute default resolves
# to a module-level constant, which the module-level walk already guards.
GUARDED_PARAMS = {"n_steps", "tp", "t_drift", "n_models", "threshold"}

# Action A1. StrictCUSUM is the fixed-p_0 accumulator of eq:cusum; its tolerance is
# CUSUM_DELTA_P = 0.01 (.tex L277), never the River PageHinkley tolerance DELTA_P = 0.005
# (.tex L480). Both lived under one registry name until A1, and neither offending site was
# reachable by the guards above: R1 inherited the wrong value through a correctly-routed alias,
# and R2 carried a bare 0.01 as a call keyword whose parameter name `delta` cannot join
# GUARDED_PARAMS without firing on River's own ADWIN/PageHinkley surface. This guard is therefore
# scoped to the class rather than to the parameter name, and resolves the argument through the
# class's own __init__ signature so a positional delta is caught as readily as a keyword.
CUSUM_CLASS = "StrictCUSUM"
CUSUM_DELTA_EXEMPT = {
    "experiments/S6_synchronized_traces/s6_detectors.py":
        "the committed S6 campaign traces were accumulated at DELTA_P = 0.005, which is a recorded "
        "property of the Parquet corpus and not a live choice; s6_recompute_cusum_delta001.py "
        "re-accumulates them at CUSUM_DELTA_P post hoc, and every published S6 numeral comes from "
        "that audit path",
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


def param_literals(path):
    """Guarded registry names still bound to a bare literal in an argument default or call keyword."""
    out = []
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Call):
            out += [f"{ast.unparse(node.func)}({kw.arg}={ast.unparse(kw.value)})"
                    for kw in node.keywords
                    if kw.arg in GUARDED_PARAMS and isinstance(kw.value, ast.Constant)]
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            a = node.args
            pos = a.posonlyargs + a.args
            pairs = list(zip(pos[len(pos) - len(a.defaults):], a.defaults))
            pairs += [(k, d) for k, d in zip(a.kwonlyargs, a.kw_defaults) if d is not None]
            out += [f"def {node.name}({arg.arg}={ast.unparse(d)})"
                    for arg, d in pairs
                    if arg.arg in GUARDED_PARAMS and isinstance(d, ast.Constant)]
    return out


def module_namespace(path):
    """The module-level constants of `path` as live values, for evaluating an expression in context."""
    ns = {"np": np, "ssot": ssot}
    for name, entry in module_constants(path, {"ssot": ssot}).items():
        if entry["value"] is None:
            continue
        try:
            ns[name] = ast.literal_eval(entry["value"])
        except Exception:
            pass
    return ns


def cusum_delta_sites(path):
    """[(site, resolved delta or UNRESOLVED)] for every StrictCUSUM construction in `path`."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    idx = default = None
    for node in ast.walk(tree):
        if not (isinstance(node, ast.ClassDef) and node.name == CUSUM_CLASS):
            continue
        init = next((n for n in node.body
                     if isinstance(n, ast.FunctionDef) and n.name == "__init__"), None)
        params = [a.arg for a in init.args.posonlyargs + init.args.args][1:] if init else []
        if "delta" not in params:
            continue
        idx = params.index("delta")
        first_default = len(params) - len(init.args.defaults)
        default = init.args.defaults[idx - first_default] if idx >= first_default else None

    out, ns = [], None
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == CUSUM_CLASS):
            continue
        arg = next((k.value for k in node.keywords if k.arg == "delta"), None)
        if arg is None and idx is not None and idx < len(node.args):
            arg = node.args[idx]
        if arg is None:
            arg = default
        if arg is None:
            out.append((f"{CUSUM_CLASS}(...)  [no delta argument and no resolvable signature]",
                        UNRESOLVED))
            continue
        src = ast.unparse(arg)
        ns = module_namespace(path) if ns is None else ns
        try:
            out.append((f"{CUSUM_CLASS}(... delta={src})",
                        eval(src, {"__builtins__": SAFE_BUILTINS}, ns)))
        except Exception:
            out.append((f"{CUSUM_CLASS}(... delta={src})", UNRESOLVED))
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
        local_literals += [f"{rel}:{hit}" for hit in param_literals(ROOT_DIR / rel)]

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


def test_strict_cusum_runs_at_the_cusum_tolerance():
    bad, checked = [], 0
    for p in sorted((ROOT_DIR / "experiments").rglob("*.py")):
        rel = str(p.relative_to(ROOT_DIR))
        if rel in CUSUM_DELTA_EXEMPT:
            continue
        for site, delta in cusum_delta_sites(p):
            checked += 1
            if delta is UNRESOLVED:
                bad.append(f"{rel}: {site} -- extend the guard, do not silence it")
            elif delta != ssot.CUSUM_DELTA_P:
                bad.append(f"{rel}: {site} -> {delta}, expected CUSUM_DELTA_P = {ssot.CUSUM_DELTA_P}")

    assert checked >= 3, (
        f"guard inspected {checked} StrictCUSUM constructions, expected at least the three of R1 "
        f"(x2) and R2. The class was renamed or moved: re-point CUSUM_CLASS rather than leave a "
        f"guard that verifies nothing.")
    assert not bad, ("StrictCUSUM constructed at a tolerance other than the registry's "
                     "CUSUM_DELTA_P:\n  " + "\n  ".join(bad))


def test_no_compiled_bytecode_tracked():
    r = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT_DIR, capture_output=True, text=True)
    if r.returncode != 0:
        pytest.skip("not a git working tree")
    tracked = [f for f in r.stdout.split("\0")
               if f.endswith(".pyc") or f.startswith("__pycache__/") or "/__pycache__/" in f]
    assert not tracked, "compiled bytecode tracked by git:\n  " + "\n  ".join(tracked)


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


def test_S6_phase0_gates_all_pass():
    """Stream S6 Phase-0 gates G0..G3 are committed artifacts with a PASS verdict.

    The gates license the S6 harness: G0 that predict_one() is RNG-neutral, G1 that a deepcopy fork
    is faithful, G2 that the private River surface the harness reads exists on the pinned build, G3
    that the campaign is affordable. A gate that stops passing invalidates the harness, so the
    verdict is asserted here rather than left in a JSON nobody re-reads."""
    gates = ROOT_DIR / "experiments" / "S6_synchronized_traces" / "gates"
    expected = {"g0_report.json": "G0", "g1_report.json": "G1",
                "g2_api_map.json": "G2", "g3_report.json": "G3"}
    missing = [n for n in expected if not (gates / n).exists()]
    assert not missing, ("Phase-0 gate reports absent: " + ", ".join(missing) +
                         " -- run experiments/S6_synchronized_traces/gates/g*.py")
    failed = []
    for name, gate in expected.items():
        payload = json.loads((gates / name).read_text(encoding="utf-8"))
        assert payload["gate"] == gate, f"{name} carries gate {payload['gate']}, expected {gate}"
        if payload["verdict"] != "PASS":
            failed.append(f"{gate} ({name}): {payload['verdict']}")
    assert not failed, "Phase-0 gates not passing:\n  " + "\n  ".join(failed)
    assert not json.loads((gates / "g2_api_map.json").read_text(encoding="utf-8"))["missing_attributes"]


# ══════════════════════════════════════════════════════════════════════════════════════════════
# S7-ter / D-4 — float round-trip guard on every CSV ingestion
# ══════════════════════════════════════════════════════════════════════════════════════════════
# The hazard this closes is a FUTURE read_csv, not a present one. Measured census at the time of
# writing: 6 `.merge`/`.join` call sites in the repository, 4 of them on a float key, and exactly
# one of those reading a CSV (test_tau_hat_identical_between_R6_and_R9 above), already hardened and
# regression-locked by its `len(m) == len(r6) == len(r9)` assertion. The other three joins are
# parquet-only, hence binary, hence immune. The specification's figure of "18 float joins" is not
# reproducible by any grep attempted and its methodology is stated nowhere; it is recorded here as
# UNRECONCILED rather than silently adopted or silently dropped.
#
# Rule: every pandas read_csv under experiments/ and tests/ carries float_precision='round_trip',
# or is declared below with a motive. Same "option B applied to the remainder, not silence" pattern
# the SSOT guard above uses for its unguarded perimeter.
# Exemptions are keyed by `file:enclosing function`, not by line: a line key is invalidated by any
# edit above the call, which fired twice in one stream on nothing but docstring edits. The function
# name is stable under reformatting and still names one site precisely, and the staleness assertion
# below fails loudly if a declared site stops existing.
READ_CSV_ROOTS = ("experiments", "tests")
ROUND_TRIP = "round_trip"

_RAW_SOURCE = ("raw benchmark source, ingested once and never joined -- no .merge/.join anywhere "
               "in this file; the float columns are features, not keys")
_FORWARDER = ("kwargs-forwarding dispatch helper: the keyword is supplied by the caller, which a "
              "static walk cannot resolve. Every CSV call site in this file passes it")

READ_CSV_EXEMPTIONS = {
    "experiments/R5_real_world_evaluation/exp_R5_compute_baf.py:simulate": _RAW_SOURCE,
    "experiments/R5_real_world_evaluation/exp_R5_compute_delta_e.py:error_stream_baf": _RAW_SOURCE,
    "experiments/R5_real_world_evaluation/exp_R5_compute_delta_e.py:error_stream_insects": _RAW_SOURCE,
    "experiments/R5_real_world_evaluation/exp_R5_compute_insects.py:simulate": _RAW_SOURCE,
    "experiments/R5_real_world_evaluation/exp_R5_smoke_test.py:smoke_baf": _RAW_SOURCE,
    "experiments/R5_real_world_evaluation/exp_R5_smoke_test.py:smoke_insects": _RAW_SOURCE,
    "tests/test_R8_lambda_op.py:test_withdrawn_surrogate_is_absent_from_the_artifacts":
        "nrows=0: reads the header row only, parses no float at all",
    "tests/test_S7_consistency.py:_read": _FORWARDER,
    "tests/test_R1_race_condition.py:_read": _FORWARDER,
    "tests/test_R2_starvation.py:_read": _FORWARDER,
    "tests/test_R3_crossover.py:_read": _FORWARDER,
    "tests/test_R4_table1.py:_read": _FORWARDER,
    "tests/test_R5_table2.py:_read": _FORWARDER,
}


def read_csv_sites(path):
    """[(enclosing function name, lineno, round_trips)] for every pandas read_csv call in `path`."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    scopes = [(n.lineno, n.end_lineno, n.name) for n in ast.walk(tree)
              if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", None)
        if name != "read_csv":
            continue
        enclosing = [s for s in scopes if s[0] <= node.lineno <= s[1]]
        # innermost wins: the narrowest span containing the call
        scope = min(enclosing, key=lambda s: s[1] - s[0])[2] if enclosing else "<module>"
        kw = next((k.value for k in node.keywords if k.arg == "float_precision"), None)
        out.append((scope, node.lineno,
                    isinstance(kw, ast.Constant) and kw.value == ROUND_TRIP))
    return out


def test_every_csv_ingestion_round_trips_its_floats():
    """The default pandas C parser loses 1 ULP on a float key and silently drops the join rows.

    It cost 400 of 2000 rows on the R6/R9 boundary_shift join before the keyword was added there.
    A bare read_csv is therefore a defect waiting for its first merge, and this walks for it."""
    bad, seen = [], set()
    for root in READ_CSV_ROOTS:
        for p in sorted((ROOT_DIR / root).rglob("*.py")):
            rel = str(p.relative_to(ROOT_DIR))
            for scope, lineno, round_trips in read_csv_sites(p):
                key = f"{rel}:{scope}"
                seen.add(key)
                if round_trips or key in READ_CSV_EXEMPTIONS:
                    continue
                bad.append(f"{key} (line {lineno}): read_csv without float_precision='{ROUND_TRIP}'")

    assert len(seen) >= 10, (
        f"guard inspected {len(seen)} read_csv sites, expected at least 10. The walk stopped "
        f"matching: re-point it rather than leave a guard that verifies nothing.")
    assert not bad, (
        "CSV ingestion without float round-trip. Add float_precision='round_trip', or declare the "
        "site in READ_CSV_EXEMPTIONS with its motive:\n  " + "\n  ".join(bad))

    stale = [f"{key}  ({motive[:48]}...)" for key, motive in READ_CSV_EXEMPTIONS.items()
             if key not in seen]
    assert not stale, (
        "declared read_csv exemptions that no longer point at a read_csv call -- an edit moved the "
        "line and the exemption now covers nothing:\n  " + "\n  ".join(stale))
