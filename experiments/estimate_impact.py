"""
Illustrative estimate of the energy and value at stake in the turbine-selection decision (docs/IMPACT.md).

    python experiments/estimate_impact.py --scada <dir with the extracted Penmanshiel Turbine_Data_*.csv>   # measure inputs, update docs
    python experiments/estimate_impact.py                                                                   # only update the README and docs

Inputs: (1) the measured average power of a Penmanshiel turbine in 2019 (Zenodo 10.5281/zenodo.16807304, SCADA), stored in
results/impact_inputs.json; (2) the modelled wake-loss shares of the best choice and of an average random choice of K of the 14
turbines (experiments/make_illustrations.py, exact enumeration). Output: energy and value per 1,000 hours of operation with only
K turbines, at illustrative prices. It is a scale estimate, not a forecast: see the limits in the generated text.
"""
import argparse
import csv
import glob
import json
import math
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "experiments"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import make_illustrations as ill  # noqa: E402
import make_results_tables as tables  # noqa: E402

START, END = "<!-- IMPACT:START -->", "<!-- IMPACT:END -->"
KS = (5, 7, 9)
HOURS = 1000
PRICES = (50, 75, 100)        # GBP per MWh: round numbers for illustration (docs/IMPACT.md gives the reference value); shown in USD
INPUTS = os.path.join(ROOT, "results", "impact_inputs.json")


def read_power(path):
    """The `Power (kW)` column of one Greenbyte 10-minute turbine file (missing values dropped)."""
    with open(path, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
    header = next(l for l in lines if l.startswith("# Date and time"))[2:]
    i = next(k for k, c in enumerate(next(csv.reader([header]))) if c == "Power (kW)")
    out = []
    for row in csv.reader(l for l in lines if not l.startswith("#")):
        try:
            v = float(row[i])
        except ValueError:
            continue
        if math.isfinite(v):
            out.append(v)
    return out


def power_stats(scada_dir, rated_kw):
    """Mean of each turbine's own mean power (kW), the capacity factor, and the counts."""
    means, n = [], 0
    for path in sorted(glob.glob(os.path.join(scada_dir, "Turbine_Data_*.csv"))):
        vals = read_power(path)
        if vals:
            means.append(sum(vals) / len(vals))
            n += len(vals)
    if not means:
        raise ValueError(f"no power readings in {scada_dir}")
    mean = sum(means) / len(means)
    return {"mean_power_kw": mean, "capacity_factor": mean / rated_kw, "n_turbines": len(means), "n_readings": n}


def estimate(K, mean_power_kw, loss_best, loss_avg, hours):
    """Energy the K kept turbines could produce, and how much more the best choice delivers than an average random choice."""
    potential = K * mean_power_kw / 1000.0 * hours          # MWh
    gain = potential * (loss_avg - loss_best)
    return {"K": K, "hours": hours, "potential_mwh": potential, "gain_mwh": gain,
            "gain_pct": 100.0 * ((1 - loss_best) / (1 - loss_avg) - 1), "value": lambda price: gain * price}


def usd_prices(inputs):
    """The illustrative GBP prices converted to whole US dollars per MWh at the stored rate."""
    return [round(p * inputs["fx"]["rate"]) for p in PRICES]


def impact_rows(inputs, data_dir, ks=KS, hours=HOURS):
    rows = []
    dollars = usd_prices(inputs)
    for K in ks:
        s = ill.wake_loss_stats(inputs["farm"], K, data_dir)
        e = estimate(K, inputs["mean_power_kw"], s["best"], s["average"], hours)
        rows.append({"K": K, "hours": hours, "loss_best": s["best"], "loss_avg": s["average"], "gain_mwh": e["gain_mwh"],
                     "gain_pct": e["gain_pct"], "values": {p: e["value"](p) for p in dollars}})
    return rows


def impact_block(inputs, data_dir):
    rows = impact_rows(inputs, data_dir)
    fx, dollars = inputs["fx"], usd_prices(inputs)
    table = tables._md(
        ["Turbines kept (K of 14)", "Modelled power lost to wakes: best vs average random choice", "More energy from the same K turbines",
         f"Extra energy per {HOURS:,} hours"] + [f"Value at ${p}/MWh" for p in dollars],
        [[r["K"], f"{100 * r['loss_best']:.1f}% vs {100 * r['loss_avg']:.1f}%", f"+{r['gain_pct']:.1f}%", f"{r['gain_mwh']:.0f} MWh"]
         + [f"${r['values'][p] / 1000:.1f}k" for p in dollars] for r in rows])
    return (
        f"**Illustrative estimate for Penmanshiel.** Assumptions: each kept turbine produces its measured 2019 average "
        f"({inputs['mean_power_kw']:.0f} kW, a capacity factor of {100 * inputs['capacity_factor']:.1f}%); the farm runs with only K of its "
        f"{inputs['n_turbines']} turbines for {HOURS:,} hours; the wake losses are the modelled ones, for the best choice against an "
        f"average random choice of the same K turbines; the prices are round numbers of £{PRICES[0]}, £{PRICES[1]} and £{PRICES[2]} per MWh, "
        f"shown in US dollars as ${dollars[0]}, ${dollars[1]} and ${dollars[2]} per MWh (1 GBP = {fx['rate']:.4f} USD, from the ECB euro "
        f"reference rates of {fx['date']}).\n\n{table}\n\n"
        f"This is an illustrative estimate of scale, not a forecast. It comes from a model, it compares with an average random choice "
        f"(not with what an operator does today), it assumes {HOURS:,} hours in that configuration (a year has 8,760; how many hours a "
        f"farm is curtailed is not in our data), and it counts neither costs nor the structure of any contract. Details and sources: "
        f"[docs/IMPACT.md](https://github.com/agustindiazcano/qwind-qaoa-windfarm/blob/main/docs/IMPACT.md).")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--scada", help="directory with the extracted Penmanshiel Turbine_Data_*.csv (measures the inputs)")
    ap.add_argument("--data", default=os.path.join(ROOT, "qollab", "data"))
    args = ap.parse_args(argv)
    if args.scada:
        s = power_stats(args.scada, 2050.0)
        inputs = {"farm": "penmanshiel", "year": 2019, "rated_kw": 2050, "mean_power_kw": round(s["mean_power_kw"], 1),
                  "capacity_factor": round(s["capacity_factor"], 4), "n_turbines": s["n_turbines"], "n_readings": s["n_readings"],
                  "source": "Zenodo 10.5281/zenodo.16807304 (SCADA 10-minute 'Power (kW)', calendar year 2019, mean of each turbine's mean)"}
        if os.path.exists(INPUTS):                       # keep the stored exchange rate when the power is measured again
            inputs["fx"] = json.load(open(INPUTS, encoding="utf-8")).get("fx")
        with open(INPUTS, "w", encoding="utf-8") as f:
            json.dump(inputs, f, indent=1)
            f.write("\n")
        print("wrote", INPUTS)
    with open(INPUTS, encoding="utf-8") as f:
        inputs = json.load(f)
    block = impact_block(inputs, args.data)
    for path in (os.path.join(ROOT, "README.md"), os.path.join(ROOT, "docs", "IMPACT.md")):
        if START in open(path, encoding="utf-8").read():
            tables.update_readme(path, block, START, END)
            print("updated", path)


if __name__ == "__main__":
    main()
