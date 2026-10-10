import time
import numpy as np
from qwind.wake import generate_h_J
from qwind.qubo import build_qubo
from qwind.classical import exact_enumeration, simulated_annealing, greedy_local_search
from qwind.qaoa import run_qaoa

RECOMMENDED_LIVE_CELLS = 12  # recommended maximum for the live Run
MAX_LIVE_CELLS = 14          # hard limit: larger instances are computed offline


def main(n_cells=8, K=3, p=2, seed=0, mixer="x", init="plus", init_params="random"):
    """
    Main entry point for Qollab platform (called by the platform after running this file).
    Runs a small instance and compares classical methods against QAOA at depth p.
    mixer ("x" | "xy"), init ("plus" | "dicke") and init_params ("random" | "ramp") select QAOA
    variants; the defaults are the penalty QAOA. mixer="xy" with init="dicke" enforces the
    cardinality constraint in the ansatz and drops the penalty from the circuit.
    """
    print("--- QWind: classical baselines vs QAOA ---")
    print(f"Instance: N={n_cells} cells, K={K} turbines, QAOA depth p={p}, seed={seed}")

    if n_cells > MAX_LIVE_CELLS:
        print(f"The live Run is limited to small instances: up to {RECOMMENDED_LIVE_CELLS} cells recommended, "
              f"hard limit {MAX_LIVE_CELLS}. Larger instances are computed offline.")
        return
    if n_cells > RECOMMENDED_LIVE_CELLS:
        print(f"Note: N > {RECOMMENDED_LIVE_CELLS} cells is above the recommended live-Run size; this may take longer.")

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

    # The penalty-free cost Hamiltonian is only used when the ansatz itself enforces the constraint
    cost_Q = build_qubo(h, J, 0.0, K) if (mixer == "xy" and init == "dicke") else None
    qaoa = run_qaoa(Q, n_cells, K, p=p, seed=seed, mixer=mixer, init=init,
                    init_params=init_params, cost_Q=cost_Q)
    # Best sampled bitstring, comparable to the single solution returned by the classical methods
    variant = "" if (mixer, init, init_params) == ("x", "plus", "random") else f" {mixer}+{init}+{init_params}"
    label = f"QAOA p={p}{variant} (best of {qaoa.shots} shots)"
    results[label] = {"energy": qaoa.best_sampled_energy, "time": qaoa.wall_time}

    width = max(len(name) for name in results)
    print(f"{'Method':<{width}} | {'Energy':<10} | {'Gap':<10} | {'Time (s)'}")
    print("-" * (width + 38))
    for name, res in results.items():
        gap = res["energy"] - best_energy
        if abs(gap) < 1e-12:
            gap = 0.0  # avoid printing -0.0000
        print(f"{name:<{width}} | {res['energy']:<10.4f} | {gap:<10.4f} | {res['time']:.4f}")

    def fmt_gap(g):
        return "n/a" if g is None else f"{g:.4f}"

    print()
    print(f"QAOA p={p} detail vs baselines ({qaoa.nfev} optimizer evaluations, {qaoa.shots} shots)")
    print(f"  {'':<28}{'QAOA':>10}{'Uniform':>10}")
    print(f"  {'P(optimal)':<28}{qaoa.p_optimal:>10.4f}{qaoa.uniform_p_optimal:>10.4f}")
    print(f"  {'P(feasible)':<28}{qaoa.p_feasible:>10.4f}{qaoa.uniform_p_feasible:>10.4f}")
    print(f"  {'Approx. ratio (feasible)':<28}{qaoa.approx_ratio_feasible:>10.4f}{qaoa.uniform_approx_ratio_feasible:>10.4f}")
    print(f"  {'Approx. ratio (all, 2nd)':<28}{qaoa.approx_ratio:>10.4f}{qaoa.uniform_approx_ratio:>10.4f}")
    print(f"  Best feasible sampled gap   : QAOA {fmt_gap(qaoa.best_sampled_feasible_gap)}"
          f" | random feasible subsets {fmt_gap(qaoa.random_best_gap)}")
    print(f"  P(optimum in {qaoa.shots} draws): QAOA sampling "
          f"{1.0 - (1.0 - qaoa.p_optimal) ** qaoa.shots:.4f} | random feasible subsets {qaoa.random_p_hit:.4f}")
