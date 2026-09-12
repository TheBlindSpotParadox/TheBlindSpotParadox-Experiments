# Stream S2 — decision rules, fixed before measurement

Committed before any S2 script is run and before any S2 output is read. Every rule below carries
its numeric threshold and its verdict on **both** sides, so that no outcome of the stream can be
arbitrated after the fact.

The discipline exists because of a near miss in S6: `q05(S_max)` sits at `15.219` against a
threshold of `15.00` at five grid points of
`results/S6_synchronized_traces/tables/cusum_delta001_quantiles.csv`. A rule read off a point
estimate would have published a knife edge. Rules R2 and R4 below are written so that the point
estimate is never the decision variable.

Stream branch `stream-s2`, parent `638ce54`.

---

## R1 — reproduction tolerance for `transfer_S1`'s third column

`docs/theory/transfer_S1.md` L25–31 carries `theta*`, the closed-form approximation and `ARL_0` at
three thresholds for three `(delta_P, p_0)` settings. No script in this repository produces them;
S2 reproduces them independently with a committed script.

**R1(a) — the tabulated column.** With `theta*_S2` the Cramér root computed by
`experiments/S2_theory/s2_arl0.py`:

| condition | verdict |
|---|---|
| `\|theta*_S2 - 0.6813\| / 0.6813 <= 1e-3` **and** `ARL_0` agrees to one significant figure at each of `lambda in {8, 25, 50}` | column **REPRODUCED**; it is carried forward as an input |
| either test fails | column **UNREPRODUCED**; the three `p_0 = 0.024` entries are **withdrawn** from `transfer_S1.md` and replaced by the S2 values, with the discrepancy stated |

The same pair of tests is applied to the `0.005 / p_0 = 0.05` column, which `transfer_S1` L23
declares reproduces exactly. That column is the **certification** of the solver: if it fails, no
other column is reported at all and the stream halts on an infrastructure fault, not on a finding.

**R1(b) — the three `NOT RECOMPUTED` lines (L61–63).** Each is recomputed from its own stated
inputs. A line that does not return its stated value under those inputs is reported as
**UNREPRODUCED** with both numbers side by side; it is never silently replaced by the S2 value and
never absorbed into a tolerance. No threshold is attached to R1(b) beyond exact arithmetic
agreement at the printed precision, because each line is a single deterministic evaluation.

---

## R2 — the `lambda_FA` gate (T2.0)

Two readings, **both reported**, one of them carrying the verdict.

- **Empirical.** `lambda_FA = R4_PHT_LAMBDA = 15`, annotated in the manuscript preamble as
  *ProteuS pre-drift calibration*. It is a measured property of a calibration run, invariant by
  construction: no recomputation of `ARL_0` mechanically displaces it.
- **Theoretical.** `lambda_FA^ARL := ARL_0^{-1}(target)` evaluated at `p_0 = 0.024`,
  `delta_P = CUSUM_DELTA_P = 0.01`, where `target := ARL_0(lambda = 15)` at `p_0 = 0.05`,
  `delta_P = 0.01` — R4's implied false-alarm budget, recovered at the base rate S1 assumed.

Decision variable: the reading declared to carry the verdict, compared against the **bootstrap
interval** of `lambda_op` on the `[0.20, 0.40]` envelope,
`[19.876, 22.398]` (`results/S6_synchronized_traces/tables/envelope_stats.json`,
`lambda_op_bootstrap./0.20_0.40`, 10 000 replicates, seed 12345).

| condition | verdict |
|---|---|
| reading `> 22.398` (interval upper bound) | **EMPTY** — the admissible set `{lambda >= lambda_FA} ∩ {lambda <= lambda_op}` is empty on `[0.20, 0.40]`; `res:tension` simplifies and the published result changes |
| reading `< 19.876` (interval lower bound) | **NON-EMPTY** — `res:tension` and `rem:envelope` hold unchanged |
| reading in `[19.876, 22.398]` | **UNDECIDED** |

`UNDECIDED` is a terminal, publishable verdict. It is **never** a reason to resample, to narrow the
interval, or to re-read the point estimate `21.9283`. The point estimate is never the decision
variable.

Both readings are printed with the verdict, together with a statement of which one carries it and
why.

---

## R3 — vacancy of Eq. (4) (`eq:markov_bound` / `prop:starvation`)

The bound `P(S* >= lambda) <= W exp(-2/W (lambda - s_0 - mu W)_+^2)` is declared **VACANT** at a
given `(W, lambda)` when `mu W >= lambda`: the positive part is zero, the exponential is `1`, and
`W e^0 = W >= 1` bounds a probability by a number at least one.

Tabulated at `delta_P = 0.01`, `s_0 = 0`, for every pair in
`lambda in {8, 15, 25, 50}` × `W in {tau_swap^(1/M), tau_erase, tau_err(0.10)}`, each `W` taken
per magnitude from `results/S6_synchronized_traces/data/runs.parquet`, arm `full`.

**Recommendation on the removal branch, fixed here and not after the table is read:**

| condition on the vacancy table | recommendation carried into `prop3_v2.tex` |
|---|---|
| at least one `(W, lambda)` pair on the measured grid is non-vacant | **RETAIN** Eq. (4), restated with the explicit domain `{(W, lambda) : mu W < lambda}` and with the domain table printed; the proposition is demoted from a claim about the operating point to a scope statement about where a fluctuation argument still says anything |
| every pair on the measured grid is vacant | **WITHDRAW** Eq. (4) from the manuscript, keeping `prop:certificate` as the load-bearing statement |

Both sides of the arbitration are written out in `prop3_v2.tex` regardless of which branch fires.

---

## R4 — the `W`-integrated bound

The deterministic-`W` bound and the `W`-integrated bound
`E_W[ W exp(-2/W (lambda - s_0 - mu W)_+^2) ]` are reported side by side, per
`lambda in {8, 15, 25, 50}`.

Right censoring is handled explicitly, never dropped. A censored run contributes exactly `1` to the
integrand, so the integrated bound is bounded below by the censoring fraction alone. **The
censoring fraction is read from the artifact and recorded before the integral is computed**, on the
arm actually used — not taken from `S6_causal_evidence.md` §2, whose `8.2 %` is the AFT's
complete-case subset (`n = 1974`), not the 2 000-run arm.

| condition | verdict |
|---|---|
| integrated bound `>= 1` at a given `lambda` | bound **VACANT** at that `lambda`; reported as a result about the bound, never as a repair of Eq. (4) |
| integrated bound `< 1` | bound **INFORMATIVE** at that `lambda`; the gap to the deterministic-`W` bound is reported as a factor |

Two estimators are reported and bracket the answer: the plug-in empirical integral treating
censored runs at their censoring time (lower), and the parametric log-normal AFT integral
extrapolating past the horizon (upper). The AFT is the one already committed in
`experiments/S6_synchronized_traces/s6_predictive_power.py`; no new dependency is introduced.

---

## R5 — `R_EDDM`

**Withdrawal is the default outcome.** `R_EDDM` survives only if a closed form of the
running-maximum-with-reset dynamics reproduces the measured collapse.

| condition | verdict |
|---|---|
| a closed form predicts **no detection** where the current normal approximation predicts `W = 155`, agreeing with the measured `F1 = 0.00` at `c_int = 1` on **sign and order of magnitude** | `R_EDDM` **RETAINED**, stated with its condition |
| no such closed form is produced, or agreement requires a fitted constant | `R_EDDM` **WITHDRAWN** from the instantiation of `R` |

Agreement is declared on sign and order of magnitude only. A constant fitted to the measurement is
not agreement and does not retain the requirement.

Withdrawing the **requirement** `R_EDDM` does not withdraw the **empirical** EDDM result, which
stands on its own measurement. The text separates the two explicitly in either branch.

---

## R6 — proof obligations

Each of `thm:floor`, `cor:split`, `prop:invariance` is marked with exactly one of:

| mark | meaning |
|---|---|
| `PROVED` | a complete proof is delivered, under the hypotheses as stated |
| `PROVED UNDER STATED CONDITION` | a complete proof is delivered under a condition that is named in the statement and whose measured status is reported |
| `NOT PRODUCED` | no proof was produced |

`NOT PRODUCED` is a legitimate terminal state. It is declared explicitly in
`docs/theory/transfer_S2.md` and in `prop3_v2.tex`, never silently omitted, and never replaced by a
proof sketch presented as a proof.
