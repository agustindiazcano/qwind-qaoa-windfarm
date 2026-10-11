"""
Explanatory illustrations for the README (drawn with matplotlib, no external images):

    python experiments/make_illustrations.py          # writes results/figures/{what_is_a_wake,the_decision,how_it_works}.png

- what_is_a_wake: a turbine, its wake, and a second turbine standing in it (a schematic, not to scale).
- the_decision: the real Penmanshiel layout (positions from qollab/data/farms.json), the dominant wind direction of its
  measured rose, and the 7 of 14 turbines that the model's exact search says to keep running.
- how_it_works: the pipeline from wind and positions to the answer.

The modelled wake losses quoted next to them are the model's (Jensen wake, pairwise additive losses, equal isolated power for
every turbine, the measured Penmanshiel 2019 wind rose). They are not measured production and not money.
"""
import argparse
import itertools
import os
import sys

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "qollab"))

from qwind.instances import (build_instance, farm_coords_D, load_farm, load_wind_rose,  # noqa: E402
                             meteorological_to_toward)

SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e1"
BLUE, ORANGE = "#2a78d6", "#eb6834"
WAKE_K, WAKE_R0 = 0.075, 0.5      # Jensen wake decay constant and rotor radius (in rotor diameters), as in qollab/qwind/wake.py


def wake_loss_stats(farm, K, data_dir):
    """
    Modelled share of the K kept turbines' potential power that is lost to wakes, over every way of choosing K of the farm's
    turbines (exact enumeration): the best choice, the average choice and the worst. Model units, not measured production.
    """
    rose = load_wind_rose(os.path.join(data_dir, "windrose.json"), farm)
    layout = load_farm(os.path.join(data_dir, "farms.json"), farm)
    coords = farm_coords_D(layout)
    n = len(coords)
    J = build_instance(n, rose, 0, coords=coords).J
    J = J + J.T
    best, worst, total, count, best_sel = np.inf, -np.inf, 0.0, 0, None
    for sel in itertools.combinations(range(n), K):
        share = J[np.ix_(list(sel), list(sel))].sum() / 2 / K
        total += share
        count += 1
        if share < best:
            best, best_sel = share, sel
        worst = max(worst, share)
    return {"best": float(best), "average": total / count, "worst": float(worst), "best_selection": list(best_sel),
            "n_choices": count, "ids": [t["id"] for t in layout["turbines"]], "coords": coords}


def dominant_direction(farm, data_dir):
    """(FROM direction in compass degrees, share of the time) of the most frequent wind sector of the measured rose."""
    import json
    with open(os.path.join(data_dir, "windrose.json"), encoding="utf-8") as f:
        sectors = json.load(f)["sites"][farm]["sectors"]
    top = max(sectors, key=lambda s: s["frequency"])
    return top["direction_deg"], top["frequency"]


# ----------------------------------------------------------------------------------------------- drawing

def _canvas(title, subtitle, size):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=size)
    fig.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    ax.axis("off")
    fig.text(0.015, 0.965, title, color=INK, fontsize=14, fontweight="bold", va="top")
    fig.text(0.015, 0.90, subtitle, color=INK2, fontsize=9.5, va="top")
    return fig, ax


def _turbine(ax, x, ground, height=3.0, blade=1.15, angle=90, color=INK2):
    hub = (x, ground + height)
    ax.plot([x, x], [ground, hub[1]], color=color, linewidth=5, solid_capstyle="round", zorder=4)
    for k in range(3):
        a = np.radians(angle + 120 * k)
        ax.plot([hub[0], hub[0] + blade * np.cos(a)], [hub[1], hub[1] + blade * np.sin(a)], color=color, linewidth=3.2,
                solid_capstyle="round", zorder=5)
    ax.plot(*hub, "o", color=INK, markersize=8, zorder=6)
    return hub


def draw_wake(path):
    fig, ax = _canvas("Why the choice of turbines matters", "Every turbine leaves a wake of slower, turbulent air behind it. "
                      "A turbine standing in that wake produces less.", (9.2, 4.6))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6)
    ground = 0.6
    ax.plot([0, 12], [ground, ground], color=GRID, linewidth=3, zorder=1)
    x1, x2 = 3.2, 8.6
    hub1 = _turbine(ax, x1, ground, angle=100)
    hub2 = _turbine(ax, x2, ground, angle=40)
    xs = np.linspace(x1 + 0.25, 11.6, 60)
    half = 1.15 + 0.095 * (xs - x1)
    ax.fill_between(xs, hub1[1] - half, hub1[1] + half, color=BLUE, alpha=0.16, linewidth=0, zorder=2)
    ax.plot(xs, hub1[1] + half, color=BLUE, linewidth=1.4, linestyle=(0, (5, 3)), zorder=3)
    ax.plot(xs, hub1[1] - half, color=BLUE, linewidth=1.4, linestyle=(0, (5, 3)), zorder=3)
    for y in (hub1[1] - 1.1, hub1[1], hub1[1] + 1.1):
        ax.annotate("", xy=(1.9, y), xytext=(0.2, y), arrowprops=dict(arrowstyle="-|>", color=INK2, linewidth=2))
    ax.text(1.05, hub1[1] + 1.55, "wind", color=INK2, fontsize=11, ha="center")
    ax.text(6.0, hub1[1] + 1.95, "wake: slower, turbulent air", color=BLUE, fontsize=11, ha="center", fontweight="bold")
    ax.text(x1, ground - 0.42, "full wind", color=INK, fontsize=11, ha="center", fontweight="bold")
    ax.text(x2, ground - 0.42, "slower wind, less power", color=INK, fontsize=11, ha="center", fontweight="bold")
    ax.text(11.9, 5.7, "schematic, not to scale", color=INK2, fontsize=8, ha="right")
    fig.subplots_adjust(left=0.02, right=0.98, top=0.82, bottom=0.04)
    fig.savefig(path, dpi=160, facecolor=SURFACE)
    import matplotlib.pyplot as plt
    plt.close(fig)


def draw_decision(path, data_dir, K=7):
    from matplotlib.patches import Polygon
    stats = wake_loss_stats("penmanshiel", K, data_dir)
    coords = np.array(stats["coords"])
    keep = set(stats["best_selection"])
    deg_from, freq = dominant_direction("penmanshiel", data_dir)
    toward = np.radians(meteorological_to_toward(deg_from))          # math angle (0 = east) the wind blows toward
    u, v = np.array([np.cos(toward), np.sin(toward)]), np.array([-np.sin(toward), np.cos(toward)])
    n = len(coords)
    fig, ax = _canvas(f"Which {K} of the {n} turbines should keep running?",
                      "Penmanshiel wind farm, Scotland (real positions). Blue: kept running. Grey: switched off. Shaded: wakes of kept ones.", (9.2, 5.9))
    for i in keep:
        L = 8.0
        p = coords[i]
        pts = [p + v * WAKE_R0, p + u * L + v * (WAKE_R0 + WAKE_K * L), p + u * L - v * (WAKE_R0 + WAKE_K * L), p - v * WAKE_R0]
        ax.add_patch(Polygon(pts, closed=True, facecolor=BLUE, alpha=0.10, edgecolor="none", zorder=1))
    for i, (x, y) in enumerate(coords):
        if i in keep:
            ax.plot(x, y, "o", markersize=17, color=BLUE, markeredgecolor=SURFACE, markeredgewidth=2.5, zorder=4)
        else:
            ax.plot(x, y, "o", markersize=17, markerfacecolor=SURFACE, markeredgecolor="#8a8984", markeredgewidth=2, zorder=3)
        ax.text(x, y - 1.15, stats["ids"][i], color=INK2, fontsize=8, ha="center", va="top", zorder=5)
    xmin, ymin = coords.min(axis=0) - 3.5
    xmax, ymax = coords.max(axis=0) + 8.5
    ax.set_xlim(xmin - 3.5, xmax + 9.0)
    ax.set_ylim(ymin - 2.0, ymax + 2.5)
    ax.set_aspect("equal")
    # dominant wind direction arrow, bottom left
    start = np.array([xmin - 1.0, ymin + 0.5])
    ax.annotate("", xy=start + u * 6.5, xytext=start, arrowprops=dict(arrowstyle="-|>", color=INK, linewidth=2.6, mutation_scale=22), zorder=6)
    ax.text(start[0], start[1] - 1.3, f"wind {freq:.0%} of the time\nfrom {deg_from:g} degrees (the model uses all directions)",
            color=INK2, fontsize=8.5, ha="left", va="top")
    # scale bar: 5 rotor diameters
    layout = load_farm(os.path.join(data_dir, "farms.json"), "penmanshiel")
    d_m = layout["rotor_diameter_m"]
    sx, sy = xmax - 5.0, ymin + 0.2
    ax.plot([sx, sx + 5.0], [sy, sy], color=INK2, linewidth=3)
    ax.text(sx + 2.5, sy + 0.5, f"5 rotor diameters = {5 * d_m:.0f} m", color=INK2, fontsize=8.5, ha="center")
    fig.text(0.015, 0.05, f"Modelled power lost to wakes: {100 * stats['best']:.1f}% with this choice, "
             f"{100 * stats['average']:.1f}% for an average random choice of {K}.\n"
             f"Model units, not measured production. This choice is the best of {stats['n_choices']:,} (exact search).",
             color=INK, fontsize=9.5, fontweight="bold", va="center", linespacing=1.5)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.84, bottom=0.11)
    fig.savefig(path, dpi=160, facecolor=SURFACE)
    import matplotlib.pyplot as plt
    plt.close(fig)


def draw_pipeline(path):
    from matplotlib.patches import FancyBboxPatch
    fig, ax = _canvas("How QWind works", "From the wind and the turbine positions to the turbines to keep running", (9.6, 3.0))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 40)
    steps = [("1", "Wind and positions", "real positions and\na measured wind rose", INK2),
             ("2", "Wake model", "which turbine shades\nwhich, and how much", INK2),
             ("3", "Choice problem", "pick the K turbines\nwith the least wake loss", INK2),
             ("4", "Quantum circuit", "built in Qiskit; keeps\nexactly K by construction", BLUE),
             ("5", "Answer", "the K turbines\nto keep running", INK2)]
    w, gap, x = 16.0, 3.4, 3.2
    for i, (num, head, body, color) in enumerate(steps):
        ax.add_patch(FancyBboxPatch((x, 8), w, 22, boxstyle="round,pad=0.4,rounding_size=1.6", facecolor=SURFACE if color == INK2 else "#e8f0fb",
                                    edgecolor=color, linewidth=2.2, zorder=2))
        ax.text(x + w / 2, 26.2, num, color=color, fontsize=13, fontweight="bold", ha="center", va="center")
        ax.text(x + w / 2, 21.0, head, color=INK, fontsize=10.2, fontweight="bold", ha="center", va="center")
        ax.text(x + w / 2, 13.6, body, color=INK2, fontsize=8.4, ha="center", va="center", linespacing=1.4)
        if i < len(steps) - 1:
            ax.annotate("", xy=(x + w + gap - 0.3, 19), xytext=(x + w + 0.5, 19), arrowprops=dict(arrowstyle="-|>", color=INK2, linewidth=2))
        x += w + gap
    ax.text(50, 2.4, "Compared against exact search, simulated annealing, greedy search and random valid choice", color=INK2, fontsize=9, ha="center")
    fig.subplots_adjust(left=0.01, right=0.99, top=0.76, bottom=0.03)
    fig.savefig(path, dpi=160, facecolor=SURFACE)
    import matplotlib.pyplot as plt
    plt.close(fig)


def build_all(out_dir, data_dir):
    os.makedirs(out_dir, exist_ok=True)
    paths = [os.path.join(out_dir, name + ".png") for name in ("what_is_a_wake", "the_decision", "how_it_works")]
    draw_wake(paths[0])
    draw_decision(paths[1], data_dir)
    draw_pipeline(paths[2])
    return paths


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=os.path.join(ROOT, "qollab", "data"))
    ap.add_argument("--out", default=os.path.join(ROOT, "results", "figures"))
    args = ap.parse_args(argv)
    for path in build_all(args.out, args.data):
        print("wrote", path)


if __name__ == "__main__":
    main()
