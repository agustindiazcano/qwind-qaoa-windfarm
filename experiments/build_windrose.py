"""
Build qollab/data/windrose.json from hourly ERA5 100 m wind (Open-Meteo archive API JSON files).

Offline tool (network is used only by the download step, never by qollab/ at runtime):
    python experiments/build_windrose.py --raw <dir with <site>_<year>.json> --out qollab/data/windrose.json

Frequencies = share of valid hours whose wind comes FROM each 360/n-degree sector (centered on 0, 22.5, ...);
mean_speed = mean 100 m wind speed (m/s) of the hours in that sector. See docs/DATA.md.
"""
import argparse
import glob
import json
import os

import numpy as np

SITES = {
    # site key: (requested latitude, requested longitude)
    "chubut": (-45.87, -67.50),
    "bahia_blanca": (-38.72, -62.27),
}
YEARS = list(range(2015, 2025))


def bin_sectors(speed, direction, n_sectors=16):
    """Hourly speed (m/s) and meteorological FROM direction (deg) to sectors; hours with a missing value are dropped."""
    s = np.array([np.nan if v is None else v for v in speed], dtype=float)
    d = np.array([np.nan if v is None else v for v in direction], dtype=float)
    ok = ~(np.isnan(s) | np.isnan(d))
    s, d = s[ok], d[ok]
    if len(s) == 0:
        raise ValueError("no valid hours")
    width = 360.0 / n_sectors
    idx = np.floor(((d % 360.0) + width / 2) / width).astype(int) % n_sectors
    sectors = []
    for k in range(n_sectors):
        mask = idx == k
        sectors.append({
            "direction_deg": round(k * width, 4),
            "frequency": float(mask.sum() / len(s)),
            "mean_speed": float(s[mask].mean()) if mask.any() else 0.0,
        })
    return sectors


def load_site(raw_dir, site):
    speed, direction, meta = [], [], None
    for year in YEARS:
        with open(os.path.join(raw_dir, f"{site}_{year}.json"), "r", encoding="utf-8") as f:
            data = json.load(f)
        speed += data["hourly"]["wind_speed_100m"]
        direction += data["hourly"]["wind_direction_100m"]
        meta = meta or {"grid_latitude": data["latitude"], "grid_longitude": data["longitude"], "elevation_m": data["elevation"]}
    return speed, direction, meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    ap.add_argument("--out", default=os.path.join("qollab", "data", "windrose.json"))
    ap.add_argument("--sectors", type=int, default=16)
    args = ap.parse_args()
    out = {"sites": {}}
    for site, (lat, lon) in SITES.items():
        speed, direction, meta = load_site(args.raw, site)
        n_valid = sum(1 for a, b in zip(speed, direction) if a is not None and b is not None)
        sectors = bin_sectors(speed, direction, args.sectors)
        out["sites"][site] = {
            "source": "ERA5 hourly 100 m wind via Open-Meteo archive API",
            "period": f"{YEARS[0]}-01-01 to {YEARS[-1]}-12-31",
            "requested_lat_lon": [lat, lon],
            "grid_lat_lon": [meta["grid_latitude"], meta["grid_longitude"]],
            "hub_height_m": 100,
            "n_hours": n_valid,
            "sectors": sectors,
        }
        print(site, n_valid, "valid hours; grid", meta)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
        f.write("\n")


if __name__ == "__main__":
    main()
