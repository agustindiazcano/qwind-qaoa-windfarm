import numpy as np
from itertools import combinations
from qwind.qubo import qubo_energy

def exact_enumeration(Q, num_cells):
    """
    Evaluate all 2^N states (or all feasible states) to find the global optimum.
    To ensure we find the true QUBO minimum, we evaluate all 2^N states.
    """
    best_E = float('inf')
    best_x = None
    
    for i in range(2**num_cells):
        binary_str = format(i, f'0{num_cells}b')
        x = np.array([int(bit) for bit in reversed(binary_str)])
        E = qubo_energy(x, Q)
        if E < best_E:
            best_E = E
            best_x = x
            
    return best_x, best_E

def greedy_local_search(Q, num_cells, K, max_iter=1000):
    """
    Greedy local search using 1-opt swaps (maintaining feasibility K).
    """
    rng = np.random.RandomState(42)
    # Start with a random feasible solution
    x = np.zeros(num_cells, dtype=int)
    ones_indices = rng.choice(num_cells, K, replace=False)
    x[ones_indices] = 1
    
    current_E = qubo_energy(x, Q)
    
    for _ in range(max_iter):
        best_swap = None
        best_E = current_E
        
        # Evaluate all possible swaps between a 1 and a 0
        ones = np.where(x == 1)[0]
        zeros = np.where(x == 0)[0]
        
        for o in ones:
            for z in zeros:
                # Test swap
                x_test = x.copy()
                x_test[o] = 0
                x_test[z] = 1
                
                E_test = qubo_energy(x_test, Q)
                if E_test < best_E:
                    best_E = E_test
                    best_swap = (o, z)
                    
        if best_swap is None:
            # Local minimum reached
            break
            
        # Apply best swap
        o, z = best_swap
        x[o] = 0
        x[z] = 1
        current_E = best_E
        
    return x, current_E

def simulated_annealing(Q, num_cells, K, num_reads=10, initial_temp=10.0, cooling_rate=0.99, max_steps=1000):
    """
    Simulated annealing using K-preserving swaps to ensure feasibility.
    """
    rng = np.random.RandomState(42)
    
    global_best_x = None
    global_best_E = float('inf')
    
    for read in range(num_reads):
        x = np.zeros(num_cells, dtype=int)
        ones_indices = rng.choice(num_cells, K, replace=False)
        x[ones_indices] = 1
        
        current_E = qubo_energy(x, Q)
        best_x = x.copy()
        best_E = current_E
        
        T = initial_temp
        
        for step in range(max_steps):
            ones = np.where(x == 1)[0]
            zeros = np.where(x == 0)[0]
            
            o = rng.choice(ones)
            z = rng.choice(zeros)
            
            x_test = x.copy()
            x_test[o] = 0
            x_test[z] = 1
            
            E_test = qubo_energy(x_test, Q)
            delta = E_test - current_E
            
            if delta < 0 or rng.rand() < np.exp(-delta / T):
                x = x_test
                current_E = E_test
                if current_E < best_E:
                    best_E = current_E
                    best_x = x.copy()
            
            T *= cooling_rate
            
        if best_E < global_best_E:
            global_best_E = best_E
            global_best_x = best_x
            
    return global_best_x, global_best_E
