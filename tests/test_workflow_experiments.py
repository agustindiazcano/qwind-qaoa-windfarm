import os
import re
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "experiments")))
import run_all  # noqa: E402

WORKFLOW = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".github", "workflows", "run-experiments.yml"))


def _text():
    with open(WORKFLOW, encoding="utf-8") as f:
        return f.read()


def test_workflow_is_manual_and_read_only():
    t = _text()
    assert "workflow_dispatch:" in t
    assert "pull_request" not in t and "push:" not in t          # never runs on its own
    assert "contents: read" in t and "contents: write" not in t  # results come back as artifacts, no pushes
    assert "git push" not in t


def test_workflow_does_not_retune_the_protocol():
    t = _text()
    for flag in ("--maxiter", "--restarts", "--shots", "--depths", "--lam"):
        assert flag not in t


def test_default_datasets_exist_and_are_the_demo_ones():
    m = re.search(r"default: \"([^\"]*)\"\s*#\s*datasets", _text())
    assert m, "the datasets input needs a default"
    defaults = m.group(1).split()
    assert defaults == ["synthetic", "real_penmanshiel_sub10"]
    for d in defaults:
        assert run_all.specs_for_dataset(d)


def test_workflow_has_timeouts_and_merges_only_downloaded_artifacts():
    t = _text()
    assert "timeout-minutes:" in t
    assert "upload-artifact" in t and "download-artifact" in t
    assert "merge_results" in t           # merge job uses a clean folder, never the committed smoke runs
