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


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=os.path.join(ROOT, "results"))
    ap.add_argument("--out", default=os.path.join(ROOT, "results", "results_tables.md"))
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


if __name__ == "__main__":
    main()
