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
    h, J = generate_h_J((4, 3))
    lam = np.abs(h).max() * 10
    
    Q = build_qubo(h, J, lam, K)
    
    rng = np.random.RandomState(42)
    x = rng.randint(0, 2, N)
    
    brute_force_E = sum(h[i] * x[i] for i in range(N))
    for i in range(N):
        for j in range(i + 1, N):
            brute_force_E += J[i, j] * x[i] * x[j]
    brute_force_E += lam * (sum(x) - K)**2
    
    qubo_E = qubo_energy(x, Q)
    np.testing.assert_allclose(qubo_E, brute_force_E)

def test_hamiltonian_diagonal():
    """2. Diagonal of the Hamiltonian (plus offset) equals the QUBO energy table.
    Checks that qubit i corresponds to bit i (little-endian) in an asymmetric instance.
    """
    N = 6
    K = 2
    # Wind rose heavily biased to one direction
    wind_rose = [(45, 1.0)] 
    # Use asymmetric P0 so linear terms are distinct per site
    P0_asym = np.linspace(1.0, 2.0, N)
    h, J = generate_h_J(grid_shape=(2, 3), wind_rose=wind_rose, P0=P0_asym)
    
    # Ensure h is asymmetric
    assert len(set(h)) == N, "Linear terms must be distinct to robustly test qubit ordering"
    
    lam = 100.0
    Q = build_qubo(h, J, lam, K)
    hamiltonian, offset = build_hamiltonian(Q, N)
    
    matrix = hamiltonian.to_matrix()
    diagonal = np.real(np.diag(matrix))
    
    for i in range(2**N):
        # Qiskit uses little-endian: index i in binary matches basis state |x_{N-1}...x_1 x_0>
        # e.g. i=1 -> |00...01> -> x_0 = 1, x_1 = 0...
        binary_str = format(i, f'0{N}b')
        x = np.array([int(bit) for bit in reversed(binary_str)])
        
        expected_E = qubo_energy(x, Q)
        actual_E = diagonal[i] + offset
        np.testing.assert_allclose(actual_E, expected_E, err_msg=f"Failed for state {x} (index {i})")

def test_exact_enumeration_feasible():
    """3. The enumeration optimum is feasible (exactly K turbines)."""
    N = 6
    K = 2
    h, J = generate_h_J((2, 3))
    lam = 100.0
    
    Q = build_qubo(h, J, lam, K)
    best_x, best_E = exact_enumeration(Q, N)
    
    assert sum(best_x) == K
    
    # Verify it's actually the minimum among feasible states
    for i in range(2**N):
        binary_str = format(i, f'0{N}b')
        x = np.array([int(bit) for bit in reversed(binary_str)])
        if sum(x) == K:
            E = qubo_energy(x, Q)
            assert best_E <= E + 1e-9

def test_heuristics_feasible_and_bounded():
    """4. SA and greedy return feasible solutions and never beat the exact optimum."""
    N = 12
    K = 4
    h, J = generate_h_J((4, 3))
    lam = 100.0
    
    Q = build_qubo(h, J, lam, K)
    exact_x, exact_E = exact_enumeration(Q, N)
    
    sa_x, sa_E = simulated_annealing(Q, N, K, num_reads=5)
    greedy_x, greedy_E = greedy_local_search(Q, N, K)
    
    assert sum(sa_x) == K
    assert sum(greedy_x) == K
    
    assert sa_E >= exact_E - 1e-9, f"SA {sa_E} beat exact {exact_E}"
    assert greedy_E >= exact_E - 1e-9, f"Greedy {greedy_E} beat exact {exact_E}"
