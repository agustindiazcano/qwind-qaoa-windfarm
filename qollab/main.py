import time
from datetime import datetime
import numpy as np
from qwind.wake import generate_h_J
from qwind.qubo import build_qubo, qubo_energy
from qwind.classical import exact_enumeration, simulated_annealing, greedy_local_search

def main(n_cells=8, K=3, seed=0):
    """
    Main entry point for Qollab platform.
    Runs a small instance and compares classical methods.
    """
    total_start = time.perf_counter()
    print(f"--- QWind QAOA Benchmark ---")
    print(f"Instance: N={n_cells} cells, K={K} turbines, seed={seed}")
    
    np.random.seed(seed)
    # Simple (4, 2) grid for N=8
    grid_shape = (n_cells // 2, 2)
    wind_rose = [(0, 0.2), (90, 0.5), (180, 0.1), (270, 0.2)]
    
    h, J = generate_h_J(grid_shape, spacing_D=5.0, wind_rose=wind_rose, P0=1.0)
    lam = np.abs(h).max() * 10
    Q = build_qubo(h, J, lam, K)
    
    methods = [
        ("Exact Enum", lambda: exact_enumeration(Q, n_cells)),
        ("Sim. Anneal", lambda: simulated_annealing(Q, n_cells, K, num_reads=5)),
        ("Greedy LS", lambda: greedy_local_search(Q, n_cells, K))
    ]
    
    results = {}
    best_energy = float('inf')
    
    for name, func in methods:
        start_t = time.time()
        x, energy = func()
        duration = time.time() - start_t
        results[name] = {"energy": energy, "time": duration}
        if name == "Exact Enum":
            best_energy = energy
            
    # Print table
    print(f"{'Method':<15} | {'Energy':<10} | {'Gap':<10} | {'Time (s)'}")
    print("-" * 55)
    for name, res in results.items():
        gap = res["energy"] - best_energy
        print(f"{name:<15} | {res['energy']:<10.4f} | {gap:<10.4f} | {res['time']:.4f}")

    print(f"QWind QAOA Benchmark finished at {datetime.now():%Y-%m-%d %H:%M:%S}")
    print(f"Total time:{time.perf_counter() - total_start:.2f} s")

if __name__ == "__main__":
    main()
