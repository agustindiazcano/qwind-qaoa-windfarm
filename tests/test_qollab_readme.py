import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def test_the_qollab_folder_carries_the_same_readme():
    """qollab/ is what gets uploaded, so its README must be the repository README (copy it by hand after editing)."""
    assert _read("qollab", "README.md") == _read("README.md")
