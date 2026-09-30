"""Window budgets and ceilings of the canonical cell at the declared delta_P = 0.01.

Stream H10, objections CONS-001/CONS-018. The published ceiling (33.5) was the median of
runs.parquet:a_unrefl_peak, a walk accumulated at the registry tolerance DELTA_P = 0.005
while every requirement, floor and certificate in the manuscript is stated at
delta_P = 0.01. This script re-simulates the canonical cell (Delta_e = 0.326793, arm
'full', the campaign's own 100 seeds) with the campaign's own runner, verifies the
regenerated delta_P = 0.005 columns against the committed runs.parquet bit for bit, and
computes at delta_P = 0.01 over H = 2500:

  - S_max, the peak of the reflected walk of Eq. (cusum) -- the named ceiling statistic,
    per-run, with the seed bootstrap interval of its median;
  - the unreflected charged-walk peak and its argmax (the W_argmax reading at the
    declared tolerance);
  - the budget accumulated over (tau*, tau* + W] at the declared windows W in
    {57, 391, 612, 1367}: the charged walk Z_W and the raw excess integral;
  - the last crossing of def:times at rho = 0.01;
  - the crossing rates of the lambda ladder within each declared window;
  - the clearance margin of the median ceiling against R_CUSUM at the certificate
    threshold lambda_op = 21.93 (31.2007, s2bis_proteus_gate.json couple 5).

Output: results/S6_synchronized_traces/tables/s6_window_budgets.json
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from joblib import Parallel, delayed

sys.path.insert(0, str(Path(__file__).resolve().parent))
import s6_defs as defs  # noqa: E402
import s6_runner as R  # noqa: E402
import _gate_common as common  # noqa: E402
from _gate_common import ssot  # noqa: E402

OUT = ssot.RESULTS_DIR / "S6_synchronized_traces" / "tables" / "s6_window_budgets.json"
DE = 0.326793
H = ssot.S6_T_HORIZON
DP = ssot.S6_AUDIT_DELTA_P            # 0.01, the declared tolerance
WINDOWS = [57, 391, 612, 1367]        # first-swap mean; argmax mean at 0.01; superseded
                                      # 0.005 argmax; last crossing at rho = 0.01
LADDER = [8.0, 15.0, 25.0, 50.0]      # the manuscript's threshold ladder
R_CUSUM_OP = 31.2007                   # s2bis_proteus_gate.json, couple 'S6 measured lambda_op'
BOOTSTRAP_SEED, N_BOOT = 12345, 10_000


def one(seed):
    records, frames = R.simulate(seed, DE, arms=("full",))
    rec, fr = records[0], frames[0]
    err = fr["err"].astype(np.float64)
    t_rel = np.asarray(fr["t_rel"])
    err_post = err[t_rel >= 0]
    e_pre = float(rec["e_pre"])
    ep = err_post[:H]

    a_u005, _ = defs.accumulations(err_post, e_pre, delta=ssot.DELTA_P)
    a_u, a_r = defs.accumulations(ep, e_pre, delta=DP)
    row = {"seed": int(seed), "e_pre": e_pre,
           "gate_a_unrefl_peak_005": float(a_u005.max()),
           "gate_tau_swap_q010": float(rec["tau_swap_q010"]),
           "s_max": float(a_r.max()), "z_peak": float(a_u.max()),
           "z_argmax": int(a_u.argmax()),
           "a_fw": float(rec["a_fw"]) if np.isfinite(rec["a_fw"]) else None,
           "w_fw_rho001": defs.tau_err_framework(err_post, e_pre, DP),
           "roll200_min_excess": float(np.nanmin(defs.rolling_mean(ep, 200)) - e_pre)}
    for W in WINDOWS:
        n = min(W, a_u.size)
        row[f"z_W{W}"] = float(a_u[n - 1])
        row[f"asig_W{W}"] = float(np.sum(ep[:n]) - e_pre * n)
        row[f"smax_W{W}"] = float(a_r[:n].max())
    return row


def main():
    seeds = common.seed_pool(len(ssot.S6_CAMPAIGN_SEEDS))
    rows = Parallel(n_jobs=-1, verbose=2)(delayed(one)(s) for s in seeds)
    df = pd.DataFrame(rows)

    # Gate: the regenerated delta_P = 0.005 columns must equal the committed runs.parquet.
    runs = pd.read_parquet(ssot.RESULTS_DIR / "S6_synchronized_traces" / "data" / "runs.parquet",
                           filters=[("delta_e", "=", DE), ("arm", "=", "full")])
    runs = runs.set_index("seed").sort_index()
    regen = df.set_index("seed").sort_index()
    assert list(regen.index) == list(runs.index), "seed pool mismatch"
    gate = {}
    for col, mine in (("a_unrefl_peak", "gate_a_unrefl_peak_005"),
                      ("tau_swap_q010", "gate_tau_swap_q010")):
        a = runs[col].to_numpy(dtype=np.float64)
        b = regen[mine].to_numpy(dtype=np.float64)
        ok = bool(np.array_equal(a, b, equal_nan=True))
        gate[col] = {"bit_identical": ok}
        assert ok, f"gate failed on {col}"

    def q(x):
        x = np.asarray(x, dtype=np.float64)
        x = x[np.isfinite(x)]
        return {"median": float(np.median(x)), "mean": float(np.mean(x)),
                "q05": float(np.quantile(x, 0.05)), "q95": float(np.quantile(x, 0.95)),
                "min": float(x.min()), "max": float(x.max()), "n": int(x.size)}

    s = df["s_max"].to_numpy()
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    idx = rng.integers(0, s.size, size=(N_BOOT, s.size))
    med_boot = np.median(s[idx], axis=1)

    out = {
        "delta_e": DE, "arm": "full", "n_seeds": int(len(df)), "delta_p": DP, "H": int(H),
        "gate_vs_runs_parquet": gate,
        "s_max": q(s), "s_max_median_bootstrap95": [float(np.quantile(med_boot, 0.025)),
                                                    float(np.quantile(med_boot, 0.975))],
        "z_peak": q(df["z_peak"]), "z_argmax": q(df["z_argmax"]),
        "a_fw": q(df["a_fw"]), "w_fw_rho001": q(df["w_fw_rho001"]),
        "roll200_min_excess": q(df["roll200_min_excess"]),
        "clearance_at_lambda_op": {
            "R_CUSUM": R_CUSUM_OP,
            "margin_median": float(np.median(s) - R_CUSUM_OP),
            "margin_median_bootstrap95": [float(np.quantile(med_boot - R_CUSUM_OP, 0.025)),
                                          float(np.quantile(med_boot - R_CUSUM_OP, 0.975))],
            "n_runs_clearing": int((s >= R_CUSUM_OP).sum())},
        "windows": {}, "crossing_rates_within": {},
    }
    for W in WINDOWS:
        out["windows"][f"W{W}"] = {"z_W": q(df[f"z_W{W}"]), "asig_W": q(df[f"asig_W{W}"]),
                                   "smax_W": q(df[f"smax_W{W}"])}
        sm = df[f"smax_W{W}"].to_numpy()
        out["crossing_rates_within"][f"W{W}"] = {f"lam{lam:g}": float((sm >= lam).mean())
                                                 for lam in LAMBDAS}

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=1, sort_keys=True, default=float) + "\n",
                   encoding="utf-8")
    print(f"written: {OUT}")
    print(json.dumps({k: out[k] for k in ("gate_vs_runs_parquet", "s_max", "clearance_at_lambda_op",
                                          "crossing_rates_within")}, indent=1))


if __name__ == "__main__":
    main()
