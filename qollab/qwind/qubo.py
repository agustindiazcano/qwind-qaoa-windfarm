import numpy as np
from qiskit.quantum_info import SparsePauliOp

def build_qubo(h, J, lam, K):
    """
    Build QUBO representation from h, J, lam, K.
    E(x) = sum_i h_i x_i + sum_{i<j} J_ij x_i x_j + lam * (sum_i x_i - K)^2
    
    Returns a dictionary with keys as tuples of indices:
    - (i, i) for linear terms
    - (i, j) for quadratic terms (i < j)
    - () for the constant offset
    """
    N = len(h)
    Q = {}
    
    # Constant offset from the penalty term: lam * K^2
    Q[()] = lam * (K**2)
    
    # Linear terms: h_i + lam * (1 - 2K)
    for i in range(N):
        Q[(i, i)] = h[i] + lam * (1 - 2 * K)
        
    # Quadratic terms: J_ij + 2 * lam
    for i in range(N):
        for j in range(i + 1, N):
            val = J[i, j] + 2 * lam
            if val != 0:
                Q[(i, j)] = val
                
    return Q

def qubo_energy(x, Q):
    """Evaluate the QUBO energy for a given binary vector x."""
    E = Q.get((), 0.0)
    N = len(x)
    for i in range(N):
        if (i, i) in Q:
            E += Q[(i, i)] * x[i]
        for j in range(i + 1, N):
            if (i, j) in Q:
                E += Q[(i, j)] * x[i] * x[j]
    return E

def build_hamiltonian(Q, num_qubits):
    """
    Convert a QUBO into an Ising Hamiltonian using SparsePauliOp.
    Mapping: x_i = (1 - Z_i) / 2
    
    Returns:
    - SparsePauliOp object representing the Hamiltonian.
    - float offset.
    """
    offset = Q.get((), 0.0)
    
    # We will collect Pauli terms
    # Each term is a string like 'IIZII' and a coefficient
    paulis = []
    coeffs = []
    
    for key, weight in Q.items():
        if not key:
            continue
        i, j = key
        if i == j:
            # Linear term: w_i * x_i = w_i * (1 - Z_i) / 2 = w_i/2 - (w_i/2) Z_i
            offset += weight / 2
            
            # Construct Pauli string with Z at position i
            # Qiskit uses little-endian, so qubit 0 is the rightmost character in the string.
            pauli_list = ['I'] * num_qubits
            pauli_list[i] = 'Z'
            pauli_str = "".join(reversed(pauli_list))
            
            paulis.append(pauli_str)
            coeffs.append(-weight / 2)
            
        elif i < j:
            # Quadratic term: w_ij * x_i * x_j = w_ij * (1 - Z_i) * (1 - Z_j) / 4
            # = w_ij/4 - w_ij/4 Z_i - w_ij/4 Z_j + w_ij/4 Z_i Z_j
            offset += weight / 4
            
            # - Z_i term
            p_list_i = ['I'] * num_qubits
            p_list_i[i] = 'Z'
            paulis.append("".join(reversed(p_list_i)))
            coeffs.append(-weight / 4)
            
            # - Z_j term
            p_list_j = ['I'] * num_qubits
            p_list_j[j] = 'Z'
            paulis.append("".join(reversed(p_list_j)))
            coeffs.append(-weight / 4)
            
            # + Z_i Z_j term
            p_list_ij = ['I'] * num_qubits
            p_list_ij[i] = 'Z'
            p_list_ij[j] = 'Z'
            paulis.append("".join(reversed(p_list_ij)))
            coeffs.append(weight / 4)
            
    # Remove zero coefficients and sum up duplicate Pauli strings
    term_dict = {}
    for p, c in zip(paulis, coeffs):
        term_dict[p] = term_dict.get(p, 0.0) + c
        
    final_paulis = []
    final_coeffs = []
    for p, c in term_dict.items():
        if abs(c) > 1e-10:
            final_paulis.append(p)
            final_coeffs.append(c)
            
    if not final_paulis:
        # If all terms cancel out, add identity
        final_paulis.append('I' * num_qubits)
        final_coeffs.append(0.0)
        
    hamiltonian = SparsePauliOp(final_paulis, final_coeffs)
    return hamiltonian, offset
