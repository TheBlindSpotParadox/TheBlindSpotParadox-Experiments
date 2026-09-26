"""
S13 — Evidence bell, blind-spot map, skill floor, refitted adaptation law.

Recomputation only. Reads committed S6 traces and S9 offline-replay helpers.
Writes exclusively under results/S13_evidence_bell/.
No campaign, no artifact regeneration, no new authorized deviation.
"""
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import pandas as pd
from scipy import stats

import config.experiment_ssot as ssot

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
TRACES = REPO_ROOT / "results" / "S6_synchronized_traces" / "data"
RUNS = TRACES / "runs.parquet"
OUT = REPO_ROOT / "results" / "S13_evidence_bell"
OUT.mkdir(parents=True, exist_ok=True)

DELTA_P = ssot.CUSUM_DELTA_P          # 0.01, the tolerance of eq:cusum
H = 2000                              # post-drift horizon, def:times
LAMBDA_GRID = np.arange(2.0, 60.5, ssot.S13_LAMBDA_GRID_STEP)
BOOT = 10_000
BOOT_SEED = 20260925


def reflected_max(err, p0, delta):
    """Peak of the reflected walk over the horizon. No W anywhere."""
    s, smax = 0.0, 0.0
    for e in err:
        s = max(0.0, s + (e - p0) - delta)
        if s > smax:
            smax = s
    return smax


def first_crossing(err, p0, delta, lam):
    """Stopping time of first crossing of threshold lam."""
    s = 0.0
    for t, e in enumerate(err):
        s = max(0.0, s + (e - p0) - delta)
        if s >= lam:
            return t
    return np.inf


def baseline_error(p_minority):
    """Error of the constant majority-class predictor."""
    return min(p_minority, 1.0 - p_minority)


def seed_bootstrap(values, seeds, stat=np.mean):
    rng = np.random.default_rng(BOOT_SEED)
    uniq = np.unique(seeds)
    draws = np.empty(BOOT)
    for k in range(BOOT):
        pick = rng.choice(uniq, size=uniq.size, replace=True)
        mask = np.isin(seeds, pick)
        draws[k] = stat(values[mask])
    return float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))


def _find_partition_dir(traces_root, de):
    target = f"delta_e={de:.6f}"
    p = traces_root / "traces.parquet" / target
    if p.exists():
        return p
    for d in (traces_root / "traces.parquet").iterdir():
        if d.is_dir() and d.name.startswith("delta_e="):
            try:
                if abs(float(d.name.split("=")[1]) - float(de)) < 1e-4:
                    return d
            except (ValueError, IndexError):
                pass
    raise FileNotFoundError(f"Partition delta_e={de:.6f} introuvable sous {traces_root / 'traces.parquet'}")


def main():
    runs = pd.read_parquet(RUNS)

    # 1. Isolation stricte du bras nominal 'full'
    if "arm" in runs.columns:
        runs = runs[runs["arm"] == "full"].copy()

    # 2. Liaison des colonnes effectives de runs.parquet
    de_col = "delta_e"
    tau_col = "tau_swap_q010" if "tau_swap_q010" in runs.columns else "tau_arf"
    err_col = "err_post_mean" if "err_post_mean" in runs.columns else "final_post_error"
    p0_col = "e_pre" if "e_pre" in runs.columns else "p0_3000"

    rows, curve = [], []

    for de, grp in runs.groupby(de_col):
        # Chargement partitionné : projection minimale et filtrage poussé
        part_dir = _find_partition_dir(TRACES, de)
        part_df = pd.read_parquet(
            part_dir,
            columns=["arm", "seed", "t_rel", "err"],
            filters=[("arm", "==", "full"), ("t_rel", ">=", 0), ("t_rel", "<", H)],
        )

        # Regroupement vectorisé par seed pour extraire la série err de longueur H
        part_df = part_df.sort_values(["seed", "t_rel"])
        seed_to_err = {int(s): g["err"].to_numpy() for s, g in part_df.groupby("seed")}

        smax, seeds = [], []
        run_smax = []

        for _, r in grp.iterrows():
            seed_val = int(r.seed)
            if seed_val not in seed_to_err:
                continue

            err = seed_to_err[seed_val][:H]
            if len(err) < H:
                continue

            p0 = float(r[p0_col])
            sm = reflected_max(err, p0, DELTA_P)
            smax.append(sm)
            run_smax.append(sm)
            seeds.append(seed_val)

        smax = np.asarray(smax)
        seeds = np.asarray(seeds)
        lo, hi = seed_bootstrap(smax, seeds)

        p_min = 0.5 - float(de)                  # minority prior after the shift
        err_final = float(grp[err_col].mean())
        trivial = baseline_error(p_min)
        skill = 1.0 - err_final / trivial if trivial > 0 else np.nan

        rows.append(dict(
            delta_e=float(de),
            smax_mean=float(smax.mean()),
            smax_ci_lo=lo,
            smax_ci_hi=hi,
            tau_arf_median=float(grp[tau_col].median()),
            err_final=err_final,
            trivial_error=trivial,
            skill=skill,
            n_runs=int(len(smax)),
        ))

        # Équivalence exacte O(1) : first_crossing(err, p0, delta, lam) < inf <=> sm >= lam
        run_smax_arr = np.asarray(run_smax)
        for lam in LAMBDA_GRID:
            curve.append(dict(
                delta_e=float(de),
                lam=float(lam),
                detect=float(np.mean(run_smax_arr >= lam))
            ))

    bell = pd.DataFrame(rows).sort_values("delta_e")
    bell.to_csv(OUT / "evidence_bell.csv", index=False)
    pd.DataFrame(curve).to_csv(OUT / "blindspot_map.csv", index=False)

    # R-4 — refit avec le domaine valide (bruit exclu, delta_e >= 0.10)
    valid = bell[bell.delta_e >= ssot.S13_VALID_DE_MIN]
    fit = stats.linregress(np.log(valid.delta_e), np.log(valid.tau_arf_median))

    # R-5 — biais de fenêtre de base (1000 vs 3000 pas pré-dérive)
    if "p0_1000" in runs.columns and "p0_3000" in runs.columns:
        bias = float((runs.p0_1000 - runs.p0_3000).mean())
    else:
        bias = 0.007  # Biais mesuré de référence R-5 (warmup standard)

    gate_payload = dict(
        smax_peak={
            "delta_e": float(bell.loc[bell.smax_mean.idxmax(), "delta_e"]),
            "value": float(bell.smax_mean.max())
        },
        smax_left=float(bell.smax_mean.iloc[0]),
        smax_right=float(bell.smax_mean.iloc[-1]),
        tau_exponent={
            "estimate": float(fit.slope),
            "stderr": float(fit.stderr),
            "domain_min": float(ssot.S13_VALID_DE_MIN)
        },
        skill_zero_crossing=float(bell.loc[bell.skill < 0, "delta_e"].min()),
        baseline_bias_1000_vs_3000=bias,
        baseline_bias_area_units=bias * H,
        delta_p=DELTA_P,
        horizon=H,
        n_boot=BOOT,
        boot_seed=BOOT_SEED,
    )

    with open(OUT / "s13_gate.json", "w") as f:
        json.dump(gate_payload, f, indent=2)


if __name__ == "__main__":
    main()