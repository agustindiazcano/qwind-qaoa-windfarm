"""
The live Qollab Run must never reach the 14-turbine Penmanshiel instance (nor any real-farm or wind-rose file):
real farms are OFFLINE ONLY (experiments/, results/).
"""
import ast
import os

QOLLAB = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "qollab"))
FORBIDDEN_TEXT = ("farms.json", "windrose.json", "load_farm", "load_wind_rose", "farm_coords_D", "select_closest",
                  "qwind.instances", "from qwind import instances")


def _imported_qwind_modules(path):
    with open(path, encoding="utf-8") as f:
        tree = ast.parse(f.read())
    mods = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and node.module.split(".")[0] == "qwind":
            mods.add(node.module.split(".")[1] if "." in node.module else None)
        elif isinstance(node, ast.Import):
            mods.update(a.name.split(".")[1] for a in node.names if a.name.startswith("qwind."))
    return {m for m in mods if m}


def _reachable_from_main():
    seen, todo = set(), list(_imported_qwind_modules(os.path.join(QOLLAB, "main.py")))
    while todo:
        m = todo.pop()
        if m in seen:
            continue
        seen.add(m)
        todo += _imported_qwind_modules(os.path.join(QOLLAB, "qwind", m + ".py"))
    return seen


def test_live_run_does_not_load_farm_or_rose_files():
    paths = [os.path.join(QOLLAB, "main.py")] + [os.path.join(QOLLAB, "qwind", m + ".py") for m in _reachable_from_main()]
    for path in paths:
        text = open(path, encoding="utf-8").read()
        for word in FORBIDDEN_TEXT:
            assert word not in text, f"{os.path.basename(path)} must not reference {word!r}"


def test_instances_module_is_not_reachable_from_main():
    assert "instances" not in _reachable_from_main()
