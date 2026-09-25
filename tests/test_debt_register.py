"""Test P1: Freeze debt register anchors against the active manuscript and fragments."""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEBT_REGISTER = REPO_ROOT / "docs" / "editorial" / "debt_register.md"
MANUSCRIPT_DIR = REPO_ROOT / "docs" / "manuscript"
CURRENT_FILE = MANUSCRIPT_DIR / "CURRENT"
ARCHIVED_V64 = "articleA_blindspot_v64_camera_ready.tex"
EXPECTED_COUNT = {"PENDING": 1, "RETAINED": 1, "PURGED": 0}
INPUT_RE = re.compile(r"\\input\{([^}]*)\}")


def rendered(path):
    """The text of `path` followed by every file it \\input s, recursively."""
    text = path.read_text(encoding="utf-8")
    for name in INPUT_RE.findall(text):
        text += "\n" + rendered(MANUSCRIPT_DIR / (name if name.endswith(".tex") else f"{name}.tex"))
    return text


def parse_anchors():
    """(file, anchor, v65 state) from markdown tables with NF>=5 (>=3 data columns)."""
    assert DEBT_REGISTER.exists(), f"Missing {DEBT_REGISTER}"
    anchors = []
    for line in DEBT_REGISTER.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 5:
            col1 = parts[1].strip(" `")
            col2 = parts[2].strip(" `")
            if col1 in ("file", "---") or not col1:
                continue
            if col2 in ("textual anchor (verbatim)", "---") or not col2:
                continue
            if any(k in col1 for k in ("articleA", "sections/", "tables/")):
                anchors.append((col1, col2, parts[-2].strip(" `")))
    return anchors


def test_debt_register_anchors_count():
    """Assert non-vacuity and exact count of 44 anchors."""
    anchors = parse_anchors()
    assert len(anchors) == 44, f"Expected 44 anchors, parsed {len(anchors)}"


def test_every_row_carries_a_v65_state():
    bad = [f"{f}: {s!r} for '{a[:60]}'" for f, a, s in parse_anchors() if s not in EXPECTED_COUNT]
    assert not bad, f"v65 column outside {sorted(EXPECTED_COUNT)}:\n" + "\n".join(bad)


def test_archived_v64_still_carries_every_anchor_once():
    v64 = (MANUSCRIPT_DIR / ARCHIVED_V64).read_text(encoding="utf-8")
    bad = [f"count={v64.count(a)} for '{a}'" for f, a, _ in parse_anchors()
           if Path(f).name == ARCHIVED_V64 and v64.count(a) != 1]
    assert not bad, "the archived v64 no longer carries its register anchors:\n" + "\n".join(bad)


def test_debt_register_anchors_match_their_v65_state():
    """A v64 row resolves in the manuscript of record and its inputs; any other row in its file."""
    manuscript = rendered(MANUSCRIPT_DIR / CURRENT_FILE.read_text(encoding="utf-8").strip())
    failures = []
    for rel_path, anchor, state in parse_anchors():
        text = manuscript if Path(rel_path).name == ARCHIVED_V64 else (
            (REPO_ROOT / rel_path).read_text(encoding="utf-8"))
        count = text.count(anchor)
        if count != EXPECTED_COUNT.get(state):
            failures.append(f"{rel_path}: {state} expects {EXPECTED_COUNT.get(state)}, "
                            f"count={count} for '{anchor}'")
    assert not failures, "Anchors not in their declared v65 state:\n" + "\n".join(failures)
