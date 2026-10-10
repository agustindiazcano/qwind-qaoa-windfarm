import os
import sys

# Add qollab to sys.path so tests can import `qwind` exactly as main.py will in the platform
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'qollab')))
