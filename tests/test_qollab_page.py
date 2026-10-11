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


def test_every_github_link_in_the_readme_points_to_a_tracked_file():
    """The README is pasted on the Qollab page: links to blob/main/<path> must not be broken."""
    paths = re.findall(r"blob/main/([^)\s#]+)", _read("README.md"))
    assert paths
    for path in paths:
        assert os.path.exists(os.path.join(ROOT, path)), f"README links to a missing file: {path}"


def test_readme_does_not_list_libraries_the_experiments_do_not_use():
    readme = _read("README.md")
    used = ""
    for folder in ("experiments", "scripts", "qollab"):
        for dirpath, _, files in os.walk(os.path.join(ROOT, folder)):
            for fn in files:
                if fn.endswith(".py"):
                    used += open(os.path.join(dirpath, fn), encoding="utf-8").read()
    for lib in ("matplotlib", "qiskit-aer", "qiskit_aer"):
        if lib in readme:
            assert lib.replace("-", "_") in used or lib in used, f"README lists {lib} but no script imports it"


def test_readme_references_list_the_data_sources_and_related_work_with_links():
    """The footer must carry every source with a link: data, price reference, license and related work."""
    refs = _read("README.md").split("## References", 1)[1]
    for link in ("doi.org/10.5281/zenodo.16807304", "doi.org/10.5281/zenodo.16807551",           # Penmanshiel, Kelmarsh
                 "cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels", "open-meteo.com",   # ERA5 via Open-Meteo
                 "cfd-ar6-budget-notice.pdf", "creativecommons.org/licenses/by/4.0",                      # price reference, license
                 "arxiv.org/abs/2312.13123", "arxiv.org/abs/2512.17582",                                   # Hancock et al.
                 "advanced.onlinelibrary.wiley.com/doi/10.1002/qute.202500358",                                                         # Nigro et al.
                 "arxiv.org/abs/2505.18396", "arxiv.org/abs/2602.14827"):                                  # XY mixers, Dicke + XY
        assert link in refs, f"missing from the References footer: {link}"
