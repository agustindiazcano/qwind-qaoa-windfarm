# Qollab runtime measurements

Our time budget for the live Run: **30 s**. The numbers below are single runs, not averages, so we keep a margin. They do not come from `results/` (those are offline cloud runs); they come from runs the project owner made in the Qollab console with the built-in simulator, and from local runs on the author's machine.

## Qollab Run of the default instance (N = 8 cells, K = 3 turbines, p = 2, seed 0)

| Date | Version of `main.py` | Total time shown by the console | QAOA | Simulated annealing | Notes |
|---|---|---|---|---|---|
| 2026-10-10 | Penalty QAOA default (before PR #29) | 15.8 s | 3.2393 s | 1.0054 s | Table printed once |
| 2026-10-10 | XY mixer + Dicke start default (PR #29) | 25.5 s | 3.3192 s | 1.3239 s | Table printed once |

- The QAOA time itself is almost the same in both runs. The total also includes loading the packages and initializing the Qollab runtime (about 10.8 s before the first output in an earlier run).
- The numbers printed by Qollab differ slightly from local runs of the same seed (for example P(optimal) 0.0621 on Qollab against 0.0631 locally with the XY + Dicke default): different Python, NumPy and SciPy versions. Reproducibility across environments is not claimed.

## Larger instances

| Instance | Where | Result |
|---|---|---|
| N = 14 cells, penalty QAOA, one run | Qollab | 42.8 s (above our 30 s budget for the live Run) |
| N = 10 cells, K = 4, p = 2, XY + Dicke | Local, Python 3.12 | 11 s wall clock |
| N = 12 cells, K = 4, p = 2, XY + Dicke | Local, Python 3.12 | 17 s wall clock (QAOA 10.4 s) |

The local N = 10 and N = 12 times are indicative only; N = 12 has not been run on Qollab. Decision: default N = 8, recommended up to 10 cells, hard limit 12 (`main()` refuses more). Larger instances, including the full 14-turbine Penmanshiel farm, are computed offline (`experiments/`, `results/`).

## Qollab smoke test (2026-10-10, QAOA-like workload with a parameterized circuit, `Estimator` and COBYLA)

| Qubits | Seconds per evaluation |
|---|---|
| 8 | 0.047 |
| 10 | 0.113 |
| 12 | 0.086 |
| 14 | 0.229 |

One machine and one run; see `docs/PROJECT_CONTEXT.md` section 5 for the rest of the runtime facts (Python 3.14.2, Qiskit 2.5.2, no matplotlib, no qiskit_aer).
