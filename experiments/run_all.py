"""
Offline benchmark: classical baselines vs QAOA variants over a fixed instance set.

Each dataset is written to its own folder, results/<dataset>/per_instance.csv + summary.json, so a run never
overwrites another dataset. `--merge` then builds the single results/summary.json (list of datasets) and
results/per_instance.csv that the website reads (schema: docs/results_schema.md).

The protocol (FULL_PROTOCOL) is fixed BEFORE running and is shared by every dataset: do not retune it
after seeing results. Datasets: "synthetic" (default) and "real_<site>" (wind rose read from
qollab/data/windrose.json; same protocol). The real sets reuse only the (N, K) pairs and seeds of the synthetic
A-rose instances (8 instances per site), not the B and C roses: the rose is the variable under study.

This script is offline-only and is never imported by qollab/.

Usage:
  python experiments/run_all.py --quick                  # tiny smoke run -> results/synthetic/, status "smoke"
  python experiments/run_all.py --jobs 4                 # full synthetic protocol (heavy, ~1 h serial)
  python experiments/run_all.py --dataset real_chubut    # site defaults to the name after "real_"
  python experiments/run_all.py --dataset real_bahia_blanca
  python experiments/run_all.py --merge                  # results/<dataset>/ -> results/summary.json + per_instance.csv
"""
import argparse
import csv
import json
import os
import platform
import re
import sys
from concurrent.futures import ProcessPoolExecutor
from math import comb

import numpy as np
import scipy
import qiskit

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "qollab"))

from qwind.qubo import build_qubo  # noqa: E402
from qwind.classical import exact_enumeration, simulated_annealing, greedy_local_search  # noqa: E402
from qwind.qaoa import run_qaoa, energy_table  # noqa: E402
from qwind.instances import (  # noqa: E402
    InstanceSpec, SYNTHETIC_ROSES, build_instance, load_wind_rose, synthetic_instance_specs)

DATASET_RE = re.compile(r"^(synthetic|real_[a-z0-9_]+)$")

FULL_PROTOCOL = {
    "id": "qwind-v1",
    "depths": [1, 2, 3],
    "restarts": 2,
    "maxiter": 60,
    "shots": 1000,
    "lam_ref_mult": 10.0,           # reference QUBO used for every metric: lam = 10 * max|h|
    "lam_multipliers": [1.0, 3.0, 10.0],
    "ramp_total_time_factor": 0.75,  # placeholder from the TQA idea, not tuned (see docs/model.md)
    "sa_reads": 5,
}
QUICK_PROTOCOL = dict(FULL_PROTOCOL, id="qwind-v1-quick", depths=[1], restarts=1, maxiter=20, shots=200)

CAVEATS = [
    "Pairwise-additive Jensen wake losses (documented approximation, docs/model.md).",
    "Small instances (6-12 cells) on an ideal statevector simulator; no hardware, no noise.",
    "No quantum advantage is claimed. At these sizes classical methods solve the problem exactly in milliseconds.",
    "Random feasible sampling with the same number of shots also finds the optimum almost surely; compare the distributions (P(optimal), approximation ratio), not the best sample.",
    "QAOA with the XY mixer and Dicke start uses a generic exponential-size state preparation in this simulation.",
    "The 95% intervals are normal approximations over instances.",
    "Real datasets use a real wind rose (ERA5 100 m, docs/DATA.md) on a synthetic grid of candidate cells, not a real farm layout; the wake model does not use mean wind speed yet.",
]


def variants(protocol):
    """The QAOA variants of the protocol, in a fixed order."""
    out = [dict(name=f"penalty+x lam={m:g}", mixer="x", init="plus", init_params="random", lam_mult=m)
           for m in protocol["lam_multipliers"]]
    out.append(dict(name=f"penalty+x lam={protocol['lam_multipliers'][-1]:g} ramp", mixer="x", init="plus",
                    init_params="ramp", lam_mult=protocol["lam_multipliers"][-1]))
    out.append(dict(name="xy+dicke", mixer="xy", init="dicke", init_params="random", lam_mult=0.0))
    out.append(dict(name="xy+dicke ramp", mixer="xy", init="dicke", init_params="ramp", lam_mult=0.0))
    return out


def uniform_feasible_baseline(Q, n, K):
    """Uniform distribution over the C(N,K) feasible bitstrings: P(optimal) and feasible-only ratio."""
    table = energy_table(Q, n)
    feas = np.array([bin(i).count("1") for i in range(2 ** n)]) == K
    ef = table[feas]
    n_opt = int(np.isclose(ef, ef.min()).sum())
    ratio = 1.0 if ef.max() == ef.min() else (ef.max() - ef.mean()) / (ef.max() - ef.min())
    return n_opt / comb(n, K), float(ratio)


def _row(spec, grid_shape, **kw):
    base = dict(dataset=spec.dataset, instance_id=spec.instance_id, wind_rose=spec.wind_rose, N=spec.N,
                K=spec.K, grid_rows=grid_shape[0], grid_cols=grid_shape[1], seed=spec.seed,
                method="", variant="", p="", lam_mult="", energy_best="", energy_gap="", p_optimal="",
                p_feasible="", approx_ratio_feasible="", uniform_feasible_p_optimal="",
                uniform_feasible_ratio="", random_p_hit="", n_evals="", shots="", time_s="")
    base.update(kw)
    return base


def rose_for(spec, windrose_path=None):
    if spec.dataset == "synthetic":
        return SYNTHETIC_ROSES[spec.wind_rose]
    return load_wind_rose(windrose_path or os.path.join(ROOT, "qollab", "data", "windrose.json"), spec.wind_rose)


def run_instance(spec, protocol, windrose_path=None):
    """All rows (classical + every QAOA variant and depth) of one instance."""
    import time
    inst = build_instance(spec.N, rose_for(spec, windrose_path), spec.seed)
    n, K = spec.N, spec.K
    hmax = float(np.abs(inst.h).max())
    Q_ref = build_qubo(inst.h, inst.J, protocol["lam_ref_mult"] * hmax, K)
    rows = []

    t = time.perf_counter()
    _, e_opt = exact_enumeration(Q_ref, n)
    rows.append(_row(spec, inst.grid_shape, method="exact", variant="exact", energy_best=e_opt, energy_gap=0.0,
                     n_evals=2 ** n, time_s=time.perf_counter() - t))
    t = time.perf_counter()
    _, e_sa = simulated_annealing(Q_ref, n, K, num_reads=protocol["sa_reads"])
    rows.append(_row(spec, inst.grid_shape, method="sa", variant="sa", energy_best=e_sa, energy_gap=e_sa - e_opt,
                     n_evals=protocol["sa_reads"] * 1001, time_s=time.perf_counter() - t))
    t = time.perf_counter()
    _, e_gr = greedy_local_search(Q_ref, n, K)
    rows.append(_row(spec, inst.grid_shape, method="greedy", variant="greedy", energy_best=e_gr,
                     energy_gap=e_gr - e_opt, time_s=time.perf_counter() - t))

    u_popt, u_ratio = uniform_feasible_baseline(Q_ref, n, K)
    for p in protocol["depths"]:
        for v in variants(protocol):
            Q_cost = build_qubo(inst.h, inst.J, v["lam_mult"] * hmax, K)
            res = run_qaoa(Q_ref, n, K, p=p, restarts=protocol["restarts"], maxiter=protocol["maxiter"],
                           shots=protocol["shots"], seed=spec.seed, mixer=v["mixer"], init=v["init"],
                           init_params=v["init_params"], cost_Q=Q_cost,
                           total_time=protocol["ramp_total_time_factor"] * p)
            rows.append(_row(
                spec, inst.grid_shape, method="qaoa", variant=v["name"], p=p, lam_mult=v["lam_mult"],
                energy_best=res.best_sampled_energy, energy_gap=res.best_sampled_energy - res.e_min,
                p_optimal=res.p_optimal, p_feasible=res.p_feasible,
                approx_ratio_feasible=res.approx_ratio_feasible, uniform_feasible_p_optimal=u_popt,
                uniform_feasible_ratio=u_ratio, random_p_hit=res.random_p_hit, n_evals=res.nfev,
                shots=res.shots, time_s=res.wall_time))
    return rows


def _run_instance_job(args):
    return run_instance(*args)


def run_all(specs, protocol, jobs=1, windrose_path=None):
    """Rows of all instances, ordered by instance id (independent of the number of jobs)."""
    work = [(s, protocol, windrose_path) for s in specs]
    if jobs > 1:
        with ProcessPoolExecutor(max_workers=jobs) as ex:
            results = list(ex.map(_run_instance_job, work))
    else:
        results = [_run_instance_job(w) for w in work]
    return [row for rows in results for row in rows]


COLUMNS = ["dataset", "instance_id", "wind_rose", "N", "K", "grid_rows", "grid_cols", "seed", "method", "variant",
           "p", "lam_mult", "energy_best", "energy_gap", "p_optimal", "p_feasible", "approx_ratio_feasible",
           "uniform_feasible_p_optimal", "uniform_feasible_ratio", "random_p_hit", "n_evals", "shots", "time_s"]
QAOA_METRICS = ["p_optimal", "p_feasible", "approx_ratio_feasible", "n_evals", "time_s"]
CLASSICAL_METRICS = ["energy_gap", "time_s"]


def _stats(values):
    v = np.array(values, dtype=float)
    mean, std = float(v.mean()), float(v.std())
    half = 1.96 * std / np.sqrt(len(v))
    return {"mean": mean, "std": std, "ci95_low": mean - half, "ci95_high": mean + half}


def aggregate(rows):
    results = []
    keys = list(dict.fromkeys((r["dataset"], r["method"], r["variant"], r["p"]) for r in rows))
    for dataset, method, variant, p in keys:
        sel = [r for r in rows if (r["dataset"], r["method"], r["variant"], r["p"]) == (dataset, method, variant, p)]
        quantum = method == "qaoa"
        rec = {"dataset": dataset, "method": method, "variant": variant, "p": p if quantum else None,
               "n_instances": len(sel),
               "metrics": {m: _stats([r[m] for r in sel]) for m in (QAOA_METRICS if quantum else CLASSICAL_METRICS)}}
        if quantum:
            rec["baselines"] = {k: float(np.mean([r[k] for r in sel]))
                                for k in ("uniform_feasible_p_optimal", "uniform_feasible_ratio", "random_p_hit")}
            rec["frac_beating_uniform_ratio"] = float(
                np.mean([r["approx_ratio_feasible"] > r["uniform_feasible_ratio"] for r in sel]))
            rec["frac_beating_uniform_p_optimal"] = float(
                np.mean([r["p_optimal"] > r["uniform_feasible_p_optimal"] for r in sel]))
        results.append(rec)
    return results


def write_outputs(out_dir, specs, protocol, rows):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "per_instance.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    status = "smoke" if protocol["id"].endswith("-quick") else "final"
    summary = {
        "schema_version": "1.0",
        "status": status,
        "protocol": dict(protocol, variants=[v["name"] for v in variants(protocol)]),
        "environment": {"python": platform.python_version(), "qiskit": qiskit.__version__,
                        "numpy": np.__version__, "scipy": scipy.__version__},
        "datasets": [{"dataset": d, "status": status, "n_instances": sum(s.dataset == d for s in specs)}
                     for d in sorted({s.dataset for s in specs})],
        "instances": [dict(dataset=s.dataset, instance_id=s.instance_id, wind_rose=s.wind_rose, N=s.N, K=s.K,
                           grid_rows=s.N // 2, grid_cols=2, seed=s.seed) for s in specs],
        "results": aggregate(rows),
        "caveats": CAVEATS,
    }
    with open(os.path.join(out_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
        f.write("\n")


def dataset_dir(base, dataset):
    return os.path.join(base, dataset)


def site_from_dataset(dataset):
    """'real_chubut' -> 'chubut' (the site key in qollab/data/windrose.json)."""
    if not dataset.startswith("real_"):
        raise ValueError(f"{dataset!r} is not a real_<site> dataset")
    return dataset[len("real_"):]


def merge_results(base, out):
    """
    Merge results/<dataset>/{summary.json, per_instance.csv} (every sub-folder of `base` that has them) into
    `out`/summary.json (list of datasets) and `out`/per_instance.csv. All datasets must share the same protocol.
    """
    parts = []
    for name in sorted(os.listdir(base)):
        d = os.path.join(base, name)
        if not DATASET_RE.match(name):   # only folders named after a dataset (skips figures/, other outputs)
            continue
        if os.path.isfile(os.path.join(d, "summary.json")) and os.path.isfile(os.path.join(d, "per_instance.csv")):
            with open(os.path.join(d, "summary.json"), encoding="utf-8") as f:
                summary = json.load(f)
            with open(os.path.join(d, "per_instance.csv"), newline="", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
            parts.append((summary, rows))
    if not parts:
        raise ValueError(f"no dataset folders with summary.json and per_instance.csv in {base}")
    protocol = parts[0][0]["protocol"]
    if any(s["protocol"] != protocol for s, _ in parts):
        raise ValueError("datasets were run with different protocols; refusing to merge")
    datasets = [d for s, _ in parts for d in s["datasets"]]
    merged = {
        "schema_version": parts[0][0]["schema_version"],
        "status": "final" if all(d["status"] == "final" for d in datasets) else "smoke",
        "protocol": protocol,
        "environment": parts[0][0]["environment"],
        "datasets": sorted(datasets, key=lambda d: d["dataset"]),
        "instances": [i for s, _ in parts for i in s["instances"]],
        "results": [r for s, _ in parts for r in s["results"]],
        "caveats": list(dict.fromkeys(c for s, _ in parts for c in s["caveats"])),
    }
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "per_instance.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        for _, rows in parts:
            w.writerows(rows)
    with open(os.path.join(out, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2)
        f.write("\n")
    return merged


def real_instance_specs(dataset, site):
    """
    Same (N, K) pairs and seeds as the synthetic A-rose instances only (8 instances per site: N = 6, 8, 10, 12 x 2 K),
    with the rose of one real site. The synthetic B and C roses have no real counterpart.
    """
    return [InstanceSpec(dataset, s.instance_id, site, s.N, s.K, s.seed) for s in synthetic_instance_specs()
            if s.wind_rose == "A"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true", help="tiny smoke run (2 instances, p=1), status 'smoke'")
    ap.add_argument("--jobs", type=int, default=1, help="processes (one instance per task)")
    ap.add_argument("--dataset", default="synthetic", help="'synthetic' or 'real_<site>'")
    ap.add_argument("--site", help="site key in qollab/data/windrose.json (default: the name after 'real_')")
    ap.add_argument("--out", help="output folder (default: results/<dataset>)")
    ap.add_argument("--merge", action="store_true",
                    help="merge results/<dataset>/ folders into results/summary.json + per_instance.csv and exit")
    args = ap.parse_args()

    results_dir = os.path.join(ROOT, "results")
    if args.merge:
        merged = merge_results(results_dir, results_dir)
        print(f"merged {[d['dataset'] for d in merged['datasets']]} -> {results_dir} (status: {merged['status']})")
        return

    protocol = QUICK_PROTOCOL if args.quick else FULL_PROTOCOL
    specs = (synthetic_instance_specs() if args.dataset == "synthetic"
             else real_instance_specs(args.dataset, args.site or site_from_dataset(args.dataset)))
    if args.quick:
        specs = [s for s in specs if s.N == 6][:2]
    rows = run_all(specs, protocol, jobs=args.jobs)
    out = args.out or dataset_dir(results_dir, args.dataset)
    write_outputs(out, specs, protocol, rows)
    print(f"{len(specs)} instances, {len(rows)} rows -> {out} (status: "
          f"{'smoke' if args.quick else 'final'})")


if __name__ == "__main__":
    main()
