"""The website pages in web/ are generated from web-src/ by scripts/build_web.py.

These tests keep the generated files in sync with their sources and check that
the navbar and footer are shared by every page.
"""
import importlib.util
import os
import re

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PAGES = ["index.html", "references.html", "team.html"]


def _load_builder():
    spec = importlib.util.spec_from_file_location("build_web", os.path.join(ROOT, "scripts", "build_web.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    out = tmp_path_factory.mktemp("web")
    _load_builder().build(os.path.join(ROOT, "web-src"), str(out))
    return {p: (out / p).read_text(encoding="utf-8") for p in PAGES}


def test_generated_pages_match_committed_files(built):
    for name in PAGES:
        with open(os.path.join(ROOT, "web", name), encoding="utf-8", newline="") as f:
            committed = f.read().replace("\r\n", "\n")
        assert committed == built[name], f"web/{name} is out of date: run python scripts/build_web.py"


def _between(html, start, end):
    i = html.index(start)
    return html[i:html.index(end, i) + len(end)]


def test_footer_is_identical_on_every_page(built):
    footers = {n: _between(h, "    <footer>\n", "    </footer>\n") for n, h in built.items()}
    assert len(set(footers.values())) == 1


def test_nav_links_are_the_same_on_every_page(built):
    links = {n: re.findall(r'href="([^"]+)"', _between(h, '<div class="nav-links">', "</div>")) for n, h in built.items()}
    assert len({tuple(v) for v in links.values()}) == 1


def test_only_the_current_page_is_marked(built):
    for name, html in built.items():
        marked = re.findall(r'<a class="btn" href="([^"]+)" aria-current="page"', html)
        assert marked == ([] if name == "index.html" else [name])


def test_demo_controls_only_on_the_home_page(built):
    assert 'id="demoToggle"' in built["index.html"]
    for name in ("references.html", "team.html"):
        assert 'id="demoToggle"' not in built[name]
        assert 'class="nav-spacer"' in built[name]


def test_no_unresolved_placeholders(built):
    for name, html in built.items():
        assert "{{" not in html, name


def test_unknown_partial_is_an_error(tmp_path):
    (tmp_path / "partials").mkdir()
    (tmp_path / "pages").mkdir()
    (tmp_path / "pages" / "x.html").write_text("---\ntitle: X\n---\n{{> missing}}\n", encoding="utf-8")
    with pytest.raises(ValueError):
        _load_builder().build(str(tmp_path), str(tmp_path / "out"))
