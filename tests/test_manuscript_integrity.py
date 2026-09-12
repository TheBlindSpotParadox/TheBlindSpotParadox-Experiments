# tests/test_manuscript_integrity.py
"""Integrity of the manuscript of record against the artifacts it displays.

`docs/manuscript/figures/` is a second copy of plots the experiment pipeline writes under
`results/<exp>/figures/`, and nothing kept the two in step. Action A1 found the Figure 1 copy
already adrift -- 301,651 bytes against the pipeline's 299,449 -- so the committed camera-ready PDF
showed a plot that no run reproduced, and a data change (A1 moved R1 to CUSUM_DELTA_P) would have
left the figure silently describing the superseded tolerance. This fails when a copy drifts again.

Authored assets with no pipeline counterpart (`fig_ontology.tex`) are out of scope by construction:
the check matches on basename, so a file the pipeline never writes is reported as unmatched and
must be declared in AUTHORED below rather than pass by silence.

Usage:  python -m pytest tests/test_manuscript_integrity.py -v
"""
import hashlib
import os
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent
MANUSCRIPT_FIGURES = ROOT_DIR / "docs" / "manuscript" / "figures"
RESULTS_DIR = ROOT_DIR / "results"

# Assets authored in the manuscript tree, not produced by any experiment.
AUTHORED = {"fig_ontology.tex"}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pipeline_counterparts(name):
    return sorted(RESULTS_DIR.glob(f"*/figures/{name}"))


def test_manuscript_figures_match_the_pipeline():
    if not MANUSCRIPT_FIGURES.is_dir():
        pytest.skip(f"{MANUSCRIPT_FIGURES.relative_to(ROOT_DIR)} absent")

    drifted, unmatched, checked = [], [], 0
    for fig in sorted(MANUSCRIPT_FIGURES.iterdir()):
        if not fig.is_file() or fig.name in AUTHORED:
            continue
        found = pipeline_counterparts(fig.name)
        if not found:
            unmatched.append(fig.name)
            continue
        checked += 1
        manuscript, pipeline = sha256(fig), sha256(found[0])
        if manuscript != pipeline:
            # os.path.relpath, not Path.relative_to: the message must never raise on a results/
            # tree that sits outside ROOT_DIR, or a drift is reported as a ValueError.
            drifted.append(f"{fig.name}: manuscript {manuscript[:12]} != "
                           f"{os.path.relpath(found[0], ROOT_DIR)} {pipeline[:12]}")

    assert not unmatched, (
        "manuscript figures with no pipeline counterpart under results/*/figures/. Either the "
        "experiment that writes them was renamed, or they are authored assets and belong in "
        "AUTHORED:\n  " + "\n  ".join(unmatched))
    assert checked, "no manuscript figure was compared; the check verifies nothing as written"
    assert not drifted, (
        "manuscript figure copies drifted from the artifacts the experiments produce. Re-copy from "
        "results/, do not re-render into docs/:\n  " + "\n  ".join(drifted))
