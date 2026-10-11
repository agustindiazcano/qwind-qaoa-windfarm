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


# ---- README block generated from results/ ----

def test_readme_block_numbers_come_from_the_file(summary, rows):
    md = tables.readme_block(summary, rows)
    for d in tables.README_ORDER:
        assert d in md
    rec = next(r for r in summary["results"] if r["dataset"] == "synthetic" and r["variant"] == "xy+dicke" and r["p"] == 3)
    assert f"{rec['metrics']['p_optimal']['mean']:.3f}" in md
    assert f"{rec['baselines']['uniform_feasible_ratio']:.3f}" in md
    assert "std" not in md.lower() and "ci95" not in md.lower()


def _section(md, title_part):
    """The table that follows the bold title containing `title_part`."""
    parts = md.split("\n\n")
    i = next(k for k, p in enumerate(parts) if p.startswith("**") and title_part in p)
    return [_cells(l) for l in parts[i + 1].splitlines()[2:]]


def test_readme_legend_maps_short_names_to_full_dataset_ids(summary, rows):
    md = tables.readme_block(summary, rows)
    legend = _section(md, "Datasets")
    ids = {d["dataset"] for d in summary["datasets"]} & set(tables.README_ORDER)     # the first batch
    assert {r[1].strip("`") for r in legend} == ids                      # the full names are the index
    assert [r[0] for r in legend] == [tables.SHORT_NAMES[d] for d in tables.README_ORDER if d in ids]
    assert len({r[0] for r in legend}) == len(legend)                      # short names are unique
    assert "Bahia" in [r[0] for r in legend] and "Penmanshiel-10" in [r[0] for r in legend]
    n_inst = {d["dataset"]: d["n_instances"] for d in summary["datasets"]}
    assert all(int(r[5]) == n_inst[r[1].strip("`")] for r in legend)       # instance counts come from the file


def test_readme_tables_use_short_names_only(summary, rows):
    md = tables.readme_block(summary, rows)
    after_legend = md.split("**Constraint-preserving", 1)[1]
    assert "real_" not in after_legend                                     # the full ids appear only in the legend


def test_readme_headline_table_is_one_row_per_dataset_at_the_deepest_p(summary, rows):
    md = tables.readme_block(summary, rows)
    body = _section(md, "depth p = 3")
    ids = {x["dataset"] for x in summary["datasets"]} & set(tables.README_ORDER)
    assert [b[0] for b in body] == [tables.SHORT_NAMES[d] for d in tables.README_ORDER if d in ids]
    assert len(body) == len(ids)
    row = next(b for b in body if b[0] == "Penmanshiel-10")
    rec = next(r for r in summary["results"] if r["dataset"] == "real_penmanshiel_sub10" and r["variant"] == "xy+dicke" and r["p"] == 3)
    assert float(row[2]) == pytest.approx(rec["metrics"]["p_optimal"]["mean"], abs=5e-4)


def test_readme_classical_table_reports_the_xy_dicke_best_sample_not_a_pooled_average(summary, rows):
    """The best-sampled gap must be per variant: pooling the penalty variants into 'QAOA' hid that XY+Dicke finds the optimum."""
    md = tables.readme_block(summary, rows)
    assert "QAOA best-sampled gap" not in md                                   # the pooled column is gone
    parts = md.split("\n\n")
    i = next(k for k, p in enumerate(parts) if p.startswith("**Final solution quality"))
    header = _cells(parts[i + 1].splitlines()[0])
    body = _section(md, "Final solution quality")
    assert "XY+Dicke best-sample gap" in header and "XY+Dicke found the optimum" in header
    assert any("random" in h.lower() for h in header)
    for name, ds in (("Synthetic", "synthetic"), ("Penmanshiel", "real_penmanshiel")):
        row = next(b for b in body if b[0] == name)
        xy = [r for r in rows if r["dataset"] == ds and r["variant"] == "xy+dicke" and r["p"] == "3"]
        gaps = [float(r["energy_gap"]) for r in xy]
        found = sum(1 for g in gaps if abs(g) < 1e-9)
        assert float(row[header.index("XY+Dicke best-sample gap")]) == pytest.approx(sum(gaps) / len(gaps), abs=5e-5)
        assert row[header.index("XY+Dicke found the optimum")] == f"{found}/{len(xy)}"
        rnd = [float(r["random_p_hit"]) for r in xy]
        assert float(row[[i for i, h in enumerate(header) if "random" in h.lower()][0]]) == pytest.approx(sum(rnd) / len(rnd), abs=5.1e-3)   # shown with 2 decimals


def test_readme_block_penalty_sweep_range_is_computed(summary, rows):
    md = tables.readme_block(summary, rows)
    pen = [r for r in summary["results"] if r["dataset"] == "synthetic" and r["method"] == "qaoa" and r["variant"].startswith("penalty")]
    lo = min(round(r["frac_beating_uniform_ratio"] * r["n_instances"]) for r in pen)
    hi = max(round(r["frac_beating_uniform_ratio"] * r["n_instances"]) for r in pen)
    assert f"{lo}-{hi}/24" in md


def test_update_readme_replaces_only_the_marked_block(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text("before\n<!-- RESULTS:START -->\nold\n<!-- RESULTS:END -->\nafter\n", encoding="utf-8")
    tables.update_readme(str(readme), "NEW BLOCK")
    text = readme.read_text(encoding="utf-8")
    assert text == "before\n<!-- RESULTS:START -->\nNEW BLOCK\n<!-- RESULTS:END -->\nafter\n"


def test_update_readme_needs_markers(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text("no markers\n", encoding="utf-8")
    with pytest.raises(ValueError, match="RESULTS"):
        tables.update_readme(str(readme), "x")


# ---- numbers quoted in the README prose ("What we found") must come from results/ ----

def _independent_multipliers(summary):
    vs_uniform, vs_penalty = [], []
    for d in {x["dataset"] for x in summary["datasets"]}:
        xy = next(r for r in summary["results"] if r["dataset"] == d and r["variant"] == "xy+dicke" and r["p"] == 3)
        pen = max(r["metrics"]["p_optimal"]["mean"] for r in summary["results"]
                  if r["dataset"] == d and r["method"] == "qaoa" and r["variant"].startswith("penalty") and r["p"] == 3)
        p = xy["metrics"]["p_optimal"]["mean"]
        vs_uniform.append(p / xy["baselines"]["uniform_feasible_p_optimal"])
        vs_penalty.append(p / pen)
    return min(vs_uniform), max(vs_uniform), min(vs_penalty), max(vs_penalty)


def test_headline_multipliers_are_computed_from_the_file(summary, rows):
    m = tables.headline_multipliers(summary, rows)
    lo_u, hi_u, lo_p, hi_p = _independent_multipliers(summary)
    assert m["vs_uniform"] == (pytest.approx(lo_u), pytest.approx(hi_u))
    assert m["vs_penalty"] == (pytest.approx(lo_p), pytest.approx(hi_p))
    assert m["found_optimum_datasets"] == 5 and m["datasets"] == 6          # best sample is the optimum in every instance of 5 of 6


def test_readme_prose_quotes_the_computed_multipliers(summary, rows):
    readme = open(os.path.join(ROOT, "README.md"), encoding="utf-8").read()
    m = tables.headline_multipliers(summary, rows)
    assert f"{round(m['vs_uniform'][0], 1):g} to {round(m['vs_uniform'][1], 1):g} times" in readme
    assert f"{round(m['vs_penalty'][0], 1):g} to {round(m['vs_penalty'][1], 1):g} times" in readme


# ---- two generated README blocks: first batch (unchanged by new datasets) and second batch ----

def _with_extra_dataset(summary, rows, source="real_penmanshiel", new="real_penmanshiel_allk"):
    """Copy of summary and rows with one extra dataset, as if the second batch had been merged into results/."""
    import copy
    s = copy.deepcopy(summary)
    s["datasets"] = [d for d in s["datasets"] if d["dataset"] != new]          # drop the real one if it is already merged
    s["results"] = [r for r in s["results"] if r["dataset"] != new]
    s["instances"] = [i for i in s["instances"] if i["dataset"] != new]
    rows = [r for r in rows if r["dataset"] != new]
    s["datasets"].append(dict(next(d for d in s["datasets"] if d["dataset"] == source), dataset=new))
    s["results"] += [dict(copy.deepcopy(r), dataset=new) for r in summary["results"] if r["dataset"] == source]
    s["instances"] += [dict(i, dataset=new) for i in summary["instances"] if i["dataset"] == source]
    return s, rows + [dict(r, dataset=new) for r in rows if r["dataset"] == source]


def test_first_batch_block_is_unchanged_when_second_batch_datasets_are_merged(summary, rows):
    s2, rows2 = _with_extra_dataset(summary, rows)
    assert tables.readme_block(s2, rows2) == tables.readme_block(summary, rows)
    assert tables.headline_multipliers(s2, rows2) == tables.headline_multipliers(summary, rows)


def test_second_batch_block_only_has_second_batch_datasets(summary, rows):
    s2, rows2 = _with_extra_dataset(summary, rows)
    md = tables.readme_block(s2, rows2, datasets=tables.BATCH2)
    legend = _section(md, "Datasets")
    assert [r[1].strip("`") for r in legend] == ["real_penmanshiel_allk"]
    assert "Synthetic |" not in md and "real_kelmarsh" not in md
    assert tables.SHORT_NAMES["real_penmanshiel_allk"] in md


def test_second_batch_is_skipped_when_it_is_not_in_the_summary(summary, rows):
    first_only = dict(summary, datasets=[d for d in summary["datasets"] if d["dataset"] in tables.README_ORDER])
    assert tables.batch2_datasets(first_only) == []
    s2, _ = _with_extra_dataset(first_only, rows)
    assert tables.batch2_datasets(s2) == ["real_penmanshiel_allk"]


def test_update_readme_with_its_own_markers(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text("a\n<!-- RESULTS:START -->\nOLD1\n<!-- RESULTS:END -->\nb\n<!-- RESULTS2:START -->\nOLD2\n<!-- RESULTS2:END -->\nc\n", encoding="utf-8")
    tables.update_readme(str(readme), "NEW2", tables.START2, tables.END2)
    text = readme.read_text(encoding="utf-8")
    assert "OLD1" in text and "NEW2" in text and "OLD2" not in text


def test_cli_updates_both_blocks_when_the_second_batch_exists(tmp_path, summary, rows):
    s2, rows2 = _with_extra_dataset(summary, rows)
    results = tmp_path / "results"
    results.mkdir()
    (results / "summary.json").write_text(json.dumps(s2), encoding="utf-8")
    with open(results / "per_instance.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows2[0].keys()))
        w.writeheader()
        w.writerows(rows2)
    readme = tmp_path / "README.md"
    readme.write_text("<!-- RESULTS:START -->\nx\n<!-- RESULTS:END -->\n<!-- RESULTS2:START -->\ny\n<!-- RESULTS2:END -->\n", encoding="utf-8")
    tables.main(["--results", str(results), "--out", str(tmp_path / "t.md"), "--readme", str(readme)])
    text = readme.read_text(encoding="utf-8")
    first, second = text.split(tables.START2)
    assert "`real_penmanshiel_allk`" not in first and "`real_penmanshiel_allk`" in second


def test_legend_gives_country_and_a_source_link_for_every_dataset(summary, rows):
    md = tables.readme_block(summary, rows)
    header = _cells(md.split("\n\n")[1].splitlines()[0])         # the table that follows the "Datasets" title
    assert header == ["name", "dataset", "country", "what it is", "source", "instances"]
    legend = {r[1].strip("`"): r for r in _section(md, "Datasets")}
    assert legend["real_penmanshiel"][2] == "Scotland, UK" and legend["real_kelmarsh"][2] == "England, UK"
    assert legend["real_chubut"][2] == "Argentina" and legend["real_bahia_blanca"][2] == "Argentina"
    for ds in ("real_penmanshiel", "real_penmanshiel_sub10", "real_kelmarsh", "real_chubut", "real_bahia_blanca"):
        assert "](https://" in legend[ds][4], f"{ds} needs a source link"
    assert "zenodo.16807304" in legend["real_penmanshiel"][4] and "zenodo.16807551" in legend["real_kelmarsh"][4]
    assert "cds.climate.copernicus.eu" in legend["real_chubut"][4] and "open-meteo.com" in legend["real_chubut"][4]
    assert "docs/DATA.md" in legend["synthetic"][4]


def test_every_dataset_has_a_country_and_a_source_entry():
    for d in tables.README_ORDER + tables.BATCH2:
        assert tables.COUNTRIES.get(d) and tables.SOURCES.get(d), d


# ---- second batch: the numbers quoted in the README prose come from the result files ----

def test_allk_highlights_are_computed_from_the_files(summary, rows):
    h = tables.allk_highlights(summary, rows)
    xy = [r for r in rows if r["dataset"] == "real_penmanshiel_allk" and r["variant"] == "xy+dicke" and r["p"] == "3"]
    assert h["instances"] == len(xy) == 9
    assert h["found"] == sum(abs(float(r["energy_gap"])) < 1e-9 for r in xy)
    hits = [float(r["random_p_hit"]) for r in xy]
    assert h["random_hit"] == (pytest.approx(min(hits)), pytest.approx(max(hits)))
    mult = []
    for r in xy:
        mult.append(float(r["p_optimal"]) / float(r["uniform_feasible_p_optimal"]))
    assert h["vs_uniform"] == (pytest.approx(min(mult)), pytest.approx(max(mult)))


def test_readme_second_batch_section_quotes_them_and_links_the_design_note(summary, rows):
    readme = open(os.path.join(ROOT, "README.md"), encoding="utf-8").read()
    h = tables.allk_highlights(summary, rows)
    assert f"{h['found']} of the {h['instances']} values of K" in readme
    assert f"{h['random_hit'][0]:.2f} to {h['random_hit'][1]:.2f}" in readme
    assert f"{h['vs_uniform'][0]:.1f} to {h['vs_uniform'][1]:.1f} times" in readme
    assert "docs/PROTOCOL_EXTENSION.md" in readme and tables.START2 in readme and tables.END2 in readme
