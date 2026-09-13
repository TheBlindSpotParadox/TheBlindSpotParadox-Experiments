"""T9.2 -- the controlled-transient grid, and the two models it separates.

P1 could not decide rule D3. The S6 corpus bottoms out at an exploitable transient of `W = 199`
steps, so the dilution region `W < n_stat` has ZERO cells there and the branch is undecidable on
any amount of that data. The fix is not more seeds, it is a different experiment: drive the error
stream directly. A rectangular transient of declared height `Delta_e` and declared duration `W` on
a Bernoulli(`p_0`) background puts the monitor alone on trial, with no classifier in the loop and
with `A = (Delta_e - delta_P) W` exact by construction rather than estimated.

THE TWO MODELS, WRITTEN BEFORE MEASUREMENT (docs/prompts/s9-decision-rules.md, Part B).

  B1, the budget model that `eq:Rkswin` instantiates:

      alarm  <=>  A >= R_KSWIN = sqrt(n_stat ln(2/alpha)) + sqrt((W/2) ln(1/eps))

  B2/contrast, the model the dilution branch implies. The recent sample holds `min(W, n_stat)` of
  its `n_stat` entries from the transient, and on a binary error stream the KS distance between the
  reference and the recent sample is the difference in the fraction of ones. Hence

      D_model = (min(W, n_stat) / n_stat) * Delta_e ,
      alarm  <=>  D_model >= k*(alpha, n_stat) / n_stat
             <=>  min(W, n_stat) * Delta_e >= k*(alpha, n_stat)

  with `k*` the exact two-sample lattice level of `s9_offline_detectors.requirement_lattice()`.
  The two disagree over a region the grid is sized to contain: B1 integrates, the contrast model
  does not, so B1 rewards a long weak transient and the contrast model rewards a short strong one.

The grid reaches `Delta_e = 1.0` deliberately. B2's region -- `W < n_stat` AND `A >= R_KSWIN`, the
cells where `eq:Rkswin` REQUIRES detection and dilution forbids it -- is empty below
`Delta_e = 0.457` at every cell of `S9_NSTAT_GRID x S9_KSWIN_ALPHA_GRID`, so a grid stopping at the
canonical 0.498 would return `NOT PRODUCED` by construction and prove nothing. `Delta_e = 1.0` is
not an extrapolation: it is the ProteuS operating point (`exp_R4_main_table.py:105`).

Alarm derivation, seeding and the `st > 0.1` guard are `s9_offline_detectors`' and are imported
rather than restated.

Usage:  PYTHONHASHSEED=0 python experiments/S9_detector_coverage/s9_kswin_dilution.py [smoke|data]
"""
import json
import sys
from pathlib import Path

import numpy as np
from joblib import Parallel, delayed

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "S6_synchronized_traces"))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "S6_synchronized_traces" / "gates"))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "S9_detector_coverage"))
from config import experiment_ssot as ssot  # noqa: E402

import _gate_common as common  # noqa: E402
import s9_offline_detectors as off  # noqa: E402
from s6_detectors import KSWINDetector  # noqa: E402

OUT_DIR = ssot.RESULTS_DIR / "S9_detector_coverage"
P0 = ssot.S9_T92_P0
PRE, POST = ssot.S9_T92_PRE, ssot.S9_T92_POST
DELTA_P = ssot.DELTA_P
EPS = ssot.S9_EPS
ALPHAS = ssot.S9_KSWIN_ALPHA_GRID


def make_stream(rng, delta_e, w):
    """Bernoulli(p_0) / Bernoulli(p_0 + Delta_e) for `w` steps / Bernoulli(p_0). t_rel = 0 at onset.

    The transient is rectangular and ENDS: this is the erasure the adaptive classifier performs,
    reproduced exogenously so that its duration is a controlled variable instead of an outcome."""
    p = np.full(PRE + w + POST, P0)
    p[PRE:PRE + w] = min(1.0, P0 + delta_e)
    return (rng.random(p.size) < p).astype(np.float64), np.arange(-PRE, w + POST, dtype=np.int32)


def cell(delta_e, w, n_stat, seed, input_arm, pv_lattice):
    """One run. Returns the first crossing per alpha, over the whole stream, in t_rel units."""
    key = (ssot.S9_SEED_MASTER, int(round(delta_e * 1e4)), int(w), int(n_stat), int(seed),
           ssot.S9_INPUT_ARMS.index(input_arm))
    stream_seed = int(np.random.SeedSequence(key).generate_state(1)[0])
    safe_seed, rng = common.lock_rng(stream_seed)
    err, t_rel = make_stream(rng, delta_e, w)

    values, first = off._input_stream(err, input_arm)
    ksw = KSWINDetector(alpha=ssot.S9_KSWIN_TRACE_ALPHA, seed=safe_seed,
                        window_size=ssot.S9_KSWIN_WINDOW, stat_size=n_stat)
    kp = np.full(err.size, np.nan)
    for j in range(first, err.size):
        ksw.update(float(values[j - first]))
        if len(ksw.detector.window) >= ssot.S9_KSWIN_WINDOW:
            kp[j] = ksw.statistic()

    out = {"delta_e": delta_e, "w": int(w), "n_stat": int(n_stat), "seed": int(seed),
           "input_arm": input_arm,
           "e_pre_emp": float(err[t_rel < 0].mean()),
           "e_transient_emp": float(err[(t_rel >= 0) & (t_rel < w)].mean()) if w else 0.0}
    for a in ALPHAS:
        hit = np.flatnonzero(kp <= a)
        t = int(t_rel[hit[0]]) if hit.size else None
        out[f"t_first_alpha{a:g}"] = t
        # inside the transient / after it / before it, the three outcomes that are not the same
        out[f"in_w_alpha{a:g}"] = bool(t is not None and 0 <= t < w)
        out[f"pre_alpha{a:g}"] = bool(t is not None and t < 0)
    return out


def block(delta_e_grid, w, n_stat, input_arm, pv_lattice, n_seeds):
    return [cell(de, w, n_stat, s, input_arm, pv_lattice)
            for de in delta_e_grid for s in range(n_seeds)]


def k_star_table():
    """{(n_stat, alpha): k*} from the committed exact lattice -- imported, not recomputed here."""
    return {(c["n_stat"], c["alpha"]): c["k_star"] for c in off.requirement_lattice()["grid"]}


def predictions(delta_e, w, n_stat, alpha, k_star):
    """(B1 says alarm, contrast model says alarm). Both are pure functions of the cell."""
    a_budget = (delta_e - DELTA_P) * w
    r_kswin = np.sqrt(n_stat * np.log(2.0 / alpha)) + np.sqrt(w / 2.0 * np.log(1.0 / EPS))
    contrast = min(w, n_stat) * delta_e
    return bool(a_budget >= r_kswin), bool(contrast >= k_star), float(a_budget), float(r_kswin)


def aggregate(rows, kstar):
    cells = {}
    for r in rows:
        for a in ALPHAS:
            k = (r["delta_e"], r["w"], r["n_stat"], r["input_arm"], a)
            c = cells.setdefault(k, {"n": 0, "hit": 0, "pre": 0})
            c["n"] += 1
            c["hit"] += r[f"in_w_alpha{a:g}"]
            c["pre"] += r[f"pre_alpha{a:g}"]
    out = []
    for (de, w, n_stat, ia, a), c in sorted(cells.items()):
        b1, ctr, A, R = predictions(de, w, n_stat, a, kstar[(n_stat, a)])
        rate = c["hit"] / c["n"]
        obs = rate >= 1.0 - EPS
        out.append({"delta_e": de, "w": w, "n_stat": n_stat, "input_arm": ia, "alpha": a,
                    "n": c["n"], "detect_in_W_rate": round(rate, 4),
                    "pre_drift_alarm_rate": round(c["pre"] / c["n"], 4),
                    "A_budget": round(A, 3), "R_KSWIN": round(R, 3),
                    "k_star": kstar[(n_stat, a)],
                    "contrast_statistic": round(min(w, n_stat) * de, 3),
                    "B1_predicts_detect": b1, "contrast_predicts_detect": ctr,
                    "observed_detect": obs,
                    "B1_agrees": b1 == obs, "contrast_agrees": ctr == obs,
                    "dilution_regime": bool(w < n_stat),
                    "B2_region": bool(w < n_stat and A >= R)})
    return out


def verdicts(cells):
    """Rules D1-bis (model comparison) and D3 (the dilution branch), applied as committed."""
    def acc(xs, field):
        return None if not xs else round(sum(x[field] for x in xs) / len(xs), 4)

    raw = [c for c in cells if c["input_arm"] == "raw"]
    b2 = [c for c in raw if c["B2_region"]]
    missed = [c for c in b2 if c["detect_in_W_rate"] < 1.0 - EPS]
    # D3 as committed, three branches and no fourth: the region is empty, or it contains a cell
    # KSWIN misses above eps, or it does not.
    d3 = ("NOT PRODUCED" if not b2
          else "PREDICTED-AND-OBSERVED" if missed
          else "PREDICTED-AND-ABSENT")
    dil = [c for c in raw if c["dilution_regime"]]
    return {
        "D3": {"verdict": d3, "B2_region_cells": len(b2),
               "B2_cells_missed_above_eps": len(missed),
               "B2_mean_detect_rate": acc(b2, "detect_in_W_rate"),
               "rule": "cells with W < n_stat AND A >= R_KSWIN; eq:Rkswin requires detection there. "
                       "A miss rate above eps = 0.05 on any of them is PREDICTED-AND-OBSERVED; "
                       "none is PREDICTED-AND-ABSENT, which refutes B2 and escalates to S1/S2."},
        "model_comparison": {
            "scope": "input_arm = raw, all cells",
            "n_cells": len(raw),
            "B1_agreement": acc(raw, "B1_agrees"),
            "contrast_agreement": acc(raw, "contrast_agrees"),
            "dilution_regime_only": {"n_cells": len(dil),
                                     "B1_agreement": acc(dil, "B1_agrees"),
                                     "contrast_agreement": acc(dil, "contrast_agrees")},
            "D2_threshold": 0.90},
    }


def main(which="data"):
    n_seeds = 5 if which == "smoke" else ssot.S9_T92_N_SEEDS
    grid = ssot.S9_T92_DELTA_E_GRID[::4] if which == "smoke" else ssot.S9_T92_DELTA_E_GRID
    ws = ssot.S9_T92_W_GRID[::3] if which == "smoke" else ssot.S9_T92_W_GRID
    nstats = ssot.S9_NSTAT_GRID
    pv, _ = off.alarm_lattice()
    kstar = k_star_table()

    print(f"=== T9.2 controlled-transient grid -- {len(grid)} magnitudes x {len(ws)} transients x "
          f"{len(nstats)} n_stat x {n_seeds} seeds x {len(ssot.S9_INPUT_ARMS)} input arms ===")
    print(f"    stream: {PRE} steps at p_0 = {P0}, W steps at p_0 + Delta_e, {POST} steps at p_0")
    print(f"    Delta_e in [{grid[0]}, {grid[-1]}], W in {ws}, n_stat in {nstats}")

    jobs = [(w, n, ia) for w in ws for n in nstats for ia in ssot.S9_INPUT_ARMS]
    res = Parallel(n_jobs=-1)(delayed(block)(grid, w, n, ia, pv, n_seeds) for w, n, ia in jobs)
    rows = [r for b in res for r in b]
    cells = aggregate(rows, kstar)
    verd = verdicts(cells)

    suffix = "" if which == "data" else f"_{which}"
    tab = OUT_DIR / "tables"
    tab.mkdir(parents=True, exist_ok=True)
    path = tab / f"s9_kswin_dilution{suffix}.json"
    path.write_text(json.dumps(
        {"which": which, "n_runs": len(rows), "n_cells": len(cells),
         "p0": P0, "pre": PRE, "post": POST, "delta_p": DELTA_P, "eps": EPS,
         "delta_e_grid": grid, "w_grid": ws, "n_stat_grid": nstats, "alphas": ALPHAS,
         "n_seeds": n_seeds, "kswin_window": ssot.S9_KSWIN_WINDOW,
         "models": {"B1": "A = (Delta_e - delta_P) W >= R_KSWIN",
                    "contrast": "min(W, n_stat) * Delta_e >= k*(alpha, n_stat)"},
         "verdicts": verd, "env": common.env_stamp(), "cells": cells},
        indent=2, sort_keys=True, default=float) + "\n", encoding="utf-8")

    m = verd["model_comparison"]
    print(f"\n--- model agreement with the measurement (raw arm, {m['n_cells']} cells) ---")
    print(f"    B1 (budget, eq:Rkswin)      {m['B1_agreement']:.4f}")
    print(f"    contrast (min(W,n_stat) De) {m['contrast_agreement']:.4f}")
    d = m["dilution_regime_only"]
    print(f"    restricted to W < n_stat ({d['n_cells']} cells): B1 {d['B1_agreement']:.4f}, "
          f"contrast {d['contrast_agreement']:.4f}")
    v = verd["D3"]
    print(f"\n--- D3 --- {v['verdict']}   B2 region: {v['B2_region_cells']} cells, "
          f"{v['B2_cells_missed_above_eps']} missed above eps, "
          f"mean detect rate {v['B2_mean_detect_rate']}")
    print(f"[INFO] wrote {path.relative_to(ssot.ROOT_DIR)} ({len(cells)} cells, {len(rows)} runs)")
    return cells


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data")
