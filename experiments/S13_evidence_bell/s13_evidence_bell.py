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
# Robustness of the quadratic onset term to the points a reader would question first: the
# leftmost magnitude (highest leverage) and the six largest (medians quantised to half-steps).
CURVATURE_SUBSETS = {"all": slice(0, None), "without the leftmost point": slice(1, None),
                     "without the six largest magnitudes": slice(0, -6), "without both": slice(1, -6)}
CURVATURE_BLOCKS = (slice(0, 6), slice(6, 12))


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


def _baseline_window_bias(traces_root, runs, horizon):
    """Pre-drift baseline bias between a 1000-step and a 3000-step window.

    Measured from the t_rel < 0 rows of the committed traces.
    If the corpus lacks 3000 pre-drift steps, returns (None, 'uncomputable_insufficient_warmup', 0)
    so the gap is formally recorded in the gate rather than masked by a placeholder.
    """
    diffs = []
    for de, _ in runs.groupby("delta_e"):
        part = pd.read_parquet(
            _find_partition_dir(traces_root, de),
            columns=["arm", "seed", "t_rel", "err"],
            filters=[("arm", "==", "full"), ("t_rel", "<", 0)],
        )
        if part.empty:
            return None, "uncomputable_empty_predrift", 0
        for _, g in part.groupby("seed"):
            e = g.sort_values("t_rel")["err"].to_numpy()
            if len(e) < 3000:
                return None, "uncomputable_insufficient_warmup", int(len(e))
            diffs.append(float(e[-1000:].mean() - e[-3000:].mean()))
    return float(np.mean(diffs)), "measured_from_traces", len(diffs)


def _skill(err, trivial):
    return 1.0 - err / trivial if trivial > 0 else float("nan")


def _first_negative(bell, col):
    """First delta_e where the column turns negative, None if it never does.

    None (JSON null) rather than NaN: the gate must stay strict JSON, and an
    absent crossing is a declared outcome, not a missing value.
    """
    neg = bell.loc[bell[col] < 0, "delta_e"]
    return float(neg.min()) if len(neg) else None


def _bootstrap_argmax(bell, n_boot=2000):
    """Posterior mass on each amplitude being the mode of the bell."""
    rng = np.random.default_rng(BOOT_SEED + 1)
    means = bell["smax_mean"].to_numpy()
    half = ((bell["smax_ci_hi"] - bell["smax_ci_lo"]) / 3.92).to_numpy()
    counts = np.zeros(len(means))
    for _ in range(n_boot):
        counts[int(np.argmax(rng.normal(means, half)))] += 1
    return {float(d): float(c / n_boot)
            for d, c in zip(bell["delta_e"], counts)}


def _bootstrap_tau_exponent(runs, de_col, tau_col, de_min, n_boot=2000, seed=BOOT_SEED + 2):
    """Seed-level bootstrap confidence interval for adaptation time slope."""
    valid_runs = runs[runs[de_col] >= de_min].copy()
    uniq_seeds = np.unique(valid_runs["seed"].to_numpy())
    des = np.sort(valid_runs[de_col].unique())
    log_des = np.log(des)
    rng = np.random.default_rng(seed)
    slopes = np.empty(n_boot)

    grouped = {de: g.set_index("seed")[tau_col] for de, g in valid_runs.groupby(de_col)}

    for b in range(n_boot):
        boot_seeds = rng.choice(uniq_seeds, size=len(uniq_seeds), replace=True)
        boot_medians = [np.median(grouped[de].reindex(boot_seeds).dropna().to_numpy()) for de in des]
        slope, _, _, _, _ = stats.linregress(log_des, np.log(boot_medians))
        slopes[b] = slope

    return float(np.percentile(slopes, 2.5)), float(np.percentile(slopes, 97.5))


def _detector_clocks():
    """R-9 — effective internal-detector configuration of both onset arms.

    The floor comparison across arms (HAT ~50 vs ARF ~29 steps) is
    interpretable only if both run their internal detectors on the same
    clock; a cadence mismatch would make the floor ratio a test-sampling
    artifact, not an ensemble effect.
    """
    from river import drift as _drift
    from river.forest import ARFClassifier as _ARF

    def arm(n_models, clock):
        det = _drift.ADWIN(clock=clock)
        arf = _ARF(n_models=n_models, seed=0,
                   drift_detector=_drift.ADWIN(clock=clock),
                   warning_detector=_drift.ADWIN(clock=clock))
        return {
            "n_models": int(n_models),
            "adwin_clock": int(det.clock),
            "adwin_delta": float(det.delta),
            "adwin_min_window_length": int(det.min_window_length),
            "adwin_grace_period": int(det.grace_period),
            "arf_grace_period": int(arf.grace_period),
        }

    equal = bool(ssot.S6_C_INT == ssot.R6_C_INT)
    return {
        "arf_arm_S6_full": arm(ssot.N_MODELS, ssot.S6_C_INT),
        "hat_arm_R6": arm(ssot.R6_N_MODELS, ssot.R6_C_INT),
        "clocks_equal": equal,
        "verdict": "identical_clocks" if equal else "clock_mismatch",
    }


def _segmented_fit(des, medians, min_side=3, fixed_k=None):
    """R-8 — two-piece onset model with the breakpoint estimated, not chosen.

    log tau = a + b log(de) for de <= de_star, constant after (continuity
    imposed: c = a + b log de_star). For each candidate grid point with at
    least min_side points on each side, (a, b) is solved by OLS on the
    augmented design and de_star minimises the residual sum of squares.
    Pre-registered in docs/prompts/2026 09 26 - 45 - R-8 pre-registration
    segmented onset regression.md. fixed_k holds the breakpoint at one grid
    index (post-hoc diagnostic, report 50).
    """
    x = np.log(np.asarray(des, dtype=float))
    y = np.log(np.asarray(medians, dtype=float))
    n = len(x)
    best = None
    for k in (range(min_side - 1, n - min_side) if fixed_k is None else [fixed_k]):
        xs = np.concatenate([x[: k + 1], np.full(n - k - 1, x[k])])
        X = np.column_stack([np.ones(n), xs])
        coef, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
        sse = float(((y - X @ coef) ** 2).sum())
        if best is None or sse < best["sse"]:
            a, b = float(coef[0]), float(coef[1])
            best = {"de_star": float(des[k]), "a": a, "b": b,
                    "floor": a + b * float(x[k]), "sse": sse}
    return best


def _pooled_sse(des, medians):
    """Residual sum of squares of the one-piece power law on the same medians."""
    x = np.log(np.asarray(des, dtype=float))
    y = np.log(np.asarray(medians, dtype=float))
    r = stats.linregress(x, y)
    return float(((y - (r.intercept + r.slope * x)) ** 2).sum())


def _bootstrap_segmented(runs, de_col, tau_col, de_min, n_boot=2000,
                         seed=BOOT_SEED + 6, min_side=3, fixed_k=None):
    """Seed bootstrap CIs for the segmented fit, breakpoint re-estimated per draw
    unless fixed_k holds it."""
    valid_runs = runs[runs[de_col] >= de_min].copy()
    uniq_seeds = np.unique(valid_runs["seed"].to_numpy())
    des = np.sort(valid_runs[de_col].unique())
    grouped = {de: g.set_index("seed")[tau_col] for de, g in valid_runs.groupby(de_col)}
    rng = np.random.default_rng(seed)
    draws = np.empty((n_boot, 3))
    for i in range(n_boot):
        boot_seeds = rng.choice(uniq_seeds, size=len(uniq_seeds), replace=True)
        meds = [np.median(grouped[de].reindex(boot_seeds).dropna().to_numpy()) for de in des]
        fit = _segmented_fit(des, meds, min_side, fixed_k)
        draws[i] = (fit["b"], fit["floor"], fit["de_star"])
    lo = np.percentile(draws, 2.5, axis=0)
    hi = np.percentile(draws, 97.5, axis=0)
    return {
        "exponent_ci": [float(lo[0]), float(hi[0])],
        "floor_ci": [float(lo[1]), float(hi[1])],
        "de_star_ci": [float(lo[2]), float(hi[2])],
    }


def _bootstrap_curvature(runs, de_col, tau_col, de_min, n_boot=2000, seed=BOOT_SEED + 9):
    """Seed bootstrap of the log-log slope between consecutive grid points, of c2 in
    ln(median) = c0 + c1 ln(de) + c2 ln(de)^2 on each of CURVATURE_SUBSETS, and of the difference
    of the OLS slopes over the two CURVATURE_BLOCKS; returns the (lo, hi) percentiles of each."""
    valid_runs = runs[runs[de_col] >= de_min].copy()
    uniq_seeds = np.unique(valid_runs["seed"].to_numpy())
    des = np.sort(valid_runs[de_col].unique())
    x = np.log(des)
    grouped = {de: g.set_index("seed")[tau_col] for de, g in valid_runs.groupby(de_col)}
    rng = np.random.default_rng(seed)
    slopes = np.empty((n_boot, len(des) - 1))
    quad = np.empty((n_boot, len(CURVATURE_SUBSETS)))
    block_diff = np.empty(n_boot)
    for i in range(n_boot):
        boot_seeds = rng.choice(uniq_seeds, size=len(uniq_seeds), replace=True)
        y = np.log([np.median(grouped[de].reindex(boot_seeds).dropna().to_numpy()) for de in des])
        slopes[i] = np.diff(y) / np.diff(x)
        quad[i] = [np.polyfit(x[s], y[s], 2)[0] for s in CURVATURE_SUBSETS.values()]
        first, second = (np.polyfit(x[s], y[s], 1)[0] for s in CURVATURE_BLOCKS)
        block_diff[i] = first - second
    return tuple(np.percentile(a, [2.5, 97.5], axis=0) for a in (slopes, quad, block_diff))


def _quad_ols(x, y):
    """c2 of y = c0 + c1 x + c2 x^2 and its OLS standard error, s^2 (X'X)^-1."""
    X = np.column_stack([np.ones_like(x), x, x ** 2])
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    s2 = float(((y - X @ beta) ** 2).sum()) / (len(x) - 3)
    return float(beta[2]), float(np.sqrt(s2 * np.linalg.inv(X.T @ X)[2, 2]))


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
        run_err_converged = []
        run_err_converged_1000 = []
        run_n_err_200 = []
        run_n_err_1000 = []

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
            # Converged error: mean over the last 200 steps of the post-drift
            # horizon, matching the students' final_post_error estimator so
            # the two campaigns are comparable. The 1000-step window (R-6)
            # widens the comparison at the degenerate end, where the 200-step
            # window carries too few error events to separate the ensemble
            # from the trivial floor.
            run_err_converged.append(float(err[H - 200 :].mean()))
            run_err_converged_1000.append(float(err[H - 1000 :].mean()))
            run_n_err_200.append(int(err[H - 200 :].sum()))
            run_n_err_1000.append(int(err[H - 1000 :].sum()))

        smax = np.asarray(smax)
        seeds = np.asarray(seeds)
        lo, hi = seed_bootstrap(smax, seeds)

        p_min = 0.5 - float(de)                  # minority prior after the shift
        trivial = baseline_error(p_min)
        err_episode = float(grp["err_post_mean"].mean()) if "err_post_mean" in grp.columns else float(grp[err_col].mean())
        if "final_post_error" in grp.columns:
            err_converged = float(grp["final_post_error"].mean())
        else:
            err_converged = float(np.mean(run_err_converged))
        skill_episode = _skill(err_episode, trivial)
        skill_converged = _skill(err_converged, trivial)
        # Seed bootstrap CI for the converged skill: the "no detectable
        # advantage" claim at the degenerate end must cite a committed
        # interval, not a session-side computation.
        errc = np.asarray(run_err_converged)
        if trivial > 0 and len(errc):
            idx = np.random.default_rng(BOOT_SEED + 3).integers(0, len(errc), size=(BOOT, len(errc)))
            skill_c_lo, skill_c_hi = np.percentile(
                1.0 - errc[idx].mean(axis=1) / trivial, [2.5, 97.5]
            )
        else:
            skill_c_lo = skill_c_hi = float("nan")

        # R-6 — widened converged window (last 1000 steps) with its own CI:
        # an equality claim at the degenerate end must carry the number of
        # events it rests on, and the 200-step window carries too few.
        errc1000 = np.asarray(run_err_converged_1000)
        err_converged_1000 = float(errc1000.mean())
        skill_converged_1000 = _skill(err_converged_1000, trivial)
        if trivial > 0 and len(errc1000):
            idx = np.random.default_rng(BOOT_SEED + 4).integers(0, len(errc1000), size=(BOOT, len(errc1000)))
            skill_c1k_lo, skill_c1k_hi = np.percentile(
                1.0 - errc1000[idx].mean(axis=1) / trivial, [2.5, 97.5]
            )
        else:
            skill_c1k_lo = skill_c1k_hi = float("nan")

        rows.append(dict(
            delta_e=float(de),
            smax_mean=float(smax.mean()),
            smax_ci_lo=lo,
            smax_ci_hi=hi,
            tau_arf_median=float(grp[tau_col].median()),
            err_episode=err_episode,
            err_converged=err_converged,
            err_converged_1000=err_converged_1000,
            trivial_error=trivial,
            skill_episode=skill_episode,
            skill_converged=skill_converged,
            skill_converged_ci_lo=float(skill_c_lo),
            skill_converged_ci_hi=float(skill_c_hi),
            skill_converged_1000=skill_converged_1000,
            skill_converged_1000_ci_lo=float(skill_c1k_lo),
            skill_converged_1000_ci_hi=float(skill_c1k_hi),
            n_errors_converged=int(np.sum(run_n_err_200)),
            n_errors_converged_1000=int(np.sum(run_n_err_1000)),
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
    tau_ci_lo, tau_ci_hi = _bootstrap_tau_exponent(
        runs, de_col, tau_col, ssot.S13_VALID_DE_MIN
    )

    # R-7 — refit de la loi d'onset du bras HAT (arbre unique) sur le même
    # domaine valide. Estimateur pré-enregistré dans
    # docs/prompts/2026 09 26 - 41 - R-7 pre-registration refit HAT.md :
    # médiane par amplitude sur les graines non censurées, linregress
    # log-log, bootstrap sur graines à graine distincte.
    hat = pd.read_parquet(
        REPO_ROOT / "results" / "R6_hydra_factor" / "data" / "R6_hat_instrumented.parquet"
    )
    hat_valid = hat[
        (hat.delta_e >= ssot.S13_VALID_DE_MIN) & hat.tau_hat.notna()
    ]
    hat_med = hat_valid.groupby("delta_e")["tau_hat"].median()
    hat_fit = stats.linregress(np.log(hat_med.index.to_numpy()), np.log(hat_med.to_numpy()))
    hat_ci_lo, hat_ci_hi = _bootstrap_tau_exponent(
        hat.dropna(subset=["tau_hat"]), "delta_e", "tau_hat",
        ssot.S13_VALID_DE_MIN, seed=BOOT_SEED + 5,
    )
    hat_n_censored = int(
        ((hat.delta_e >= ssot.S13_VALID_DE_MIN) & hat.tau_hat.isna()).sum()
    )

    # R-8 — segmented onset regression, breakpoint estimated (pre-registered
    # in docs/prompts/2026 09 26 - 45). HAT arm included: R-9 verdict is
    # identical_clocks (gate entry detector_clocks).
    seg_arf = _segmented_fit(valid.delta_e.to_numpy(), valid.tau_arf_median.to_numpy())
    seg_arf_ci = _bootstrap_segmented(
        runs, de_col, tau_col, ssot.S13_VALID_DE_MIN, seed=BOOT_SEED + 6
    )
    sse_arf_pooled = _pooled_sse(valid.delta_e.to_numpy(), valid.tau_arf_median.to_numpy())
    # R-8 past the break: the decline a -2 exponent predicts across the points
    # the constant piece holds, against the decline their medians show.
    des_valid = valid.delta_e.to_numpy()
    med_valid = valid.tau_arf_median.to_numpy()
    k_star = int(np.flatnonzero(des_valid == seg_arf["de_star"])[0])
    past_de, past_med = des_valid[k_star + 1:], med_valid[k_star + 1:]
    # Post-hoc diagnostics, computed after the R-8 verdict was read (report 50):
    # the penalised comparison the pre-registration left undefined, and the
    # flank interval with the break held at its estimate.
    n_valid = len(des_valid)
    f_stat = (sse_arf_pooled - seg_arf["sse"]) / (seg_arf["sse"] / (n_valid - 3))
    seg_fixed_ci = _bootstrap_segmented(
        runs, de_col, tau_col, ssot.S13_VALID_DE_MIN, seed=BOOT_SEED + 8, fixed_k=k_star
    )
    ll = {m: n_valid * np.log(s / n_valid)
          for m, s in (("pooled", sse_arf_pooled), ("segmented", seg_arf["sse"]))}
    n_par = {"pooled": 2, "segmented": 3}
    # Shape of the onset curve, also computed after the R-8 verdict was read: the slope between
    # consecutive grid points with the half-steps its medians span, and the quadratic term in
    # x = ln(de) of y = ln(median).
    x_v, y_v = np.log(des_valid), np.log(med_valid)
    (ls_lo, ls_hi), (q_lo, q_hi), block_ci = _bootstrap_curvature(
        runs, de_col, tau_col, ssot.S13_VALID_DE_MIN)
    block_slopes = [float(np.polyfit(x_v[s], y_v[s], 1)[0]) for s in CURVATURE_BLOCKS]
    local_slopes = [dict(de_lo=float(des_valid[i]), de_hi=float(des_valid[i + 1]),
                         median_lo=float(med_valid[i]), median_hi=float(med_valid[i + 1]),
                         half_steps=int(round(2 * abs(med_valid[i + 1] - med_valid[i]))),
                         slope=float((y_v[i + 1] - y_v[i]) / (x_v[i + 1] - x_v[i])),
                         ci=[float(ls_lo[i]), float(ls_hi[i])])
                    for i in range(n_valid - 1)]
    seg_hat = _segmented_fit(hat_med.index.to_numpy(), hat_med.to_numpy())
    seg_hat_ci = _bootstrap_segmented(
        hat.dropna(subset=["tau_hat"]), "delta_e", "tau_hat",
        ssot.S13_VALID_DE_MIN, seed=BOOT_SEED + 7,
    )
    sse_hat_pooled = _pooled_sse(hat_med.index.to_numpy(), hat_med.to_numpy())

    # R-5 — biais de fenêtre de base mesuré sur les lignes pré-dérive des traces
    bias, bias_source, bias_n = _baseline_window_bias(TRACES, runs, H)
    bias_area = float(bias * H) if bias is not None else None

    mode_post = _bootstrap_argmax(bell)

    gate_payload = dict(
        smax_peak={
            "delta_e": float(bell.loc[bell.smax_mean.idxmax(), "delta_e"]),
            "value": float(bell.smax_mean.max())
        },
        smax_left=float(bell.smax_mean.iloc[0]),
        smax_right=float(bell.smax_mean.iloc[-1]),
        mode_posterior=mode_post,
        tau_exponent={
            "estimate": float(fit.slope),
            "stderr": float(fit.stderr),
            "intercept": float(fit.intercept),
            "ci_lo": tau_ci_lo,
            "ci_hi": tau_ci_hi,
            "domain_min": float(ssot.S13_VALID_DE_MIN)
        },
        tau_exponent_hat={
            "estimate": float(hat_fit.slope),
            "stderr": float(hat_fit.stderr),
            "intercept": float(hat_fit.intercept),
            "ci_lo": hat_ci_lo,
            "ci_hi": hat_ci_hi,
            "domain_min": float(ssot.S13_VALID_DE_MIN),
            "n_censored": hat_n_censored
        },
        detector_clocks=_detector_clocks(),
        tau_segmented={
            "de_star": seg_arf["de_star"],
            "exponent": seg_arf["b"],
            "floor": seg_arf["floor"],
            "exponent_ci": seg_arf_ci["exponent_ci"],
            "floor_ci": seg_arf_ci["floor_ci"],
            "de_star_ci": seg_arf_ci["de_star_ci"],
            "sse_segmented": seg_arf["sse"],
            "sse_pooled": sse_arf_pooled,
            "sse_gain": 1.0 - seg_arf["sse"] / sse_arf_pooled,
            "minus2_decline_past_break": float(1.0 - (past_de[0] / past_de[-1]) ** 2),
            "median_decline_past_break": float(1.0 - past_med[-1] / past_med[0]),
            "post_hoc": {
                "note": "computed after the R-8 verdict was read; not pre-registered",
                "f_stat": float(f_stat),
                "f_pvalue": float(stats.f.sf(f_stat, 1, n_valid - 3)),
                "aic": {m: float(ll[m] + 2 * n_par[m]) for m in ll},
                "bic": {m: float(ll[m] + n_par[m] * np.log(n_valid)) for m in ll},
                "exponent_ci_break_fixed": seg_fixed_ci["exponent_ci"],
                "tail_ols_slope": float(stats.linregress(np.log(past_de), np.log(past_med)).slope),
            },
        },
        tau_segmented_hat={
            "de_star": seg_hat["de_star"],
            "exponent": seg_hat["b"],
            "floor": seg_hat["floor"],
            "exponent_ci": seg_hat_ci["exponent_ci"],
            "floor_ci": seg_hat_ci["floor_ci"],
            "de_star_ci": seg_hat_ci["de_star_ci"],
            "sse_segmented": seg_hat["sse"],
            "sse_pooled": sse_hat_pooled,
        },
        local_slopes=local_slopes,
        curvature={
            "model": f"ln(tau_arf_median) = c0 + c1 ln(delta_e) + c2 ln(delta_e)^2, "
                     f"{n_valid} grid points, delta_e >= {ssot.S13_VALID_DE_MIN}",
            "quadratic_coef": float(np.polyfit(x_v, y_v, 2)[0]),
            "quadratic_ci": [float(q_lo[0]), float(q_hi[0])],
            "note": "computed after the R-8 verdict was read; not pre-registered",
            "robustness": {
                "note": "same seed-bootstrap draws as quadratic_ci; not cited by the paper",
                "subsets": [dict(points=name, n=len(x_v[s]),
                                 **dict(zip(("c2", "stderr_ols"), _quad_ols(x_v[s], y_v[s]))),
                                 ci=[float(q_lo[j]), float(q_hi[j])])
                            for j, (name, s) in enumerate(CURVATURE_SUBSETS.items())],
                "disjoint_blocks": {
                    "points": "the first six and the next six points of the valid grid",
                    "slopes": block_slopes,
                    "difference": block_slopes[0] - block_slopes[1],
                    "difference_ci": [float(block_ci[0]), float(block_ci[1])],
                },
            },
        },
        skill_zero_crossing_episode=_first_negative(bell, "skill_episode"),
        skill_zero_crossing_converged=_first_negative(bell, "skill_converged"),
        baseline_bias_1000_vs_3000=bias,
        baseline_bias_source=bias_source,
        baseline_bias_n=bias_n,
        baseline_bias_area_units=bias_area,
        delta_p=DELTA_P,
        horizon=H,
        n_boot=BOOT,
        boot_seed=BOOT_SEED,
    )

    with open(OUT / "s13_gate.json", "w") as f:
        json.dump(gate_payload, f, indent=2)


if __name__ == "__main__":
    main()