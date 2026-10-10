import json
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "experiments")))
import build_windrose  # noqa: E402
from qwind.instances import load_wind_rose  # noqa: E402

DATA = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "qollab", "data", "windrose.json"))
SITES = ["chubut", "bahia_blanca"]


@pytest.fixture(scope="module")
def sites():
    # the real file, not a fixture
    with open(DATA, "r", encoding="utf-8") as f:
        return json.load(f)["sites"]


def test_both_sites_present(sites):
    for s in SITES:
        assert s in sites


@pytest.mark.parametrize("site", SITES)
def test_sector_count(sites, site):
    assert 12 <= len(sites[site]["sectors"]) <= 16


@pytest.mark.parametrize("site", SITES)
def test_frequencies(sites, site):
    f = np.array([s["frequency"] for s in sites[site]["sectors"]])
    assert np.all(f > 0)
    assert abs(f.sum() - 1.0) < 1e-6


@pytest.mark.parametrize("site", SITES)
def test_directions(sites, site):
    d = [s["direction_deg"] for s in sites[site]["sectors"]]
    assert all(0 <= x < 360 for x in d)
    assert len(set(d)) == len(d)


@pytest.mark.parametrize("site", SITES)
def test_mean_speeds_positive(sites, site):
    assert all(s["mean_speed"] > 0 for s in sites[site]["sectors"])


@pytest.mark.parametrize("site", SITES)
def test_load_wind_rose_probabilities(site):
    rose = load_wind_rose(DATA, site)
    assert sum(p for _, p in rose) == pytest.approx(1.0, abs=1e-9)
    assert all(0 <= a < 360 for a, _ in rose)


# --- binning used to build the file (experiments/build_windrose.py), checked on a tiny known input ---

def test_bin_sectors_known_input():
    # 4 hours: two from north (speed 4 and 6), one from east (10), one from 350 deg (wraps into the north sector)
    speed = [4.0, 6.0, 10.0, 8.0]
    direction = [0.0, 5.0, 90.0, 350.0]
    sectors = build_windrose.bin_sectors(speed, direction, n_sectors=16)
    by_dir = {s["direction_deg"]: s for s in sectors}
    assert len(sectors) == 16
    assert by_dir[0.0]["frequency"] == pytest.approx(3 / 4)
    assert by_dir[0.0]["mean_speed"] == pytest.approx(6.0)
    assert by_dir[90.0]["frequency"] == pytest.approx(1 / 4)
    assert by_dir[90.0]["mean_speed"] == pytest.approx(10.0)
    assert by_dir[180.0]["frequency"] == 0.0


def test_bin_sectors_ignores_missing():
    sectors = build_windrose.bin_sectors([5.0, None, 7.0], [10.0, 20.0, None], n_sectors=16)
    assert sum(s["frequency"] for s in sectors) == pytest.approx(1.0)
    assert {s["direction_deg"]: s["frequency"] for s in sectors}[0.0] == pytest.approx(1.0)
