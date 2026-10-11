**This effort is supported by Qollab & IonQ**

# QWind: QAOA for Wind Farm Turbine Selection

**Theme:** Quantum Impact · **Status:** Hackathon submission (Qollab)

**A quantum algorithm that picks which wind turbines to keep running, and never proposes an invalid plan.** Tested on the real turbines and measured winds of two operating wind farms.

- **3.4 to 17.1 times** more likely to find the best layout than the standard quantum formulation.
- **Exact optimum** in every instance of 5 of 6 datasets, matching simulated annealing, with about 120 optimizer evaluations.
- **100% valid plans:** the "keep exactly *K* turbines" rule is built into the circuit.
- **Real data:** the 14 real turbine positions of Penmanshiel (Scotland) and the 6 of Kelmarsh (England), with measured winds, plus wind roses from Argentina (Chubut, Bahia Blanca).
- **Open source (MIT)**, 150+ tests, protocol fixed before running, and it runs on Qollab in about 20 seconds.

## The problem in pictures

![Schematic side view of two wind turbines in a row with the wind coming from the left. The first turbine has full wind and leaves behind a widening blue wake of slower, turbulent air; the second turbine stands inside that wake and gets slower wind and less power.](https://raw.githubusercontent.com/agustindiazcano/qwind-qaoa-windfarm/main/results/figures/what_is_a_wake.png)

![Top view of the 14 real turbine positions of the Penmanshiel wind farm in Scotland, with an arrow for the dominant wind direction. Seven turbines are blue (kept running) and seven are grey outlines (switched off); light blue strips downwind of the blue turbines show their wakes.](https://raw.githubusercontent.com/agustindiazcano/qwind-qaoa-windfarm/main/results/figures/the_decision.png)

![Flow diagram in five boxes: wind and turbine positions, wake model, choice problem, quantum circuit built in Qiskit that keeps exactly K turbines by construction, and the answer, the K turbines to keep running.](https://raw.githubusercontent.com/agustindiazcano/qwind-qaoa-windfarm/main/results/figures/how_it_works.png)

## Results at a glance

![Horizontal bar chart for six datasets: how many times more likely the XY mixer + Dicke circuit is to sample the best layout than random valid choice (3 to 7.5 times) and than the best penalty version (3.4 to 17.1 times); the tallest bar is Penmanshiel, 17.1 times.](https://raw.githubusercontent.com/agustindiazcano/qwind-qaoa-windfarm/main/results/figures/multipliers.png)

![Horizontal bar chart for six datasets: share of instances where the best of 1000 samples is the exact optimum. The XY mixer + Dicke circuit reaches 100% on five datasets and 67% on Penmanshiel; the penalty formulation reaches between 0% and 100%.](https://raw.githubusercontent.com/agustindiazcano/qwind-qaoa-windfarm/main/results/figures/chance_of_best.png)

![Horizontal bar chart for six datasets: share of the circuit's probability that falls on valid layouts. The XY mixer + Dicke circuit is at 100% everywhere; the penalty formulation is between 26% and 64%.](https://raw.githubusercontent.com/agustindiazcano/qwind-qaoa-windfarm/main/results/figures/valid_plans.png)

![Line chart for the synthetic dataset: probability of sampling the best layout at circuit depths 1, 2 and 3. The XY mixer + Dicke circuit rises from 5.0% to 7.2%; the penalty formulation stays near 1%; random valid choice is a flat line near 2%.](https://raw.githubusercontent.com/agustindiazcano/qwind-qaoa-windfarm/main/results/figures/depth.png)

*Figures generated from `results/` by `experiments/make_figures.py`. Full tables below.*

## In plain words

Wind turbines steal wind from each other. Every turbine leaves a slower, turbulent wake behind it, and a turbine standing in that wake produces less. In a wind farm that already exists, an operator who has to run fewer turbines (a curtailment) can choose *which* ones to keep, and that choice changes how much energy the wakes waste.

We turned that choice into an optimization problem, pick the best *K* of *N* turbine positions, and asked a concrete question: **can a quantum algorithm (QAOA, simulated in Qiskit) solve it well, and does the way you build the circuit matter?** We tested it the way a skeptic would: against exact enumeration, simulated annealing, greedy search and plain random choice among valid layouts, on six datasets, including the real turbine positions and measured winds of two operating wind farms (Penmanshiel and Kelmarsh).

## What we found

1. **Building the constraint into the circuit pays off.** A QAOA that always keeps exactly *K* turbines (XY mixer + Dicke start state) turns every output into a valid layout, and the probability of sampling the best layout is 3 to 7.5 times higher than random choice among valid layouts and 3.4 to 17.1 times higher than the usual penalty formulation, depending on the dataset.
2. **It reaches the exact optimum.** Its best sample is the exact optimum in every instance of 5 of the 6 datasets, matching simulated annealing's result with about 120 optimizer evaluations.
3. **It holds up on real wind farms.** The same circuit works with the real turbine positions and measured winds of two operating farms. On the 14 turbines of Penmanshiel, where picking valid layouts at random finds the best one with probability about 0.35 on average, it finds the best layout in 2 of 3 instances.
4. **A reproducible benchmark.** Every result comes with controls and is generated from a protocol fixed before running.

The lesson we take is practical: when a problem has a hard constraint, build it into the circuit, and always benchmark against the boring baselines, because they decide whether a result means anything.

## Why it matters

When a wind farm has to run fewer turbines, the choice of which ones to keep decides how much of the production that remains is lost to wakes. In our model, using the real Penmanshiel layout and its measured wind rose, the share of potential power lost to wakes is 4.0% against 8.0% for 7 of the 14 turbines (the best choice against an average random choice), 1.0% against 5.3% for 5 turbines, and 7.0% against 10.6% for 9 turbines. QWind is a way to search that decision systematically, and at this size exact search can verify the choices it finds.

These are modelled wake losses (a Jensen wake model, equal turbines), not measured production or costs. We have not measured costs, or the algorithm working in a real farm, so the impact is potential: the decision affects the energy a curtailed farm still delivers and, through it, the value of that energy. The next section puts an illustrative scale on it.

## What it could be worth

Using the measured production of the Penmanshiel turbines, this is the scale of what the choice is worth in an illustrative scenario:

<!-- IMPACT:START -->
**Illustrative estimate for Penmanshiel.** Assumptions: each kept turbine produces its measured 2019 average (637 kW, a capacity factor of 31.1%); the farm runs with only K of its 14 turbines for 1,000 hours; the wake losses are the modelled ones, for the best choice against an average random choice of the same K turbines; the prices are round numbers for illustration.

| Turbines kept (K of 14) | Modelled power lost to wakes: best vs average random choice | More energy from the same K turbines | Extra energy per 1,000 hours | Value at £50/MWh | Value at £75/MWh | Value at £100/MWh |
|---|---|---|---|---|---|---|
| 5 | 1.0% vs 5.3% | +4.5% | 136 MWh | £6.8k | £10.2k | £13.6k |
| 7 | 4.0% vs 8.0% | +4.3% | 176 MWh | £8.8k | £13.2k | £17.6k |
| 9 | 7.0% vs 10.6% | +4.0% | 207 MWh | £10.3k | £15.5k | £20.7k |

This is an illustrative estimate of scale, not a forecast. It comes from a model, it compares with an average random choice (not with what an operator does today), it assumes 1,000 hours in that configuration (a year has 8,760; how many hours a farm is curtailed is not in our data), and it counts neither costs nor the structure of any contract. Details and sources: [docs/IMPACT.md](https://github.com/agustindiazcano/qwind-qaoa-windfarm/blob/main/docs/IMPACT.md).
<!-- IMPACT:END -->

## What we built

- A wake-loss model (Jensen, pairwise additive) turned into a QUBO with an exactly-*K* constraint, and a QAOA written by hand in Qiskit with two ways of enforcing the constraint (penalty, or XY mixer + Dicke state).
- A fixed experimental protocol (`qwind-v1`), decided before running and never retuned, run in GitHub Actions on six datasets: synthetic wind roses, the real positions and measured winds of Penmanshiel and Kelmarsh, and two ERA5 wind roses (open licenses for all the real data).
- Controls next to every result: the uniform distribution over valid layouts, random valid sampling with the same 1000 samples, exact enumeration, simulated annealing and greedy search.
- 150+ tests, continuous integration, and tables in this README that are generated from `results/`, so no number is typed by hand.

Everything is simulated on a CPU (no quantum hardware), the instances are small (at most 14 cells), the wake model is simplified and there is one year of wind data per farm. The limitations are listed below.

## Try it

Click **Run your code** on this page with the built-in simulator selected. Source code, tests and experiments: https://github.com/agustindiazcano/qwind-qaoa-windfarm

The default Run (N = 8 cells, K = 3 turbines, QAOA depth p = 2, seed 0) prints one comparison table (exact enumeration, simulated annealing, greedy search, QAOA with XY mixer + Dicke start), followed by a detail block that compares QAOA with the uniform-over-feasible baseline. In our tests the Run takes about 15 to 25 s in total (measurements: [docs/QOLLAB_RUNTIME.md](https://github.com/agustindiazcano/qwind-qaoa-windfarm/blob/main/docs/QOLLAB_RUNTIME.md)). The Run accepts up to 12 cells (recommended up to 10); larger instances are computed offline and their stored results are shown below.

## Results

All numbers come from `results/summary.json` and `results/per_instance.csv` (fixed protocol `qwind-v1`, run in GitHub Actions). Nothing is typed by hand. Full tables, every variant and every instance: [results/results_tables.md](https://github.com/agustindiazcano/qwind-qaoa-windfarm/blob/main/results/results_tables.md). Datasets are never averaged together.

<!-- RESULTS:START -->
**Datasets** (short name used in the tables below; the full name is the dataset id in `results/`)

| name | dataset | country | what it is | source | instances |
|---|---|---|---|---|---|
| Synthetic | `synthetic` | n/a | Synthetic wind roses on a synthetic grid | Generated by us, see `docs/DATA.md` | 24 |
| Penmanshiel | `real_penmanshiel` | Scotland, UK | All 14 real turbine positions of the Penmanshiel farm, measured wind rose | [Zenodo](https://doi.org/10.5281/zenodo.16807304), CC BY 4.0 | 3 |
| Penmanshiel-10 | `real_penmanshiel_sub10` | Scotland, UK | The 10 Penmanshiel turbines closest to the farm centroid (a subset) | [Zenodo](https://doi.org/10.5281/zenodo.16807304), CC BY 4.0 | 3 |
| Kelmarsh | `real_kelmarsh` | England, UK | The 6 real turbines of the Kelmarsh farm, measured wind rose (trivial contrast) | [Zenodo](https://doi.org/10.5281/zenodo.16807551), CC BY 4.0 | 3 |
| Chubut | `real_chubut` | Argentina | ERA5 wind rose of the Chubut coast on a synthetic grid (secondary) | [ERA5](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels) via [Open-Meteo](https://open-meteo.com/en/docs/historical-weather-api), CC BY 4.0 | 8 |
| Bahia | `real_bahia_blanca` | Argentina | ERA5 wind rose of Bahia Blanca on a synthetic grid (secondary) | [ERA5](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels) via [Open-Meteo](https://open-meteo.com/en/docs/historical-weather-api), CC BY 4.0 | 8 |

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
- A different question from related quantum work on wind farms [4, 6]. Those studies design new layouts on a grid; Nigro et al. set the number of turbines as a penalty and report that their quantum annealer sometimes placed the wrong number of turbines. QWind chooses which of the existing turbines to keep running, on real positions, and builds the number of turbines into the circuit so every answer has exactly *K*.

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

### Related work

4. Hancock, J., Craven, M. J., McNeile, C., Vadacchino, D. "Investigating Techniques to Optimise the Layout of Turbines in a Windfarm using a Quantum Computer." [arXiv:2312.13123](https://arxiv.org/abs/2312.13123)
5. Hancock, J., Craven, M., McNeile, C. "Investigating methods to solve large windfarm optimization problems with a minimum number of qubits using circuit-based quantum computers." [arXiv:2512.17582](https://arxiv.org/abs/2512.17582)
6. Nigro, L., Sala, S., Amendola, A., Prati, E. "Leveraging Quantum Annealing for Layout Optimization." *Advanced Quantum Technologies* 8(11), e00358 (2025). [doi:10.1002/qute.202500358](https://doi.org/10.1002/qute.202500358)
7. Kordonowy, S., Leipold, H. "The Lie Algebra of XY-mixer Topologies and Warm Starting QAOA for Constrained Optimization." *npj Quantum Information* 12, 61 (2026). [arXiv:2505.18396](https://arxiv.org/abs/2505.18396)
8. Mancilla, J., Bouloumis, T. D., Goguikian, F. "Constrained Portfolio Optimization via QAOA with XY-Mixers and Trotterized Initialization: A Hybrid Approach for Direct Indexing." [arXiv:2602.14827](https://arxiv.org/abs/2602.14827)

### Data and sources

- Penmanshiel wind farm data (Scotland, UK). Plumley, C., Takeuchi, R.; released by Cubico Sustainable Investments Ltd. Zenodo, CC BY 4.0. [doi:10.5281/zenodo.16807304](https://doi.org/10.5281/zenodo.16807304)
- Kelmarsh wind farm data (England, UK). Plumley, C., Takeuchi, R.; released by Cubico Sustainable Investments Ltd. Zenodo, CC BY 4.0. [doi:10.5281/zenodo.16807551](https://doi.org/10.5281/zenodo.16807551)
- ERA5 hourly data on single levels from 1940 to present. Copernicus Climate Change Service (C3S) Climate Data Store. [dataset page](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels), [doi:10.24381/cds.adbb2d47](https://doi.org/10.24381/cds.adbb2d47)
- Open-Meteo Historical Weather API, used to access ERA5. Zippenfenig, P. (2023). Open-Meteo.com Weather API. [documentation](https://open-meteo.com/en/docs/historical-weather-api), [doi:10.5281/zenodo.7970649](https://doi.org/10.5281/zenodo.7970649)
- UK Government, Contracts for Difference Allocation Round 6, budget notice (administrative strike prices, 2012 prices), used as a price reference in the impact estimate. [PDF](https://assets.publishing.service.gov.uk/media/65e867c162ff48001a87b252/cfd-ar6-budget-notice.pdf)
- License of the data: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
