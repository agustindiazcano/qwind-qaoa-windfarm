import json
import os
import shutil
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import sync_results_to_web as sync  # noqa: E402

REAL_SUMMARY = os.path.join(ROOT, "results", "summary.json")


def _write(tmp_path, **changes):
    with open(REAL_SUMMARY, encoding="utf-8") as f:
        summary = json.load(f)
    summary.update(changes)
    results = tmp_path / "results"
    results.mkdir()
    (results / "summary.json").write_text(json.dumps(summary), encoding="utf-8")
    return str(results), str(tmp_path / "web")


def test_sync_copies_summary_to_web_data(tmp_path):
    results, web = _write(tmp_path)
    out = sync.sync(results, web)
    assert out == os.path.join(web, "data", "summary.json")
    assert json.load(open(out, encoding="utf-8")) == json.load(open(os.path.join(results, "summary.json"), encoding="utf-8"))


def test_sync_refuses_smoke_unless_allowed(tmp_path):
    results, web = _write(tmp_path, status="smoke")
    with pytest.raises(ValueError, match="smoke"):
        sync.sync(results, web)
    assert not os.path.exists(os.path.join(web, "data", "summary.json"))
    assert sync.sync(results, web, allow_smoke=True)


def test_sync_refuses_a_file_that_is_not_a_summary(tmp_path):
    results = tmp_path / "results"
    results.mkdir()
    (results / "summary.json").write_text(json.dumps({"hello": 1}), encoding="utf-8")
    with pytest.raises(ValueError, match="datasets"):
        sync.sync(str(results), str(tmp_path / "web"))


def test_sync_refuses_missing_or_empty_file(tmp_path):
    (tmp_path / "results").mkdir()
    with pytest.raises(FileNotFoundError):
        sync.sync(str(tmp_path / "results"), str(tmp_path / "web"))
    (tmp_path / "results" / "summary.json").write_text("", encoding="utf-8")
    with pytest.raises(ValueError):
        sync.sync(str(tmp_path / "results"), str(tmp_path / "web"))
