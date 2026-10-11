"""Dark/light theme button: dark by default (whatever the OS prefers), light only when the visitor chooses it."""
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8", newline="") as f:
        return f.read().replace("\r\n", "\n")


def test_css_light_theme_follows_the_button_not_the_os():
    css = _read("web/styles.css")
    assert "prefers-color-scheme" not in css
    assert 'html[data-theme="light"]' in css


def test_every_page_has_the_theme_toggle_and_the_dark_default():
    for page in ("index.html", "references.html", "team.html"):
        html = _read(f"web/{page}")
        assert 'id="themeToggle"' in html, page
        assert "qwind-theme" in html, page
        assert "data-theme" in html, page


def test_theme_defaults_to_dark():
    head = _read("web-src/partials/head.html")
    script = head[head.index("qwind-theme") - 400:head.index("qwind-theme") + 400]
    assert "'light'" in script and "'dark'" in script
    assert re.search(r"theme\s*=\s*'dark'", script)


def test_theme_toggle_is_a_labelled_button():
    nav = _read("web-src/partials/nav.html")
    assert re.search(r'<button[^>]*id="themeToggle"[^>]*aria-label="[^"]+"', nav)
    assert "aria-pressed" in nav
