"""
Build qollab/data/farms.json (real turbine positions) from the *_WT_static.csv files of the Zenodo records.

    python experiments/build_farms.py --penmanshiel <Penmanshiel_WT_static.csv> --kelmarsh <Kelmarsh_WT_static.csv>

Sources (CC-BY-4.0, Plumley and Takeuchi, published by Cubico Sustainable Investments Ltd), see docs/DATA.md.
Offline tool; qollab/ only reads the resulting file.
"""
import argparse
import csv
import json
import os

FARMS = {
    "penmanshiel": {"doi": "10.5281/zenodo.16807304", "record": "https://zenodo.org/records/16807304"},
    "kelmarsh": {"doi": "10.5281/zenodo.16807551", "record": "https://zenodo.org/records/16807551"},
}


def read_static(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = [r for r in csv.DictReader(f) if (r.get("Title") or "").strip()]
    if not rows:
        raise ValueError(f"no turbines in {path}")
    return rows


def farm_record(name, rows):
    diam = {float(r["Rotor Diameter (m)"]) for r in rows}
    if len(diam) != 1:
        raise ValueError("turbines with different rotor diameters are not supported")
    return {
        "source_doi": FARMS[name]["doi"], "source_record": FARMS[name]["record"], "license": "CC-BY-4.0",
        "manufacturer_model": f"{rows[0]['Manufacturer']} {rows[0]['Model']}",
        "rotor_diameter_m": diam.pop(),
        "hub_heights_m": sorted({float(r["Hub Height (m)"]) for r in rows}),
        "turbines": [{"id": r["Alternative Title"], "latitude": float(r["Latitude"]),
                      "longitude": float(r["Longitude"])} for r in rows],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--penmanshiel", required=True)
    ap.add_argument("--kelmarsh", required=True)
    ap.add_argument("--out", default=os.path.join("qollab", "data", "farms.json"))
    args = ap.parse_args()
    out = {"farms": {n: farm_record(n, read_static(getattr(args, n))) for n in FARMS}}
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
        f.write("\n")


if __name__ == "__main__":
    main()
