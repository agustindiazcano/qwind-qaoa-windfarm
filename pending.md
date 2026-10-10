# Pending Tasks
1. [x] Implement `tests/test_core.py` and core modules in `qollab/qwind/` (`wake.py`, `qubo.py`, `classical.py`).
2. [x] Restructure layout, adjust `main.py`, and prepare for Qollab deployment.
3. [x] Add a dedicated runtime requirements file for Qollab and enforce it with a test.
4. [x] Fix the failing GitHub Actions workflows (ci.yml, pages.yml).
5. [x] Implement QAOA in `qollab/qwind/qaoa.py` and integrate it into `main.py` (PR open on `feat/qaoa`, awaiting human review).
6. [ ] Draft `docs/results_schema.md` and create an example `results/summary.json` (to enable parallel frontend work).
7. [ ] Run the uploaded `qollab/` folder in Qollab for real (built-in simulator) and check the table prints once.
8. [ ] `experiments/run_all.py`: QAOA p = 1, 2, 3 on larger instances (restarts/maxiter/shots exposed as arguments of `run_qaoa`).
9. [ ] Decide how to improve QAOA beyond uniform sampling (tune lam, try p = 3, CVaR objective, XY mixer) and record results in `results/`.
