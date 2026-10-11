"""
Figures for the README and the Qollab page, generated from results/summary.json and results/per_instance.csv.

    python experiments/make_figures.py            # writes results/figures/*.png

Offline tool (matplotlib is not available inside qollab/). Only the first batch of datasets is drawn (the same six as the
README tables). Colors are the validated categorical slots 1-3 of the reference palette (blue, orange, aqua), checked with
scripts/validate_palette.js; the aqua mark is below 3:1 contrast on the light surface, so every bar carries its value.
"""
import argparse
import csv
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import make_results_tables as tables  # noqa: E402

SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e1"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
PENALTY = "penalty+x lam=10"     # the reference penalty variant of the protocol (weight 10 x max|h|)


def _found_share(rows, dataset, variant, p):
    sel = [r for r in rows if r["dataset"] == dataset and r["variant"] == variant and r["p"] == str(p)]
    return 100.0 * sum(abs(float(r["energy_gap"])) < 1e-9 for r in sel) / len(sel)


def figure_data(summary, rows):
    """Every number drawn in the figures, read from the result files (p = the deepest circuit of the protocol)."""
    p = max(summary["protocol"]["depths"])
    present = {d["dataset"] for d in summary["datasets"]}
    names = [d for d in tables.README_ORDER if d in present]
    labels = [tables.SHORT_NAMES[d] for d in names]
    res = lambda d, v, q=p: next(r for r in summary["results"] if r["dataset"] == d and r["variant"] == v and r["p"] == q)

    vs_uniform, vs_penalty = [], []
    for d in names:
        xy = res(d, "xy+dicke")
        best_pen = max(r["metrics"]["p_optimal"]["mean"] for r in summary["results"]
                       if r["dataset"] == d and r["method"] == "qaoa" and r["variant"].startswith("penalty") and r["p"] == p)
        vs_uniform.append(xy["metrics"]["p_optimal"]["mean"] / xy["baselines"]["uniform_feasible_p_optimal"])
        vs_penalty.append(xy["metrics"]["p_optimal"]["mean"] / best_pen)

    def random_hit(d):
        sel = [float(r["random_p_hit"]) for r in rows if r["dataset"] == d and r["variant"] == "xy+dicke" and r["p"] == str(p)]
        return 100.0 * sum(sel) / len(sel)

    depths = sorted(summary["protocol"]["depths"])
    return {
        "p": p,
        "multipliers": {"labels": labels, "vs_uniform": vs_uniform, "vs_penalty": vs_penalty},
        "chance_of_best": {"labels": labels,
                           "xy_dicke": [_found_share(rows, d, "xy+dicke", p) for d in names],
                           "penalty": [_found_share(rows, d, PENALTY, p) for d in names],
                           "random": [random_hit(d) for d in names]},
        "valid_plans": {"labels": labels,
                        "xy_dicke": [100.0 * res(d, "xy+dicke")["metrics"]["p_feasible"]["mean"] for d in names],
                        "penalty": [100.0 * res(d, PENALTY)["metrics"]["p_feasible"]["mean"] for d in names]},
        "depth": {"p": depths,
                  "xy_dicke": [res("synthetic", "xy+dicke", q)["metrics"]["p_optimal"]["mean"] for q in depths],
                  "penalty": [res("synthetic", PENALTY, q)["metrics"]["p_optimal"]["mean"] for q in depths],
                  "uniform": res("synthetic", "xy+dicke", depths[-1])["baselines"]["uniform_feasible_p_optimal"]},
    }


# ----------------------------------------------------------------------------------------------- drawing

def _style(ax, title, subtitle):
    ax.figure.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=INK2, length=0)
    ax.figure.text(0.015, 0.965, title, color=INK, fontsize=14, fontweight="bold", va="top")
    ax.figure.text(0.015, 0.905, subtitle, color=INK2, fontsize=9.5, va="top")


def _grouped_hbars(labels, series, title, subtitle, xlabel, fmt, xmax, path):
    """Horizontal grouped bars: one group per dataset, one thin bar per series, value written at the end of each bar."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    n, k = len(labels), len(series)
    fig, ax = plt.subplots(figsize=(8.6, 1.4 + 0.62 * n * (0.55 + 0.2 * k)))
    h = 0.2
    for j, (name, vals, color) in enumerate(series):
        ys = [i + (j - (k - 1) / 2) * (h + 0.03) for i in range(n)]
        ax.barh(ys, vals, height=h, color=color, label=name, zorder=3)
        for y, v in zip(ys, vals):
            ax.text(v + xmax * 0.012, y, fmt(v), va="center", color=INK, fontsize=9)
    ax.set_yticks(range(n))
    ax.set_yticklabels(labels, color=INK, fontsize=10.5)
    ax.invert_yaxis()
    ax.set_xlim(0, xmax)
    ax.xaxis.grid(True, color=GRID, linewidth=0.8, zorder=0)
    ax.set_xlabel(xlabel, color=INK2, fontsize=9.5)
    _style(ax, title, subtitle)
    leg = ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=k, frameon=False, fontsize=9.5)
    for t in leg.get_texts():
        t.set_color(INK)
    fig.subplots_adjust(left=0.17, right=0.97, top=0.84, bottom=0.24)
    fig.savefig(path, dpi=160, facecolor=SURFACE)
    plt.close(fig)


def _depth_chart(d, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8.6, 4.4))
    pct = lambda v: [100 * x for x in v]
    ax.plot(d["p"], pct(d["xy_dicke"]), color=BLUE, linewidth=2, marker="o", markersize=9, markeredgecolor=SURFACE, markeredgewidth=2, zorder=3)
    ax.plot(d["p"], pct(d["penalty"]), color=ORANGE, linewidth=2, marker="o", markersize=9, markeredgecolor=SURFACE, markeredgewidth=2, zorder=3)
    ax.axhline(100 * d["uniform"], color=AQUA, linewidth=2, linestyle=(0, (5, 3)), zorder=2)
    ax.set_xticks(d["p"])
    ax.set_xticklabels([f"p = {q}" for q in d["p"]], color=INK, fontsize=10.5)
    ax.set_xlim(0.7, 3.95)
    top = 100 * max(d["xy_dicke"]) * 1.25
    ax.set_ylim(0, top)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8, zorder=0)
    ax.set_ylabel("Probability of sampling the best layout (%)", color=INK2, fontsize=9.5)
    for q, v in zip(d["p"], d["xy_dicke"]):
        ax.text(q, 100 * v + top * 0.035, f"{100 * v:.1f}%", ha="center", color=INK, fontsize=9.5)
    ax.text(3.08, 100 * d["xy_dicke"][-1], "XY mixer + Dicke start", color=INK, fontsize=10, va="center")
    ax.text(3.08, 100 * d["penalty"][-1], "Penalty formulation", color=INK, fontsize=10, va="center")
    ax.text(3.08, 100 * d["uniform"] + top * 0.02, "Random valid choice", color=INK, fontsize=10, va="bottom")
    _style(ax, "A deeper circuit finds the best layout more often",
           "Synthetic dataset, 24 instances: mean probability of sampling the best layout, by circuit depth p")
    fig.subplots_adjust(left=0.1, right=0.97, top=0.84, bottom=0.1)
    fig.savefig(path, dpi=160, facecolor=SURFACE)
    plt.close(fig)


def build_all(summary, rows, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    d = figure_data(summary, rows)
    p = d["p"]
    paths = []

    m = d["multipliers"]
    path = os.path.join(out_dir, "multipliers.png")
    _grouped_hbars(m["labels"], [("Random valid choice", m["vs_uniform"], BLUE), ("Best penalty version", m["vs_penalty"], ORANGE)],
                   "Up to 17 times more likely to find the best layout",
                   f"Probability of sampling the best layout with the XY mixer + Dicke circuit, as a multiple of each alternative (p = {p})",
                   "times higher", lambda v: f"{v:.1f}×", max(m["vs_penalty"] + m["vs_uniform"]) * 1.12, path)
    paths.append(path)

    c = d["chance_of_best"]
    path = os.path.join(out_dir, "chance_of_best.png")
    _grouped_hbars(c["labels"], [("XY mixer + Dicke circuit", c["xy_dicke"], BLUE), ("Penalty formulation", c["penalty"], ORANGE)],
                   "The best sample is the exact optimum",
                   f"Share of instances where the best of 1000 samples is the exact optimum, p = {p}",
                   "percent", lambda v: f"{v:.0f}%", 116, path)
    paths.append(path)

    v = d["valid_plans"]
    path = os.path.join(out_dir, "valid_plans.png")
    _grouped_hbars(v["labels"], [("XY mixer + Dicke circuit", v["xy_dicke"], BLUE), ("Penalty formulation", v["penalty"], ORANGE)],
                   "Every plan from the circuit is valid",
                   f"Share of the circuit's probability that falls on valid layouts (exactly K turbines), p = {p}",
                   "percent", lambda x: f"{x:.0f}%", 116, path)
    paths.append(path)

    path = os.path.join(out_dir, "depth.png")
    _depth_chart(d["depth"], path)
    paths.append(path)
    return paths


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=os.path.join(ROOT, "results"))
    ap.add_argument("--out", default=os.path.join(ROOT, "results", "figures"))
    args = ap.parse_args(argv)
    summary = json.load(open(os.path.join(args.results, "summary.json"), encoding="utf-8"))
    with open(os.path.join(args.results, "per_instance.csv"), newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for path in build_all(summary, rows, args.out):
        print("wrote", path)


if __name__ == "__main__":
    main()
