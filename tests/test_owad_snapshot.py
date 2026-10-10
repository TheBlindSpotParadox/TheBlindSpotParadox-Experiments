import filecmp
import hashlib
import math
import re
from pathlib import Path

import pandas as pd
import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent
OWAD_DIR = ROOT_DIR / "docs" / "manuscript" / "owad2026"

SNAPSHOT_SHA256 = {
    "The_Blind_Spot_Paradox_ICDM_OWAD_2026.bib":
        "6d82fbaf38f96ea77d3d81c61e9b8d6910ad358bb26d31cd5c560ae54fe0f3b6",
    "The_Blind_Spot_Paradox_ICDM_OWAD_2026.pdf":
        "f8001dce80d46c907b23ec8435a097e68cd6fed5682ec3ec1d983caa4f9b02e6",
    "The_Blind_Spot_Paradox_ICDM_OWAD_2026.tex":
        "4ed09a783b809847067478518be2bd0de60243ceb27c8999158f4f97bd740020",
    "figures/Fig_R1_race_condition.png":
        "6910f8f3efdd1f01079f9725215dc5b0a89ea07b0e34f37bb1bd4125267c1b66",
    "figures/Fig_R2_A_PHT_ARF.png":
        "bd7eaad3a1d57d48487b8743edd6b25fb86654861a11ecd236bae0295c49bd15",
    "figures/Fig_R2_B_PHT_ARF.png":
        "fd844784b907b56e46935bef6b402cf224ca52e603f06576c37f9cf1a46e2ec6",
    "figures/Fig_R2_C_PHT_ARF.png":
        "547f4c810f38a10a6d335275e189081071009a11eeaaed378476e10c56622135",
    "figures/Fig_R3_Regime_Crossover.png":
        "8cc2e41eef1929353d08560b262c247f7bb16ca8cc3fccd4bc8c8fdf8c4c4825",
    "tables/table1_proteus_summary.tex":
        "fd7acc0d4dee8c289198075ff1914d962f25d43966e42558bcc4d0c0a89de38f",
    "tables/table2_real_data_summary.tex":
        "e8e7f5de6e1fa5dc43b8e87031235ec8c773e5a1aaac5142481b8895f042d4cb",
}

PIPELINE_FIGURES = {
    "figures/Fig_R1_race_condition.png":
        "results/R1_race_condition/owad2026/figures/Fig_R1_race_condition.png",
    "figures/Fig_R2_A_PHT_ARF.png": "results/R2_instrumented_blind_spot/figures/Fig_R2_A_PHT_ARF.png",
    "figures/Fig_R2_B_PHT_ARF.png": "results/R2_instrumented_blind_spot/figures/Fig_R2_B_PHT_ARF.png",
    "figures/Fig_R2_C_PHT_ARF.png": "results/R2_instrumented_blind_spot/figures/Fig_R2_C_PHT_ARF.png",
    "figures/Fig_R3_Regime_Crossover.png":
        "results/R3_regime_crossover/figures/Fig_R3_Regime_Crossover.png",
}

TABLE1 = "tables/table1_proteus_summary.tex"
TABLE1_SOURCES = (
    "results/audit_S7/s7ter_arms/u0_frozen/table1_proteus_summary.tex",
    "results/R4_proteus_evaluation/owad2026/tables/table1_proteus_summary.tex",
)
TABLE2 = "tables/table2_real_data_summary.tex"
TABLE2_VALUES = "results/R5_real_world_evaluation/tables/table2_values.csv"
TABLE2_PIPELINE = "results/R5_real_world_evaluation/tables/table2_real_data_summary.tex"
TABLE2_COLUMNS = ("delta_e", "F1_PHT_HT", "F1_PHT_ARF", "F1_ADW_ARF", "ratio")

OWAD_DECLARED_DEVIATIONS = {
    "results/R1_race_condition/owad2026/figures/Fig_R1_race_condition.png":
        "the R1 arm at the published tolerance delta_P = 0.005 reproduces its data byte for byte "
        "(the parquet frozen in results/audit_S7/_baseline/) and renders, byte for byte, the pipeline "
        "figure of the initial commit (git blob 1c4f1a91); the published file is the manuscript copy "
        "committed beside it (git blob fa66d0cf) and differs from that render in 0.39 % of its "
        "pixels, the plotting code being unchanged since",
}

OWAD_DECLARED_EDITS = {
    TABLE1: {"caption": "edited by hand; no committed source"},
    TABLE2: {"caption": "edited by hand; no committed source",
             "row labels": "INSECTS variants typeset in italics, reoccurring_balanced renamed",
             "sign-test column": "removed; the pipeline table still prints it"},
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tabular_body(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    start = next(i for i, ln in enumerate(lines) if ln.strip() == r"\midrule")
    end = next(i for i, ln in enumerate(lines) if ln.strip() == r"\bottomrule")
    return lines[start + 1:end]


def table1_rows(path):
    return [" ".join(ln.split()) for ln in tabular_body(path) if ln.strip().startswith(r"\textbf{")]


def table2_rows(path):
    return [[c.strip() for c in ln.strip().removesuffix("\\\\").split("&")]
            for ln in tabular_body(path) if "&" in ln]


def caption(path):
    return re.search(r"^\s*\\caption\{(.*)\}\s*$", path.read_text(encoding="utf-8"), re.MULTILINE)[1]


def header(path):
    return next(ln for ln in path.read_text(encoding="utf-8").splitlines() if "&" in ln)


def plain(cell):
    return re.sub(r"\\textbf\{([^}]*)\}", r"\1", cell).replace("$", "").replace(r"^{\ast}", "").strip()


def printed(value, column):
    if column == "delta_e" and abs(value) < 0.005:
        return r"\approx 0"
    if column == "ratio" and math.isinf(value):
        return "--"
    return f"{value:.2f}"


def same_bytes(a, b):
    return filecmp.cmp(a, b, shallow=False)


def same_table1_rows(a, b):
    return table1_rows(a) == table1_rows(b)


def check_against(name, target, compare):
    path = ROOT_DIR / target
    if target in OWAD_DECLARED_DEVIATIONS:
        reason = OWAD_DECLARED_DEVIATIONS[target]
        assert reason.strip(), f"{target}: declared deviation without a reason"
        assert path.is_file() or reason.startswith("not yet regenerated"), (
            f"{target} is absent, but its deviation is declared as measured")
        assert not (path.is_file() and compare(OWAD_DIR / name, path)), (
            f"{target} now matches {name}: remove it from OWAD_DECLARED_DEVIATIONS")
        return
    assert path.is_file(), f"{target} is absent"
    assert compare(OWAD_DIR / name, path), f"{name} does not match {target}"


def test_snapshot_files_are_pinned():
    on_disk = {p.relative_to(OWAD_DIR).as_posix() for p in OWAD_DIR.rglob("*") if p.is_file()}
    assert on_disk == set(SNAPSHOT_SHA256), (
        f"files under {OWAD_DIR.relative_to(ROOT_DIR)}/ differ from the sealed snapshot: "
        f"unpinned {sorted(on_disk - set(SNAPSHOT_SHA256))}, "
        f"missing {sorted(set(SNAPSHOT_SHA256) - on_disk)}")
    drifted = [f"{name}: {sha256(OWAD_DIR / name)} != pinned {pinned}"
               for name, pinned in sorted(SNAPSHOT_SHA256.items()) if sha256(OWAD_DIR / name) != pinned]
    assert not drifted, "snapshot files changed after sealing:\n  " + "\n  ".join(drifted)


@pytest.mark.parametrize("name", sorted(PIPELINE_FIGURES))
def test_snapshot_figure_matches_the_pipeline(name):
    check_against(name, PIPELINE_FIGURES[name], same_bytes)


@pytest.mark.parametrize("source", TABLE1_SOURCES)
def test_table1_body_rows_match_the_pipeline(source):
    assert len(table1_rows(OWAD_DIR / TABLE1)) == 14
    check_against(TABLE1, source, same_table1_rows)


def test_a_measured_deviation_needs_its_target(monkeypatch):
    target = "results/R3_regime_crossover/figures/absent.png"
    monkeypatch.setitem(OWAD_DECLARED_DEVIATIONS, target, "differs in 1 % of its pixels")
    with pytest.raises(AssertionError, match="absent"):
        check_against("figures/Fig_R3_Regime_Crossover.png", target, same_bytes)


def test_table1_caption_is_a_declared_edit():
    assert set(OWAD_DECLARED_EDITS[TABLE1]) == {"caption"}
    assert caption(OWAD_DIR / TABLE1) != caption(ROOT_DIR / TABLE1_SOURCES[0]), (
        "the Table I caption no longer differs from the pipeline: remove the declared edit")


def test_table2_numeric_cells_match_table2_values():
    rows = table2_rows(OWAD_DIR / TABLE2)
    values = pd.read_csv(ROOT_DIR / TABLE2_VALUES, float_precision="round_trip")
    assert len(rows) == len(values) == 6, f"{len(rows)} Table II rows against {len(values)} values"
    bad = []
    for cells, (_, record) in zip(rows, values.iterrows()):
        assert len(cells) == 1 + len(TABLE2_COLUMNS), f"{cells[0]}: {len(cells)} cells"
        bad += [f"{record['row']} / {column}: printed {cell!r}, table2_values {record[column]!r}"
                for cell, column in zip(cells[1:], TABLE2_COLUMNS)
                if plain(cell) != printed(record[column], column)]
    assert not bad, "Table II cells that are not the committed values:\n  " + "\n  ".join(bad)


def test_table2_edits_are_declared_and_present():
    assert set(OWAD_DECLARED_EDITS[TABLE2]) == {"caption", "row labels", "sign-test column"}
    snapshot, pipeline = OWAD_DIR / TABLE2, ROOT_DIR / TABLE2_PIPELINE
    assert caption(snapshot) != caption(pipeline)
    labels = pd.read_csv(ROOT_DIR / TABLE2_VALUES, float_precision="round_trip")["row"].tolist()
    assert [cells[0] for cells in table2_rows(snapshot)] != labels
    assert "sign test" in header(pipeline).lower() and "sign" not in header(snapshot).lower()
