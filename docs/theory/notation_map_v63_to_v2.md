# Notation map — v63 to v2

## Notations

| v63              | v2                     | Status              | Note                                                          |
| ---------------- | ---------------------- | ------------------- | ------------------------------------------------------------- |
| `tau_ARF`        | `tau_swap^(1/M)`       | renamed             | first swap; now a lower bound on `W`, not the adaptation time |
| —                | `tau_swap^(q)`         | new                 | fraction-`q` replacement time                                 |
| —                | `tau_err(rho)`         | new                 | error return into tolerance `rho`                             |
| —                | `tau_erase`            | new                 | `tau_err(delta_P)`; governs signal erasure                    |
| —                | `W`                    | new                 | `tau_erase - tau*`, exploitable transient                     |
| —                | `kappa`                | new                 | dilation ratio `W / (tau_swap^(1/M) - tau*)`, measured        |
| `lambda_limit`   | `A`                    | generalised         | rectangular case of the proof budget                          |
| —                | `R(D, eps, alpha)`     | new                 | proof requirement, implementation-free                        |
| `lambda`         | `lambda(alpha)`        | reparameterised     | threshold expressed through the false-alarm level             |
| `c_int`, `c_ext` | —                      | removed from theory | retained as experimental settings only                        |
| `tau_det^*`      | —                      | removed             | nominal accumulation time; replaced by the random `tau_det`   |
| `Delta e`        | `Delta_e`, `Delta_max` | split               | nominal jump vs. realised maximum excess over `W`             |
| —                | `alpha`                | new                 | windowed false-alarm level                                    |
| —                | `eps`                  | new                 | miss level                                                    |
| —                | `theta*`               | new                 | Cramer root of the CUSUM increment                            |

## v63 statements

| Object                       | v63 label                            | Status   | Disposition                                                                 |
| ---------------------------- | ------------------------------------ | -------- | --------------------------------------------------------------------------- |
| CUSUM recursion              | `eq:cusum`                           | kept     | unchanged                                                                   |
| Blind spot definition        | `def:blindspot` (v63)                | modified | now `A < R`, not `tau_ARF < tau_det`                                        |
| Hydra identity               | `eq:hydra`                           | modified | defines `tau_swap^(1/M)`, no longer the adaptation time                     |
| Starvation                   | `prop:starvation` (Prop. 3)          | modified | stream S2; fluctuation restored, `S_0` in statement, finite horizon         |
| Sufficiency remark           | `rem:sufficient`                     | void     | absorbed into the corrected statement                                       |
| Detector-agnosticity         | `rem:agnostic`                       | modified | becomes `cor:split`, derived rather than asserted                           |
| Starvation boundary          | `prop:starvation_boundary` (Prop. 9) | modified | stream S3; the `=` of `eq:pmiss` becomes the two-sided distribution-free envelope `F <= P_miss <= min(1, M F)`, the independence form is kept as the conditional case with its hypothesis measured to fail (D1), and `tau_det*` is replaced by the competing-risks race |
| Critical ensemble size       | `cor:mcrit`                          | withdrawn | stream S3, rule D5(b). The quantity `M_crit` is withdrawn: the surviving envelope saturates at `M F >= 1` and is constant in `M` there, so it cannot be inverted; the `F = F_HAT` plug-in is refuted on 10 of 80 measured cells. The LABEL is retained, carrying the negative statement, because `.tex` L463 references it from outside the S3 write perimeter |
| Decoupling Principle         | `def:decoupling` (Def. 11)           | void     | replaced by `A < R`; the `c_ext < c_int` clause has no cross-family meaning |
| Operational calibration (ii) | `def:decoupling` (ii)                | kept     | survives as the measurement procedure for `A`, restated on `tau_erase`      |
| Exponent revision            | `rem:exponent`                       | kept     | now supports `prop:invariance`                                              |
| Background swaps             | `rem:bgswap`                         | kept     | reinterpreted: sets a floor on `W` in the weak-signal band                  |
| Flooding                     | `rem:flooding`                       | modified | stream S2; restated through `ARL_0`                                         |
| Clock parameter              | `rem:clock`                          | kept     | experimental setting only                                                   |

## New bibliography entries required

- Lai, 1998, Information bounds and quick detection of parameter changes in stochastic systems
- Siegmund, 1985, Sequential Analysis: Tests and Confidence Intervals
- Kingman, 1970, Inequalities in the theory of queues
- Tsybakov, 2009, Introduction to Nonparametric Estimation (change-of-measure lemma)