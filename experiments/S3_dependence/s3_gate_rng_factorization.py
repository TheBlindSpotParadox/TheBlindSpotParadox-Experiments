"""Gate D1 -- does River's shared forest generator factorise across the M trees?

`prop:starvation_boundary` assumes the per-tree detection delays are conditionally independent.
`gates/g2_river_introspection.py` already records `model.data[i].rng is model._rng`: one
`random.Random` is threaded through the whole forest. Object sharing alone neither establishes nor
refutes the assumption. What the committed decision rule D1 fixes as decisive is the factorisation
of the DRAW STREAM: whether the positions consumed by tree i on the shared sequence form a
deterministic set, independent of the state of the other trees.

Two channels are separated, because they behave differently:

  * the Oza/Poisson weight, drawn once per tree per instance in index order. If a weight cost one
    draw, tree i would own exactly the residue class {i, M+i, 2M+i, ...} -- deterministic, disjoint,
    hence independent on an idealised i.i.d. source. River's `utils.random.poisson` is a rejection
    loop that consumes k+1 uniforms for a returned weight k, so the cost is itself random;
  * the `max_features='sqrt'` feature subsample, drawn through `rng.sample` at every leaf creation
    (`tree/nodes/arf_htc_nodes.py::_sample_features`). Its number and position depend on the
    drawing tree's own state and displace every later tree's positions.

Decision variables, exactly as committed in `docs/prompts/s3-decision-rules.md`:

  residue_ok  every (step, tree) pair consumes exactly one draw
  n_shift     draw positions whose consumer index differs between a baseline replay and a replay
              of the identical stream in which the state of tree j alone was perturbed, counted
              only where neither label is j

Verdict FACTORISES iff `n_shift == 0 and residue_ok`; DOES NOT FACTORISE otherwise. No tolerance:
the variables are integer counts on a deterministic replay.

The gate also checks the second channel through which the trees could be coupled independently of
the generator -- a feedback path from the ensemble vote into per-tree learning -- by reading the
per-tree drift-detector input off the live River class rather than off its documentation.
"""
import inspect
import json
import random
import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "S6_synchronized_traces" / "gates"))

import river  # noqa: E402
from river import forest  # noqa: E402
from river.forest import adaptive_random_forest as arf_mod  # noqa: E402

import _gate_common as common  # noqa: E402
from _gate_common import ssot  # noqa: E402

OUT_DIR = ROOT_DIR / "results" / "S3"
N_MODELS = ssot.N_MODELS
C_INT = ssot.C_INT
T_WARM = 300          # steps run in lock-step before tree j is perturbed
T_PROBE = 200         # steps over which the draw map is compared
PERTURBED_TREE = 3    # j; any index in [0, N_MODELS) -- the census covers every tree
PROBE_DELTA_E = ssot.S6_GATE_DELTA_E[1]


class TracingRandom(random.Random):
    """`random.Random` that records, for every primitive draw, which tree consumed it.

    Both primitives are traced: `random()` carries the Poisson rejection loop, `getrandbits()`
    carries `random.Random.sample` through `_randbelow`, which is how the feature subsample is
    drawn. Tracing only `random()` would miss the second channel entirely.
    """

    def __init__(self, seed):
        super().__init__(seed)
        self.trace = []
        self.tag = -1       # -1 = drawn outside any per-tree window

    def random(self):
        self.trace.append(self.tag)
        return super().random()

    def getrandbits(self, k):
        self.trace.append(self.tag)
        return super().getrandbits(k)


def traced_poisson(rate, rng):
    """River's `poisson`, wrapped so the draw window opens on the tree whose weight is sampled.

    `BaseForest.learn_one` calls it exactly once per tree per instance, in index order, before that
    tree learns. Everything drawn until the next call therefore belongs to that tree: its own
    rejection loop first, then whatever its `learn_one` consumes.
    """
    if isinstance(rng, TracingRandom):
        rng.tag = getattr(rng, "_step_calls", 0)
        rng._step_calls = rng.tag + 1
    return _POISSON(rate=rate, rng=rng)


_POISSON = arf_mod.poisson


def make_traced_arf(seed):
    """ARF on the project's blind-spot configuration, with every generator reference traced."""
    model = common.make_arf(seed, N_MODELS, C_INT)
    model._rng = TracingRandom(seed)
    return model


def bind_trees(model):
    """Rebind the per-tree generator references after `_init_ensemble` has built the ensemble.

    River constructs the trees with `rng=self._rng`, captured at construction; leaves capture
    `self.rng` at creation. Rebinding immediately after the first `learn_one` therefore puts the
    tracing generator on every tree and on every leaf created from then on.
    """
    for tree in model.data:
        tree.rng = model._rng


def stream(rng, n, t_drift, b_shift):
    """The R2/R6/S6 two-feature Gaussian stream, generated once and replayed on both forests."""
    out = []
    for t in range(n):
        x0, x1 = rng.normal(), rng.normal()
        out.append(({0: x0, 1: x1}, int(x0 + x1 > (0.0 if t < t_drift else b_shift))))
    return out


def run(model, data):
    """Replay `data`; returns the trace segment consumed over the replay."""
    start = len(model._rng.trace)
    for x, y in data:
        model._rng._step_calls = 0
        model._rng.tag = -1              # draws before the first weight belong to no tree
        model.predict_one(x)
        model.learn_one(x, y)
    return model._rng.trace[start:]


def census(trace, n_models, n_steps):
    """Per-(step, tree) draw counts, read off the consumer tags in consumption order.

    Tags are non-decreasing within a step -- `learn_one` walks the trees in index order -- so a
    step boundary is exactly a decrease. Untagged draws (-1) are counted separately.
    """
    counts, step, prev, untagged = [], [0] * n_models, -1, 0
    for tag in trace:
        if tag < 0:
            untagged += 1
            continue
        if tag < prev:
            counts.append(step)
            step = [0] * n_models
        step[tag] += 1
        prev = tag
    if any(step):
        counts.append(step)
    return counts[:n_steps], untagged


def main():
    t0 = time.perf_counter()
    arf_mod.poisson = traced_poisson

    seed = common.seed_pool(1)[0]
    safe_seed, data_rng = common.lock_rng(seed)
    b_shift = common.boundary_shift(PROBE_DELTA_E)
    warm = stream(data_rng, T_WARM, T_WARM + T_PROBE, b_shift)
    probe = stream(data_rng, T_PROBE, 0, b_shift)

    a, b = make_traced_arf(safe_seed), make_traced_arf(safe_seed)
    for model in (a, b):
        model._init_ensemble(sorted(warm[0][0].keys()))
        bind_trees(model)
    aliasing = {f"tree_{i}": a.data[i].rng is a._rng for i in range(N_MODELS)}

    run(a, warm)
    run(b, warm)
    lockstep_ok = a._rng.trace == b._rng.trace

    # In-model perturbation of one tree: exactly what a drift replacement does to tree j, applied
    # to B alone. Both generators are then forced to the same state, so the two replays differ in
    # the state of tree j and in nothing else.
    b.data[PERTURBED_TREE] = b._new_base_model()
    b.data[PERTURBED_TREE].rng = b._rng
    b._rng.setstate(a._rng.getstate())

    trace_a, trace_b = run(a, probe), run(b, probe)
    common_len = min(len(trace_a), len(trace_b))
    n_shift = sum(1 for p in range(common_len)
                  if trace_a[p] != trace_b[p]
                  and PERTURBED_TREE not in (trace_a[p], trace_b[p]))
    first_shift = next((p for p in range(common_len)
                        if trace_a[p] != trace_b[p]
                        and PERTURBED_TREE not in (trace_a[p], trace_b[p])), None)

    counts, untagged = census(trace_a, N_MODELS, T_PROBE)
    flat = [c for step in counts for c in step]
    residue_ok = bool(flat) and all(c == 1 for c in flat)
    histogram = {str(v): flat.count(v) for v in sorted(set(flat))}

    detector_input = inspect.getsource(type(a)._drift_detector_input)
    no_vote_feedback = "y_pred" in detector_input and "self.data" not in detector_input

    factorises = bool(n_shift == 0 and residue_ok)
    payload = {
        "gate": "D1",
        "rule": "docs/prompts/s3-decision-rules.md :: D1",
        "verdict": "FACTORISES" if factorises else "DOES NOT FACTORISE",
        "decision_variables": {
            "residue_ok": residue_ok,
            "n_shift": n_shift,
            "first_shifted_position": first_shift,
        },
        "consequence": (
            "conditional independence tenable; the Jensen/exchangeability path of T3.1 is open"
            if factorises else
            "the Jensen path falls under D1 as committed; the Boole bound of T3.2 carries alone, "
            "and the Jensen bound is stated only with its hypothesis named, entering no published "
            "numeral (D2, D5(b))"),
        "channel_poisson": {
            "draws_per_tree_per_step": histogram,
            "n_steps_censused": len(counts),
            "untagged_draws": untagged,
            "mean_draws_per_tree_step": round(sum(flat) / len(flat), 4) if flat else None,
            "reading": (
                "one draw per tree per step would put tree i on the residue class {i, M+i, ...}; "
                "River's poisson is a rejection loop consuming k+1 uniforms for weight k, so the "
                "cost is random and the residue class does not hold"),
        },
        "channel_features": {
            "max_features": a.data[0].max_features,
            "n_features": len(warm[0][0]),
            "sample_call_site": "river/tree/nodes/arf_htc_nodes.py::RandomLeaf._sample_features",
            "traced_primitives": ["random", "getrandbits"],
        },
        "perturbation": {
            "tree": PERTURBED_TREE,
            "operation": "tree j replaced by a fresh base model (the in-model drift replacement)",
            "lockstep_traces_identical_before_perturbation": lockstep_ok,
            "generator_state_equalised_at_probe_start": True,
            "trace_len_baseline": len(trace_a),
            "trace_len_perturbed": len(trace_b),
        },
        "aliasing": aliasing,
        "aliasing_all_trees_share_forest_rng": all(aliasing.values()),
        "vote_feedback_into_per_tree_learning": {
            "absent": bool(no_vote_feedback),
            "drift_detector_input_source": detector_input.strip(),
            "reading": (
                "ARFClassifier._drift_detector_input is int(not y_true == y_pred) on the "
                "PER-TREE prediction passed by learn_one; the ensemble vote does not enter "
                "per-tree learning, so the trees are coupled through the generator or not at all"),
        },
        "criterion_scope": (
            "D1 is a criterion on POSITIONS. A displacement proves that the consumed positions are "
            "state-dependent; it does not by itself prove that the per-tree draw BLOCKS are "
            "probabilistically dependent, because a sequential allocation by adapted stopping "
            "times preserves independence on an idealised i.i.d. source. The criterion is "
            "sufficient for factorisation and not necessary. The gap is recorded here and argued "
            "in docs/theory/S3_dependence_bounds.md; the rule is applied as committed and is not "
            "moved after the measurement."),
        "config": {"n_models": N_MODELS, "c_int": C_INT, "seed": safe_seed,
                   "t_warm": T_WARM, "t_probe": T_PROBE, "probe_delta_e": PROBE_DELTA_E},
        "env": common.env_stamp(),
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "rng_factorization.json"
    out.write_text(json.dumps(payload, indent=2, sort_keys=True, default=float) + "\n",
                   encoding="utf-8")
    print(f"[INFO] wrote {out.relative_to(ROOT_DIR)}")
    print(f"\n=== D1 {payload['verdict']} ===  residue_ok={residue_ok}  n_shift={n_shift}  "
          f"first_shift={first_shift}  draws/tree/step={histogram}")
    print(f"  aliasing all trees share forest rng: {payload['aliasing_all_trees_share_forest_rng']}")
    print(f"  vote feedback into per-tree learning absent: {no_vote_feedback}")
    print(f"  river={river.__version__}  {time.perf_counter() - t0:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
