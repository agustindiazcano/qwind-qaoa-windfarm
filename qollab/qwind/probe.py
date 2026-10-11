"""
Backend probe: run the OPTIMIZED constraint-preserving QAOA circuit once on a backend and compare what it measures with the
exact (ideal) distribution. Intended for a separate Qollab test project, in this order: the free built-in simulator (the circuit
compiles), a free IonQ noise-model simulator (a realistic preview and the shot count), then, only if the price quoted by the
runner is acceptable, a quantum computer. The live Run (qollab/main.py) never imports this module.

The parameters are optimized on the exact statevector (never on the backend): one backend call, not a loop.
Uses only qiskit, numpy and scipy (through the rest of qwind) and the standard library.
"""
import numpy as np
from qiskit import transpile

from qwind.qaoa import build_qaoa_circuit, energy_table, run_qaoa
from qwind.qubo import build_hamiltonian, build_qubo
from qwind.wake import generate_h_J

WIND_ROSE = [(0, 0.2), (90, 0.5), (180, 0.1), (270, 0.2)]     # same instance family as the live Run


def _default_backend():
    from qiskit.providers.basic_provider import BasicSimulator
    return BasicSimulator()


def _backend_name(backend):
    name = getattr(backend, "name", None)
    if callable(name):
        name = name()
    return str(name or backend)


def _gate_stats(circuit):
    one = two = 0
    for inst in circuit.data:
        if inst.operation.name in ("measure", "barrier"):
            continue
        if len(inst.qubits) == 1:
            one += 1
        elif len(inst.qubits) == 2:
            two += 1
    return one, two, circuit.depth()


def run_probe(n_cells=6, K=3, p=1, shots=1000, seed=0, backend=None, restarts=2, maxiter=60):
    """Optimize on the exact statevector, then sample the circuit once on `backend` (default: Qiskit's noiseless basic simulator)."""
    grid_shape = (n_cells // 2, 2)
    h, J = generate_h_J(grid_shape, spacing_D=5.0, wind_rose=WIND_ROSE, P0=1.0)
    Q = build_qubo(h, J, np.abs(h).max() * 10, K)            # reference QUBO for every metric
    cost_Q = build_qubo(h, J, 0.0, K)                         # the ansatz enforces the constraint: no penalty in the circuit
    res = run_qaoa(Q, n_cells, K, p=p, restarts=restarts, maxiter=maxiter, shots=1000, seed=seed,
                   mixer="xy", init="dicke", cost_Q=cost_Q)

    H, _ = build_hamiltonian(cost_Q, n_cells)
    circuit, _ = build_qaoa_circuit(H, p, mixer="xy", init="dicke", K=K)
    bound = circuit.assign_parameters(res.params)
    bound.measure_all()
    backend = backend if backend is not None else _default_backend()
    compiled = transpile(bound, backend)
    one_q, two_q, depth = _gate_stats(compiled)

    counts = {str(k).replace(" ", ""): float(v) for k, v in backend.run(compiled, shots=shots).result().get_counts().items()}
    total = sum(counts.values())
    table = energy_table(Q, n_cells)
    optimal = np.isclose(table, table.min())
    p_opt = sum(c for b, c in counts.items() if optimal[int(b, 2)]) / total      # big-endian string <-> little-endian index
    p_feas = sum(c for b, c in counts.items() if b.count("1") == K) / total
    best_gap = min(table[int(b, 2)] for b in counts) - float(table.min())
    return {
        "backend": _backend_name(backend), "n_cells": n_cells, "K": K, "p": p, "shots": int(round(total)),
        "counts": {b: int(round(c)) for b, c in counts.items()},
        "measured_p_optimal": p_opt, "measured_p_feasible": p_feas, "best_sampled_gap": float(best_gap),
        "ideal_p_optimal": float(res.p_optimal), "ideal_p_feasible": float(res.p_feasible),
        "uniform_p_optimal": float(res.uniform_p_optimal), "uniform_p_feasible": float(res.uniform_p_feasible),
        "ideal_probabilities": res.probabilities, "one_qubit_gates": one_q, "two_qubit_gates": two_q, "depth": depth,
    }


def format_report(r, label=None):
    """Plain text for the console and for results/ (every number in the README must come from a file)."""
    label = label or r["backend"]
    rows = [
        ("", "ideal (exact)", "measured", "uniform"),
        ("P(optimal)", f"{r['ideal_p_optimal']:.4f}", f"{r['measured_p_optimal']:.4f}", f"{r['uniform_p_optimal']:.4f}"),
        ("P(feasible)", f"{r['ideal_p_feasible']:.4f}", f"{r['measured_p_feasible']:.4f}", f"{r['uniform_p_feasible']:.4f}"),
    ]
    lines = [f"--- Backend probe: {label} ---",
             f"N = {r['n_cells']} cells, K = {r['K']} turbines, QAOA depth p = {r['p']} (XY mixer + Dicke start), {r['shots']} shots",
             f"compiled circuit: {r['one_qubit_gates']} one-qubit gates, {r['two_qubit_gates']} two-qubit gates, depth {r['depth']}", ""]
    lines += [f"{a:<14}{b:>16}{c:>12}{d:>10}" for a, b, c, d in rows]
    lines += ["", f"best sampled layout: gap {r['best_sampled_gap']:.4f} to the exact optimum"]
    return "\n".join(lines)
