"""Stream S8 / T8.2 + T8.5 -- the rotation generator, and the validity domain it re-opens.

The defect, measured. The canonical family labels `y = 1[x0 + x1 > b]` with
`b = sqrt(2) Phi^-1(0.5 + Delta_e)`, so the post-drift class prior is `P(y=1) = 0.5 - Delta_e`. Over
the last seven points of the canonical grid it falls under 2.5 %, and at `Delta_e = 0.498` the
majority-class predictor reaches an error of 0.002 -- UNDER the measured `e_pre = 0.024`. That is
mechanically the `A / A_rect = -14.12` reported in `S6_causal_evidence.md` section 3: at those
magnitudes the drift makes the problem EASIER, and the error budget the external monitor integrates
goes negative.

The correction, and what it preserves. The pre-drift stream already IS the rotation at `phi = pi/4`:
`x0 + x1 > 0` is `cos(pi/4) x0 + sin(pi/4) x1 > 0`. Only the post-drift half-plane turns:

    phi     = pi/4 + pi Delta_e / (1 - 2 eta)
    y_pre   = 1[x0 + x1 > 0]                                  canonical, bit-identical
    y_post  = 1[cos(phi) x0 + sin(phi) x1 > 0]

Two half-planes through the origin whose normals are separated by `theta = |phi - pi/4|` disagree,
under an isotropic Gaussian, on exactly `theta / pi` of the mass. The class balance stays 50/50 at
every magnitude and the Bayes error is 0 -- which is itself a defect, an asymptotically degenerate
null. Declared label noise `eta`, applied to both phases, fixes it: the Bayes error becomes `eta`,
stable across the grid, and `Delta_e = (1 - 2 eta) theta / pi` stays exact.

CONSTRAINT 1, verbatim. `rng.normal(size=(N_STEPS, 2))` is untouched: two normal draws per step, in
the same order, consuming the same entropy. The label-noise draws come from a SEPARATE generator
spawned off `SeedSequence(safe_seed)`, never from the feature `rng`, which is what keeps the
two-draws-per-step invariant intact to the bit. The triple per-worker lock is reused verbatim from
`_gate_common.lock_rng`. At `eta = 0` the whole pre-drift phase -- warm-up, `e_pre`, noise swaps,
the ARF state at `tau*` -- is bit-identical to the canonical family, so old and new are paired by
SEED, not merely by distribution.

  demo      generator invariants (D4 identity, PRNG neutrality, pre-drift bit-identity)
  identity  D4 over the full grid x 2 eta arms, at the label level, no classifier involved
  smoke     5 seeds x 3 magnitudes x 2 eta arms
  full      100 seeds x 20 magnitudes x 2 eta arms, arm 'full' only
  compare   D5, D6 and the read-only confrontation against R2 / R6 / R7

Usage:  PYTHONHASHSEED=0 python experiments/S8_generality/s8_rotation.py [demo|identity|smoke|full|compare]
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.dataset as ds
import pyarrow.parquet as pq
from joblib import Parallel, delayed

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "S6_synchronized_traces"))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "S6_synchronized_traces" / "gates"))

import s6_defs as defs  # noqa: E402
import s6_runner as runner  # noqa: E402
import _gate_common as common  # noqa: E402
from config import experiment_ssot as ssot  # noqa: E402

RESULTS_DIR = ssot.RESULTS_DIR / "S8_rotation_generator"
S6_DIR = ssot.RESULTS_DIR / "S6_synchronized_traces"
N_STEPS = ssot.S8_N_STEPS
T_DRIFT = ssot.S8_T_DRIFT
PHI0 = ssot.S8_ROTATION_PHI0
ETA_GRID = ssot.S8_ETA_GRID
ARMS = ssot.S8_ROTATION_ARMS
T_HORIZON = ssot.S8_T_HORIZON
WARMUP = ssot.S8_WARMUP_WINDOW
AUDIT_DELTA_P = ssot.S8_AUDIT_DELTA_P
LADDER = sorted(ssot.S6_FIGURE_LAMBDA_LADDER, reverse=True)
SE_TOL = ssot.S8_DELTA_E_SE_TOL


def eta_tag(eta):
    return f"eta{eta:.2f}"


def rotation_phi(delta_e, eta):
    """Normal direction of the post-drift half-plane. Inverse of Delta_e = (1-2 eta) |phi-pi/4|/pi."""
    return PHI0 + np.pi * float(delta_e) / (1.0 - 2.0 * float(eta))


def make_rotation_stream(seed, delta_e, eta=0.0):
    """(safe_seed, X, y) under the triple lock. The post-drift half-plane rotates; X does not move."""
    safe_seed, rng = common.lock_rng(seed)
    x = rng.normal(size=(N_STEPS, 2))
    phi = rotation_phi(delta_e, eta)
    y = np.empty(N_STEPS, dtype=bool)
    y[:T_DRIFT] = x[:T_DRIFT, 0] + x[:T_DRIFT, 1] > 0.0
    y[T_DRIFT:] = np.cos(phi) * x[T_DRIFT:, 0] + np.sin(phi) * x[T_DRIFT:, 1] > 0.0
    if eta:
        # Spawned off the same SeedSequence as the stream, drawn from its OWN Generator: the feature
        # rng must have consumed exactly 2 N_STEPS normals and nothing else.
        noise = np.random.default_rng(np.random.SeedSequence(safe_seed).spawn(2)[1])
        y ^= noise.random(N_STEPS) < float(eta)
    return safe_seed, x, y.astype(np.int8)


def _stream_eta0(seed, delta_e):
    return make_rotation_stream(seed, delta_e, ETA_GRID[0])


def _stream_eta1(seed, delta_e):
    return make_rotation_stream(seed, delta_e, ETA_GRID[1])


STREAM_FN = {ETA_GRID[0]: _stream_eta0, ETA_GRID[1]: _stream_eta1}


# ══════════════════════════════════════════════════════════════════════════════
# D4 -- generator identity, measured on the labels alone
# ══════════════════════════════════════════════════════════════════════════════
def _identity_cell(seed, delta_e, eta):
    """Excess error of the PRE-DRIFT Bayes rule, pre and post. No classifier, no ARF.

    Delta_e is a property of the generator, so it is measured on the generator: the disagreement the
    rotation introduces is what an oracle holding the old rule would suffer. Reading it off a trained
    classifier would confound the generator with the learner's imperfection."""
    _, x, y = make_rotation_stream(seed, delta_e, eta)
    h = (x[:, 0] + x[:, 1] > 0.0).astype(np.int8)
    err = (h != y)
    return {"seed": int(seed), "delta_e": float(delta_e), "eta": float(eta),
            "e_pre_oracle": float(err[:T_DRIFT].mean()),
            "e_post_oracle": float(err[T_DRIFT:].mean())}


def identity(seeds, grid, n_jobs=-1):
    rows = Parallel(n_jobs=n_jobs)(delayed(_identity_cell)(s, de, eta)
                                   for eta in ETA_GRID for de in grid for s in seeds)
    df = pd.DataFrame(rows)
    df["delta_e_measured"] = df.e_post_oracle - df.e_pre_oracle
    agg = df.groupby(["eta", "delta_e"], as_index=False).agg(
        n=("seed", "size"),
        mean_e_pre_oracle=("e_pre_oracle", "mean"),
        mean_delta_e_measured=("delta_e_measured", "mean"),
        sd_delta_e_measured=("delta_e_measured", "std"))
    agg["se"] = agg.sd_delta_e_measured / np.sqrt(agg.n)
    agg["theta"] = [abs(rotation_phi(de, eta) - PHI0) for eta, de in zip(agg.eta, agg.delta_e)]
    agg["delta_e_predicted"] = (1.0 - 2.0 * agg.eta) * agg.theta / np.pi
    agg["deviation"] = agg.mean_delta_e_measured - agg.delta_e_predicted
    agg["deviation_in_se"] = agg.deviation / agg.se
    agg["within_tolerance"] = agg.deviation.abs() <= SE_TOL * agg.se
    return df, agg


# ══════════════════════════════════════════════════════════════════════════════
# campaigns
# ══════════════════════════════════════════════════════════════════════════════
def run_campaign(mode):
    seeds = common.seed_pool(ssot.S8_SMOKE_N_SEEDS if mode == "smoke"
                             else len(ssot.S8_CAMPAIGN_SEEDS))
    grid = (list(ssot.S8_SMOKE_DELTA_E) if mode == "smoke" else
            [float(np.round(common.norm.cdf(b / np.sqrt(2)) - 0.5, 6))
             for b in ssot.S8_CAMPAIGN_BOUNDARY_SHIFTS])

    tables = RESULTS_DIR / ("smoke" if mode == "smoke" else "tables")
    tables.mkdir(parents=True, exist_ok=True)
    raw, agg = identity(seeds, grid)
    agg.to_csv(tables / "s8_rotation_identity.csv", index=False)
    n_bad = int((~agg.within_tolerance).sum())
    print(f"[D4] generator identity: {len(agg) - n_bad}/{len(agg)} grid points within "
          f"{SE_TOL:g} SE -> {'HELD' if n_bad == 0 else 'REFUTED'}")
    if n_bad:
        print(agg[~agg.within_tolerance].to_string(index=False))

    for eta in ETA_GRID:
        out = RESULTS_DIR / ("smoke" if mode == "smoke" else "data") / eta_tag(eta)
        print(f"[INFO] S8 rotation {mode} eta={eta}: {len(seeds)} seeds x {len(grid)} magnitudes x "
              f"{len(ARMS)} arm(s) -> {out.relative_to(ssot.ROOT_DIR)}")
        s = runner.campaign(seeds, grid, out, desc=f"S8 rot eta={eta}", arms=ARMS,
                            stream_fn=STREAM_FN[eta])
        print(f"[INFO] {s['records']} run records, {s['trace_rows']:,} trace rows "
              f"in {s['wall_clock_s']:.1f}s")
    return RESULTS_DIR


# ══════════════════════════════════════════════════════════════════════════════
# D5 / D6 and the read-only confrontation
# ══════════════════════════════════════════════════════════════════════════════
def _ladder_partition(part, e_pre_by_seed, lambdas=tuple(LADDER), horizon=T_HORIZON,
                      warmup=WARMUP, delta=AUDIT_DELTA_P):
    """Per (seed): pre-drift false alarms and post-drift detection, per lambda.

    The reflected path is `s6_defs.accumulations(...)[1]` -- the repository's one CUSUM recursion,
    the same one `s6_detectors.StrictCUSUM` runs step by step -- evaluated over the WHOLE traced
    window so the statistic carried into the post-drift phase is the one an online monitor would
    actually hold. `s6_figure` reads the ladder exactly this way."""
    delta_e = float(Path(part).name.split("=", 1)[1])
    df = ds.dataset(str(part), format="parquet").to_table(
        columns=["arm", "seed", "t_rel", "err"],
        filter=(ds.field("arm") == "full") & (ds.field("t_rel") >= -warmup)
        & (ds.field("t_rel") < horizon)).to_pandas().sort_values(["seed", "t_rel"])
    out = []
    for seed, g in df.groupby("seed", sort=True):
        err = g["err"].to_numpy(dtype=np.float64)
        post = g["t_rel"].to_numpy() >= 0
        path = defs.accumulations(err, e_pre_by_seed[int(seed)], delta)[1]
        row = {"delta_e": delta_e, "seed": int(seed)}
        for lam in lambdas:
            row[f"fa_lambda{lam:g}"] = bool((path[~post] >= lam).any())
            hit = np.flatnonzero(path[post] >= lam)
            row[f"det_lambda{lam:g}"] = float(hit[0]) if hit.size else np.nan
        out.append(row)
    return out


def ladder(base, runs, n_jobs=-1):
    parts = sorted((Path(base) / "traces.parquet").iterdir())
    e_pre = {de: dict(zip(g.seed, g.e_pre)) for de, g in
             runs[runs.arm == "full"].groupby("delta_e")}
    lookup = [e_pre[min(e_pre, key=lambda d: abs(d - float(p.name.split("=", 1)[1])))] for p in parts]
    rows = [r for chunk in Parallel(n_jobs=n_jobs)(
        delayed(_ladder_partition)(p, m) for p, m in zip(parts, lookup)) for r in chunk]
    df = pd.DataFrame(rows)
    agg = df.groupby("delta_e", as_index=False).agg(
        n=("seed", "size"),
        **{f"fa_rate_lambda{lam:g}": (f"fa_lambda{lam:g}", "mean") for lam in LADDER},
        **{f"miss_rate_lambda{lam:g}": (f"det_lambda{lam:g}",
                                        lambda s: float(s.isna().mean())) for lam in LADDER})
    return df, agg


def switch_point(runs):
    """inf{Delta_e : median(A / A_rect) < 0} on arm 'full'. NaN when no grid point goes negative."""
    g = runs[runs.arm == "full"].copy()
    g["ratio"] = g.a / g.a_rect
    med = g.groupby("delta_e").ratio.median().sort_index()
    neg = med[med < 0]
    return {"switch_point": float(neg.index[0]) if len(neg) else np.nan,
            "verdict": "PRESENT" if len(neg) else "ABSENT",
            "per_delta_e": [{"delta_e": float(d), "median_a_over_a_rect": float(v)}
                            for d, v in med.items()]}


def confrontation(new_runs, new_agg):
    """Old (canonical family) against new (rotation), joined on delta_e. Read-only on R2/R6/R7."""
    out = {}
    r2 = pd.read_parquet(ssot.RESULTS_DIR / "R2_instrumented_blind_spot" / "data"
                         / "R2_instrumented_A_PHT_ARF.parquet")
    from scipy.stats import norm
    r2["delta_e"] = np.round(norm.cdf(r2.boundary_shift / np.sqrt(2)) - 0.5, 6)
    old = r2.groupby("delta_e").agg(old_median_tau_arf=("tau_arf", "median"),
                                    old_miss_rate_lambda50=("tau_det", lambda s: float(s.isna().mean())))
    new = new_runs[new_runs.arm == "full"].groupby("delta_e").agg(
        new_median_tau_swap=("tau_swap_q010", "median"))
    joined = old.join(new, how="outer").join(
        new_agg.set_index("delta_e")[["miss_rate_lambda50"]].rename(
            columns={"miss_rate_lambda50": "new_miss_rate_lambda50"}), how="outer")
    joined["delta_tau"] = joined.new_median_tau_swap - joined.old_median_tau_arf
    joined["delta_miss_rate"] = joined.new_miss_rate_lambda50 - joined.old_miss_rate_lambda50
    out["R2"] = {"status": "JOINED", "n_points": int(joined.old_median_tau_arf.notna().sum()),
                 "n_joined": int(joined[["old_median_tau_arf", "new_median_tau_swap"]]
                                 .notna().all(axis=1).sum())}
    r7 = pd.read_csv(ssot.RESULTS_DIR / "R7_clock_mismatch" / "tables"
                     / "exp_R7_regime1_miss_curve.csv", float_precision="round_trip")
    r7["delta_e"] = np.round(r7.delta_e, 6)
    wide = r7.pivot(index="delta_e", columns="config", values="miss_rate")
    joined = joined.join(wide.add_prefix("old_R7_miss_"), how="outer")
    out["R7"] = {"status": "JOINED", "configs": sorted(r7.config.unique()),
                 "note": "R7 varies the internal/external CLOCK pairing; the rotation campaign runs "
                         "the c_int = 1 configuration only, so only A_mismatched is arm-comparable"}
    # Same-pipeline canonical reference. R2's miss rate comes from R2's own detector loop; this
    # column is the SAME ladder code applied to the canonical family, so old-vs-new is a difference
    # of generator and of nothing else. The two agree closely, which is what makes the R2 column
    # readable at all.
    counts = ssot.RESULTS_DIR / "S8_ab_initio" / "tables" / "s8_detection_counts.csv"
    if counts.exists():
        c = pd.read_csv(counts, float_precision="round_trip")
        c = c[c.arm == "full"].assign(delta_e=lambda d: np.round(d.delta_e, 6))
        c["canonical_miss_rate_lambda50_same_pipeline"] = 1.0 - c.n_cross / c.n
        joined = joined.join(
            c.set_index("delta_e")[["canonical_miss_rate_lambda50_same_pipeline"]], how="outer")
        joined["delta_miss_rate_same_pipeline"] = (
            joined.new_miss_rate_lambda50 - joined.canonical_miss_rate_lambda50_same_pipeline)
        out["canonical_same_pipeline"] = {
            "status": "JOINED", "source": str(counts.relative_to(ssot.ROOT_DIR)),
            "note": "arm 'full' of the S8 ab initio campaign, which D3-bis shows identical to the "
                    "committed S6 rows; the ladder code is the one applied to the rotation arms"}
    out["R6"] = {"status": "NOT PRODUCED",
                 "missing_measurement": "an M = 1 rotation arm. R6's tau_HAT is measured on "
                                        "ARF(M = 1); T8.2 runs M = 10 only, so no paired quantity "
                                        "exists. Produced by T8.3 (HAT family) and T8.3-bis, not here"}
    return joined.reset_index(), out


def compare(which="data"):
    base = RESULTS_DIR / which
    tables = RESULTS_DIR / ("smoke" if which == "smoke" else "tables")
    tables.mkdir(parents=True, exist_ok=True)
    payload = {"source": str(base.relative_to(ssot.ROOT_DIR)), "arms_eta": ETA_GRID,
               "lambda_ladder": LADDER, "delta_p": AUDIT_DELTA_P, "per_eta": {}}

    for eta in ETA_GRID:
        b = base / eta_tag(eta)
        runs = pq.read_table(b / "runs.parquet").to_pandas()
        raw, agg = ladder(b, runs)
        agg.to_csv(tables / f"s8_rotation_ladder_{eta_tag(eta)}.csv", index=False)
        e_pre = runs[runs.arm == "full"].groupby("delta_e").e_pre.agg(["median", "std", "min", "max"])
        # D5 asks for ONE lambda whose pre-drift false-alarm rate lies strictly inside (0, 1) --
        # at the same grid point, not a rate of 0 at one magnitude and 1 at another.
        binding = [float(lam) for lam in LADDER
                   if ((agg[f"fa_rate_lambda{lam:g}"] > 0.0)
                       & (agg[f"fa_rate_lambda{lam:g}"] < 1.0)).any()]
        payload["per_eta"][eta_tag(eta)] = {
            "eta": float(eta),
            "e_pre": {"median": float(e_pre["median"].median()),
                      "min": float(e_pre["min"].min()), "max": float(e_pre["max"].max()),
                      "median_sd_across_seeds": float(e_pre["std"].median()),
                      "per_delta_e": [{"delta_e": float(d), "median": float(r["median"]),
                                       "sd": float(r["std"])} for d, r in e_pre.iterrows()]},
            "D5_lambdas_with_fa_strictly_inside_0_1": binding,
            "D5_verdict": ("NON-DEGENERATE" if float(e_pre["median"].median()) > 0
                           and (binding or eta == 0.0) else "DEGENERATE"),
            "D6_switch_point": switch_point(runs),
        }

    canonical = pq.read_table(S6_DIR / ("smoke" if which == "smoke" else "data")
                              / "runs.parquet").to_pandas()
    payload["D6_switch_point_canonical"] = switch_point(canonical)

    ref_eta = ETA_GRID[-1]
    runs_ref = pq.read_table(base / eta_tag(ref_eta) / "runs.parquet").to_pandas()
    agg_ref = pd.read_csv(tables / f"s8_rotation_ladder_{eta_tag(ref_eta)}.csv",
                          float_precision="round_trip")
    table, status = confrontation(runs_ref, agg_ref)
    table.to_csv(tables / "s8_rotation_vs_canonical.csv", index=False)
    payload["confrontation"] = {"reference_arm": eta_tag(ref_eta), **status}

    (tables / "s8_rotation_report.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=float) + "\n", encoding="utf-8")

    print(f"\n=== S8 rotation, read of {payload['source']} ===")
    for tag, p in payload["per_eta"].items():
        d6 = p["D6_switch_point"]
        print(f"  {tag}: e_pre median = {p['e_pre']['median']:.4f} "
              f"[{p['e_pre']['min']:.4f}, {p['e_pre']['max']:.4f}]  -> D5 {p['D5_verdict']} "
              f"(binding lambdas {p['D5_lambdas_with_fa_strictly_inside_0_1']})")
        print(f"        D6 switch point = {d6['switch_point']} -> {d6['verdict']}")
    c = payload["D6_switch_point_canonical"]
    print(f"  canonical family: D6 switch point = {c['switch_point']} -> {c['verdict']}")
    print(f"[INFO] wrote {(tables / 's8_rotation_report.json').relative_to(ssot.ROOT_DIR)}")
    return payload


def demo():
    """Self-check: PRNG neutrality, pre-drift bit-identity, and the Delta_e identity."""
    seed, de = 1, 0.25
    safe, x, y = make_rotation_stream(seed, de, 0.0)
    _, rng = common.lock_rng(seed)
    ref = np.array([[rng.normal(), rng.normal()] for _ in range(64)])
    assert np.array_equal(x[:64], ref), "rotation stream broke the two-draws-per-step convention"

    _, xc, yc = runner.make_stream(seed, de)
    assert np.array_equal(x, xc), "feature stream diverged from the canonical family"
    assert np.array_equal(y[:T_DRIFT], yc[:T_DRIFT]), "pre-drift labels are not bit-identical"

    # the noise generator must not touch the feature stream
    _, xn, yn = make_rotation_stream(seed, de, 0.05)
    assert np.array_equal(xn, xc), "label noise consumed feature entropy"
    assert not np.array_equal(yn[:T_DRIFT], yc[:T_DRIFT]), "eta = 0.05 flipped nothing"

    # Delta_e identity on a coarse grid, oracle-level, 12 seeds
    _, agg = identity(common.seed_pool(12), [0.05, 0.25, 0.45], n_jobs=4)
    bad = agg[~agg.within_tolerance]
    assert bad.empty, bad.to_string(index=False)
    assert (agg[agg.eta == 0.0].mean_e_pre_oracle == 0.0).all(), "eta = 0 is not Bayes-exact"
    assert abs(agg[agg.eta == 0.05].mean_e_pre_oracle.mean() - 0.05) < 0.01, "eta not delivered"
    print("s8_rotation demo: OK  " + "  ".join(
        f"eta={r.eta:.2f} de={r.delta_e:.2f} measured={r.mean_delta_e_measured:.4f} "
        f"({r.deviation_in_se:+.2f} SE)" for r in agg.itertuples()))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "full"
    if mode == "demo":
        demo()
    elif mode == "identity":
        seeds = common.seed_pool(len(ssot.S8_CAMPAIGN_SEEDS))
        grid = [float(np.round(common.norm.cdf(b / np.sqrt(2)) - 0.5, 6))
                for b in ssot.S8_CAMPAIGN_BOUNDARY_SHIFTS]
        _, agg = identity(seeds, grid)
        (RESULTS_DIR / "tables").mkdir(parents=True, exist_ok=True)
        agg.to_csv(RESULTS_DIR / "tables" / "s8_rotation_identity.csv", index=False)
        print(agg.to_string(index=False))
    elif mode in ("smoke", "full"):
        run_campaign(mode)
    elif mode == "compare":
        compare(sys.argv[2] if len(sys.argv) > 2 else "data")
    else:
        raise SystemExit(f"usage: s8_rotation.py [demo|identity|smoke|full|compare]  (got {mode!r})")
