import itertools
import os
import re
import sys

import numpy as np
import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "experiments"))
sys.path.insert(0, os.path.join(ROOT, "qollab"))
import make_illustrations as ill  # noqa: E402
from qwind.instances import build_instance, farm_coords_D, load_farm, load_wind_rose  # noqa: E402

DATA = os.path.join(ROOT, "qollab", "data")
IMAGES = ["what_is_a_wake", "the_decision", "how_it_works"]


def _brute_force(farm, K):
    rose = load_wind_rose(os.path.join(DATA, "windrose.json"), farm)
    coords = farm_coords_D(load_farm(os.path.join(DATA, "farms.json"), farm))
    inst = build_instance(len(coords), rose, 0, coords=coords)
    J = inst.J + inst.J.T
    shares = [J[np.ix_(list(s), list(s))].sum() / 2 / K for s in itertools.combinations(range(len(coords)), K)]
    return min(shares), float(np.mean(shares)), max(shares)


def test_wake_loss_stats_match_a_brute_force_on_kelmarsh():
    stats = ill.wake_loss_stats("kelmarsh", 3, DATA)
    best, avg, worst = _brute_force("kelmarsh", 3)
    assert stats["best"] == pytest.approx(best) and stats["average"] == pytest.approx(avg) and stats["worst"] == pytest.approx(worst)
    assert 0 <= stats["best"] <= stats["average"] <= stats["worst"] < 1
    assert len(stats["best_selection"]) == 3 and stats["n_choices"] == 20


def test_the_best_choice_loses_less_than_an_average_random_choice_at_penmanshiel():
    for K in (5, 7, 9):
        s = ill.wake_loss_stats("penmanshiel", K, DATA)
        assert s["best"] < s["average"] < s["worst"]
        assert len(s["best_selection"]) == K and len(set(s["best_selection"])) == K


def test_build_all_writes_the_images(tmp_path):
    paths = ill.build_all(str(tmp_path), DATA)
    assert sorted(os.path.basename(p) for p in paths) == sorted(n + ".png" for n in IMAGES)
    assert all(os.path.getsize(p) > 8000 for p in paths)


def test_readme_embeds_the_images_with_alt_text_and_the_modelled_numbers():
    readme = open(os.path.join(ROOT, "README.md"), encoding="utf-8").read()
    for name in IMAGES:
        assert os.path.exists(os.path.join(ROOT, "results", "figures", name + ".png")), name
        m = re.search(r"!\[([^\]]+)\]\(([^)]*results/figures/" + name + r"\.png)\)", readme)
        assert m and len(m.group(1)) > 40, f"{name}: embed with a descriptive alt text"
    for K in (5, 7, 9):
        s = ill.wake_loss_stats("penmanshiel", K, DATA)
        assert f"{100 * s['best']:.1f}% against {100 * s['average']:.1f}%" in readme, f"README impact numbers for K = {K}"


def test_the_readme_never_turns_the_model_into_money():
    readme = open(os.path.join(ROOT, "README.md"), encoding="utf-8").read().lower()
    section = readme.split("## why it matters", 1)[1].split("\n## ", 1)[0]
    assert "modelled" in section or "modeled" in section
    assert "potential" in section
    for bad in ("saves", "savings of", "$", "eur", "usd", "profit", "revenue gain"):
        assert bad not in section, bad
