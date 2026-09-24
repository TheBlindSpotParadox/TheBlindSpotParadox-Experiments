"""Test P1: Freeze debt register anchors against the active manuscript and fragments."""

from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
DEBT_REGISTER = REPO_ROOT / "docs" / "editorial" / "debt_register.md"
CURRENT_FILE = REPO_ROOT / "docs" / "manuscript" / "CURRENT"


def resolve_target_file(rel_path: str) -> Path:
    """Resolve camera_ready manuscript through CURRENT, or return fragment path."""
    if "articleA_blindspot" in rel_path:
        assert CURRENT_FILE.exists(), f"Missing {CURRENT_FILE}"
        tex_name = CURRENT_FILE.read_text(encoding="utf-8").strip()
        return REPO_ROOT / "docs" / "manuscript" / tex_name
    return REPO_ROOT / rel_path


def parse_anchors():
    """Extract anchors from markdown tables with NF>=5 (>=3 data columns)."""
    assert DEBT_REGISTER.exists(), f"Missing {DEBT_REGISTER}"
    lines = DEBT_REGISTER.read_text(encoding="utf-8").splitlines()
    anchors = []

    for line in lines:
        if not line.startswith("|"):
            continue
        parts = [p.strip() for p in line.split("|")]
        # Markdown row: ['' (before first |), col1, col2, col3, ..., '' (after last |)]
        # len(parts) >= 5 corresponds to awk NF >= 5 (at least 3 columns)
        if len(parts) >= 5:
            col1 = parts[1].strip(" `")
            col2 = parts[2].strip(" `")
            # Filter headers and separators
            if col1 in ("file", "---") or not col1:
                continue
            if col2 in ("textual anchor (verbatim)", "---") or not col2:
                continue
            # Retain only actual file paths containing text anchors
            if any(k in col1 for k in ("articleA", "sections/", "tables/")):
                anchors.append((col1, col2))
    return anchors


def test_debt_register_anchors_count():
    """Assert non-vacuity and exact count of 44 anchors."""
    anchors = parse_anchors()
    assert len(anchors) == 44, f"Expected 44 anchors, parsed {len(anchors)}"


def test_debt_register_anchors_resolve_uniquely():
    """Ensure every anchor resolves exactly once in its target file."""
    anchors = parse_anchors()
    assert len(anchors) == 44

    failures = []
    for rel_path, anchor in anchors:
        target_path = resolve_target_file(rel_path)
        assert target_path.exists(), f"Target file missing: {target_path}"
        content = target_path.read_text(encoding="utf-8")
        count = content.count(anchor)
        if count != 1:
            failures.append(f"{target_path.name}: count={count} for '{anchor}'")

    assert not failures, "Anchors not resolving uniquely (count != 1):\n" + "\n".join(failures)