"""Stream S10 / T10.4 -- Holm over the family this stream enlarges, and over the census.

H0, the verdict of record: the ten tests `protocol_v2.tex` section Multiplicity declares, plus the
eight members S10 adds with rules L2-L4. H1, reported beside it: H0 plus the p-values the live
manuscript carries outside the declared ten -- twenty KS exponentiality tests (`.tex:408`,
`dependence_v2.tex:228`) and one Fisher homogeneity test (`.tex:298`). Every p-value is read from its
artifact, never retyped (docs/theory/S10_decision_rules.md, Part E).

Holm step-down at S10_HOLM_ALPHA; a bootstrap p-value of exactly 0 becomes 1 / (N + 1) with
N = s3_bounds.KS_N_BOOT. The provisional verdicts of L2-L4 are closed here, because they turn on
retention. A claim withdrawn by a declared correction is reported as withdrawn.

Usage:  PYTHONHASHSEED=0 MPLBACKEND=Agg python experiments/S10_external_validity/s10_holm.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "S3_dependence"))
sys.path.insert(0, str(ROOT_DIR / "experiments" / "S6_synchronized_traces"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import experiment_ssot as ssot  # noqa: E402

import s10_latency as lat  # noqa: E402
from s3_bounds import KS_N_BOOT  # noqa: E402

ALPHA = ssot.S10_HOLM_ALPHA
RES = ssot.RESULTS_DIR
R4_TESTS = RES / "R4_proteus_evaluation" / "data" / "exp_R4_seed_level_tests.csv"
R4_ALPHA = RES / "R4_proteus_evaluation" / "data" / "exp_R4_seed_level_tests_KSWIN_alpha_sweep.csv"
TABLE2 = RES / "R5_real_world_evaluation" / "tables" / "table2_values.csv"
KS = RES / "S3" / "ks_exponentiality.csv"
ENVELOPE = RES / "S6_synchronized_traces" / "tables" / "envelope_stats.json"
LATENCY = RES / "S10_external_validity" / "tables" / "s10_latency.json"
OUT = RES / "S10_external_validity" / "tables" / "s10_holm.json"

SITE_R4 = "Table I (.tex sec:proteus, seed-level contrasts); protocol_v2.tex section Multiplicity"
SITE_R5 = "Table II (.tex sec:crossover, real-world validation); protocol_v2.tex section Multiplicity"
SITE_KS = ".tex:408 (sec:starvation_boundary); dependence_v2.tex:228"
SITE_FISHER = ".tex:298 (inside sec:starvation, excluded zone: a charge routes to framework_v2.tex)"
SITE_S10 = "none yet: new claims, carried by charge S10-C"


def holm(pvals, alpha=ALPHA):
    """(retained, adjusted p) under Holm's step-down; ties keep member order (stable sort)."""
    p = np.asarray(pvals, dtype=np.float64)
    m = p.size
    retained, adjusted = np.zeros(m, dtype=bool), np.empty(m)
    running, stopped = 0.0, False
    for k, i in enumerate(np.argsort(p, kind="stable")):
        running = max(running, min(1.0, (m - k) * p[i]))
        adjusted[i] = running
        if not stopped and p[i] <= alpha / (m - k):
            retained[i] = True
        else:
            stopped = True
    return retained, adjusted


def declared_members():
    """The ten of protocol_v2.tex section Multiplicity, from their committed artifacts."""
    r4 = pd.read_csv(R4_TESTS, float_precision="round_trip")
    ra = pd.read_csv(R4_ALPHA, float_precision="round_trip")
    t2 = pd.read_csv(TABLE2, float_precision="round_trip")
    out = [{"member": f"R4-{i + 1}", "claim": f"{r.pipeline_A} vs {r.pipeline_B}",
            "p": float(r.sign_test_p), "site": SITE_R4} for i, r in r4.iterrows()]
    out += [{"member": "R4-alpha", "claim": f"{r.pipeline_A} vs {r.pipeline_B}",
             "p": float(r.sign_test_p), "site": SITE_R4} for _, r in ra.iterrows()]
    out += [{"member": f"R5-{r.variant}", "claim": f"Table II F1 ratio HT/ARF, {r.variant}",
             "p": float(r.sign_test_p), "site": SITE_R5}
            for _, r in t2[t2.dataset == "insects"].iterrows()]
    return out


def s10_members():
    tests = json.loads(LATENCY.read_text(encoding="utf-8"))["tests"]
    return [{"member": name, "claim": f"rule {t['rule']}, {t['arm']}, {t['stream']}: "
                                      f"n+ = {t['n_plus']}, n- = {t['n_minus']}",
             "p": float(t["p"]), "site": SITE_S10} for name, t in sorted(tests.items())]


def census_members():
    ks = pd.read_csv(KS, float_precision="round_trip")
    floor = 1.0 / (KS_N_BOOT + 1)
    out = [{"member": f"S3-KS-{i + 1}", "claim": f"exponential fit of tau_HAT rejected, Delta_e = {r.delta_e}",
            "p": float(r.p_bootstrap) if r.p_bootstrap > 0 else floor,
            "p_as_committed": float(r.p_bootstrap), "site": SITE_KS} for i, r in ks.iterrows()]
    fisher = json.loads(ENVELOPE.read_text(encoding="utf-8"))["crossing_counts"]["envelope_homogeneity"]
    out.append({"member": "S6-homogeneity", "claim": "crossing rate homogeneous across the envelope "
                                                     "(a non-rejection: Holm cannot change it)",
                "p": float(fisher["fisher_exact"]["p_value"]), "site": SITE_FISHER})
    return out


def apply(members):
    retained, adjusted = holm([m["p"] for m in members])
    order = np.argsort([m["p"] for m in members], kind="stable")
    rank = {int(i): k + 1 for k, i in enumerate(order)}
    m = len(members)
    rows = [{**mem, "rank": rank[i], "threshold": ALPHA / (m - rank[i] + 1),
             "adjusted_p": float(adjusted[i]), "retained": bool(retained[i])}
            for i, mem in enumerate(members)]
    return {"m": m, "members": rows,
            "not_retained": [r["member"] for r in sorted(rows, key=lambda r: r["rank"]) if not r["retained"]]}


def close_t10_1(h0, latency):
    """L1-L4 verdicts; L2-L4 turn on retention in the primary family."""
    kept = {r["member"]: r["retained"] for r in h0["members"]}
    tests, out = latency["tests"], {}
    for stream, s in latency["streams"].items():
        sh = s["shifts"][str(ssot.S10_TEST_LAG)]
        t2 = tests[f"S10-L2-{stream}"]
        lo, hi = sh["T_shift_ci"]
        if kept[f"S10-L2-{stream}"] and t2["n_plus"] > t2["n_minus"] and sh["T_shift_over_lag_median"] >= 0.5:
            l2 = "P-b REFUTED"
        elif abs(sh["T_shift_median"]) <= 50 and lo is not None and -50 <= lo and hi <= 50:
            l2 = "P-b HOLDS"
        else:
            l2 = "UNDECIDED"
        t3 = tests[f"S10-L3-{stream}"]
        l3 = ("UNDECIDED" if not kept[f"S10-L3-{stream}"] else
              "P-c HOLDS" if t3["n_minus"] > t3["n_plus"] else "P-c REFUTED")
        l4 = {}
        for arm in ("M1", "M2"):
            t4 = tests[f"S10-L4-{arm}-{stream}"]
            l4[arm] = ("NOT SHOWN" if not kept[f"S10-L4-{arm}-{stream}"] else
                       "REDUCED" if t4["n_minus"] > t4["n_plus"] else "INCREASED")
        l1 = {lag: s["shifts"][lag]["d_shift"][f"{ssot.S10_TEST_LAMBDA:g}"]["verdict_L1"]
              for lag in sorted(s["shifts"], key=int)}
        out[stream] = {"L1_P-a_under_M2": l1, "L2_P-b_under_M2": l2, "L3_P-c_under_M2": l3,
                       "L4_detection_within_deadline": l4,
                       "M1": "P-a and P-b hold by construction (tautological, not evidence)"}
    return out


def main():
    declared, s10, census = declared_members(), s10_members(), census_members()
    only_declared = apply(declared)
    kept = {r["member"]: r["retained"] for r in only_declared["members"]}
    if sum(kept.values()) != 8 or kept["R5-abrupt_balanced"] or kept["R4-alpha"]:
        raise SystemExit("[FATAL] the declared ten no longer reproduce protocol_v2's verdict")
    h0, h1 = apply(declared + s10), apply(declared + s10 + census)
    h1_kept = {r["member"]: r["retained"] for r in h1["members"]}
    flagged = [r["member"] for r in h0["members"] if r["retained"] and not h1_kept[r["member"]]]
    payload = {"alpha": ALPHA, "ks_zero_replaced_by": 1.0 / (KS_N_BOOT + 1),
               "declared_ten_alone": only_declared, "H0_primary": h0, "H1_census": h1,
               "retained_in_H0_not_in_H1": flagged,
               "T10_1_verdicts": close_t10_1(h0, json.loads(LATENCY.read_text(encoding="utf-8"))),
               "env": lat._env()}
    lat._write_json(OUT, payload)
    for name, fam in (("H0", h0), ("H1", h1)):
        print(f"--- {name}: m = {fam['m']}, not retained: {fam['not_retained']}")
    print(f"--- retained in H0, not in H1: {flagged}")
    for stream, v in payload["T10_1_verdicts"].items():
        print(f"    {stream}: {v}")
    return payload


if __name__ == "__main__":
    main()
