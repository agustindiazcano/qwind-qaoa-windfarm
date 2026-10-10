"""
Build qollab/data/windrose.json from (a) hourly ERA5 100 m wind (Open-Meteo archive API JSON files) and
(b) measured 10-minute SCADA files of real farms (Greenbyte exports of the Kelmarsh / Penmanshiel Zenodo records).

Offline tool (network is used only by the download step, never by qollab/ at runtime):
    python experiments/build_windrose.py --raw <dir with <site>_<year>.json> --out qollab/data/windrose.json
    python experiments/build_windrose.py --scada kelmarsh=<dir> --scada penmanshiel=<dir>   # keeps the other sites

Frequencies = share of valid readings whose wind comes FROM each 360/n-degree sector (centered on 0, 22.5, ...);
mean_speed = mean wind speed (m/s) of the readings in that sector. SCADA: every turbine's `Wind direction (deg)`
(nacelle position + vane, absolute) and `Wind speed (m/s)` at each 10-minute stamp, all turbines pooled, readings with
a missing value dropped, no other filtering. See docs/DATA.md.
"""
import argparse
import csv
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


SCADA_YEAR = 2019   # one complete calendar year, fixed before looking at the data


def read_greenbyte(path):
    """Speed and absolute wind direction columns of one Greenbyte 10-minute turbine file (NaN rows dropped)."""
    with open(path, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
    header = next(l for l in lines if l.startswith("# Date and time"))[2:]
    cols = next(csv.reader([header]))
    i_speed, i_dir = cols.index("Wind speed (m/s)"), cols.index("Wind direction (°)")
    speed, direction = [], []
    for row in csv.reader(l for l in lines if not l.startswith("#")):
        try:
            s, d = float(row[i_speed]), float(row[i_dir])
        except ValueError:
            continue
        if np.isfinite(s) and np.isfinite(d):
            speed.append(s)
            direction.append(d)
    return speed, direction


def read_scada_dir(directory):
    """Pool the `Turbine_Data_*.csv` files of a directory (all turbines of a farm, one period)."""
    speed, direction = [], []
    for path in sorted(glob.glob(os.path.join(directory, "Turbine_Data_*.csv"))):
        s, d = read_greenbyte(path)
        speed += s
        direction += d
    if not speed:
        raise ValueError(f"no valid SCADA readings in {directory}")
    return speed, direction


def scada_site(directory, n_sectors, farm):
    speed, direction = read_scada_dir(directory)
    return {
        "source": "measured 10-minute SCADA, nacelle anemometer and wind direction (Zenodo, CC-BY-4.0)",
        "record": farm["source_record"], "period": f"{SCADA_YEAR}-01-01 to {SCADA_YEAR}-12-31",
        "n_readings": len(speed), "hub_height_m": farm["hub_heights_m"],
        "sectors": bin_sectors(speed, direction, n_sectors),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", help="directory with the ERA5 <site>_<year>.json files")
    ap.add_argument("--scada", action="append", default=[], metavar="FARM=DIR",
                    help="farm key (as in qollab/data/farms.json) = directory with its extracted SCADA csv files")
    ap.add_argument("--farms", default=os.path.join("qollab", "data", "farms.json"))
    ap.add_argument("--out", default=os.path.join("qollab", "data", "windrose.json"))
    ap.add_argument("--sectors", type=int, default=16)
    args = ap.parse_args()
    out = {"sites": {}}
    if os.path.exists(args.out) and os.path.getsize(args.out) > 0:
        with open(args.out, "r", encoding="utf-8") as f:
            out = json.load(f)
    if args.raw:
        for site, (lat, lon) in SITES.items():
            speed, direction, meta = load_site(args.raw, site)
            n_valid = sum(1 for a, b in zip(speed, direction) if a is not None and b is not None)
            out["sites"][site] = {
                "source": "ERA5 hourly 100 m wind via Open-Meteo archive API",
                "period": f"{YEARS[0]}-01-01 to {YEARS[-1]}-12-31",
                "requested_lat_lon": [lat, lon],
                "grid_lat_lon": [meta["grid_latitude"], meta["grid_longitude"]],
                "hub_height_m": 100,
                "n_hours": n_valid,
                "sectors": bin_sectors(speed, direction, args.sectors),
            }
            print(site, n_valid, "valid hours; grid", meta)
    if args.scada:
        with open(args.farms, "r", encoding="utf-8") as f:
            farms = json.load(f)["farms"]
        for item in args.scada:
            farm, directory = item.split("=", 1)
            out["sites"][farm] = scada_site(directory, args.sectors, farms[farm])
            print(farm, out["sites"][farm]["n_readings"], "readings")
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
        f.write("\n")


if __name__ == "__main__":
    main()
