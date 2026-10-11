import os
import re

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIR = os.path.join(ROOT, "results", "backend_probe")


def _read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def _parse(path):
    text = _read("results", "backend_probe", path)
    p_opt = re.search(r"P\(optimal\)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", text)
    p_feas = re.search(r"P\(feasible\)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", text)
    valid = re.search(r"ideal ([\d.]+) \| measured ([\d.]+) \| uniform over valid layouts ([\d.]+)", text)
    shots = re.search(r"(\d+) shots", text)
    return {"ideal": p_opt.group(1), "measured": p_opt.group(2), "feasible": p_feas.group(2), "valid": valid.group(2),
            "valid_ideal": valid.group(1), "baseline": valid.group(3), "shots": int(shots.group(1))}


def test_the_qpu_output_is_saved_with_its_numbers():
    r = _parse("ionq_forte1_qpu.txt")
    assert (r["ideal"], r["measured"], r["feasible"], r["valid"], r["shots"]) == ("0.1784", "0.1304", "0.7834", "0.1665", 997)
    text = _read("results", "backend_probe", "ionq_forte1_qpu.txt")
    assert "ionq_qpu.forte-1" in text and "Circuit execution time: 200920ms" in text
    assert "best sampled layout: gap 0.0000" in text


def test_valid_only_value_is_the_conditional_probability():
    r = _parse("ionq_forte1_qpu.txt")
    assert float(r["valid"]) == pytest.approx(float(r["measured"]) / float(r["feasible"]), abs=1e-3)


def test_readme_quotes_the_hardware_numbers_from_the_saved_output():
    readme = _read("README.md")
    r = _parse("ionq_forte1_qpu.txt")
    section = readme.split("## Run on real quantum hardware", 1)[1].split("\n## ", 1)[0]
    for value in (r["valid"], r["valid_ideal"], r["baseline"], r["measured"], r["feasible"]):
        assert value in section, f"README hardware section is missing {value}"
    assert str(r["shots"]) in section
    low = section.lower()
    assert "one run" in low or "single run" in low
    assert "results/backend_probe" in section


def test_summary_table_has_the_qpu_row():
    text = _read("results", "backend_probe", "summary.md")
    assert "IonQ Forte 1" in text and "0.1665" in text and "0.7834" in text


def test_readme_headline_says_it_ran_on_a_real_quantum_computer_with_the_measured_share():
    readme = _read("README.md")
    headline = readme.split("\n## ", 1)[0]
    r = _parse("ionq_forte1_qpu.txt")
    share = round(100 * float(r["valid"]) / float(r["valid_ideal"]))          # share of the ideal probability that the hardware reached
    assert "IonQ Forte 1" in headline and "real quantum computer" in headline
    assert f"{share}%" in headline and "N = 6" in headline


ORIGINAL = "agustindiazcano-qwind-output-completed-2026-10-11T03-37-01.138Z.html"


def test_the_original_qollab_export_is_kept_and_matches_the_saved_text():
    html = _read("results", "backend_probe", ORIGINAL)
    assert "<script" not in html.lower()                              # a static console export, nothing executable
    for must in ("IonQQPUBackend", "ionq_qpu.forte-1", "997 shots", "Circuit execution time: 200920ms",
                 "measured 0.1665", "0.1304", "0.7834", "gap 0.0000 to the exact optimum"):
        assert must in html, must
    r = _parse("ionq_forte1_qpu.txt")
    assert r["measured"] in html and r["feasible"] in html and r["valid"] in html


def test_the_readme_links_the_original_export():
    readme = _read("README.md")
    section = readme.split("## Run on real quantum hardware", 1)[1].split("\n## ", 1)[0]
    assert "results/backend_probe/" + ORIGINAL in section
