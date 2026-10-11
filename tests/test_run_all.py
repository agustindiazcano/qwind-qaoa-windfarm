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


@pytest.mark.heavy
def test_parallel_run_matches_serial():
    specs = SPECS + [InstanceSpec(dataset="synthetic", instance_id=1, wind_rose="B", N=6, K=2, seed=1)]
    tiny = dict(TINY, maxiter=4)
    serial = run_all.run_all(specs, tiny, jobs=1)
    parallel = run_all.run_all(specs, tiny, jobs=2)
    assert _strip_time(serial) == _strip_time(parallel)


# --- one folder per dataset and merge into the single results/summary.json the website reads ---

@pytest.fixture(scope="module")
def two_dataset_dirs(tmp_path_factory):
    """Tiny runs (N = 6, p = 1, 4 evaluations) of the synthetic set and of the real Chubut rose, one folder each."""
    base = tmp_path_factory.mktemp("results")
    tiny = dict(TINY, maxiter=4)
    real = [InstanceSpec("real_chubut", 0, "chubut", 6, 2, 0)]
    for specs in (SPECS, real):
        rows = run_all.run_all(specs, tiny, jobs=1)
        run_all.write_outputs(run_all.dataset_dir(str(base), specs[0].dataset), specs, tiny, rows)
    return base


def test_dataset_dir_layout():
    assert run_all.dataset_dir("results", "real_chubut") == os.path.join("results", "real_chubut")


def test_each_dataset_writes_its_own_folder(two_dataset_dirs):
    for ds in ("synthetic", "real_chubut"):
        assert (two_dataset_dirs / ds / "per_instance.csv").exists()
        assert (two_dataset_dirs / ds / "summary.json").exists()
    summary = json.loads((two_dataset_dirs / "real_chubut" / "summary.json").read_text(encoding="utf-8"))
    assert validate_summary(summary) == []
    assert [d["dataset"] for d in summary["datasets"]] == ["real_chubut"]
    assert {r["dataset"] for r in summary["results"]} == {"real_chubut"}


def test_merge_builds_single_summary_and_csv(two_dataset_dirs):
    out = two_dataset_dirs / "merged"
    run_all.merge_results(str(two_dataset_dirs), str(out))
    summary = json.loads((out / "summary.json").read_text(encoding="utf-8"))
    assert validate_summary(summary) == []
    assert [d["dataset"] for d in summary["datasets"]] == ["real_chubut", "synthetic"]   # sorted, deterministic
    assert summary["status"] == "smoke"
    assert {r["dataset"] for r in summary["results"]} == {"synthetic", "real_chubut"}
    with open(out / "per_instance.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    assert validate_per_instance(rows, reader.fieldnames) == []
    assert {r["dataset"] for r in rows} == {"synthetic", "real_chubut"}


def test_merge_into_base_folder_is_idempotent(two_dataset_dirs):
    """Merging into the base folder itself must ignore a previous merged summary and loose files."""
    (two_dataset_dirs / "qaoa_variants_summary.csv").write_text("x\n", encoding="utf-8")
    run_all.merge_results(str(two_dataset_dirs), str(two_dataset_dirs))
    first = (two_dataset_dirs / "summary.json").read_text(encoding="utf-8")
    run_all.merge_results(str(two_dataset_dirs), str(two_dataset_dirs))
    assert (two_dataset_dirs / "summary.json").read_text(encoding="utf-8") == first
    assert [d["dataset"] for d in json.loads(first)["datasets"]] == ["real_chubut", "synthetic"]


def test_merge_rejects_different_protocols(two_dataset_dirs, tmp_path):
    for ds in ("synthetic", "real_chubut"):
        (tmp_path / ds).mkdir()
        s = json.loads((two_dataset_dirs / ds / "summary.json").read_text(encoding="utf-8"))
        if ds == "real_chubut":
            s["protocol"]["maxiter"] += 1
        (tmp_path / ds / "summary.json").write_text(json.dumps(s), encoding="utf-8")
        (tmp_path / ds / "per_instance.csv").write_text(
            (two_dataset_dirs / ds / "per_instance.csv").read_text(encoding="utf-8"), encoding="utf-8")
    with pytest.raises(ValueError, match="protocol"):
        run_all.merge_results(str(tmp_path), str(tmp_path / "out"))


def test_merge_without_datasets_fails(tmp_path):
    with pytest.raises(ValueError, match="no dataset"):
        run_all.merge_results(str(tmp_path), str(tmp_path))


def test_real_instance_specs_use_only_the_a_rose_pairs():
    """Documented choice: the real sets reuse the (N, K) pairs and seeds of the synthetic A-rose instances."""
    specs = run_all.real_instance_specs("real_chubut", "chubut")
    synth_a = [s for s in run_all.synthetic_instance_specs() if s.wind_rose == "A"]
    assert len(specs) == len(synth_a) == 8
    assert [(s.N, s.K, s.seed) for s in specs] == [(s.N, s.K, s.seed) for s in synth_a]
    assert {s.dataset for s in specs} == {"real_chubut"} and {s.wind_rose for s in specs} == {"chubut"}


def test_site_defaults_from_dataset_name():
    assert run_all.site_from_dataset("real_bahia_blanca") == "bahia_blanca"
    with pytest.raises(ValueError):
        run_all.site_from_dataset("synthetic")


# --- real farms: the candidate cells are the real turbine positions ---

FARMS_PATH = os.path.join(os.path.dirname(__file__), "..", "qollab", "data", "farms.json")


def test_farm_instance_specs_are_fixed_before_running():
    pen = run_all.specs_for_dataset("real_penmanshiel")
    kel = run_all.specs_for_dataset("real_kelmarsh")
    assert [(s.N, s.K) for s in pen] == [(14, 5), (14, 7), (14, 9)]
    assert [(s.N, s.K) for s in kel] == [(6, 2), (6, 3), (6, 4)]
    assert {s.wind_rose for s in pen} == {"penmanshiel"} and {s.dataset for s in kel} == {"real_kelmarsh"}


def test_specs_for_dataset_dispatch():
    assert len(run_all.specs_for_dataset("synthetic")) == 24
    assert len(run_all.specs_for_dataset("real_chubut")) == 8                # Argentine rose on the synthetic grid
    assert run_all.specs_for_dataset("real_chubut")[0].wind_rose == "chubut"


def test_run_instance_on_real_farm_layout(tmp_path):
    rose = tmp_path / "windrose.json"
    rose.write_text(json.dumps({"sites": {"kelmarsh": {"sectors": [
        {"direction_deg": 225.0, "frequency": 0.6, "mean_speed": 8.0},
        {"direction_deg": 270.0, "frequency": 0.4, "mean_speed": 7.0}]}}}), encoding="utf-8")
    spec = InstanceSpec("real_kelmarsh", 0, "kelmarsh", 6, 2, 0)
    rows = run_all.run_instance(spec, dict(TINY, maxiter=4), windrose_path=str(rose), farms_path=FARMS_PATH)
    assert {(r["grid_rows"], r["grid_cols"]) for r in rows} == {(6, 1)}
    assert next(r for r in rows if r["method"] == "exact")["energy_gap"] == pytest.approx(0.0)
    assert all(r["energy_gap"] >= -1e-9 for r in rows)


# --- sub-instance, Kelmarsh as trivial contrast, datasets never mixed ---

def test_penmanshiel_sub10_specs_are_fixed():
    specs = run_all.specs_for_dataset("real_penmanshiel_sub10")
    assert [(s.N, s.K) for s in specs] == [(10, 3), (10, 5), (10, 7)]
    assert {s.dataset for s in specs} == {"real_penmanshiel_sub10"} and {s.wind_rose for s in specs} == {"penmanshiel"}
    assert all(run_all.is_farm(s) and run_all.grid_for(s) == (10, 1) for s in specs)


def test_farm_cells_sub10_vs_full():
    full = run_all.farm_cells(run_all.specs_for_dataset("real_penmanshiel")[0], FARMS_PATH)
    sub = run_all.farm_cells(run_all.specs_for_dataset("real_penmanshiel_sub10")[0], FARMS_PATH)
    assert len(full) == 14 and len(sub) == 10
    assert all(c in full for c in sub)                      # sub-instance uses real positions of the same farm
    assert len(run_all.farm_cells(run_all.specs_for_dataset("real_kelmarsh")[0], FARMS_PATH)) == 6


def test_kelmarsh_is_labeled_as_trivial_contrast():
    assert any("Kelmarsh" in c and "trivial" in c for c in run_all.CAVEATS)


def test_aggregate_never_mixes_datasets():
    def r(dataset, gap):
        return dict(dataset=dataset, method="exact", variant="exact", p="", energy_gap=gap, time_s=0.1)
    out = run_all.aggregate([r("real_penmanshiel", 0.0), r("real_kelmarsh", 1.0), r("synthetic", 2.0)])
    assert sorted(x["dataset"] for x in out) == ["real_kelmarsh", "real_penmanshiel", "synthetic"]
    assert all(x["n_instances"] == 1 for x in out)


# --- extended instance sets (docs/PROTOCOL_EXTENSION.md): same protocol qwind-v1, larger N and more K ---

def test_extended_instance_sets_are_fixed_in_advance():
    n16 = run_all.specs_for_dataset("synthetic_n16")
    n18 = run_all.specs_for_dataset("synthetic_n18")
    allk = run_all.specs_for_dataset("real_penmanshiel_allk")
    assert sorted({(s.N, s.K) for s in n16}) == [(16, 5), (16, 8)] and len(n16) == 6
    assert sorted({(s.N, s.K) for s in n18}) == [(18, 6), (18, 9)] and len(n18) == 6
    assert sorted({s.wind_rose for s in n16}) == ["A", "B", "C"]
    assert [(s.N, s.K) for s in allk] == [(14, k) for k in range(3, 12)]
    assert {s.wind_rose for s in allk} == {"penmanshiel"}
    assert {s.dataset for s in n16} == {"synthetic_n16"} and {s.dataset for s in allk} == {"real_penmanshiel_allk"}


def test_extended_synthetic_seeds_do_not_overlap_the_original_set():
    original = {s.seed for s in run_all.specs_for_dataset("synthetic")}
    extended = {s.seed for d in ("synthetic_n16", "synthetic_n18") for s in run_all.specs_for_dataset(d)}
    assert not original & extended and len(extended) == 12


def test_allk_uses_all_fourteen_real_positions_in_their_original_order():
    spec = run_all.specs_for_dataset("real_penmanshiel_allk")[0]
    cells = run_all.farm_cells(spec, FARMS_PATH)
    full = run_all.farm_cells(run_all.specs_for_dataset("real_penmanshiel")[0], FARMS_PATH)
    assert cells == full and len(cells) == 14


def test_extended_synthetic_uses_the_synthetic_roses_and_grid(tmp_path):
    spec = InstanceSpec("synthetic_n16", 0, "B", 6, 2, 100)           # tiny N only to keep the test fast
    assert run_all.rose_for(spec) == run_all.SYNTHETIC_ROSES["B"]
    assert run_all.grid_for(spec) == (3, 2)
    rows = run_all.run_instance(spec, dict(TINY, maxiter=4))
    assert {r["dataset"] for r in rows} == {"synthetic_n16"}


def test_extended_protocol_parameters_are_the_qwind_v1_ones():
    """The larger sets must not come with different QAOA settings."""
    proto = run_all.FULL_PROTOCOL
    assert (proto["id"], proto["depths"], proto["restarts"], proto["maxiter"], proto["shots"]) == ("qwind-v1", [1, 2, 3], 2, 60, 1000)
    assert proto["lam_multipliers"] == [1.0, 3.0, 10.0] and proto["ramp_total_time_factor"] == 0.75


def test_protocol_extension_is_documented_before_running():
    path = os.path.join(os.path.dirname(__file__), "..", "docs", "PROTOCOL_EXTENSION.md")
    text = open(path, encoding="utf-8").read()
    for name in ("synthetic_n16", "synthetic_n18", "real_penmanshiel_allk", "qwind-v1", "not changed", "published, whatever they show"):
        assert name in text


def test_protocol_extension_records_that_n16_did_not_finish():
    path = os.path.join(os.path.dirname(__file__), "..", "docs", "PROTOCOL_EXTENSION.md")
    text = open(path, encoding="utf-8").read()
    assert "did not finish" in text and "no N = 16 result is reported" in text
