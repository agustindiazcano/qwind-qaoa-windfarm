# Results tables

Generated from results/summary.json and results/per_instance.csv by scripts/make_results_tables.py. Protocol qwind-v1, status final, Python 3.12.15, Qiskit 2.5.2, NumPy 2.4.6, SciPy 1.18.0. Do not edit by hand.

Evaluation budgets are not matched across methods (simulated annealing uses far more objective evaluations than QAOA). Datasets are never averaged together.

## real_bahia_blanca (8 instances, status final)

### QAOA against the uniform-over-feasible baseline

| variant | p | instances | P(optimal) | uniform P(optimal) | P(feasible) | approx. ratio (feasible) | uniform approx. ratio | beat uniform ratio | beat uniform P(optimal) | optimizer evaluations |
|---|---|---|---|---|---|---|---|---|---|---|
| penalty+x lam=1 | 1 | 8 | 0.009 | 0.021 | 0.291 | 0.479 | 0.485 | 3/8 | 0/8 | 85 |
| penalty+x lam=3 | 1 | 8 | 0.004 | 0.021 | 0.220 | 0.486 | 0.485 | 5/8 | 0/8 | 81 |
| penalty+x lam=10 | 1 | 8 | 0.010 | 0.021 | 0.414 | 0.484 | 0.485 | 5/8 | 0/8 | 109 |
| penalty+x lam=10 ramp | 1 | 8 | 0.011 | 0.021 | 0.435 | 0.485 | 0.485 | 6/8 | 0/8 | 109 |
| xy+dicke | 1 | 8 | 0.035 | 0.021 | 1.000 | 0.587 | 0.485 | 8/8 | 8/8 | 116 |
| xy+dicke ramp | 1 | 8 | 0.025 | 0.021 | 1.000 | 0.535 | 0.485 | 8/8 | 4/8 | 120 |
| penalty+x lam=1 | 2 | 8 | 0.011 | 0.021 | 0.319 | 0.505 | 0.485 | 6/8 | 1/8 | 119 |
| penalty+x lam=3 | 2 | 8 | 0.012 | 0.021 | 0.494 | 0.484 | 0.485 | 2/8 | 0/8 | 120 |
| penalty+x lam=10 | 2 | 8 | 0.015 | 0.021 | 0.522 | 0.477 | 0.485 | 1/8 | 0/8 | 115 |
| penalty+x lam=10 ramp | 2 | 8 | 0.012 | 0.021 | 0.414 | 0.484 | 0.485 | 5/8 | 0/8 | 118 |
| xy+dicke | 2 | 8 | 0.044 | 0.021 | 1.000 | 0.671 | 0.485 | 8/8 | 7/8 | 120 |
| xy+dicke ramp | 2 | 8 | 0.014 | 0.021 | 1.000 | 0.563 | 0.485 | 8/8 | 2/8 | 120 |
| penalty+x lam=1 | 3 | 8 | 0.016 | 0.021 | 0.443 | 0.502 | 0.485 | 7/8 | 1/8 | 120 |
| penalty+x lam=3 | 3 | 8 | 0.012 | 0.021 | 0.529 | 0.480 | 0.485 | 4/8 | 0/8 | 120 |
| penalty+x lam=10 | 3 | 8 | 0.009 | 0.021 | 0.349 | 0.496 | 0.485 | 3/8 | 0/8 | 120 |
| penalty+x lam=10 ramp | 3 | 8 | 0.008 | 0.021 | 0.372 | 0.492 | 0.485 | 7/8 | 0/8 | 120 |
| xy+dicke | 3 | 8 | 0.065 | 0.021 | 1.000 | 0.685 | 0.485 | 8/8 | 8/8 | 120 |
| xy+dicke ramp | 3 | 8 | 0.026 | 0.021 | 1.000 | 0.546 | 0.485 | 8/8 | 6/8 | 120 |

### Evaluation budget per method

| method | mean evaluations | mean energy gap | mean time (s) |
|---|---|---|---|
| exact | 1360 | 0.0000 | 0.062 |
| sa | 5005 | 0.0000 | 0.221 |
| greedy | n/a | 0.0000 | 0.002 |
| qaoa | 114 | 0.0064 | 0.990 |

## real_chubut (8 instances, status final)

### QAOA against the uniform-over-feasible baseline

| variant | p | instances | P(optimal) | uniform P(optimal) | P(feasible) | approx. ratio (feasible) | uniform approx. ratio | beat uniform ratio | beat uniform P(optimal) | optimizer evaluations |
|---|---|---|---|---|---|---|---|---|---|---|
| penalty+x lam=1 | 1 | 8 | 0.009 | 0.021 | 0.291 | 0.525 | 0.527 | 5/8 | 0/8 | 87 |
| penalty+x lam=3 | 1 | 8 | 0.006 | 0.021 | 0.263 | 0.534 | 0.527 | 6/8 | 0/8 | 84 |
| penalty+x lam=10 | 1 | 8 | 0.010 | 0.021 | 0.395 | 0.530 | 0.527 | 5/8 | 0/8 | 106 |
| penalty+x lam=10 ramp | 1 | 8 | 0.011 | 0.021 | 0.447 | 0.527 | 0.527 | 5/8 | 0/8 | 106 |
| xy+dicke | 1 | 8 | 0.054 | 0.021 | 1.000 | 0.678 | 0.527 | 8/8 | 8/8 | 120 |
| xy+dicke ramp | 1 | 8 | 0.033 | 0.021 | 1.000 | 0.622 | 0.527 | 8/8 | 7/8 | 120 |
| penalty+x lam=1 | 2 | 8 | 0.012 | 0.021 | 0.419 | 0.566 | 0.527 | 7/8 | 1/8 | 120 |
| penalty+x lam=3 | 2 | 8 | 0.012 | 0.021 | 0.418 | 0.514 | 0.527 | 2/8 | 0/8 | 120 |
| penalty+x lam=10 | 2 | 8 | 0.010 | 0.021 | 0.434 | 0.530 | 0.527 | 2/8 | 0/8 | 113 |
| penalty+x lam=10 ramp | 2 | 8 | 0.013 | 0.021 | 0.434 | 0.529 | 0.527 | 6/8 | 0/8 | 117 |
| xy+dicke | 2 | 8 | 0.088 | 0.021 | 1.000 | 0.720 | 0.527 | 8/8 | 8/8 | 120 |
| xy+dicke ramp | 2 | 8 | 0.051 | 0.021 | 1.000 | 0.640 | 0.527 | 8/8 | 8/8 | 120 |
| penalty+x lam=1 | 3 | 8 | 0.016 | 0.021 | 0.496 | 0.530 | 0.527 | 4/8 | 0/8 | 120 |
| penalty+x lam=3 | 3 | 8 | 0.010 | 0.021 | 0.391 | 0.527 | 0.527 | 3/8 | 0/8 | 120 |
| penalty+x lam=10 | 3 | 8 | 0.011 | 0.021 | 0.431 | 0.521 | 0.527 | 3/8 | 0/8 | 120 |
| penalty+x lam=10 ramp | 3 | 8 | 0.005 | 0.021 | 0.317 | 0.532 | 0.527 | 7/8 | 0/8 | 119 |
| xy+dicke | 3 | 8 | 0.092 | 0.021 | 1.000 | 0.713 | 0.527 | 8/8 | 7/8 | 120 |
| xy+dicke ramp | 3 | 8 | 0.032 | 0.021 | 1.000 | 0.653 | 0.527 | 8/8 | 6/8 | 120 |

### Evaluation budget per method

| method | mean evaluations | mean energy gap | mean time (s) |
|---|---|---|---|
| exact | 1360 | 0.0000 | 0.132 |
| sa | 5005 | 0.0000 | 0.549 |
| greedy | n/a | 0.0000 | 0.006 |
| qaoa | 114 | 0.0114 | 2.319 |

## real_kelmarsh (3 instances, status final)

### QAOA against the uniform-over-feasible baseline

| variant | p | instances | P(optimal) | uniform P(optimal) | P(feasible) | approx. ratio (feasible) | uniform approx. ratio | beat uniform ratio | beat uniform P(optimal) | optimizer evaluations |
|---|---|---|---|---|---|---|---|---|---|---|
| penalty+x lam=1 | 1 | 3 | 0.036 | 0.106 | 0.354 | 0.594 | 0.595 | 2/3 | 0/3 | 102 |
| penalty+x lam=3 | 1 | 3 | 0.055 | 0.106 | 0.519 | 0.599 | 0.595 | 3/3 | 0/3 | 98 |
| penalty+x lam=10 | 1 | 3 | 0.049 | 0.106 | 0.493 | 0.593 | 0.595 | 2/3 | 0/3 | 120 |
| penalty+x lam=10 ramp | 1 | 3 | 0.053 | 0.106 | 0.533 | 0.598 | 0.595 | 3/3 | 0/3 | 120 |
| xy+dicke | 1 | 3 | 0.152 | 0.106 | 1.000 | 0.692 | 0.595 | 3/3 | 2/3 | 120 |
| xy+dicke ramp | 1 | 3 | 0.089 | 0.106 | 1.000 | 0.642 | 0.595 | 3/3 | 1/3 | 120 |
| penalty+x lam=1 | 2 | 3 | 0.025 | 0.106 | 0.321 | 0.581 | 0.595 | 1/3 | 0/3 | 120 |
| penalty+x lam=3 | 2 | 3 | 0.056 | 0.106 | 0.564 | 0.599 | 0.595 | 2/3 | 0/3 | 120 |
| penalty+x lam=10 | 2 | 3 | 0.056 | 0.106 | 0.541 | 0.597 | 0.595 | 2/3 | 0/3 | 120 |
| penalty+x lam=10 ramp | 2 | 3 | 0.062 | 0.106 | 0.599 | 0.602 | 0.595 | 3/3 | 0/3 | 120 |
| xy+dicke | 2 | 3 | 0.146 | 0.106 | 1.000 | 0.692 | 0.595 | 3/3 | 3/3 | 120 |
| xy+dicke ramp | 2 | 3 | 0.151 | 0.106 | 1.000 | 0.667 | 0.595 | 3/3 | 2/3 | 120 |
| penalty+x lam=1 | 3 | 3 | 0.059 | 0.106 | 0.460 | 0.600 | 0.595 | 2/3 | 0/3 | 120 |
| penalty+x lam=3 | 3 | 3 | 0.079 | 0.106 | 0.597 | 0.600 | 0.595 | 2/3 | 0/3 | 120 |
| penalty+x lam=10 | 3 | 3 | 0.067 | 0.106 | 0.643 | 0.588 | 0.595 | 0/3 | 0/3 | 120 |
| penalty+x lam=10 ramp | 3 | 3 | 0.094 | 0.106 | 0.846 | 0.599 | 0.595 | 3/3 | 0/3 | 120 |
| xy+dicke | 3 | 3 | 0.320 | 0.106 | 1.000 | 0.785 | 0.595 | 3/3 | 3/3 | 120 |
| xy+dicke ramp | 3 | 3 | 0.157 | 0.106 | 1.000 | 0.686 | 0.595 | 3/3 | 3/3 | 120 |

### Evaluation budget per method

| method | mean evaluations | mean energy gap | mean time (s) |
|---|---|---|---|
| exact | 64 | 0.0000 | 0.002 |
| sa | 5005 | 0.0000 | 0.280 |
| greedy | n/a | 0.0000 | 0.001 |
| qaoa | 118 | 0.0000 | 1.033 |

### Every instance, xy+dicke

| K | N | p | P(optimal) | uniform P(optimal) | approx. ratio (feasible) | uniform approx. ratio | optimizer evaluations |
|---|---|---|---|---|---|---|---|
| 2 | 6 | 1 | 0.225 | 0.200 | 0.687 | 0.594 | 120 |
| 2 | 6 | 2 | 0.220 | 0.200 | 0.686 | 0.594 | 120 |
| 2 | 6 | 3 | 0.531 | 0.200 | 0.787 | 0.594 | 120 |
| 3 | 6 | 1 | 0.180 | 0.050 | 0.739 | 0.618 | 120 |
| 3 | 6 | 2 | 0.091 | 0.050 | 0.708 | 0.618 | 120 |
| 3 | 6 | 3 | 0.194 | 0.050 | 0.771 | 0.618 | 120 |
| 4 | 6 | 1 | 0.051 | 0.067 | 0.649 | 0.575 | 120 |
| 4 | 6 | 2 | 0.126 | 0.067 | 0.681 | 0.575 | 120 |
| 4 | 6 | 3 | 0.233 | 0.067 | 0.797 | 0.575 | 120 |

### Every instance, penalty+x lam=10

| K | N | p | P(optimal) | uniform P(optimal) | approx. ratio (feasible) | uniform approx. ratio | optimizer evaluations |
|---|---|---|---|---|---|---|---|
| 2 | 6 | 1 | 0.090 | 0.200 | 0.595 | 0.594 | 120 |
| 2 | 6 | 2 | 0.105 | 0.200 | 0.587 | 0.594 | 120 |
| 2 | 6 | 3 | 0.125 | 0.200 | 0.591 | 0.594 | 120 |
| 3 | 6 | 1 | 0.033 | 0.050 | 0.618 | 0.618 | 120 |
| 3 | 6 | 2 | 0.033 | 0.050 | 0.618 | 0.618 | 120 |
| 3 | 6 | 3 | 0.026 | 0.050 | 0.599 | 0.618 | 120 |
| 4 | 6 | 1 | 0.023 | 0.067 | 0.565 | 0.575 | 120 |
| 4 | 6 | 2 | 0.029 | 0.067 | 0.586 | 0.575 | 120 |
| 4 | 6 | 3 | 0.050 | 0.067 | 0.574 | 0.575 | 120 |

## real_penmanshiel (3 instances, status final)

### QAOA against the uniform-over-feasible baseline

| variant | p | instances | P(optimal) | uniform P(optimal) | P(feasible) | approx. ratio (feasible) | uniform approx. ratio | beat uniform ratio | beat uniform P(optimal) | optimizer evaluations |
|---|---|---|---|---|---|---|---|---|---|---|
| penalty+x lam=1 | 1 | 3 | 0.000 | 0.000 | 0.269 | 0.519 | 0.523 | 1/3 | 0/3 | 71 |
| penalty+x lam=3 | 1 | 3 | 0.000 | 0.000 | 0.138 | 0.517 | 0.523 | 1/3 | 0/3 | 60 |
| penalty+x lam=10 | 1 | 3 | 0.000 | 0.000 | 0.366 | 0.527 | 0.523 | 3/3 | 0/3 | 95 |
| penalty+x lam=10 ramp | 1 | 3 | 0.000 | 0.000 | 0.363 | 0.523 | 0.523 | 2/3 | 0/3 | 96 |
| xy+dicke | 1 | 3 | 0.001 | 0.000 | 1.000 | 0.621 | 0.523 | 3/3 | 1/3 | 120 |
| xy+dicke ramp | 1 | 3 | 0.000 | 0.000 | 1.000 | 0.558 | 0.523 | 3/3 | 1/3 | 120 |
| penalty+x lam=1 | 2 | 3 | 0.000 | 0.000 | 0.212 | 0.522 | 0.523 | 1/3 | 0/3 | 114 |
| penalty+x lam=3 | 2 | 3 | 0.000 | 0.000 | 0.378 | 0.526 | 0.523 | 2/3 | 0/3 | 120 |
| penalty+x lam=10 | 2 | 3 | 0.000 | 0.000 | 0.357 | 0.524 | 0.523 | 2/3 | 0/3 | 120 |
| penalty+x lam=10 ramp | 2 | 3 | 0.000 | 0.000 | 0.349 | 0.527 | 0.523 | 3/3 | 0/3 | 115 |
| xy+dicke | 2 | 3 | 0.002 | 0.000 | 1.000 | 0.673 | 0.523 | 3/3 | 2/3 | 120 |
| xy+dicke ramp | 2 | 3 | 0.001 | 0.000 | 1.000 | 0.582 | 0.523 | 3/3 | 1/3 | 120 |
| penalty+x lam=1 | 3 | 3 | 0.000 | 0.000 | 0.141 | 0.518 | 0.523 | 2/3 | 0/3 | 120 |
| penalty+x lam=3 | 3 | 3 | 0.000 | 0.000 | 0.115 | 0.549 | 0.523 | 2/3 | 0/3 | 120 |
| penalty+x lam=10 | 3 | 3 | 0.000 | 0.000 | 0.434 | 0.521 | 0.523 | 1/3 | 0/3 | 120 |
| penalty+x lam=10 ramp | 3 | 3 | 0.000 | 0.000 | 0.359 | 0.527 | 0.523 | 3/3 | 0/3 | 120 |
| xy+dicke | 3 | 3 | 0.003 | 0.000 | 1.000 | 0.682 | 0.523 | 3/3 | 3/3 | 120 |
| xy+dicke ramp | 3 | 3 | 0.000 | 0.000 | 1.000 | 0.576 | 0.523 | 3/3 | 1/3 | 120 |

### Evaluation budget per method

| method | mean evaluations | mean energy gap | mean time (s) |
|---|---|---|---|
| exact | 16384 | 0.0000 | 1.511 |
| sa | 5005 | 0.0000 | 0.661 |
| greedy | n/a | 0.0060 | 0.016 |
| qaoa | 111 | 0.0308 | 21.313 |

### Every instance, xy+dicke

| K | N | p | P(optimal) | uniform P(optimal) | approx. ratio (feasible) | uniform approx. ratio | optimizer evaluations |
|---|---|---|---|---|---|---|---|
| 5 | 14 | 1 | 0.003 | 0.000 | 0.613 | 0.533 | 120 |
| 5 | 14 | 2 | 0.007 | 0.000 | 0.669 | 0.533 | 120 |
| 5 | 14 | 3 | 0.008 | 0.000 | 0.676 | 0.533 | 120 |
| 7 | 14 | 1 | 0.000 | 0.000 | 0.628 | 0.535 | 120 |
| 7 | 14 | 2 | 0.000 | 0.000 | 0.694 | 0.535 | 120 |
| 7 | 14 | 3 | 0.001 | 0.000 | 0.695 | 0.535 | 120 |
| 9 | 14 | 1 | 0.000 | 0.000 | 0.622 | 0.501 | 120 |
| 9 | 14 | 2 | 0.000 | 0.000 | 0.655 | 0.501 | 120 |
| 9 | 14 | 3 | 0.001 | 0.000 | 0.675 | 0.501 | 120 |

### Every instance, penalty+x lam=10

| K | N | p | P(optimal) | uniform P(optimal) | approx. ratio (feasible) | uniform approx. ratio | optimizer evaluations |
|---|---|---|---|---|---|---|---|
| 5 | 14 | 1 | 0.000 | 0.000 | 0.533 | 0.533 | 120 |
| 5 | 14 | 2 | 0.000 | 0.000 | 0.533 | 0.533 | 120 |
| 5 | 14 | 3 | 0.000 | 0.000 | 0.532 | 0.533 | 120 |
| 7 | 14 | 1 | 0.000 | 0.000 | 0.536 | 0.535 | 84 |
| 7 | 14 | 2 | 0.000 | 0.000 | 0.535 | 0.535 | 120 |
| 7 | 14 | 3 | 0.000 | 0.000 | 0.530 | 0.535 | 120 |
| 9 | 14 | 1 | 0.000 | 0.000 | 0.510 | 0.501 | 80 |
| 9 | 14 | 2 | 0.000 | 0.000 | 0.503 | 0.501 | 120 |
| 9 | 14 | 3 | 0.000 | 0.000 | 0.502 | 0.501 | 120 |

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
