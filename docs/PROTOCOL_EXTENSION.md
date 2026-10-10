# Extension of the experiments (written before running)

This document fixes, **before any of these runs exist**, a second batch of experiments. The git history of this file is the record of what was decided in advance. The first batch (protocol `qwind-v1`, six datasets) is already in `results/` and is not modified.

## Why

The first batch left two open questions:

1. **Does the constraint-preserving QAOA separate from random feasible sampling at larger N?** For N up to 12, random feasible sampling with the same 1000 samples finds the optimum with probability 0.95 to 1.00, so matching simulated annealing there does not show anything about QAOA. Random sampling gets much worse as N grows (0.35 at N = 14), so larger N is where the comparison becomes informative.
2. **Penmanshiel (N = 14) has only 3 instances (K = 5, 7, 9)**, too few for any conclusion.

## What is run (identical settings, more and larger instances)

The QAOA and baseline settings are exactly those of `qwind-v1` and are **not changed**: depths p = 1, 2, 3; 2 restarts; 60 optimizer evaluations per restart; 1000 shots; penalty weights 1, 3 and 10 times max|h| plus the ramp variant; XY + Dicke and its ramp variant; seeds fixed per instance; simulated annealing with 5 reads; reference QUBO with penalty 10 times max|h|. A test checks these values.

| Dataset | Instances | Notes |
|---|---|---|
| `synthetic_n16` | N = 16, K = 5 and 8, synthetic roses A, B, C: 6 instances (seeds 100 to 105) | Synthetic grid, as in `synthetic` |
| `synthetic_n18` | N = 18, K = 6 and 9, roses A, B, C: 6 instances (seeds 110 to 115) | Same |
| `real_penmanshiel_allk` | All 14 real turbine positions, K = 3, 4, ..., 11: 9 instances | Measured 2019 rose; includes the K = 5, 7, 9 of `real_penmanshiel` |

The K values are about N/3 and N/2 for the synthetic sets and every K from 3 to 11 for Penmanshiel. No other values were considered.

## Questions asked in advance (no answer is expected or required)

- Q1. At N = 16 and 18, how often does the best of the 1000 XY + Dicke samples equal the exact optimum, compared with the probability that 1000 random feasible samples contain it (`random_p_hit`)?
- Q2. Does XY + Dicke still beat the uniform-over-feasible baseline on the approximation ratio and on P(optimal)?
- Q3. Does the penalty formulation still fail to beat the uniform baseline consistently?
- Q4. On Penmanshiel with nine values of K, how often does XY + Dicke find the optimum, and how does the gap to simulated annealing behave?

## Rules for this batch

- All results of these datasets are published, whatever they show: better, equal or worse than the first batch. They are reported next to it and never replace it.
- No QAOA setting is changed after seeing results. In particular **60 evaluations may be too few for N = 16 or 18**; that is a limitation to report, not something to tune afterwards.
- No instance is excluded or added after seeing results. An instance that fails or times out is reported as missing.
- Datasets are never averaged together, and the larger synthetic sets are not merged with `synthetic`.
- Few-instance datasets are reported instance by instance.
- Nothing is claimed beyond what the numbers show. No quantum advantage is claimed.

## Cost estimate (an extrapolation, not a measurement) and the rule if it is wrong

At N = 14 the measured single-run times of the full protocol were 7.7 to 20 s for the penalty variants and 31 to 41 s for XY + Dicke (6 to 7 minutes per instance for all variants and depths). The state vector grows 4 times for every 2 more qubits, so the extrapolation is about 26 minutes per instance at N = 16 and about 100 minutes at N = 18, uncertain by a factor of about 2. With 4 worker processes: `synthetic_n16` about 40 minutes, `synthetic_n18` about 2.6 hours, `real_penmanshiel_allk` about 20 minutes. Each dataset is its own job in GitHub Actions (limit 6 hours).

A quick probe (one instance, p = 1, reduced settings) is run first. **If the probe projects more than 5 hours for `synthetic_n18`, that dataset is dropped** (the QAOA settings are not reduced, to keep the batches comparable) and the decision is recorded here.
