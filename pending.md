# Pending Tasks
1. [x] Implement `tests/test_core.py` and core modules in `qollab/qwind/` (`wake.py`, `qubo.py`, `classical.py`).
2. [x] Restructure layout, adjust `main.py`, and prepare for Qollab deployment.
3. [x] Add a dedicated runtime requirements file for Qollab and enforce it with a test.
4. [x] Fix the failing GitHub Actions workflows (ci.yml, pages.yml).
5. [x] Implement QAOA in `qollab/qwind/qaoa.py` and integrate it into `main.py` (PR open on `feat/qaoa`, awaiting human review).
6. [~] `docs/results_schema.md` is written and enforced by `tests/test_results_schema.py` (PR open on `docs/results-schema`). The example `results/summary.json` comes from the `run_all.py --quick` smoke run in the next PR (`feat/run-all`).
7. [ ] Run the uploaded `qollab/` folder in Qollab for real (built-in simulator) and check the table prints once.
8. [ ] `experiments/run_all.py`: QAOA p = 1, 2, 3 on larger instances (restarts/maxiter/shots exposed as arguments of `run_qaoa`).
9. [x] Compare QAOA variants (lam sweep, p = 3, ramp init, XY + Dicke). Result: XY + Dicke beats uniform-over-feasible in every instance; penalty + X mixer does not do so reliably (see `results/qaoa_variants_summary.csv`). PR open on `feat/qaoa-xy`, awaiting human review.
10. [ ] Decide whether the live Run defaults of `main.py` should switch to xy + dicke (not changed yet; needs a human decision) and re-check the Qollab runtime with the Dicke state.
11. [ ] Verify the Hadfield et al. (2019) and Sack and Serbyn (2021) references in `docs/model.md` before citing; the ramp total time 0.75 p is a placeholder.
