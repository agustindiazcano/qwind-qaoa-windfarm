"""
Markdown tables for the README / Qollab page, generated from results/summary.json and results/per_instance.csv
(nothing is typed by hand).

    python scripts/make_results_tables.py                      # writes results/results_tables.md

Per dataset: QAOA vs the uniform-over-feasible baseline (all variants and depths), evaluation budgets per method, and,
for datasets with few instances, every instance on its own (no mean or interval over so few). Standard library only.
"""
import argparse
import csv
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FEW_INSTANCES = 5          # up to this many instances a dataset is listed one by one
LISTED_VARIANTS = ("xy+dicke", "penalty+x lam=10")


def _md(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def qaoa_table(summary, dataset):
    recs = [r for r in summary["results"] if r["dataset"] == dataset and r["method"] == "qaoa"]
    if not recs:
        raise ValueError(f"no QAOA results for dataset {dataset!r}")
    header = ["variant", "p", "instances", "P(optimal)", "uniform P(optimal)", "P(feasible)",
              "approx. ratio (feasible)", "uniform approx. ratio", "beat uniform ratio", "beat uniform P(optimal)",
              "optimizer evaluations"]
    rows = []
    for r in recs:
        n, m, b = r["n_instances"], r["metrics"], r["baselines"]
        rows.append([r["variant"], r["p"], n, f"{m['p_optimal']['mean']:.3f}", f"{b['uniform_feasible_p_optimal']:.3f}",
                     f"{m['p_feasible']['mean']:.3f}", f"{m['approx_ratio_feasible']['mean']:.3f}",
                     f"{b['uniform_feasible_ratio']:.3f}", f"{round(r['frac_beating_uniform_ratio'] * n)}/{n}",
                     f"{round(r['frac_beating_uniform_p_optimal'] * n)}/{n}", f"{m['n_evals']['mean']:.0f}"])
    return _md(header, rows)


def per_instance_table(rows, dataset, variant):
    sel = [r for r in rows if r["dataset"] == dataset and r["method"] == "qaoa" and r["variant"] == variant]
    if not sel:
        raise ValueError(f"no rows for {dataset!r} / {variant!r}")
    sel.sort(key=lambda r: (int(r["K"]), int(r["p"])))
    header = ["K", "N", "p", "P(optimal)", "uniform P(optimal)", "approx. ratio (feasible)", "uniform approx. ratio",
              "optimizer evaluations"]
    return _md(header, [[r["K"], r["N"], r["p"], f"{float(r['p_optimal']):.3f}",
                         f"{float(r['uniform_feasible_p_optimal']):.3f}", f"{float(r['approx_ratio_feasible']):.3f}",
                         f"{float(r['uniform_feasible_ratio']):.3f}", r["n_evals"]] for r in sel])


def budget_table(rows, dataset):
    """Mean objective evaluations, energy gap and time per method. The budgets are NOT matched across methods."""
    out = []
    for method in ("exact", "sa", "greedy", "qaoa"):
        sel = [r for r in rows if r["dataset"] == dataset and r["method"] == method]
        if not sel:
            continue
        evals = [float(r["n_evals"]) for r in sel if r["n_evals"] != ""]
        out.append([method, f"{sum(evals) / len(evals):.0f}" if evals else "n/a",
                    f"{sum(float(r['energy_gap']) for r in sel) / len(sel):.4f}",
                    f"{sum(float(r['time_s']) for r in sel) / len(sel):.3f}"])
    return _md(["method", "mean evaluations", "mean energy gap", "mean time (s)"], out)


def _range(values, n):
    lo, hi = min(values), max(values)
    return f"{lo}/{n}" if lo == hi else f"{lo}-{hi}/{n}"


def readme_block(summary, rows, datasets=None):
    """Condensed README tables (every number read from the files). Few-instance datasets are not summarized as mean +/- interval."""
    present = [d["dataset"] for d in summary["datasets"]]
    names = [d for d in (README_ORDER if datasets is None else datasets) if d in present]   # default: the first batch only
    p_top = max(summary["protocol"]["depths"])      # compact headline: the deepest circuit; all depths are in results_tables.md
    n_inst = {d["dataset"]: d["n_instances"] for d in summary["datasets"]}
    out = ["**Datasets** (short name used in the tables below; the full name is the dataset id in `results/`)", "",
           _md(["name", "dataset", "country", "what it is", "source", "instances"],
               [[SHORT_NAMES.get(n, n), f"`{n}`", COUNTRIES.get(n, ""), DESCRIPTIONS.get(n, ""), SOURCES.get(n, ""), n_inst[n]]
                for n in names]), "",
           f"**Constraint-preserving QAOA (XY mixer + Dicke start) against the uniform-over-feasible baseline, depth p = {p_top}**", ""]
    a_rows = []
    for name in names:
        for r in summary["results"]:
            if r["dataset"] == name and r["method"] == "qaoa" and r["variant"] == "xy+dicke" and r["p"] == p_top:
                n, m, b = r["n_instances"], r["metrics"], r["baselines"]
                a_rows.append([SHORT_NAMES.get(name, name), n, f"{m['p_optimal']['mean']:.3f}", f"{b['uniform_feasible_p_optimal']:.3f}",
                               f"{m['approx_ratio_feasible']['mean']:.3f}", f"{b['uniform_feasible_ratio']:.3f}",
                               f"{round(r['frac_beating_uniform_ratio'] * n)}/{n}",
                               f"{round(r['frac_beating_uniform_p_optimal'] * n)}/{n}", f"{m['n_evals']['mean']:.0f}"])
    out += [_md(["dataset", "instances", "P(optimal)", "uniform P(optimal)", "approx. ratio (feasible)",
                 "uniform ratio", "beat uniform ratio", "beat uniform P(optimal)", "evaluations"], a_rows), ""]

    out += ["**Penalty QAOA (X mixer), all settings of the sweep** (penalty weight 1, 3 and 10 times max|h|, plus one "
            "ramp variant; p = 1-3). Range of instances that beat the uniform baseline over settings and depths:", ""]
    b_rows = []
    for name in names:
        pen = [r for r in summary["results"] if r["dataset"] == name and r["method"] == "qaoa" and r["variant"].startswith("penalty")]
        n = pen[0]["n_instances"]
        cnt = lambda key: [round(r[key] * n) for r in pen]
        b_rows.append([SHORT_NAMES.get(name, name), n, len({r["variant"] for r in pen}), _range(cnt("frac_beating_uniform_ratio"), n),
                       _range(cnt("frac_beating_uniform_p_optimal"), n),
                       f"{min(r['metrics']['p_feasible']['mean'] for r in pen):.2f}-{max(r['metrics']['p_feasible']['mean'] for r in pen):.2f}"])
    out += [_md(["dataset", "instances", "settings", "beat uniform ratio", "beat uniform P(optimal)", "P(feasible) range"], b_rows), ""]

    out += [f"**Final solution quality against the classical methods** (gap to the exact optimum, mean over the instances of each "
            f"dataset; XY + Dicke at depth p = {p_top}, best layout of its 1000 samples). The budgets are not matched: simulated "
            f"annealing uses far more objective evaluations than QAOA, and random feasible sampling uses the same 1000 samples "
            f"as QAOA:", ""]
    c_rows = []
    for name in names:
        def stat(method, col, variant=None, p=None):
            sel = [r for r in rows if r["dataset"] == name and r["method"] == method and r[col] != ""
                   and (variant is None or r["variant"] == variant) and (p is None or r["p"] == str(p))]
            return sum(float(r[col]) for r in sel) / len(sel) if sel else None
        xy = [r for r in rows if r["dataset"] == name and r["variant"] == "xy+dicke" and r["p"] == str(p_top)]
        found = sum(1 for r in xy if abs(float(r["energy_gap"])) < 1e-9)
        c_rows.append([SHORT_NAMES.get(name, name), f"{stat('sa', 'energy_gap'):.4f}", f"{stat('sa', 'n_evals'):.0f}",
                       f"{stat('greedy', 'energy_gap'):.4f}", f"{stat('qaoa', 'energy_gap', 'xy+dicke', p_top):.4f}",
                       f"{found}/{len(xy)}", f"{stat('qaoa', 'random_p_hit', 'xy+dicke', p_top):.2f}",
                       f"{stat('qaoa', 'n_evals', 'xy+dicke', p_top):.0f}"])
    out += [_md(["dataset", "SA gap", "SA evaluations", "greedy gap", "XY+Dicke best-sample gap", "XY+Dicke found the optimum",
                 "random feasible sampling finds the optimum (probability)", "XY+Dicke evaluations"], c_rows)]
    return "\n".join(out)


def headline_multipliers(summary, rows, datasets=None):
    """Numbers quoted in the README prose, at the deepest p: how many times higher P(optimal) is for XY + Dicke than for the
    uniform baseline and than for the best penalty variant (range over datasets), and in how many datasets its best sample is
    the exact optimum in every instance."""
    p_top = max(summary["protocol"]["depths"])
    vs_uniform, vs_penalty, all_found = [], [], 0
    present = [d["dataset"] for d in summary["datasets"]]
    names = [d for d in (README_ORDER if datasets is None else datasets) if d in present]
    for d in names:
        xy = next(r for r in summary["results"] if r["dataset"] == d and r["variant"] == "xy+dicke" and r["p"] == p_top)
        pen = max(r["metrics"]["p_optimal"]["mean"] for r in summary["results"]
                  if r["dataset"] == d and r["method"] == "qaoa" and r["variant"].startswith("penalty") and r["p"] == p_top)
        p = xy["metrics"]["p_optimal"]["mean"]
        vs_uniform.append(p / xy["baselines"]["uniform_feasible_p_optimal"])
        vs_penalty.append(p / pen)
        sel = [r for r in rows if r["dataset"] == d and r["variant"] == "xy+dicke"]      # every depth and instance of the dataset
        if sel and all(abs(float(r["energy_gap"])) < 1e-9 for r in sel):
            all_found += 1
    return {"vs_uniform": (min(vs_uniform), max(vs_uniform)), "vs_penalty": (min(vs_penalty), max(vs_penalty)),
            "found_optimum_datasets": all_found, "datasets": len(names)}


START, END = "<!-- RESULTS:START -->", "<!-- RESULTS:END -->"
START2, END2 = "<!-- RESULTS2:START -->", "<!-- RESULTS2:END -->"      # second batch (docs/PROTOCOL_EXTENSION.md)
BATCH2 = ["real_penmanshiel_allk", "synthetic_n16"]


def batch2_datasets(summary):
    present = {d["dataset"] for d in summary["datasets"]}
    return [d for d in BATCH2 if d in present]
# Order of the datasets in the README tables: the synthetic set, the real farms, then the secondary ERA5 sets
README_ORDER = ["synthetic", "real_penmanshiel", "real_penmanshiel_sub10", "real_kelmarsh", "real_chubut", "real_bahia_blanca"]
# Short names used in the README tables (the full dataset id is the index in the legend table)
SHORT_NAMES = {"real_penmanshiel_allk": "Penmanshiel-allK", "synthetic_n16": "Synthetic-16", "synthetic": "Synthetic", "real_penmanshiel": "Penmanshiel", "real_penmanshiel_sub10": "Penmanshiel-10",
               "real_kelmarsh": "Kelmarsh", "real_chubut": "Chubut", "real_bahia_blanca": "Bahia"}
ZENODO = "[Zenodo](https://doi.org/10.5281/zenodo.%s), CC BY 4.0"
ERA5 = ("[ERA5](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels) via "
        "[Open-Meteo](https://open-meteo.com/en/docs/historical-weather-api), CC BY 4.0")
GENERATED = "Generated by us, see `docs/DATA.md`"
# Country of each dataset and where its data comes from (shown in the README legend; details in docs/DATA.md)
COUNTRIES = {"synthetic": "n/a", "synthetic_n16": "n/a", "real_penmanshiel": "Scotland, UK",
             "real_penmanshiel_sub10": "Scotland, UK", "real_penmanshiel_allk": "Scotland, UK",
             "real_kelmarsh": "England, UK", "real_chubut": "Argentina", "real_bahia_blanca": "Argentina"}
SOURCES = {"synthetic": GENERATED, "synthetic_n16": GENERATED,
           "real_penmanshiel": ZENODO % "16807304", "real_penmanshiel_sub10": ZENODO % "16807304",
           "real_penmanshiel_allk": ZENODO % "16807304", "real_kelmarsh": ZENODO % "16807551",
           "real_chubut": ERA5, "real_bahia_blanca": ERA5}
DESCRIPTIONS = {
    "real_penmanshiel_allk": "All 14 real Penmanshiel positions with every K from 3 to 11 (9 instances)",
    "synthetic_n16": "Synthetic roses on a synthetic grid with N = 16 (6 instances)",
    "synthetic": "Synthetic wind roses on a synthetic grid",
    "real_penmanshiel": "All 14 real turbine positions of the Penmanshiel farm, measured wind rose",
    "real_penmanshiel_sub10": "The 10 Penmanshiel turbines closest to the farm centroid (a subset)",
    "real_kelmarsh": "The 6 real turbines of the Kelmarsh farm, measured wind rose (trivial contrast)",
    "real_chubut": "ERA5 wind rose of the Chubut coast on a synthetic grid (secondary)",
    "real_bahia_blanca": "ERA5 wind rose of Bahia Blanca on a synthetic grid (secondary)",
}


def update_readme(path, block, start=START, end=END):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    if start not in text or end not in text:
        raise ValueError(f"{path} needs the {start} ... {end} markers (RESULTS block)")
    head, rest = text.split(start, 1)
    _, tail = rest.split(end, 1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(head + start + "\n" + block + "\n" + end + tail)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=os.path.join(ROOT, "results"))
    ap.add_argument("--out", default=os.path.join(ROOT, "results", "results_tables.md"))
    ap.add_argument("--readme", help="also rewrite the RESULTS block of this README")
    args = ap.parse_args(argv)
    with open(os.path.join(args.results, "summary.json"), encoding="utf-8") as f:
        summary = json.load(f)
    with open(os.path.join(args.results, "per_instance.csv"), newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    env = summary["environment"]
    parts = [
        "# Results tables",
        "",
        f"Generated from results/summary.json and results/per_instance.csv by scripts/make_results_tables.py. "
        f"Protocol {summary['protocol']['id']}, status {summary['status']}, Python {env['python']}, Qiskit {env['qiskit']}, "
        f"NumPy {env['numpy']}, SciPy {env['scipy']}. Do not edit by hand.",
        "",
        "Evaluation budgets are not matched across methods (simulated annealing uses far more objective evaluations "
        "than QAOA). Datasets are never averaged together.",
    ]
    for d in summary["datasets"]:
        name = d["dataset"]
        parts += ["", f"## {name} ({d['n_instances']} instances, status {d['status']})", "",
                  "### QAOA against the uniform-over-feasible baseline", "", qaoa_table(summary, name), "",
                  "### Evaluation budget per method", "", budget_table(rows, name)]
        if d["n_instances"] <= FEW_INSTANCES:
            for v in LISTED_VARIANTS:
                parts += ["", f"### Every instance, {v}", "", per_instance_table(rows, name, v)]
    with open(args.out, "w", encoding="utf-8") as f:
        f.write("\n".join(parts) + "\n")
    print("wrote", args.out)
    if args.readme:
        update_readme(args.readme, readme_block(summary, rows))
        print("updated", args.readme)
        second = batch2_datasets(summary)
        if second and START2 in open(args.readme, encoding="utf-8").read():
            update_readme(args.readme, readme_block(summary, rows, datasets=second), START2, END2)
            print("updated the second-batch block of", args.readme)


if __name__ == "__main__":
    main()
