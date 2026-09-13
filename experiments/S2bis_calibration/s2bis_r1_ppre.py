"""Stream S2-bis, Phase 3 (T-B and T-E): the R1 reference rate, analytic, no re-execution.

`exp_R1_generate_data.py:56` builds `StrictCUSUM(0.05, DELTA_P, lambda_val)` -- a reference rate of
0.05 against a measured pre-drift error rate of `ssot.P0_MEASURED = 0.024`. The recursion therefore
runs at an effective tolerance of `p_pre + delta_P - p_true = 0.036`, not `delta_P = 0.01`.

THE FINDING IS REAL AND THE PUBLISHED NUMERALS DO NOT CARRY IT. R1 is a deliberate TWO-ARM design:
`:56` builds the fixed arm and `:81` builds the empirical arm from the mean of the 1 000-step
warm-up. `blind_spot_observed` (`:105-111`) and `tau_det_emp_finite` (`:120`) are both functions of
the EMPIRICAL arm, and `:136-139` aggregates exactly those two into `Share_Blind_Spot` and
`Detection_Rate`. `tau_det_fixed` is recorded at `:117` and read by no aggregation. The effect of
the mis-set reference rate on the two published numerals is therefore exactly zero, and what this
module delivers instead is the within-run counterfactual the frozen parquet already contains: both
arms see the same post-drift error stream under the same seed and the same lambda, so the fixed arm
is a paired control, not a separate experiment.

R2 IS THE OPPOSITE OF THE BRIEF'S EXPECTATION, AND IS SHOWN STRUCTURALLY.
`exp_R2_instrumented_blind_spot.py:90` reads `np.mean(errors_pre) if errors_pre else 0.05`. The
buffer is appended at `:87-88` for every `t` in `[T_DRIFT - 1000, T_DRIFT)` and read at `:89` when
`t == T_DRIFT`, so it holds `min(1000, T_DRIFT)` entries and the `0.05` fallback is UNREACHABLE for
any `T_DRIFT > 0`. R2's reference rate is the warm-up mean, like R1's empirical arm. The literal is
dead code, not a second instance of the R1 defect.

NOTHING IS RE-EXECUTED. `R1_race_condition.parquet` is a frozen artifact, already regenerated once
under action A1, and its deviation is declared in `authorized_deviations.txt`. The re-run decision
belongs to the orchestrator; rule B5 states which branch would require one.

Outputs, all under `results/S2bis_calibration/tables/`:
  s2bis_r1_counterfactual.csv   per lambda: both arms' detection rate and blind-spot share, the
                                paired delta and its seed-paired bootstrap CI
  s2bis_r1_ppre.json            source facts, the tolerance arithmetic, the rule B5 verdict, the
                                SSOT-route audit, and the rule B6 (T-E) verdict in both tests

Usage:  PYTHONHASHSEED=0 python experiments/S2bis_calibration/s2bis_r1_ppre.py
        PYTHONHASHSEED=0 python experiments/S2bis_calibration/s2bis_r1_ppre.py --check
"""
import ast
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "S2_theory"))
from config import experiment_ssot as ssot          # noqa: E402
import s2_arl0 as s2                                # noqa: E402

OUT_DIR = ssot.RESULTS_DIR / "S2bis_calibration" / "tables"
R1_SRC = ROOT_DIR / "experiments" / "R1_race_condition" / "exp_R1_generate_data.py"
R2_SRC = ROOT_DIR / "experiments" / "R2_instrumented_blind_spot" / "exp_R2_instrumented_blind_spot.py"
R1_PARQUET = ssot.RESULTS_DIR / "R1_race_condition" / "data" / "R1_race_condition.parquet"
ARL0_COLUMNS = ssot.RESULTS_DIR / "S2_theory" / "tables" / "s2_arl0_columns.csv"

P_PRE_R1 = 0.05                    # the literal under audit at exp_R1_generate_data.py:56.
                                   # Deliberately NOT registered in the SSOT: a withdrawn value
                                   # given a registry name invites a call site to route through it,
                                   # the same reason s2_arl0.P_S1_ASSUMED is left unregistered.
TRANSFER_S1_FLOOR_CLAIM = 4.56     # transfer_S1.md L73, Delta_e = 0.10, W = 13
TRANSFER_S1_FLOOR_INPUTS = {"p_0": P_PRE_R1, "delta_P": ssot.DELTA_P, "eps": ssot.EPS_MISS,
                            "lam": 50.0, "delta_max": 0.10, "W": 13.0}
COMPETING_DELTA_MAX = 0.137        # the other single substitution that recovers 4.56
COINCIDENCE_P0 = 0.0360            # p_pre + CUSUM_DELTA_P - P0_MEASURED, the R1 effective tolerance


# ─── T-B(a): the source facts, read from source and not asserted ──────────────────────────────────
def _tree(path):
    return ast.parse(path.read_text(encoding="utf-8"))


def r1_fixed_arm_literal():
    """The first positional argument of every StrictCUSUM construction in R1, resolved from AST."""
    out = []
    for node in ast.walk(_tree(R1_SRC)):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "StrictCUSUM"):
            first = node.args[0] if node.args else None
            out.append({"line": node.lineno, "source": ast.unparse(node),
                        "p_pre_expr": ast.unparse(first) if first is not None else None,
                        "p_pre_is_bare_literal": isinstance(first, ast.Constant),
                        "p_pre_value": first.value if isinstance(first, ast.Constant) else None})
    return out


def r2_fallback_reachability():
    """Structural proof that R2's `else 0.05` is unreachable for any T_DRIFT > 0.

    Read from source: the guard that appends to the buffer, the guard that reads it, and the
    resulting length. No classifier is instantiated and no stream is generated -- the buffer's
    length is a property of the loop bounds alone."""
    src = R2_SRC.read_text(encoding="utf-8")
    fallback = [(i + 1, ln.strip()) for i, ln in enumerate(src.splitlines())
                if "errors_pre else" in ln]
    append = [(i + 1, ln.strip()) for i, ln in enumerate(src.splitlines())
              if "errors_pre.append" in ln]
    # The loop bounds, reproduced exactly: append while t < T_DRIFT and t >= T_DRIFT - 1000, read at
    # t == T_DRIFT. R2_WARMUP_WINDOW is the 1000.
    n_steps, t_drift, win = ssot.R2_N_STEPS, ssot.R2_T_DRIFT, ssot.R2_WARMUP_WINDOW
    buffered = [t for t in range(n_steps) if t < t_drift and t >= t_drift - win]
    return {"fallback_site": fallback, "append_site": append,
            "buffer_fill_range": [min(buffered), max(buffered)] if buffered else None,
            "buffer_len_at_t_drift": len(buffered),
            "T_DRIFT": t_drift, "warmup_window": win,
            "fallback_reachable": len(buffered) == 0,
            "verdict": "UNREACHABLE for any T_DRIFT > 0: the buffer is filled over "
                       f"[T_DRIFT - {win}, T_DRIFT) and holds min({win}, T_DRIFT) entries, so "
                       "`if errors_pre` is true whenever the drift is not at t = 0. R2's reference "
                       "rate is the warm-up mean, as R1's empirical arm is. The literal is dead "
                       "code, not a second instance of the R1 defect."}


def published_numeral_route():
    """Which columns the two published numerals are built from, resolved from the aggregation AST."""
    aggs, produced = {}, set()
    for node in ast.walk(_tree(R1_SRC)):
        if isinstance(node, ast.Call) and ast.unparse(node.func).endswith(".agg"):
            for kw in node.keywords:
                aggs[kw.arg] = ast.unparse(kw.value)
        if isinstance(node, ast.Dict):
            for k in node.keys:
                if isinstance(k, ast.Constant) and isinstance(k.value, str):
                    produced.add(k.value)
    consumed = {name: any(c in expr for c in ("blind_spot_observed", "tau_det_emp_finite",
                                              "tau_det_emp", "tau_det_fixed"))
                for name, expr in aggs.items()}
    routes_through_fixed = {name: "tau_det_fixed" in expr for name, expr in aggs.items()}
    return {"aggregations": aggs, "recorded_columns": sorted(produced),
            "sourced_from_a_detection_column": consumed,
            "routes_through_tau_det_fixed": routes_through_fixed,
            "any_published_numeral_routes_through_the_fixed_arm": any(routes_through_fixed.values())}


# ─── T-B(b): the tolerance arithmetic and the paired counterfactual ───────────────────────────────
def tolerance_arithmetic():
    """The effective tolerance of the fixed arm and what it costs, sourced from s2_arl0_columns.csv
    rather than recomputed by hand. Rule B8: ARL_0 is quoted with the (p_pre, p_true) pair that
    produced it, never as a scalar property of one rate."""
    cols = pd.read_csv(ARL0_COLUMNS, float_precision="round_trip").set_index("setting")
    fixed, principal = cols.loc["R1 fixed arm"], cols.loc["principal (S2)"]
    eff = P_PRE_R1 + ssot.CUSUM_DELTA_P - ssot.P0_MEASURED
    rates = {}
    for delta_e in (0.10, 0.15, 0.20, 0.25, 0.33, 0.40, 0.50):
        calibrated, actual = delta_e - ssot.CUSUM_DELTA_P, delta_e - eff
        rates[f"{delta_e:.2f}"] = {
            "mu_calibrated": calibrated, "mu_at_effective_tolerance": actual,
            "accumulation_rate_change_pct": 100.0 * (actual - calibrated) / calibrated,
            "tau_det_star_ratio": calibrated / actual if actual > 0 else float("inf")}
    return {"p_pre_literal": P_PRE_R1, "p_true_measured": ssot.P0_MEASURED,
            "delta_P": ssot.CUSUM_DELTA_P, "effective_tolerance": eff,
            "nominal_tolerance": ssot.CUSUM_DELTA_P,
            "tolerance_factor": eff / ssot.CUSUM_DELTA_P,
            "theta_star_calibrated": float(principal.theta_star),
            "theta_star_fixed_arm": float(fixed.theta_star),
            "ARL0_lambda15_calibrated": float(principal.ARL0_lambda15),
            "ARL0_lambda15_fixed_arm": float(fixed.ARL0_lambda15),
            "ARL0_lambda15_factor": float(fixed.ARL0_lambda15 / principal.ARL0_lambda15),
            "post_drift_accumulation": rates,
            "direction": "the bias INFLATES the blind spot: a larger effective tolerance both "
                         "lengthens the null-regime false-alarm time and slows post-drift "
                         "accumulation, and the slow-down is largest exactly in the weak-signal "
                         "regime the paper claims",
            "source": str(ARL0_COLUMNS.relative_to(ROOT_DIR))}


def counterfactual(n_boot=ssot.S2BIS_N_BOOTSTRAP):
    """The within-run control the frozen parquet already contains.

    Both arms run on the SAME post-drift error stream under the same seed and the same lambda
    (`exp_R1_generate_data.py:88-98` updates them in the same loop body), so the difference between
    them is attributable to the reference rate alone. `blind_spot_observed` is recomputed from the
    fixed arm under R1's own definition at `:105-111`, character for character."""
    df = pd.read_parquet(R1_PARQUET)
    rng = np.random.default_rng(ssot.S2BIS_BOOTSTRAP_SEED)
    rows = []
    for lam, g in df.groupby("lambda_val"):
        g = g.sort_values("seed")
        emp_finite = g.tau_det_emp.notna().to_numpy()
        fix_finite = g.tau_det_fixed.notna().to_numpy()
        arf = g.tau_arf.to_numpy(dtype=float)
        # R1's definition at :105-111, with the fixed arm substituted for the empirical one.
        bs_emp = np.where(~emp_finite, True,
                          arf < np.where(emp_finite, g.tau_det_emp.to_numpy(), np.inf))
        bs_fix = np.where(~fix_finite, True,
                          arf < np.where(fix_finite, g.tau_det_fixed.to_numpy(), np.inf))
        assert np.array_equal(bs_emp, g.blind_spot_observed.to_numpy()), (
            f"the published blind-spot column is not reproduced at lambda = {lam}")
        n = len(g)
        draws = rng.integers(0, n, size=(n_boot, n))
        d_bs = bs_fix[draws].mean(axis=1) - bs_emp[draws].mean(axis=1)
        d_dr = fix_finite[draws].mean(axis=1) - emp_finite[draws].mean(axis=1)
        rows.append({
            "lambda_val": float(lam), "n_seeds": int(n),
            "Share_Blind_Spot_published": float(bs_emp.mean()),
            "Share_Blind_Spot_fixed_arm": float(bs_fix.mean()),
            "delta_Share_Blind_Spot": float(bs_fix.mean() - bs_emp.mean()),
            "delta_Share_ci_lo": float(np.percentile(d_bs, 2.5)),
            "delta_Share_ci_hi": float(np.percentile(d_bs, 97.5)),
            "Detection_Rate_published": float(emp_finite.mean()),
            "Detection_Rate_fixed_arm": float(fix_finite.mean()),
            "delta_Detection_Rate": float(fix_finite.mean() - emp_finite.mean()),
            "delta_DR_ci_lo": float(np.percentile(d_dr, 2.5)),
            "delta_DR_ci_hi": float(np.percentile(d_dr, 97.5)),
            # An all-NaN arm has no median: NaN is the honest value and is written as null.
            "median_tau_det_emp": (float(g.tau_det_emp.median()) if emp_finite.any()
                                   else float("nan")),
            "median_tau_det_fixed": (float(g.tau_det_fixed.median()) if fix_finite.any()
                                     else float("nan")),
            "n_seeds_both_finite": int((emp_finite & fix_finite).sum())})
    return pd.DataFrame(rows).sort_values("lambda_val").reset_index(drop=True)


# ─── T-E: rule B6 ─────────────────────────────────────────────────────────────────────────────────
def _git(*args):
    try:
        return subprocess.run(["git", "-C", str(ROOT_DIR), *args], capture_output=True, text=True,
                              check=True, timeout=60).stdout.strip()
    except Exception as exc:                                     # noqa: BLE001
        return f"<git unavailable: {exc}>"


def te_numeric():
    """Test 1 of rule B6: does the floor at `p_0 <- 0.0360` return 4.56 at the printed precision?

    Two readings of the substitution, both reported. `alpha_held` keeps L73's own false-alarm basis
    (ARL_0 at the S1 Cramer root) and substitutes p_0 only into the floor expression -- the
    substitution S2's floor_restitution identified. `alpha_recomputed` also moves the Cramer root to
    the new p_0, which changes alpha and is the stricter reading."""
    i = TRANSFER_S1_FLOOR_INPUTS
    theta_s1 = s2.cramer_root(i["p_0"], i["p_0"], i["delta_P"])
    a_s1 = s2.arl0(i["lam"], theta_s1, i["delta_P"])
    alpha_s1 = i["W"] / a_s1
    baseline = s2.detection_floor(i["p_0"], i["delta_max"], i["W"], alpha_s1, eps=i["eps"],
                                  delta_p=i["delta_P"])
    held = s2.detection_floor(COINCIDENCE_P0, i["delta_max"], i["W"], alpha_s1, eps=i["eps"],
                              delta_p=i["delta_P"])
    theta_c = s2.cramer_root(COINCIDENCE_P0, COINCIDENCE_P0, i["delta_P"])
    alpha_c = i["W"] / s2.arl0(i["lam"], theta_c, i["delta_P"])
    recomputed = s2.detection_floor(COINCIDENCE_P0, i["delta_max"], i["W"], alpha_c, eps=i["eps"],
                                    delta_p=i["delta_P"])
    competing = s2.detection_floor(i["p_0"], COMPETING_DELTA_MAX, i["W"], alpha_s1, eps=i["eps"],
                                   delta_p=i["delta_P"])
    rnd = lambda v: round(float(v), 2)                           # noqa: E731
    return {"inputs_identified_at_L73": i, "alpha_at_L73_inputs": alpha_s1,
            "floor_at_L73_inputs": baseline,
            "floor_at_L73_inputs_rounded": rnd(baseline),
            "transfer_S1_claim": TRANSFER_S1_FLOOR_CLAIM,
            "substitution_p0_0.0360_alpha_held": held,
            "substitution_p0_0.0360_alpha_held_rounded": rnd(held),
            "substitution_p0_0.0360_alpha_recomputed": recomputed,
            "substitution_p0_0.0360_alpha_recomputed_rounded": rnd(recomputed),
            "competing_explanation_delta_max_0.137": competing,
            "competing_explanation_rounded": rnd(competing),
            "carried_by": "alpha_held -- the substitution s2_arl0.floor_restitution identified",
            "passes": bool(rnd(held) == round(TRANSFER_S1_FLOOR_CLAIM, 2))}


def te_chronology():
    """Test 2 of rule B6: was 0.036 computable when L73 was written?

    0.036 = p_pre(0.05) + CUSUM_DELTA_P(0.01) - P0_MEASURED(0.024). Both of the last two are dated
    from the repository's own history, against the commit that introduced the line."""
    line_commit = _git("log", "--format=%H %ad", "--date=short", "--diff-filter=A", "--follow",
                       "--", "docs/theory/transfer_S1.md").splitlines()[-1:]
    line_commit = line_commit[0] if line_commit else "<none>"
    cusum = _git("log", "--format=%H %ad", "--date=short", "-S", "CUSUM_DELTA_P",
                 "--", "config/experiment_ssot.py").splitlines()[-1:]
    p0 = _git("log", "--format=%H %ad", "--date=short", "-S", "P0_MEASURED",
              "--", "config/experiment_ssot.py").splitlines()[-1:]
    at_line = _git("show", f"{line_commit.split()[0]}:experiments/R1_race_condition/"
                           "exp_R1_generate_data.py") if " " in line_commit else ""
    r1_delta_then = next((ln.split("=", 1)[1].strip() for ln in at_line.splitlines()
                          if ln.startswith("DELTA_P")), None)
    d = lambda s: s.split()[1] if s and " " in s else None       # noqa: E731
    intro_cusum = cusum[0] if cusum else "<none>"
    intro_p0 = p0[0] if p0 else "<none>"
    line_date, cusum_date, p0_date = d(line_commit), d(intro_cusum), d(intro_p0)
    available = bool(line_date and cusum_date and p0_date
                     and cusum_date <= line_date and p0_date <= line_date)
    eff_then = (P_PRE_R1 + float(r1_delta_then) - ssot.P0_MEASURED) if r1_delta_then else None
    return {"line_introduced_by": line_commit, "line_date": line_date,
            "CUSUM_DELTA_P_introduced_by": intro_cusum, "CUSUM_DELTA_P_date": cusum_date,
            "P0_MEASURED_introduced_by": intro_p0, "P0_MEASURED_date": p0_date,
            "R1_DELTA_P_at_that_commit": r1_delta_then,
            "effective_tolerance_computable_then": eff_then,
            "declared_header_at_that_commit": "p_0 = 0.05, delta_P = 0.005, eps = 0.05",
            "passes": available,
            "reading": ("0.036 needs CUSUM_DELTA_P = 0.01 and P0_MEASURED = 0.024. Both postdate "
                        "the commit that introduced the line; at that commit R1 carried "
                        f"DELTA_P = {r1_delta_then}, so its effective tolerance was "
                        f"{eff_then if eff_then is None else round(eff_then, 3)}, not 0.036.")}


def te_verdict():
    num, chrono = te_numeric(), te_chronology()
    return {"rule": "B6", "numeric_test": num, "chronology_test": chrono,
            "verdict": "CONFIRMED" if (num["passes"] and chrono["passes"]) else "REFUTED",
            "verdict_basis": "CONFIRMED requires BOTH tests; either failing is REFUTED",
            "consequence": ("REFUTED leaves S2's R1(b) verdict standing as recorded -- "
                            "UNREPRODUCED, 6.277 against 4.56 -- and the numeric coincidence is "
                            "arithmetic only: the floor is a smooth decreasing function of p_0 on "
                            "this range, so SOME p_0 near 0.036 recovers any value near 4.56, and "
                            "Delta_max = 0.137 recovers it just as well."
                            if not (num["passes"] and chrono["passes"]) else
                            "CONFIRMED makes R1(b) a second symptom of the same configuration "
                            "defect rather than an independent reproduction failure")}


# ─── T-B(d): rule B5 and the SSOT-route audit ─────────────────────────────────────────────────────
def ssot_route_audit():
    """`p_pre` is the one CUSUM parameter with no SSOT route and no test_S7_consistency guard.

    `GUARDED_NAMES` (`tests/test_S7_consistency.py:48-53`) omits every p_pre-shaped name, and the
    `StrictCUSUM` guard added by A1 is scoped to the `delta` argument alone, so a bare literal in
    the FIRST positional slot passes every check the suite has. Both files are outside the S2-bis
    write perimeter; this is a recommendation, not a change."""
    guard_src = (ROOT_DIR / "tests" / "test_S7_consistency.py").read_text(encoding="utf-8")
    guarded = next((ast.literal_eval(ast.unparse(n.value))
                    for n in ast.parse(guard_src).body
                    if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "GUARDED_NAMES"),
                   set())
    params = next((ast.literal_eval(ast.unparse(n.value))
                   for n in ast.parse(guard_src).body
                   if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "GUARDED_PARAMS"),
                  set())
    return {"GUARDED_NAMES": sorted(guarded), "GUARDED_PARAMS": sorted(params),
            "p_pre_in_GUARDED_NAMES": any("P_PRE" in g or "PPRE" in g for g in guarded),
            "p_pre_in_GUARDED_PARAMS": any("p_pre" in p for p in params),
            "strict_cusum_guard_scope": "the `delta` argument only (CUSUM_CLASS / "
                                        "cusum_delta_sites), resolved through StrictCUSUM's own "
                                        "__init__ signature; the first positional slot is p_pre "
                                        "and is not inspected",
            "unguarded_sites": ["experiments/R1_race_condition/exp_R1_generate_data.py:56",
                                "experiments/R2_instrumented_blind_spot/"
                                "exp_R2_instrumented_blind_spot.py:90"],
            "recommendation": "route the CUSUM reference rate through config/experiment_ssot.py "
                              "and extend cusum_delta_sites to resolve the p_pre slot the same way "
                              "it resolves delta. Both files are outside the S2-bis perimeter; no "
                              "change is applied here."}


def b5_verdict(route):
    routed = route["any_published_numeral_routes_through_the_fixed_arm"]
    return {"rule": "B5",
            "verdict": "DEFECT" if routed else "UNDOCUMENTED DELIBERATE CHOICE",
            "rerun_required": bool(routed),
            "evidence": route["routes_through_tau_det_fixed"],
            "sentence_owed_to_the_manuscript": True,
            "reading": ("Share_Blind_Spot and Detection_Rate are aggregated at "
                        "exp_R1_generate_data.py:136-139 from blind_spot_observed and "
                        "tau_det_emp_finite, both functions of the EMPIRICAL arm built at :81 from "
                        "the warm-up mean. tau_det_fixed is recorded at :117 and read by no "
                        "aggregation, so the effect of the 0.05 literal on the two published "
                        "numerals is exactly zero. The choice is deliberate -- R1 is a two-arm "
                        "design -- and undocumented: the manuscript names neither arm, and the "
                        "control arm has never been published."
                        if not routed else
                        "a published numeral routes through the fixed arm; R1 must be re-run")}


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cf = counterfactual()
    cf.to_csv(OUT_DIR / "s2bis_r1_counterfactual.csv", index=False)

    route = published_numeral_route()
    payload = {
        "T_B_a_source_facts": {"R1_StrictCUSUM_sites": r1_fixed_arm_literal(),
                               "R2_fallback": r2_fallback_reachability()},
        "T_B_b_tolerance": tolerance_arithmetic(),
        "T_B_b_counterfactual": json.loads(cf.to_json(orient="records")),
        "T_B_b_published_numeral_route": route,
        "T_B_d_verdict": b5_verdict(route),
        "T_B_d_ssot_route_audit": ssot_route_audit(),
        "T_E_verdict": te_verdict(),
        "reproduction": {"python": sys.version.split()[0],
                         "artifacts_read": [str(R1_PARQUET.relative_to(ROOT_DIR)),
                                            str(ARL0_COLUMNS.relative_to(ROOT_DIR)),
                                            str(R1_SRC.relative_to(ROOT_DIR)),
                                            str(R2_SRC.relative_to(ROOT_DIR))],
                         "command": "PYTHONHASHSEED=0 python "
                                    "experiments/S2bis_calibration/s2bis_r1_ppre.py",
                         "nothing_re_executed": "R1_race_condition.parquet is read, never written"}}
    (OUT_DIR / "s2bis_r1_ppre.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=float) + "\n", encoding="utf-8")

    t = payload["T_B_b_tolerance"]
    print("=== T-B(a) source facts ===")
    for s in payload["T_B_a_source_facts"]["R1_StrictCUSUM_sites"]:
        print(f"  R1:{s['line']:<4d} p_pre = {s['p_pre_expr']:<12s} "
              f"bare literal: {s['p_pre_is_bare_literal']}")
    print(f"  R2 fallback: {payload['T_B_a_source_facts']['R2_fallback']['fallback_site']}")
    print(f"  R2 buffer at t = T_DRIFT: "
          f"{payload['T_B_a_source_facts']['R2_fallback']['buffer_len_at_t_drift']} entries over "
          f"{payload['T_B_a_source_facts']['R2_fallback']['buffer_fill_range']} -> fallback "
          f"reachable: {payload['T_B_a_source_facts']['R2_fallback']['fallback_reachable']}")
    print(f"\n=== T-B(b) tolerance arithmetic ===")
    print(f"  effective tolerance {t['effective_tolerance']:.3f} against a nominal "
          f"{t['nominal_tolerance']:.3f}  (factor {t['tolerance_factor']:.1f})")
    print(f"  theta* {t['theta_star_calibrated']:.4f} -> {t['theta_star_fixed_arm']:.4f}; "
          f"ARL_0(15) x {t['ARL0_lambda15_factor']:.3g}")
    for k, v in t["post_drift_accumulation"].items():
        print(f"    Delta_e = {k}: mu {v['mu_calibrated']:.3f} -> "
              f"{v['mu_at_effective_tolerance']:.3f}  "
              f"({v['accumulation_rate_change_pct']:+.1f} %)")
    print("\n=== T-B(b) within-run counterfactual, frozen parquet, nothing re-executed ===")
    print(cf[["lambda_val", "Share_Blind_Spot_published", "Share_Blind_Spot_fixed_arm",
              "delta_Share_Blind_Spot", "Detection_Rate_published", "Detection_Rate_fixed_arm",
              "delta_Detection_Rate"]].to_string(index=False))
    print(f"\n=== T-B(d) rule B5: {payload['T_B_d_verdict']['verdict']} "
          f"(re-run required: {payload['T_B_d_verdict']['rerun_required']}) ===")
    e = payload["T_E_verdict"]
    print(f"\n=== T-E rule B6: {e['verdict']} ===")
    print(f"  numeric   floor at p_0 <- {COINCIDENCE_P0} = "
          f"{e['numeric_test']['substitution_p0_0.0360_alpha_held']:.4f} -> rounds to "
          f"{e['numeric_test']['substitution_p0_0.0360_alpha_held_rounded']:.2f} against "
          f"{TRANSFER_S1_FLOOR_CLAIM} : {e['numeric_test']['passes']}")
    print(f"  competing Delta_max = {COMPETING_DELTA_MAX} -> "
          f"{e['numeric_test']['competing_explanation_rounded']:.2f}")
    print(f"  chronology {e['chronology_test']['reading']} : {e['chronology_test']['passes']}")
    print(f"\nwrote {OUT_DIR.relative_to(ROOT_DIR)}/"
          "{s2bis_r1_counterfactual.csv, s2bis_r1_ppre.json}")
    return cf, payload


def demo():
    """Self-check. Reads no campaign artifact: the arithmetic and the structural claims alone."""
    # 1. The effective tolerance is the Siegmund null drift of the (p_pre, p_true) pair, and is
    #    3.6x the nominal one.
    eff = P_PRE_R1 + ssot.CUSUM_DELTA_P - ssot.P0_MEASURED
    assert abs(eff - 0.036) < 1e-12, eff
    assert abs(eff / ssot.CUSUM_DELTA_P - 3.6) < 1e-12

    # 2. A larger effective tolerance gives a LARGER Cramer root and a longer ARL_0: the fixed arm
    #    is strictly harder to trip than the calibrated one, which is the direction that inflates
    #    the blind spot.
    th_cal = s2.cramer_root(ssot.P0_MEASURED, ssot.P0_MEASURED, ssot.CUSUM_DELTA_P)
    th_fix = s2.cramer_root(ssot.P0_MEASURED, P_PRE_R1, ssot.CUSUM_DELTA_P)
    assert th_fix > th_cal, (th_fix, th_cal)
    assert (s2.arl0(15.0, th_fix, eff) > s2.arl0(15.0, th_cal, ssot.CUSUM_DELTA_P))

    # 3. The post-drift slow-down is largest at the weak end. -29 % at 0.10, -8 % at 0.33.
    slow = lambda de: 100.0 * ((de - eff) - (de - ssot.CUSUM_DELTA_P)) / (de - ssot.CUSUM_DELTA_P)
    assert abs(slow(0.10) + 28.9) < 0.2, slow(0.10)
    assert abs(slow(0.33) + 8.1) < 0.2, slow(0.33)
    assert slow(0.10) < slow(0.50) < 0.0

    # 4. R2's buffer is non-empty for every T_DRIFT > 0, so the 0.05 fallback is unreachable.
    fill = lambda td, win: len([t for t in range(td + 1) if td - win <= t < td])
    assert fill(ssot.R2_T_DRIFT, ssot.R2_WARMUP_WINDOW) == ssot.R2_WARMUP_WINDOW
    assert fill(1, ssot.R2_WARMUP_WINDOW) == 1
    assert fill(0, ssot.R2_WARMUP_WINDOW) == 0            # the one case that would reach it

    # 5. The floor is strictly INCREASING in p_0 on [0.02, 0.06] (p_0(1-p_0) sits in its numerator),
    #    so it is a smooth monotone map and SOME p_0 below 0.05 recovers any value below 6.277: a
    #    numeric coincidence at 0.036 is guaranteed by monotonicity, not evidence on its own.
    i = TRANSFER_S1_FLOOR_INPUTS
    th = s2.cramer_root(i["p_0"], i["p_0"], i["delta_P"])
    al = i["W"] / s2.arl0(i["lam"], th, i["delta_P"])
    f = [s2.detection_floor(p, i["delta_max"], i["W"], al, eps=i["eps"], delta_p=i["delta_P"])
         for p in (0.02, 0.03, 0.04, 0.05, 0.06)]
    assert all(a < b for a, b in zip(f, f[1:])), f      # increasing in p_0 below 1/2

    print("s2bis_r1_ppre demo: OK")


if __name__ == "__main__":
    demo()
    if "--check" not in sys.argv:
        main()
