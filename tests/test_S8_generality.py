# tests/test_S8_generality.py
"""
Stream S8 generality suite -- one invariant per piece of non-trivial logic the stream introduces.

1. Generator identity. `Delta_e = (1 - 2 eta) |phi - pi/4| / pi` is the whole justification for the
   rotation family: it is what lets the new campaign be read on the same magnitude axis as R2/R6/R7.
   Asserted analytically on the canonical grid and empirically on the labels themselves.
2. PRNG neutrality (CONSTRAINT 1). The rotation stream must consume exactly two `rng.normal()` per
   step, in the same order as the canonical family, on BOTH eta arms. The label noise comes from a
   separately spawned Generator; if it ever came from the feature `rng`, every artifact of every
   other stream would stop being comparable to this one and nothing would say so.
3. Pre-drift bit-identity. At eta = 0 the whole pre-drift phase must be byte-identical to the
   canonical family -- same features AND same labels -- which is what makes the old/new comparison
   paired by seed rather than only by distribution.
4. Ab initio arm invariants. `swaps_total == 0` and `fork_t_rel == 0` are what PROVE the
   intervention happened: the arm name proves nothing. Asserted on the committed smoke artifact,
   and the per-tree tau vector must be all-NaN on those arms for the same reason.
5. Write perimeter. Every file under `results/S8_*/tables/` carries an `s8_` basename, the guard
   `tests/test_S2bis_calibration.py` already applies to its own tree. Scoped to `tables/`: `data/`
   holds the deterministic Parquet contract, whose file names (`runs.parquet`, `traces.parquet/`)
   are fixed by `s6_writer`, and `figures/` holds manuscript twins whose names are fixed by
   `tests/test_manuscript_integrity.py`'s `results/*/figures/<name>` glob.

6. Manuscript payloads. Every SEARCH anchor of `docs/theory/transfer_S8.md` resolves in its target
   file and is in exactly one of the two valid states, and none of them falls inside a subsection
   `CLAUDE.md` excludes. Same invariant `tests/test_S2bis_calibration.py` enforces on its own
   transfer document, transposed to a payload set that targets three files rather than one.

Assertions 4 to 6 read committed artifacts and skip with an explicit motive when absent, so the
suite is green on a fresh clone and enforcing after a smoke run.

Usage:  PYTHONHASHSEED=0 python -m pytest tests/test_S8_generality.py -v
"""
import sys
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq
import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "S6_synchronized_traces"))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "S6_synchronized_traces" / "gates"))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "S8_generality"))
from config import experiment_ssot as ssot  # noqa: E402

import s6_runner as runner  # noqa: E402
import s8_rotation as rot  # noqa: E402
import _gate_common as common  # noqa: E402

SMOKE_DIR = ssot.RESULTS_DIR / "S8_ab_initio" / "smoke"
GRID = [float(np.round(common.norm.cdf(b / np.sqrt(2)) - 0.5, 6))
        for b in ssot.S8_CAMPAIGN_BOUNDARY_SHIFTS]


def _smoke(name):
    path = SMOKE_DIR / name
    if not path.exists():
        pytest.skip("S8 smoke artifact absent -- run "
                    "`python experiments/S8_generality/s8_arms.py smoke`")
    return path


# ══════════════════════════════════════════════════════════════════════════════
# 1. the generator identity
# ══════════════════════════════════════════════════════════════════════════════
def test_rotation_angle_inverts_the_delta_e_identity():
    """phi is the inverse of Delta_e = (1 - 2 eta) theta / pi, at every grid point and both arms."""
    for eta in ssot.S8_ETA_GRID:
        for de in GRID:
            theta = abs(rot.rotation_phi(de, eta) - ssot.S8_ROTATION_PHI0)
            assert abs((1.0 - 2.0 * eta) * theta / np.pi - de) < 1e-12, (eta, de)


def test_measured_delta_e_matches_the_identity_on_the_labels():
    """The identity holds on the realised labels, not only in the algebra.

    Measured with the PRE-DRIFT Bayes rule as the oracle: Delta_e is a property of the generator, so
    reading it off a trained classifier would confound the generator with the learner."""
    _, agg = rot.identity(common.seed_pool(24), [GRID[2], GRID[6], GRID[11]], n_jobs=4)
    bad = agg[~agg.within_tolerance]
    assert bad.empty, ("Delta_e departs from (1 - 2 eta) theta / pi:\n"
                       + bad.to_string(index=False))
    assert (agg[agg.eta == 0.0].mean_e_pre_oracle == 0.0).all(), "eta = 0 is not Bayes-exact"
    assert abs(agg[agg.eta == ssot.S8_ETA_GRID[1]].mean_e_pre_oracle.mean()
               - ssot.S8_ETA_GRID[1]) < 0.01, "declared eta is not the Bayes error"


# ══════════════════════════════════════════════════════════════════════════════
# 2 and 3. CONSTRAINT 1 -- PRNG neutrality and pre-drift bit-identity
# ══════════════════════════════════════════════════════════════════════════════
@pytest.mark.parametrize("eta", ssot.S8_ETA_GRID)
def test_rotation_stream_draws_two_normals_per_step(eta):
    _, x, _ = rot.make_rotation_stream(1, 0.25, eta)
    _, rng = common.lock_rng(1)
    ref = np.array([[rng.normal(), rng.normal()] for _ in range(128)])
    assert np.array_equal(x[:128], ref), "rotation stream broke the two-draws-per-step convention"


@pytest.mark.parametrize("eta", ssot.S8_ETA_GRID)
def test_rotation_features_are_the_canonical_features(eta):
    """The label noise must consume no feature entropy: same seed, same X, byte for byte."""
    _, x, _ = rot.make_rotation_stream(3, 0.40, eta)
    _, x_canonical, _ = runner.make_stream(3, 0.40)
    assert np.array_equal(x, x_canonical), "label noise displaced the feature draws"


def test_pre_drift_labels_are_bit_identical_to_the_canonical_family():
    """At eta = 0 the pre-drift phase IS the canonical family: warm-up, e_pre, the ARF state at
    tau*. That is what pairs old and new by seed."""
    for seed in common.seed_pool(4):
        for de in (GRID[2], GRID[11]):
            _, _, y = rot.make_rotation_stream(seed, de, 0.0)
            _, _, y_canonical = runner.make_stream(seed, de)
            t = ssot.S8_T_DRIFT
            assert np.array_equal(y[:t], y_canonical[:t]), (seed, de)


def test_label_noise_flips_at_the_declared_rate():
    """The noise channel alone, isolated at a FIXED half-plane.

    Comparing the eta = 0 and eta = 0.05 streams at the same nominal Delta_e would compare two
    different rotations as well as two noise levels. `phi(de / (1 - 2 eta), 0) == phi(de, eta)` by
    the identity, so that pair of calls holds the geometry fixed and leaves only the flips."""
    eta, seed, de = ssot.S8_ETA_GRID[1], 5, 0.30
    assert abs(rot.rotation_phi(de / (1 - 2 * eta), 0.0) - rot.rotation_phi(de, eta)) < 1e-12
    _, _, clean = rot.make_rotation_stream(seed, de / (1 - 2 * eta), 0.0)
    _, _, noisy = rot.make_rotation_stream(seed, de, eta)
    flipped = float(np.mean(clean != noisy))
    assert abs(flipped - eta) < 0.01, flipped


# ══════════════════════════════════════════════════════════════════════════════
# 4. the ab initio arms
# ══════════════════════════════════════════════════════════════════════════════
def test_ab_initio_arms_never_replace_a_tree():
    runs = pq.read_table(_smoke("runs.parquet")).to_pandas()
    assert set(runs["arm"]) == set(ssot.S8_ARM_NAMES), sorted(set(runs["arm"]))
    sub = runs[runs.arm.isin(ssot.S8_AB_INITIO_ARMS)]
    assert len(sub), "no ab initio row in the smoke artifact"
    assert (sub.swaps_total == 0).all(), sub[sub.swaps_total != 0].head().to_string(index=False)
    assert (sub.trees_swapped_total == 0).all()
    assert (sub.fork_t_rel == 0.0).all(), "the fork is not anchored at tau*"
    assert sub.tau_swap_q010.isna().all(), "a tau_swap is finite on an arm that never swaps"


def test_ab_initio_per_tree_tau_is_all_censored():
    per_tree = pq.read_table(_smoke("s8_tau_per_tree.parquet")).to_pandas()
    sub = per_tree[per_tree.arm.isin(ssot.S8_AB_INITIO_ARMS)]
    assert len(sub) == len(sub.groupby(["delta_e", "arm", "seed"])) * ssot.S8_N_MODELS
    assert sub.tau_i.isna().all(), "a tree was replaced on an ab initio arm"


def test_per_tree_tau_reproduces_the_published_order_statistic():
    """tau_swap^(q) is the ceil(q M)-th order statistic of the per-tree vector, by definition of
    both. `transfer_S3.md` section 6 item 1 asked for this vector; this is what makes it checkable
    against the four statistics already published."""
    runs = pq.read_table(_smoke("runs.parquet")).to_pandas().set_index(["delta_e", "arm", "seed"])
    per_tree = pq.read_table(_smoke("s8_tau_per_tree.parquet")).to_pandas()
    checked = 0
    for key, g in per_tree.groupby(["delta_e", "arm", "seed"]):
        tau = np.sort(g.sort_values("tree_index").tau_i.to_numpy(dtype=np.float64))
        for q in ssot.S6_Q_GRID:
            k = int(np.ceil(q * ssot.S8_N_MODELS))
            published = runs.loc[key, f"tau_swap_q{int(round(q * 100)):03d}"]
            if np.isnan(published):
                assert np.isnan(tau[k - 1]), (key, q, tau[k - 1])
            else:
                assert tau[k - 1] == published, (key, q, tau[k - 1], published)
            checked += 1
    assert checked >= 40, f"order-statistic guard checked {checked} pairs, expected at least 40"


# ══════════════════════════════════════════════════════════════════════════════
# 5. write perimeter
# ══════════════════════════════════════════════════════════════════════════════
def test_every_s8_table_carries_the_stream_prefix():
    trees = sorted(ssot.RESULTS_DIR.glob("S8_*"))
    if not trees:
        pytest.skip("no S8 artifact tree -- run the S8 campaigns")
    bad, seen = [], 0
    for tree in trees:
        for tables in tree.rglob("tables"):
            for p in tables.rglob("*"):
                if not p.is_file():
                    continue
                seen += 1
                if not p.name.startswith("s8_"):
                    bad.append(str(p.relative_to(ssot.RESULTS_DIR)))
    if not seen:
        pytest.skip("no S8 table produced yet")
    assert not bad, "S8 tables without the stream prefix:\n  " + "\n  ".join(bad)


def test_s8_writes_nothing_under_the_frozen_trees():
    """The S8 perimeter, enforced on the artifact tree: no S8 basename may appear under R2/R6/R7 or
    under the S6 corpus, whose bit-for-bit freeze is this stream's acceptance gate."""
    frozen = ["R2_instrumented_blind_spot", "R6_hydra_factor", "R7_clock_mismatch",
              "S6_synchronized_traces"]
    bad = [str(p.relative_to(ssot.RESULTS_DIR))
           for name in frozen for p in (ssot.RESULTS_DIR / name).rglob("s8_*") if p.exists()]
    assert not bad, "stream S8 wrote inside a frozen tree:\n  " + "\n  ".join(bad)


# ══════════════════════════════════════════════════════════════════════════════
# 6. the manuscript payloads: every SEARCH anchor must resolve, and none inside the excluded zone
# ══════════════════════════════════════════════════════════════════════════════
# Same invariant `tests/test_S2bis_calibration.py` enforces on transfer_S2bis.md, transposed. S8's
# payloads differ in one respect: they target THREE files -- the manuscript of record and two v2
# section fragments -- so each block names its target on the line above the anchor and the guard
# resolves against that file rather than against a single hard-coded document.
TRANSFER = ROOT_DIR / "docs" / "theory" / "transfer_S8.md"
EXCLUDED_LABELS = ("sec:race", "sec:hydra", "sec:starvation", "sec:decoupling")


def _payload_blocks(path):
    """[(target path, search, replace)] for every fenced SEARCH/REPLACE payload in `path`."""
    import re
    return re.findall(r"^([\w./-]+\.tex)\n<<<<<<< SEARCH\n(.*?)\n=======\n(.*?)\n>>>>>>> REPLACE",
                      path.read_text(encoding="utf-8"), re.S | re.M)


def _excluded_spans(tex):
    """[(lo, hi)] character spans of the four inline subsections CLAUDE.md excludes."""
    import re
    starts = sorted((m.start(), m.group(1)) for label in EXCLUDED_LABELS
                    for m in re.finditer(r"\\subsection\{[^}]*\}\\label\{(" + label + r")\}", tex))
    heads = sorted(m.start() for m in re.finditer(r"\\subsection\{", tex))
    spans = []
    for pos, _ in starts:
        after = [h for h in heads if h > pos]
        spans.append((pos, after[0] if after else len(tex)))
    return spans


def test_transfer_S8_payload_anchors_resolve_uniquely():
    """A SEARCH/REPLACE payload is applicable only while its anchor is present and unique.

    Valid in exactly two states, as S2-bis established: (1, 0) PENDING or (0, 1) APPLIED, the first
    component netted against the replacement so an append-style payload that re-emits its own anchor
    is not read as a duplication."""
    if not TRANSFER.exists():
        pytest.skip("transfer_S8.md not written yet")
    blocks = _payload_blocks(TRANSFER)
    assert blocks, "no SEARCH/REPLACE block found in transfer_S8.md"
    bad = []
    for i, (target, search, replace) in enumerate(blocks, 1):
        path = ROOT_DIR / target
        if not path.exists():
            bad.append(f"block {i}: target {target} does not exist")
            continue
        tex = path.read_text(encoding="utf-8")
        state = (tex.count(search) - tex.count(replace) * replace.count(search), tex.count(replace))
        if state not in [(1, 0), (0, 1)]:
            bad.append(f"block {i} {state} in {target}: {search[:70]!r}")
    assert not bad, ("S8 payloads that are neither pending (1, 0) nor applied (0, 1), as "
                     "(anchors outside the replacement, replacements):\n  " + "\n  ".join(bad))


def test_transfer_S8_payloads_avoid_the_excluded_subsections():
    """`CLAUDE.md` excludes sec:race, sec:hydra, sec:starvation and sec:decoupling until the v65
    assembly. A payload anchored inside one is lost at assembly or duplicated and divergent --
    exactly the failure that had v63 edited while v64 was live, transposed one level down."""
    if not TRANSFER.exists():
        pytest.skip("transfer_S8.md not written yet")
    current = (ROOT_DIR / "docs" / "manuscript" / "CURRENT").read_text(encoding="utf-8").strip()
    main_tex = ROOT_DIR / "docs" / "manuscript" / current
    tex = main_tex.read_text(encoding="utf-8")
    spans = _excluded_spans(tex)
    assert len(spans) == len(EXCLUDED_LABELS), f"excluded subsections not located: {len(spans)}"
    bad = []
    for i, (target, search, _) in enumerate(_payload_blocks(TRANSFER), 1):
        if Path(target).name != current:
            continue
        pos = tex.find(search)
        if pos >= 0 and any(lo <= pos < hi for lo, hi in spans):
            bad.append(f"block {i}: {search[:70]!r}")
    assert not bad, ("S8 payloads anchored inside a subsection CLAUDE.md excludes; they belong in "
                     "docs/manuscript/sections/framework_v2.tex:\n  " + "\n  ".join(bad))
