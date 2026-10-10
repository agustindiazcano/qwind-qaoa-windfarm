import numpy as np

def generate_h_J(num_cells, spacing=5.0, P0=1.0):
    """
    Generate linear terms h and quadratic terms J for the QUBO formulation.
    
    h_i = -P0 (isolated-turbine power)
    J_ij = pairwise wake loss between sites i and j.
    
    For now, uses a simplified randomized wake model to fulfill tests.
    A full Jensen/Park deficit model with wind rose integration will be
    implemented for actual instances.
    """
    h = -P0 * np.ones(num_cells)
    
    # Generate pairwise wake losses (positive penalty for interference)
    J = np.zeros((num_cells, num_cells))
    
    # We use a deterministic pseudo-random symmetric matrix for tests
    rng = np.random.RandomState(42)
    for i in range(num_cells):
        for j in range(i + 1, num_cells):
            # Wake loss is some positive value
            loss = rng.uniform(0.01, 0.2) * P0
            J[i, j] = loss
            J[j, i] = loss
            
    return h, J
