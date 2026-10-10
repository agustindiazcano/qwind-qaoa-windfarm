"""
Offline comparison of QAOA variants against the uniform-over-feasible baseline.

Variants (all evaluated on the SAME reference QUBO, lam_ref = 10 * max|h|):
  penalty+x        : |+>^n start, X mixer, penalty weight lam = m * max|h| for m in LAM_MULTIPLIERS
  penalty+x+ramp   : same as lam_mult=10 but with the linear-ramp parameter initialization
  xy+dicke         : Dicke start + XY mixer, lam = 0 in the circuit (constraint enforced by the ansatz)
  xy+dicke+ramp    : same with the linear-ramp initialization

Everything is seeded. Results are mean/std over instances; nothing is tuned after looking at them.
This script is offline-only and is never imported by qollab/.

Usage: python experiments/compare_qaoa_variants.py [--quick]
"""
import argparse
import csv
import os
import sys
from math import comb

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "qollab"))

from qwind.wake import generate_h_J  # noqa: E402
from qwind.qubo import build_qubo  # noqa: E402
from qwind.qaoa import run_qaoa, energy_table  # noqa: E402

WIND_ROSES = {
    "A": [(0, 0.2), (90, 0.5), (180, 0.1), (270, 0.2)],
    "B": [(0, 0.7), (180, 0.3)],
    "C": [(45, 0.4), (135, 0.3), (225, 0.2), (315, 0.1)],
}
# (N cells, K, wind rose). The instance seed is its index.
INSTANCES = [(6, 2, "A"), (6, 3, "B"), (8, 3, "A"), (8, 3, "C"), (8, 4, "B"), (10, 3, "A"), (10, 4, "C")]
DEPTHS = (1, 2, 3)
LAM_MULTIPLIERS = (1.0, 3.0, 10.0)
LAM_REF = 10.0

VARIANTS = (
    [dict(name=f"penalty+x lam={m:g}", mixer="x", init="plus", init_params="random", lam_mult=m)
     for m in LAM_MULTIPLIERS]
    + [dict(name="penalty+x lam=10 ramp", mixer="x", init="plus", init_params="ramp", lam_mult=10.0),
       dict(name="xy+dicke", mixer="xy", init="dicke", init_params="random", lam_mult=0.0),
       dict(name="xy+dicke ramp", mixer="xy", init="dicke", init_params="ramp", lam_mult=0.0)]
)

METRICS = ["p_optimal", "p_feasible", "approx_ratio_feasible", "nfev"]


def make_instance(inst_id, n, K, rose):
    rng = np.random.default_rng(inst_id)
    P0 = 1.0 + 0.2 * rng.random(n)  # mildly heterogeneous sites, seeded
    h, J = generate_h_J((n // 2, 2), spacing_D=5.0, wind_rose=WIND_ROSES[rose], P0=P0)
    return h, J


def uniform_feasible_baseline(Q, n, K):
    """Uniform distribution over the C(N,K) feasible bitstrings: P(opt) and feasible-only ratio."""
    table = energy_table(Q, n)
    feas = np.array([bin(i).count("1") for i in range(2 ** n)]) == K
    ef = table[feas]
    n_opt = int(np.isclose(ef, ef.min()).sum())
    ratio = 1.0 if ef.max() == ef.min() else (ef.max() - ef.mean()) / (ef.max() - ef.min())
    return n_opt / comb(n, K), float(ratio)


def run_all(instances, depths, maxiter, restarts, shots):
    rows = []
    for inst_id, (n, K, rose) in enumerate(instances):
        h, J = make_instance(inst_id, n, K, rose)
        hmax = np.abs(h).max()
        Q_ref = build_qubo(h, J, LAM_REF * hmax, K)
        u_popt, u_ratio = uniform_feasible_baseline(Q_ref, n, K)
        for p in depths:
            for v in VARIANTS:
                Q_cost = build_qubo(h, J, v["lam_mult"] * hmax, K)
                res = run_qaoa(Q_ref, n, K, p=p, restarts=restarts, maxiter=maxiter, shots=shots,
                               seed=inst_id, mixer=v["mixer"], init=v["init"],
                               init_params=v["init_params"], cost_Q=Q_cost)
                rows.append(dict(
                    instance=inst_id, N=n, K=K, wind_rose=rose, seed=inst_id, p=p, variant=v["name"],
                    p_optimal=res.p_optimal, p_feasible=res.p_feasible,
                    approx_ratio_feasible=res.approx_ratio_feasible,
                    uniform_feasible_p_optimal=u_popt, uniform_feasible_ratio=u_ratio,
                    random_p_hit=res.random_p_hit, nfev=res.nfev, wall_time=res.wall_time))
                print(f"inst {inst_id} N={n} K={K} p={p} {v['name']:<24} "
                      f"P(opt)={res.p_optimal:.3f} (unif {u_popt:.3f}) "
                      f"ratio_f={res.approx_ratio_feasible:.3f} (unif {u_ratio:.3f}) "
                      f"P(feas)={res.p_feasible:.3f} nfev={res.nfev}", flush=True)
    return rows


def summarize(rows):
    out = []
    for p in sorted({r["p"] for r in rows}):
        for name in dict.fromkeys(r["variant"] for r in rows):
            sel = [r for r in rows if r["p"] == p and r["variant"] == name]
            rec = dict(p=p, variant=name, n_instances=len(sel))
            for m in METRICS:
                vals = np.array([r[m] for r in sel], dtype=float)
                rec[f"{m}_mean"], rec[f"{m}_std"] = vals.mean(), vals.std()
            for m in ("uniform_feasible_p_optimal", "uniform_feasible_ratio", "random_p_hit"):
                rec[f"{m}_mean"] = float(np.mean([r[m] for r in sel]))
            rec["frac_beating_uniform_ratio"] = float(
                np.mean([r["approx_ratio_feasible"] > r["uniform_feasible_ratio"] for r in sel]))
            rec["frac_beating_uniform_p_optimal"] = float(
                np.mean([r["p_optimal"] > r["uniform_feasible_p_optimal"] for r in sel]))
            out.append(rec)
    return out


def write_csv(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true", help="tiny smoke run (2 instances, p=1)")
    ap.add_argument("--maxiter", type=int, default=60)
    ap.add_argument("--restarts", type=int, default=2)
    ap.add_argument("--shots", type=int, default=1000)
    args = ap.parse_args()
    instances, depths = (INSTANCES[:2], (1,)) if args.quick else (INSTANCES, DEPTHS)
    rows = run_all(instances, depths, args.maxiter, args.restarts, args.shots)
    suffix = "_quick" if args.quick else ""
    write_csv(os.path.join(ROOT, "results", f"qaoa_variants_per_run{suffix}.csv"), rows)
    summary = summarize(rows)
    write_csv(os.path.join(ROOT, "results", f"qaoa_variants_summary{suffix}.csv"), summary)
    print("\nSummary (mean over instances; ratio = feasible-only approximation ratio)")
    for r in summary:
        print(f"p={r['p']} {r['variant']:<24} P(opt) {r['p_optimal_mean']:.3f}"
              f" vs unif {r['uniform_feasible_p_optimal_mean']:.3f} | ratio {r['approx_ratio_feasible_mean']:.3f}"
              f" vs unif {r['uniform_feasible_ratio_mean']:.3f} | P(feas) {r['p_feasible_mean']:.3f}"
              f" | beats unif ratio in {r['frac_beating_uniform_ratio']:.0%} of instances")


if __name__ == "__main__":
    main()
