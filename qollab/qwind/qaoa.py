import time
from dataclasses import dataclass

import numpy as np
from scipy.optimize import minimize
from qiskit import QuantumCircuit
from qiskit.circuit import ParameterVector
from qiskit.primitives import StatevectorEstimator, StatevectorSampler
from qiskit.quantum_info import Statevector

from qwind.qubo import build_hamiltonian


@dataclass
class QAOAResult:
    params: np.ndarray                 # optimal [gamma_1..gamma_p, beta_1..beta_p]
    expectation: float                 # <E> of the optimized circuit (offset included)
    approx_ratio: float                # (E_max - <E>) / (E_max - E_min)
    p_optimal: float                   # probability mass on the exact optimal bitstring(s)
    p_feasible: float                  # probability mass on states with exactly K ones
    best_sampled_energy: float         # lowest QUBO energy among the sampled bitstrings
    best_sampled_feasible_gap: object  # best feasible sampled energy - exact optimum (None if no feasible sample)
    nfev: int                          # objective evaluations over all restarts
    wall_time: float                   # seconds
    probabilities: np.ndarray          # exact output distribution, index i <-> x_q = (i >> q) & 1
    counts: dict                       # sampled bitstrings (Qiskit big-endian strings) -> counts
    e_min: float
    e_max: float


def energy_table(Q, num_qubits):
    """QUBO energy of all 2^n bitstrings. Index i encodes x_q = (i >> q) & 1 (Qiskit little-endian)."""
    idx = np.arange(2 ** num_qubits)
    x = (idx[:, None] >> np.arange(num_qubits)) & 1
    E = np.full(2 ** num_qubits, Q.get((), 0.0), dtype=float)
    for key, w in Q.items():
        if not key:
            continue
        i, j = key
        E += w * (x[:, i] if i == j else x[:, i] * x[:, j])
    return E


def build_qaoa_circuit(hamiltonian, p):
    """
    QAOA circuit: |+>^n, then p layers of cost exp(-i gamma H) and mixer exp(-i beta sum X).
    Built by hand from the Z terms of the SparsePauliOp (identity terms are a global phase).
    Returns (circuit, ParameterVector) with parameters ordered [gamma_1..gamma_p, beta_1..beta_p].
    """
    n = hamiltonian.num_qubits
    params = ParameterVector("t", 2 * p)
    gammas, betas = params[:p], params[p:]
    qc = QuantumCircuit(n)
    qc.h(range(n))
    for layer in range(p):
        for pauli, coeff in zip(hamiltonian.paulis, hamiltonian.coeffs):
            qubits = [q for q in range(n) if pauli.z[q]]
            angle = 2 * float(coeff.real) * gammas[layer]
            if len(qubits) == 1:
                qc.rz(angle, qubits[0])
            elif len(qubits) == 2:
                qc.rzz(angle, qubits[0], qubits[1])
            elif len(qubits) > 2:
                raise ValueError("QAOA circuit supports only 1- and 2-body Z terms")
        qc.rx(2 * betas[layer], range(n))
    return qc, params


def run_qaoa(Q, num_cells, K, p=2, restarts=2, maxiter=60, shots=1000, seed=0):
    """
    Optimize a depth-p QAOA for the QUBO Q with COBYLA (random restarts, fixed seed), then
    compute the exact output distribution and sample it. Keeps the best restart.
    """
    t0 = time.perf_counter()
    n = num_cells
    H, offset = build_hamiltonian(Q, n)
    table = energy_table(Q, n)
    e_min, e_max = float(table.min()), float(table.max())

    circuit, params = build_qaoa_circuit(H, p)
    estimator = StatevectorEstimator()

    def objective(theta):
        return float(estimator.run([(circuit, H, theta)]).result()[0].data.evs)

    # Angles are scaled by the largest Hamiltonian coefficient so the random starts are sensible
    scale = float(np.max(np.abs(H.coeffs)))
    rng = np.random.default_rng(seed)
    best = None
    nfev = 0
    for _ in range(restarts):
        x0 = np.concatenate([rng.uniform(0, np.pi, p) / scale, rng.uniform(0, np.pi / 2, p)])
        res = minimize(objective, x0, method="COBYLA", options={"maxiter": maxiter, "rhobeg": 0.3})
        nfev += int(res.nfev)
        if best is None or res.fun < best.fun:
            best = res
    theta = np.asarray(best.x, dtype=float)

    bound = circuit.assign_parameters(theta)
    probs = Statevector(bound).probabilities()
    expectation = float(probs @ table)

    measured = bound.copy()
    measured.measure_all()
    sampler = StatevectorSampler(default_shots=shots, seed=seed)
    counts = sampler.run([measured]).result()[0].data.meas.get_counts()

    popcount = np.array([bin(i).count("1") for i in range(2 ** n)])
    feasible = popcount == K
    optimal = np.isclose(table, e_min)
    sampled_idx = np.array([int(b, 2) for b in counts])
    sampled_feasible = sampled_idx[feasible[sampled_idx]]
    gap = float(table[sampled_feasible].min() - e_min) if sampled_feasible.size else None

    return QAOAResult(
        params=theta,
        expectation=expectation,
        approx_ratio=1.0 if e_max == e_min else (e_max - expectation) / (e_max - e_min),
        p_optimal=float(probs[optimal].sum()),
        p_feasible=float(probs[feasible].sum()),
        best_sampled_energy=float(table[sampled_idx].min()),
        best_sampled_feasible_gap=gap,
        nfev=nfev,
        wall_time=time.perf_counter() - t0,
        probabilities=probs,
        counts=dict(counts),
        e_min=e_min,
        e_max=e_max,
    )
