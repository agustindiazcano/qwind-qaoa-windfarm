# Wake Model Assumptions

The objective of the QWind optimization is to determine the optimal placement of wind turbines on a grid of candidate cells.

## Wake Loss Approximations
For the QUBO formulation, we assume **pairwise-additive wake losses**. This is an approximation:
- The true physical deficit of multiple overlapping wakes combines non-linearly (e.g., via sum of squares of velocity deficits). Here we use the standard Jensen (1983) / Park model.
- Typical parameter values are used: wake decay constant $k = 0.075$ (standard for onshore wind farms, recommended by WAsP guidelines) and thrust coefficient $C_T = 0.8$ (typical for modern turbines like the NREL 5MW near rated speed).
- To fit the problem into a Quadratic Unconstrained Binary Optimization (QUBO) model, we calculate the pairwise wake loss between any two potential turbine locations `i` and `j` in isolation, and simply sum them up.

## Wind Rose Integration
The model incorporates wind directions and frequencies defined via a wind rose. We discretize the compass into sectors and calculate the expected wake interaction for each pair based on the probability of the wind blowing along the vector connecting them.
