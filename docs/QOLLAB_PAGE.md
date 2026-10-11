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

> QWind compares QAOA in Qiskit (XY mixer + Dicke state) with exact, annealing and greedy search to choose which K of N turbines to keep, on real farm positions and wind roses. Also run once on IonQ Forte 1. No quantum advantage claimed.

## Before pasting: checklist

- [ ] The uploaded `qollab/` folder is the one from `main` (default Run N = 8, K = 3, p = 2, XY + Dicke) and the table prints once; the last check printed it once in 25.5 s total (QAOA 3.3 s).
- [ ] MIT license in the project.
- [ ] Do not click Publish on test projects (reversibility unknown).
- [ ] The README preview shows the tables; the line `This effort is supported by Qollab & IonQ` is visible.

## Demo video (2-3 minutes, public, with captions)

All numbers come from the README RESULTS block, which is generated from `results/`.

| Time | What is on screen | What to say |
|---|---|---|
| 0:00-0:20 | A wind farm picture or the turbine positions of Penmanshiel | "Every wind turbine steals wind from the ones behind it. When an operator has to run fewer turbines, choosing which to keep running changes how much energy is wasted." |
| 0:20-0:45 | The QUBO formula in the README | "We turned that choice into an optimization problem and built a quantum circuit for it in Qiskit, with the rule 'keep exactly K turbines' inside the circuit itself." |
| 0:45-1:30 | Click **Run your code** on Qollab and show the table and the detail block | "Eight cells, three turbines. Every result is a valid plan, and the circuit samples the best layout about four times more often than random valid choice." |
| 1:30-2:10 | The README headline and results table | "We tested it on six datasets, including the real positions and measured winds of the Penmanshiel and Kelmarsh wind farms. It finds the exact optimum on five of six, matching simulated annealing, and it beats the standard penalty approach by 3.4 to 17 times." |
| 2:10-2:35 | The README section "Run on real quantum hardware" | "We also ran the circuit once on IonQ Forte 1, a real quantum computer: 997 shots on a small instance, six cells and three turbines. About 78% of the samples were valid plans, and the rest can be discarded because the rule is inside the circuit. Among the valid ones, the best layout showed up with probability 0.1665, close to the ideal 0.1784 and above the 0.1000 of a random valid choice, and the best sample was the exact optimum. It was a single run." |
| 2:35-2:55 | The repository page | "It's open source under MIT, fully reproducible, with 150 tests and a protocol fixed in advance. QWind: a rigorous foundation for quantum optimization on real wind farms. This effort is supported by Qollab and IonQ." |

Captions: upload an `.srt` or burn them in; the text above is the caption source. Say it plainly: the hardware result is one small run on IonQ Forte 1 (N = 6, 997 shots, numbers in the README section "Run on real quantum hardware"). The benchmark itself is simulated, and the live Run on Qollab uses the built-in simulator. Do not claim a quantum advantage.
