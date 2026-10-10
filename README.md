# QWind: QAOA for Wind Farm Layout

**Theme:** Quantum Impact · **Status:** Work in Progress (Hackathon, Qollab)

Wind turbines steal wind from each other: every turbine leaves a slower, turbulent "wake" behind it, and any turbine standing in that wake produces less energy. So *where* you place turbines matters.

**QWind** picks the best *K* sites out of *N* candidates, using a quantum algorithm (QAOA, built with Qiskit), and compares it honestly against classical methods.

**Honest expectation:** at the sizes a simulator can handle, classical methods solve this exactly in milliseconds. **We do not claim a quantum advantage.** The goal is to measure how close QAOA gets to the best layout, how that changes with circuit depth, and where it starts to break down.

**Try it:** click **Run your code** on this page (built-in simulator). Source code, tests and experiments: https://github.com/agustindiazcano/qwind-qaoa-windfarm

---

## Results

> ⚠️ **In development.** Results, tables and plots will be added during the hackathon.

---

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
- A wind rose (direction, frequency, speed) weights the losses; power scales with wind speed cubed.
- **Approximation:** losses are pairwise additive. A full multi-wake superposition is not pairwise, so this is a simplification (documented in `docs/model.md`).

### Quantum part
- QAOA with depth *p* = 1, 2, 3: diagonal cost layer plus RX mixer, built in Qiskit.
- The Hamiltonian is built by hand as a `SparsePauliOp` (Ising mapping `x = (1 - Z) / 2`, qubit *i* = bit *i* of the state index).
- Expectation values with `StatevectorEstimator`, classical optimization with `scipy.optimize` (COBYLA) and multiple seeded restarts, final sampling with `StatevectorSampler`.

### Classical baselines
- Exact enumeration (ground truth)
- Simulated annealing
- Greedy search with local swaps

### What we measure
- Gap to the optimal layout
- Probability that QAOA samples the optimal layout
- Probability mass on feasible layouts (exactly *K* turbines)
- Effect of circuit depth (*p* = 1, 2, 3)
- Instance size limits (qubits versus runtime)

### Run environment (Qollab)
- Python 3.14, Qiskit 2.5.2, NumPy, SciPy on the built-in simulator.
- The live Run uses a small instance (up to ~12 qubits). Larger instances are computed offline and their stored results are included.

### Repository layout
```
qollab/        what runs on Qollab (main.py, qwind/ package, small data)
experiments/   full offline runs
results/       results used by this page and the website
tests/         correctness tests (QUBO energy equals brute force, qubit ordering)
docs/          model notes, data sources, project context
web/           presentation website
```

---

## How to run

> ⚠️ **In development.** Click "Run your code" on this page, with the built-in simulator selected. Detailed instructions will be added once the final version is uploaded.

---

## Limitations

- Simplified wake model (pairwise additive losses)
- Small instances only (simulator limit)
- Simulation only; no real quantum hardware execution

---

## Tech Stack

- Qiskit 2.5.2
- NumPy
- SciPy
- Python 3.14

---

## Hackathon node

Competing at the **UNICEN** node (Universidad Nacional del Centro de la Provincia de Buenos Aires, Argentina): https://exa.unicen.edu.ar/

Track: *Professional*

## Team Salta

- Agustin Diaz-Cano
- Baltazar Salerno

---

## Disclosure

- Built during the official hackathon window.
- AI tools used: Claude Code (coding agent, planning, code and documentation assistance), Gemini Antigravity (planning, coding agent and brainstorming, web search), Grok (brainstorming, web search).
- Libraries: Qiskit, NumPy, SciPy.
- Wind data: *(source and license, to be completed)*

---

## Acknowledgments

This effort is supported by Qollab & IonQ