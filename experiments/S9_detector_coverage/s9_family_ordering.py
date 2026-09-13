"""T9.4 -- the monitor-family ordering that carries contribution (C4), with the calibration exposed.

The claim (C4) makes is that monitor families can be ordered by their exposure to the adaptation
loop -- cumulative on the error stream, windowed on the error stream, distributional on the input
space -- and that each pays a stated cost. Table I of the manuscript prints such a comparison, and
S2-bis measured that it is not one: at the operating point `lambda = 15`, KSWIN is deployed at an
alpha `4.52x` MORE PERMISSIVE than the CUSUM it is said to beat, and ADWIN at a delta `45x`
TIGHTER. Columns compared at different false-alarm levels order calibrations, not families.

This script produces the matrix twice, side by side and never merged:

  published  CUSUM/PHT lambda = 15 (R4) and 50 (S6), ADWIN delta = 0.002, KSWIN alpha = 0.005
  equalised  the same lambda, with ADWIN and KSWIN moved to the levels at which their requirement
             equals R_CUSUM(lambda_eq) -- `equalising_alpha_*` of
             results/S2bis_calibration/tables/s2bis_proteus_gate.json, couple `S9_T94_COUPLE`

The equalising levels were derived at the ProteuS anchor (`W = 57.4`, `n_stat = 30`, `eps = 0.05`)
and are applied here to the canonical Bernoulli family. That transposition is DECLARED, not hidden:
it is what rule D5 names, and the alternative -- re-equalising per stream -- would answer a
different question and would not be comparable to what S2-bis published.

EDDM enters under rule D9, with an explicit armed / not-armed column rather than as a defeated
family. S2-bis measured that the `0/1080` collapse on ProteuS is a detector that never armed: 0
pre-drift errors, 9 errors over 8 000 steps, warm_start = 30 never reached. On the canonical family
`p_0 = 0.024` gives of the order of 100 pre-drift errors, so EDDM DOES arm here and its result is a
measurement of the detector rather than of its warm-up.

The input-space row is not measured here: it has no false-alarm level on the error stream to
equalise. It comes from `s9_input_space.py` (T9.3) and is carried into the report as the third
exposure class with the cost it actually pays.

Usage:  PYTHONHASHSEED=0 python experiments/S9_detector_coverage/s9_family_ordering.py [smoke|data]
"""
import json
import sys
from pathlib import Path

import numpy as np
import pyarrow.dataset as ds
import pyarrow.parquet as pq
from joblib import Parallel, delayed
from river.drift.binary import EDDM

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "S6_synchronized_traces"))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "S6_synchronized_traces" / "gates"))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "S9_detector_coverage"))
from config import experiment_ssot as ssot  # noqa: E402

import _gate_common as common  # noqa: E402
import s6_recompute_cusum_delta001 as recompute  # noqa: E402
import s9_offline_detectors as off  # noqa: E402
from s6_detectors import ADWINDetector, KSWINDetector, PHT  # noqa: E402

SOURCE_DIR = ssot.RESULTS_DIR / "S6_synchronized_traces"
OUT_DIR = ssot.RESULTS_DIR / "S9_detector_coverage"
ROT_DIR = OUT_DIR / f"rotation_eta{ssot.S9_HDDDM_ETA:.2f}"
# T9.5 reads the SAME matrix off a second stream whose pre-drift null is not degenerate. One script,
# two sources: a near-duplicate file would drift from this one the first time a column moves.
SOURCES = {"s6": (SOURCE_DIR / "data", "canonical Bernoulli boundary shift, e_pre ~ 0.024"),
           "rotation": (ROT_DIR, f"S8 rotation generator, eta = {ssot.S9_HDDDM_ETA}, "
                                 f"Bayes error eta and a 50/50 class prior at every magnitude")}
GATE_JSON = ssot.RESULTS_DIR / "S2bis_calibration" / "tables" / "s2bis_proteus_gate.json"
ARM = "full"
WARMUP = ssot.S9_WARMUP_WINDOW
T_HORIZON = ssot.S9_T_HORIZON
LAMBDAS = ssot.S6_AUDIT_LAMBDAS                 # [15, 50] -- R4's operating threshold and S6's
                                                # starvation certificate, the exact pair the S6
                                                # CUSUM audit already reads its crossing rates at
EXPOSURE = {"StrictCUSUM": "cumulative on the error stream",
            "PHT": "cumulative on the error stream",
            "EDDM": "cumulative on the error stream",
            "ADWIN": "windowed on the error stream",
            "KSWIN": "windowed on the error stream"}


def equalising_levels():
    """The two committed equalising levels, read from the artifact -- never retyped."""
    gate = json.loads(GATE_JSON.read_text(encoding="utf-8"))["family_requirements_at_lambda_eq"]
    couple = next(c for c in gate["per_couple"] if c["couple"] == ssot.S9_T94_COUPLE)
    return {"lambda_eq": couple["lambda_eq"],
            "ADWIN": {"published": couple["deployed_alpha_ADWIN"],
                      "equalised": couple["equalising_alpha_ADWIN"]},
            "KSWIN": {"published": couple["deployed_alpha_KSWIN"],
                      "equalised": couple["equalising_alpha_KSWIN"]},
            "anchor": gate["at"], "R_CUSUM_at_lambda_eq": couple["R_CUSUM"]}


def cusum_path(excess):
    """The reflected CUSUM path in closed form. `max(S)` is `s6_recompute...s_max` by construction."""
    m = np.concatenate(([0.0], np.cumsum(excess)))
    return (m - np.minimum.accumulate(m))[1:]


def run_cell(err, t_rel, delta_e, seed, input_arm, levels):
    values, first = off._input_stream(err, input_arm)
    n = err.size
    key = (ssot.S9_SEED_MASTER, int(round(delta_e * 1e6)), int(seed),
           ssot.S9_INPUT_ARMS.index(input_arm), 94)
    safe_seed, _ = common.lock_rng(int(np.random.SeedSequence(key).generate_state(1)[0]))

    pht = PHT(threshold=ssot.S9_PHT_TRACE_THRESHOLD, delta=ssot.DELTA_P)
    adw = {k: ADWINDetector(delta=levels["ADWIN"][k], clock=ssot.S9_ADWIN_CLOCK)
           for k in ("published", "equalised")}
    ksw = KSWINDetector(alpha=ssot.S9_KSWIN_TRACE_ALPHA, seed=safe_seed,
                        window_size=ssot.S9_KSWIN_WINDOW, stat_size=ssot.S9_KSWIN_STAT)
    eddm = EDDM(warm_start=ssot.S9_EDDM_WARM_START)

    ps = np.full(n, np.nan)
    kp = np.full(n, np.nan)
    ad = {k: np.zeros(n, dtype=bool) for k in adw}
    ed = np.zeros(n, dtype=bool)
    armed_at = None
    for j in range(first, n):
        x = float(values[j - first])
        pht.update(x)
        ps[j] = pht.statistic()
        for k, d in adw.items():
            d.update(x)
            ad[k][j] = d.drift_detected
        ksw.update(x)
        if len(ksw.detector.window) >= ssot.S9_KSWIN_WINDOW:
            kp[j] = ksw.statistic()
        # EDDM consumes the BINARY error, never the smoothed average: its statistic is built from
        # distances between errors, which a moving average does not define. The smoothed arm feeds
        # it the raw stream and that restriction is reported rather than papered over.
        eddm.update(bool(err[j]))
        ed[j] = eddm.drift_detected
        if armed_at is None and eddm._n_errors >= ssot.S9_EDDM_WARM_START:
            armed_at = int(t_rel[j])

    p0 = float(err[t_rel < 0].mean())
    scu = cusum_path(err - p0 - ssot.CUSUM_DELTA_P)

    def cross(mask):
        hit = np.flatnonzero(mask)
        return int(t_rel[hit[0]]) if hit.size else None

    out = {"delta_e": round(delta_e, 6), "seed": int(seed), "input_arm": input_arm, "p0": p0,
           "eddm_armed": bool(armed_at is not None),
           "eddm_armed_t_rel": armed_at,
           "EDDM|armed": cross(ed)}
    for lam in LAMBDAS:
        out[f"StrictCUSUM|lambda={lam:g}"] = cross(scu >= lam)
        out[f"PHT|lambda={lam:g}"] = cross(ps > lam)
    for k in ("published", "equalised"):
        out[f"ADWIN|{k}"] = cross(ad[k])
        out[f"KSWIN|{k}"] = cross(kp <= levels["KSWIN"][k])
    return out


def partition(part, levels, seed_cap=None):
    delta_e = float(Path(part).name.split("=", 1)[1])
    df = ds.dataset(str(part), format="parquet").to_table(
        columns=["arm", "seed", "t_rel", "err"],
        filter=(ds.field("arm") == ARM) & (ds.field("t_rel") >= -WARMUP)
        & (ds.field("t_rel") < T_HORIZON)).to_pandas().sort_values(["seed", "t_rel"])
    rows = []
    for s in sorted(df["seed"].unique())[:seed_cap]:
        g = df[df.seed == s]
        err = g["err"].to_numpy(dtype=np.float64)
        t_rel = g["t_rel"].to_numpy()
        for ia in ssot.S9_INPUT_ARMS:
            rows.append(run_cell(err, t_rel, delta_e, int(s), ia, levels))
    return rows


def matrix(rows, runs):
    """Family x setting x magnitude: false-alarm cost, detection inside W, delay."""
    w = runs.set_index(["delta_e", "seed"])["w_fw"]
    cols = ([(f"StrictCUSUM|lambda={l:g}", "StrictCUSUM", "published", l) for l in LAMBDAS]
            + [(f"PHT|lambda={l:g}", "PHT", "published", l) for l in LAMBDAS]
            + [(f"ADWIN|{k}", "ADWIN", k, None) for k in ("published", "equalised")]
            + [(f"KSWIN|{k}", "KSWIN", k, None) for k in ("published", "equalised")]
            + [("EDDM|armed", "EDDM", "published", None)])
    cells = {}
    for r in rows:
        wr = float(w.get((r["delta_e"], r["seed"]), np.nan))
        for field, fam, setting, thr in cols:
            c = cells.setdefault((r["delta_e"], r["input_arm"], fam, setting, thr),
                                 {"n": 0, "pre": 0, "inW": 0, "nW": 0, "delays": [], "armed": 0})
            c["n"] += 1
            c["armed"] += r["eddm_armed"]
            t = r[field]
            if np.isfinite(wr):
                c["nW"] += 1
            if t is None:
                continue
            if t < 0:
                c["pre"] += 1
            elif np.isfinite(wr) and t <= wr:
                c["inW"] += 1
                c["delays"].append(t)
    out = []
    for (de, ia, fam, setting, thr), c in sorted(cells.items(), key=lambda kv: (kv[0][2], kv[0][3] or "",
                                                                               kv[0][4] or 0, kv[0][1], kv[0][0])):
        out.append({"delta_e": de, "input_arm": ia, "family": fam, "setting": setting,
                    "threshold": thr, "exposure": EXPOSURE[fam], "n": c["n"],
                    "pre_drift_alarm_rate": round(c["pre"] / c["n"], 4),
                    "detect_within_W_rate": None if c["nW"] == 0 else round(c["inW"] / c["nW"], 4),
                    "add_median": None if not c["delays"] else round(float(np.median(c["delays"])), 1),
                    "armed_rate": round(c["armed"] / c["n"], 4) if fam == "EDDM" else None})
    return out


def main(which="data", source="s6"):
    if source not in SOURCES:
        raise SystemExit(f"usage: s9_family_ordering.py [smoke|data] [{'|'.join(SOURCES)}]")
    base, source_desc = SOURCES[source]
    root = base / "traces.parquet"
    if not root.exists():
        raise SystemExit(f"[FATAL] {root} absent -- "
                         + ("the S6 trace corpus is not reachable" if source == "s6" else
                            "run experiments/S9_detector_coverage/s9_rotation_traces.py first"))
    levels = equalising_levels()
    parts = sorted(root.iterdir())
    seed_cap = 5 if which == "smoke" else None
    if which == "smoke":
        parts = parts[::7]

    print(f"=== family ordering on '{source}' -- arm '{ARM}', {len(parts)} magnitudes, "
          f"both input arms ===")
    print(f"    stream: {source_desc}")
    print(f"    published : CUSUM/PHT lambda {LAMBDAS}, ADWIN delta "
          f"{levels['ADWIN']['published']:g}, KSWIN alpha {levels['KSWIN']['published']:g}")
    print(f"    equalised : same lambda, ADWIN delta {levels['ADWIN']['equalised']:.6g} "
          f"({levels['ADWIN']['equalised'] / levels['ADWIN']['published']:.1f}x looser), "
          f"KSWIN alpha {levels['KSWIN']['equalised']:.6g} "
          f"({levels['KSWIN']['published'] / levels['KSWIN']['equalised']:.2f}x tighter)")
    print(f"    equalisation anchor: lambda_eq = {levels['lambda_eq']:g}, "
          f"R_CUSUM = {levels['R_CUSUM_at_lambda_eq']:.3f} at W = {levels['anchor']['W']}")

    res = Parallel(n_jobs=-1)(delayed(partition)(p, levels, seed_cap) for p in parts)
    rows = [r for b in res for r in b]
    runs = pq.read_table(base / "runs.parquet").to_pandas()
    runs = runs[runs.arm == ARM].copy()
    runs["delta_e"] = runs["delta_e"].round(6)
    mat = matrix(rows, runs)

    armed = [r for r in rows if r["eddm_armed"]]
    p0_med = float(np.median([r["p0"] for r in rows]))
    armed_med = None if not armed else float(np.median([r["eddm_armed_t_rel"] for r in armed]))
    d9 = {"verdict": "ARMED-COLUMN",
          "armed_rate": round(len(armed) / len(rows), 4),
          "armed_t_rel_median": armed_med,
          "warm_start": ssot.S9_EDDM_WARM_START,
          "traced_pre_drift_steps": int(WARMUP),
          "campaign_pre_drift_steps": int(ssot.S6_T_DRIFT),
          "p0_median": round(p0_med, 5),
          "analytic_arming_t_rel": round(ssot.S9_EDDM_WARM_START / p0_med - ssot.S6_T_DRIFT, 1),
          "measurement_window_caveat":
              "The corpus traces the LAST {} pre-drift steps, not the campaign's {}. At "
              "p_0 = {:.4f} those {} steps carry about {:.0f} errors against a warm_start of {}, so "
              "the arming instant MEASURED here falls inside the transient and EDDM's delay is not "
              "separable from its warm-up on this window. In the deployed pipeline the same "
              "p_0 arms it near t_rel = {:.0f}, which is derived from p_0 and not observed."
              .format(int(WARMUP), int(ssot.S6_T_DRIFT), p0_med, int(WARMUP),
                      p0_med * WARMUP, ssot.S9_EDDM_WARM_START,
                      ssot.S9_EDDM_WARM_START / p0_med - ssot.S6_T_DRIFT),
          "rule": "D9 keeps EDDM in the table only with an explicit armed / not-armed column and a "
                  "stream on which it can arm. On ProteuS it never arms (0 pre-drift errors, 9 over "
                  "the whole stream). On the canonical family it arms, but the traced window places "
                  "the arming instant inside the transient, so the row carries the arming instant "
                  "beside the delay rather than the delay alone."}

    suffix = ("" if source == "s6" else f"_{source}") + ("" if which == "data" else f"_{which}")
    tab = OUT_DIR / "tables"
    tab.mkdir(parents=True, exist_ok=True)
    path = tab / f"s9_family_ordering{suffix}.json"
    path.write_text(json.dumps(
        {"which": which, "source": source, "source_description": source_desc,
         "arm": ARM, "n_runs": len(rows), "lambdas": LAMBDAS,
         "levels": levels, "exposure_classes": EXPOSURE,
         "equalisation_transposition": "the equalising levels were derived at the ProteuS anchor "
                                       "(W = 57.4, n_stat = 30, eps = 0.05) and are applied here to "
                                       "the canonical Bernoulli family; rule D5 names those values",
         "D9": d9, "env": common.env_stamp(), "cells": mat},
        indent=2, sort_keys=True, default=float) + "\n", encoding="utf-8")

    print(f"\n--- grid mean over the {len(parts)} magnitudes, arm 'full' ---")
    print(f"{'input':9s} {'family':12s} {'setting':10s} {'thr':>6s} {'preFA':>7s} {'inW':>7s} {'ADD':>7s}")
    for ia in ssot.S9_INPUT_ARMS:
        for fam in ("StrictCUSUM", "PHT", "ADWIN", "KSWIN", "EDDM"):
            for setting in ("published", "equalised"):
                for thr in (LAMBDAS if fam in ("StrictCUSUM", "PHT") else [None]):
                    sub = [c for c in mat if c["input_arm"] == ia and c["family"] == fam
                           and c["setting"] == setting and c["threshold"] == thr]
                    if not sub:
                        continue
                    iw = [c["detect_within_W_rate"] for c in sub if c["detect_within_W_rate"] is not None]
                    ad = [c["add_median"] for c in sub if c["add_median"] is not None]
                    print(f"{ia:9s} {fam:12s} {setting:10s} {str(thr) if thr else '-':>6s} "
                          f"{np.mean([c['pre_drift_alarm_rate'] for c in sub]):7.3f} "
                          f"{np.mean(iw) if iw else float('nan'):7.3f} "
                          f"{np.median(ad) if ad else float('nan'):7.1f}")
    print(f"\n--- D9 --- {d9['verdict']}: EDDM armed on {d9['armed_rate']:.1%} of runs, "
          f"median at t_rel = {d9['armed_t_rel_median']} (inside the transient); at p_0 = "
          f"{d9['p0_median']} the deployed {d9['campaign_pre_drift_steps']}-step pre-drift phase "
          f"arms it near t_rel = {d9['analytic_arming_t_rel']}, derived not observed")
    print(f"[INFO] wrote {path.relative_to(ssot.ROOT_DIR)} ({len(mat)} cells, {len(rows)} runs)")
    return mat


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data",
         sys.argv[2] if len(sys.argv) > 2 else "s6")
