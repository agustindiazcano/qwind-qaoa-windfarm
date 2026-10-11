import csv
import json
import os
import re
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "experiments"))
import make_figures as figs  # noqa: E402
import make_results_tables as tables  # noqa: E402

FIGURES = ["multipliers", "chance_of_best", "valid_plans", "depth"]


@pytest.fixture(scope="module")
def summary():
    return json.load(open(os.path.join(ROOT, "results", "summary.json"), encoding="utf-8"))


@pytest.fixture(scope="module")
def rows():
    with open(os.path.join(ROOT, "results", "per_instance.csv"), newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_figures_cover_the_first_batch_in_the_readme_order(summary, rows):
    data = figs.figure_data(summary, rows)
    names = [tables.SHORT_NAMES[d] for d in tables.README_ORDER]
    for key in ("multipliers", "chance_of_best", "valid_plans"):
        assert data[key]["labels"] == names


def test_multipliers_match_the_headline_range(summary, rows):
    data = figs.figure_data(summary, rows)["multipliers"]
    m = tables.headline_multipliers(summary, rows)
    assert min(data["vs_uniform"]) == pytest.approx(m["vs_uniform"][0]) and max(data["vs_uniform"]) == pytest.approx(m["vs_uniform"][1])
    assert min(data["vs_penalty"]) == pytest.approx(m["vs_penalty"][0]) and max(data["vs_penalty"]) == pytest.approx(m["vs_penalty"][1])


def test_chance_of_best_is_computed_from_per_instance_rows(summary, rows):
    data = figs.figure_data(summary, rows)["chance_of_best"]
    i = data["labels"].index("Synthetic")
    xy = [r for r in rows if r["dataset"] == "synthetic" and r["variant"] == "xy+dicke" and r["p"] == "3"]
    pen = [r for r in rows if r["dataset"] == "synthetic" and r["variant"] == "penalty+x lam=10" and r["p"] == "3"]
    assert data["xy_dicke"][i] == pytest.approx(100 * sum(abs(float(r["energy_gap"])) < 1e-9 for r in xy) / len(xy))
    assert data["penalty"][i] == pytest.approx(100 * sum(abs(float(r["energy_gap"])) < 1e-9 for r in pen) / len(pen))
    assert data["random"][i] == pytest.approx(100 * sum(float(r["random_p_hit"]) for r in xy) / len(xy))
    assert all(0 <= v <= 100 for k in ("xy_dicke", "penalty", "random") for v in data[k])


def test_valid_plans_are_percentages(summary, rows):
    data = figs.figure_data(summary, rows)["valid_plans"]
    assert all(v == pytest.approx(100.0) for v in data["xy_dicke"])
    assert all(0 < v < 100 for v in data["penalty"])


def test_depth_figure_uses_the_synthetic_dataset(summary, rows):
    d = figs.figure_data(summary, rows)["depth"]
    assert d["p"] == [1, 2, 3] and len(d["xy_dicke"]) == 3 and len(d["penalty"]) == 3
    rec = next(r for r in summary["results"] if r["dataset"] == "synthetic" and r["variant"] == "xy+dicke" and r["p"] == 2)
    assert d["xy_dicke"][1] == pytest.approx(rec["metrics"]["p_optimal"]["mean"])
    assert d["uniform"] == pytest.approx(rec["baselines"]["uniform_feasible_p_optimal"])


def test_build_all_writes_the_pngs(tmp_path, summary, rows):
    paths = figs.build_all(summary, rows, str(tmp_path))
    assert sorted(os.path.basename(p) for p in paths) == sorted(f + ".png" for f in FIGURES)
    assert all(os.path.getsize(p) > 5000 for p in paths)


def test_figures_are_committed_and_the_readme_embeds_them_with_alt_text():
    readme = open(os.path.join(ROOT, "README.md"), encoding="utf-8").read()
    for name in FIGURES:
        assert os.path.exists(os.path.join(ROOT, "results", "figures", name + ".png")), f"results/figures/{name}.png is missing"
        m = re.search(r"!\[([^\]]+)\]\(([^)]*results/figures/" + name + r"\.png)\)", readme)
        assert m, f"the README must embed {name}.png with alt text"
        assert len(m.group(1)) > 40, "alt text must describe the figure"
