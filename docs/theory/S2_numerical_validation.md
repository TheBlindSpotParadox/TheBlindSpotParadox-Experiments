# Stream S2 — numerical validation

Deliverable 3. The statutory guard-rail matrix, the reproduction commands, and the artifact
hashes. Every assertion below is executable; none is a narrative claim.

## 1. Reproduction

```bash
PYTHONHASHSEED=0 python experiments/S2_theory/s2_arl0.py        #  T2.0, T2.3, T2.5(c)
PYTHONHASHSEED=0 python experiments/S2_theory/s2_w_random.py    #  T2.1, T2.2
PYTHONHASHSEED=0 python experiments/S2_theory/s2_eddm.py        #  T2.4   (~4 min, reads traces)

PYTHONHASHSEED=0 python experiments/S2_theory/s2_arl0.py     --check   # self-check, writes nothing
PYTHONHASHSEED=0 python experiments/S2_theory/s2_w_random.py --check
PYTHONHASHSEED=0 python experiments/S2_theory/s2_eddm.py     --check

PYTHONHASHSEED=0 python -m pytest tests/test_S2_theory.py tests/test_S7_consistency.py \
                                  tests/test_manuscript_integrity.py -v
sha256sum -c results/audit_S7/_baseline/artifacts_sha256_pre_ssot.txt
tectonic docs/manuscript/$(cat docs/manuscript/CURRENT)
```

Interpreter and package pins: `docs/ENVIRONMENT.md`. Run from the repository root. No S2 module
draws a random number: the only stochastic-looking object, the Gauss–Hermite quadrature of
`s2_w_random.parametric_bound`, is a deterministic 64-node rule, and the one generator that does
appear (`s2_eddm._certify_against_river`) is local to a self-check, feeds no experiment and writes
no artifact.

## 2. Artifact hashes

Bit-reproducible: re-running all three modules reproduces all ten files byte-for-byte.

```
5ad45baa1c8bd1fef5e9fac1bf8a43235e8a1b72b9b966c0b6bcf4646e5f5da9  s2_arl0_columns.csv
9aa3eb3e0b573caeec315b763d5100defb80dfb793a68b39b9097a825ac5b339  s2_gate_T20.json
8d413c71f29e9a0d7106eafeb1e358361e63b7ecffb2101e241c518e750de970  s2_lambda_starve.csv
18b7599d1650fc4bcd81f01421f40d360e49d507e325e195e5ee8c7987089c21  s2_flooding_retrodiction.json
cfc63353ffa7a2b33bf9de4c44644bb984956e8074582338b834e0eacb3daa27  s2_w_random.csv
96b1ea9f60b516ada07c5cf56cd16f412bd25c79c368819b66d2e37f4cb78953  s2_w_random.json
18a561f488fa77e54e8189fe2dd3b606a2528e5631885b836a0a44e197b45598  s2_eq4_domain.csv
f04a19fcb344dc3e8fcffc046e202853e1f45db5d3944252b9c2ab5cf169d1db  s2_eddm_traces.csv
e078d08a6123be7ee31bbc2790872da622f96d68e182a69defd5d8e13036bfe7  s2_eddm_closed_form.csv
55d72e7cda82d75d045f366628a2777d03a0042701d0992a1e37c713d33fb509  s2_eddm.json
```

All paths relative to `results/S2_theory/tables/`. S2 writes no artifact outside that directory;
`sha256sum -c results/audit_S7/_baseline/artifacts_sha256_pre_ssot.txt` reports 29 OK and 5 FAILED,
and the five failures are exactly the set already declared in
`results/audit_S7/_baseline/authorized_deviations.txt` (verified by set comparison, not by
inspection). **S2 adds no entry to `authorized_deviations.txt`.**

## 3. Statutory guard-rail — degenerate inputs

`tests/test_S2_theory.py`. Each row states the expected behaviour and the reason a naive
expectation would be wrong.

| input | expected | why the opposite would pass on a wrong premise |
|---|---|---|
| `p_0 -> 0` and `p_0 -> 1` in `thm:floor` | floor **vacuous** at both ends, collapsing to `-W delta_P`; maximal at `p_0 = 1/2`; symmetric under `p_0 <-> 1-p_0` | `p_0(1-p_0)` is the DENOMINATOR of the KL upper bound, hence the NUMERATOR of the floor. A test asserting the bound tightens as the base rate falls would pass on an inverted reading of the proof |
| `sigma = 0` | the same degeneracy, not an independent one | on a Bernoulli error stream `sigma^2 = p_0(1-p_0)`, so `sigma = 0` **is** the two endpoints above. Treating it as a separate knob would double-count |
| `lambda = 0` | `ARL_0 = 0`, and `ARL_0` strictly increasing in `lambda` | no threshold buys no false-alarm time |
| `p_true = 0` | Cramér root `= inf`, `ARL_0 = inf` | the reflected statistic never leaves zero; a solver returning a finite root here would be inventing a crossing |
| non-negative null drift (`p_true >= p_pre + delta_P`) | `ValueError` | there is no positive Cramér root and `ARL_0` is undefined; returning the trivial root `theta = 0` would silently produce `ARL_0 = 0/0` |
| `W = 0` | `lambda_starve = s_0`; Eq. (4) returns `0` | an empty window carries no accumulation and no crossing |
| `W = 1` | finite, in `[0, 1]` after the cap; underflows to `0` at `lambda = 50` | one step cannot accumulate 50 units of evidence, and the underflow is the correct reading, not a defect |
| `Delta_e = delta_P` (so `mu = 0`) | `lambda_starve` reduces to the pure fluctuation margin `sqrt(W/2 ln(W/eps))` | the drift term vanishes and nothing else may move |
| `p_1 = p_0` in `s2_eddm` | `f* = nan`, `W_EDDM = inf` | no change, no level crossing; a finite requirement here would fit noise |

## 4. Statutory guard-rail — the specific matrix

| input | assertion |
|---|---|
| `W` at powers of two, `2^0 … 2^11` | `lambda_starve` strictly increasing in `W` at every `mu in {0, 1e-6, 0.09, 0.3168, 0.488}` |
| `Delta_e -> delta_P` from above (`1e-1 … 1e-12`) | `lambda_starve` descends continuously to the pure margin, monotonically, with no sign flip |
| `lambda` near `mu W` (`+/- 1e-12 … 1e-3`) | Eq. (4) is continuous through the vacancy boundary and never exceeds `W`; at `mu W = lambda` it returns exactly `W` |
| `Delta_e >= 0.452` | measured `err_post_mean < e_pre` at **every** magnitude of the top band, so `A = sum(e_t - p_0) < 0` and every bound assuming `A > 0` is **void**, not violated. The floor there is strictly positive, so the comparison `A >= floor` is not evaluable and is declared so |
| chord floor vs `chi^2` floor | the tightened floor dominates `eq:floor` at every `(p_0, Delta_max)` tested; equality only as `Delta_max/p_0 -> 0` |
| `cor:split` scaling | `lambda(alpha)` slope in `ln(1/alpha)` approaches `1/theta*` **from below** and matches it to `1e-4` on the last segment; the `o(1)` is still 0.6 % on the `8 -> 15` segment |
| R4 censoring floor | the capped integrated bound is `>= ` the censoring fraction at every `lambda`, on a synthetic 80/20 split |
| EDDM recursion | the vectorised path agrees with `river.drift.binary.EDDM` on the first alarm across four `(p_0, p_1)` regimes, including no-drift and reverse-drift |

## 5. Two claims corrected during execution

Recorded because both were written before the matrix was run, and the matrix refuted them.

1. **`W_EDDM` does shorten with the drift magnitude.** The first draft asserted that the
   between-group variance term keeps the requirement from falling with `Delta_e`. Measured,
   `f*` is nearly invariant (0.235 to 0.240 over `p_1 in [0.10, 0.70]`), so
   `W_EDDM ~ 0.31 n_0/p_1` and it falls at nearly the `1/Delta_e` rate of a first-passage bound.
   The surviving distinction is the factor `n_0`, which no first-passage bound carries.
2. **R3's vacancy criterion is necessary, not sufficient.** `mu W < lambda` admits 52 of the 240
   measured pairs; only 32 of those give `W exp(-2/W (lambda - mu W)^2) < 1`. The rule was fixed
   on the positive-part criterion and is applied as fixed; the gap is reported rather than used to
   move the rule after the measurement.

## 6. What the guard-rail does not cover

- `s_0` is set to 0 throughout, by the convention `transfer_S1` L62 uses. It is measurable on the
  committed traces and is not measured here.
- The `thm:floor` chain rule is audited for its conditional reading, not re-derived under a
  specific dependence model for the learning classifier.
- `R_EDDM` is withdrawn, so no guard-rail is written for a requirement that does not exist; the
  closed form retains its own degenerate-input tests.
