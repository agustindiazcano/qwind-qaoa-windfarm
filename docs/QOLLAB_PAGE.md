# Qollab project page and demo video

The Qollab project page is the **same Markdown as the README** (`README.md`): paste it as is into the Markdown description editor of the project. It already starts with "Try it: click Run your code on this page", contains the exact line `This effort is supported by Qollab & IonQ` at the end, the Disclosure and the References, and has no relative links (paths such as `docs/DATA.md` are plain code text; the repository link is absolute). The RESULTS block is generated from `results/` (`python scripts/make_results_tables.py --readme README.md`); regenerate it before pasting if `results/` changed. Check the preview after pasting: if the Markdown tables do not render in the editor, use the list version of the results.

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

## Demo video (2-3 minutes, public, with captions)

All numbers come from the README RESULTS block, which is generated from `results/`.

| Time | What is on screen | What to say |
|---|---|---|
| 0:00-0:20 | A wind farm picture or the turbine positions of Penmanshiel | "Turbines steal wind from each other. If an operator has to run fewer turbines, which ones should keep running? That is a selection problem, not layout design." |
| 0:20-0:45 | The QUBO formula in the README | "We turn it into an optimization problem with an exactly-K constraint and ask: can a quantum algorithm, QAOA simulated in Qiskit, solve it, and does the way you build the circuit matter? We test it against exact enumeration, annealing, greedy search and plain random choice." |
| 0:45-1:30 | Click **Run your code** on Qollab and show the table and the detail block | "Default run: 8 cells, 3 turbines. Every method finds the best layout. The detail block shows the point: the circuit that keeps exactly K turbines samples the best layout about four times more often than random valid choice, and every sample is a valid layout." |
| 1:30-2:15 | The README results table (all six datasets) | "Across synthetic data and the real positions and measured winds of two wind farms, putting the constraint inside the circuit is clearly better than the usual penalty, and its best sample is the exact optimum in five of six datasets, as good as simulated annealing." |
| 2:15-2:45 | The limitations section | "But this is not an advantage: random valid sampling is almost as good up to 12 turbines, and annealing and exact enumeration are just as good and cheap. Simulated on a CPU, instances up to 14 cells, a simplified wake model. We do not claim a quantum advantage. This effort is supported by Qollab and IonQ." |

Captions: upload an `.srt` or burn them in; the text above is the caption source. Do not say "we ran on a quantum computer".
