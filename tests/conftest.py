import os
import sys

# Add qollab to sys.path so tests can import `qwind` exactly as main.py will in the platform
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'qollab')))


def pytest_configure(config):
    config.addinivalue_line("markers", "heavy: slowest tests (process pool); deselect locally with -m 'not heavy'")
