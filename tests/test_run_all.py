import csv
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "experiments")))
import run_all  # noqa: E402
from qwind.instances import InstanceSpec  # noqa: E402
from test_results_schema import validate_per_instance, validate_summary  # noqa: E402

TINY = dict(run_all.QUICK_PROTOCOL, depths=[1], maxiter=8, restarts=1, shots=50)
SPECS = [InstanceSpec(dataset="synthetic", instance_id=0, wind_rose="A", N=6, K=3, seed=0)]


def _strip_time(rows):
    return [{k: v for k, v in r.items() if k != "time_s"} for r in rows]


def test_protocol_is_fixed_before_running_real_data():
    proto = run_all.FULL_PROTOCOL
    assert proto["id"] == "qwind-v1"
    assert proto["depths"] == [1, 2, 3]
    assert proto["lam_multipliers"] == [1.0, 3.0, 10.0]
    assert proto["restarts"] == 2 and proto["maxiter"] == 60 and proto["shots"] == 1000
    assert proto["ramp_total_time_factor"] == 0.75
    assert [v["name"] for v in run_all.variants(proto)] == [
        "penalty+x lam=1", "penalty+x lam=3", "penalty+x lam=10",
        "penalty+x lam=10 ramp", "xy+dicke", "xy+dicke ramp"]


def test_rows_follow_schema_and_are_reproducible():
    rows = run_all.run_instance(SPECS[0], TINY)
    methods = [r["method"] for r in rows]
    assert methods.count("exact") == methods.count("sa") == methods.count("greedy") == 1
    assert methods.count("qaoa") == len(run_all.variants(TINY)) * len(TINY["depths"])
    assert all(r["dataset"] == "synthetic" for r in rows)
    exact = next(r for r in rows if r["method"] == "exact")
    assert exact["energy_gap"] == pytest.approx(0.0)
    assert all(r["energy_gap"] >= -1e-9 for r in rows)
    again = run_all.run_instance(SPECS[0], TINY)
    assert _strip_time(rows) == _strip_time(again)


def test_write_outputs_validate(tmp_path):
    rows = run_all.run_all(SPECS, TINY, jobs=1)
    run_all.write_outputs(str(tmp_path), SPECS, TINY, rows)
    with open(tmp_path / "per_instance.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        data = list(reader)
        assert validate_per_instance(data, reader.fieldnames) == []
    summary = json.loads((tmp_path / "summary.json").read_text(encoding="utf-8"))
    assert validate_summary(summary) == []
    assert summary["status"] == "smoke"
    qaoa = [r for r in summary["results"] if r["method"] == "qaoa"]
    assert {r["variant"] for r in qaoa} == {v["name"] for v in run_all.variants(TINY)}
    assert all(r["baselines"]["uniform_feasible_ratio"] > 0 for r in qaoa)


def test_parallel_run_matches_serial():
    specs = SPECS + [InstanceSpec(dataset="synthetic", instance_id=1, wind_rose="B", N=6, K=2, seed=1)]
    tiny = dict(TINY, maxiter=4)
    serial = run_all.run_all(specs, tiny, jobs=1)
    parallel = run_all.run_all(specs, tiny, jobs=2)
    assert _strip_time(serial) == _strip_time(parallel)
