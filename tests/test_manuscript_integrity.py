# tests/test_manuscript_integrity.py
"""Integrity of the manuscript of record against the artifacts it displays.

`docs/manuscript/figures/` and `docs/manuscript/tables/` are second copies of what the experiment
pipeline writes under `results/<exp>/figures/` and `results/<exp>/tables/`, and nothing kept them
in step. Action A1 found the Figure 1 copy already adrift -- 301,651 bytes against the pipeline's
299,449 -- so the committed camera-ready PDF showed a plot that no run reproduced, and a data
change (A1 moved R1 to CUSUM_DELTA_P) would have left the figure silently describing the
superseded tolerance. This fails when a copy drifts again.

Action A5 extends the check from figures to tables. The tables are the more dangerous half: they
are `\\input` into the compiled document, so a drifted copy prints wrong numbers straight into the
PDF, where a drifted figure is at least visible as a plot nobody recognises.

Authored assets with no pipeline counterpart (`fig_ontology.tex`) are out of scope by construction:
the check matches on basename, so a file the pipeline never writes is reported as unmatched and
must be declared in AUTHORED below rather than pass by silence.

Action A4 adds the single-source check. A second copy of the manuscript, carrying neither the
S6 nor the S7-bis edits, was being served to an agent reading the project mount rather than the
repository, and the resulting report described a manuscript two streams behind. The repository has
never held that copy -- the check below proves it on every run instead of leaving the claim to a
one-off grep -- and `docs/manuscript/CURRENT` now names the live document in one place any tool
can read.

Usage:  python -m pytest tests/test_manuscript_integrity.py -v
"""
import hashlib
import os
import re
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent
MANUSCRIPT_DIR = ROOT_DIR / "docs" / "manuscript"
RESULTS_DIR = ROOT_DIR / "results"
CURRENT = MANUSCRIPT_DIR / "CURRENT"

# Subdirectories of docs/manuscript/ that mirror results/<exp>/<same name>/. Adding a kind here is
# all it takes to bring a new mirrored asset class under the check.
MIRRORED = ("figures", "tables")

# Assets authored in the manuscript tree, not produced by any experiment.
AUTHORED = {"fig_ontology.tex"}

# Main documents (a .tex carrying \documentclass) retained for lineage and deliberately NOT the
# manuscript of record. Empty today: v63 is referenced by CLAUDE.md but is not in the repository.
# Adding a file here is the declaration the check demands -- it is never a way to silence a
# surprise, only to record an archive the operator intends to keep.
ARCHIVED_MAIN_TEX = set()


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main_tex_documents():
    """Every .tex under docs/manuscript/ that carries \\documentclass, i.e. is compilable on its own.

    Discriminating on \\documentclass rather than on a filename pattern is what keeps the include
    fragments (figures/fig_ontology.tex, tables/*.tex) out without a hand-maintained exclusion list."""
    return sorted(p for p in MANUSCRIPT_DIR.rglob("*.tex")
                  if "\\documentclass" in p.read_text(encoding="utf-8", errors="ignore"))


def pipeline_counterparts(kind, name):
    return sorted(RESULTS_DIR.glob(f"*/{kind}/{name}"))


def test_manuscript_assets_match_the_pipeline():
    drifted, unmatched, checked = [], [], 0
    for kind in MIRRORED:
        mirror = MANUSCRIPT_DIR / kind
        if not mirror.is_dir():
            continue
        for asset in sorted(mirror.iterdir()):
            if not asset.is_file() or asset.name in AUTHORED:
                continue
            found = pipeline_counterparts(kind, asset.name)
            if not found:
                unmatched.append(f"{kind}/{asset.name}")
                continue
            checked += 1
            manuscript, pipeline = sha256(asset), sha256(found[0])
            if manuscript != pipeline:
                # os.path.relpath, not Path.relative_to: the message must never raise on a results/
                # tree that sits outside ROOT_DIR, or a drift is reported as a ValueError.
                drifted.append(f"{kind}/{asset.name}: manuscript {manuscript[:12]} != "
                               f"{os.path.relpath(found[0], ROOT_DIR)} {pipeline[:12]}")

    assert not unmatched, (
        f"manuscript assets with no pipeline counterpart under results/*/{{{','.join(MIRRORED)}}}/. "
        "Either the experiment that writes them was renamed, or they are authored assets and "
        "belong in AUTHORED:\n  " + "\n  ".join(unmatched))
    assert checked, (
        f"no manuscript asset was compared across {MIRRORED}; the check verifies nothing as written")
    assert not drifted, (
        "manuscript copies drifted from the artifacts the experiments produce. Re-copy from "
        "results/, do not re-render into docs/:\n  " + "\n  ".join(drifted))


def test_current_manuscript_is_unique_and_live():
    """docs/manuscript/CURRENT names the one live document, and nothing else claims that role.

    Four failure modes, each observed or narrowly avoided in this project: CURRENT missing or
    naming a file that does not exist; a stray .tex at the repository root shadowing the real one;
    a second compilable manuscript in the tree with no declaration saying which is authoritative;
    and CURRENT pointing at a document that is not the one the tests and the audit trail target."""
    assert CURRENT.is_file(), (
        f"{CURRENT.relative_to(ROOT_DIR)} is missing. It must contain the bare filename of the "
        f"manuscript of record, one line, no path.")

    lines = [ln.strip() for ln in CURRENT.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(lines) == 1, f"CURRENT must carry exactly one filename, found {len(lines)}: {lines}"
    name = lines[0]
    assert "/" not in name and "\\" not in name, f"CURRENT must carry a bare filename, got {name!r}"
    assert name.endswith(".tex"), f"CURRENT must name a .tex file, got {name!r}"

    target = MANUSCRIPT_DIR / name
    assert target.is_file(), (
        f"CURRENT names {name}, which does not exist under "
        f"{MANUSCRIPT_DIR.relative_to(ROOT_DIR)}/")

    stray = sorted(p.name for p in ROOT_DIR.glob("*.tex"))
    assert not stray, (
        "stray .tex at the repository root, shadowing the manuscript of record. A root copy is "
        "how a superseded manuscript gets read in place of the live one:\n  " + "\n  ".join(stray))

    mains = main_tex_documents()
    undeclared = [p for p in mains if p != target and p.name not in ARCHIVED_MAIN_TEX]
    assert not undeclared, (
        f"more than one compilable manuscript under {MANUSCRIPT_DIR.relative_to(ROOT_DIR)}/ and "
        f"CURRENT names {name}. Declare the others in ARCHIVED_MAIN_TEX or remove them:\n  "
        + "\n  ".join(os.path.relpath(p, ROOT_DIR) for p in undeclared))
    assert target in mains, (
        f"CURRENT names {name}, but it carries no \\documentclass and is not compilable on its own")


CITE_RE = re.compile(r"\\[a-zA-Z]*cite[a-zA-Z]*\s*(?:\[[^\]]*\]\s*)*\{([^}]*)\}")
# A .bib entry key: @type{key, ... }. @string macro definitions carry no comma and are excluded --
# they define journal abbreviations (IEEEabrv.bib), which \cite never resolves against.
ENTRY_RE = re.compile(r"^@(?!string\b)[a-zA-Z]+\s*\{\s*([^,\s]+)\s*,", re.MULTILINE | re.IGNORECASE)


def cited_keys():
    """{key: [files citing it]} over every .tex under docs/manuscript/, sections included."""
    out = {}
    for tex in sorted(MANUSCRIPT_DIR.rglob("*.tex")):
        for group in CITE_RE.findall(tex.read_text(encoding="utf-8", errors="ignore")):
            for key in (k.strip() for k in group.split(",")):
                if key:
                    out.setdefault(key, []).append(os.path.relpath(tex, ROOT_DIR))
    return out


def bib_entries():
    """{key: [bib files defining it]} over every .bib under docs/manuscript/."""
    out = {}
    for bib in sorted(MANUSCRIPT_DIR.glob("*.bib")):
        for key in ENTRY_RE.findall(bib.read_text(encoding="utf-8", errors="ignore")):
            out.setdefault(key, []).append(bib.name)
    return out


def test_every_cited_key_resolves_in_the_bibliography():
    """Action A6. The v2 sections are not \\input by the manuscript yet, so LaTeX cannot report a
    dangling citation in them: the failure would surface only on assembly day, as a page of
    undefined references. This resolves them now, against the same bibliography the document loads.

    It also fails on a duplicate entry key, which BibTeX reports as a warning and is easy to miss --
    the failure mode a second .bib file would have reintroduced."""
    entries, cited = bib_entries(), cited_keys()
    assert entries, f"no .bib entry found under {MANUSCRIPT_DIR.relative_to(ROOT_DIR)}/"
    assert cited, "no citation found; the check verifies nothing as written"

    duplicates = [f"{k} defined in {', '.join(f)}" for k, f in sorted(entries.items()) if len(f) > 1]
    assert not duplicates, (
        "duplicate bibliography keys; BibTeX resolves one and warns about the rest:\n  "
        + "\n  ".join(duplicates))

    dangling = [f"{k}  cited by {', '.join(sorted(set(f)))}"
                for k, f in sorted(cited.items()) if k not in entries]
    assert not dangling, (
        "citations with no bibliography entry:\n  " + "\n  ".join(dangling))


# Environments the document class or a package in the preamble supplies (IEEEtran, amsmath, amsthm,
# graphicx, tikz, enumitem). Anything a section uses outside this set must carry its own \newtheorem
# in the main document, or the assembly halts -- which is how framework_v2.tex's \begin{lemma}
# survived three streams unnoticed. Declared by name, not by silence: adding to this set asserts the
# preamble provides it, so it is a claim to check, not a way to quiet a surprise.
STANDARD_ENVIRONMENTS = {
    "document", "abstract", "IEEEkeywords", "thebibliography",
    "figure", "figure*", "table", "table*", "tabular", "tabularx", "center",
    "align", "align*", "equation", "equation*", "gather", "gather*", "split",
    "cases", "array", "subequations", "proof",
    "itemize", "enumerate", "description", "tikzpicture",
}

BEGIN_RE = re.compile(r"\\begin\{([A-Za-z][A-Za-z0-9*]*)\}")
NEWTHEOREM_RE = re.compile(r"\\newtheorem\*?\{([^}]*)\}")
LABEL_RE = re.compile(r"\\label\{([^}]*)\}")
REF_RE = re.compile(r"\\(?:eq)?ref\{([^}]*)\}|\\hyperref\[([^}]*)\]")


def _tex_sources():
    """(main document, [every other .tex under docs/manuscript/])."""
    mains = main_tex_documents()
    main = mains[0] if mains else None
    return main, [p for p in sorted(MANUSCRIPT_DIR.rglob("*.tex")) if p != main]


def test_sections_assemble_into_the_main_document():
    """Action A7 follow-up. The section drafts are not \\input by the main document, so nothing
    compiles them and LaTeX reports none of their defects. Two were live when this was written:
    framework_v2.tex used \\begin{lemma} against a preamble declaring no lemma environment, and
    intro_v2.tex referenced a figure no file included. Both halt or deface an assembly; neither was
    visible from the main document's own clean compile.

    Static substitutes for that compile, with no toolchain dependency:
      - a theorem-like environment must be declared by \\newtheorem in the main document, whose
        preamble is the one an assembly will use. Environments supplied by the document class or by
        a loaded package are out of scope -- a static check cannot honestly verify package
        availability -- and are named in STANDARD_ENVIRONMENTS rather than passed over in silence;
      - a \\ref target must be defined somewhere in the manuscript tree."""
    main, others = _tex_sources()
    if main is None or not others:
        pytest.skip("no main document or no section fragment to check")

    main_src = main.read_text(encoding="utf-8")
    available = set(NEWTHEOREM_RE.findall(main_src)) | STANDARD_ENVIRONMENTS

    undeclared, dangling = [], []
    labels = set(LABEL_RE.findall(main_src))
    for p in others:
        labels |= set(LABEL_RE.findall(p.read_text(encoding="utf-8")))

    for p in others:
        src = p.read_text(encoding="utf-8")
        rel = os.path.relpath(p, ROOT_DIR)
        undeclared += [f"{rel}: \\begin{{{e}}}" for e in sorted(set(BEGIN_RE.findall(src)))
                       if e not in available]
        dangling += [f"{rel}: \\ref{{{t}}}" for t in
                     sorted({a or b for a, b in REF_RE.findall(src)} - labels) if t]

    assert not undeclared, (
        f"environments used by a section but neither declared nor used in {main.name}; an "
        "assembly halts on these:\n  " + "\n  ".join(undeclared))
    assert not dangling, (
        "\\ref targets defined in no .tex of the manuscript tree; these typeset as ??:\n  "
        + "\n  ".join(dangling))


# Sources carrying status X in docs/editorial/source_verification.md: unverified in session, or
# rescinded, and therefore not citable. The ledger is a markdown table nobody re-reads before adding
# a reference; this is what actually holds the line. SR 11-7 was rescinded on 2026-04-17 and
# replaced by Fed SR 26-2 / OCC 2026-13 -- citing it as a current requirement would be a factual
# error, not a stylistic one.
PROSCRIBED_KEYS = {"fiddler", "arize", "azure_data_drift", "azure_ml_drift", "sr_11_7", "sr11_7"}


def test_proscribed_sources_are_not_cited():
    """Action A10. None of the status-X sources may enter the bibliography or be cited.

    Checked in both directions, because either alone leaves a hole: an entry with no citation is a
    loaded gun the next author finds and fires, and a citation with no entry is a dangling key the
    bibliography guard would report as a different defect entirely."""
    entries = {k.lower(): v for k, v in bib_entries().items()}
    cited = {k.lower(): v for k, v in cited_keys().items()}

    defined = [f"{k} defined in {', '.join(entries[k])}" for k in sorted(PROSCRIBED_KEYS)
               if k in entries]
    used = [f"{k} cited by {', '.join(sorted(set(cited[k])))}" for k in sorted(PROSCRIBED_KEYS)
            if k in cited]

    assert not defined, (
        "bibliography entries for sources marked X in docs/editorial/source_verification.md:\n  "
        + "\n  ".join(defined))
    assert not used, (
        "citations of sources marked X in docs/editorial/source_verification.md:\n  "
        + "\n  ".join(used))
