# Project
QWind: a Qiskit QAOA benchmark for wind-farm layout optimization (wake-loss QUBO with cardinality constraint), compared against exact enumeration, simulated annealing and greedy search. Hackathon project (Qollab x IonQ), theme: Quantum Impact. Submission deadline: Sunday Oct 11, 19:00 ET (20:00 Argentina time).

> **For full architectural and scientific context, read [docs/PROJECT_CONTEXT.md](docs/PROJECT_CONTEXT.md).**

## Workflow (strict)
- One branch per task. Never commit directly to main. Exception: the initial repository scaffold.
- TDD: write the test first, see it fail, then write the code.
- Every change goes through a pull request with CI/tests passing.
- A human approves every PR. Do not merge on your own.
- Do not suggest shortcuts that skip these steps.

## Repository layout
- `qollab/`: exactly what gets uploaded to Qollab (self-contained). Entry point is a top-level `main.py`. Code lives in `qollab/qwind/`.
- `experiments/`: full offline runs (may use extra libraries).
- `results/`: output of experiments and the only input of the website (`summary.json`, `per_instance.csv`, `figures/`).
- `web/`: static presentation site. It only reads `results/summary.json` (copied by `scripts/sync_results_to_web.py`).
- `tests/`: imports from `qollab/qwind/`. No duplicated code between folders. Single source of truth.
- `docs/`: results schema, data sources and licenses, model assumptions.

## Dependencies
- `qollab/` imports only `numpy`, `scipy`, `qiskit` (plus the standard library).
- `qollab/requirements.txt` is the closed list of runtime dependencies. Changing it requires human approval.
- Do not add any dependency to `qollab/` without human approval.
- `qiskit-aer`, `matplotlib` may only be used in `experiments/`, never in `qollab/`.
- Do not use `qiskit-optimization` or `ortools`. Build the QUBO and Hamiltonian by hand (`SparsePauliOp`).

## Runtime constraints
- `qollab/main.py` MUST define `main(n_cells=8, K=3, seed=0)`. The platform calls `main()` after running the file. It must finish in a few seconds (e.g. evaluating classical heuristics on small live instances).
- The live Run is limited to small instances: up to 12 cells recommended, hard limit 14. Larger instances are computed offline. (`main()` refuses `n_cells > 14`.)
- Do not use `backend.run` in optimization loops.
- Use fixed random seeds everywhere. Results must be reproducible. Figures must be generated from `results/`.
- No network access at runtime.

## Claims and honesty
- Never claim quantum advantage, speedups, energy or cost savings.
- Every number in the README, the Qollab page or the website must come from a file in `results/`. Nothing hand-written.
- If QAOA loses to classical methods, report it plainly.
- State model limitations explicitly (pairwise additive wake losses, small instances, simulator only).

## Required text
- The README and the Qollab project page must include exactly: `This effort is supported by Qollab & IonQ`
- The Disclosure section must list: AI tools used, prior code (if any), libraries, and data sources with licenses.
- License: MIT.

## Accessibility (website and figures)
- Sufficient color contrast, alt text on every figure, keyboard-navigable pages, captions or subtitles for the video.

## Suggested Creation Order
1. Repo + README + LICENSE + AI agent docs (`agents.md`, `CLAUDE.md`, `gemini.md`).
2. `tests/test_core.py` and `qollab/qwind/` (`wake.py`, `qubo.py`, `classical.py`).
3. `docs/results_schema.md` and an example `summary.json` (to enable parallel frontend work).
4. `qaoa.py`, `main.py`, `experiments/`.
5. Web, final README, video.

## Priorities if time runs short (cut from the bottom)
1. Core correctness (QUBO == brute-force energy) and a working `main.py` Run.
2. README and Qollab project page.
3. Demo video (2-3 min, public link).
4. QAOA results for p = 1, 2, 3 against the classical baselines.
5. Noise simulation, instance-size scaling.
6. Website and extra visuals.

## AI Agent Protocols
- **Context Initialization**: At the beginning of a new session, agents MUST read `lastcontext.md` and `pending.md` to understand the recent progress and current task list.
- **Environment Awareness**: Always check the git status, current branch, and worktree before proceeding. Multiple people and agents are collaborating on this repository; never take the local state for granted.
- **Testing Constraints**: Heavy tests must ALWAYS be launched in the cloud. Never run heavy tests locally in order to save time.
