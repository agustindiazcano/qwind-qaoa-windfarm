import numpy as np
import pytest
from qiskit.quantum_info import SparsePauliOp

from qollab.qwind.wake import generate_h_J
from qollab.qwind.qubo import build_qubo, qubo_energy, build_hamiltonian
from qollab.qwind.classical import exact_enumeration, simulated_annealing, greedy_local_search

def test_qubo_energy_vs_brute_force():
    """1. QUBO energy equals brute-force energy on a 12-cell, K=4 instance."""
    N = 12
    K = 4
    np.random.seed(42)
    h, J = generate_h_J(N)
    lam = np.abs(h).max() * 10  # Penalization factor
    
    Q = build_qubo(h, J, lam, K)
    
    # Generate a random state x
    x = np.random.randint(0, 2, N)
    
    # Calculate energy using brute force formula
    brute_force_E = sum(h[i] * x[i] for i in range(N))
    for i in range(N):
        for j in range(i + 1, N):
            brute_force_E += J[i, j] * x[i] * x[j]
    brute_force_E += lam * (sum(x) - K)**2
    
    qubo_E = qubo_energy(x, Q)
    
    np.testing.assert_allclose(qubo_E, brute_force_E)

def test_hamiltonian_diagonal():
    """2. Diagonal of the Hamiltonian (plus offset) equals the QUBO energy table."""
    N = 5  # Use a smaller N for full table comparison to keep it fast
    K = 2
    np.random.seed(42)
    h, J = generate_h_J(N)
    lam = 100.0
    
    Q = build_qubo(h, J, lam, K)
    hamiltonian, offset = build_hamiltonian(Q, N)
    
    # Qiskit uses little-endian, so |00001> corresponds to x_0=1
    # We construct the diagonal of the Hamiltonian
    matrix = hamiltonian.to_matrix()
    diagonal = np.real(np.diag(matrix))
    
    # Check every basis state
    for i in range(2**N):
        # Convert index i to binary array x using little-endian
        binary_str = format(i, f'0{N}b')
        # Format gives big-endian representation (e.g., if N=3, i=1 -> '001')
        # Little-endian means x[0] is the least significant bit
        x = np.array([int(bit) for bit in reversed(binary_str)])
        
        expected_E = qubo_energy(x, Q)
        actual_E = diagonal[i] + offset
        np.testing.assert_allclose(actual_E, expected_E)

def test_exact_enumeration_feasible():
    """3. The enumeration optimum is feasible (exactly K turbines)."""
    N = 8
    K = 3
    np.random.seed(42)
    h, J = generate_h_J(N)
    lam = 100.0
    
    Q = build_qubo(h, J, lam, K)
    best_x, best_E = exact_enumeration(Q, N)
    
    assert sum(best_x) == K

def test_heuristics_feasible_and_bounded():
    """4. SA and greedy return feasible solutions and never beat the exact optimum."""
    N = 8
    K = 3
    np.random.seed(42)
    h, J = generate_h_J(N)
    lam = 100.0
    
    Q = build_qubo(h, J, lam, K)
    exact_x, exact_E = exact_enumeration(Q, N)
    
    sa_x, sa_E = simulated_annealing(Q, N, K, num_reads=10)
    greedy_x, greedy_E = greedy_local_search(Q, N, K)
    
    # Check feasibility
    assert sum(sa_x) == K
    assert sum(greedy_x) == K
    
    # Check bound (heuristics should have energy >= exact minimum)
    assert sa_E >= exact_E - 1e-9
    assert greedy_E >= exact_E - 1e-9
