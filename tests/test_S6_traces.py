# tests/test_S6_traces.py
"""
Stream S6 trace suite -- the oracle of the Parquet contract and of the causal arms.

1. Byte-for-byte reproducibility. One (seed, Delta_e) cell is simulated twice from scratch, written
   twice, and the SHA-256 of every produced file must match. This covers the simulation and the
   writer together: a GUID partition name, a drifting row-group boundary or a non-deterministic
   model would all break it.
2. `err_cum` and `swaps_cum` are non-decreasing on every (delta_e, arm, seed) trajectory.
3. `a_refl >= a_unrefl` at every step. The reflected accumulation is the same running sum floored at
   zero, so the inequality is structural; the test is what proves the pipeline did not lose it.
4. 'no_swap' invariant: zero ADDITIONAL replacement after the fork, and a strictly growing forest.
   River's trees only split occasionally, so "strictly growing" is asserted as non-decreasing at
   every step AND strictly greater at the horizon than at the fork -- a step function cannot be
   strictly increasing step by step, and asserting that it is would be a false invariant.
5. 'frozen' invariant: zero replacement and a strictly constant forest after the fork.

Assertions 2-5 read the committed smoke artifacts and skip with an explicit motive when absent, so
the suite is green on a fresh clone and enforcing after a smoke run.

Usage:  PYTHONHASHSEED=0 python -m pytest tests/test_S6_traces.py -v
"""
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import pytest
from joblib import Parallel, delayed

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "S6_synchronized_traces"))
from config import experiment_ssot as ssot  # noqa: E402

import s6_runner as runner  # noqa: E402
import s6_writer as writer  # noqa: E402

SMOKE_DIR = ssot.RESULTS_DIR / "S6_synchronized_traces" / "smoke"
TRACE_KEYS = ["delta_e", "arm", "seed"]


def _smoke(name):
    path = SMOKE_DIR / name
    if not path.exists():
        pytest.skip("smoke artifact absent -- run "
                    "`python experiments/S6_synchronized_traces/s6_runner.py smoke`")
    return path


@pytest.fixture(scope="module")
def traces():
    return writer.read_traces(_smoke("traces.parquet")).to_pandas()


@pytest.fixture(scope="module")
def runs():
    return pq.read_table(_smoke("runs.parquet")).to_pandas()


def test_parquet_replay_is_byte_identical():
    seed, delta_e = runner.common.seed_pool(1)[0], ssot.S6_SMOKE_DELTA_E[1]
    with tempfile.TemporaryDirectory() as tmp:
        out = [Path(tmp) / "a", Path(tmp) / "b"]
        Parallel(n_jobs=2)(delayed(runner.campaign)([seed], [delta_e], d, 1, "replay") for d in out)
        for artifact in ("runs.parquet", "traces.parquet"):
            a, b = (writer.sha256_tree(d / artifact) for d in out)
            assert a == b, f"{artifact} is not byte-identical on replay:\n{a}\n{b}"
            assert a, f"{artifact} produced no file"


def test_parquet_contract(traces, runs):
    assert pq.read_table(_smoke("runs.parquet")).schema.equals(writer.RUNS_SCHEMA)
    parts = sorted(p.name for p in _smoke("traces.parquet").iterdir())
    assert parts == [f"delta_e={ssot.S6_PARQUET_PARTITION_FMT.format(d)}"
                     for d in sorted(ssot.S6_SMOKE_DELTA_E)], parts
    assert set(runs["arm"]) == set(ssot.S6_ARM_NAMES)
    assert set(traces["arm"]) == set(ssot.S6_ARM_NAMES)
    assert traces["t_rel"].min() == -ssot.S6_TRACE_PRE
    assert traces["t_rel"].max() == ssot.S6_TRACE_POST - 1
    assert not runs.duplicated(subset=TRACE_KEYS).any(), "duplicate (delta_e, arm, seed) in runs"


def test_cumulative_columns_are_monotone(traces):
    for key, g in traces.sort_values(TRACE_KEYS + ["t_rel"]).groupby(TRACE_KEYS, sort=False):
        for col in ("err_cum", "swaps_cum"):
            d = np.diff(g[col].to_numpy())
            assert (d >= 0).all(), f"{col} decreases on {key} at step {int(np.argmin(d))}"


def test_reflected_accumulation_dominates(traces):
    bad = traces[traces["a_refl"] < traces["a_unrefl"] - 1e-9]
    assert bad.empty, f"a_refl < a_unrefl on {len(bad)} rows:\n{bad.head().to_string(index=False)}"


def _post_fork(traces, runs, arm):
    """Rows strictly after the fork, per trajectory, for a forked arm."""
    fork = runs[runs["arm"] == arm].set_index(TRACE_KEYS)["fork_t_rel"]
    sub = traces[traces["arm"] == arm]
    if sub.empty or fork.isna().all():
        pytest.skip(f"no forked '{arm}' trajectory in the smoke artifact")
    for key, g in sub.sort_values(TRACE_KEYS + ["t_rel"]).groupby(TRACE_KEYS, sort=False):
        f = fork.loc[key]
        if not np.isfinite(f):
            continue
        yield key, g[g["t_rel"] > f]


def test_no_swap_arm_takes_no_further_replacement(traces, runs):
    n = 0
    for key, g in _post_fork(traces, runs, "no_swap"):
        swaps = g["swaps_cum"].to_numpy()
        nodes = g["n_nodes_mean"].to_numpy()
        assert swaps[-1] == swaps[0], f"no_swap replaced a tree after the fork on {key}"
        assert (np.diff(nodes) >= 0).all(), f"no_swap forest shrank on {key}"
        assert nodes[-1] > nodes[0], f"no_swap forest did not grow on {key}"
        n += 1
    assert n, "no forked no_swap trajectory was checked"


def test_frozen_arm_is_immobile(traces, runs):
    n = 0
    for key, g in _post_fork(traces, runs, "frozen"):
        swaps = g["swaps_cum"].to_numpy()
        nodes = g["n_nodes_mean"].to_numpy()
        assert swaps[-1] == swaps[0], f"frozen replaced a tree after the fork on {key}"
        assert (nodes == nodes[0]).all(), f"frozen forest moved on {key}"
        assert (g["n_active_leaves_mean"].to_numpy() == g["n_active_leaves_mean"].iloc[0]).all()
        n += 1
    assert n, "no forked frozen trajectory was checked"
