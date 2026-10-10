# Last Context
- Investigated failing CI on `main`. Workflows were missing due to being empty files (0 bytes).
- Re-created `.github/workflows/ci.yml` with `python-version: '3.12'`, configured it to install `requirements-dev.txt`, and run `pytest`.
- Re-created `.github/workflows/pages.yml` and set its trigger to `workflow_dispatch` with appropriate permissions.
- Ensured local tests run fast and green before pushing.
