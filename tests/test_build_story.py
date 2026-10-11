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
    n = len(re.findall(r'<section class="slide[^"]*" id="slide-en-\d+"', story["index"]))
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


def test_short_demo_deck_has_nine_slides_in_both_languages(story):
    html = story["index"]
    for lang in ("en", "es"):
        short = re.findall(rf'<section class="slide[^"]*" id="slide-{lang}-s\d+" lang="{lang}" data-lang="{lang}" data-deck="short"', html)
        assert len(short) == 9, lang


def test_short_demo_switch_exists_but_starts_hidden(story):
    html = story["index"] + story["nav"]
    assert 'id="shortToggle"' in html and 'role="switch"' in html
    assert re.search(r'id="shortSwitch"[^>]*hidden', html)


def test_short_deck_follows_the_planned_story(story):
    html = story["index"]
    es = html[html.index('id="slide-es-s1"'):]
    # title, problem, impact, why quantum, solution, results, classical, hardware, claims, closing
    for needle in ("estela", "Penmanshiel", "3 billones", "interruptores", "100%", "recocido", "IonQ Forte 1", "Run your code"):
        assert needle in es, needle
    assert "This effort is supported by Qollab &amp; IonQ" in html[html.index('id="slide-en-s9"'):]


def test_what_we_do_not_claim_section_is_gone_from_the_web_and_the_readme(story):
    for text in (story["index"], _read("README.md"), _read("qollab/README.md")):
        assert "What we do not claim" not in text
        assert "Lo que no afirmamos" not in text


def test_slides_have_no_no_quantum_advantage_phrases_but_the_home_keeps_its_text(story):
    html = story["index"]
    slides = html[html.index('<div id="demo"'):].lower()
    home = html[html.index('<main id="main">'):html.index("</main>")].lower()
    for phrase in ("no quantum advantage", "no afirmamos ventaja", "claim no quantum", "still exact in every case", "budgets are not matched"):
        assert phrase not in slides, phrase
    assert "we claim no quantum advantage" in home
