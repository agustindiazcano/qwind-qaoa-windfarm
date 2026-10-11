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

## Probe result and decision (recorded before the full runs)

A quick probe in GitHub Actions (run 38096248863; one instance per dataset, p = 1, 20 evaluations, one restart, 200 shots) measured the time of one QAOA run per variant:

| N | penalty variants (each) | XY + Dicke (each) |
|---|---|---|
| 14 | 0.4 s | 4.3 s |
| 16 | 2.3 s | 76 s |
| 18 | not finished: one instance was still running after more than 24 minutes when the probe was cancelled | |

XY + Dicke grows about 17 times from N = 14 to N = 16, much faster than the 4 times expected from the size of the state vector. Projected to the full protocol (6 times more evaluations, and p = 1, 2, 3), one N = 16 instance takes about 100 minutes and one N = 18 instance is far beyond any reasonable budget.

Decision, following the rule above:
- **`synthetic_n18` is dropped and not run.** Its instance definition stays in the code only so that this decision is reproducible.
- `synthetic_n16` (about 100 minutes per instance, six instances, run with 6 worker processes) and `real_penmanshiel_allk` (about 6 to 7 minutes per instance, nine instances) are run with the unchanged `qwind-v1` settings.
- The QAOA settings are not reduced.

## Outcome of `synthetic_n16` (recorded after the run)

`real_penmanshiel_allk` finished (28 minutes, 9 instances) and is reported in the README. **`synthetic_n16` did not finish**: the GitHub Actions job (run 38097697100, 6 instances, 6 worker processes on a 4-core runner) reached its 5-hour limit and was cancelled at 5 h 0 min, with no results saved. The extrapolation of about 100 minutes per instance (about 2.5 hours in total) was too optimistic, most likely because 6 processes shared 4 cores.

Following the rules of this note, an instance that fails or times out is reported as missing: **no N = 16 result is reported and none is claimed.** The QAOA settings were not reduced. Re-running it would need the instances split across several jobs and is left out of the submission.
