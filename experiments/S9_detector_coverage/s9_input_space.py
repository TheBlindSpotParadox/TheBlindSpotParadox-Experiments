"""T9.3 -- the input-space arm, and the design-space boundary it returns.

Contribution (C4) orders monitor families by their exposure to the adaptation loop: cumulative on
the error stream, windowed on the error stream, distributional on the INPUT space. The third row
has never been measured in this repository, and it carries the most discriminating test of the S5
closed-loop reframing, quoted in `docs/prompts/s9-decision-rules.md` D8: *"a detector operating on
P(X) suffers a degradation correlated with tau_erase, although it does not read e_t"*. Observing
that correlation makes the reframing FALSE.

WHAT THE GENERATOR ALLOWS, ESTABLISHED ON THE SOURCE BEFORE IMPLEMENTING. `s8_rotation
.make_rotation_stream` draws `x = rng.normal(size=(N_STEPS, 2))` ONCE per seed, with no dependence
on `t`, on `Delta_e` or on `eta`; the drift is entirely in the labelling half-plane, which turns
from `pi/4` to `phi`. `P(X)` is therefore invariant by construction, exactly, at every magnitude.
An input-space monitor is structurally blind to this drift. That is not a failure of the arm: it is
the cost the third family pays, and stating it with a measurement behind it delimits the design
space instead of populating it with a number that means nothing.

Two consequences for D8, both declared here rather than discovered later:
  - the HDDDM signal on this stream is noise around its own null, so a Spearman correlation against
    `tau_erase` measures the correlation of NOISE with `tau_erase`. It is reported, because D8 asks
    for it, and it is NOT the verdict. The verdict is the blindness;
  - BAF and INSECTS are excluded as terrain by S7-ter's measurement, and the canonical Bernoulli
    family moves the boundary at fixed `P(X)` exactly as the rotation family does. There is no
    stream in this repository on which the third family can see the drift under study.

HDDDM (Ditzler & Polikar 2011) is re-implemented here in NumPy alone. No drift detector in river
operates on `P(X)`, and neither `frouros` nor `menelaus` is in the pinned environment; adding one
to measure a detector predicted to see nothing would be the wrong trade.

Usage:  PYTHONHASHSEED=0 python experiments/S9_detector_coverage/s9_input_space.py [smoke|data]
"""
import json
import sys
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq
from joblib import Parallel, delayed
from scipy import stats

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "S6_synchronized_traces"))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "S6_synchronized_traces" / "gates"))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "S8_generality"))
from config import experiment_ssot as ssot  # noqa: E402

import _gate_common as common  # noqa: E402
import s8_rotation as rot  # noqa: E402

OUT_DIR = ssot.RESULTS_DIR / "S9_detector_coverage"
ROT_DIR = ssot.RESULTS_DIR / "S8_rotation_generator" / "data"
BATCH = ssot.S9_HDDDM_BATCH
GAMMA = ssot.S9_HDDDM_GAMMA
ETA = ssot.S9_HDDDM_ETA
MIN_HISTORY = ssot.S9_HDDDM_MIN_HISTORY
T_DRIFT = ssot.S8_T_DRIFT


# ══════════════════════════════════════════════════════════════════════════════
# HDDDM, NumPy only
# ══════════════════════════════════════════════════════════════════════════════
def hellinger(ref, cur):
    """Mean over features of the Hellinger distance between two histograms.

    b = floor(sqrt(|ref|)) equal-width bins spanning the union of the two supports, per feature,
    which is the binning rule of the paper. The distance is
    sqrt(sum_i (sqrt(p_i/|P|) - sqrt(q_i/|Q|))^2), averaged over features."""
    n_bins = max(2, int(np.floor(np.sqrt(ref.shape[0]))))
    out = np.empty(ref.shape[1])
    for k in range(ref.shape[1]):
        lo = min(ref[:, k].min(), cur[:, k].min())
        hi = max(ref[:, k].max(), cur[:, k].max())
        edges = np.linspace(lo, hi, n_bins + 1)
        edges[-1] = np.nextafter(edges[-1], np.inf)
        p = np.histogram(ref[:, k], bins=edges)[0] / ref.shape[0]
        q = np.histogram(cur[:, k], bins=edges)[0] / cur.shape[0]
        out[k] = np.sqrt(np.sum((np.sqrt(p) - np.sqrt(q)) ** 2))
    return float(out.mean())


def hdddm(x, batch=BATCH, gamma=GAMMA, min_history=MIN_HISTORY):
    """(H per batch, detection batch indices). Reference grows until a detection resets it."""
    n_batches = x.shape[0] // batch
    ref = x[:batch]
    h = np.full(n_batches, np.nan)
    eps_hist, detections = [], []
    h_prev = None
    for t in range(1, n_batches):
        cur = x[t * batch:(t + 1) * batch]
        h_t = hellinger(ref, cur)
        h[t] = h_t
        if h_prev is not None:
            eps = h_t - h_prev
            if len(eps_hist) >= min_history:
                a = np.abs(eps_hist)
                beta = a.mean() + gamma * a.std(ddof=1)
                if abs(eps) > beta:
                    detections.append(t)
                    ref, eps_hist, h_prev = cur, [], None
                    continue
            eps_hist.append(eps)
        h_prev = h_t
        ref = np.vstack([ref, cur])
    return h, detections


# ══════════════════════════════════════════════════════════════════════════════
# One run
# ══════════════════════════════════════════════════════════════════════════════
def run_cell(seed, delta_e, eta=ETA):
    """HDDDM on the rotation feature stream, plus the P(X)-invariance control on the same X."""
    _, x, _ = rot.make_rotation_stream(seed, delta_e, eta)
    h, det = hdddm(x)
    b_drift = T_DRIFT // BATCH
    pre, post = h[1:b_drift], h[b_drift:]
    pre, post = pre[np.isfinite(pre)], post[np.isfinite(post)]

    # The two degradation statistics, both declared before reading. The first is the excess of the
    # post-drift peak over the pre-drift level; the second is the delay of the first post-drift
    # detection, in steps, NaN when none occurs.
    peak_excess = float(post.max() - np.median(pre)) if pre.size and post.size else np.nan
    post_det = [d for d in det if d >= b_drift]
    delay = float(post_det[0] * BATCH - T_DRIFT) if post_det else np.nan

    # P(X) invariance control, on the same X the detector saw: two-sample KS per feature, the
    # 4000 pre-drift rows against the 4000 post-drift rows.
    ks = [float(stats.ks_2samp(x[:T_DRIFT, k], x[T_DRIFT:, k]).pvalue) for k in range(x.shape[1])]
    return {"seed": int(seed), "delta_e": float(delta_e), "eta": float(eta),
            "h_pre_median": float(np.median(pre)) if pre.size else np.nan,
            "h_post_max": float(post.max()) if post.size else np.nan,
            "peak_excess": peak_excess,
            "n_detections_total": len(det),
            "n_detections_pre": len([d for d in det if d < b_drift]),
            "n_detections_post": len(post_det),
            "detection_delay": delay,
            "px_ks_pvalue_min": float(min(ks))}


# ══════════════════════════════════════════════════════════════════════════════
# Positive control -- without it, "HDDDM saw nothing" and "HDDDM is broken" are one measurement
# ══════════════════════════════════════════════════════════════════════════════
def _control_rung(shift, n_seeds, gamma=None):
    out = []
    for s in range(n_seeds):
        rng = np.random.default_rng(np.random.SeedSequence((ssot.S9_SEED_MASTER, 8, s)))
        x = rng.normal(size=(ssot.S8_N_STEPS, 2))
        x[T_DRIFT:] += shift
        h, det = hdddm(x, gamma=GAMMA if gamma is None else gamma)
        b = T_DRIFT // BATCH
        post = h[b:][np.isfinite(h[b:])]
        pre = h[1:b][np.isfinite(h[1:b])]
        first = next((d for d in det if d >= b), None)
        out.append({"peak_excess": float(post.max() - np.median(pre)),
                    "detected": first is not None,
                    "delay": None if first is None else int(first * BATCH - T_DRIFT)})
    delays = [r["delay"] for r in out if r["delay"] is not None]
    return {"shift": shift, "n_seeds": n_seeds,
            "detection_rate": round(float(np.mean([r["detected"] for r in out])), 4),
            "delay_median": None if not delays else float(np.median(delays)),
            "peak_excess_median": round(float(np.median([r["peak_excess"] for r in out])), 4)}


def gamma_calibration(gammas=(1.0, 1.5, 2.0, 2.5, 3.0, 4.0), n_seeds=20):
    """Why S9_HDDDM_GAMMA is 3 and not the 1 first declared, published rather than asserted.

    `beta = mean(|eps|) + gamma std(|eps|)` at gamma = 1 sits near the 84th percentile of |eps|, so
    it fires on roughly one stationary batch in six. Every firing resets the reference and leaves
    the detector unable to signal for MIN_HISTORY + 1 batches, and a drift landing inside that
    window is missed outright -- which is why the positive control came out non-monotone in the
    shift. The column that settles the choice is the false-alarm one: the repository already fixes
    a convention for it, one false alarm per warm-up (S8_PHT_TARGET_FA)."""
    rows = []
    for g in gammas:
        fa = []
        for s in common.seed_pool(n_seeds):
            _, x, _ = rot.make_rotation_stream(s, 0.25, ETA)
            _, det = hdddm(x, gamma=g)
            fa.append(len([d for d in det if d < T_DRIFT // BATCH]))
        rows.append({"gamma": g,
                     "pre_drift_false_alarms_per_run": round(float(np.mean(fa)), 3),
                     **{f"detect_at_shift_{sh:g}": _control_rung(sh, n_seeds, gamma=g)["detection_rate"]
                        for sh in ssot.S9_HDDDM_CONTROL_SHIFTS}})
    return {"sweep": rows, "selected": ssot.S9_HDDDM_GAMMA,
            "criterion": "the largest gamma is not the target: the choice is the smallest gamma "
                         "whose pre-drift false-alarm count is at or under one per run AND whose "
                         "positive-control ladder is monotone in the shift. Both are read off this "
                         "table, before the rotation measurement is interpreted."}


def positive_control(shifts=None, n_seeds=None):
    """The same HDDDM on streams whose P(X) DOES move: a mean shift on both features from T_DRIFT
    onward, everything else identical.

    Reported as a LADDER, not a single pass/fail. A control placed at the detector's own sensitivity
    boundary measures the boundary, and moving the gate until such a control passes would be
    tuning a threshold to a desired verdict. The verdict therefore gates on the LARGEST rung --
    a shift the implementation must find or be declared broken -- and the smaller rungs are
    published as the sensitivity curve they are."""
    shifts = ssot.S9_HDDDM_CONTROL_SHIFTS if shifts is None else shifts
    n_seeds = ssot.S9_HDDDM_CONTROL_SEEDS if n_seeds is None else n_seeds
    ladder = [_control_rung(sh, n_seeds) for sh in sorted(shifts)]
    top = ladder[-1]
    return {"ladder": ladder, "gate_shift": top["shift"],
            "gate_rate": ssot.S9_HDDDM_CONTROL_GATE,
            "detection_rate": top["detection_rate"],
            "delay_median": top["delay_median"],
            "peak_excess_median": top["peak_excess_median"],
            "verdict": ("SENSITIVE" if top["detection_rate"] >= ssot.S9_HDDDM_CONTROL_GATE
                        else "INSENSITIVE"),
            "reading": "the null reported on the rotation stream is interpretable only beside this "
                       "ladder: the same code, the same batch size, a covariate shift it does find"}


# ══════════════════════════════════════════════════════════════════════════════
# D8
# ══════════════════════════════════════════════════════════════════════════════
def spearman_ci(a, b, cluster, seed=None, n_boot=None):
    """(rho, CI95) with the bootstrap resampling CLUSTERS, not rows.

    X depends on the SEED alone, so the 20 rows a seed contributes carry ONE realisation of the
    feature stream between them. Resampling rows would treat 2 000 observations as independent
    when there are 100, and would divide every interval by roughly sqrt(20) -- which is exactly how
    a null correlation acquires an interval that excludes zero. The design effect is `deff = 20` by
    construction here, and it is integrated by resampling seeds with replacement and taking all
    their rows, rather than by a variance inflation factor applied afterwards."""
    seed = ssot.S9_BOOTSTRAP_SEED if seed is None else seed
    n_boot = ssot.S2BIS_N_BOOTSTRAP if n_boot is None else n_boot
    a, b = np.asarray(a, dtype=np.float64), np.asarray(b, dtype=np.float64)
    cluster = np.asarray(cluster)
    ok = np.isfinite(a) & np.isfinite(b)
    a, b, cluster = a[ok], b[ok], cluster[ok]
    uniq = np.unique(cluster)
    if a.size < 3 or np.ptp(a) == 0 or np.ptp(b) == 0 or uniq.size < 3:
        return {"rho": None, "ci_lo": None, "ci_hi": None, "n": int(a.size),
                "n_clusters": int(uniq.size), "n_dropped": int((~ok).sum()),
                "reason": "degenerate or too few finite pairs"}
    members = [np.flatnonzero(cluster == c) for c in uniq]
    rng = np.random.default_rng(seed)
    reps = np.empty(n_boot)
    for r in range(n_boot):
        pick = rng.integers(0, len(members), size=len(members))
        idx = np.concatenate([members[i] for i in pick])
        reps[r] = stats.spearmanr(a[idx], b[idx]).statistic
    reps = reps[np.isfinite(reps)]
    return {"rho": round(float(stats.spearmanr(a, b).statistic), 4),
            "ci_lo": round(float(np.quantile(reps, 0.025)), 4),
            "ci_hi": round(float(np.quantile(reps, 0.975)), 4),
            "n": int(a.size), "n_clusters": int(uniq.size), "n_dropped": int((~ok).sum()),
            "deff_note": "cluster bootstrap over seeds; rows within a seed share one X",
            "n_bootstrap": int(n_boot), "bootstrap_seed": int(seed)}


def main(which="data"):
    runs_path = ROT_DIR / rot.eta_tag(ETA) / "runs.parquet"
    if not runs_path.exists():
        raise SystemExit(f"[FATAL] {runs_path} absent -- run s8_rotation.py full first")
    runs = pq.read_table(runs_path).to_pandas()
    runs = runs[runs.arm == "full"].copy()
    runs["delta_e"] = runs["delta_e"].round(6)

    pairs = list(zip(runs["seed"].astype(int), runs["delta_e"].astype(float)))
    if which == "smoke":
        pairs = pairs[::101]      # stride coprime with the 100-seed block, so the subsample spans
                                  # SEEDS as well as magnitudes. A stride of 200 lands on one seed
                                  # at 10 magnitudes and every statistic below comes out constant --
                                  # which is the blindness, but measured by accident rather than on
                                  # purpose. `delta_e_invariance` below measures it on purpose.
    print(f"=== T9.3 input-space arm -- HDDDM on the rotation generator, eta = {ETA} ===")
    print(f"    {len(pairs)} runs, batch {BATCH}, gamma {GAMMA}, {ssot.S8_N_STEPS // BATCH} batches "
          f"per run ({T_DRIFT // BATCH} pre-drift)")

    rows = Parallel(n_jobs=-1)(delayed(run_cell)(s, de) for s, de in pairs)
    key = runs.set_index(["seed", "delta_e"])
    for r in rows:
        ctx = key.loc[(r["seed"], round(r["delta_e"], 6))]
        for c in ("tau_erase", "tau_erase_fw", "w_fw", "a_fw", "e_pre", "delta_e_emp"):
            r[c] = float(ctx[c])

    # The sharpest available statement of the blindness, and it is an equality rather than a
    # correlation: X depends on the SEED alone, so at fixed seed every HDDDM statistic must be
    # identical across the whole magnitude grid. Counting distinct values per seed measures that.
    by_seed = {}
    for r in rows:
        by_seed.setdefault(r["seed"], []).append(r)
    inv = {"n_seeds": len(by_seed),
           "magnitudes_per_seed": sorted({len(v) for v in by_seed.values()}),
           "seeds_with_one_distinct_peak_excess":
               sum(len({round(x["peak_excess"], 12) for x in v}) == 1 for v in by_seed.values()),
           "seeds_with_one_distinct_detection_count":
               sum(len({x["n_detections_total"] for x in v}) == 1 for v in by_seed.values()),
           "reading": "at fixed seed the HDDDM statistics are constant across the magnitude grid "
                      "iff the detector saw nothing that the drift changed"}

    # The control is read over the 100 INDEPENDENT feature streams, not over the 2 000 rows: X is
    # a function of the seed, so a row-level rate counts each stream 20 times and its standard
    # error is understated by sqrt(20). Under the null the min of two independent KS p-values
    # rejects at 1 - 0.95^2 = 0.0975, not at 0.05; both the reference rate and the interval are
    # stated so the reading is not done against the wrong number.
    calib = gamma_calibration()
    control = positive_control()
    px_by_seed = {r["seed"]: r["px_ks_pvalue_min"] for r in rows}
    px = np.array(sorted(px_by_seed.values()))
    rate = float(np.mean(px <= 0.05))
    ref = 1.0 - 0.95 ** 2
    se = float(np.sqrt(ref * (1 - ref) / px.size))
    blind = {
        "claim": "P(X) is invariant under the rotation generator, exactly and by construction",
        "source_evidence": "s8_rotation.make_rotation_stream draws x = rng.normal(size=(N_STEPS,2)) "
                           "once per seed, with no dependence on t, Delta_e or eta; only the "
                           "labelling half-plane turns",
        "measured_control": "two-sample KS on each feature, 4000 pre-drift rows against 4000 "
                            "post-drift rows, per INDEPENDENT feature stream (one per seed)",
        "n_independent_streams": int(px.size),
        "px_ks_pvalue_min_median": round(float(np.median(px)), 4),
        "px_ks_reject_rate_at_0p05": round(rate, 4),
        "null_reference_rate": round(ref, 4),
        "deviation_in_se": round((rate - ref) / se, 2),
        "consistent_with_invariance": bool(abs(rate - ref) <= 3 * se),
        "n_runs": len(rows)}

    seeds_col = [r["seed"] for r in rows]
    d8 = {}
    for stat_name in ("peak_excess", "detection_delay"):
        for tau_name in ("tau_erase_fw", "tau_erase"):
            d8[f"{stat_name}__vs__{tau_name}"] = spearman_ci(
                [r[stat_name] for r in rows], [r[tau_name] for r in rows], seeds_col)

    contains_zero = [k for k, v in d8.items()
                     if v["rho"] is not None and v["ci_lo"] <= 0.0 <= v["ci_hi"]]
    computable = [k for k, v in d8.items() if v["rho"] is not None]

    # The verdict keys on an EQUALITY, not on an interval. If every seed yields one and the same
    # HDDDM statistic across the whole magnitude grid, the detector's output is not a function of
    # the drift at all, and a correlation between it and tau_erase has no content to report -- it
    # is the correlation of one stream's noise with an adaptation time measured on another signal.
    # D8 names that case explicitly and forbids dressing it as ABSENT.
    fully_blind = (inv["seeds_with_one_distinct_peak_excess"] == inv["n_seeds"]
                   and inv["seeds_with_one_distinct_detection_count"] == inv["n_seeds"])
    # A null from an insensitive detector is not a result. If the positive control fails, the
    # blindness reading is withheld and the instrument is reported instead.
    if control["verdict"] == "INSENSITIVE":
        fully_blind = False
    verdict = ("INSTRUMENT NOT VALIDATED" if control["verdict"] == "INSENSITIVE"
               else "NOT PRODUCED" if fully_blind
               else ("ABSENT" if len(contains_zero) == len(computable) else "PRESENT"))

    payload = {"which": which, "eta": ETA, "batch": BATCH, "gamma": GAMMA,
               "n_runs": len(rows), "structural_blindness": blind,
               "delta_e_invariance": inv,
               "positive_control": control,
               "gamma_calibration": calib,
               "D8": {"verdict": verdict,
                      "rule": "D8 returns NOT PRODUCED, never a silent ABSENT, when the detector is "
                              "structurally blind to the drift under study: a correlation computed "
                              "between a detector's noise and tau_erase is not evidence that the "
                              "closed-loop reframing survives its test. The correlations are "
                              "reported because D8 asks for them; the verdict rests on the "
                              "blindness.",
                      "spearman": d8},
               "env": common.env_stamp(), "runs": rows}
    tab = OUT_DIR / "tables"
    tab.mkdir(parents=True, exist_ok=True)
    path = tab / f"s9_input_space{'' if which == 'data' else '_' + which}.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=float) + "\n",
                    encoding="utf-8")

    print(f"\n--- P(X) invariance control ---")
    print(f"    {blind['n_independent_streams']} independent feature streams; median min "
          f"p-value {blind['px_ks_pvalue_min_median']}")
    print(f"    reject rate at 0.05: {blind['px_ks_reject_rate_at_0p05']} against a null reference "
          f"of {blind['null_reference_rate']} ({blind['deviation_in_se']:+.2f} SE) -> "
          f"invariance {'HELD' if blind['consistent_with_invariance'] else 'CONTRADICTED'}")
    print(f"\n--- gamma calibration (selected {calib['selected']}) ---")
    print("    " + "  ".join(f"g={r['gamma']}:FA={r['pre_drift_false_alarms_per_run']}"
                             for r in calib["sweep"]))
    print(f"\n--- positive control: the same HDDDM on a real covariate shift ---")
    for r in control["ladder"]:
        print(f"    mean shift {r['shift']:<5} on both features from tau*: detection rate "
              f"{r['detection_rate']:.2f}, median delay {r['delay_median']} steps, "
              f"peak excess {r['peak_excess_median']}")
    print(f"    gate: detection rate at shift {control['gate_shift']} must reach "
          f"{control['gate_rate']} -> {control['verdict']}")
    print(f"\n--- Delta_e invariance of the HDDDM statistics, at fixed seed ---")
    print(f"    {inv['seeds_with_one_distinct_peak_excess']}/{inv['n_seeds']} seeds give ONE "
          f"distinct peak_excess across {inv['magnitudes_per_seed']} magnitudes; "
          f"{inv['seeds_with_one_distinct_detection_count']}/{inv['n_seeds']} give one distinct "
          f"detection count")
    print(f"\n--- HDDDM signal ---")
    print(f"    H pre-drift median {np.median([r['h_pre_median'] for r in rows]):.4f}   "
          f"post-drift max {np.median([r['h_post_max'] for r in rows]):.4f}   "
          f"peak excess median {np.median([r['peak_excess'] for r in rows]):.4f}")
    print(f"    detections: pre {sum(r['n_detections_pre'] for r in rows)}, "
          f"post {sum(r['n_detections_post'] for r in rows)} over {len(rows)} runs")
    print(f"\n--- D8 --- {verdict}")
    for k, v in d8.items():
        print(f"    {k:38s} rho={v['rho']}  CI95 [{v['ci_lo']}, {v['ci_hi']}]  "
              f"n={v['n']} in {v.get('n_clusters')} clusters"
              + (f"  ({v.get('reason')})" if v["rho"] is None else ""))
    print(f"[INFO] wrote {path.relative_to(ssot.ROOT_DIR)}")
    return payload


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data")
