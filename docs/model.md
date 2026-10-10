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

- Constraint-preserving mixers: Hadfield et al., "From the Quantum Approximate Optimization Algorithm to a Quantum Alternating Operator Ansatz", Algorithms 12(2), 34 (2019). **To verify** (title, venue, year) before citing.
- Linear-ramp / annealing-inspired initialization (TQA): Sack and Serbyn, "Quantum annealing initialization of the quantum approximate optimization algorithm", Quantum 5, 491 (2021). **To verify** before citing. The default `total_time = 0.75 * p` in `run_qaoa` is a placeholder, not a tuned value.
- Dicke states: the exact preparation circuit (Baertschi and Eidenbenz, 2019) is not used; `StatePreparation` is used instead for simplicity. **To verify** the reference if it is cited.
