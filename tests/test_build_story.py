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


def test_short_demo_deck_has_eleven_slides_in_both_languages(story):
    html = story["index"]
    for lang in ("en", "es"):
        short = re.findall(rf'<section class="slide[^"]*" id="slide-{lang}-s\d+" lang="{lang}" data-lang="{lang}" data-deck="short"', html)
        assert len(short) == 11, lang


def test_short_demo_switch_exists_but_starts_hidden(story):
    html = story["index"] + story["nav"]
    assert 'id="shortToggle"' in html and 'role="switch"' in html
    assert re.search(r'id="shortSwitch"[^>]*hidden', html)


def _short(html, lang, n):
    start = html.index(f'id="slide-{lang}-s{n}"')
    nxt = html.find(f'id="slide-{lang}-s{n + 1}"', start)
    return html[start:nxt if nxt > 0 else len(html)]


def test_short_deck_order_hardware_first_then_problem_data_impact_money(story):
    html = story["index"]
    expected = {2: "Tested on real quantum hardware", 3: "turbines steal wind", 4: "Tested on real wind farms and real winds",
                5: "Which 7 of the 14 turbines", 6: "What the choice could be worth", 7: "Why a quantum computer", 8: "Wake model", 9: "Key results"}
    for n, text in expected.items():
        assert text in _short(html, "en", n), (n, text)
    es = {2: "hardware cuántico real", 3: "roban viento", 4: "Probado en parques", 6: "Cuánto podría valer", 7: "computadora cuántica"}
    for n, text in es.items():
        assert text in _short(html, "es", n), (n, text)


def test_short_deck_merges_both_classical_comparisons_in_one_slide_and_has_no_solution_slide(story):
    html = story["index"]
    merged = _short(html, "en", 10)
    for text in ("Simulated annealing", "Greedy search", "Average gap to the exact best answer", "120"):
        assert text in merged, text
    short_deck = html[html.index('id="slide-en-s1"'):html.index('id="slide-es-s1"')]
    assert "Always exactly 3 on" not in short_deck
    assert "QAOA" in _short(html, "en", 11)
    assert "This effort is supported by Qollab &amp; IonQ" in _short(html, "en", 11)


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
