"""Deterministic Parquet contract of stream S6.

The repository invariant is that artifacts under `results/` are bit-reproducible and that a
byte-different artifact on replay is a defect. Parquet does not give that for free: the default
`write_to_dataset` names partition files with a random GUID, row-group boundaries depend on the
caller's batching, and a pandas round-trip embeds a metadata blob whose column ordering is
incidental. Every one of those is pinned here.

  - Explicit `pyarrow` schema, built from the SSOT grids. No pandas in the write path, so no
    `pandas` metadata blob.
  - Total sort order before writing: runs by (delta_e, arm, seed), traces by (arm, seed, t_rel)
    inside a partition. Ties are impossible by construction; the order is a function of the data.
  - Hive partitioning written by hand, one file per delta_e at a fixed path
    `traces.parquet/delta_e=<%.6f>/part-0.parquet`. `delta_e` lives in the directory name and NOT in
    the file schema, which is the standard Hive shape and avoids an ambiguous field on read.
  - Compression, compression level, format version and row-group size all pinned in the SSOT.

`tests/test_S6_traces.py` is the oracle: it replays one seed and compares SHA-256.
"""
import hashlib
import shutil
import sys
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.dataset as ds
import pyarrow.parquet as pq

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))
from config import experiment_ssot as ssot  # noqa: E402

COMPRESSION = ssot.S6_PARQUET_COMPRESSION
COMPRESSION_LEVEL = ssot.S6_PARQUET_COMPRESSION_LEVEL
FORMAT_VERSION = ssot.S6_PARQUET_VERSION
ROW_GROUP = ssot.S6_PARQUET_ROW_GROUP
PARTITION_FMT = ssot.S6_PARQUET_PARTITION_FMT

Q_GRID = ssot.S6_Q_GRID
RHO_GRID = ssot.S6_RHO_GRID


def tau_swap_col(q):
    return f"tau_swap_q{int(round(q * 100)):03d}"


def tau_err_col(rho):
    return f"tau_err_rho{int(round(rho * 100)):03d}"


RUNS_SCHEMA = pa.schema(
    [("seed", pa.int64()), ("delta_e", pa.float64()), ("arm", pa.string()),
     ("n_models", pa.int32()), ("clock", pa.int32()),
     ("fork_taken", pa.bool_()), ("fork_t_rel", pa.float64()),
     ("e_pre", pa.float64()), ("delta_e_emp", pa.float64()),
     ("n_trees_swapped_pre_drift", pa.int32()),
     ("swaps_total", pa.int32()), ("trees_swapped_total", pa.int32())]
    + [(tau_swap_col(q), pa.float64()) for q in Q_GRID]
    + [(tau_err_col(r), pa.float64()) for r in RHO_GRID]
    + [("tau_erase", pa.float64()),
       ("a", pa.float64()), ("a_rect", pa.float64()), ("a_refl", pa.float64()),
       ("a_unrefl_peak", pa.float64()),
       ("n_nodes_mean_at_drift", pa.float64()), ("n_nodes_mean_at_horizon", pa.float64()),
       ("n_active_leaves_mean_at_horizon", pa.float64()),
       ("err_post_mean", pa.float64())]
)

TRACES_SCHEMA = pa.schema(
    [("arm", pa.string()), ("seed", pa.int64()), ("t_rel", pa.int32()),
     ("err", pa.int8()), ("err_cum", pa.int32()),
     ("swaps_cum", pa.int32()), ("trees_swapped_cum", pa.int16()),
     ("a_unrefl", pa.float64()), ("a_refl", pa.float64()),
     ("n_nodes_mean", pa.float32()), ("n_active_leaves_mean", pa.float32())]
)

TRACES_PARTITIONING = ds.partitioning(pa.schema([("delta_e", pa.string())]), flavor="hive")


def _write(table, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(table, path, compression=COMPRESSION, compression_level=COMPRESSION_LEVEL,
                   version=FORMAT_VERSION, row_group_size=ROW_GROUP,
                   write_statistics=True, store_schema=True)
    return path


def _sorted_table(columns, schema, order):
    """Build a table from column arrays and apply a total lexicographic sort."""
    table = pa.table({f.name: columns[f.name] for f in schema}, schema=schema)
    return table.take(pa.compute.sort_indices(table, sort_keys=[(k, "ascending") for k in order]))


def write_runs(records, out_dir):
    """One flat file. `records` is a list of dicts carrying exactly the RUNS_SCHEMA keys."""
    cols = {f.name: [r[f.name] for r in records] for f in RUNS_SCHEMA}
    table = _sorted_table(cols, RUNS_SCHEMA, ["delta_e", "arm", "seed"])
    return _write(table, Path(out_dir) / "runs.parquet")


def write_traces(frames, out_dir):
    """Hive dataset partitioned by delta_e. `frames` is a list of dicts of equal-length arrays,
    each carrying the TRACES_SCHEMA keys plus a scalar `delta_e`."""
    root = Path(out_dir) / "traces.parquet"
    if root.exists():
        shutil.rmtree(root)
    written = []
    for de in sorted({f["delta_e"] for f in frames}):
        part = [f for f in frames if f["delta_e"] == de]
        cols = {f_.name: np.concatenate([p[f_.name] for p in part]) for f_ in TRACES_SCHEMA}
        table = _sorted_table(cols, TRACES_SCHEMA, ["arm", "seed", "t_rel"])
        written.append(_write(table, root / f"delta_e={PARTITION_FMT.format(de)}" / "part-0.parquet"))
    return root, written


def read_traces(root):
    """Read the partitioned dataset back with an explicit partition schema; `delta_e` returns as a
    float column, recovered from the directory name."""
    table = ds.dataset(str(root), format="parquet", partitioning=TRACES_PARTITIONING).to_table()
    de = pa.compute.cast(table.column("delta_e"), pa.float64())
    return table.set_column(table.schema.get_field_index("delta_e"), "delta_e", de)


def sha256_tree(root):
    """{relative posix path: sha256} over every file under `root`, or the file itself."""
    root = Path(root)
    files = sorted(root.rglob("*")) if root.is_dir() else [root]
    return {str(p.relative_to(root.parent).as_posix()): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in files if p.is_file()}


def demo():
    """Self-check: schema round-trip, sort totality and byte-identity on a rewrite."""
    import tempfile

    rec = {f.name: (0 if pa.types.is_integer(f.type) else
                    False if pa.types.is_boolean(f.type) else
                    "full" if pa.types.is_string(f.type) else 0.0)
           for f in RUNS_SCHEMA}
    recs = [{**rec, "seed": s, "delta_e": de, "arm": a}
            for de in (0.25, 0.10) for a in ("static", "full") for s in (2, 1)]
    n = 7
    frames = [{"delta_e": de, "arm": np.array([a] * n), "seed": np.full(n, s, dtype=np.int64),
               "t_rel": np.arange(-3, n - 3, dtype=np.int32),
               "err": np.zeros(n, dtype=np.int8), "err_cum": np.zeros(n, dtype=np.int32),
               "swaps_cum": np.zeros(n, dtype=np.int32),
               "trees_swapped_cum": np.zeros(n, dtype=np.int16),
               "a_unrefl": np.zeros(n), "a_refl": np.zeros(n),
               "n_nodes_mean": np.ones(n, dtype=np.float32),
               "n_active_leaves_mean": np.ones(n, dtype=np.float32)}
              for de in (0.25, 0.10) for a in ("static", "full") for s in (2, 1)]

    with tempfile.TemporaryDirectory() as d:
        a_dir, b_dir = Path(d) / "a", Path(d) / "b"
        for out in (a_dir, b_dir):
            write_runs(recs, out)
            write_traces(frames, out)
        assert sha256_tree(a_dir / "runs.parquet") == sha256_tree(b_dir / "runs.parquet"), \
            "runs.parquet is not byte-identical on rewrite"
        assert sha256_tree(a_dir / "traces.parquet") == sha256_tree(b_dir / "traces.parquet"), \
            "traces.parquet is not byte-identical on rewrite"

        runs = pq.read_table(a_dir / "runs.parquet")
        assert runs.schema.equals(RUNS_SCHEMA), "runs schema drifted"
        keys = list(zip(runs.column("delta_e").to_pylist(), runs.column("arm").to_pylist(),
                        runs.column("seed").to_pylist()))
        assert keys == sorted(keys), "runs are not totally ordered"

        tr = read_traces(a_dir / "traces.parquet")
        assert tr.num_rows == len(frames) * n and "delta_e" in tr.schema.names
        assert set(tr.column("delta_e").to_pylist()) == {0.10, 0.25}
    print("s6_writer demo: OK")


if __name__ == "__main__":
    demo()
