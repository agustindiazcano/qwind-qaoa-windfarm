# Wake Model Assumptions

The objective of the QWind optimization is to determine the optimal placement of wind turbines on a grid of candidate cells.

## Wake Loss Approximations
For the QUBO formulation, we assume **pairwise-additive wake losses**. This is an approximation:
- The true physical deficit of multiple overlapping wakes combines non-linearly (e.g., via sum of squares of velocity deficits). Here we use the standard Jensen (1983) / Park model.
- Typical parameter values are used: wake decay constant $k = 0.075$ (standard for onshore wind farms, recommended by WAsP guidelines) and thrust coefficient $C_T = 0.8$ (typical for modern turbines like the NREL 5MW near rated speed).
- To fit the problem into a Quadratic Unconstrained Binary Optimization (QUBO) model, we calculate the pairwise wake loss between any two potential turbine locations `i` and `j` in isolation, and simply sum them up.

## Wind Rose Integration
The model incorporates wind directions and frequencies defined via a wind rose. We discretize the compass into sectors and calculate the expected wake interaction for each pair based on the probability of the wind blowing along the vector connecting them.

## QAOA variants and references
Besides the penalty formulation (|+>^n start, X mixer, penalty weight `lam`), `qollab/qwind/qaoa.py` offers a constraint-preserving variant: a Dicke initial state (uniform over all K-subsets, `StatePreparation`) with an XY mixer on a ring of sites (`RXX`/`RYY` gates in a fixed even/odd order per layer). The ansatz never leaves the K-turbine subspace, so P(feasible) = 1 and the cost Hamiltonian uses `lam = 0`. A linear-ramp (annealing-inspired) parameter initialization is also available.

Verified 2026-10-10 at the level of the arXiv abstract page (title, authors, venue, DOI, date). The full texts were NOT read.

1. Hadfield, S., Wang, Z., O'Gorman, B., Rieffel, E. G., Venturelli, D., Biswas, R. "From the Quantum Approximate Optimization Algorithm to a Quantum Alternating Operator Ansatz." Algorithms 12(2), 34 (2019). DOI: [10.3390/a12020034](https://doi.org/10.3390/a12020034). arXiv: [1709.03489](https://arxiv.org/abs/1709.03489). Introduces mixers that keep the state in the feasible subspace, useful for hard constraints. Not checked against the paper: the exact form of the XY mixer on a ring used here (even/odd order of `RXX`/`RYY` gates); compare with the paper before writing "following Hadfield et al." for that detail.
2. Bartschi, A., Eidenbenz, S. "Deterministic Preparation of Dicke States." 22nd International Symposium on Fundamentals of Computation Theory (FCT 2019), pp. 126-139. DOI: [10.1007/978-3-030-25027-0_9](https://doi.org/10.1007/978-3-030-25027-0_9) (publisher DOI as shown on the arXiv page). arXiv: [1904.07358](https://arxiv.org/abs/1904.07358). Circuit with O(kn) gates and depth O(n). **We do not implement their circuit**: `qaoa.py` uses Qiskit's `StatePreparation` from the amplitude vector. The paper is cited for the definition of the Dicke state and as a reference for an efficient preparation. A shorter-depth variant exists (arXiv:[2207.09998](https://arxiv.org/abs/2207.09998), mention only, not checked).
3. Sack, S. H., Serbyn, M. "Quantum annealing initialization of the quantum approximate optimization algorithm." Quantum 5, 491 (2021). DOI: [10.22331/q-2021-07-01-491](https://doi.org/10.22331/q-2021-07-01-491). arXiv: [2101.05742](https://arxiv.org/abs/2101.05742). That paper studies MaxCut on random graphs. Our linear-ramp initialization is **inspired by** their TQA idea, not a replication; the default `total_time = 0.75 * p` in `run_qaoa` is a placeholder, not a tuned value.
