import numpy as np
import pytest
from math import comb
from qiskit.primitives import StatevectorEstimator
from qiskit.quantum_info import Statevector

from qwind.wake import generate_h_J
from qwind.qubo import build_qubo, qubo_energy, build_hamiltonian
from qwind.qaoa import build_qaoa_circuit, energy_table, run_qaoa


def make_instance(grid_shape, K, asymmetric=True):
    """Small QUBO. Asymmetric per-site P0 makes every qubit distinguishable."""
    n = grid_shape[0] * grid_shape[1]
    P0 = np.linspace(1.0, 2.0, n) if asymmetric else 1.0
    h, J = generate_h_J(grid_shape, wind_rose=[(0, 0.6), (90, 0.4)], P0=P0)
    lam = np.abs(h).max() * 10
    return build_qubo(h, J, lam, K), n


@pytest.mark.parametrize("p", [1, 2])
def test_estimator_matches_statevector_expectation(p):
    """1. Estimator expectation == sum(probabilities * QUBO energy table), random params."""
    Q, n = make_instance((3, 2), K=3)
    H, offset = build_hamiltonian(Q, n)
    table = energy_table(Q, n)
    circuit, params = build_qaoa_circuit(H, p)
    assert len(params) == 2 * p

    rng = np.random.default_rng(123)
    for _ in range(3):
        theta = rng.uniform(-1.0, 1.0, 2 * p)
        evs = StatevectorEstimator().run([(circuit, H, theta)]).result()[0].data.evs
        probs = Statevector(circuit.assign_parameters(theta)).probabilities()
        np.testing.assert_allclose(float(evs) + offset, probs @ table, atol=1e-9)


def test_qubit_ordering_matches_qubo_table():
    """2. Probability-vector index i maps to bitstring x_q = (i >> q) & 1 (Qiskit little-endian)."""
    Q, n = make_instance((4, 2), K=3)
    H, offset = build_hamiltonian(Q, n)
    table = energy_table(Q, n)
    for i in range(2 ** n):
        x = [(i >> q) & 1 for q in range(n)]
        e_ref = qubo_energy(x, Q)  # independent of energy_table
        assert table[i] == pytest.approx(e_ref)
        e_ham = Statevector.from_int(i, 2 ** n).expectation_value(H).real + offset
        assert e_ham == pytest.approx(e_ref)
    # The asymmetric instance must not be bit-reversal symmetric, or the test proves nothing.
    assert not np.allclose(table, table[[int(format(i, f"0{n}b")[::-1], 2) for i in range(2 ** n)]])


def test_p1_beats_uniform_baseline():
    """3. After optimization (p=1) optimum probability and feasible mass beat the uniform distribution."""
    Q, n = make_instance((3, 2), K=3)
    res = run_qaoa(Q, n, K=3, p=1, restarts=2, maxiter=60, shots=200, seed=0)
    assert res.p_optimal > 1 / 2 ** n
    assert res.p_feasible > comb(n, 3) / 2 ** n
    assert 0.0 <= res.approx_ratio <= 1.0
    assert res.nfev > 0 and res.wall_time > 0


def test_same_seed_is_reproducible():
    """4. Same seed gives identical results."""
    Q, n = make_instance((3, 2), K=3)
    kwargs = dict(p=1, restarts=2, maxiter=30, shots=200, seed=7)
    a = run_qaoa(Q, n, 3, **kwargs)
    b = run_qaoa(Q, n, 3, **kwargs)
    np.testing.assert_array_equal(a.params, b.params)
    assert a.expectation == b.expectation
    assert a.counts == b.counts
    assert a.best_sampled_feasible_gap == b.best_sampled_feasible_gap


def test_result_fields_are_consistent():
    Q, n = make_instance((3, 2), K=3)
    res = run_qaoa(Q, n, 3, p=1, restarts=1, maxiter=20, shots=100, seed=1)
    table = energy_table(Q, n)
    assert res.expectation == pytest.approx(res.probabilities @ table)
    assert res.probabilities.sum() == pytest.approx(1.0)
    assert sum(res.counts.values()) == 100
    assert res.best_sampled_feasible_gap is None or res.best_sampled_feasible_gap >= -1e-9


def test_main_prints_one_table_with_qaoa_row(capsys):
    import main
    main.main(n_cells=6, K=3, p=1)
    out = capsys.readouterr().out
    assert out.count("Method") == 1
    assert "QAOA" in out
    assert "P(optimal)" in out


def test_main_refuses_large_instances(capsys):
    import main
    main.main(n_cells=16)
    out = capsys.readouterr().out
    assert "limited" in out
    assert "Method" not in out
