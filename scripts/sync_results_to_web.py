"""
Copy results/summary.json to web/data/summary.json (the only file the website reads).

    python scripts/sync_results_to_web.py                 # refuses a `smoke` summary
    python scripts/sync_results_to_web.py --allow-smoke   # for frontend development with sample data only

Checks the minimum the page relies on (schema in docs/results_schema.md; the full validator is
tests/test_results_schema.py). Standard library only.
"""
import argparse
import json
import os
import shutil

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REQUIRED = ["schema_version", "status", "protocol", "datasets", "instances", "results", "caveats"]


def sync(results_dir, web_dir, allow_smoke=False):
    src = os.path.join(results_dir, "summary.json")
    if not os.path.exists(src):
        raise FileNotFoundError(src)
    with open(src, encoding="utf-8") as f:
        text = f.read()
    if not text.strip():
        raise ValueError(f"{src} is empty")
    summary = json.loads(text)
    missing = [k for k in REQUIRED if k not in summary]
    if missing:
        raise ValueError(f"{src} is not a results summary, missing keys (datasets, results, ...): {missing}")
    if summary["status"] != "final" and not allow_smoke:
        raise ValueError(f"{src} has status {summary['status']!r} (smoke runs are not results); use --allow-smoke for sample data")
    dst_dir = os.path.join(web_dir, "data")
    os.makedirs(dst_dir, exist_ok=True)
    dst = os.path.join(dst_dir, "summary.json")
    shutil.copyfile(src, dst)
    return dst


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=os.path.join(ROOT, "results"))
    ap.add_argument("--web", default=os.path.join(ROOT, "web"))
    ap.add_argument("--allow-smoke", action="store_true")
    args = ap.parse_args(argv)
    print("copied ->", sync(args.results, args.web, allow_smoke=args.allow_smoke))


if __name__ == "__main__":
    main()
