"""
Executable form of docs/results_schema.md.

The validators below define what results/summary.json and results/per_instance.csv must contain.
They are used on the real files (when they have been generated) and on small fixtures.
"""
import csv
import json
import math
import os
import re

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SUMMARY = os.path.join(ROOT, "results", "summary.json")
PER_INSTANCE = os.path.join(ROOT, "results", "per_instance.csv")
SCHEMA_DOC = os.path.join(ROOT, "docs", "results_schema.md")

DATASET_RE = re.compile(r"^(synthetic(_[a-z0-9]+)?|real_[a-z0-9_]+)$")
METHODS = {"exact", "sa", "greedy", "qaoa"}
STATUSES = {"final", "smoke"}

PER_INSTANCE_COLUMNS = [
    "dataset", "instance_id", "wind_rose", "N", "K", "grid_rows", "grid_cols", "seed",
    "method", "variant", "p", "lam_mult",
    "energy_best", "energy_gap", "p_optimal", "p_feasible", "approx_ratio_feasible",
    "uniform_feasible_p_optimal", "uniform_feasible_ratio", "random_p_hit",
    "n_evals", "shots", "time_s",
]
INTEGER_COLUMNS = ["instance_id", "N", "K", "grid_rows", "grid_cols", "seed"]
QAOA_ONLY_COLUMNS = ["p", "p_optimal", "p_feasible", "approx_ratio_feasible",
                     "uniform_feasible_p_optimal", "uniform_feasible_ratio", "random_p_hit", "shots"]

SUMMARY_KEYS = ["schema_version", "status", "protocol", "environment", "datasets", "instances", "results", "caveats"]
DATASET_KEYS = ["dataset", "status", "n_instances"]
INSTANCE_KEYS = ["dataset", "instance_id", "wind_rose", "N", "K", "grid_rows", "grid_cols", "seed"]
RESULT_KEYS = ["dataset", "method", "variant", "p", "n_instances", "metrics"]
METRIC_KEYS = ["mean", "std", "ci95_low", "ci95_high"]
QAOA_METRICS = ["p_optimal", "p_feasible", "approx_ratio_feasible", "n_evals", "time_s"]
CLASSICAL_METRICS = ["energy_gap", "time_s"]
QAOA_RESULT_EXTRA = ["baselines", "frac_beating_uniform_ratio", "frac_beating_uniform_p_optimal"]
BASELINE_KEYS = ["uniform_feasible_p_optimal", "uniform_feasible_ratio", "random_p_hit"]


def _finite(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def validate_summary(obj):
    """Return a list of problems (empty if the summary follows the schema)."""
    errs = []
    for k in SUMMARY_KEYS:
        if k not in obj:
            errs.append(f"missing top-level key {k!r}")
    if errs:
        return errs
    if obj["status"] not in STATUSES:
        errs.append(f"status must be one of {sorted(STATUSES)}")
    declared = set()
    for d in obj["datasets"]:
        errs += [f"datasets entry missing {k!r}" for k in DATASET_KEYS if k not in d]
        if "dataset" in d:
            declared.add(d["dataset"])
            if not DATASET_RE.match(d["dataset"]):
                errs.append(f"bad dataset {d['dataset']!r}")
        if d.get("status") not in STATUSES:
            errs.append(f"dataset status must be one of {sorted(STATUSES)}")
    if len(declared) != len(obj["datasets"]):
        errs.append("datasets must list each dataset once")
    if obj["status"] == "final" and any(d.get("status") != "final" for d in obj["datasets"]):
        errs.append("top-level status is final only if every dataset is final")
    if obj["status"] == "smoke" and obj["datasets"] and all(d.get("status") == "final" for d in obj["datasets"]):
        errs.append("top-level status is smoke if any dataset is smoke")
    for inst in obj["instances"]:
        if inst.get("dataset") not in declared:
            errs.append(f"instance dataset {inst.get('dataset')!r} not listed in datasets")
        errs += [f"instance missing {k!r}" for k in INSTANCE_KEYS if k not in inst]
        if "dataset" in inst and not DATASET_RE.match(inst["dataset"]):
            errs.append(f"bad dataset {inst['dataset']!r}")
    if not obj["caveats"]:
        errs.append("caveats must list the model limitations")
    for r in obj["results"]:
        errs += [f"result missing {k!r}" for k in RESULT_KEYS if k not in r]
        if any(k not in r for k in RESULT_KEYS):
            continue
        if not DATASET_RE.match(r["dataset"]):
            errs.append(f"bad dataset {r['dataset']!r}")
        if r["dataset"] not in declared:
            errs.append(f"result dataset {r['dataset']!r} not listed in datasets")
        if r["method"] not in METHODS:
            errs.append(f"bad method {r['method']!r}")
            continue
        quantum = r["method"] == "qaoa"
        if quantum and not isinstance(r["p"], int):
            errs.append("qaoa results need an integer p")
        if not quantum and r["p"] is not None:
            errs.append("classical results must have p = null")
        required = QAOA_METRICS if quantum else CLASSICAL_METRICS
        for m in required:
            if m not in r["metrics"]:
                errs.append(f"{r['method']}/{r['variant']} missing metric {m!r}")
                continue
            for k in METRIC_KEYS:
                if not _finite(r["metrics"][m].get(k)):
                    errs.append(f"metric {m}.{k} is not a finite number")
        if quantum:
            errs += [f"qaoa result missing {k!r}" for k in QAOA_RESULT_EXTRA if k not in r]
            errs += [f"baselines missing {k!r}" for k in BASELINE_KEYS if k not in r.get("baselines", {})]
    return errs


def validate_per_instance(rows, fieldnames):
    errs = []
    if list(fieldnames) != PER_INSTANCE_COLUMNS:
        errs.append(f"columns must be exactly {PER_INSTANCE_COLUMNS}")
        return errs
    for i, row in enumerate(rows):
        if not DATASET_RE.match(row["dataset"]):
            errs.append(f"row {i}: bad dataset {row['dataset']!r}")
        if row["method"] not in METHODS:
            errs.append(f"row {i}: bad method {row['method']!r}")
            continue
        for c in INTEGER_COLUMNS:
            if not re.fullmatch(r"\d+", row[c]):
                errs.append(f"row {i}: {c} must be a non-negative integer")
        for c in ("energy_best", "energy_gap", "time_s"):
            try:
                if not math.isfinite(float(row[c])):
                    raise ValueError
            except ValueError:
                errs.append(f"row {i}: {c} must be a finite number")
        quantum = row["method"] == "qaoa"
        for c in QAOA_ONLY_COLUMNS:
            if quantum and row[c] == "":
                errs.append(f"row {i}: qaoa row needs {c}")
            if not quantum and row[c] != "":
                errs.append(f"row {i}: {c} must be empty for classical methods")
    return errs


def _metric(mean):
    return {"mean": mean, "std": 0.0, "ci95_low": mean, "ci95_high": mean}


def _valid_summary():
    inst = {"dataset": "synthetic", "instance_id": 0, "wind_rose": "A", "N": 6, "K": 3,
            "grid_rows": 3, "grid_cols": 2, "seed": 0}
    return {
        "schema_version": "1.0", "status": "smoke", "protocol": {"id": "fixture"},
        "environment": {"python": "3.12"}, "instances": [inst, dict(inst, dataset="real_chubut", wind_rose="chubut")],
        "datasets": [{"dataset": "synthetic", "status": "smoke", "n_instances": 1},
                     {"dataset": "real_chubut", "status": "smoke", "n_instances": 1}],
        "caveats": ["pairwise additive wake losses"],
        "results": [
            {"dataset": "synthetic", "method": "exact", "variant": "exact", "p": None, "n_instances": 1,
             "metrics": {m: _metric(0.0) for m in CLASSICAL_METRICS}},
            {"dataset": "real_chubut", "method": "qaoa", "variant": "xy+dicke", "p": 1, "n_instances": 1,
             "metrics": {m: _metric(0.5) for m in QAOA_METRICS},
             "baselines": {k: 0.1 for k in BASELINE_KEYS},
             "frac_beating_uniform_ratio": 1.0, "frac_beating_uniform_p_optimal": 1.0},
        ],
    }


def test_validator_accepts_valid_summary():
    assert validate_summary(_valid_summary()) == []


@pytest.mark.parametrize("mutate", [
    lambda s: s.pop("caveats"),
    lambda s: s.update(status="draft"),
    lambda s: s["results"][0].update(dataset="Synthetic"),
    lambda s: s["results"][0].update(p=1),
    lambda s: s["results"][1]["metrics"].pop("p_optimal"),
    lambda s: s["results"][1]["metrics"]["p_optimal"].update(mean=float("nan")),
    lambda s: s["results"][1].pop("baselines"),
    lambda s: s["instances"][0].update(dataset="real"),
    lambda s: s.pop("datasets"),
    lambda s: s["datasets"].pop(),                                  # results/instances reference an unlisted dataset
    lambda s: s["datasets"][0].pop("status"),
    lambda s: s["datasets"].append(dict(s["datasets"][0])),         # duplicate dataset
    lambda s: s.update(status="final"),                              # final top-level with smoke datasets
])
def test_validator_rejects_broken_summary(mutate):
    s = _valid_summary()
    mutate(s)
    assert validate_summary(s) != []


def test_per_instance_validator():
    classical = dict.fromkeys(PER_INSTANCE_COLUMNS, "")
    classical.update(dataset="synthetic", instance_id="0", wind_rose="A", N="6", K="3", grid_rows="3",
                     grid_cols="2", seed="0", method="exact", variant="exact",
                     energy_best="-1.5", energy_gap="0.0", time_s="0.01")
    quantum = dict(classical, method="qaoa", variant="xy+dicke", p="1", lam_mult="0.0", p_optimal="0.1",
                   p_feasible="1.0", approx_ratio_feasible="0.7", uniform_feasible_p_optimal="0.05",
                   uniform_feasible_ratio="0.5", random_p_hit="0.9", shots="1000", n_evals="120")
    assert validate_per_instance([classical, quantum], PER_INSTANCE_COLUMNS) == []
    assert validate_per_instance([dict(classical, dataset="real")], PER_INSTANCE_COLUMNS) != []
    assert validate_per_instance([dict(classical, p="1")], PER_INSTANCE_COLUMNS) != []
    assert validate_per_instance([dict(quantum, p_optimal="")], PER_INSTANCE_COLUMNS) != []
    assert validate_per_instance([classical], PER_INSTANCE_COLUMNS[:-1]) != []


def test_schema_doc_documents_every_field():
    """docs/results_schema.md must name every key and column the validators require."""
    assert os.path.getsize(SCHEMA_DOC) > 0, "docs/results_schema.md is empty"
    with open(SCHEMA_DOC, encoding="utf-8") as f:
        doc = f.read()
    names = (set(SUMMARY_KEYS) | set(INSTANCE_KEYS) | set(RESULT_KEYS) | set(METRIC_KEYS)
             | set(QAOA_METRICS) | set(CLASSICAL_METRICS) | set(QAOA_RESULT_EXTRA) | set(BASELINE_KEYS)
             | set(PER_INSTANCE_COLUMNS) | set(DATASET_KEYS))
    missing = sorted(n for n in names if n not in doc)
    assert not missing, f"undocumented fields: {missing}"
    assert "real_<site>" in doc and "synthetic" in doc


def test_generated_summary_follows_schema():
    if not os.path.exists(SUMMARY) or os.path.getsize(SUMMARY) == 0:
        pytest.skip("results/summary.json has not been generated yet")
    with open(SUMMARY, encoding="utf-8") as f:
        assert validate_summary(json.load(f)) == []


def test_generated_per_instance_follows_schema():
    if not os.path.exists(PER_INSTANCE) or os.path.getsize(PER_INSTANCE) == 0:
        pytest.skip("results/per_instance.csv has not been generated yet")
    with open(PER_INSTANCE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert validate_per_instance(rows, reader.fieldnames) == []


@pytest.mark.parametrize("name", ["synthetic", "synthetic_n16", "synthetic_n18", "real_penmanshiel_allk"])
def test_extended_dataset_names_are_valid(name):
    s = _valid_summary()
    for d in s["datasets"]:
        d["dataset"] = name if d["dataset"] == "synthetic" else d["dataset"]
    for i in s["instances"]:
        i["dataset"] = name if i["dataset"] == "synthetic" else i["dataset"]
    for r in s["results"]:
        r["dataset"] = name if r["dataset"] == "synthetic" else r["dataset"]
    assert validate_summary(s) == []


@pytest.mark.parametrize("name", ["Synthetic", "synthetic_", "synthetic_N16", "synthetic-n16", "real"])
def test_bad_dataset_names_are_rejected(name):
    assert not DATASET_RE.match(name)
