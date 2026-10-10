import csv
import json
import os
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import make_results_tables as tables  # noqa: E402

SUMMARY = os.path.join(ROOT, "results", "summary.json")
PER_INSTANCE = os.path.join(ROOT, "results", "per_instance.csv")


@pytest.fixture(scope="module")
def summary():
    return json.load(open(SUMMARY, encoding="utf-8"))


@pytest.fixture(scope="module")
def rows():
    return list(csv.DictReader(open(PER_INSTANCE, newline="", encoding="utf-8")))


def _cells(md_line):
    return [c.strip() for c in md_line.strip().strip("|").split("|")]


def test_qaoa_table_numbers_come_from_the_file(summary):
    md = tables.qaoa_table(summary, "synthetic")
    lines = md.splitlines()
    header = _cells(lines[0])
    assert "P(optimal)" in header and "uniform P(optimal)" in header and "approx. ratio (feasible)" in header
    rec = next(r for r in summary["results"] if r["dataset"] == "synthetic" and r["variant"] == "xy+dicke" and r["p"] == 2)
    row = next(_cells(l) for l in lines[2:] if _cells(l)[0] == "xy+dicke" and _cells(l)[1] == "2")
    assert float(row[header.index("P(optimal)")]) == pytest.approx(rec["metrics"]["p_optimal"]["mean"], abs=5e-4)
    assert float(row[header.index("uniform P(optimal)")]) == pytest.approx(rec["baselines"]["uniform_feasible_p_optimal"], abs=5e-4)
    assert float(row[header.index("approx. ratio (feasible)")]) == pytest.approx(rec["metrics"]["approx_ratio_feasible"]["mean"], abs=5e-4)


def test_qaoa_table_has_every_variant_and_depth_of_the_dataset(summary):
    md = tables.qaoa_table(summary, "synthetic")
    body = [_cells(l) for l in md.splitlines()[2:]]
    expected = {(r["variant"], str(r["p"])) for r in summary["results"] if r["dataset"] == "synthetic" and r["method"] == "qaoa"}
    assert {(r[0], r[1]) for r in body} == expected


def test_qaoa_table_unknown_dataset_fails(summary):
    with pytest.raises(ValueError):
        tables.qaoa_table(summary, "real_nowhere")


def test_small_datasets_are_listed_one_instance_at_a_time(rows):
    md = tables.per_instance_table(rows, "real_penmanshiel_sub10", "xy+dicke")
    body = [_cells(l) for l in md.splitlines()[2:]]
    ks = sorted({int(r["K"]) for r in rows if r["dataset"] == "real_penmanshiel_sub10"})
    assert sorted({int(b[0]) for b in body}) == ks          # one row per (K, p), no mean/std/CI
    assert "std" not in md.lower() and "ci95" not in md.lower()
    assert len(body) == len(ks) * 3


def test_budget_table_states_evaluations_per_method(rows):
    md = tables.budget_table(rows, "synthetic")
    text = md.lower()
    assert "exact" in text and "sa" in text and "greedy" in text and "qaoa" in text
    sa = next(_cells(l) for l in md.splitlines()[2:] if _cells(l)[0] == "sa")
    n_sa = {float(r["n_evals"]) for r in rows if r["dataset"] == "synthetic" and r["method"] == "sa"}
    assert float(sa[1]) == pytest.approx(sum(n_sa) / len(n_sa))


def test_cli_writes_a_markdown_file_with_all_datasets(tmp_path, summary):
    out = tmp_path / "results_tables.md"
    tables.main(["--results", os.path.join(ROOT, "results"), "--out", str(out)])
    text = out.read_text(encoding="utf-8")
    for d in summary["datasets"]:
        assert d["dataset"] in text
    assert "generated from results/summary.json" in text.lower()
