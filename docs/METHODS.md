# Decision rules, and the notes this artifact does not ship

## Decision rules

Where a script, a test or a result file cites a decision rule, that rule was written and committed
before the measurement it governs was run. It fixes the estimator, the data, the threshold and the
verdicts the measurement can return. Verdicts use a small closed vocabulary (for example REPRODUCED /
UNREPRODUCED, RETAINED / NOT RETAINED, CONFIRMED / REFUTED, NOT PRODUCED), and a verdict that goes
against the paper is reported as such.

## References to files that are not shipped

Those citations take the form `docs/prompts/<package>-decision-rules.md :: <rule id>`, or point to a
design note under `docs/theory/`, `docs/editorial/`, `docs/reports/` or `docs/plans/`. None of these
files is part of this artifact. They are the working notes of the authors' review process: they
interleave the rules with correspondence, superseded drafts and instructions to the AI assistant
declared in the paper, and they describe states of the work that the paper no longer holds.

Nothing needed to reproduce a number is in them:

- the rule a reference names is applied by the script that cites it, with its parameters in
  `config/experiment_ssot.py` or in that script;
- the verdict it returned is stored in the result file that carries the reference, beside the numbers
  it was computed from;
- `tests/` checks the published results against those files.

A reference records where a rule came from; following it is not needed to rerun or to check anything.

## Work-package identifiers

Directory names such as `experiments/S13_evidence_bell/` or `results/R5_real_world_evaluation/` carry
the identifier of the work package that produced them (R1–R9, S2–S13). Code comments call these
packages streams, and call the text patches they applied to the manuscript payloads.
