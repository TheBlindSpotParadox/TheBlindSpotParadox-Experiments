#!/usr/bin/env bash
# Build the submission artifact from the committed tree (HEAD) without the internal design notes.
# Usage: ./make_submission_export.sh <output-dir>   (the directory must not exist yet)
set -euo pipefail
[ $# -eq 1 ] || { echo "usage: $0 <output-dir>" >&2; exit 2; }
out=$(realpath -m "$1")
[ ! -e "$out" ] || { echo "refusing to overwrite $out" >&2; exit 1; }
cd "$(dirname "$(realpath "$0")")"
mkdir -p "$out"
git archive --format=tar HEAD -- . \
    ':(exclude)docs/prompts' ':(exclude)docs/reports' ':(exclude)docs/theory' \
    ':(exclude)docs/editorial' ':(exclude)docs/plans' ':(exclude)CLAUDE.md' \
    ':(exclude,glob)**/WRAPUP_*' ':(exclude,glob)**/* - [0-9][0-9] - *' \
    ':(exclude)results/audit_S7/reconciliation_report.md' ':(exclude)make_submission_export.sh' \
    | tar -x -C "$out"
leaks=$(grep -rIlE '\bClaude (Code|Opus)\b|\bOpus\b|CLAUDE\.md|round [H-J]\b|prompt [0-9]{2}\b' "$out" || true)
if [ -n "$leaks" ]; then
    printf 'identity references left in the export:\n%s\n' "$leaks" >&2
    exit 1
fi
echo "submission export written to $out"
