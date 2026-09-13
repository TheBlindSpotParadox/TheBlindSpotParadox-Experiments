"""T9.5 prerequisite -- regenerate the rotation error traces, and prove the regeneration is the
same campaign S8 committed.

`results/S8_rotation_generator/data/eta*/traces.parquet/` is gitignored under the S6 regime and is
absent from every worktree; only `runs.parquet` survives. T9.5 needs the per-step error stream, so
the campaign is re-simulated -- the `eta = 0.05` arm alone, which is the one carrying a binding
false-alarm budget (S8 rule D5).

Nothing of S8's is overwritten. The regenerated corpus lands under `results/S9_detector_coverage/`
and S8's committed `runs.parquet` is used as the ORACLE: every shared column of every shared row
must be identical, which is S8's own D3-bis gate transposed. If it is not, the regeneration is not
the committed campaign and no T9.5 number may be read from it.

`s8_rotation.STREAM_FN[eta]` and `s6_runner.campaign` are called as they stand. The triple
per-worker lock, the two-normals-per-step invariant and the seed pool are therefore S8's, verbatim,
and not restated here.

Usage:  PYTHONHASHSEED=0 python experiments/S9_detector_coverage/s9_rotation_traces.py [smoke|full]
"""
import json
import sys
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "S6_synchronized_traces"))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "S6_synchronized_traces" / "gates"))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "S8_generality"))
from config import experiment_ssot as ssot  # noqa: E402

import s6_runner as runner  # noqa: E402
import s8_rotation as rot  # noqa: E402
import _gate_common as common  # noqa: E402

ETA = ssot.S9_HDDDM_ETA
OUT = ssot.RESULTS_DIR / "S9_detector_coverage" / f"rotation_eta{ETA:.2f}"
ORACLE = ssot.RESULTS_DIR / "S8_rotation_generator" / "data" / rot.eta_tag(ETA) / "runs.parquet"


def trunk_identity(regenerated, oracle_path):
    """Every shared column of every shared (delta_e, seed, arm) row, identical or not."""
    a = pq.read_table(regenerated).to_pandas()
    b = pq.read_table(oracle_path).to_pandas()
    keys = ["delta_e", "seed", "arm"]
    for df in (a, b):
        df["delta_e"] = df["delta_e"].round(6)
    m = a.merge(b, on=keys, suffixes=("_new", "_ref"), how="inner")
    shared = [c for c in a.columns if c not in keys and c in b.columns]
    bad = {}
    for c in shared:
        x, y = m[f"{c}_new"].to_numpy(), m[f"{c}_ref"].to_numpy()
        if x.dtype.kind in "fc" or y.dtype.kind in "fc":
            same = np.array_equal(np.nan_to_num(x.astype(float), nan=-np.inf),
                                  np.nan_to_num(y.astype(float), nan=-np.inf))
        else:
            same = np.array_equal(x, y)
        if not same:
            bad[c] = int((x != y).sum())
    return {"rows_joined": int(len(m)), "rows_new": int(len(a)), "rows_ref": int(len(b)),
            "columns_compared": len(shared), "columns_divergent": bad,
            "verdict": "PRESERVED" if not bad and len(m) == len(b) else "BREACH"}


def main(mode="full"):
    seeds = common.seed_pool(ssot.S8_SMOKE_N_SEEDS if mode == "smoke"
                             else len(ssot.S8_CAMPAIGN_SEEDS))
    grid = (list(ssot.S8_SMOKE_DELTA_E) if mode == "smoke" else
            [float(np.round(common.norm.cdf(b / np.sqrt(2)) - 0.5, 6))
             for b in ssot.S8_CAMPAIGN_BOUNDARY_SHIFTS])
    out = OUT if mode == "full" else OUT.with_name(OUT.name + "_smoke")
    print(f"=== T9.5 / regenerate the rotation traces, eta = {ETA} ===")
    print(f"    {len(seeds)} seeds x {len(grid)} magnitudes x arms {ssot.S8_ROTATION_ARMS} "
          f"-> {out.relative_to(ssot.ROOT_DIR)}")

    s = runner.campaign(seeds, grid, out, desc=f"S9 rot eta={ETA}",
                        arms=ssot.S8_ROTATION_ARMS, stream_fn=rot.STREAM_FN[ETA])
    print(f"[INFO] {s['records']} records, {s['trace_rows']:,} trace rows "
          f"in {s['wall_clock_s']:.1f}s")

    ident = trunk_identity(s["runs_path"], ORACLE) if mode == "full" else {
        "verdict": "SKIPPED", "reason": "smoke grid is not the committed campaign"}
    report = {"eta": ETA, "mode": mode, "seeds": len(seeds), "magnitudes": len(grid),
              "wall_clock_s": round(s["wall_clock_s"], 1), "trace_rows": s["trace_rows"],
              "oracle": str(ORACLE.relative_to(ssot.ROOT_DIR)),
              "trunk_identity": ident, "env": common.env_stamp()}
    tab = ssot.RESULTS_DIR / "S9_detector_coverage" / "tables"
    tab.mkdir(parents=True, exist_ok=True)
    path = tab / f"s9_rotation_regeneration{'' if mode == 'full' else '_' + mode}.json"
    path.write_text(json.dumps(report, indent=2, sort_keys=True, default=float) + "\n",
                    encoding="utf-8")
    print(f"\n--- trunk identity against S8's committed runs.parquet --- {ident['verdict']}")
    if ident.get("columns_divergent"):
        print(f"    divergent columns: {ident['columns_divergent']}")
    print(f"[INFO] wrote {path.relative_to(ssot.ROOT_DIR)}")
    if ident["verdict"] == "BREACH":
        raise SystemExit("[FATAL] the regenerated campaign is not the committed one -- HALT")
    return report


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "full")
