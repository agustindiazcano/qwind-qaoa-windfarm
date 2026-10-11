import math
import os
import subprocess
import sys

import numpy as np
import pytest

from qwind.probe import format_report, run_probe

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture(scope="module")
def result():
    # no backend given: the probe falls back to Qiskit's basic simulator, which is noiseless
    return run_probe(n_cells=6, K=3, p=1, shots=4000, seed=0)


def test_counts_add_up_to_the_shots(result):
    assert sum(result["counts"].values()) == result["shots"] == 4000
    assert all(len(b) == 6 and set(b) <= {"0", "1"} for b in result["counts"])


def test_a_noiseless_backend_keeps_every_sample_valid(result):
    """XY mixer + Dicke start never leaves the K-turbine subspace, so every measured bitstring has exactly K ones."""
    assert result["measured_p_feasible"] == pytest.approx(1.0)
    assert all(b.count("1") == 3 for b in result["counts"])


def test_measured_distribution_matches_the_exact_one(result):
    """The sampled circuit must reproduce the exact statevector distribution (checks qubit order and the circuit)."""
    probs, shots = result["ideal_probabilities"], result["shots"]
    measured = np.zeros_like(probs)
    for bits, c in result["counts"].items():
        measured[int(bits, 2)] += c / shots                       # big-endian string <-> little-endian index
    assert 0.5 * np.abs(measured - probs).sum() < 0.06            # total variation distance, 4000 shots, 20 valid states
    sigma = math.sqrt(result["ideal_p_optimal"] * (1 - result["ideal_p_optimal"]) / shots)
    assert abs(result["measured_p_optimal"] - result["ideal_p_optimal"]) < 5 * sigma + 1e-9


def test_reports_the_baselines_and_the_compiled_size(result):
    assert 0 < result["uniform_p_optimal"] < result["ideal_p_optimal"] <= 1
    assert result["two_qubit_gates"] > 0 and result["depth"] > 0 and result["one_qubit_gates"] >= 0
    assert result["best_sampled_gap"] >= -1e-9


def test_report_text_has_the_numbers_a_person_needs(result):
    text = format_report(result, "basic simulator")
    for must in ("basic simulator", "P(optimal)", "P(feasible)", "two-qubit gates", "shots", "ideal", "measured"):
        assert must in text


def test_the_probe_project_runs_as_a_script_without_a_backend(tmp_path):
    """scripts/make_probe_project.py assembles the folder to upload to a separate Qollab test project."""
    out = tmp_path / "probe_project"
    subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "make_probe_project.py"), "--out", str(out)], check=True)
    assert (out / "main.py").exists() and (out / "qwind" / "probe.py").exists() and (out / "requirements.txt").exists()
    done = subprocess.run([sys.executable, str(out / "main.py")], capture_output=True, text=True, timeout=120, cwd=str(out))
    assert done.returncode == 0, done.stderr
    assert "P(optimal)" in done.stdout and "two-qubit gates" in done.stdout


def test_the_live_run_never_imports_the_probe():
    src = open(os.path.join(ROOT, "qollab", "main.py"), encoding="utf-8").read()
    assert "probe" not in src


def test_postselected_and_valid_baselines_are_reported(result):
    """Noise can leave the valid subspace; the fair baseline is the uniform distribution over VALID layouts."""
    n_opt = round(result["uniform_p_optimal"] * 2 ** 6)
    assert result["uniform_valid_p_optimal"] == pytest.approx(n_opt / math.comb(6, 3))
    assert result["postselected_p_optimal"] == pytest.approx(result["measured_p_optimal"] / result["measured_p_feasible"])
    assert result["ideal_postselected_p_optimal"] == pytest.approx(result["ideal_p_optimal"] / result["ideal_p_feasible"])
    assert result["postselected_p_optimal"] > result["uniform_valid_p_optimal"]


def test_report_shows_the_postselected_numbers(result):
    text = format_report(result)
    assert "valid samples only" in text and "uniform over valid layouts" in text
