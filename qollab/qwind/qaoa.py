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
    shots: int
    # Secondary: ratio over ALL 2^n bitstrings (inflated by absurd, heavily penalized states)
    uniform_approx_ratio: float
    # Primary: ratio over FEASIBLE states only (E_min/E_max over bitstrings with exactly K ones,
    # <E> conditioned on feasibility)
    approx_ratio_feasible: float
    uniform_approx_ratio_feasible: float
    # Uniform-distribution baselines
    uniform_p_optimal: float           # (#optimal bitstrings) / 2^n
    uniform_p_feasible: float          # C(N, K) / 2^n
    # Random-sampling baseline: `shots` random feasible K-subsets
    random_p_hit: float                # probability that they contain an optimal feasible bitstring
    random_best_gap: float             # best gap of one seeded draw of `shots` random feasible subsets


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

    n_feasible = int(feasible.sum())
    ef = table[feasible]
    ef_min, ef_max = float(ef.min()), float(ef.max())
    p_feas = float(probs[feasible].sum())
    cond_expectation = float(probs[feasible] @ ef) / p_feas if p_feas > 0 else float("nan")

    def ratio(e, lo, hi):
        return 1.0 if hi == lo else (hi - e) / (hi - lo)

    n_opt_feasible = int(np.isclose(ef, ef_min).sum())
    draws = np.random.default_rng(seed + 1).choice(ef, size=shots, replace=True)

    return QAOAResult(
        params=theta,
        expectation=expectation,
        approx_ratio=ratio(expectation, e_min, e_max),
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
        shots=shots,
        uniform_approx_ratio=ratio(float(table.mean()), e_min, e_max),
        approx_ratio_feasible=ratio(cond_expectation, ef_min, ef_max),
        uniform_approx_ratio_feasible=ratio(float(ef.mean()), ef_min, ef_max),
        uniform_p_optimal=float(optimal.sum()) / 2 ** n,
        uniform_p_feasible=n_feasible / 2 ** n,
        random_p_hit=1.0 - (1.0 - n_opt_feasible / n_feasible) ** shots,
        random_best_gap=float(draws.min() - e_min),
    )
