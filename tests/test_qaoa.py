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


def test_baselines_are_reported():
    """Uniform and random-feasible-sampling baselines next to the QAOA values."""
    Q, n = make_instance((3, 2), K=3)
    shots = 50
    res = run_qaoa(Q, n, 3, p=1, restarts=1, maxiter=20, shots=shots, seed=0)
    table = energy_table(Q, n)
    n_opt = int(np.isclose(table, table.min()).sum())
    assert res.shots == shots
    assert res.uniform_p_optimal == pytest.approx(n_opt / 2 ** n)
    assert res.uniform_p_feasible == pytest.approx(comb(n, 3) / 2 ** n)

    feas = np.array([bin(i).count("1") == 3 for i in range(2 ** n)])
    ef = table[feas]
    n_opt_f = int(np.isclose(ef, ef.min()).sum())
    assert res.random_p_hit == pytest.approx(1 - (1 - n_opt_f / comb(n, 3)) ** shots)
    assert res.random_best_gap >= 0.0

    # Feasible-only ratios: conditional mean over feasible states vs uniform over feasible states
    uniform_f = (ef.max() - ef.mean()) / (ef.max() - ef.min())
    assert res.uniform_approx_ratio_feasible == pytest.approx(uniform_f)
    cond = (res.probabilities[feas] @ ef) / res.probabilities[feas].sum()
    assert res.approx_ratio_feasible == pytest.approx((ef.max() - cond) / (ef.max() - ef.min()))
    assert 0.0 <= res.approx_ratio_feasible <= 1.0
    uniform_all = (table.max() - table.mean()) / (table.max() - table.min())
    assert res.uniform_approx_ratio == pytest.approx(uniform_all)


def _without_timings(text):
    return "\n".join(line.rsplit("|", 1)[0] if "|" in line else line for line in text.splitlines())


def test_main_output_table_labels_and_determinism(capsys):
    import main
    main.main(n_cells=6, K=3, p=1)
    first = capsys.readouterr().out
    assert first.count("Method") == 1
    assert "QAOA p=1 (best of 1000 shots)" in first
    assert "P(optimal)" in first and "uniform" in first.lower() and "random" in first.lower()
    assert "finished at" not in first
    main.main(n_cells=6, K=3, p=1)
    second = capsys.readouterr().out
    # Only the wall-clock Time column may differ between runs with the same seed
    assert _without_timings(first) == _without_timings(second)


def test_main_refuses_large_instances(capsys):
    import main
    main.main(n_cells=16)
    out = capsys.readouterr().out
    assert "limited" in out
    assert "Method" not in out
