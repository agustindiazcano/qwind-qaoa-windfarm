import json
from dataclasses import dataclass

import numpy as np

from qwind.wake import generate_h_J

# Wind roses as [(angle, probability)], angle = direction the wind blows TOWARD, in math degrees
# (0 = east, 90 = north), the convention of wake.py. Synthetic roses A, B, C.
SYNTHETIC_ROSES = {
    "A": [(0, 0.2), (90, 0.5), (180, 0.1), (270, 0.2)],
    "B": [(0, 0.7), (180, 0.3)],
    "C": [(45, 0.4), (135, 0.3), (225, 0.2), (315, 0.1)],
}

# (N cells, candidate K values) of the synthetic instance set; live-Run sizes stop at 14 cells
SYNTHETIC_SIZES = {6: (2, 3), 8: (3, 4), 10: (3, 4), 12: (4, 5)}


@dataclass(frozen=True)
class InstanceSpec:
    dataset: str      # "synthetic" or "real_<site>"
    instance_id: int
    wind_rose: str    # synthetic rose id (A, B, C) or the site key in qollab/data/windrose.json
    N: int
    K: int
    seed: int


@dataclass
class Instance:
    h: np.ndarray
    J: np.ndarray
    grid_shape: tuple
    P0: np.ndarray


def meteorological_to_toward(from_deg):
    """Meteorological direction (wind comes FROM, 0 = north, clockwise) to the math angle the wind blows TOWARD."""
    return (270.0 - from_deg) % 360.0


def rose_from_sectors(sectors):
    """
    Sectors [{"direction_deg": FROM direction, "frequency": f, "mean_speed": v}] to [(toward angle, probability)].
    Frequencies are normalized to sum to 1. Mean speeds are kept in the data files but the pairwise wake
    model does not use them yet.
    """
    total = float(sum(s["frequency"] for s in sectors))
    if total <= 0:
        raise ValueError("wind rose frequencies must sum to a positive number")
    return [(meteorological_to_toward(float(s["direction_deg"])), s["frequency"] / total) for s in sectors]


def load_wind_rose(path, site):
    """Read one site of a wind-rose file (qollab/data/windrose.json layout: {"sites": {site: {"sectors": [...]}}})."""
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    if not text.strip():
        raise ValueError(f"{path} is empty")
    return rose_from_sectors(json.loads(text)["sites"][site]["sectors"])


EARTH_RADIUS_M = 6371000.0


def latlon_to_xy_m(lat, lon, lat0, lon0):
    """Local equirectangular projection (x east, y north, meters) around (lat0, lon0); fine for a few km."""
    lat, lon = np.asarray(lat, dtype=float), np.asarray(lon, dtype=float)
    x = EARTH_RADIUS_M * np.radians(lon - lon0) * np.cos(np.radians(lat0))
    y = EARTH_RADIUS_M * np.radians(lat - lat0)
    return x, y


def load_farm(path, name):
    """One real farm of qollab/data/farms.json: {"farms": {name: {rotor_diameter_m, turbines: [{id, latitude, longitude}]}}}."""
    with open(path, "r", encoding="utf-8") as f:
        farm = json.load(f)["farms"][name]
    return dict(farm, name=name)


def farm_coords_D(farm):
    """Turbine positions of a farm as (x east, y north) in rotor diameters, relative to the centroid."""
    lat = [t["latitude"] for t in farm["turbines"]]
    lon = [t["longitude"] for t in farm["turbines"]]
    x, y = latlon_to_xy_m(lat, lon, float(np.mean(lat)), float(np.mean(lon)))
    D = float(farm["rotor_diameter_m"])
    return [(float(a) / D, float(b) / D) for a, b in zip(x, y)]


def select_closest_to_centroid(ids, coords, n):
    """
    Fixed sub-instance rule: keep the n positions closest to the centroid of all positions (ties broken by the
    original order of `ids`). Returns (ids, coords) of the kept cells in their ORIGINAL order, ids preserved.
    """
    if not 0 < n <= len(coords):
        raise ValueError(f"cannot select {n} of {len(coords)} positions")
    c = np.asarray(coords, dtype=float)
    dist = np.linalg.norm(c - c.mean(axis=0), axis=1)
    keep = sorted(sorted(range(len(c)), key=lambda i: (dist[i], i))[:n])
    return [ids[i] for i in keep], [tuple(coords[i]) for i in keep]


def build_instance(n_cells, wind_rose, seed, spacing_D=5.0, coords=None, P0=None):
    """
    Default: grid (N/2, 2) with mildly heterogeneous, seeded per-site isolated power P0 in [1, 1.2].
    With `coords` (positions in rotor diameters, e.g. a real farm) the cells sit at those positions, there is no grid
    (grid_shape = (N, 1)) and P0 defaults to 1 everywhere (no invented heterogeneity).
    """
    if coords is not None:
        P0 = np.ones(n_cells) if P0 is None else np.broadcast_to(np.asarray(P0, dtype=float), (n_cells,)).copy()
        h, J = generate_h_J(wind_rose=wind_rose, P0=P0, coords=coords)
        return Instance(h=h, J=J, grid_shape=(n_cells, 1), P0=P0)
    P0 = 1.0 + 0.2 * np.random.default_rng(seed).random(n_cells) if P0 is None else P0
    grid_shape = (n_cells // 2, 2)
    h, J = generate_h_J(grid_shape, spacing_D=spacing_D, wind_rose=wind_rose, P0=P0)
    return Instance(h=h, J=J, grid_shape=grid_shape, P0=P0)


def synthetic_instance_specs():
    """The fixed synthetic instance set: 4 sizes x 2 K values x 3 roses = 24 instances, seed = instance id."""
    specs = []
    for n, ks in SYNTHETIC_SIZES.items():
        for K in ks:
            for rose in SYNTHETIC_ROSES:
                i = len(specs)
                specs.append(InstanceSpec("synthetic", i, rose, n, K, i))
    return specs


# Extended synthetic sets (docs/PROTOCOL_EXTENSION.md), fixed before running: larger N at the same protocol.
# dataset -> (N, K values); 2 K values x 3 roses = 6 instances each, seeds 100+ so they never overlap the base set.
SYNTHETIC_EXTENDED = {"synthetic_n16": (16, (5, 8)), "synthetic_n18": (18, (6, 9))}


def extended_synthetic_specs(dataset):
    n, ks = SYNTHETIC_EXTENDED[dataset]
    first_seed = 100 if dataset == "synthetic_n16" else 110
    specs = []
    for K in ks:
        for rose in SYNTHETIC_ROSES:
            i = len(specs)
            specs.append(InstanceSpec(dataset, i, rose, n, K, first_seed + i))
    return specs
