# Results tables

Generated from results/summary.json and results/per_instance.csv by scripts/make_results_tables.py. Protocol qwind-v1, status final, Python 3.12.15, Qiskit 2.5.2, NumPy 2.4.6, SciPy 1.18.0. Do not edit by hand.

Evaluation budgets are not matched across methods (simulated annealing uses far more objective evaluations than QAOA). Datasets are never averaged together.

## real_penmanshiel_sub10 (3 instances, status final)

### QAOA against the uniform-over-feasible baseline

| variant | p | instances | P(optimal) | uniform P(optimal) | P(feasible) | approx. ratio (feasible) | uniform approx. ratio | beat uniform ratio | beat uniform P(optimal) | optimizer evaluations |
|---|---|---|---|---|---|---|---|---|---|---|
| penalty+x lam=1 | 1 | 3 | 0.004 | 0.015 | 0.289 | 0.475 | 0.483 | 1/3 | 0/3 | 86 |
| penalty+x lam=3 | 1 | 3 | 0.002 | 0.015 | 0.269 | 0.475 | 0.483 | 0/3 | 0/3 | 93 |
| penalty+x lam=10 | 1 | 3 | 0.006 | 0.015 | 0.429 | 0.486 | 0.483 | 3/3 | 0/3 | 114 |
| penalty+x lam=10 ramp | 1 | 3 | 0.006 | 0.015 | 0.441 | 0.482 | 0.483 | 2/3 | 0/3 | 99 |
| xy+dicke | 1 | 3 | 0.020 | 0.015 | 1.000 | 0.570 | 0.483 | 3/3 | 2/3 | 120 |
| xy+dicke ramp | 1 | 3 | 0.016 | 0.015 | 1.000 | 0.517 | 0.483 | 3/3 | 1/3 | 120 |
| penalty+x lam=1 | 2 | 3 | 0.005 | 0.015 | 0.389 | 0.494 | 0.483 | 1/3 | 0/3 | 116 |
| penalty+x lam=3 | 2 | 3 | 0.002 | 0.015 | 0.224 | 0.466 | 0.483 | 0/3 | 0/3 | 120 |
| penalty+x lam=10 | 2 | 3 | 0.005 | 0.015 | 0.422 | 0.485 | 0.483 | 2/3 | 0/3 | 115 |
| penalty+x lam=10 ramp | 2 | 3 | 0.006 | 0.015 | 0.352 | 0.484 | 0.483 | 2/3 | 0/3 | 120 |
| xy+dicke | 2 | 3 | 0.045 | 0.015 | 1.000 | 0.647 | 0.483 | 3/3 | 3/3 | 120 |
| xy+dicke ramp | 2 | 3 | 0.016 | 0.015 | 1.000 | 0.524 | 0.483 | 3/3 | 1/3 | 120 |
| penalty+x lam=1 | 3 | 3 | 0.004 | 0.015 | 0.276 | 0.471 | 0.483 | 0/3 | 0/3 | 120 |
| penalty+x lam=3 | 3 | 3 | 0.006 | 0.015 | 0.311 | 0.462 | 0.483 | 1/3 | 0/3 | 120 |
| penalty+x lam=10 | 3 | 3 | 0.003 | 0.015 | 0.256 | 0.480 | 0.483 | 2/3 | 0/3 | 120 |
| penalty+x lam=10 ramp | 3 | 3 | 0.010 | 0.015 | 0.513 | 0.486 | 0.483 | 3/3 | 0/3 | 120 |
| xy+dicke | 3 | 3 | 0.054 | 0.015 | 1.000 | 0.660 | 0.483 | 3/3 | 3/3 | 120 |
| xy+dicke ramp | 3 | 3 | 0.014 | 0.015 | 1.000 | 0.501 | 0.483 | 3/3 | 1/3 | 120 |

### Evaluation budget per method

| method | mean evaluations | mean energy gap | mean time (s) |
|---|---|---|---|
| exact | 1024 | 0.0000 | 0.038 |
| sa | 5005 | 0.0000 | 0.295 |
| greedy | n/a | 0.0000 | 0.002 |
| qaoa | 115 | 0.0026 | 1.213 |

### Every instance, xy+dicke

| K | N | p | P(optimal) | uniform P(optimal) | approx. ratio (feasible) | uniform approx. ratio | optimizer evaluations |
|---|---|---|---|---|---|---|---|
| 3 | 10 | 1 | 0.043 | 0.033 | 0.522 | 0.496 | 120 |
| 3 | 10 | 2 | 0.110 | 0.033 | 0.642 | 0.496 | 120 |
| 3 | 10 | 3 | 0.118 | 0.033 | 0.651 | 0.496 | 120 |
| 5 | 10 | 1 | 0.003 | 0.004 | 0.606 | 0.518 | 120 |
| 5 | 10 | 2 | 0.006 | 0.004 | 0.682 | 0.518 | 120 |
| 5 | 10 | 3 | 0.009 | 0.004 | 0.696 | 0.518 | 120 |
| 7 | 10 | 1 | 0.015 | 0.008 | 0.581 | 0.435 | 120 |
| 7 | 10 | 2 | 0.018 | 0.008 | 0.616 | 0.435 | 120 |
| 7 | 10 | 3 | 0.035 | 0.008 | 0.633 | 0.435 | 120 |

### Every instance, penalty+x lam=10

| K | N | p | P(optimal) | uniform P(optimal) | approx. ratio (feasible) | uniform approx. ratio | optimizer evaluations |
|---|---|---|---|---|---|---|---|
| 3 | 10 | 1 | 0.013 | 0.033 | 0.496 | 0.496 | 120 |
| 3 | 10 | 2 | 0.011 | 0.033 | 0.502 | 0.496 | 104 |
| 3 | 10 | 3 | 0.006 | 0.033 | 0.499 | 0.496 | 120 |
| 5 | 10 | 1 | 0.002 | 0.004 | 0.519 | 0.518 | 103 |
| 5 | 10 | 2 | 0.002 | 0.004 | 0.518 | 0.518 | 120 |
| 5 | 10 | 3 | 0.000 | 0.004 | 0.502 | 0.518 | 120 |
| 7 | 10 | 1 | 0.004 | 0.008 | 0.443 | 0.435 | 120 |
| 7 | 10 | 2 | 0.003 | 0.008 | 0.436 | 0.435 | 120 |
| 7 | 10 | 3 | 0.004 | 0.008 | 0.440 | 0.435 | 120 |

## synthetic (24 instances, status final)

### QAOA against the uniform-over-feasible baseline

| variant | p | instances | P(optimal) | uniform P(optimal) | P(feasible) | approx. ratio (feasible) | uniform approx. ratio | beat uniform ratio | beat uniform P(optimal) | optimizer evaluations |
|---|---|---|---|---|---|---|---|---|---|---|
| penalty+x lam=1 | 1 | 24 | 0.007 | 0.021 | 0.263 | 0.554 | 0.578 | 12/24 | 0/24 | 84 |
| penalty+x lam=3 | 1 | 24 | 0.006 | 0.021 | 0.294 | 0.585 | 0.578 | 14/24 | 0/24 | 90 |
| penalty+x lam=10 | 1 | 24 | 0.010 | 0.021 | 0.415 | 0.583 | 0.578 | 16/24 | 0/24 | 103 |
| penalty+x lam=10 ramp | 1 | 24 | 0.011 | 0.021 | 0.436 | 0.579 | 0.578 | 17/24 | 0/24 | 111 |
| xy+dicke | 1 | 24 | 0.050 | 0.021 | 1.000 | 0.687 | 0.578 | 24/24 | 22/24 | 118 |
| xy+dicke ramp | 1 | 24 | 0.030 | 0.021 | 1.000 | 0.678 | 0.578 | 24/24 | 18/24 | 120 |
| penalty+x lam=1 | 2 | 24 | 0.012 | 0.021 | 0.379 | 0.591 | 0.578 | 10/24 | 3/24 | 120 |
| penalty+x lam=3 | 2 | 24 | 0.012 | 0.021 | 0.422 | 0.592 | 0.578 | 15/24 | 2/24 | 120 |
| penalty+x lam=10 | 2 | 24 | 0.011 | 0.021 | 0.433 | 0.578 | 0.578 | 12/24 | 0/24 | 118 |
| penalty+x lam=10 ramp | 2 | 24 | 0.012 | 0.021 | 0.372 | 0.574 | 0.578 | 14/24 | 0/24 | 119 |
| xy+dicke | 2 | 24 | 0.065 | 0.021 | 1.000 | 0.705 | 0.578 | 24/24 | 20/24 | 120 |
| xy+dicke ramp | 2 | 24 | 0.038 | 0.021 | 1.000 | 0.721 | 0.578 | 24/24 | 19/24 | 120 |
| penalty+x lam=1 | 3 | 24 | 0.014 | 0.021 | 0.352 | 0.575 | 0.578 | 13/24 | 4/24 | 120 |
| penalty+x lam=3 | 3 | 24 | 0.010 | 0.021 | 0.424 | 0.573 | 0.578 | 13/24 | 1/24 | 120 |
| penalty+x lam=10 | 3 | 24 | 0.010 | 0.021 | 0.386 | 0.562 | 0.578 | 9/24 | 0/24 | 120 |
| penalty+x lam=10 ramp | 3 | 24 | 0.011 | 0.021 | 0.372 | 0.570 | 0.578 | 10/24 | 0/24 | 120 |
| xy+dicke | 3 | 24 | 0.072 | 0.021 | 1.000 | 0.731 | 0.578 | 24/24 | 20/24 | 120 |
| xy+dicke ramp | 3 | 24 | 0.046 | 0.021 | 1.000 | 0.726 | 0.578 | 24/24 | 22/24 | 120 |

### Evaluation budget per method

| method | mean evaluations | mean energy gap | mean time (s) |
|---|---|---|---|
| exact | 1360 | 0.0000 | 0.129 |
| sa | 5005 | 0.0000 | 0.565 |
| greedy | n/a | 0.0129 | 0.005 |
| qaoa | 115 | 0.0132 | 2.365 |
