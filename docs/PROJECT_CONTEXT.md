# QWind: Project Context and Handoff

Last updated: Sat 2026-10-10, ~14:55 ART. Update the "Status" section at the end of every working session.
This document lets a new session (human or AI agent) continue without prior conversation history.

---

## 1. What this project is

**QWind** is a hackathon project: a Qiskit **QAOA benchmark for wind-farm layout optimization**.

- Problem: choose K turbine sites out of N candidate sites so that wake losses are minimized (each turbine reduces the wind seen by turbines behind it).
- Method: encode wake losses as a QUBO with a cardinality constraint, solve with QAOA (Qiskit, statevector simulation), benchmark against exact enumeration, simulated annealing and greedy local search.
- Hackathon: **Qollab x IonQ Global Hackathon**, Oct 9-11, 2026. Theme: **Quantum Impact**. Node: UNICEN (Argentina). Team "Salta": Agustin Diaz-Cano (owner) and Baltazar Salerno.
- Qollab project: "QWind" (Draft). GitHub repo: `agustindiazcano/qwind-qaoa-windfarm`.

**Honest claim (do not change without the owner's approval):** "We measure how close QAOA gets to the optimal wind-farm layout versus classical methods, how this changes with circuit depth, and where it breaks down." **No quantum advantage is claimed.** At the sizes that fit a simulator, exact enumeration and classical heuristics solve the problem in milliseconds, and that is the expected result. The value of the project is a rigorous, reproducible, honestly reported benchmark on a real energy-industry problem.

---

## 2. Hackathon rules (summary of the official terms)

- **Deadline: Sunday Oct 11, 19:00 ET = 23:00 UTC = 20:00 Argentina time.** Submissions can be edited until the deadline. The team captain submits from the team page (qollab.xyz/programs/hackathon/register); up to 5 projects per team. Aim to submit at least 2-3 hours early.
- Must use **Qiskit**, run on Qollab's free simulators, be **published and runnable on Qollab.xyz under an MIT license** before the deadline.
- Judges run every project on a **free local simulator**. Results from IonQ simulators or real hardware **neither add nor subtract points**. What matters is that the code runs without errors.
- Project page on Qollab must explain: what it does, what problem it explores, how to run it, and enough for others to replicate or extend it. Judges start by reading this page.
- Required attribution text (exact): `This effort is supported by Qollab & IonQ`. (A summary of the official video wrote "Qollab and IonQ"; the written rules say "&". We use the rules' version. Ask in #hackathon-all if in doubt.)
- **Disclosure is mandatory**: AI tools used (Claude, and others if used), forks, templates, prior code, libraries. Missing disclosure can lead to disqualification.
- Demo video: **2 to 3 minutes**, public link that opens without signing in (YouTube public or unlisted).
- UI accessibility best practices are required (contrast, alt text, keyboard navigation, captions).
- Built during the hackathon window (Oct 9 19:00 ET to Oct 11 19:00 ET). Existing code is allowed only if disclosed.
- **Rubric:** Novelty and Creativity, Technical Execution, Impact Potential, Documentation Quality.
- **"Beyond the tutorial bar":** a panel can score 0 on Novelty and Technical Execution if the project is tutorial-level. Our qualifying contribution: comparative benchmarking against strong classical baselines, plus parameter/depth analysis.
- Themes: Quantum Impact (real-world problem, public dataset, strong classical baseline, hybrid), Quantum Playground, Quantum Unlocked. Theme only affects specialty awards; placement awards use the same rubric.
- Specialty awards: Most Novel/Creative, Best of each theme, Most Impact, Best Documentation.
- Mentors: 15-minute calls on Oct 10 or 11 (ET), up to two per team, booked at qollab.xyz/hackathon/mentor-booking. Support channels: Slack #hackathon-all (platform/tools) and the node channel (Hackathon-unicen). The node also has a Google Meet room for check-ins.

---

## 3. Why this idea (decision history)

The project started as an RL robot-navigation idea (grid world, then MuJoCo, VQC policy vs MLP baseline, with C++ inference). It was dropped because: Qiskit is mandatory, MuJoCo/C++ are outside the required framework, and the scope was too large for ~40 hours. Several alternatives were scored and compared (MAPF as QUBO, satellite observation scheduling, QAOA inside LNS, finance and fraud-detection ideas from other assistants). **Wind-farm layout was chosen** because it is the most likely to be finished well, has an exact classical baseline, fits the physics-first approach (real wake mechanism, then math), and is a legitimate Quantum Impact framing (energy industry).

Frank expectations (keep them in all texts):
- Classical methods will win at these sizes. That is reported plainly.
- Impact Potential is the weak criterion; strength lies in Technical Execution and Documentation.
- Industrial-scale advantage is a research hypothesis, not a result of this project.

Scientific principles of the owner for this project: model rooted in the real physical mechanism (wake deficit) before the mathematics; falsifiable, parameter-parsimonious modeling; honest controls; no ad hoc patches presented as insight.

---

## 4. Technical design

### 4.1 Problem and QUBO
- Candidate sites: a grid of cells with spacing expressed in rotor diameters. N cells, choose exactly K turbines.
- Binary variable x_i = 1 if a turbine is placed at site i.
- Energy (to minimize): `E(x) = sum_i h_i x_i + sum_{i<j} J_ij x_i x_j + lam * (sum_i x_i - K)^2`
  - `h_i = -P0`: negative isolated-turbine power (potentially site-dependent).
  - `J_ij`: pairwise wake loss between sites i and j, summed over wind-rose sectors weighted by frequency (power ~ v^3).
  - `lam`: cardinality penalty weight (must be tuned; it controls feasibility versus landscape quality).
- **Conventions (fixed):** qubit i corresponds to bit i of the basis-state index (Qiskit little-endian). Ising mapping `x = (1 - Z)/2`. The Hamiltonian is built by hand as a `SparsePauliOp`, with a constant offset tracked separately.

### 4.2 Wake model
- Jensen/Park top-hat wake: deficit decays with downwind distance, wake cone expands with decay constant k; coefficient Ct for thrust. Wind rose with sectors (direction, frequency, speed).
- **Approximation:** pairwise-additive losses (a true multi-wake superposition, e.g. sqrt of sum of squares, is not pairwise). The error is documented in `docs/model.md` and checked against the full model on sparse layouts.
- **TODO/unverified:** cite sources for k and Ct values in docs/model.md; do not use values from memory.

### 4.3 QAOA
- Depth p = 1, 2, 3. Cost layer is diagonal (RZZ/RZ), mixer is RX. Expectation via `StatevectorEstimator`, classical optimizer `scipy.optimize` (COBYLA), multiple random restarts with fixed seeds. Final sampling with `StatevectorSampler`.
- Do not use `backend.run` inside optimization loops (job-based and slow).
- Optional extensions (only if time remains): CVaR objective, tuning lam, XY mixer for the cardinality constraint, noise.

### 4.4 Classical baselines (all must run without extra dependencies)
- Exact enumeration over combinations of size K (the ground truth for N up to about 20-22).
- Simulated annealing (fixed seed), preserving cardinality K.
- Greedy plus local search (swap moves), preserving K.
- No ortools, no qiskit-optimization (decided: avoid dependencies that may not exist in Qollab).

### 4.5 Metrics
- Layout quality: best feasible power found / optimal power (from enumeration).
- Gap to optimum in energy; probability of sampling the exact optimum; probability mass on feasible states; approximation ratio of the expected energy.
- Effect of depth p; number of restarts and function evaluations; wall-clock time versus number of qubits (scaling).
- Multiple instances (different wind roses, K, grid shapes), reported with confidence intervals or distributions, fixed seeds.
- Planned instance sizes: 9, 12, 16, 20 cells (live Run in Qollab: up to 10 cells recommended, hard limit 12, default N = 8).

### 4.6 Optional: noise
- Not available through `qiskit_aer` in Qollab. The platform offers noise-model simulators (IBM, IonQ), selected in the Run dialog; whether and how they can be used from code is an open question for a mentor. Noise results are optional and do not score extra points.

---

## 5. Qollab runtime (confirmed by smoke test on Oct 10)

| Item | Result |
|---|---|
| Python | 3.14.2 |
| Qiskit | 2.5.2 |
| NumPy / SciPy | 2.4.6 / 1.18.0 (both available) |
| matplotlib | **NOT available** (also `circuit.draw("mpl")` fails) |
| qiskit_aer | **NOT available** |
| `backend` | pre-created global, a `BasicSimulator`. `backend.run` is fast for small circuits, but the platform's template polls job status |
| Primitives | `StatevectorEstimator`, `StatevectorSampler`, `SparsePauliOp` work |
| Entry point | **Corrected 2026-10-10:** with an uploaded folder, a `main.py` that only defined `main()` printed nothing in the Run (boot lines only, ~10.8 s); a bare `main()` at the end of the file printed the whole table once. So `main.py` is executed as a script and must call `main()` itself, behind `if __name__ == "__main__":`; `main()` skips one immediate duplicate call with the same arguments. Earlier note "the platform calls `main()` after running the file" came from the in-browser project shape and is not reliable. `__name__ == "__main__"` under Qollab is assumed: to be confirmed by the first Run of this version |
| Output | Textual console. The platform renders a probabilities histogram from counts automatically |

QAOA-like workload timings (parameterized circuit, all-to-all RZZ, Estimator plus COBYLA):

| Qubits | Seconds per evaluation | Notes |
|---|---|---|
| 8 | 0.047 | 40 evals in 3.3 s |
| 10 | 0.113 | 40 evals in 3.9 s |
| 12 | 0.086 | 40 evals in 4.1 s |
| 14 | 0.229 | 20 evals in 4.9 s |

Rules derived from this: The live Run is limited to small instances: up to 10 cells recommended, hard limit 12, default N = 8. **Measured in the live Run: N = 14 took 42.8 s (penalty QAOA, one run), over the 30 s budget**, so the limits were lowered from 12/14 to 10/12 and N = 14 is offline only. The live Run must finish well under a minute; larger instances (including the 14-turbine Penmanshiel farm) are computed offline and stored in `results/`. Timings come from one machine and one run; leave a safety margin.

Run dialog (QPU selector): Built-in simulator (24q, ideal, free, local) is the default and the one judges use. AWS Braket local simulator (25q), IBM noise-model simulators (free, local), remote IonQ simulators (Aria 1/2 25q, Forte 1 29q; noise model, free) and real IonQ Forte 1 36q (credits apply). Use the built-in simulator for development. Do not use remote simulators or QPUs.

Project creation form: title, description (max 240 characters), optional template (leave empty), project shape: "Python / Qiskit" (runs in the browser), "JS / Qiskit wrapper", or "Upload your own files" (Python runs from a top-level `main.py`). Project page editor has a Markdown description, tags (restricted list), contributors, a "Project Website" field and a **Publish** button (a separate step; do not publish test projects; reversibility unknown).

Allowed tags seen in the platform list: quantum, spring2026, visualization, entanglement, noise, circuit, education, interactive, quantumalgorithms, example, nisq, chemistry, finance, vqe, art, sonification, qiskit-machine-learning, qubo. Chosen: `qubo`, `quantumalgorithms`, `quantum`, `nisq` (+ `visualization` if figures or website, `noise` only if noise is actually measured). Avoid `example` (suggests tutorial level).

---

## 6. Repository layout

```
qwind-qaoa-windfarm/
├── README.md
├── LICENSE                  # MIT
├── AGENTS.md / CLAUDE.md / GEMINI.md   # agent rules (single source: AGENTS.md)
├── lastcontext.md, pending.md          # session handoff files
├── requirements.txt         # qiskit==2.5.2, numpy==2.4.6, scipy==1.18.0
├── requirements-dev.txt     # pytest + offline extras (qiskit-aer, matplotlib)
├── docs/                    # PROJECT_CONTEXT.md, model.md, results_schema.md, DATA.md
├── qollab/                  # EXACTLY what is uploaded to Qollab
│   ├── main.py              # defines main(...)
│   ├── qwind/               # wake.py, qubo.py, classical.py, qaoa.py, instances.py
│   └── data/                # small wind-rose file
├── experiments/             # offline runs (may use aer, matplotlib), figures
├── results/                 # summary.json, per_instance.csv, figures/
├── web/                     # static site (HTML/CSS/JS), reads only results/summary.json
├── scripts/                 # sync_results_to_web.py
├── tests/                   # imports from qollab/qwind
└── .github/workflows/       # ci.yml (pytest), optional
```

Rules: `qollab/` may import only numpy, scipy, qiskit and the standard library. No code duplication between folders. The website reads only `results/summary.json`. Every number shown anywhere must come from `results/`. Tests live in GitHub (CI or local), are never uploaded to Qollab, and `main.py` does not run pytest. Heavy experiments run offline once, and `main.py` loads their stored results.

**Results contract (`results/summary.json`, to be finalized in `docs/results_schema.md`):** metadata (versions, seeds, date), list of instances (id, grid shape, N, K, wind rose id), per method (exact, SA, greedy, QAOA with p) the layout quality, energy gap, probability of optimum, feasibility mass, evaluations and time.

**Website:** plain HTML/CSS/JS (no framework), built by teammate Baltazar Salerno, deployed on Vercel or GitHub Pages (Vercel's free plan is for non-commercial use; verify terms or use GitHub Pages). Root directory is `web/`. Loads data via `fetch('data/summary.json')` (needs a local server for development, not `file://`). Its link goes in the Qollab "Project Website" field. The site is optional for judging: the project must be complete without it. It must present results honestly (no advantage claims).

---

## 7. Workflow rules for contributors and agents

- One branch per task; never commit directly to main (exception: initial scaffold). TDD: failing test first. Every change goes through a pull request; a **human approves every PR; never merge on your own**.
- Stage files explicitly by name. **Never `git add .` or `git add -A`.** If an unknown file shows up in the diff, stop and ask. (An agent once committed a stray `example.py` this way.)
- Check git status, branch and worktree at the start; multiple people and agents work on this repo.
- Read `lastcontext.md` and `pending.md` at the start of a session and update them at the end.
- Heavy tests run in the cloud, not locally. Heavy means more than ~30 s or the full experiment grid. Keep PR tests under ~30 s on small instances (8-12 cells).
- Do not add dependencies to `qollab/` without human approval.
- Language: the owner talks to assistants in Spanish; code, docs, commits and READMEs are in English. Be concise and direct, no filler; disagree plainly with evidence.

---

## 8. Status (update this section)

**Done**
- Qollab project "QWind" created as Draft; description, long project-page text (with required attribution and disclosure), tags decided.
- Smoke test in Qollab passed (section 5).
- Task 1 (`feat/core-model`): wake.py (Jensen), qubo.py, classical.py, tests/test_core.py, docs/model.md. **PR #5 merged.**
- Task 2 (`chore/qollab-layout`): Repository structured according to Qollab constraints (`qollab/` self-contained, strict dependencies). **PR #6 merged.**
- Task 3 (`feat/qollab-requirements`): Added strict requirements.txt checking for `qollab/` using AST. **PR #7 open.**
- Chore: `.gitignore` added and committed `.pyc` files untracked (PR #13 merged). `main.py` only defines `main()` (PR #12 merged), covered by an import-side-effects test.
- Task 4 (`feat/qaoa`): `qaoa.py` (hand-built circuit, Estimator + COBYLA, exact distribution, Sampler) and `main(n_cells=8, K=3, p=2, seed=0)` with a QAOA row and detail block; live Run limited to N <= 12 (lowered from 14 after N = 14 took 42.8 s in the live Run). Default run ~6.5 s locally (120 evaluations at 8 qubits). Output reports QAOA next to uniform and random-feasible-sampling baselines and a feasible-only approximation ratio. **PR #14 merged, awaiting human review. Not yet run inside Qollab.**
- Task 6 (`feat/qaoa-xy`): constraint-preserving QAOA (XY mixer + Dicke start, no penalty) and ramp initialization, selectable by arguments; offline comparison in `experiments/compare_qaoa_variants.py` with CSVs in `results/`. On 7 small instances xy + dicke beats the uniform-over-feasible baseline everywhere while the penalty QAOA does not reliably do so; with 1000 shots even random feasible sampling finds the optimum at these sizes. **PR open, awaiting human review.** Live Run defaults unchanged.
- Task 7 (`docs/results-schema`, PR #19 and `feat/run-all`): results schema enforced by tests, `instances.py`, `run_all.py` with the fixed protocol `qwind-v1`. Only a smoke run exists in `results/`; the full synthetic run (~1 h, heavy) is pending.
- Task 8 (`data/real-wind-roses`): two real ERA5 100 m wind roses (`chubut`, `bahia_blanca`, 16 sectors) in `qollab/data/windrose.json`, derivation and licenses in `docs/DATA.md`, tests in `tests/test_windrose_data.py`. PR open, awaiting human review. Real runs not executed yet.
- Task 9 (`feat/run-all-datasets`, stacked on Task 8): per-dataset result folders plus `--merge` into the single `results/summary.json` (schema gains `datasets`). Smoke runs only; full runs of the three datasets pending a human decision (local vs cloud).
- Task 10 (`feat/real-farms`, stacked on Task 9): real farms Penmanshiel (14 turbines) and Kelmarsh (6) with real positions (`qollab/data/farms.json`) and measured 2019 SCADA roses (`windrose.json`); `wake.generate_h_J(coords=...)`, `build_instance(coords=...)`, `run_all.py` datasets `real_penmanshiel` and `real_kelmarsh` (K fixed before running). Smoke runs only; full runs pending.
- Task 10b (same PR, live-Run limits): `main()` hard limit 12 (recommended 10, default 8), `tests/test_live_run_isolation.py` (live Run never loads farm or rose files), fixed sub-instance `real_penmanshiel_sub10` (10 turbines closest to the farm centroid, K = 3, 5, 7; offline only), Kelmarsh labeled trivial contrast, offline cost estimate in `docs/DATA.md`. **Hard stop: if Penmanshiel is not producing results by Sunday 2026-10-11 10:00 ART, we ship with the ERA5 datasets (`real_chubut`, `real_bahia_blanca`) as primary.**
- Task 11 (`results/final-demo`, `results/all-datasets`, `ci/run-experiments`): manual GitHub Actions workflow and the final `qwind-v1` results of all six datasets (Python 3.12.15, Qiskit 2.5.2). **Merged.**
- Task 12 (`feat/live-run-xy-dicke`, PR #29): the live Run defaults to XY + Dicke. Checked in Qollab by the owner (table once, 25.5 s total). **Merged.**
- Task 13 (`feat/results-tables-web`, `docs/references`, `docs/readme-results`): `scripts/sync_results_to_web.py`, `scripts/make_results_tables.py` (README RESULTS block generated from `results/`), verified references, final README. **Merged.** Remaining: Qollab page text, demo video and website (teammate); see `pending.md`.

**Next tasks (in order)** (the full list with priorities is `pending.md`)
1. Owner: paste the README into the Qollab project page (`docs/QOLLAB_PAGE.md`), record the demo video, add the Project Website link if the site is ready.
2. Website: built (plain HTML/CSS/JS, sources in `web-src/`, generated by `python scripts/build_web.py`). Left: demo video link in the navbar, manual Pages deploy, URL in Project Website (`PENDING-FRONT.md`).
3. Resolve the items marked to verify (CC BY 4.0 legal text link, ERA5 notice year, XY ring mixer vs Hadfield et al.).
4. Captain submits with at least 2-3 hours of margin.

**Time plan (from Sat 14:30 to Sun 20:00 ART, ~29 h):** core and QAOA by Sat night; experiments and results Sun morning; README, page and video from Sun midday; submit by ~17:00.

### Decision (Sat 2026-10-10): two real wind roses
**Superseded the same evening by the owner's decision to use real operating farms with real layout and measured wind (Penmanshiel and Kelmarsh, CC-BY-4.0, Zenodo); the ERA5 roses of Chubut and Bahia Blanca are kept as an extra on the synthetic grid. See `docs/DATA.md`.** Original text below.
1. **Primary:** Patagonia, Chubut coast (Comodoro Rivadavia / Rawson area). Strong, highly directional.
2. **Contrast:** one site with a more dispersed rose (Salta or Bahia Blanca; pick whichever has verifiable data).

Conditions:
- The source must have a verifiable license and attribution. Candidates: Global Wind Atlas, ERA5. Verify the license terms from the source itself, not from memory. If unverifiable, stop and tell the owner.
- Record in `docs/DATA.md`: source, license, access date, coordinates, hub height, number of sectors, and how frequencies and speeds were derived.
- Reduce to 12-16 sectors (frequency, direction, mean speed). Store as a small file in `qollab/data/`. No network at runtime.
- Never fill values from memory. If the download fails, use the documented synthetic Weibull rose (explicit parameters and seed) and label it synthetic.
- Fix the protocol (lam sweep, ramp, seeds, p, instances) BEFORE running real data. Do not retune after seeing results.
- `results/` must have a `dataset` column (`synthetic` / `real_<site>`).
- One branch per task, TDD, human approval of every PR.

---

## 9. Open questions and unverified assumptions

- Who is the team captain, and does that account have access to submit?
- Is the theme chosen at registration (Quantum Impact) editable? Is "Publish" reversible? Does Qollab allow renaming the project?
- How to include noise in Qollab (IBM noise-model simulators from code?). Ask a mentor.
- Wind data: done (`docs/DATA.md`); licenses read at the source (CC-BY-4.0 for the Zenodo farms, Copernicus licence and CC-BY 4.0 for ERA5/Open-Meteo). CC BY 4.0 link, Copernicus notice year (2026) and the non-commercial use of the free Open-Meteo API are settled in `docs/DATA.md`.
- k and Ct constants and the size of the pairwise-superposition error (verify and document).
- Whether the judges' machine matches the measured timings (keep a margin). Qollab total for the default Run: 15.8 s on one run and 25.5 s on another (QAOA itself 3.2 to 3.3 s), so the platform boot time varies; the budget is 30 s.
- Mentor booking: up to two 15-minute calls. Suggested questions: noise inside Qollab, best practices for QAOA with a cardinality penalty (lam tuning or XY mixer), and the practical size limit for a Run.
- Vercel free-plan terms for hackathon projects.

---

## 10. Final submission checklist

- [~] Project on Qollab with MIT license; Run works with the built-in simulator (Run verified; the project page itself is the owner's step)
- [ ] Project page: what it does, problem, how to run, results, limitations
- [x] Exact text: `This effort is supported by Qollab & IonQ` (end of the README)
- [x] Disclosure: AI tools, prior code or templates, libraries, data sources and licenses (README; prior code: none)
- [ ] Theme declared (Quantum Impact)
- [x] All numbers traceable to `results/` (the README RESULTS block is generated); no claim of quantum advantage
- [ ] Demo video 2-3 min, public, with captions
- [ ] Website link in "Project Website" (if ready)
- [x] "Work in Progress" and "In development" notices removed (README); check the Qollab page text too
- [ ] Captain submits at least 2-3 hours before the deadline