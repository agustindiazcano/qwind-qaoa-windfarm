# Pending Tasks

Legend: [x] done, [~] partly done, [ ] open. Owner = the human captain/author; only the owner can act on Qollab and the video.

## Done
1. [x] Core model, QUBO, classical baselines, tests (`qollab/qwind/`, `tests/test_core.py`).
2. [x] Qollab layout, strict runtime requirements enforced by a test, CI and Pages workflows fixed.
3. [x] QAOA (`qaoa.py`) and `main.py`; constraint-preserving variant (XY mixer + Dicke start) and ramp initialization; offline variant comparison.
4. [x] Results schema, enforced by `tests/test_results_schema.py` (per-dataset folders, merged `results/summary.json` with a `datasets` list).
5. [x] Fixed protocol `qwind-v1` (`experiments/run_all.py`), never retuned.
6. [x] Real data: Penmanshiel (14 turbines) and Kelmarsh (6) with real positions and measured 2019 SCADA roses (CC-BY-4.0, Zenodo), plus ERA5 roses for Chubut and Bahia Blanca (secondary); sources, licenses and derivation in `docs/DATA.md`.
7. [x] Live-Run limits: default N = 8, recommended 10, hard limit 12 (N = 14 took 42.8 s in Qollab); the live Run never loads the farm or rose files (test).
8. [x] Live Run defaults to XY + Dicke (PR #29); checked in Qollab by the owner: table prints once, 25.5 s total, QAOA 3.3 s (boot time varies 15.8 to 25.5 s). Keep N = 8.
9. [x] Cloud runs (manual workflow `run-experiments.yml`): all six datasets, status final, in `results/` (synthetic 24 instances, real_penmanshiel_sub10 3, real_penmanshiel 3, real_kelmarsh 3, real_chubut 8, real_bahia_blanca 8).
10. [x] `scripts/sync_results_to_web.py` and `scripts/make_results_tables.py` (README RESULTS block and `results/results_tables.md`, generated from `results/`).
11. [x] README finalized (Results, How to run, Limitations, Disclosure with data licenses, References).
12. [x] References verified at the abstract level on 2026-10-10 (Hadfield et al., Bartschi and Eidenbenz, Sack and Serbyn).

## Open (numbered by priority)
13. [ ] 🔴 Owner: paste the README into the Qollab project page (title, description up to 240 characters, tags `qubo`, `quantumalgorithms`, `quantum`, `nisq`; the exact line `This effort is supported by Qollab & IonQ` is at the end of the README), Project Website field if the site is ready. See `docs/QOLLAB_PAGE.md`.
14. [ ] 🔴 Owner: demo video 2-3 min, public, with captions (script in `docs/QOLLAB_PAGE.md`).
15. [ ] 🟡 Website (`web/index.html` is still empty, teammate): read `web/data/summary.json` produced by `python scripts/sync_results_to_web.py`; alt text on every figure; `experiments/make_figures.py` is still empty.
16. [x] Attribution details resolved: CC BY 4.0 link and wording, Copernicus notice year (2026, the year the derived material was generated; the license leaves it open), Open-Meteo non-commercial use (open-source research project, no ads or subscriptions). Global Wind Atlas not used.
17. [ ] 🟢 Optional: use the fixed sub-instance `real_penmanshiel_sub10` inside the live Run (today offline only; needs a human decision and a new Qollab check).
18. [ ] 🟢 Optional: histogram of the optimal circuit with one final `backend.run` (few shots); any change in `main.py` requires re-checking in Qollab that the table prints once.
19. [ ] 🟢 Optional: measure 120 evaluations with `backend.run` against 120 with `StatevectorEstimator` (N = 8) to be able to cite "too slow" (today the README says it is a design choice, not measured).
20. [ ] 🟢 Optional: simulated-annealing control with an evaluation budget matched to QAOA (~120), labeled as a later control, not part of `qwind-v1`.
21. [ ] ⚪ Noise (IBM noise-model simulators in Qollab): not done; do not claim it.
22. [ ] Captain submits at least 2-3 hours before Sunday 2026-10-11 19:00 ET (20:00 Argentina time).
