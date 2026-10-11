import json
import os
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "experiments"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import estimate_impact as imp  # noqa: E402
import make_illustrations as ill  # noqa: E402
import make_results_tables as tables  # noqa: E402

DATA = os.path.join(ROOT, "qollab", "data")
INPUTS = os.path.join(ROOT, "results", "impact_inputs.json")

GREENBYTE = (
    "# This file was exported by Greenbyte.\n#\n"
    '# Date and time,Wind speed (m/s),Power (kW)\n'
    "2019-01-01 00:00:00,5.0,100.0\n"
    "2019-01-01 00:10:00,7.0,300.0\n"
    "2019-01-01 00:20:00,NaN,NaN\n"
    "2019-01-01 00:30:00,9.0,200.0\n"
)


def test_read_power_skips_header_and_missing(tmp_path):
    f = tmp_path / "Turbine_Data_Test_1.csv"
    f.write_text(GREENBYTE, encoding="utf-8")
    assert imp.read_power(str(f)) == [100.0, 300.0, 200.0]


def test_power_stats_average_the_turbines(tmp_path):
    (tmp_path / "Turbine_Data_Test_1.csv").write_text(GREENBYTE, encoding="utf-8")
    (tmp_path / "Turbine_Data_Test_2.csv").write_text(GREENBYTE.replace("300.0", "500.0"), encoding="utf-8")
    s = imp.power_stats(str(tmp_path), rated_kw=1000.0)
    assert s["n_turbines"] == 2 and s["n_readings"] == 6
    assert s["mean_power_kw"] == pytest.approx((200.0 + 266.6666667) / 2)        # mean of each turbine's own mean
    assert s["capacity_factor"] == pytest.approx(s["mean_power_kw"] / 1000.0)


def test_estimate_by_hand():
    e = imp.estimate(K=7, mean_power_kw=637.2, loss_best=0.04, loss_avg=0.08, hours=1000)
    potential = 7 * 0.6372 * 1000                                                  # MWh the K turbines could produce
    assert e["potential_mwh"] == pytest.approx(potential)
    assert e["gain_mwh"] == pytest.approx(potential * 0.04)                       # (0.08 - 0.04) of the potential
    assert e["gain_pct"] == pytest.approx(100 * (0.96 / 0.92 - 1))
    assert e["value_gbp"](75) == pytest.approx(potential * 0.04 * 75)


def test_estimate_is_zero_when_the_choice_does_not_matter():
    e = imp.estimate(K=5, mean_power_kw=600.0, loss_best=0.05, loss_avg=0.05, hours=1000)
    assert e["gain_mwh"] == 0 and e["gain_pct"] == 0


def test_inputs_file_is_the_measured_penmanshiel_power():
    inputs = json.load(open(INPUTS, encoding="utf-8"))
    assert inputs["farm"] == "penmanshiel" and inputs["year"] == 2019 and inputs["rated_kw"] == 2050
    assert 500 < inputs["mean_power_kw"] < 800 and 0.2 < inputs["capacity_factor"] < 0.4
    assert inputs["n_turbines"] == 14 and inputs["source"].startswith("Zenodo 10.5281/zenodo.16807304")


def test_rows_use_the_modelled_wake_losses():
    inputs = json.load(open(INPUTS, encoding="utf-8"))
    rows = imp.impact_rows(inputs, DATA)
    assert [r["K"] for r in rows] == [5, 7, 9]
    for r in rows:
        s = ill.wake_loss_stats("penmanshiel", r["K"], DATA)
        assert r["loss_best"] == pytest.approx(s["best"]) and r["loss_avg"] == pytest.approx(s["average"])
        assert r["gain_mwh"] > 0 and r["hours"] == 1000


def test_readme_and_docs_blocks_are_generated_from_the_inputs():
    inputs = json.load(open(INPUTS, encoding="utf-8"))
    block = imp.impact_block(inputs, DATA)
    for path in ("README.md", os.path.join("docs", "IMPACT.md")):
        text = open(os.path.join(ROOT, path), encoding="utf-8").read()
        got = text.split(imp.START, 1)[1].split(imp.END, 1)[0].strip()
        assert got == block.strip(), f"{path}: regenerate with python experiments/estimate_impact.py"


def test_the_estimate_is_labelled_illustrative_and_not_a_forecast():
    inputs = json.load(open(INPUTS, encoding="utf-8"))
    low = imp.impact_block(inputs, DATA).lower()
    assert "illustrative" in low and "not a forecast" in low and "average random choice" in low
    for bad in ("guarantee", "will save", "saves "):
        assert bad not in low


def test_impact_doc_cites_the_price_source_and_lists_the_assumptions():
    text = open(os.path.join(ROOT, "docs", "IMPACT.md"), encoding="utf-8").read()
    assert "cfd-ar6-budget-notice" in text and "64" in text and "2012 prices" in text
    assert "zenodo.16807304" in text
    for must in ("Assumptions", "Limits"):
        assert must in text
