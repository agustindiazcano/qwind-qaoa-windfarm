# Last Context
- Merged layout branch into new feature branch.
- Added `qollab/requirements.txt` to strictly pin runtime dependencies.
- Refactored root `requirements.txt` and `requirements-dev.txt`.
- Replaced `test_forbidden_imports.py` with `test_qollab_imports.py` which dynamically checks dependencies from `qollab/requirements.txt` using AST.
- Enforced AST check to fail correctly if `matplotlib` or `qiskit-aer` is imported in `qollab/`.
- Updated `README.md` and `agents.md` documenting strict requirements rules.
