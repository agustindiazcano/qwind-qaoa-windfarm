# Wake Model Assumptions

The objective of the QWind optimization is to determine the optimal placement of wind turbines on a grid of candidate cells.

## Wake Loss Approximations
For the QUBO formulation, we assume **pairwise-additive wake losses**. This is an approximation:
- The true physical deficit (e.g. using the Jensen or Park models) of multiple overlapping wakes combines non-linearly (typically via sum of squares of velocity deficits).
- To fit the problem into a Quadratic Unconstrained Binary Optimization (QUBO) model, we calculate the pairwise wake loss between any two potential turbine locations `i` and `j` in isolation, and simply sum them up.

## Wind Rose Integration
The model incorporates wind directions and frequencies defined via a wind rose. We discretize the compass into sectors and calculate the expected wake interaction for each pair based on the probability of the wind blowing along the vector connecting them.
