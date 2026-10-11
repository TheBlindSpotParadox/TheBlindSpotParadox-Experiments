#!/usr/bin/env bash
# ==============================================================================
# Script: run_owad2026.sh
# Objective: Regenerate every artifact docs/OWAD_CLAIMS.md cites for the ICDM 2026 OWAD paper, in a
#            copy of the repository, and compare each output with the repository's file.
# Usage:     ./run_owad2026.sh --dry-run        stage table and artifact -> stage map; runs nothing
#            ./run_owad2026.sh --copy <dir>     copies the repository to <dir> and runs there
# Outputs:   <dir>/owad_regen_report.{md,json}, written even when a stage fails
# Determinism: PYTHONHASHSEED is pinned for bit-wise reproducibility.
# ==============================================================================
set -euo pipefail
export PYTHONHASHSEED=0 MPLBACKEND=Agg

REPO=$(dirname "$(realpath "$0")")
usage() { echo "usage: $0 --dry-run | --copy <dir>" >&2; exit 2; }
case "${1:-}" in
    --dry-run) [ $# -eq 1 ] || usage ;;
    --copy) [ $# -eq 2 ] || usage ;;
    *) usage ;;
esac

# id|command|where the command is documented|outputs, deleted before the stage|references
# A reference is "repo" (the repository's file at the same path) or an archive directory of
# results/audit_S7/s7ter_arms/ (its file of the same name). R8 is cited by no claim and not run.
R1=results/R1_race_condition; R2=results/R2_instrumented_blind_spot; R3=results/R3_regime_crossover
R4=results/R4_proteus_evaluation; R5=results/R5_real_world_evaluation; S6=results/S6_synchronized_traces
ARMS=results/audit_S7/s7ter_arms
STAGES="R1|./run_experiment_R1.sh|docs/ENVIRONMENT.md|$R1/data/R1_race_condition.parquet $R1/data/R1_race_condition_diagnostic.md $R1/figures/Fig_R1_race_condition.png|repo
R1-owad2026|python experiments/R1_race_condition/exp_R1_generate_data.py --arm owad2026 && python experiments/R1_race_condition/exp_R1_plot_figure.py --arm owad2026|--arm of both scripts|$R1/owad2026/data/R1_race_condition.parquet $R1/owad2026/data/R1_race_condition_diagnostic.md $R1/owad2026/figures/Fig_R1_race_condition.png|repo
R2|./run_experiment_R2.sh|docs/ENVIRONMENT.md|$R2/data/R2_instrumented_A_PHT_ARF.parquet $R2/data/R2_instrumented_B_PHT_ARF.parquet $R2/data/R2_instrumented_C_PHT_ARF.parquet $R2/figures/Fig_R2_A_PHT_ARF.png $R2/figures/Fig_R2_B_PHT_ARF.png $R2/figures/Fig_R2_C_PHT_ARF.png|repo
R3-U1|python experiments/R3_regime_crossover/exp_R3_regime_crossover.py --arm U1|docs/ENVIRONMENT.md|$R3/data/R3_regime_crossover_metrics.parquet $R3/figures/Fig_R3_Regime_Crossover.png|$ARMS/r3_u1
R3|./run_experiment_R3.sh|docs/ENVIRONMENT.md|$R3/data/R3_regime_crossover_metrics.parquet $R3/figures/Fig_R3_Regime_Crossover.png|repo
R4|python experiments/R4_proteus_evaluation/exp_R4_main_table.py|run_experiment_R4.sh step 1/2 (the KSWIN sweep is cited by no claim)|$R4/data/exp_R4_results_aligned_fusion.csv $R4/data/exp_R4_seed_level_tests.csv $R4/tables/table1_proteus_summary.tex|repo
R4-owad2026|python experiments/R4_proteus_evaluation/exp_R4_main_table.py --arm owad2026|docs/ENVIRONMENT.md|$R4/owad2026/data/exp_R4_results_aligned_fusion.csv $R4/owad2026/data/exp_R4_seed_level_tests.csv $R4/owad2026/tables/table1_proteus_summary.tex|repo $ARMS/u0_frozen
R4-seedboot|python experiments/R4_proteus_evaluation/exp_R4_main_table.py --arm owad2026 --bootstrap seed --summarise-only|results/audit_S7/s7ter_arms/README.md|$R4/owad2026_seedboot/tables/table1_proteus_summary.tex $R4/owad2026/data/exp_R4_seed_level_tests.csv|repo
R5|./run_experiment_R5.sh|docs/ENVIRONMENT.md|$R5/data/checkpoints $R5/data/baf_results.parquet $R5/data/insects_results.parquet $R5/data/insects_per_episode.parquet $R5/data/delta_e.parquet $R5/data/delta_e_oracle.parquet $R5/data/flooding_decomposition.parquet $R5/tables/table2_real_data_summary.tex $R5/tables/table2_values.csv|repo
R6|./run_experiment_R6.sh|docs/ENVIRONMENT.md|results/R6_hydra_factor/data/R6_hat_instrumented.parquet results/R6_hydra_factor/tables/exp_R6_hydra_empirical_validation.tex results/audit_S7/hydra_survival.csv results/audit_S7/hydra_survival.tex|repo
R7|./run_experiment_R7.sh|docs/ENVIRONMENT.md|results/R7_clock_mismatch/data/R7_clock_mismatch.parquet results/R7_clock_mismatch/tables/exp_R7_regime1_miss_curve.csv results/R7_clock_mismatch/tables/exp_R7_regime1_miss_summary.tex|repo
R9-data|python experiments/R9_mcrit/exp_R9_generate_data.py && python experiments/R9_mcrit/exp_R9_generate_data.py 1|docs/ENVIRONMENT.md|results/R9_mcrit/data/results_instrumented_A_ADWIN_HAT.csv results/R9_mcrit/data/results_instrumented_matched_cext1_ADWIN_HAT.csv|repo
S6-full|python experiments/S6_synchronized_traces/s6_runner.py full|s6_runner.py usage|$S6/data/runs.parquet $S6/data/traces.parquet|repo
S6-refine|python experiments/S6_synchronized_traces/s6_runner.py refine && python experiments/S6_synchronized_traces/s6_recompute_cusum_delta001.py data_refine|docstrings of both scripts|$S6/data_refine/runs.parquet $S6/data_refine/traces.parquet $S6/tables/delta_e_c_data_refine.json $S6/tables/cusum_delta001_quantiles_data_refine.csv $S6/tables/cusum_delta001_quantiles_all_arms_data_refine.csv|repo
S6-envelope|python experiments/S6_synchronized_traces/s6_envelope_stats.py|s6_envelope_stats.py docstring|$S6/tables/envelope_stats.json|repo
S6-power|python experiments/S6_synchronized_traces/s6_predictive_power.py data|s6_predictive_power.py docstring|$S6/tables/first_swap_predictive_power.tex|repo
S3|python experiments/S3_dependence/s3_gate_rng_factorization.py|s3_gate_rng_factorization.py docstring|results/S3/rng_factorization.json|repo
S8|python experiments/S8_generality/s8_arms.py full && python experiments/S8_generality/s8_arms.py causal|docs/ENVIRONMENT.md|results/S8_ab_initio/data/runs.parquet results/S8_ab_initio/data/traces.parquet results/S8_ab_initio/data/s8_tau_per_tree.parquet results/S8_ab_initio/data/s8_causal.json results/S8_ab_initio/tables/s8_trunk_identity.json results/S8_ab_initio/tables/s8_detection_counts.csv|repo
S9|python experiments/S9_detector_coverage/s9_offline_detectors.py data && python experiments/S9_detector_coverage/s9_family_ordering.py data s6|docs/ENVIRONMENT.md|results/S9_detector_coverage/data/traces.parquet results/S9_detector_coverage/tables/s9_offline_summary.json results/S9_detector_coverage/tables/s9_requirement_lattice.json results/S9_detector_coverage/tables/s9_family_ordering.json|repo
S13|python experiments/S13_evidence_bell/s13_evidence_bell.py|s13_evidence_bell.py docstring|results/S13_evidence_bell/evidence_bell.csv results/S13_evidence_bell/blindspot_map.csv results/S13_evidence_bell/s13_gate.json|repo
S2bis|python experiments/S2bis_calibration/s2bis_lambda_eq.py|reproduction.command of s2bis_flooding_gate.json|results/S2bis_calibration/tables/s2bis_lambda_eq_insects.csv results/S2bis_calibration/tables/s2bis_insects_sweep.csv results/S2bis_calibration/tables/s2bis_flooding_gate.json|repo"
export STAGES

# Every artifact path of the claims registry must be static, archived or written by a stage.
python - "$REPO" <<'PY'
import os, re, sys
from pathlib import Path

repo = Path(sys.argv[1])
stages = [line.split("|") for line in os.environ["STAGES"].splitlines()]
print(f"{'stage':12s} {'outputs':>7s}  {'references':34s} command  [documented in]")
for sid, cmd, src, outs, refs in stages:
    print(f"{sid:12s} {len(outs.split()):7d}  {refs:34s} {cmd}  [{src}]")
    for o in outs.split():
        if not (repo / o).exists():
            print(f"{'':12s} note: {o} has no counterpart in the repository; it is compared with nothing")

cited = {}
for line in (repo / "docs" / "OWAD_CLAIMS.md").read_text(encoding="utf-8").splitlines():
    if re.match(r"^\| [A-Z]\d{2} \|", line):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        for token in re.findall(r"`([^`]+)`", cells[3]):
            path = token.split("::")[0].split()[0]
            if "/" in path or re.search(r"\.(txt|csv|json|parquet|tex|md|py|png|pdf)$", path):
                cited.setdefault(path, []).append(cells[0])


def owner(path):
    if path == "requirements.txt" or path.startswith(("config/", "experiments/", "tests/", "docs/", "data/")):
        return "static"
    archived = [sid for sid, _, _, _, refs in stages for r in refs.split() if path.startswith(r + "/")]
    if archived:
        return "archive, compared with " + ", ".join(archived)
    if path.startswith("results/audit_S7/s7ter_arms/"):
        return "archive"
    hits = [sid for sid, _, _, outs, _ in stages for o in outs.split()
            if o == path.rstrip("/") or o.startswith(path.rstrip("/") + "/") or path.startswith(o + "/")]
    return ", ".join(dict.fromkeys(hits))


print(f"\n{'artifact cited by docs/OWAD_CLAIMS.md':86s} stage  [rows]")
unmapped = []
for path, rows in cited.items():
    who = owner(path)
    print(f"{path:86s} {who or 'NO STAGE'}  [{', '.join(dict.fromkeys(rows))}]")
    if not who:
        unmapped.append(path)
if unmapped:
    sys.exit(f"\n{len(unmapped)} cited artifact(s) without a stage: {unmapped}")
PY

[ "$1" = --dry-run ] && exit 0

DIR=$(realpath -m "$2")
case "$DIR/" in "$REPO/"*) echo "refusing to run inside the repository: $DIR" >&2; exit 1 ;; esac
[ ! -e "$DIR/experiments" ] || { echo "refusing to reuse $DIR: it already holds a copy" >&2; exit 1; }
mkdir -p "$DIR"
STAGE_LOG=$DIR/owad_regen_stages.tsv OUT_LOG=$DIR/owad_regen_outputs.tsv TEST_LOG=$DIR/owad_regen_tests.tsv
: > "$STAGE_LOG"; : > "$OUT_LOG"; : > "$TEST_LOG"
CURRENT=setup
START=$(date +%s.%N)

report() {
    python - "$DIR" "$1" "$CURRENT" "$START" <<'PY'
import csv, json, sys, time
from pathlib import Path

d, rc, current, start = Path(sys.argv[1]), int(sys.argv[2]), sys.argv[3], float(sys.argv[4])
read = lambda name: list(csv.reader(open(d / name, encoding="utf-8"), delimiter="\t"))
host = dict(read("owad_regen_host.tsv")) if (d / "owad_regen_host.tsv").exists() else {}
stages = [dict(zip(("stage", "start", "end", "seconds", "command", "documented_in"), r))
          for r in read("owad_regen_stages.tsv")]
outputs = [dict(zip(("stage", "path", "sha256", "reference", "reference_sha256", "verdict", "declared"), r))
           for r in read("owad_regen_outputs.tsv")]
tests = [dict(zip(("suite", "exit_code", "summary"), r)) for r in read("owad_regen_tests.tsv")]
for s in stages:
    s["seconds"] = float(s["seconds"])
    s["verdicts"] = {}
    for o in outputs:
        if o["stage"] == s["stage"]:
            s["verdicts"][o["verdict"]] = s["verdicts"].get(o["verdict"], 0) + 1
total = sum(s["seconds"] for s in stages)
status = "completed" if rc == 0 and current == "done" else f"stopped during {current} (exit {rc})"
payload = {"status": status, "host": host, "stage_wall_clock_seconds": round(total, 1),
           "stage_wall_clock_hours": round(total / 3600, 2),
           "elapsed_seconds": round(time.time() - start, 1), "stages": stages, "outputs": outputs,
           "tests": tests}
(d / "owad_regen_report.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

hms = lambda s: f"{int(s // 3600)} h {int(s % 3600 // 60):02d} min {int(s % 60):02d} s"
md = ["# OWAD 2026 regeneration report", "", f"Status: {status}.", ""]
md += [f"- {k}: {v}" for k, v in host.items()]
md += ["", "| stage | command | wall clock | outputs | verdicts |", "|---|---|---:|---:|---|"]
md += [f"| {s['stage']} | `{s['command']}` | {hms(s['seconds'])} | "
       f"{sum(s['verdicts'].values())} | {', '.join(f'{k} {v}' for k, v in sorted(s['verdicts'].items()))} |"
       for s in stages]
md += ["", f"Stage wall clock, summed: {hms(total)} ({total:.0f} s, {total / 3600:.2f} h). "
           f"Elapsed, copy and tests included: {hms(payload['elapsed_seconds'])}.", ""]
odd = [o for o in outputs if o["verdict"] != "identical" or o["declared"] != "declared"]
if odd:
    md += ["## Outputs not identical to their reference, or not declared", "",
           "| stage | output | reference | verdict | declared |", "|---|---|---|---|---|"]
    md += [f"| {o['stage']} | `{o['path']}` | `{o['reference']}` | {o['verdict']} | {o['declared']} |"
           for o in odd]
    md.append("")
md += ["## Tests in the copy", ""] + [f"- {t['suite']}: {t['summary']} (exit {t['exit_code']})" for t in tests]
(d / "owad_regen_report.md").write_text("\n".join(md) + "\n", encoding="utf-8")
print(f"[report] {status}; stage wall clock {hms(total)} -> {d}/owad_regen_report.{{md,json}}")
PY
}
trap 'report $?' EXIT

{
    printf 'repository HEAD\t%s\n' "$(git -C "$REPO" rev-parse HEAD 2>/dev/null || echo unknown)"
    printf 'tracked files modified at copy time\t%s\n' "$(git -C "$REPO" status --porcelain 2>/dev/null | grep -vc '^??' || true)"
    printf 'nproc\t%s\n' "$(nproc)"
    printf 'load average at start\t%s\n' "$(cut -d' ' -f1-3 /proc/loadavg)"
    printf 'free disk at start\t%s\n' "$(df -h "$DIR" | awk 'NR == 2 {print $4}')"
    printf 'python\t%s\n' "$(python -c 'import sys; print(sys.executable, sys.version.split()[0])')"
    printf 'river\t%s\n' "$(python -c 'import river; print(river.__version__)')"
    printf 'started (UTC)\t%s\n' "$(date -u +%FT%TZ)"
} > "$DIR/owad_regen_host.tsv"

rsync -a --exclude .git --exclude logs/ "$REPO/" "$DIR/"
cd "$DIR"

compare() {
    local id=$1 outs=$2 refs=$3 f o r ref declared verdict
    for o in $outs; do
        [ -e "$o" ] || printf '%s\t%s\t-\t-\t-\tmissing\tdeclared\n' "$id" "$o" >> "$OUT_LOG"
    done
    { for o in $outs; do [ ! -e "$o" ] || find "$o" -type f; done; find results -type f -newer .stage_stamp; } |
    sort -u | while read -r f; do
        declared=undeclared
        for o in $outs; do case "$f" in "$o" | "$o"/*) declared=declared ;; esac; done
        for r in $refs; do
            if [ "$r" = repo ]; then ref=$REPO/$f; else ref=$REPO/$r/$(basename "$f"); fi
            if [ -f "$ref" ]; then
                if cmp -s "$f" "$ref"; then verdict=identical; else verdict=different; fi
                printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$id" "$f" "$(sha256sum < "$f" | cut -c1-64)" \
                    "${ref#"$REPO"/}" "$(sha256sum < "$ref" | cut -c1-64)" "$verdict" "$declared" >> "$OUT_LOG"
            elif [ "$r" = repo ]; then
                printf '%s\t%s\t%s\t%s\t-\tno reference\t%s\n' "$id" "$f" "$(sha256sum < "$f" | cut -c1-64)" \
                    "${ref#"$REPO"/}" "$declared" >> "$OUT_LOG"
            fi
        done
    done
}

while IFS='|' read -r id cmd src outs refs; do
    CURRENT=$id
    for o in $outs; do rm -rf "$o"; done
    touch .stage_stamp; sleep 1
    s=$(date +%s.%N); started=$(date -u +%FT%TZ)
    echo "=== [$id] $(date -u +%T) $cmd"
    bash -c "$cmd"
    e=$(date +%s.%N)
    printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$id" "$started" "$(date -u +%FT%TZ)" \
        "$(awk "BEGIN {print $e - $s}")" "$cmd" "$src" >> "$STAGE_LOG"
    compare "$id" "$outs" "$refs"
done <<< "$STAGES"

CURRENT=tests
for suite in "OWAD tests|tests/test_owad_snapshot.py tests/test_owad_claims.py tests/test_manuscript_integrity.py" \
             "full suite|tests/"; do
    rc=0
    summary=$(python -m pytest ${suite#*|} -q -p no:cacheprovider 2>&1 | tee -a pytest.log | tail -1) || rc=$?
    printf '%s\t%s\t%s\n' "${suite%%|*}" "$rc" "$summary" >> "$TEST_LOG"
done
CURRENT=done
