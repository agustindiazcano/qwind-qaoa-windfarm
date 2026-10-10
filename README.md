**This effort is supported by Qollab & IonQ**

# QWind: QAOA for Wind Farm Turbine Selection

**Theme:** Quantum Impact · **Status:** Hackathon submission (Qollab)

## In plain words

Wind turbines steal wind from each other: every turbine leaves a slower, turbulent "wake" behind it, and any turbine standing in that wake produces less energy. So *which* turbines you use matters.

**QWind** picks the best *K* turbines out of *N* candidate positions. It does this with a quantum algorithm (QAOA, built and simulated with Qiskit) and compares it honestly against classical methods. On real wind farms it is a **selection (curtailment) problem**: choose which *K* of the existing turbine positions to keep operating. It is not layout design.

## What we found

- **Putting the constraint inside the circuit helps.** A QAOA variant that always keeps exactly *K* turbines (XY mixer + Dicke start state) beats a uniform random choice over valid layouts in every instance we ran, at depths p = 1 to 3 (on the approximation ratio over feasible layouts).
- **The standard penalty version does not.** Encoding "exactly K turbines" as a penalty does not beat the uniform baseline consistently, for any penalty weight we tested.
- **At these sizes, classical methods are enough.** Simulated annealing reaches the exact optimum on every dataset. The best layout sampled from the XY + Dicke QAOA also reaches it in every instance of five of the six datasets (and in 2 of 3 instances at N = 14), but random feasible sampling with the same 1000 samples is almost as good at N up to 12, so this is not evidence of an advantage. **We do not claim a quantum advantage, a speedup, or energy or cost savings.**

Everything is simulated on a CPU (no quantum hardware), and the instances are small (at most 14 cells).

## Try it

Click **Run your code** on this page with the built-in simulator selected. Source code, tests and experiments: https://github.com/agustindiazcano/qwind-qaoa-windfarm

The default Run (N = 8 cells, K = 3 turbines, QAOA depth p = 2, seed 0) prints one comparison table (exact enumeration, simulated annealing, greedy search, QAOA with XY mixer + Dicke start), followed by a detail block that compares QAOA with the uniform-over-feasible baseline. In our tests the Run takes about 15 to 25 s in total (measurements: [docs/QOLLAB_RUNTIME.md](https://github.com/agustindiazcano/qwind-qaoa-windfarm/blob/main/docs/QOLLAB_RUNTIME.md)). The Run accepts up to 12 cells (recommended up to 10); larger instances are computed offline and their stored results are shown below.

## Results

All numbers come from `results/summary.json` and `results/per_instance.csv` (fixed protocol `qwind-v1`, run in GitHub Actions). Nothing is typed by hand. Full tables, every variant and every instance: [results/results_tables.md](https://github.com/agustindiazcano/qwind-qaoa-windfarm/blob/main/results/results_tables.md). Datasets are never averaged together.

<!-- RESULTS:START -->
**Datasets** (short name used in the tables below; the full name is the dataset id in `results/`)

| name | dataset | what it is | instances |
|---|---|---|---|
| Synthetic | `synthetic` | Synthetic wind roses on a synthetic grid | 24 |
| Penmanshiel | `real_penmanshiel` | All 14 real turbine positions of the Penmanshiel farm, measured wind rose | 3 |
| Penmanshiel-10 | `real_penmanshiel_sub10` | The 10 Penmanshiel turbines closest to the farm centroid (a subset) | 3 |
| Kelmarsh | `real_kelmarsh` | The 6 real turbines of the Kelmarsh farm, measured wind rose (trivial contrast) | 3 |
| Chubut | `real_chubut` | ERA5 wind rose of the Chubut coast on a synthetic grid (secondary) | 8 |
| Bahia | `real_bahia_blanca` | ERA5 wind rose of Bahia Blanca on a synthetic grid (secondary) | 8 |

**Constraint-preserving QAOA (XY mixer + Dicke start) against the uniform-over-feasible baseline, depth p = 3**

| dataset | instances | P(optimal) | uniform P(optimal) | approx. ratio (feasible) | uniform ratio | beat uniform ratio | beat uniform P(optimal) | evaluations |
|---|---|---|---|---|---|---|---|---|
| Synthetic | 24 | 0.072 | 0.021 | 0.731 | 0.578 | 24/24 | 20/24 | 120 |
| Penmanshiel | 3 | 0.003 | 0.000 | 0.682 | 0.523 | 3/3 | 3/3 | 120 |
| Penmanshiel-10 | 3 | 0.054 | 0.015 | 0.660 | 0.483 | 3/3 | 3/3 | 120 |
| Kelmarsh | 3 | 0.320 | 0.106 | 0.785 | 0.595 | 3/3 | 3/3 | 120 |
| Chubut | 8 | 0.092 | 0.021 | 0.713 | 0.527 | 8/8 | 7/8 | 120 |
| Bahia | 8 | 0.065 | 0.021 | 0.685 | 0.485 | 8/8 | 8/8 | 120 |

**Penalty QAOA (X mixer), all settings of the sweep** (penalty weight 1, 3 and 10 times max|h|, plus one ramp variant; p = 1-3). Range of instances that beat the uniform baseline over settings and depths:

| dataset | instances | settings | beat uniform ratio | beat uniform P(optimal) | P(feasible) range |
|---|---|---|---|---|---|
| Synthetic | 24 | 4 | 9-17/24 | 0-4/24 | 0.26-0.44 |
| Penmanshiel | 3 | 4 | 1-3/3 | 0/3 | 0.11-0.43 |
| Penmanshiel-10 | 3 | 4 | 0-3/3 | 0/3 | 0.22-0.51 |
| Kelmarsh | 3 | 4 | 0-3/3 | 0/3 | 0.32-0.85 |
| Chubut | 8 | 4 | 2-7/8 | 0-1/8 | 0.26-0.50 |
| Bahia | 8 | 4 | 1-7/8 | 0-1/8 | 0.22-0.53 |

**Final solution quality against the classical methods** (gap to the exact optimum, mean over the instances of each dataset; XY + Dicke at depth p = 3, best layout of its 1000 samples). The budgets are not matched: simulated annealing uses far more objective evaluations than QAOA, and random feasible sampling uses the same 1000 samples as QAOA:

| dataset | SA gap | SA evaluations | greedy gap | XY+Dicke best-sample gap | XY+Dicke found the optimum | random feasible sampling finds the optimum (probability) | XY+Dicke evaluations |
|---|---|---|---|---|---|---|---|
| Synthetic | 0.0000 | 5005 | 0.0129 | 0.0000 | 24/24 | 0.95 | 120 |
| Penmanshiel | 0.0000 | 5005 | 0.0060 | 0.0060 | 2/3 | 0.35 | 120 |
| Penmanshiel-10 | 0.0000 | 5005 | 0.0000 | 0.0000 | 3/3 | 0.99 | 120 |
| Kelmarsh | 0.0000 | 5005 | 0.0000 | 0.0000 | 3/3 | 1.00 | 120 |
| Chubut | 0.0000 | 5005 | 0.0000 | 0.0000 | 8/8 | 0.95 | 120 |
| Bahia | 0.0000 | 5005 | 0.0000 | 0.0000 | 8/8 | 0.95 | 120 |
<!-- RESULTS:END -->

### How to read the tables

- The reference point is the *uniform distribution over feasible layouts*, not 1. QAOA's approximation ratios are well below 1; the absolute values are in the tables.
- The constraint-preserving ansatz beats the uniform baseline on the approximation ratio in every instance reported here, at p = 1 to 3. On P(optimal) it does so in most instances but not all (counts in the table).
- Classical methods solve these instances exactly or nearly so: simulated annealing reaches gap 0 in every dataset (about 5005 evaluations), and greedy search misses by a small margin on two. The best layout sampled from the XY + Dicke QAOA reaches the exact optimum in every instance of five datasets and in 2 of 3 instances at N = 14 (p = 3); the penalty variants do so less often (`results/results_tables.md`). Random feasible sampling with the same 1000 samples already finds the optimum with probability 0.95 to 1.00 for N up to 12, so matching simulated annealing at those sizes does not show an advantage. At N = 14 random sampling finds it with probability 0.35 on average (XY + Dicke: 2 of 3 instances, too few to conclude).
- Penmanshiel, Penmanshiel-10 and Kelmarsh have 3 instances each, too few for a mean or an interval: read them instance by instance in `results/results_tables.md`. The means above for those rows are only a summary.
- At N = 14 (Penmanshiel) the probability of sampling the optimal layout is tiny in absolute terms for both QAOA and the uniform baseline; what improves is the distribution over feasible layouts.
- One run per instance, one simulator, at most 14 cells. Results come from one environment (Python 3.12.15 in GitHub Actions). A Run on Qollab (Python 3.14.2) can give slightly different values; we do not claim reproducibility across environments.

## How to run

**On Qollab:** click **Run your code** with the built-in simulator.

**Locally:**
```
pip install -r qollab/requirements.txt pytest
python qollab/main.py            # the same Run as on Qollab
python -m pytest                 # tests (add -m "not heavy" to skip the slowest ones)
```

**Offline experiments** (fixed protocol `qwind-v1`, never retuned): `python experiments/run_all.py --dataset <name> --jobs 4`, then `python experiments/run_all.py --merge`. The full runs were executed with the manual GitHub Actions workflow `run-experiments.yml`. Tables: `python scripts/make_results_tables.py --readme README.md`.

## What this adds beyond running QAOA

- A comparative benchmark with controls: uniform sampling over feasible layouts and random feasible sampling with the same number of shots, next to exact, simulated annealing and greedy search.
- A constraint-preserving variant (XY mixer with a Dicke start state) measured against the penalty formulation, with the penalty weight swept.
- Real data: operating-farm turbine positions and measured wind roses, plus ERA5 roses as a secondary dataset (sources and licenses: [docs/DATA.md](https://github.com/agustindiazcano/qwind-qaoa-windfarm/blob/main/docs/DATA.md)).

## Technical details

### The problem
Choosing *K* turbine sites out of *N* candidates is a combinatorial optimization problem: the number of layouts grows as C(N, K). We encode the wake losses as a **QUBO** with a cardinality constraint:

```
E(x) = sum_i h_i x_i + sum_{i<j} J_ij x_i x_j + lam * (sum_i x_i - K)^2

x_i  = 1 if a turbine is placed at site i
h_i  = -P0   (negative isolated-turbine power)
J_ij = pairwise wake loss between sites i and j (wind-rose weighted)
lam  = penalty weight for the "exactly K turbines" constraint
```

### Physical model
- Jensen/Park top-hat wake model: the velocity deficit decays with downwind distance inside an expanding wake cone.
- A wind rose (direction, frequency, speed) weights the losses.
- **Approximation:** losses are pairwise additive. A full multi-wake superposition is not pairwise, so this is a simplification (documented in [docs/model.md](https://github.com/agustindiazcano/qwind-qaoa-windfarm/blob/main/docs/model.md)). Mean wind speed is stored in the data but not used by the model yet.

### Quantum part
- QAOA with depth *p* = 1, 2, 3: diagonal cost layer plus RX mixer, built in Qiskit.
- The Hamiltonian is built by hand as a `SparsePauliOp` (Ising mapping `x = (1 - Z) / 2`, qubit *i* = bit *i* of the state index).
- Constraint-preserving variant: XY mixer and Dicke initial state, in the line of Hadfield et al. [1] and Bärtschi and Eidenbenz [2]. The Dicke state is built with Qiskit's `StatePreparation`, not with their circuit. Parameter ramp inspired by Sack and Serbyn [3] (their paper studies MaxCut; ours is not a replication).
- Expectation values with `StatevectorEstimator`, classical optimization with `scipy.optimize` (COBYLA) and multiple seeded restarts, final sampling with `StatevectorSampler`.

### How the circuit is simulated
We simulate the full QAOA circuit in Qiskit. `StatevectorEstimator` and `StatevectorSampler` compute the exact expectation values and the exact output distribution on the CPU, so the optimization has no shot noise. We use these primitives for the optimization loop and do not call `backend.run` inside it. We have not benchmarked `backend.run` for this loop. Nothing runs on quantum hardware.

### Classical baselines
Exact enumeration (ground truth), simulated annealing, greedy search with local swaps.

### What we measure
- Probability mass on feasible layouts (exactly *K* turbines)
- Approximation ratio over feasible layouts, with the uniform-over-feasible distribution as the reference
- Probability that QAOA samples the optimal layout, and gap of the best sampled layout
- Effect of circuit depth (*p* = 1, 2, 3) and of the penalty weight
- Optimizer evaluations and run time

### Run environment (Qollab)
- Python 3.14 on Qollab (stored results produced with Python 3.12 in GitHub Actions), Qiskit 2.5.2, NumPy, SciPy, built-in simulator.
- Live Run: we keep it small so it finishes quickly (default N = 8, recommended up to 10 cells, hard limit 12). Larger instances, including the full 14-turbine Penmanshiel farm, are computed offline and their stored results are included.

### Repository layout
```
qollab/        what runs on Qollab (main.py, qwind/ package, small data)
experiments/   full offline runs
results/       results used by this page and the website
tests/         correctness tests (QUBO energy equals brute force, qubit ordering)
docs/          model notes, data sources, project context
web/           presentation website
```

## Limitations

- Simplified wake model: Jensen losses that are pairwise additive; mean wind speed not used yet.
- Small instances only (at most 14 cells, exact statevector simulation); the live Run is limited to 12.
- CPU simulation only (Qiskit statevector primitives); no real quantum hardware and no noise.
- "Real" means real turbine positions and a measured or reanalysis wind rose, not a validated farm model: the nacelle anemometer sees upwind wakes, there is one year (2019) per farm, and the farm layouts were not designed for this objective.
- Few instances for the real farms (3 each); no statistical claim beyond this benchmark.
- No quantum advantage is claimed.

## Tech Stack

Qiskit 2.5.2, NumPy, SciPy, Python 3.14 (Qollab) / 3.12 (GitHub Actions results).

## Hackathon node and team

Competing at the **UNICEN** node (Universidad Nacional del Centro de la Provincia de Buenos Aires, Argentina): https://exa.unicen.edu.ar/ · Track: *Professional*

**Team Salta**
- Agustin Diaz-Cano, MS Candidate, Information Systems Engineering (UTN)
- Baltazar Salerno, Frontend Developer

## Disclosure

- Built during the official hackathon window. Prior code, templates and forks: none.
- Process: every change went through a pull request that a team member approved and merged, with automated tests and CI; results come from a fixed protocol run in GitHub Actions.
- AI tools used: Claude (chat: planning, review) and Claude Code (coding agent, code and documentation assistance), Gemini Antigravity (planning, coding agent and brainstorming, web search), Grok (brainstorming, web search).
- Libraries: Qiskit, NumPy, SciPy (the offline experiments and the Qollab Run use only these and the standard library; pytest for the tests).
- Method: QAOA, the constraint-preserving mixer, the Dicke state and the ramp initialization come from the literature in [References](#references). The application to wind-farm turbine selection, the comparative benchmark with controls and the data pipeline are our own work.
- Wind data and licenses (details in [docs/DATA.md](https://github.com/agustindiazcano/qwind-qaoa-windfarm/blob/main/docs/DATA.md)):
  - Penmanshiel and Kelmarsh wind farm data: Plumley, C. and Takeuchi, R., released by Cubico Sustainable Investments Ltd, Zenodo, CC BY 4.0 ([license](https://creativecommons.org/licenses/by/4.0/); [10.5281/zenodo.16807304](https://doi.org/10.5281/zenodo.16807304), [10.5281/zenodo.16807551](https://doi.org/10.5281/zenodo.16807551)). Adapted: only turbine positions and a 16-sector wind rose from 2019 SCADA were derived.
  - ERA5 hourly 100 m wind via the Open-Meteo API (CC BY 4.0, [license](https://creativecommons.org/licenses/by/4.0/)). Contains modified Copernicus Climate Change Service information 2026. Neither the European Commission nor ECMWF is responsible for any use that may be made of the Copernicus information or data it contains.

## References

1. Hadfield, S., Wang, Z., O'Gorman, B., Rieffel, E. G., Venturelli, D., Biswas, R. "From the Quantum Approximate Optimization Algorithm to a Quantum Alternating Operator Ansatz." *Algorithms* 12(2), 34 (2019). [doi:10.3390/a12020034](https://doi.org/10.3390/a12020034), [arXiv:1709.03489](https://arxiv.org/abs/1709.03489)
2. Bärtschi, A., Eidenbenz, S. "Deterministic Preparation of Dicke States." *FCT 2019*, pp. 126-139. [doi:10.1007/978-3-030-25027-0_9](https://doi.org/10.1007/978-3-030-25027-0_9), [arXiv:1904.07358](https://arxiv.org/abs/1904.07358)
3. Sack, S. H., Serbyn, M. "Quantum annealing initialization of the quantum approximate optimization algorithm." *Quantum* 5, 491 (2021). [doi:10.22331/q-2021-07-01-491](https://doi.org/10.22331/q-2021-07-01-491), [arXiv:2101.05742](https://arxiv.org/abs/2101.05742)
