import csv
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import make_results_tables as tables  # noqa: E402


def _read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def test_qollab_description_fits_the_240_character_limit():
    m = re.search(r"\*\*Description \(max 240 characters\):\*\*\s*\n\s*\n>\s*(.+)", _read("docs", "QOLLAB_PAGE.md"))
    assert m, "docs/QOLLAB_PAGE.md must contain the description"
    assert len(m.group(1).strip()) <= 240


def test_readme_has_the_required_text_and_no_draft_notices():
    readme = _read("README.md")
    assert "This effort is supported by Qollab & IonQ" in readme
    for draft in ("In development", "Work in Progress", "to be completed"):
        assert draft not in readme
    assert "no quantum advantage" in readme.lower() or "do not claim a quantum advantage" in readme.lower()


def test_readme_results_block_matches_results_files():
    """Every number in the README results block is generated: it must equal what the script produces now."""
    summary = json.loads(_read("results", "summary.json"))
    with open(os.path.join(ROOT, "results", "per_instance.csv"), newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    readme = _read("README.md")
    block = readme.split(tables.START, 1)[1].split(tables.END, 1)[0].strip()
    assert block == tables.readme_block(summary, rows).strip()
