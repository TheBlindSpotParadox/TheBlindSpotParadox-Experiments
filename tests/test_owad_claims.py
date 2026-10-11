import collections
import functools
import hashlib
import inspect
import itertools
import json
import math
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from scipy.special import expit
from scipy.stats import norm

from test_owad_snapshot import OWAD_DIR, TABLE1, table1_rows

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
from config import experiment_ssot as ssot  # noqa: E402

LEDGER = ROOT_DIR / "docs" / "OWAD_CLAIMS.md"
ROW_RE = re.compile(r"^\| [A-Z]\d{2} \|")
# A sign only where it cannot be the dash of a range such as 0.56-0.68.
NUMBER_RE = re.compile(r"(?<![\w.])-?\d+(?:\.\d+)?")
PREFIX_STATUS = {"M": "MATCH", "A": "ANALYTIC", "P": "PROVENANCE", "X": "MISMATCH", "B": "AMBIGUOUS",
                 "U": "UNTRACED", "L": "LAYOUT", "Q": "QUALIFICATION"}

S8 = "results/S8_ab_initio/data/s8_causal.json"
S8_COUNTS = "results/S8_ab_initio/tables/s8_detection_counts.csv"
S6_SPEARMAN = "results/S6_synchronized_traces/tables/first_swap_predictive_power.tex"
HYDRA = "results/audit_S7/hydra_survival.csv"
S13 = "results/S13_evidence_bell/s13_gate.json"
BELL = "results/S13_evidence_bell/evidence_bell.csv"
BLINDSPOT_MAP = "results/S13_evidence_bell/blindspot_map.csv"
ENVELOPE = "results/S6_synchronized_traces/tables/envelope_stats.json"
DELTA_E_C = "results/S6_synchronized_traces/tables/delta_e_c_data_refine.json"
R1_CURRENT = "results/R1_race_condition/data/R1_race_condition.parquet"
R1_OWAD = "results/R1_race_condition/owad2026/data/R1_race_condition.parquet"
R3 = "results/R3_regime_crossover/data/R3_regime_crossover_metrics.parquet"
R3_U1 = "results/audit_S7/s7ter_arms/r3_u1/R3_regime_crossover_metrics.parquet"
R4_U0 = "results/audit_S7/s7ter_arms/u0_frozen/exp_R4_results_aligned_fusion.csv"
R4_CURRENT = "results/R4_proteus_evaluation/data/exp_R4_results_aligned_fusion.csv"
R4_U0_SIGN = "results/audit_S7/s7ter_arms/u0_frozen/exp_R4_seed_level_tests.csv"
R4_TABLES = ("results/audit_S7/s7ter_arms/u0_frozen/table1_proteus_summary.tex",
             "results/R4_proteus_evaluation/owad2026/tables/table1_proteus_summary.tex")
R4_SCRIPT = "experiments/R4_proteus_evaluation/exp_R4_main_table.py"
R4_SEEDBOOT = "results/R4_proteus_evaluation/owad2026_seedboot/tables/table1_proteus_summary.tex"
R5 = "results/R5_real_world_evaluation"
S2BIS_GATE = "results/S2bis_calibration/tables/s2bis_flooding_gate.json"
S9 = "results/S9_detector_coverage/tables/s9_offline_summary.json"
S9_ORDER = "results/S9_detector_coverage/tables/s9_family_ordering.json"
R9 = "results/R9_mcrit/data"

UNTRACED = {
    "U01": "the variant is absent from data/insects/ and its value was withdrawn by the reconciliation",
    "U02": "no artifact counts KSWIN pre-change false alarms per thousand steps on the Bernoulli streams",
    "U03": "no artifact evaluates the classical first-passage bounds over Delta_e",
}
LAYOUT = {
    "L01": "Table I caption, checked by tests/test_owad_snapshot.py",
    "L02": "Table II caption, row labels and sign-test column, checked by tests/test_owad_snapshot.py",
    "L03": "Fig. 1 image, a declared deviation of tests/test_owad_snapshot.py",
}


@functools.cache
def js(rel):
    return json.loads((ROOT_DIR / rel).read_text(encoding="utf-8"))


@functools.cache
def csv(rel):
    return pd.read_csv(ROOT_DIR / rel, float_precision="round_trip")


@functools.cache
def pq(rel):
    return pd.read_parquet(ROOT_DIR / rel)


def text(rel):
    return (ROOT_DIR / rel).read_text(encoding="utf-8")


def theory_delta_e(b):
    return norm.cdf(np.asarray(b) / math.sqrt(2)) - 0.5


def share(name, stat):
    return 100 * js(S8)["decomposition_ab_initio"]["a_pos_common"]["share_ci"][name][stat]


def s8_cross(arm):
    d = csv(S8_COUNTS)
    return d[(d.delta_e == ssot.S8_DECISION_DELTA_E) & (d.arm == arm)].n_cross.item()


def spearman(target, band):
    row = next(ln for ln in text(S6_SPEARMAN).splitlines() if ln.startswith(target + " &"))
    return float(re.search(r"-?\d+\.\d+", row.split("&")[("pooled", "weak", "mid", "strong").index(band) + 1])[0])


def hydra(delta_e, column):
    d = csv(HYDRA)
    return d.loc[d.delta_e == delta_e, column].item()


def powerlaw(series_mean):
    v = series_mean[(series_mean.index > 0) & (series_mean.values > 0)]
    slope, intercept = np.polyfit(np.log(v.index.values), np.log(v.values), 1)
    return math.exp(intercept), slope


def r1(path, lam, column):
    d = pq(path)
    return d[d.lambda_val == lam][column].mean()


def r2(scenario):
    d = pq(f"results/R2_instrumented_blind_spot/data/R2_instrumented_{scenario}_PHT_ARF.parquet")
    return d.assign(delta_e=theory_delta_e(d.boundary_shift).round(6), detect=d.tau_det.notna())


def r2_detect(scenario):
    return r2(scenario).groupby("delta_e").detect.mean()


def blindspot_map(lam):
    d = csv(BLINDSPOT_MAP)
    return d[d.lam == lam].set_index("delta_e").detect


def r7_miss(config):
    d = pq("results/R7_clock_mismatch/data/R7_clock_mismatch.parquet")
    g = d[d.config == config]
    return (g.tau_arf.fillna(np.inf) < g.tau_det.fillna(np.inf)).groupby(g.delta_e.round(6)).mean()


def r3(pipeline, column, path=R3):
    d = pq(path)
    g = d[d.pipeline == pipeline]
    return pd.Series(g[column].values, index=g.delta_e.round(6).values)


def r4_runs(path, detector, clock):
    d = csv(path)
    return d[(d.Detector == detector) & (d.Clock == clock)]


def r4_cells(path, detector, clock, column):
    return r4_runs(path, detector, clock).groupby("Calibration")[column].mean()


def s9_rate(detector, input_arm, threshold, field="detect_within_W_rate"):
    cells = [c for c in js(S9)["cells"] if c["arm"] == "full" and c["detector"] == detector
             and c["input_arm"] == input_arm and c["threshold"] == threshold]
    return sum(c[field] * c["n"] for c in cells) / sum(c["n"] for c in cells)


def mean_alpha_beta(name):
    block = re.search(name + r" = \{(.*?)\n\}", text(R4_SCRIPT), re.S)[1]
    return np.mean([float(a) + float(b) for a, b in re.findall(r"'alpha': ([\d.]+),\s*'beta': ([\d.]+)", block)])


def r4_constant(pattern):
    return float(re.search(pattern, text(R4_SCRIPT))[1])


def flooding(variant, pipeline, column):
    d = pq(f"{R5}/data/flooding_decomposition.parquet")
    return d[(d.variant == variant) & (d.pipeline == pipeline)][column].item()


def m04():
    return [("full", "0", s8_cross("full")), ("no_swap", "18", s8_cross("no_swap")),
            ("no_swap_ab_initio", "49", s8_cross("no_swap_ab_initio")),
            ("drop", "31", s8_cross("no_swap_ab_initio") - s8_cross("no_swap")),
            ("runs per arm", "100", csv(S8_COUNTS).n.max()),
            ("lambda", "50", ssot.S8_DECISION_LAMBDA), ("delta_e", "0.33", ssot.S8_DECISION_DELTA_E)]


def m05():
    src = text("experiments/S6_synchronized_traces/s6_predictive_power.py")
    err, erase = r"$\tau_{\mathrm{err}}(0.50)$", r"$\tau_{\mathrm{erase}}$"
    return [("tau_err(0.50) mid", "0.73", spearman(err, "mid")),
            ("tau_err(0.50) strong", "0.78", spearman(err, "strong")),
            ("tau_erase mid", "0.13", spearman(erase, "mid")), ("tau_erase weak", "-0.14", spearman(erase, "weak")),
            ("band edges", "True", all(s in src for s in ("full.delta_e <= 0.15", "(full.delta_e > 0.15) & (full.delta_e <= 0.35)",
                                                         "full.delta_e > 0.35")))]


def m09():
    hat = pq("results/R6_hydra_factor/data/R6_hat_instrumented.parquet").dropna(subset=["tau_hat"])
    arf = r2("A").dropna(subset=["tau_arf"])
    (_, a_hat), (k_arf, a_arf) = (powerlaw(hat.groupby("delta_e").tau_hat.mean()),
                                  powerlaw(arf.groupby("delta_e").tau_arf.mean()))
    return [("alpha_HAT", "1.02", -a_hat), ("alpha_ARF", "0.98", -a_arf), ("prefactor ARF", "18.5", k_arf)]


def m15():
    bell = csv(BELL).set_index("delta_e")
    plateau = bell[(bell.index >= 0.19) & (bell.index <= 0.25)].smax_mean
    return [("S_max at 0.028186", "5.28", bell.smax_mean[0.028186]), ("lo", "5.01", bell.smax_ci_lo[0.028186]),
            ("hi", "5.55", bell.smax_ci_hi[0.028186]), ("left grid point", "0.028", 0.028186),
            ("plateau points", "2", len(plateau))] + [(f"plateau at {de}", "33", v) for de, v in plateau.items()] + [
            ("S_max at 0.497661", "19.13", bell.smax_mean[0.497661]), ("lo", "18.73", bell.smax_ci_lo[0.497661]),
            ("hi", "19.50", bell.smax_ci_hi[0.497661]), ("right grid point", "0.498", 0.497661)]


def m17():
    a, b, c = r7_miss("A_mismatched"), r7_miss("B_matched"), r7_miss("C_decoupled")
    return [("mismatched min over delta_e > 0.35", "0.51", a[a.index > 0.35].min()),
            ("mismatched max over delta_e > 0.35", "0.72", a[a.index > 0.35].max()),
            ("mismatched above 50 %", "True", a[a.index > 0.35].min() > 0.50),
            ("mismatched at 0.193621", "0.27", a[0.193621]), ("mismatched rises", "True", a.iloc[-1] > a[0.193621]),
            ("matched max over delta_e > 0.30", "0.04", b[b.index > 0.30].max()),
            ("decoupled max over delta_e > 0.30", "0.04", c[c.index > 0.30].max()),
            ("matched at 0.193621", "0.11", b[0.193621])]


def m18():
    rf = r3("RF_Static", "miss_mean")
    return [("ARF false alarms min", "1.01", r3("ARF", "fp_mean").min()), ("max", "1.01", r3("ARF", "fp_mean").max()),
            ("HT false alarms min", "2.00", r3("HT", "fp_mean").min()), ("max", "2.00", r3("HT", "fp_mean").max()),
            ("ARF miss at 0.50", "100", r3("ARF", "miss_mean")[0.5]),
            ("RF_Static miss from 0.25", "0", rf[rf.index >= 0.25].max())]


def m19():
    counts = [("PHT + ARF", "0"), ("EDDM + ARF", "0"), ("SRP + PHT", "0"), ("PHT + HT", "932"), ("EDDM + HT", "882"),
              ("PHT + RF (Static)", "913"), ("ADWIN + RF (Static)", "959"), ("KSWIN + ARF", "1080")]
    out = [(f"{path} {det}", n, int((r4_runs(path, det, 1).F1 > 0).sum())) for path in (R4_U0, R4_CURRENT)
           for det, n in counts]
    out += [(f"{path} runs per pipeline", "1080", len(r4_runs(path, "PHT + HT", 1))) for path in (R4_U0, R4_CURRENT)]
    sign = csv(R4_U0_SIGN)
    return out + [(f"seeds {a} vs {b}", "30", max(fa, fb))
                  for a, b, fa, fb in sign[["pipeline_A", "pipeline_B", "seeds_favor_A", "seeds_favor_B"]].values]


def m20():
    return [("ADWIN+ARF c1 detections", "1063", int((r4_runs(R4_U0, "ADWIN + ARF", 1).F1 > 0).sum())),
            ("PHT+ARF c32 F1 min", "0.56", r4_cells(R4_U0, "PHT + ARF", 32, "F1").min()),
            ("PHT+ARF c32 F1 max", "0.68", r4_cells(R4_U0, "PHT + ARF", 32, "F1").max()),
            ("ADWIN+ARF c1 F1 min", "0.96", r4_cells(R4_U0, "ADWIN + ARF", 1, "F1").min()),
            ("current ADWIN+ARF c1 detections", "1070", int((r4_runs(R4_CURRENT, "ADWIN + ARF", 1).F1 > 0).sum())),
            ("current PHT+ARF c32 F1 min", "0.6056", r4_cells(R4_CURRENT, "PHT + ARF", 32, "F1").min()),
            ("current PHT+ARF c32 F1 max", "0.6750", r4_cells(R4_CURRENT, "PHT + ARF", 32, "F1").max()),
            ("current ADWIN+ARF c1 F1 min", "0.9778", r4_cells(R4_CURRENT, "ADWIN + ARF", 1, "F1").min()),
            ("the external ADWIN runs at the clock c of its pipeline", "True",
             "lambda cc=c: adwin(cc)" in text(R4_SCRIPT))]


def m21():
    out = []
    for path in (R4_U0, R4_CURRENT):
        rf = r4_cells(path, "PHT + RF (Static)", 1, "F1")
        out += [(f"{path} PHT+HT F1 min", "0.75", r4_cells(path, "PHT + HT", 1, "F1").min()),
                (f"{path} PHT+RF F1 min", "0.73", rf.min()), (f"{path} PHT+RF F1 max", "0.96", rf.max())]
        out += [(f"{path} KSWIN c{c} {col}", v, r4_cells(path, "KSWIN + ARF", c, col).agg(agg))
                for c in (1, 32) for col, v, agg in (("F1", "1.00", "min"), ("ADD", "14", "min"), ("ADD", "14", "max"))]
    return out


def m23():
    t2 = csv(f"{R5}/tables/table2_values.csv").set_index("variant")
    ins = pq(f"{R5}/data/insects_results.parquet")
    arf = ins[(ins.variant == "gradual_balanced") & (ins.pipeline == "pht_arf_c1")]
    return [("ARF alarms", "86", flooding("gradual_balanced", "pht_arf_c1", "n_alarms")),
            ("ARF alarms seed mean", "85.67", flooding("gradual_balanced", "pht_arf_c1", "n_alarms")),
            ("ARF alarms seed median", "79.5", arf.n_detections.median()),
            ("HT alarms", "7", flooding("gradual_balanced", "pht_ht", "n_alarms")),
            ("ARF precision", "0.012", flooding("gradual_balanced", "pht_arf_c1", "precision")),
            ("HT precision", "0.14", flooding("gradual_balanced", "pht_ht", "precision")),
            ("ARF F1", "0.02", t2.F1_PHT_ARF["gradual_balanced"]), ("HT F1", "0.25", t2.F1_PHT_HT["gradual_balanced"]),
            ("ratio gradual", "10.57", t2.ratio["gradual_balanced"]),
            ("ratio reoccurring", "1.61", t2.ratio["incremental_reoccurring_balanced"]),
            ("abrupt ARF F1", "0.18", t2.F1_PHT_ARF["abrupt_balanced"]),
            ("abrupt HT F1", "0.13", t2.F1_PHT_HT["abrupt_balanced"])]


def m24():
    de = pq(f"{R5}/data/delta_e.parquet").set_index("variant")
    config = text("experiments/R5_real_world_evaluation/exp_R5_config.py")
    per_drift = list(de.delta_e_per_drift["abrupt_balanced"])
    return [("abrupt", "0.07", de.delta_e_mean["abrupt_balanced"]), ("gradual", "0.45", de.delta_e_mean["gradual_balanced"]),
            ("reoccurring", "0.39", de.delta_e_mean["incremental_reoccurring_balanced"])] + [
            (f"transition {k}", v, x) for k, (v, x) in enumerate(zip(("0.68", "-0.15", "0.24", "-0.27", "-0.13"), per_drift))] + [
            ("transitions", "5", len(per_drift)),
            ("window cap", "5000", float(re.search(r"DELTA_E_WINDOW_CAP\s*=\s*([\d_]+)", config)[1].replace("_", ""))),
            ("window factor", "3", float(re.search(r"DELTA_E_WINDOW_FACTOR\s*=\s*(\d+)", config)[1]))]


def m28():
    manifest = text("results/audit_S7/_baseline/artifacts_sha256_pre_ssot.txt")
    frozen = re.search(r"^(\w{64})  results/R1_race_condition/data/R1_race_condition.parquet$", manifest, re.MULTILINE)[1]
    figure = ROOT_DIR / "results/R1_race_condition/owad2026/figures/Fig_R1_race_condition.png"
    return [("alarm rate", "0.965", r1(R1_OWAD, 25.0, "tau_det_emp_finite")),
            ("printed > 95 %", "True", r1(R1_OWAD, 25.0, "tau_det_emp_finite") > 0.95),
            ("preemption", "88", 100 * r1(R1_OWAD, 25.0, "blind_spot_observed")),
            ("parquet equals its frozen manifest entry", "True",
             hashlib.sha256((ROOT_DIR / R1_OWAD).read_bytes()).hexdigest() == frozen),
            ("figure sha256", "0075b9757df81835406ad9ac003e0910e7e09e5896b96de03297ae165fcfcbc1",
             hashlib.sha256(figure.read_bytes()).hexdigest())]


def m29():
    out = []
    for arm, path, values in (("current", R1_CURRENT, ("0.035", "0.195", "0.685", "0.895")),
                              ("published", R1_OWAD, ("0.035", "0.170", "0.640", "0.880"))):
        out += [(f"{arm} lambda {lam}", v, r1(path, lam, "blind_spot_observed"))
                for lam, v in zip((10.0, 15.0, 20.0, 25.0), values)]
    return out


def m30():
    snapshot = table1_rows(OWAD_DIR / TABLE1)
    regenerated = ROOT_DIR / "results/R4_proteus_evaluation/owad2026/data"
    return [("snapshot rows", "14", len(snapshot))] + [
        (f"{path} rows identical to the snapshot", "True", table1_rows(ROOT_DIR / path) == snapshot)
        for path in R4_TABLES] + [
        (f"regenerated {name} identical to u0_frozen", "True",
         (regenerated / name).read_bytes() == (ROOT_DIR / "results/audit_S7/s7ter_arms/u0_frozen" / name).read_bytes())
        for name in ("exp_R4_results_aligned_fusion.csv", "exp_R4_seed_level_tests.csv")]


def m38():
    env = " ".join(text("docs/ENVIRONMENT.md").split())
    return [("CPU", "True", "AMD EPYC 8224P, 24 cores / 48 threads" in env), ("RAM", "True", "192 GB nominal" in env)]


def m39():
    tickers = re.findall(r"'(\w+)'", re.search(r"TICKERS\s*=\s*\[([^\]]*)\]", text(R4_SCRIPT))[1])
    transitions = len(list(itertools.permutations(tickers, 2)))
    regimes = len(re.findall(r"\('(?:IID|Cal\. [AB])', ETF_PARAMS_[AB]\)", text(R4_SCRIPT)))
    return [("tickers", "4", len(tickers)), ("transitions", "12", transitions),
            ("widths", "True", ssot.R4_DRIFT_WIDTHS == [100, 500, 1000]), ("n", "8000", ssot.R4_N_STEPS),
            ("tau*", "4000", ssot.R4_T_DRIFT), ("alpha + beta, Cal. A", "0.95", mean_alpha_beta("ETF_PARAMS_A")),
            ("alpha + beta, Cal. B", "0.99", mean_alpha_beta("ETF_PARAMS_B")),
            ("Student-t degrees of freedom", "7", r4_constant(r"nu\s*=\s*([\d.]+)")), ("seeds", "30", len(ssot.R4_SEEDS)),
            ("streams per cell", "360", transitions * len(ssot.R4_SEEDS)),
            ("volatility window", "20", r4_constant(r"rolling\((\d+)")),
            ("tolerance floor", "1000", r4_constant(r"max\((\d+), w\)")), ("lambda", "15", ssot.R4_PHT_LAMBDA),
            ("regimes", "3", regimes), ("streams per seed", "36", transitions * regimes),
            ("IID regime has no GARCH recursion", "True",
             "if regime_name == 'IID':" in text(R4_SCRIPT) and "np.random.standard_normal(n_steps)" in text(R4_SCRIPT))]


def b04():
    spans = [tuple(map(float, s)) for s in
             re.findall(r"axvspan\(([\d.]+), ([\d.]+)", text("experiments/R3_regime_crossover/exp_R3_regime_crossover.py"))]
    arf, ht, bell = r3("ARF", "miss_mean"), r3("HT", "miss_mean"), csv(BELL).set_index("delta_e").smax_mean
    return [("weak signal upper", "0.09", spans[0][1]), ("safe zone lower", "0.09", spans[1][0]),
            ("safe zone upper", "0.25", spans[1][1]), ("blind spot lower", "0.25", spans[2][0]),
            ("ARF miss at 0.26", "1", arf[0.26]), ("ARF miss at 0.294286", "2", arf[0.294286]),
            ("ARF miss at 0.328571", "8", arf[0.328571]), ("HT miss at 0.328571", "2", ht[0.328571]),
            ("S_max at 0.287108", "31.81", bell[0.287108]), ("S_max at 0.326793", "31.33", bell[0.326793])]


def a01():
    shifts = [abs(b * b - a * a) / 200 for a, b in itertools.pairwise((8, 9, 7, 9.5))]
    return [("8 -> 9", "0.085", shifts[0]), ("9 -> 7", "0.16", shifts[1]), ("7 -> 9.5", "0.21", shifts[2]),
            ("largest at most 0.21", "True", max(shifts) <= 0.21)]


def a04():
    from river import forest
    return [("lambda_value", "6", inspect.signature(forest.ARFClassifier).parameters["lambda_value"].default)]


def a05():
    from river import drift
    return [("clock", "32", drift.ADWIN().clock)]


def a06():
    t = np.arange(ssot.R4_T_DRIFT + 1)
    return [("a positive pre-change label exists", "False",
             any((expit(4.0 * (t - ssot.R4_T_DRIFT) / w) > 0.5).any() for w in ssot.R4_DRIFT_WIDTHS))]


def x01():
    a = r2("A")
    late = a[a.delta_e > 0.24]
    return [("detections above 0.24", "1", late.detect.sum()), ("runs above 0.24", "1600", len(late)),
            ("detecting seed", "6", late[late.detect].seed.item()), ("at", "0.326793", late[late.detect].delta_e.item()),
            ("S13 at 0.242568", "0.01", blindspot_map(50.0)[0.242568])]


def x09():
    m = csv(f"{R9}/results_instrumented_matched_cext1_ADWIN_HAT.csv")
    miss = m.tau_hat.fillna(np.inf) < m.tau_det.fillna(np.inf)
    strong = theory_delta_e(m.boundary_shift) > 0.30
    return [("grid", "35.2", 100 * miss.mean()), ("delta_e > 0.30", "29.7", 100 * miss[strong].mean())]


def x10():
    env = " ".join(text("docs/ENVIRONMENT.md").split())
    hours = float(re.search(r"\*\*Total, stages summed\*\* \| \*\*([\d ]+) s =", env)[1].replace(" ", "")) / 3600
    return [("composition of 2026-10-01 marked superseded", "True", "**Superseded (2026-10-10).**" in env),
            ("measured total, hours", "10.32", hours), ("within [4.5 h, 5.5 h)", "False", 4.5 <= hours < 5.5)]


def x12():
    levels = js(S9_ORDER)["levels"]
    return [("ADWIN equalised", "0.0904", levels["ADWIN"]["equalised"]),
            ("ADWIN factor", "45.2", levels["ADWIN"]["equalised"] / levels["ADWIN"]["published"]),
            ("KSWIN equalised", "0.0011", levels["KSWIN"]["equalised"]),
            ("KSWIN factor", "4.52", levels["KSWIN"]["published"] / levels["KSWIN"]["equalised"])]


def q04():
    sys.path.insert(0, str(ROOT_DIR / "experiments" / "R4_proteus_evaluation"))
    import exp_R4_main_table as r4

    def widths(tex):
        row = next(ln for ln in tex.splitlines() if ln.strip().startswith(r"\textbf{PHT + ARF} ($c_{\mathrm{int}} = 32$)"))
        return [float(x) for x in re.findall(r"\$\\pm\$(\d\.\d+)", row)]

    run_level, seed_level = widths(text(R4_TABLES[0])), widths(text(R4_SEEDBOOT))
    current = widths(text("results/R4_proteus_evaluation/tables/table1_proteus_summary.tex"))
    return [("published run-level min", "0.05", min(run_level)), ("max", "0.05", max(run_level)),
            ("seed-level on the published data min", "0.13", min(seed_level)), ("max", "0.15", max(seed_level)),
            ("seed-level body rows equal the in-memory computation", "True",
             table1_rows(ROOT_DIR / R4_SEEDBOOT) == table1_rows(r4.summarise(csv(R4_U0), "seed")[1])),
            ("seed-level on the current data min", "0.12", min(current)), ("max", "0.15", max(current))]


CHECKS = {
    "M01": lambda: [("median", "98.6", share("share_learn_pure", "median")),
                    ("lo", "98.5", share("share_learn_pure", "lo")), ("hi", "98.8", share("share_learn_pure", "hi"))],
    "M02": lambda: [("median", "0.71", share("share_swap_first", "median")),
                    ("lo", "0.63", share("share_swap_first", "lo")), ("hi", "0.78", share("share_swap_first", "hi"))],
    "M03": lambda: [("median", "0.56", share("share_swap_rest", "median"))],
    "M04": m04,
    "M05": m05,
    "M06": lambda: [("delta_e", "0.14", 0.140949), ("rmst ratio", "4.12", hydra(0.140949, "rmst_ratio")),
                    ("lo", "3.45", hydra(0.140949, "rmst_ratio_ci_lo")), ("hi", "4.96", hydra(0.140949, "rmst_ratio_ci_hi")),
                    ("median ratio", "5.32", hydra(0.140949, "median_ratio"))],
    "M07": lambda: [("delta_e", "0.33", 0.326793), ("rmst ratio", "7.99", hydra(0.326793, "rmst_ratio")),
                    ("lo", "6.40", hydra(0.326793, "rmst_ratio_ci_lo")), ("hi", "9.72", hydra(0.326793, "rmst_ratio_ci_hi")),
                    ("median ratio", "3.10", hydra(0.326793, "median_ratio"))],
    "M08": lambda: [("ARF censored fraction max", "0", csv(HYDRA).censored_frac_arf.max()), ("rows", "20", len(csv(HYDRA))),
                    ("horizon", "4000", ssot.CENSORING_HORIZON)],
    "M09": m09,
    "M10": lambda: [("alpha", "1.77", -js(S13)["tau_exponent"]["estimate"]),
                    ("ci low", "1.67", -js(S13)["tau_exponent"]["ci_hi"]),
                    ("ci high", "1.90", -js(S13)["tau_exponent"]["ci_lo"]),
                    ("fit domain", "0.10", js(S13)["tau_exponent"]["domain_min"])],
    "M11": lambda: [("beta_2", "0.50", js(S13)["curvature"]["quadratic_coef"]),
                    ("lo", "0.30", js(S13)["curvature"]["quadratic_ci"][0]),
                    ("hi", "0.76", js(S13)["curvature"]["quadratic_ci"][1])],
    "M12": lambda: [("estimate", "0.120", js(DELTA_E_C)["delta_e_c"]["interpolated"]["estimate"]),
                    ("lo", "0.114", js(DELTA_E_C)["delta_e_c"]["interpolated"]["ci_lo_2p5"]),
                    ("hi", "0.127", js(DELTA_E_C)["delta_e_c"]["interpolated"]["ci_hi_97p5"])],
    "M13": lambda: [("lambda_op", "21.93", js(ENVELOPE)["lambda_op_bootstrap"]["0.20_0.40"]["estimate"]),
                    ("lo", "19.88", js(ENVELOPE)["lambda_op_bootstrap"]["0.20_0.40"]["ci_lo_2p5"]),
                    ("hi", "22.40", js(ENVELOPE)["lambda_op_bootstrap"]["0.20_0.40"]["ci_hi_97p5"]),
                    ("envelope lo", "0.20", js(ENVELOPE)["lambda_op_bootstrap"]["0.20_0.40"]["envelope"][0]),
                    ("envelope hi", "0.40", js(ENVELOPE)["lambda_op_bootstrap"]["0.20_0.40"]["envelope"][1])],
    "M14": lambda: [("fraction below lambda_FA", "62.6", 100 * js(ENVELOPE)["lambda_op_bootstrap"]["0.20_0.50"]["fraction_below_15"]),
                    ("replicates", "10000", js(ENVELOPE)["lambda_op_bootstrap"]["0.20_0.50"]["n_bootstrap"]),
                    ("envelope hi", "0.50", js(ENVELOPE)["lambda_op_bootstrap"]["0.20_0.50"]["envelope"][1])],
    "M15": m15,
    "M16": lambda: [("lambda", "8", ssot.R2_LAMBDAS[2]), ("detection at 0.085449", "0.97", r2_detect("C")[0.085449]),
                    ("lowest detection from 0.140949", "1.00", r2_detect("C")[r2_detect("C").index >= 0.140949].min())],
    "M17": m17,
    "M18": m18,
    "M19": m19,
    "M20": m20,
    "M21": m21,
    "M22": lambda: [("CUSUM", "0.928", s9_rate("PHT", "raw", 15.0)), ("ADWIN", "0.885", s9_rate("ADWIN", "raw", None))],
    "M23": m23,
    "M24": m24,
    "M25": lambda: [(stat, v, agg(js(S2BIS_GATE)["variants"][var]["budget_span_mismatch"]["pht_arf_c1"]["p_true_span_mean"]
                                  for var in js(S2BIS_GATE)["variants"]))
                    for stat, v, agg in (("min", "0.16", min), ("max", "0.26", max))],
    "M26": lambda: [("precision", "0.33", csv("results/S2bis_calibration/tables/s2bis_insects_sweep.csv").query(
        "variant == 'gradual_balanced' and pipeline == 'pht_arf_c1' and alarms_pre_change <= 1").precision_bp.max())],
    "M27": lambda: [("shared generator", "True", js("results/S3/rng_factorization.json")["aliasing_all_trees_share_forest_rng"]),
                    ("verdict", "DOES NOT FACTORISE", js("results/S3/rng_factorization.json")["verdict"])],
    "M28": m28,
    "M29": m29,
    "M30": m30,
    "M31": lambda: [("c_int", "1", ssot.C_INT), ("c_ext", "32", ssot.C_EXT), ("ratio", "32", ssot.C_EXT / ssot.C_INT)],
    "M32": lambda: [("river", "0.23.0", re.search(r"^river==(\S+)$", text("requirements.txt"), re.MULTILINE)[1])],
    "M33": lambda: [("ARF", "10", ssot.N_MODELS), ("HAT", "1", ssot.R6_N_MODELS)],
    "M34": lambda: [("delta_e", "0.25", ssot.R1_DELTA_E), ("seeds", "200", ssot.R1_N_SEEDS),
                    ("horizon", "50000", ssot.R1_CENSORING_HORIZON)],
    "M35": lambda: [("lambda A", "50", ssot.R2_LAMBDAS[0]), ("lambda B", "25", ssot.R2_LAMBDAS[1]),
                    ("lambda C", "8", ssot.R2_LAMBDAS[2]), ("delta_P", "0.01", ssot.R2_CUSUM_DELTA),
                    ("seeds", "100", len(ssot.R2_SEEDS))],
    "M36": lambda: [(col, v, pq("results/R7_clock_mismatch/data/R7_clock_mismatch.parquet")[col].nunique())
                    for col, v in (("seed", "100"), ("delta_e", "20"), ("config", "3"))],
    "M37": lambda: [("delta_P", "0.01", js(ENVELOPE)["config"]["audit_delta_p"]),
                    ("alpha", "0.05", float(re.search(r"np\.quantile\(s\[idx\], ([\d.]+)",
                                                      text("experiments/S6_synchronized_traces/s6_envelope_stats.py"))[1]))],
    "M38": m38,
    "M39": m39,
    "M40": lambda: [("streams", "100", ssot.R3_N_SEEDS), ("steps", "8000", ssot.R3_N_STEPS), ("t*", "4000", ssot.R3_T_DRIFT),
                    ("lambda", "25", ssot.R3_PHT_LAMBDA), ("delta_P", "0.005", ssot.R3_DELTA_P), ("c_int", "1", ssot.R3_C_INT),
                    ("horizon", "1000", ssot.R3_TAU_TOL), ("grid low", "0.02", ssot.R3_DELTA_E_GRID.min()),
                    ("grid high", "0.50", ssot.R3_DELTA_E_GRID.max())],
    "M41": lambda: [("streams", "6", len(csv(f"{R5}/tables/table2_values.csv"))), ("seeds", "30", ssot.N_SEEDS_REAL)],
    "A01": a01,
    "A02": lambda: [("Delta_e at b = 4.0", "0.50", theory_delta_e(4.0))],
    "A03": lambda: [("p in units of 1e-9", "2", 2 * 0.5 ** 30 / 1e-9)],
    "A04": a04,
    "A05": a05,
    "A06": a06,
    "P01": lambda: [("S13 at 0.326793", "0.92", blindspot_map(25.0)[0.326793]),
                    ("S13 at 0.497661", "0.04", blindspot_map(25.0)[0.497661]),
                    ("R2 B at 0.326793", "0.95", r2_detect("B")[0.326793]),
                    ("R2 B at 0.497661", "0.01", r2_detect("B")[0.497661])],
    "P02": lambda: [("S13 detection at 0.326793", "0.00", blindspot_map(50.0)[0.326793]),
                    ("R2 A miss at 0.326793", "0.99", 1 - r2_detect("A")[0.326793])],
    "P03": lambda: [("alpha 0.05 raw", "0.7134", s9_rate("KSWIN", "raw", 0.05)),
                    ("alpha 0.005 raw", "0.4642", s9_rate("KSWIN", "raw", 0.005)),
                    ("alpha 0.005 smoothed", "0.000", s9_rate("KSWIN", "smoothed", 0.005)),
                    ("smoothed pre-drift alarm rate", "1.00", s9_rate("KSWIN", "smoothed", 0.005, "pre_drift_alarm_rate"))],
    "X01": x01,
    "X02": lambda: [("lowest R2 A miss", "0.97", 1 - r2_detect("A").max()), ("at", "0.193621", r2_detect("A").idxmax()),
                    ("lowest S13 miss", "0.99", 1 - blindspot_map(50.0).max())],
    "X03": lambda: [("S13", "0.13", blindspot_map(25.0)[0.085449]), ("R2 B", "0.22", r2_detect("B")[0.085449])],
    "X04": lambda: [(f"HT at {de}", v, r3("HT", "miss_mean")[de]) for de, v in ((0.02, "77"), (0.054286, "73"), (0.088571, "71"))],
    "X05": lambda: [(f"ARF at {de}", v, r3("ARF", "miss_mean")[de])
                    for de, v in ((0.088571, "1"), (0.122857, "1"), (0.157143, "1"), (0.191429, "0"), (0.225714, "0"))],
    "X06": lambda: [("RF_Static", "0.7498", r3("RF_Static", "acc_mean")[0.5]), ("ARF", "0.9840", r3("ARF", "acc_mean")[0.5]),
                    ("gap in points", "23.4", 100 * (r3("ARF", "acc_mean")[0.5] - r3("RF_Static", "acc_mean")[0.5]))],
    "X07": lambda: [("mean delta_e-hat at b = 4.0", "-0.0235", csv(f"{R9}/results_instrumented_A_ADWIN_HAT.csv").query(
        "boundary_shift == 4.0").delta_e.mean())],
    "X08": lambda: [("ADD min", "31", r4_runs(R4_U0, "ADWIN + ARF", 32).ADD.min()),
                    ("ADD max", "31", r4_runs(R4_U0, "ADWIN + ARF", 32).ADD.max()),
                    ("uniform phase mean offset", "15.5", np.arange(32).mean())],
    "X09": x09,
    "X10": x10,
    "X11": lambda: [("grid low", "0.028186", theory_delta_e(ssot.BOUNDARY_SHIFTS.min())),
                    ("grid high", "0.497661", theory_delta_e(ssot.BOUNDARY_SHIFTS.max()))],
    "X12": x12,
    "B01": lambda: [("pooled detections", "5", r2("A").detect.sum()), ("runs", "2000", len(r2("A"))),
                    ("largest R2 rate", "0.03", r2_detect("A").max()), ("largest S13 rate", "0.01", blindspot_map(50.0).max())],
    "B02": lambda: [("rmst_arf at 0.028186", "171.4", hydra(0.028186, "rmst_arf"))],
    "B03": lambda: [(regime, v, r4_cells(R4_U0, "PHT + ARF", 32, "ADD")[regime])
                    for regime, v in (("IID", "19.38"), ("Cal. A", "19.81"), ("Cal. B", "19.47"))],
    "B04": b04,
    "Q01": lambda: [("ratio", "1.27", js(S2BIS_GATE)["B3_headline"]["at_lambda_eq"]["point"]),
                    ("lo", "1.16", js(S2BIS_GATE)["B3_headline"]["at_lambda_eq"]["ci"][0]),
                    ("hi", "1.43", js(S2BIS_GATE)["B3_headline"]["at_lambda_eq"]["ci"][1]),
                    ("share of the log-ratio", "0.899",
                     js(S2BIS_GATE)["variants"]["gradual_balanced"]["decomposition_B4"]["share_threshold_attributable"])] + [
        (f"lambda {pipe}", v, js(S2BIS_GATE)["variants"]["gradual_balanced"]["budget_span_mismatch"][pipe]["lambda_eq_T_warm_mean"])
        for pipe, v in (("pht_arf_c1", "20.97"), ("pht_ht", "132.50"))],
    "Q02": lambda: [(var, v, pq(f"{R5}/data/delta_e_oracle.parquet").set_index("variant").delta_e_mean[var])
                    for var, v in (("abrupt_balanced", "0.034"), ("gradual_balanced", "-0.003"),
                                   ("incremental_reoccurring_balanced", "-0.109"))],
    "Q03": lambda: [(f"ARF at {de}", v, r3("ARF", "miss_mean", R3_U1)[de])
                    for de, v in ((0.088571, "69"), (0.122857, "24"), (0.157143, "13"), (0.191429, "5"), (0.225714, "5"))],
    "Q04": q04,
}


def ledger():
    rows = {}
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        if ROW_RE.match(line):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            assert len(cells) == 6, f"{cells[0]}: {len(cells)} cells, expected 6"
            assert cells[0] not in rows, f"duplicate ledger ID {cells[0]}"
            rows[cells[0]] = cells
    return rows


def in_row(expected, row):
    try:
        return float(expected) in {float(n) for n in NUMBER_RE.findall(row.replace(",", ""))}
    except ValueError:
        return expected.lower() in row.lower()


def holds(expected, value):
    if isinstance(value, str):
        return value == expected
    if isinstance(value, (bool, np.bool_)):
        return str(bool(value)) == expected
    places = len(expected.split(".")[1]) if "." in expected else 0
    return abs(float(value) - float(expected)) <= 0.5 * 10 ** -places + 1e-9


def test_every_ledger_row_has_exactly_one_check():
    rows = {r: cells[5] for r, cells in ledger().items()}
    assert rows, f"no row parsed from {LEDGER.relative_to(ROOT_DIR)}"
    wrong_status = sorted(r for r, s in rows.items() if PREFIX_STATUS.get(r[0]) != s)
    assert not wrong_status, f"rows whose status does not match their ID prefix: {wrong_status}"
    checked = {r for r, s in rows.items() if s not in ("UNTRACED", "LAYOUT")}
    assert checked == set(CHECKS), (f"ledger rows without a check {sorted(checked - set(CHECKS))}, "
                                    f"checks without a ledger row {sorted(set(CHECKS) - checked)}")
    for status, declared in (("UNTRACED", UNTRACED), ("LAYOUT", LAYOUT)):
        in_ledger = {r for r, s in rows.items() if s == status}
        assert in_ledger == set(declared), (f"{status} rows in the ledger {sorted(in_ledger)} against the "
                                            f"module constant {sorted(declared)}")


def test_readme_status_counts_match_the_ledger():
    readme = (ROOT_DIR / "README.md").read_text(encoding="utf-8")
    printed = {s: int(n) for s, n in re.findall(r"^\| ([A-Z]+) \| (\d+) \|$", readme, re.MULTILINE)}
    counts = collections.Counter(cells[5] for cells in ledger().values())
    assert printed == dict(counts), f"README.md prints {printed}, the ledger counts {dict(counts)}"


@pytest.mark.parametrize("row", sorted(CHECKS))
def test_ledger_row_matches_its_artifact(row):
    checks = CHECKS[row]()
    bad = [f"{label}: ledger {expected}, artifact {value!r}"
           for label, expected, value in checks if not holds(expected, value)]
    assert not bad, f"{row} no longer matches its artifact:\n  " + "\n  ".join(bad)
    # A literal counts where the row prints values, in the claim and value cells; the artifact cell
    # names fields and selectors. True and False are outcomes of a predicate the check evaluates.
    cells = ledger()[row]
    line = f"{cells[2]} | {cells[4]}"
    absent = [f"{label}: {expected}" for label, expected, _ in checks
              if expected not in ("True", "False") and not in_row(expected, line)]
    assert not absent, f"{row} checks literals its ledger row does not carry:\n  " + "\n  ".join(absent)
