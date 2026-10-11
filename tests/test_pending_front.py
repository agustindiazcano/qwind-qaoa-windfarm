import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _text():
    with open(os.path.join(ROOT, "PENDING-FRONT.md"), encoding="utf-8") as f:
        return f.read()


def test_every_file_the_list_mentions_exists():
    text = _text()
    paths = set(re.findall(r"`((?:results|scripts|docs|web|\.github)/[A-Za-z0-9_./-]+\.[a-z]+)`", text))
    paths = {p for p in paths if not p.startswith("web/data/")}          # created by scripts/sync_results_to_web.py
    assert len(paths) >= 6
    for p in sorted(paths):
        assert os.path.exists(os.path.join(ROOT, p)), f"PENDING-FRONT.md mentions a missing file: {p}"


def test_all_seven_figures_are_listed():
    text = _text()
    figures = sorted(f for f in os.listdir(os.path.join(ROOT, "results", "figures")) if f.endswith(".png"))
    assert len(figures) == 7
    for f in figures:
        assert f in text, f"{f} is not in the list"


def test_the_list_keeps_the_project_rules():
    low = _text().lower()
    assert "results/" in low and "ventaja" in low and "alt" in low and "mit" in low
