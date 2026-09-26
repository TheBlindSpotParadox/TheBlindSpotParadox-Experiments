import json
import re
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent
for _sub in ("", "experiments/S2_theory", "experiments/S6_synchronized_traces",
             "experiments/S6_synchronized_traces/gates", "experiments/S9_detector_coverage"):
    sys.path.insert(0, str(ROOT_DIR / _sub))
from config import experiment_ssot as ssot  # noqa: E402

import s2_arl0 as s2  # noqa: E402
import s9_kswin_dilution as dil  # noqa: E402
import s9_offline_detectors as off  # noqa: E402

S9_TABLES = ssot.RESULTS_DIR / "S9_detector_coverage" / "tables"
ROTATION_RUNS = (ssot.RESULTS_DIR / "S9_detector_coverage" / f"rotation_eta{ssot.S9_HDDDM_ETA:.2f}"
                 / "runs.parquet")
GATE_JSON = ssot.RESULTS_DIR / "S2bis_calibration" / "tables" / "s2bis_proteus_gate.json"
S2_GATE_JSON = ssot.RESULTS_DIR / "S2_theory" / "tables" / "s2_gate_T20.json"
S6_CAUSAL_JSON = ssot.RESULTS_DIR / "S6_synchronized_traces" / "data" / "s6_causal.json"
N_STAT = ssot.S9_KSWIN_STAT
TRANSFER_S2TER = ROOT_DIR / "docs" / "theory" / "transfer_S2ter.md"
MANUSCRIPT_DIR = ROOT_DIR / "docs" / "manuscript"
ARCHIVED_V64 = "articleA_blindspot_v64_camera_ready.tex"
PAYLOAD_RE = re.compile(r"~{9}\n(?P<f>[^\n]+)\n<<<<<<< SEARCH\n(?P<s>.*?)\n=======\n"
                        r"(?P<r>.*?)\n>>>>>>> REPLACE\n~{9}", re.S)
EXCLUDED_SUBSECTIONS = {"sec:race", "sec:hydra", "sec:starvation", "sec:decoupling"}
REGIMES = ("W<=n", "n<W<Wx", "W>=Wx")
EXPECTED_ERROR = {"W<=n": "false_miss", "n<W<Wx": "false_miss", "W>=Wx": "false_detection"}


def _json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def observed_detect(rate):
    return rate is not None and rate >= 1.0 - ssot.S9_EPS


def readable_budget(e_bar_transient, p0, delta_d, m):
    excess = np.clip(np.asarray(e_bar_transient, dtype=np.float64) - p0 - delta_d, 0.0, None)
    if m >= excess.size:
        return float(excess.sum())
    c = np.concatenate(([0.0], np.cumsum(excess)))
    return float(np.max(c[m:] - c[:-m]))


def readable_budget_rectangular(delta_e, w, m, delta_d=0.0):
    return (delta_e - delta_d) * min(w, m)


def generalised_predicts(delta_e, w, n_stat, k_star):
    return bool(readable_budget_rectangular(delta_e, w, n_stat)
                >= max(k_star, ssot.S9_KSWIN_ST_FLOOR * n_stat))


def contrast_predicts(delta_e, w, n_stat, k_star):
    return bool(min(w, n_stat) * delta_e >= k_star)


def b1_measured(a, w, n_stat, alpha):
    return bool(a >= np.sqrt(n_stat * np.log(2.0 / alpha)) + np.sqrt(w / 2.0 * np.log(1.0 / ssot.S9_EPS)))


def crossing_w(alpha, n_stat, k_star, eps=ssot.S9_EPS, delta_p=ssot.DELTA_P):
    r_fa = np.sqrt(n_stat * np.log(2.0 / alpha))
    b = np.sqrt(np.log(1.0 / eps) / 2.0)
    c = k_star / n_stat - delta_p
    return float(((b + np.sqrt(b * b + 4.0 * c * r_fa)) / (2.0 * c)) ** 2)


def amplitude_gap(w, alpha, n_stat, k_star, eps=ssot.S9_EPS, delta_p=ssot.DELTA_P):
    b1 = delta_p + (np.sqrt(n_stat * np.log(2.0 / alpha)) + np.sqrt(w / 2.0 * np.log(1.0 / eps))) / w
    return float(b1 - k_star / min(w, n_stat))


def regime(w, alpha, n_stat, k_star):
    if w <= n_stat:
        return "W<=n"
    return "n<W<Wx" if w < crossing_w(alpha, n_stat, k_star) else "W>=Wx"


def agreement(predicted, cells):
    return Fraction(sum(p == observed_detect(c["rate"]) for p, c in zip(predicted, cells)), len(cells))


def ctrl_grid():
    doc = _json(S9_TABLES / "s9_kswin_dilution.json")
    return doc, [{"delta_e": c["delta_e"], "w": c["w"], "n_stat": c["n_stat"], "alpha": c["alpha"],
                  "k_star": c["k_star"], "rate": c["detect_in_W_rate"], "stored": c}
                 for c in doc["cells"] if c["input_arm"] == "raw"]


def can_grid():
    k_star = {c["alpha"]: c["k_star"] for c in _json(S9_TABLES / "s9_requirement_lattice.json")["grid"]
              if c["n_stat"] == N_STAT}
    # ponytail: A_{n_stat} on the classifier grids is its rectangular reduction at the nominal Delta_e; the trace-level estimator needs the S6 and rotation traces, unreachable from this worktree
    return [{"delta_e": c["delta_e"], "w": c["w_median"], "n_stat": N_STAT, "alpha": c["threshold"],
             "k_star": k_star[c["threshold"]], "rate": c["detect_within_W_rate"], "a": c["a_fw_median"]}
            for c in _json(S9_TABLES / "s9_offline_summary.json")["cells"]
            if c["detector"] == "KSWIN" and c["arm"] == "full" and c["input_arm"] == "raw"
            and c["threshold"] in ssot.S9_KSWIN_ALPHA_GRID]


def rot_grid():
    doc = _json(S9_TABLES / "s9_family_ordering_rotation.json")
    full = pq.read_table(ROTATION_RUNS).to_pandas().query("arm == 'full'")
    full = full.assign(delta_e=full["delta_e"].round(6))
    w_med = full.groupby("delta_e")["w_fw"].median()
    a_med = full.groupby("delta_e")["a_fw"].median()
    p_values = np.array([p for p, _ in off._ks_lattice(N_STAT)])
    rows = []
    for c in doc["cells"]:
        if c["family"] != "KSWIN" or c["input_arm"] != "raw":
            continue
        alpha = doc["levels"]["KSWIN"][c["setting"]]
        rows.append({"delta_e": c["delta_e"], "w": float(w_med[c["delta_e"]]), "n_stat": N_STAT,
                     "alpha": alpha, "k_star": int(np.flatnonzero(p_values <= alpha)[0]),
                     "rate": c["detect_within_W_rate"], "a": float(a_med[c["delta_e"]]),
                     "setting": c["setting"]})
    return rows


def e0():
    doc, ctrl = ctrl_grid()
    can, rot = can_grid(), rot_grid()
    w_published = _json(GATE_JSON)["family_requirements_at_lambda_eq"]["at"]["W"]
    pub = [c for c in rot if c["setting"] == "published"]
    equ = [c for c in rot if c["setting"] == "equalised"]
    t92 = [dil.predictions(c["delta_e"], c["w"], c["n_stat"], c["alpha"], c["k_star"]) for c in ctrl]
    rows = [
        ("contrast, G_ctrl", agreement([p[1] for p in t92], ctrl),
         doc["verdicts"]["model_comparison"]["contrast_agreement"], 4),
        ("B1, G_ctrl", agreement([p[0] for p in t92], ctrl), 0.850, 3),
        ("B1, G_can, W = w_median", agreement([b1_measured(c["a"], c["w"], N_STAT, c["alpha"])
                                              for c in can], can), 0.863, 3),
        ("B1, G_can, W = 57.4", agreement([b1_measured(c["a"], w_published, N_STAT, c["alpha"])
                                          for c in can], can), 0.800, 3),
        ("B1, G_rot, published", agreement([b1_measured(c["a"], c["w"], N_STAT, c["alpha"])
                                           for c in pub], pub), 0.850, 3),
        ("B1, G_rot, equalised", agreement([b1_measured(c["a"], c["w"], N_STAT, c["alpha"])
                                           for c in equ], equ), 1.000, 3),
        ("contrast, G_rot, equalised", agreement([contrast_predicts(c["delta_e"], c["w"], N_STAT,
                                                                    c["k_star"]) for c in equ], equ),
         1.000, 3),
    ]
    return [{"numeral": name, "recomputed": frac, "target": target,
             "verdict": "REPRODUCED" if round(float(frac), digits) == target else "UNREPRODUCED"}
            for name, frac, target, digits in rows]


def e1():
    grids = {"G_ctrl": ctrl_grid()[1], "G_can": can_grid(), "G_rot": rot_grid()}
    out = {}
    for name, cells in grids.items():
        a = [generalised_predicts(c["delta_e"], c["w"], c["n_stat"], c["k_star"]) for c in cells]
        k = [contrast_predicts(c["delta_e"], c["w"], c["n_stat"], c["k_star"]) for c in cells]
        out[name] = {"cells": len(cells), "acc_a": agreement(a, cells), "acc_c": agreement(k, cells),
                     "identical": a == k}
    pooled = sum(v["acc_a"] * v["cells"] for v in out.values()) / sum(v["cells"] for v in out.values())
    bar = out["G_ctrl"]["acc_c"]
    relative = all(v["acc_a"] >= v["acc_c"] for v in out.values())
    return {"grids": out, "pooled_acc_a": pooled, "threshold": bar, "relative_holds": relative,
            "verdict": "RETAINED" if relative and pooled >= bar else "NOT RETAINED"}


def disagreeing_cells():
    out = {}
    for name, cells in (("G_can", can_grid()), ("G_rot", rot_grid())):
        out[name] = [{**{k: c[k] for k in ("delta_e", "alpha", "k_star", "rate", "w")},
                      "contrast_statistic": min(c["w"], c["n_stat"]) * c["delta_e"],
                      "predicted": contrast_predicts(c["delta_e"], c["w"], c["n_stat"], c["k_star"])}
                     for c in cells
                     if contrast_predicts(c["delta_e"], c["w"], c["n_stat"], c["k_star"])
                     != observed_detect(c["rate"])]
    b1_errors = []
    for c in ctrl_grid()[1]:
        b1 = dil.predictions(c["delta_e"], c["w"], c["n_stat"], c["alpha"], c["k_star"])[0]
        if regime(c["w"], c["alpha"], c["n_stat"], c["k_star"]) == "n<W<Wx" and b1 != observed_detect(c["rate"]):
            b1_errors.append({k: c[k] for k in ("delta_e", "w", "n_stat", "alpha", "k_star", "rate")})
    out["G_ctrl, B1 errors with n < W < W_x"] = b1_errors
    return out


def e2():
    tally = {r: {"false_miss": 0, "false_detection": 0} for r in REGIMES}
    sign_defects = set()
    for c in ctrl_grid()[1]:
        b1 = dil.predictions(c["delta_e"], c["w"], c["n_stat"], c["alpha"], c["k_star"])[0]
        obs = observed_detect(c["rate"])
        r = regime(c["w"], c["alpha"], c["n_stat"], c["k_star"])
        if (amplitude_gap(c["w"], c["alpha"], c["n_stat"], c["k_star"]) > 0) != (r != "W>=Wx"):
            sign_defects.add((c["w"], c["n_stat"], c["alpha"]))
        if b1 != obs:
            tally[r]["false_miss" if obs else "false_detection"] += 1
    out = {}
    for r in REGIMES:
        total = sum(tally[r].values())
        share = Fraction(tally[r][EXPECTED_ERROR[r]], total) if total else None
        out[r] = {**tally[r], "expected": EXPECTED_ERROR[r], "share": share,
                  "verdict": ("NOT PRODUCED" if share is None
                              else "CONFIRMED" if share >= Fraction(9, 10) else "REFUTED")}
    return {"regimes": out, "sign_defects": sorted(sign_defects)}


def e3():
    gate = _json(GATE_JSON)["family_requirements_at_lambda_eq"]["at"]
    readings = {
        "tau_swap^(1/M)": gate["W"],
        "W_argmax": _json(S6_CAUSAL_JSON)["kappa_gate_transfer_S1"]["erasure_surrogates"]
                                         ["argmax_A_unrefl"]["mean"],
        "W_fw": _json(S9_TABLES / "s9_offline_summary.json")["W_provenance"]["w_def_times_median"]}
    ceiling = gate["measured_ceiling_median_A_unrefl"]
    series = pd.Series({gate["delta_e"]: ceiling})
    per = {k: s2.floor_and_family(list(gate["p_true_band"]), series, w=v, delta_e=gate["delta_e"])
           for k, v in readings.items()}
    published = _json(S2_GATE_JSON)["floor_and_family"]
    here = per["tau_swap^(1/M)"]
    reproduced = (
        np.allclose(here["floor_chord_interval"], published["floor_chord_interval"], rtol=0, atol=1e-9)
        and all(abs(a[k] - b[k]) <= 1e-9 and a["met_by"] == b["met_by"]
                for a, b in zip(here["family_requirements"]["common_alpha_ladder"],
                                published["family_requirements"]["common_alpha_ladder"])
                for k in ("R_CUSUM", "R_ADWIN", "R_KSWIN", "alpha")))

    def flags(res):
        f = {(r["lambda_cusum"], k): v for r in res["family_requirements"]["common_alpha_ladder"]
             for k, v in r["met_by"].items()}
        f[("deployed", "R_KSWIN")] = bool(
            ceiling >= res["family_requirements"]["deployed_alphas"]["R_KSWIN_at_deployed_alpha"])
        return f

    table = {k: flags(v) for k, v in per.items()}
    first = next(iter(table.values()))
    return {"readings": readings, "reproduced_at_published_W": reproduced, "flags": table,
            "requirements": {k: v["family_requirements"] for k, v in per.items()},
            "floor_chord_interval": {k: v["floor_chord_interval"] for k, v in per.items()},
            "verdict": ("UNREPRODUCED" if not reproduced
                        else "LABEL-ONLY" if all(t == first for t in table.values())
                        else "VERDICT-BEARING")}


def family_table(path):
    doc = _json(path)
    groups = {}
    for c in doc["cells"]:
        if c["input_arm"] == "raw":
            groups.setdefault((c["family"], c["setting"], c["threshold"]), []).append(c)
    rows = {}
    for key, sub in groups.items():
        det = [c["detect_within_W_rate"] for c in sub if c["detect_within_W_rate"] is not None]
        add = [c["add_median"] for c in sub if c["add_median"] is not None]
        rows[key] = {"fa": float(np.mean([c["pre_drift_alarm_rate"] for c in sub])),
                     "det": float(np.mean(det)) if det else None,
                     "add": float(np.median(add)) if add else None,
                     "armed": float(np.mean([c["armed_rate"] for c in sub])) if key[0] == "EDDM" else None}
    return {"p0": doc["D9"]["p0_median"], "armed_t_rel_median": doc["D9"]["armed_t_rel_median"],
            "rows": rows}


def proteus_eddm():
    eddm = next(c for c in _json(GATE_JSON)["eddm_arming_T_D"]["per_couple"]
                if c["couple"] == "EDDM + ARF (c=1)")
    p0 = next(c for c in _json(GATE_JSON)["per_couple"] if c["couple"] == "PHT + ARF (c=1)")
    return {"p0": p0["p_true_pre_drift_mean"], "share_never_armed": eddm["share_never_armed"],
            "detection_rate": eddm["detection_rate"], "n_runs": eddm["n_runs"]}


T4_TARGETS = [
    ("s6", ("KSWIN", "published", None), "det", 0.458, 3),
    ("s6", ("KSWIN", "equalised", None), "det", 0.337, 3),
    ("s6", ("KSWIN", "published", None), "fa", 0.000, 3),
    ("s6", ("KSWIN", "equalised", None), "fa", 0.000, 3),
    ("s6", ("ADWIN", "published", None), "det", 0.885, 3),
    ("s6", ("ADWIN", "equalised", None), "det", 0.926, 3),
    ("s6", ("ADWIN", "published", None), "add", 28.0, 1),
    ("s6", ("ADWIN", "equalised", None), "add", 15.0, 1),
    ("s6", ("ADWIN", "published", None), "fa", 0.000, 3),
    ("s6", ("ADWIN", "equalised", None), "fa", 0.000, 3),
    ("s6", ("EDDM", "published", None), "det", 0.974, 3),
    ("s6", ("EDDM", "published", None), "fa", 0.020, 3),
    ("rotation", ("EDDM", "published", None), "det", 0.022, 3),
    ("rotation", ("EDDM", "published", None), "fa", 0.930, 3),
    ("rotation", ("KSWIN", "published", None), "det", 0.572, 3),
    ("rotation", ("KSWIN", "equalised", None), "det", 0.478, 3),
    ("rotation", ("ADWIN", "published", None), "det", 0.891, 3),
    ("rotation", ("ADWIN", "equalised", None), "det", 0.933, 3),
]


def e4():
    tables = {"s6": family_table(S9_TABLES / "s9_family_ordering.json"),
              "rotation": family_table(S9_TABLES / "s9_family_ordering_rotation.json")}
    checks = [{"stream": s, "row": key, "field": f, "target": t,
               "recomputed": tables[s]["rows"][key][f],
               "verdict": "REPRODUCED" if round(tables[s]["rows"][key][f], d) == t else "UNREPRODUCED"}
              for s, key, f, t, d in T4_TARGETS]
    pe = proteus_eddm()
    checks.append({"stream": "proteus", "row": ("EDDM + ARF (c=1)",), "field": "never armed, 0/1080",
                   "target": (0.0, 1.0, 0.0), "recomputed": (pe["p0"], pe["share_never_armed"],
                                                             pe["detection_rate"]),
                   "verdict": "REPRODUCED" if (pe["p0"], pe["share_never_armed"], pe["detection_rate"])
                   == (0.0, 1.0, 0.0) else "UNREPRODUCED"})
    return {"tables": tables, "proteus_eddm": pe, "checks": checks,
            "verdict": "REPRODUCED" if all(c["verdict"] == "REPRODUCED" for c in checks)
            else "UNREPRODUCED"}


FAMILY_ROWS = [("StrictCUSUM", "published", 15.0), ("StrictCUSUM", "published", 50.0),
               ("PHT", "published", 15.0), ("PHT", "published", 50.0),
               ("ADWIN", "published", None), ("ADWIN", "equalised", None),
               ("KSWIN", "published", None), ("KSWIN", "equalised", None),
               ("EDDM", "published", None)]


def _num(x, fmt):
    return "---" if x is None else f"${x:{fmt}}$"


def family_table_latex():
    v = e4()
    pe = v["proteus_eddm"]
    lines = [f"    EDDM & published & {_num(pe['p0'], '.3f')} & never, $0/{pe['n_runs']}$ & --- & "
             f"{_num(pe['detection_rate'], '.3f')} & --- \\\\", "    \\midrule"]
    for stream in ("s6", "rotation"):
        t = v["tables"][stream]
        for fam, setting, thr in FAMILY_ROWS:
            r = t["rows"][(fam, setting, thr)]
            label = fam if thr is None else f"{fam}, $\\lambda = {thr:g}$"
            armed = (f"${r['armed']:.3f}$ at $t_{{\\mathrm{{rel}}}} = {t['armed_t_rel_median']:+.0f}$"
                     if fam == "EDDM" else "---")
            lines.append(f"    {label} & {setting} & {_num(t['p0'], '.3f')} & {armed} & "
                         f"{_num(r['fa'], '.3f')} & {_num(r['det'], '.3f')} & {_num(r['add'], '.1f')} \\\\")
        lines.append("    \\midrule")
    return "\n".join(lines[:-1])


def equalising_alpha_adwin(w, lam):
    return float(4.0 * w * np.exp(-2.0 * lam ** 2 / w))


def detection_at_operating_point(family, threshold):
    return next(c["detect_within_W_rate"] for c in _json(S9_TABLES / "s9_family_ordering.json")["cells"]
                if c["family"] == family and c["threshold"] == threshold and c["input_arm"] == "raw"
                and c["setting"] == "published" and c["delta_e"] == ssot.S9_DELTA_E_REF)


def test_readable_budget_reduces_to_A_and_to_the_rectangle():
    p0, delta = 0.024, 0.005
    for w in (5, 29, 30, 31, 200):
        for de in (0.05, 0.3268, 1.0 - p0):
            rect = np.full(w, p0 + de)
            for m in (1, 10, 30, 50, 10 ** 6):
                assert readable_budget(rect, p0, delta, m) == pytest.approx((de - delta) * min(w, m))
                assert readable_budget_rectangular(de, w, m, delta) == pytest.approx((de - delta) * min(w, m))
    decay = 0.024 + 0.3 * np.exp(-np.arange(400) / 60.0)
    a_m = [readable_budget(decay, 0.024, 0.005, m) for m in (1, 5, 30, 100, 399, 400, 10 ** 6)]
    assert all(x <= y + 1e-12 for x, y in zip(a_m, a_m[1:]))
    assert a_m[-1] == pytest.approx(np.clip(decay - 0.029, 0, None).sum())
    assert a_m[-2] == a_m[-1] and a_m[0] < a_m[-1]


def test_generalised_predicate_is_the_contrast_predicate_on_every_cell():
    for cells in (ctrl_grid()[1], can_grid(), rot_grid()):
        assert cells
        for c in cells:
            assert c["k_star"] > ssot.S9_KSWIN_ST_FLOOR * c["n_stat"], c
            assert generalised_predicts(c["delta_e"], c["w"], c["n_stat"], c["k_star"]) \
                == contrast_predicts(c["delta_e"], c["w"], c["n_stat"], c["k_star"]), c


def test_grid_shapes_and_the_committed_T92_formulas():
    doc, ctrl = ctrl_grid()
    assert (len(ctrl), len(can_grid()), len(rot_grid())) == (3840, 80, 40)
    for c in ctrl:
        b1, ctr, _, _ = dil.predictions(c["delta_e"], c["w"], c["n_stat"], c["alpha"], c["k_star"])
        s = c["stored"]
        assert (b1, ctr, observed_detect(c["rate"])) == (s["B1_predicts_detect"],
                                                        s["contrast_predicts_detect"],
                                                        s["observed_detect"]), s
    for c in can_grid() + rot_grid():
        assert c["w"] > c["n_stat"], c


def test_gate_json_labels_the_first_swap_time_beside_its_W_alias():
    tau_swap = _json(S6_CAUSAL_JSON)["kappa_gate_transfer_S1"]["mean_tau_swap_1m"]
    gate = _json(GATE_JSON)
    for block in ("cor_split_crossings", "family_requirements_at_lambda_eq"):
        at = gate[block]["at"]
        assert at["W_alias_of"] == "tau_swap_1_over_M", at
        assert at["tau_swap_1_over_M"] == at["W"] == round(tau_swap, 1), at


def test_the_named_documents_carry_no_bare_W_for_the_first_swap_time():
    texts = {p: (ROOT_DIR / p).read_text(encoding="utf-8")
             for p in ("docs/manuscript/sections/framework_v2.tex", "docs/theory/transfer_S2.md",
                       "docs/theory/S2_arl0_recomputation.md")}
    for p, t in texts.items():
        assert "$W = 57.4$" not in t and "`W = 57.4`" not in t, p
    assert texts["docs/manuscript/sections/framework_v2.tex"].count(
        "$\\tau_{\\mathrm{swap}}^{(1/M)} = 57.4$ in place of $W$") == 2
    assert texts["docs/theory/transfer_S2.md"].count("`tau_swap^(1/M) = 57.4` in place of `W`") == 1
    assert texts["docs/theory/S2_arl0_recomputation.md"].count("`tau_swap^(1/M) = 57.4` in place of `W`") == 2


def test_part_C_closed_forms():
    lattice = _json(S9_TABLES / "s9_requirement_lattice.json")["grid"]
    k30 = {c["alpha"]: c["k_star"] for c in lattice if c["n_stat"] == 30}[0.005]
    assert k30 == 14 and crossing_w(0.005, 30, k30) == pytest.approx(47.2657, abs=1e-4)
    assert k30 / 0.70 == pytest.approx(20.0) and k30 / 1.0 == 14.0 and 30 * 0.30 < k30
    for c in lattice:
        n, a, k = c["n_stat"], c["alpha"], c["k_star"]
        wx = crossing_w(a, n, k)
        assert np.floor(wx) > n, c
        assert amplitude_gap(np.floor(wx), a, n, k) > 0 > amplitude_gap(np.ceil(wx), a, n, k), c
        assert all(amplitude_gap(w, a, n, k) > 0 for w in range(1, n + 1)), c


def _payloads(path):
    return PAYLOAD_RE.findall(path.read_text(encoding="utf-8"))


def _target(f):
    if Path(f).name == ARCHIVED_V64:
        return MANUSCRIPT_DIR / (MANUSCRIPT_DIR / "CURRENT").read_text(encoding="utf-8").strip()
    return ROOT_DIR / f


S2TER_I_SINGLE_COLUMN = (("  \\begin{tabular}{llrlrrr}\n", "  \\resizebox{\\textwidth}{!}{%\n  \\begin{tabular}{llrlrrr}\n"),
                         ("  \\end{tabular}\n\\end{table*}", "  \\end{tabular}}\n\\end{table*}"))


def test_transfer_S2ter_payloads_are_applied():
    """All seven payloads are applied, (0, 1). The S8 and S9 transfers they had to avoid while
    pending are applied too, so the overlap check that guarded pending anchors had nothing left to
    compare and is removed rather than kept as a check that cannot fail."""
    payloads = _payloads(TRANSFER_S2TER)
    assert len(payloads) == 7, len(payloads)
    for f, search, replace in payloads:
        if "\\label{tab:family_order}" in replace:
            for old, new in S2TER_I_SINGLE_COLUMN:
                replace = replace.replace(old, new)
        text = _target(f).read_text(encoding="utf-8")
        state = (text.count(search) - text.count(replace) * replace.count(search), text.count(replace))
        assert state == (0, 1), (f, search.splitlines()[0][:80], state)


def test_transfer_S2ter_payloads_avoid_the_excluded_subsections():
    archived = MANUSCRIPT_DIR / ARCHIVED_V64
    text = archived.read_text(encoding="utf-8")
    subs = [(m.start(), m.group(1)) for m in re.finditer(r"\\subsection\{[^}]*\}\\label\{(sec:[^}]+)\}", text)]
    zones = [(lab, pos, subs[i + 1][0] if i + 1 < len(subs) else len(text))
             for i, (pos, lab) in enumerate(subs) if lab in EXCLUDED_SUBSECTIONS]
    assert len(zones) == len(EXCLUDED_SUBSECTIONS), zones
    targets = [search for f, search, _ in _payloads(TRANSFER_S2TER)
               if (ROOT_DIR / f).resolve() == archived.resolve()]
    assert targets
    for search in targets:
        offset = text.find(search)
        assert not [lab for lab, a, b in zones if a <= offset < b], search[:60]


def test_the_ordering_table_payload_is_the_recomputation():
    transfer = TRANSFER_S2TER.read_text(encoding="utf-8")
    assert family_table_latex() in transfer
    assert "family & setting & $p_0$ & armed &" in transfer


def test_published_verdicts():
    assert [r["verdict"] for r in e0()] == ["REPRODUCED"] * 7
    v1 = e1()
    assert v1["verdict"] == "NOT RETAINED" and v1["relative_holds"]
    assert {g: v["acc_a"] for g, v in v1["grids"].items()} == {
        "G_ctrl": Fraction(715, 768), "G_can": Fraction(31, 40), "G_rot": Fraction(9, 10)}
    assert (v1["pooled_acc_a"], v1["threshold"]) == (Fraction(3673, 3960), Fraction(715, 768))
    v2 = e2()
    assert [(v2["regimes"][r]["false_miss"], v2["regimes"][r]["false_detection"], v2["regimes"][r]["verdict"])
            for r in REGIMES] == [(91, 0, "CONFIRMED"), (1, 7, "REFUTED"), (0, 478, "CONFIRMED")]
    assert v2["sign_defects"] == []
    v3 = e3()
    assert v3["verdict"] == "VERDICT-BEARING" and v3["reproduced_at_published_W"]
    assert not any(v3["flags"]["W_argmax"].values()) and not any(v3["flags"]["W_fw"].values())
    assert np.allclose(v3["floor_chord_interval"]["W_argmax"], [7.1125, 11.8284], rtol=0, atol=1e-4)
    assert np.allclose(v3["floor_chord_interval"]["W_fw"], [-7.3323, -2.4648], rtol=0, atol=1e-4)
    assert [equalising_alpha_adwin(w, ssot.R4_PHT_LAMBDA) for w in v3["readings"].values()] == pytest.approx(
        [0.0904116, 1173.05, 6370.52], rel=1e-5)
    assert [detection_at_operating_point(f, ssot.R4_PHT_LAMBDA) for f in ("StrictCUSUM", "PHT")] == [1.0, 1.0]
    assert e4()["verdict"] == "REPRODUCED"


if __name__ == "__main__":
    for r in e0():
        print(f"E0  {r['numeral']:30s} {float(r['recomputed']):.4f} ({r['recomputed']})  "
              f"target {r['target']}  {r['verdict']}")
    v1 = e1()
    for g, v in v1["grids"].items():
        print(f"E1  {g:7s} cells {v['cells']:5d}  acc_a {float(v['acc_a']):.4f} ({v['acc_a']})  "
              f"acc_c {float(v['acc_c']):.4f}  identical {v['identical']}")
    print(f"E1  pooled acc_a {float(v1['pooled_acc_a']):.5f} ({v1['pooled_acc_a']})  threshold "
          f"{float(v1['threshold']):.5f} ({v1['threshold']})  relative {v1['relative_holds']}  "
          f"{v1['verdict']}")
    for g, rows in disagreeing_cells().items():
        print(f"E1  disagreements, {g}: {len(rows)}")
        for r in rows:
            print(f"      {r}")
    v2 = e2()
    for r, v in v2["regimes"].items():
        print(f"E2  {r:7s} false_miss {v['false_miss']:3d}  false_detection {v['false_detection']:3d}  "
              f"share({v['expected']}) {v['share'] if v['share'] is None else round(float(v['share']), 4)}"
              f"  {v['verdict']}")
    print(f"E2  sign defects {v2['sign_defects']}")
    v3 = e3()
    print(f"E3  readings {v3['readings']}  reproduced at published W {v3['reproduced_at_published_W']}")
    for k, req in v3["requirements"].items():
        print(f"E3  {k:15s} floor band {np.round(v3['floor_chord_interval'][k], 3).tolist()}  "
              f"R_KSWIN(deployed) {req['deployed_alphas']['R_KSWIN_at_deployed_alpha']:.3f}")
        for r in req["common_alpha_ladder"]:
            print(f"      lambda {r['lambda_cusum']:4.0f} alpha {r['alpha']:.3e}  R_CUSUM {r['R_CUSUM']:.2f}"
                  f"  R_ADWIN {r['R_ADWIN']:.2f}  R_KSWIN {r['R_KSWIN']:.2f}  met {r['met_by']}")
    print(f"E3  {v3['verdict']}")
    v4 = e4()
    for c in v4["checks"]:
        print(f"E4  {c['stream']:8s} {str(c['row']):40s} {c['field']:22s} target {c['target']}  "
              f"recomputed {c['recomputed']}  {c['verdict']}")
    for s, t in v4["tables"].items():
        print(f"E4  {s}: p0 {t['p0']}  EDDM armed t_rel median {t['armed_t_rel_median']}")
        for key in sorted(t["rows"], key=str):
            print(f"      {str(key):40s} {t['rows'][key]}")
    print(f"E4  {v4['verdict']}")
    for k, w in v3["readings"].items():
        print(f"T4  equalising ADWIN level at lambda = {ssot.R4_PHT_LAMBDA:g}, {k} = {w}: "
              f"{equalising_alpha_adwin(w, ssot.R4_PHT_LAMBDA):.6g}")
    for fam in ("StrictCUSUM", "PHT"):
        print(f"T3  {fam} lambda = {ssot.R4_PHT_LAMBDA:g} at Delta_e = {ssot.S9_DELTA_E_REF}: detection within W "
              f"{detection_at_operating_point(fam, ssot.R4_PHT_LAMBDA)}")
    print(family_table_latex())
