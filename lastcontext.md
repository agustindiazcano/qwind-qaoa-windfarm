# Last Context
- Branch `feat/qaoa` (from up-to-date `main`): implemented QAOA in `qollab/qwind/qaoa.py` (hand-built circuit from the `SparsePauliOp`, `StatevectorEstimator` + COBYLA with restarts, exact distribution + `StatevectorSampler`, result object with approximation ratio, P(optimal), P(feasible), feasible gap, nfev, wall time).
- `qollab/main.py`: `main(n_cells=8, K=3, p=2, seed=0)` now runs exact, SA, greedy and QAOA, prints one comparison table plus a QAOA detail block, and refuses `n_cells > 14` with a clear message. Default run takes ~6.5 s locally.
- Double-execution bug (module-level `main()` call) was already fixed and merged in PR #12; this branch also removes the whole-run `Total time` print (Qollab shows it).
- Tests: `tests/test_qaoa.py` (Estimator vs statevector, qubit ordering with asymmetric P0, p=1 beats uniform baseline, reproducibility, main output). Qubit-ordering mutation (reversed bit order) was verified to fail, then reverted.
- `.pyc` files are untracked and ignored (PR #13 merged).
