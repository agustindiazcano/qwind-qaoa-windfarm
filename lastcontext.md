# Last Context
- Branch `feat/core-model` was created to implement the core QWind mechanics.
- Wrote TDD tests in `tests/test_core.py` targeting QUBO vs brute-force energy, Hamiltonian diagonal mapping, and feasibility of heuristic/exact solvers.
- Implemented `qollab/qwind/wake.py` (basic dummy generator), `qubo.py` (QUBO dict & Hamiltonian builder), and `classical.py` (exact enum, greedy local search, simulated annealing).
- Documented wake model assumptions in `docs/model.md` as required.
- All tests are passing green.
