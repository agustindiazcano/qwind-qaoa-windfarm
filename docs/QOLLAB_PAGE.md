# Qollab project page and demo video

The Qollab project page is the **same Markdown as the README** (`README.md`): paste it as is into the Markdown description editor of the project. It already starts with "Try it: click Run your code on this page", contains the exact line `This effort is supported by Qollab & IonQ` at the end, the Disclosure and the References, and has no relative links (paths such as `docs/DATA.md` are plain code text; the repository link is absolute). The RESULTS block is generated from `results/` (`python scripts/make_results_tables.py --readme README.md`); regenerate it before pasting if `results/` changed. Whether the Qollab editor renders Markdown tables is **not verified**: check the preview after pasting and, if tables do not render, say so and I will produce a list version.

## Fields of the project form

| Field | Value |
|---|---|
| Title | QWind |
| Description (max 240 characters) | See below (counted by `tests/test_qollab_page.py`) |
| Template | Leave empty |
| Project shape | Upload your own files (the `qollab/` folder; Python runs from the top-level `main.py`) |
| Tags | `qubo`, `quantumalgorithms`, `quantum`, `nisq` (add `visualization` only if figures or the website are included; `noise` only if noise is actually measured, which it is not) |
| Theme | Quantum Impact |
| Project Website | The deployed website URL, only if it is ready |
| Contributors | Agustin Diaz-Cano, Baltazar Salerno |

**Description (max 240 characters):**

> QWind compares QAOA in Qiskit (XY mixer + Dicke state) with exact, annealing and greedy search to choose which K of N turbines to keep, on real farm positions and wind roses. Simulator only; no quantum advantage claimed.

## Before pasting: checklist

- [ ] The uploaded `qollab/` folder is the one from `main` (default Run N = 8, K = 3, p = 2, XY + Dicke) and the table prints once; the last check printed it once in 25.5 s total (QAOA 3.3 s).
- [ ] MIT license in the project.
- [ ] Do not click Publish on test projects (reversibility unknown).
- [ ] The README preview shows the tables; the line `This effort is supported by Qollab & IonQ` is visible.
- [ ] Items still marked "to verify" in `docs/DATA.md` (year of the Copernicus notice, link to the CC BY 4.0 legal text) are decided.

## Demo video (2-3 minutes, public, with captions)

All numbers come from the README RESULTS block, which is generated from `results/`.

| Time | What is on screen | What to say |
|---|---|---|
| 0:00-0:20 | A wind farm picture or the turbine positions of Penmanshiel | "Turbines steal wind from each other. Given the turbines that already exist, which K should keep operating? That is a selection problem, not layout design." |
| 0:20-0:45 | The QUBO formula in the README | "We turn it into a QUBO with an exactly-K constraint and solve it with QAOA, simulated in Qiskit, next to exact enumeration, simulated annealing and greedy search." |
| 0:45-1:30 | Click **Run your code** on Qollab and show the table and the detail block | "Default run: 8 cells, 3 turbines, depth 2. All methods find the best layout. The detail block shows the useful part: P(optimal) 0.062 for QAOA against 0.016 for uniform sampling, and every sample is feasible." |
| 1:30-2:15 | The README results table (synthetic and Penmanshiel) | "Across 24 synthetic instances and the real farms, the constraint-preserving ansatz beats uniform sampling over feasible layouts on the approximation ratio in every instance, at depths 1 to 3. The penalty formulation does not do so consistently." |
| 2:15-2:45 | The limitations section | "Limits: simulator only, instances up to 14 cells, pairwise-additive wake losses, three instances per real farm, and classical methods solve these exactly. We do not claim a quantum advantage. This effort is supported by Qollab and IonQ." |

Captions: upload an `.srt` or burn them in; the text above is the caption source. Do not say "we ran on a quantum computer".
