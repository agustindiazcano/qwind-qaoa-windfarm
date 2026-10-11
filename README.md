**This effort is supported by Qollab & IonQ**

![QWind, with Qollab, IonQ and Facultad de Ciencias Exactas UNICEN](https://raw.githubusercontent.com/agustindiazcano/qwind-qaoa-windfarm/main/docs/img/qwind-header.png)

# QWind: Quantum Optimization for Wind Farms

**Theme:** Quantum Impact · **Status:** Hackathon submission (Qollab) · [Project page on Qollab](https://qollab.xyz/u/agustindiazcano/qwind)

**Ran on real quantum hardware: [IonQ Forte 1 (36q)](#run-on-real-quantum-hardware), IonQ's real quantum computer, through Qollab. Among the valid samples the circuit reached 93% of its ideal success probability (N = 6, one run, 997 shots).**

## 1. What is it?

Wind turbines steal wind from each other. When a turbine runs, it leaves a turbulent "wake" of slower air behind it. If a second turbine stands in that wake, it generates less power. QWind is a quantum algorithm that decides which turbines to keep running and which to turn off when a farm has to reduce its power output. By choosing the right combination, it minimizes the energy wasted by these wakes. We tested the algorithm using real measured turbine positions and wind data from Penmanshiel (Scotland, UK) and Kelmarsh (England, UK), alongside reanalysis wind datasets from Chubut and Bahia Blanca (Argentina).

**Why a quantum computer? The space of plans explodes with farm size.**

| Farm size | Turbines kept | Possible plans |
|---|---|---|
| 14 turbines (Penmanshiel, our largest test) | 7 | 3,432 |
| 50 turbines | 25 | about 10^14 (126 trillion) |
| 100 turbines | 50 | about 10^29 |
| 1,000 turbines (illustrative, hypothetical) | 500 | about 10^299 |

Real farms typically have tens to a couple of hundred turbines; the 1,000-turbine row is only there to show how fast the space grows. A laptop checks 3,432 plans instantly, which is why we could verify every answer we report. Exact search is the classical bottleneck: checking plans one by one at a billion plans per second would take about 3 trillion years for 100 turbines, and at 1,000 turbines the count exceeds the number of atoms in the universe (about 10^80). Classical heuristics such as simulated annealing keep working at larger sizes, but they do not guarantee the optimum. Whether a constraint-preserving quantum circuit can match or beat them at 50 to 100 turbines is the open question that motivates this project; we do not answer it here.

## 2. Why does it matter, and who is it for?

This tool is for wind farm operators who need to temporarily curtail power because of grid limits, maintenance or environmental restrictions, and for quantum developers looking for a reproducible, honest benchmark. The choice of which turbines to shut down has a financial footprint. In an illustrative scenario using the measured wind and layout of Penmanshiel, our modelled wake losses show the potential extra energy value of picking the best layout instead of an average random choice:

| Turbines kept (of 14) | Power lost to wakes: best vs average random | Extra energy per 1,000 h | Value |
|---|---|---|---|
| 5 | 1.0% vs 5.3% | 136 MWh | $9.0k to $18.0k |
| 7 | 4.0% vs 8.0% | 176 MWh | $11.6k to $23.2k |
| 9 | 7.0% vs 10.6% | 207 MWh | $13.7k to $27.3k |

Values use $66 to $132 per MWh and assume 1,000 hours in that configuration. This is a modelled, illustrative scale (Jensen wake model), not a forecast and not a measured saving. Assumptions and sources: [What it could be worth](#what-it-could-be-worth).

## 3. How does the quantum part work?

The usual quantum approach adds a mathematical penalty to discourage invalid answers, but it still produces many of them. We built a circuit that enforces the rule by design (a Quantum Approximate Optimization Algorithm, QAOA, with an XY mixer and a Dicke initial state). Think of one switch per turbine: the circuit starts from a valid plan (exactly the right number of switches on) and only ever swaps them in pairs, so the ideal circuit never outputs an invalid layout. The wake losses between every pair of turbines are encoded as a QUBO cost, and a classical optimizer (COBYLA, about 120 evaluations) tunes the circuit angles; we then sample 1,000 times and keep the best layout.

| | XY mixer + Dicke circuit (ours) | Standard penalty formulation | Random valid choice |
|---|---|---|---|
| Share of output that is a valid plan | 100% | 26% to 64% | 100% |
| Chance of sampling the best layout | reference | ours is 3.4 to 17.1 times more likely, depending on dataset | ours is 3 to 7.5 times more likely than one random valid draw, depending on dataset |
| Best sampled layout is the exact optimum | all instances of 5 of 6 datasets; 2 of 3 on Penmanshiel (14 turbines) | less often | with the same 1,000 draws it finds it with probability 0.95 to 1.00 up to 12 turbines, 0.35 on average at 14 turbines |

We also ran the optimized circuit once on a real quantum computer (IonQ Forte 1) for a small instance (6 cells, 3 turbines, 997 shots). Under real noise, 22% of the samples were not valid layouts; they are recognized and discarded, and among the valid ones the circuit came close to the ideal and the best sample found was the exact optimum. [Details](#run-on-real-quantum-hardware).

| | P(optimal) | P(valid layout) | P(optimal), valid samples only |
|---|---|---|---|
| Ideal simulator | 0.1784 | 1.0000 | 0.1784 |
| IonQ Forte 1 | 0.1304 | 0.7834 | 0.1665 |
| Random valid choice | 0.1000 | 1.0000 | 0.1000 |

**What we do not claim:** quantum advantage. At these sizes classical simulated annealing solves all the instances we tested exactly, and picking valid layouts at random already finds the best one with probability 0.95 or higher for up to 12 cells. We could only test up to 14 turbines because we simulate the circuit exactly on a CPU, which stops being possible at around 30 qubits. Settling the large-farm question needs larger hardware runs. Our contribution is the constraint-preserving circuit design, a benchmark with honest baselines, and a first execution on noisy quantum hardware (one small run).

## 4. How do I run it?

**On Qollab:** open the [project page](https://qollab.xyz/u/agustindiazcano/qwind) and click **Run your code** with the built-in simulator selected. The default run takes about 20 seconds and prints a comparison table (exact search, simulated annealing, greedy, QAOA).

**Locally:** clone the GitHub repository and run:
```
pip install -r qollab/requirements.txt pytest
python qollab/main.py
python -m pytest
```

<!-- TODO(owner): add the public YouTube link to the 3-minute demo video (with captions) here and in the top banner -->

Open source (MIT), 150+ tests, protocol fixed before running. Source: https://github.com/agustindiazcano/qwind-qaoa-windfarm. More options in [How to run](#how-to-run).

**Quick links:** [The problem in pictures](#the-problem-in-pictures) · [Results at a glance](#results-at-a-glance) · [Run on real quantum hardware](#run-on-real-quantum-hardware) · [What it could be worth](#what-it-could-be-worth) · [Limitations](#limitations)

**Contents**

- **The four questions:** [1. What is it?](#1-what-is-it) · [2. Why does it matter, and who is it for?](#2-why-does-it-matter-and-who-is-it-for) · [3. How does the quantum part work?](#3-how-does-the-quantum-part-work) · [4. How do I run it?](#4-how-do-i-run-it)
- **Overview:** [The problem in pictures](#the-problem-in-pictures) · [Results at a glance](#results-at-a-glance) · [In plain words](#in-plain-words) · [What we found](#what-we-found)
- **Impact and hardware:** [Why it matters](#why-it-matters) · [What it could be worth](#what-it-could-be-worth) · [Run on real quantum hardware](#run-on-real-quantum-hardware)
- **The project:** [What we built](#what-we-built) · [Try it](#try-it) · [Results](#results) · [How to run](#how-to-run) · [What this adds beyond running QAOA](#what-this-adds-beyond-running-qaoa) · [Technical details](#technical-details)
- **Limits and credits:** [Limitations](#limitations) · [Tech Stack](#tech-stack) · [Hackathon node and team](#hackathon-node-and-team) · [Disclosure](#disclosure) · [References](#references)

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
**Illustrative estimate for Penmanshiel.** Assumptions: each kept turbine produces its measured 2019 average (637 kW, a capacity factor of 31.1%); the farm runs with only K of its 14 turbines for 1,000 hours; the wake losses are the modelled ones, for the best choice against an average random choice of the same K turbines; the prices are round numbers of £50, £75 and £100 per MWh, shown in US dollars as $66, $99 and $132 per MWh (1 GBP = 1.3220 USD, from the ECB euro reference rates of 2026-10-09).

| Turbines kept (K of 14) | Modelled power lost to wakes: best vs average random choice | More energy from the same K turbines | Extra energy per 1,000 hours | Value at $66/MWh | Value at $99/MWh | Value at $132/MWh |
|---|---|---|---|---|---|---|
| 5 | 1.0% vs 5.3% | +4.5% | 136 MWh | $9.0k | $13.5k | $18.0k |
| 7 | 4.0% vs 8.0% | +4.3% | 176 MWh | $11.6k | $17.4k | $23.2k |
| 9 | 7.0% vs 10.6% | +4.0% | 207 MWh | $13.7k | $20.5k | $27.3k |

This is an illustrative estimate of scale, not a forecast. It comes from a model, it compares with an average random choice (not with what an operator does today), it assumes 1,000 hours in that configuration (a year has 8,760; how many hours a farm is curtailed is not in our data), and it counts neither costs nor the structure of any contract. Details and sources: [docs/IMPACT.md](https://github.com/agustindiazcano/qwind-qaoa-windfarm/blob/main/docs/IMPACT.md).
<!-- IMPACT:END -->

## Run on real quantum hardware

We also ran the optimized circuit once on **IonQ Forte 1**, a real quantum computer, for a small instance (N = 6 cells, K = 3 turbines, depth p = 1, 997 shots). The circuit compiles to 123 one-qubit and 78 two-qubit gates. The parameters were optimized on the exact simulator, and the hardware was used only to sample the circuit. This was a single run.

| | P(optimal) | P(valid layout) | P(optimal), valid samples only |
|---|---|---|---|
| Ideal (exact) | 0.1784 | 1.0000 | 0.1784 |
| IonQ Forte 1, measured | 0.1304 | 0.7834 | 0.1665 |
| Random choice among valid layouts | 0.1000 | 1.0000 | 0.1000 |

Because the circuit keeps exactly *K* turbines by construction, the 22% of samples that left the valid layouts can be recognized and discarded, and among the valid ones the best layout appears with probability 0.1665, close to the ideal 0.1784 and above the 0.1000 of a random valid choice. The best sampled layout was the exact optimum. Outputs from the simulators and from the quantum computer: [results/backend_probe](https://github.com/agustindiazcano/qwind-qaoa-windfarm/tree/main/results/backend_probe). The original console export of the quantum computer run, as downloaded from Qollab: [agustindiazcano-qwind-output-completed-2026-10-11T03-37-01.138Z.html](https://github.com/agustindiazcano/qwind-qaoa-windfarm/blob/main/results/backend_probe/agustindiazcano-qwind-output-completed-2026-10-11T03-37-01.138Z.html) (a static HTML file; download it and open it in a browser).

## What we built

- A wake-loss model (Jensen, pairwise additive) turned into a QUBO with an exactly-*K* constraint, and a QAOA written by hand in Qiskit with two ways of enforcing the constraint (penalty, or XY mixer + Dicke state).
- A fixed experimental protocol (`qwind-v1`), decided before running and never retuned, run in GitHub Actions on six datasets: synthetic wind roses, the real positions and measured winds of Penmanshiel and Kelmarsh, and two ERA5 wind roses (open licenses for all the real data).
- Controls next to every result: the uniform distribution over valid layouts, random valid sampling with the same 1000 samples, exact enumeration, simulated annealing and greedy search.
- 150+ tests, continuous integration, and tables in this README that are generated from `results/`, so no number is typed by hand.

The experiments are simulated on a CPU, with one small probe on real quantum hardware (see above); the instances are small (at most 14 cells), the wake model is simplified and there is one year of wind data per farm. The limitations are listed below.

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

### More instances: Penmanshiel with every K

The first batch has three values of K for Penmanshiel. To test the result on more instances, we ran the same protocol on the 14 real turbines with every K from 3 to 11. The design was written down before running ([docs/PROTOCOL_EXTENSION.md](https://github.com/agustindiazcano/qwind-qaoa-windfarm/blob/main/docs/PROTOCOL_EXTENSION.md)).

The best sample of the XY mixer + Dicke circuit is the exact optimum for 8 of the 9 values of K, and its probability of sampling the best layout is 1.5 to 14.0 times higher than random valid choice. Random valid choice finds the best layout with probability 0.25 to 1.00, depending on K.

<!-- RESULTS2:START -->
**Datasets** (short name used in the tables below; the full name is the dataset id in `results/`)

| name | dataset | country | what it is | source | instances |
|---|---|---|---|---|---|
| Penmanshiel-allK | `real_penmanshiel_allk` | Scotland, UK | All 14 real Penmanshiel positions with every K from 3 to 11 (9 instances) | [Zenodo](https://doi.org/10.5281/zenodo.16807304), CC BY 4.0 | 9 |

**Constraint-preserving QAOA (XY mixer + Dicke start) against the uniform-over-feasible baseline, depth p = 3**

| dataset | instances | P(optimal) | uniform P(optimal) | approx. ratio (feasible) | uniform ratio | beat uniform ratio | beat uniform P(optimal) | evaluations |
|---|---|---|---|---|---|---|---|---|
| Penmanshiel-allK | 9 | 0.021 | 0.005 | 0.668 | 0.514 | 9/9 | 9/9 | 120 |

**Penalty QAOA (X mixer), all settings of the sweep** (penalty weight 1, 3 and 10 times max|h|, plus one ramp variant; p = 1-3). Range of instances that beat the uniform baseline over settings and depths:

| dataset | instances | settings | beat uniform ratio | beat uniform P(optimal) | P(feasible) range |
|---|---|---|---|---|---|
| Penmanshiel-allK | 9 | 4 | 1-8/9 | 0-1/9 | 0.15-0.43 |

**Final solution quality against the classical methods** (gap to the exact optimum, mean over the instances of each dataset; XY + Dicke at depth p = 3, best layout of its 1000 samples). The budgets are not matched: simulated annealing uses far more objective evaluations than QAOA, and random feasible sampling uses the same 1000 samples as QAOA:

| dataset | SA gap | SA evaluations | greedy gap | XY+Dicke best-sample gap | XY+Dicke found the optimum | random feasible sampling finds the optimum (probability) | XY+Dicke evaluations |
|---|---|---|---|---|---|---|---|
| Penmanshiel-allK | 0.0000 | 5005 | 0.0020 | 0.0020 | 8/9 | 0.57 | 120 |
<!-- RESULTS2:END -->

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
We simulate the full QAOA circuit in Qiskit. `StatevectorEstimator` and `StatevectorSampler` compute the exact expectation values and the exact output distribution on the CPU, so the optimization has no shot noise. We use these primitives for the optimization loop and do not call `backend.run` inside it. We have not benchmarked `backend.run` for this loop. The only runs on a backend are the probe described in "Run on real quantum hardware", which samples the already optimized circuit once.

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
- The experiments are CPU simulations (Qiskit statevector primitives, no noise). Real hardware and noise models were used only for one small probe (N = 6, one run, see "Run on real quantum hardware").
- "Real" means real turbine positions and a measured or reanalysis wind rose, not a validated farm model: the nacelle anemometer sees upwind wakes, there is one year (2019) per farm, and the farm layouts were not designed for this objective.
- Few instances for the real farms (3 each); no statistical claim beyond this benchmark.
- No quantum advantage is claimed.

## Tech Stack

Qiskit 2.5.2, NumPy, SciPy, Python 3.14 (Qollab) / 3.12 (GitHub Actions results). Presentation website (`web/`): plain HTML, CSS and JavaScript, no framework.

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
6. Nigro, L., Sala, S., Amendola, A., Prati, E. "Leveraging Quantum Annealing for Layout Optimization." *Advanced Quantum Technologies* 8(11), e00358 (2025). [doi:10.1002/qute.202500358](https://advanced.onlinelibrary.wiley.com/doi/10.1002/qute.202500358)
7. Kordonowy, S., Leipold, H. "The Lie Algebra of XY-mixer Topologies and Warm Starting QAOA for Constrained Optimization." *npj Quantum Information* 12, 61 (2026). [arXiv:2505.18396](https://arxiv.org/abs/2505.18396)
8. Mancilla, J., Bouloumis, T. D., Goguikian, F. "Constrained Portfolio Optimization via QAOA with XY-Mixers and Trotterized Initialization: A Hybrid Approach for Direct Indexing." [arXiv:2602.14827](https://arxiv.org/abs/2602.14827)

### Data and sources

- Penmanshiel wind farm data (Scotland, UK). Plumley, C., Takeuchi, R.; released by Cubico Sustainable Investments Ltd. Zenodo, CC BY 4.0. [doi:10.5281/zenodo.16807304](https://doi.org/10.5281/zenodo.16807304)
- Kelmarsh wind farm data (England, UK). Plumley, C., Takeuchi, R.; released by Cubico Sustainable Investments Ltd. Zenodo, CC BY 4.0. [doi:10.5281/zenodo.16807551](https://doi.org/10.5281/zenodo.16807551)
- ERA5 hourly data on single levels from 1940 to present. Copernicus Climate Change Service (C3S) Climate Data Store. [dataset page](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels), [doi:10.24381/cds.adbb2d47](https://doi.org/10.24381/cds.adbb2d47)
- Open-Meteo Historical Weather API, used to access ERA5. Zippenfenig, P. (2023). Open-Meteo.com Weather API. [documentation](https://open-meteo.com/en/docs/historical-weather-api), [doi:10.5281/zenodo.7970649](https://doi.org/10.5281/zenodo.7970649)
- UK Government, Contracts for Difference Allocation Round 6, budget notice (administrative strike prices, 2012 prices), used as a price reference in the impact estimate. [PDF](https://assets.publishing.service.gov.uk/media/65e867c162ff48001a87b252/cfd-ar6-budget-notice.pdf)
- European Central Bank, euro foreign exchange reference rates (USD and GBP per euro, 2026-10-09), crossed to convert pounds to US dollars in the impact estimate (1 GBP = 1.3220 USD). [data](https://data-api.ecb.europa.eu/service/data/EXR/D.USD+GBP.EUR.SP00.A?lastNObservations=3&format=csvdata)
- License of the data: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
