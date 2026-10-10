import time
from datetime import datetime
import numpy as np
from qwind.wake import generate_h_J
from qwind.qubo import build_qubo
from qwind.classical import exact_enumeration, simulated_annealing, greedy_local_search
from qwind.qaoa import run_qaoa

MAX_LIVE_CELLS = 14


def main(n_cells=8, K=3, p=2, seed=0):
    """
    Main entry point for Qollab platform (called by the platform after running this file).
    Runs a small instance and compares classical methods against QAOA at depth p.
    """
    print("--- QWind: classical baselines vs QAOA ---")
    print(f"Instance: N={n_cells} cells, K={K} turbines, QAOA depth p={p}, seed={seed}")

    if n_cells > MAX_LIVE_CELLS:
        print(f"The live Run is limited to small instances (N <= {MAX_LIVE_CELLS} cells). "
              "Larger instances are computed offline.")
        return

    np.random.seed(seed)
    # Simple (N/2, 2) grid
    grid_shape = (n_cells // 2, 2)
    wind_rose = [(0, 0.2), (90, 0.5), (180, 0.1), (270, 0.2)]

    h, J = generate_h_J(grid_shape, spacing_D=5.0, wind_rose=wind_rose, P0=1.0)
    lam = np.abs(h).max() * 10
    Q = build_qubo(h, J, lam, K)

    results = {}
    best_energy = float('inf')

    methods = [
        ("Exact Enum", lambda: exact_enumeration(Q, n_cells)),
        ("Sim. Anneal", lambda: simulated_annealing(Q, n_cells, K, num_reads=5)),
        ("Greedy LS", lambda: greedy_local_search(Q, n_cells, K)),
    ]
    for name, func in methods:
        start_t = time.perf_counter()
        x, energy = func()
        results[name] = {"energy": energy, "time": time.perf_counter() - start_t}
        if name == "Exact Enum":
            best_energy = energy

    qaoa = run_qaoa(Q, n_cells, K, p=p, seed=seed)
    # Best sampled bitstring, comparable to the single solution returned by the classical methods
    results[f"QAOA p={p}"] = {"energy": qaoa.best_sampled_energy, "time": qaoa.wall_time}

    print(f"{'Method':<15} | {'Energy':<10} | {'Gap':<10} | {'Time (s)'}")
    print("-" * 55)
    for name, res in results.items():
        gap = res["energy"] - best_energy
        if abs(gap) < 1e-12:
            gap = 0.0  # avoid printing -0.0000
        print(f"{name:<15} | {res['energy']:<10.4f} | {gap:<10.4f} | {res['time']:.4f}")

    gap_feasible = qaoa.best_sampled_feasible_gap
    print()
    print(f"QAOA p={p} detail (energy = best of {sum(qaoa.counts.values())} sampled bitstrings)")
    print(f"  Approximation ratio : {qaoa.approx_ratio:.4f}")
    print(f"  P(optimal)          : {qaoa.p_optimal:.4f}")
    print(f"  P(feasible)         : {qaoa.p_feasible:.4f}")
    print(f"  Best feasible gap   : {'none sampled' if gap_feasible is None else f'{gap_feasible:.4f}'}")
    print(f"  Function evaluations: {qaoa.nfev}")
    print(f"QWind benchmark finished at {datetime.now():%Y-%m-%d %H:%M:%S}")
