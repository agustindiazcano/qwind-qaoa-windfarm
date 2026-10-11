"""
Assemble the folder to upload to a SEPARATE Qollab test project (do not publish it; the submission project stays untouched):

    python scripts/make_probe_project.py                 # writes build/probe_project/{main.py, qwind/, requirements.txt}

The folder holds the qwind package, the backend probe as main.py, and the same pinned requirements as qollab/.
Standard library only.
"""
import argparse
import os
import shutil

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "build", "probe_project"))
    args = ap.parse_args(argv)
    if os.path.exists(args.out):
        shutil.rmtree(args.out)
    shutil.copytree(os.path.join(ROOT, "qollab", "qwind"), os.path.join(args.out, "qwind"),
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    shutil.copyfile(os.path.join(ROOT, "experiments", "probe_main.py"), os.path.join(args.out, "main.py"))
    shutil.copyfile(os.path.join(ROOT, "qollab", "requirements.txt"), os.path.join(args.out, "requirements.txt"))
    print("wrote", args.out)


if __name__ == "__main__":
    main()
