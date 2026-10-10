# Last Context
- Restructured repository layout to match Qollab requirements, moving model code to `qollab/qwind/` and updating all import paths.
- Removed `example.py`.
- Updated `qollab/main.py` to define `main(n_cells=8, K=3, seed=0)` for rapid execution and table printing.
- Implemented tests to verify `main()` execution and to check for forbidden imports in `qollab/`.
- Updated `requirements.txt` with strict versions for the runtime and `requirements-dev.txt` for local use.
- Documented Jensen wake model citations in `docs/model.md` and upload instructions in `README.md`.
