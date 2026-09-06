#!/usr/bin/env bash
# ==============================================================================
# Script: run_all.sh
# Objective: One-click reproduction of all experiments (R1 to R9) and tests.
# ==============================================================================
set -e
set -o pipefail

# [IEEE/ICDM FAIR Compliance] Enforcing global determinism for child processes
export PYTHONHASHSEED=0

echo "======================================================================"
echo " ICDM 2026 Artifact Evaluation: FULL REPRODUCTION PIPELINE"
echo "======================================================================"

# S1: Execute all experiments in dependency order.
# R6 (Hydra factor) joins its own tau_HAT against the tau_ARF produced by R2, so R2 MUST complete
# before R6. The order below encodes that dependency explicitly instead of leaning on the numeric
# order of a {1..9} loop, which expressed the constraint only by accident.
EXPERIMENTS=(R1 R2 R3 R4 R5 R6 R7 R8 R9)   # R6 depends on R2

for exp in "${EXPERIMENTS[@]}"; do
    script="./run_experiment_${exp}.sh"
    echo -e "\n>>> Executing ${script}..."
    $script
done

echo -e "\n======================================================================"
echo " [INFO] All experiments generated successfully. Launching validation..."
echo "======================================================================"

# S2 & S4: Trigger the test suite
./run_tests.sh

echo -e "\n======================================================================"
echo " [SUCCESS] 100% of the repository pipelines executed and validated."
echo "======================================================================"