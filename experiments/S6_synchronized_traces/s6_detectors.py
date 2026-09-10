"""External detectors of stream S6, behind one interface.

Two problems this file closes.

1. `StrictCUSUM` was defined inside `exp_R2_instrumented_blind_spot.py` with `delta=0.01` hard-coded
   at the call site, while `config.experiment_ssot.DELTA_P = 0.005` is the registry tolerance and R1
   uses it. S6 has ONE implementation, defaulting to `DELTA_P`; R2's 0.01 stays reachable as
   `R2_CUSUM_DELTA` for anyone reproducing that figure.

2. PHT, ADWIN and KSWIN each expose a different surface, so every experiment re-wrote the same glue.
   Each wrapper here exposes `.update(x)`, `.drift_detected`, `.statistic()`, `.threshold` and
   `.alarm_sense`.

`statistic()` returns the detector's OWN test quantity, not a rescaled one, and `alarm_sense` says
how it is compared: "above" means the alarm fires when the statistic exceeds the threshold, "below"
when it falls under it. KSWIN is the one detector whose sense is inverted (a p-value against alpha);
that is stated rather than hidden behind a transform, because a monotone recoding of a p-value into
an "evidence" scale is an editorial act, not a measurement. ADWIN publishes no scalar test quantity
at all -- its cut is decided over the bucket structure -- so its `statistic()` returns the window
mean `estimation` and `threshold` is None. That is a documented gap, not an equivalence.
"""
import sys
from pathlib import Path

import numpy as np
from river import drift

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))
from config import experiment_ssot as ssot  # noqa: E402

DELTA_P = ssot.DELTA_P
DEMO_CUSUM_LAMBDA = ssot.R2_LAMBDAS[2]     # 8.0, R2 scenario C
DEMO_PHT_LAMBDA = ssot.R3_PHT_LAMBDA       # 25.0, R3


class StrictCUSUM:
    """One-sided CUSUM on a prequential error stream, reflected at zero.

    S_t = max(0, S_{t-1} + (x_t - p_pre) - delta); alarm when S_t >= threshold. This is the same
    recursion as `s6_defs.accumulations`'s reflected branch, which is why `A_refl` and this
    statistic coincide when both are fed the same p_pre and delta."""

    alarm_sense = "above"

    def __init__(self, p_pre, threshold, delta=DELTA_P):
        self.p_pre = float(p_pre)
        self.delta = float(delta)
        self.threshold = float(threshold)
        self.S = 0.0
        self.drift_detected = False

    def update(self, x):
        self.S = max(0.0, self.S + (float(x) - self.p_pre) - self.delta)
        if self.S >= self.threshold:
            self.drift_detected = True
        return self

    def statistic(self):
        return self.S


class _Wrapped:
    """Common shell: delegate update/drift_detected to a River detector."""

    def __init__(self, detector):
        self.detector = detector

    def update(self, x):
        self.detector.update(float(x))
        return self

    @property
    def drift_detected(self):
        return self.detector.drift_detected


class PHT(_Wrapped):
    """PageHinkley. statistic() is River's own test quantity under mode='both':
    max(sum_increase - min_increase, max_decrease - sum_decrease), compared to `threshold`."""

    alarm_sense = "above"

    def __init__(self, threshold, delta=DELTA_P, **kwargs):
        super().__init__(drift.PageHinkley(threshold=threshold, delta=delta, **kwargs))
        self.threshold = float(threshold)

    def statistic(self):
        d = self.detector
        if d._min_increase == float("inf"):
            return 0.0
        return max(d._sum_increase - d._min_increase, d._max_decrease - d._sum_decrease)


class ADWINDetector(_Wrapped):
    """ADWIN. No scalar test quantity is published: the cut is decided over the bucket structure.
    statistic() returns the window mean `estimation`; `threshold` is None by construction, and
    `width` / `variance` are exposed for the trace."""

    alarm_sense = None
    threshold = None

    def __init__(self, delta=None, clock=None, **kwargs):
        if delta is not None:
            kwargs["delta"] = delta
        if clock is not None:
            kwargs["clock"] = clock
        super().__init__(drift.ADWIN(**kwargs))

    def statistic(self):
        return self.detector.estimation

    @property
    def width(self):
        return self.detector.width

    @property
    def variance(self):
        return self.detector.variance


class KSWINDetector(_Wrapped):
    """KSWIN. statistic() is the p-value River stores; the alarm fires when it falls at or under
    alpha, hence alarm_sense = "below". This is the only wrapper whose sense is inverted."""

    alarm_sense = "below"

    def __init__(self, alpha, seed=None, **kwargs):
        super().__init__(drift.KSWIN(alpha=alpha, seed=seed, **kwargs))
        self.threshold = float(alpha)

    def statistic(self):
        return self.detector.p_value


def demo():
    """Self-check: the reflection floor, the alarm senses, and CUSUM == A_refl on one stream."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from s6_defs import accumulations

    err = np.concatenate([np.zeros(200), np.ones(40), np.zeros(200)])
    cus = StrictCUSUM(p_pre=0.0, threshold=DEMO_CUSUM_LAMBDA)
    stats = []
    for x in err:
        stats.append(cus.update(x).statistic())
    assert min(stats) >= 0.0, "CUSUM is not reflected at zero"
    assert cus.drift_detected, "alarm never fired on a 40-step unit excursion"

    _, a_refl = accumulations(err, e_pre=0.0, delta=DELTA_P)
    assert np.allclose(stats, a_refl), "StrictCUSUM and A_refl disagree on the same input"
    assert cus.delta == DELTA_P, "StrictCUSUM default is not the registry tolerance"

    pht = PHT(threshold=DEMO_PHT_LAMBDA)
    assert pht.statistic() == 0.0 and pht.alarm_sense == "above"
    ad = ADWINDetector(clock=ssot.C_INT)
    ks = KSWINDetector(alpha=0.005, seed=1, window_size=100, stat_size=30)
    pht_peak, pht_fired, ks_min = 0.0, False, 1.0
    for x in err:
        pht.update(x), ad.update(x), ks.update(x)
        pht_peak = max(pht_peak, pht.statistic())
        pht_fired |= pht.drift_detected
        ks_min = min(ks_min, ks.statistic())
    # River latches drift_detected per update, so the alarm is read on the stream, not at the end;
    # both PageHinkley branches collapse back to 0 once the excursion is absorbed into its mean.
    assert pht_peak > pht.threshold and pht_fired, (pht_peak, pht_fired)
    assert pht.statistic() == 0.0, pht.statistic()
    assert ad.threshold is None and ad.alarm_sense is None and ad.width > 0
    assert ks.alarm_sense == "below" and 0.0 <= ks_min <= 1.0
    print("s6_detectors demo: OK")


if __name__ == "__main__":
    demo()
