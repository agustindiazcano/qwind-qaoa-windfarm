import time
from dataclasses import dataclass

import numpy as np
from scipy.optimize import minimize
from qiskit import QuantumCircuit
from math import comb

from qiskit.circuit import ParameterVector
from qiskit.circuit.library import StatePreparation
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


def dicke_amplitudes(num_qubits, K):
    """Uniform superposition over all bitstrings with exactly K ones (index i <-> x_q = (i >> q) & 1)."""
    amps = np.zeros(2 ** num_qubits)
    ones = np.array([bin(i).count("1") for i in range(2 ** num_qubits)]) == K
    amps[ones] = 1.0 / np.sqrt(comb(num_qubits, K))
    return amps


def _xy_groups(n):
    """
    Ring pairs (i, i+1 mod n) split into groups of qubit-disjoint pairs: even pairs (0,1),(2,3)...,
    odd pairs (1,2),(3,4)..., and the wrap-around pair (n-1, 0), which joins the odd group when n is
    even and forms a third group when n is odd.
    """
    even = [(i, i + 1) for i in range(0, n - 1, 2)]
    odd = [(i, i + 1) for i in range(1, n - 1, 2)]
    groups = [even, odd]
    if n > 2:
        if n % 2 == 0:
            odd.append((n - 1, 0))
        else:
            groups.append([(n - 1, 0)])
    return [g for g in groups if g]


def build_qaoa_circuit(hamiltonian, p, mixer="x", init="plus", K=None, include_init=True):
    """
    QAOA circuit: initial state, then p layers of cost exp(-i gamma H) and a mixer.
    The cost layer is built by hand from the Z terms of the SparsePauliOp (identity terms are a
    global phase).

    mixer="x"  : exp(-i beta sum_i X_i) via RX(2 beta).
    mixer="xy" : exp(-i beta (XX + YY)) on each pair of a ring of sites via RXX(2 beta) RYY(2 beta),
                 which conserves the number of ones. The ring terms do not all commute, so each layer
                 applies the groups in the same fixed order: even pairs, odd pairs (plus the wrap
                 pair; a third group when n is odd). Within a group the pairs are qubit-disjoint.
    init="plus" : |+>^n.
    init="dicke": uniform superposition over all K-subsets (needs K), via StatePreparation.
    include_init=False omits the initial-state gates (the caller starts from the state itself).

    Returns (circuit, ParameterVector) with parameters ordered [gamma_1..gamma_p, beta_1..beta_p].
    """
    if mixer not in ("x", "xy"):
        raise ValueError(f"unknown mixer {mixer!r}")
    if init not in ("plus", "dicke"):
        raise ValueError(f"unknown init {init!r}")
    n = hamiltonian.num_qubits
    params = ParameterVector("t", 2 * p)
    gammas, betas = params[:p], params[p:]
    qc = QuantumCircuit(n)
    if init == "dicke" and K is None:
        raise ValueError("init='dicke' needs K")
    if include_init:
        if init == "plus":
            qc.h(range(n))
        else:
            qc.append(StatePreparation(dicke_amplitudes(n, K)), range(n))
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
        if mixer == "x":
            qc.rx(2 * betas[layer], range(n))
        else:
            for group in _xy_groups(n):
                for i, j in group:
                    qc.rxx(2 * betas[layer], i, j)
                    qc.ryy(2 * betas[layer], i, j)
    return qc, params


def ramp_init(p, scale, total_time):
    """
    Linear-ramp (annealing-inspired) initial angles: gamma ramps up and beta ramps down.
    With dt = total_time / p and s_l = (l + 1/2) / p: gamma_l = s_l * dt / scale, beta_l = (1 - s_l) * dt.
    `scale` is the largest Hamiltonian coefficient, so total_time is dimensionless.
    Idea after Sack & Serbyn (2021), see docs/model.md (reference to verify).
    """
    s = (np.arange(p) + 0.5) / p
    dt = total_time / p
    return s * dt / scale, (1.0 - s) * dt


def run_qaoa(Q, num_cells, K, p=2, restarts=2, maxiter=60, shots=1000, seed=0,
             mixer="x", init="plus", init_params="random", total_time=None, cost_Q=None):
    """
    Optimize a depth-p QAOA with COBYLA (seeded restarts), then compute the exact output
    distribution and sample it. Keeps the best restart.

    Q is the reference QUBO used for every reported metric. cost_Q (default Q) is the QUBO whose
    Hamiltonian goes into the circuit: pass a lam = 0 QUBO when the ansatz enforces the constraint
    (mixer="xy", init="dicke").
    init_params="random": uniform random starts. "ramp": restart 0 is the linear ramp (see
    ramp_init, total_time defaults to 0.75 * p), later restarts add seeded Gaussian jitter.
    """
    if init_params not in ("random", "ramp"):
        raise ValueError(f"unknown init_params {init_params!r}")
    t0 = time.perf_counter()
    n = num_cells
    H, offset = build_hamiltonian(Q if cost_Q is None else cost_Q, n)
    table = energy_table(Q, n)
    e_min, e_max = float(table.min()), float(table.max())

    circuit, params = build_qaoa_circuit(H, p, mixer=mixer, init=init, K=K)
    estimator = StatevectorEstimator()

    if init == "dicke":
        # StatePreparation is re-synthesized on every evaluation (~10x slower), so the optimization
        # loop starts from the Dicke statevector and evolves only the QAOA layers. The full circuit
        # (with StatePreparation) is still used for sampling.
        layers, _ = build_qaoa_circuit(H, p, mixer=mixer, init=init, K=K, include_init=False)
        start = Statevector(dicke_amplitudes(n, K))

        def final_state(theta):
            return start.evolve(layers.assign_parameters(theta))

        def objective(theta):
            return float(final_state(theta).expectation_value(H).real)
    else:
        def final_state(theta):
            return Statevector(circuit.assign_parameters(theta))

        def objective(theta):
            return float(estimator.run([(circuit, H, theta)]).result()[0].data.evs)

    # Angles are scaled by the largest Hamiltonian coefficient so the random starts are sensible
    scale = float(np.max(np.abs(H.coeffs)))
    rng = np.random.default_rng(seed)
    best = None
    nfev = 0
    for r in range(restarts):
        if init_params == "ramp":
            gam, bet = ramp_init(p, scale, 0.75 * p if total_time is None else total_time)
            x0 = np.concatenate([gam, bet])
            if r > 0:
                x0 = x0 + rng.normal(0.0, 0.1, 2 * p)
        else:
            x0 = np.concatenate([rng.uniform(0, np.pi, p) / scale, rng.uniform(0, np.pi / 2, p)])
        res = minimize(objective, x0, method="COBYLA", options={"maxiter": maxiter, "rhobeg": 0.3})
        nfev += int(res.nfev)
        if best is None or res.fun < best.fun:
            best = res
    theta = np.asarray(best.x, dtype=float)

    bound = circuit.assign_parameters(theta)
    probs = final_state(theta).probabilities()
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
