# QWind: QAOA for Wind Farm Layout

**Theme:** Quantum Impact

**Status:** Work in Progress (Hackathon, Qollab)

---

## What it does

Each wind turbine steals wind from the ones behind it (the "wake effect").
Given a set of candidate sites, **QWind** selects the *K* sites that lose the least energy to wakes using a quantum algorithm (QAOA, built with Qiskit) and compares the results against classical methods.

---

## The problem

Choosing *K* turbine sites out of *N* candidates is a combinatorial optimization problem.
We encode the wake losses as a **QUBO**, solve it with **QAOA** on a simulator, and benchmark it against:

- Exact enumeration
- Simulated annealing
- Greedy search

---

## What we measure

- Gap to the optimal layout
- Probability that QAOA samples the optimal layout
- Effect of circuit depth (*p* = 1, 2, 3)
- Instance size limits

---

## Honest expectation

At the current instance sizes, classical methods are expected to solve the problem exactly in milliseconds.
**We do not claim a quantum advantage.**
The goal is to measure how close QAOA gets to the optimum and where it starts to break down.

---

## How to run

> ⚠️ **In development.** Click "Run your code" on this page. Detailed instructions will be added once the Run environment is fully working.

---

## Results

> ⚠️ **In development.** Results, tables and plots will be added during the hackathon.

---

## Limitations

- Simplified wake model (pairwise additive losses)
- Small instances only (simulator limit)
- No real quantum hardware execution

---

## Tech Stack

- Qiskit
- NumPy
- (other libraries to be listed)

---

## Team Salta

- Agustin Diaz-Cano
- Baltazar Salerno

---

## Disclosure

- Built during the official hackathon window.
- AI tools used: Claude (code and documentation assistance).
- Libraries: Qiskit, NumPy.
- Wind data: *(source and license, to be completed)*

---

## Acknowledgments

This effort is supported by Qollab & IonQ
