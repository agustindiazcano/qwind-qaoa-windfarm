import json
import os

import numpy as np
import pytest

from qwind.instances import (build_instance, farm_coords_D, latlon_to_xy_m, load_farm)
from qwind.wake import generate_h_J

FARMS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "qollab", "data", "farms.json"))
EXPECTED = {"penmanshiel": (14, 82.0), "kelmarsh": (6, 92.0)}


def test_latlon_to_xy_m_local_projection():
    x, y = latlon_to_xy_m([52.0, 52.0, 53.0], [0.0, 1.0, 0.0], 52.0, 0.0)
    assert x[0] == pytest.approx(0.0) and y[0] == pytest.approx(0.0)
    assert y[2] == pytest.approx(111195, rel=1e-3)                       # 1 degree of latitude
    assert x[1] == pytest.approx(111195 * np.cos(np.radians(52.0)), rel=1e-3)  # 1 degree of longitude at 52 N
    assert y[1] == pytest.approx(0.0, abs=1e-6)


def test_generate_h_J_coords_matches_grid():
    rose = [(0, 0.2), (90, 0.5), (180, 0.1), (270, 0.2)]
    h1, J1 = generate_h_J((3, 2), spacing_D=5.0, wind_rose=rose, P0=1.0)
    coords = [(c * 5.0, r * 5.0) for r in range(3) for c in range(2)]
    h2, J2 = generate_h_J(wind_rose=rose, P0=1.0, coords=coords)
    assert np.allclose(h1, h2) and np.allclose(J1, J2)


def test_generate_h_J_coords_wind_direction():
    """Two turbines 4 D apart on an east-west line: wind blowing toward the east wakes them, wind toward the north does not."""
    coords = [(0.0, 0.0), (4.0, 0.0)]
    _, J_east = generate_h_J(wind_rose=[(0, 1.0)], coords=coords)
    _, J_north = generate_h_J(wind_rose=[(90, 1.0)], coords=coords)
    assert J_east[0, 1] > 0
    assert J_north[0, 1] == 0


def test_build_instance_with_coords():
    coords = [(0.0, 0.0), (4.0, 0.0), (0.0, 5.0)]
    inst = build_instance(3, [(0, 1.0)], seed=0, coords=coords, P0=1.0)
    assert np.allclose(inst.h, -1.0)
    assert inst.J.shape == (3, 3) and np.all(np.tril(inst.J) == 0) and inst.J[0, 1] > 0
    assert inst.grid_shape == (3, 1)


@pytest.fixture(scope="module")
def farms():
    with open(FARMS, "r", encoding="utf-8") as f:
        return json.load(f)["farms"]


@pytest.mark.parametrize("name", list(EXPECTED))
def test_farm_file_real_layout(farms, name):
    n, D = EXPECTED[name]
    farm = farms[name]
    assert len(farm["turbines"]) == n and farm["rotor_diameter_m"] == D
    ids = [t["id"] for t in farm["turbines"]]
    assert len(set(ids)) == n
    lat = np.array([t["latitude"] for t in farm["turbines"]])
    lon = np.array([t["longitude"] for t in farm["turbines"]])
    assert np.ptp(lat) > 0 and np.ptp(lon) > 0 and np.ptp(lat) < 0.05 and np.ptp(lon) < 0.05  # one site, < ~5 km
    assert farm["license"] == "CC-BY-4.0" and farm["source_doi"].startswith("10.5281/zenodo.")


@pytest.mark.parametrize("name", list(EXPECTED))
def test_farm_coords_in_rotor_diameters(farms, name):
    coords = np.array(farm_coords_D(load_farm(FARMS, name)))
    d = np.linalg.norm(coords[:, None] - coords[None], axis=2) + np.eye(len(coords)) * 1e9
    assert d.min() > 2.0          # real turbines are never closer than 2 rotor diameters
    assert d.min() < 15.0         # and the layout is one compact farm
    assert abs(coords.mean()) < 1e9


def test_load_farm_returns_name_and_ids():
    farm = load_farm(FARMS, "kelmarsh")
    assert farm["name"] == "kelmarsh" and len(farm["turbines"]) == 6
