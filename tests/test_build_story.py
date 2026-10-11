"""The home page story and the demo slides are generated, in English and Spanish, by scripts/build_story.py.

These tests keep web-src/ in sync with the generator and check the bilingual structure.
"""
import importlib.util
import os
import re

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EMOJI = re.compile("[\U0001F000-\U0001FFFF☀-➿⬀-⯿]|&#\\d{4,};")


def _load():
    spec = importlib.util.spec_from_file_location("build_story", os.path.join(ROOT, "scripts", "build_story.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def story():
    return _load().render()


def _read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8", newline="") as f:
        return f.read().replace("\r\n", "\n")


def test_sources_match_generator(story):
    assert _read("web-src/pages/index.html") == story["index"], "run python scripts/build_story.py"
    assert _read("web-src/partials/nav.html") == story["nav"], "run python scripts/build_story.py"


def test_slides_exist_in_both_languages_with_the_same_count(story):
    html = story["index"]
    en = re.findall(r'<section class="slide[^"]*" id="slide-en-\d+" lang="en" data-lang="en"', html)
    es = re.findall(r'<section class="slide[^"]*" id="slide-es-\d+" lang="es" data-lang="es"', html)
    assert len(en) == len(es) >= 20


def test_navbar_has_one_button_per_slide_and_a_language_switch(story):
    nav = story["nav"]
    n = len(re.findall(r'<section class="slide[^"]*" id="slide-en-', story["index"]))
    assert len(re.findall(r'class="slide-btn"', nav)) == n
    assert 'data-set-lang="en"' in nav and 'data-set-lang="es"' in nav


def test_every_text_block_has_both_languages(story):
    html = story["index"]
    assert html.count('data-lang="en"') == html.count('data-lang="es"')


def test_no_emojis_and_every_image_has_alt(story):
    html = story["index"] + story["nav"]
    assert not EMOJI.search(html)
    for tag in re.findall(r"<img\b[^>]*>", html):
        assert "alt=" in tag, tag


def test_wind_turbine_next_to_the_logo_on_home_and_first_slide(story):
    html = story["index"]
    assert html.count('class="hero-turbine"') >= 2
    assert 'aria-hidden="true"' in html[html.index('class="hero-turbine"') - 200:html.index('class="hero-turbine"') + 200]


def test_required_qollab_line_is_kept_in_english_in_both_languages(story):
    html = story["index"]
    spanish = html[html.index('id="slide-es-1"'):html.index('id="slide-es-2"')]
    assert "This effort is supported by Qollab &amp; IonQ" in spanish


def test_no_quantum_advantage_claim_is_made(story):
    low = story["index"].lower()
    assert "we claim no quantum advantage" in low
    assert "no afirmamos ventaja cu" in low


def test_home_cards_use_the_glass_style_and_hover_but_slides_do_not(story):
    html = story["index"]
    home = html[html.index('<main id="main">'):html.index("</main>")]
    slides = html[html.index('<div id="demo"'):]
    for needle in ('card glass-surface', 'figure-card glass-surface', 'home-box glass-surface', 'flow-step home-lift'):
        assert needle in home, needle
    assert "glass-surface" not in slides.replace('<nav class="glass-surface"', "")
    assert "home-lift" not in slides
