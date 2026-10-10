import os
import ast
import importlib
import pytest
import importlib

def test_qollab_forbidden_imports():
    """Ensure qollab/ only imports allowed modules (numpy, scipy, qiskit, stdlib)."""
    allowed_external = {"numpy", "scipy", "qiskit", "qwind"}
    
    qollab_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'qollab'))
    
    for root, _, files in os.walk(qollab_dir):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read(), filename=path)
                
                for node in ast.walk(tree):
                    module_name = None
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            module_name = alias.name.split('.')[0]
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            module_name = node.module.split('.')[0]
                            
                    if module_name:
                        # Check if it's a built-in / stdlib
                        # A simple heuristic: if we can import it and it doesn't have a __file__ (some C modules) 
                        # or it's in the standard library path. A safer way in Python 3.10+ is sys.stdlib_module_names
                        import sys
                        if hasattr(sys, 'stdlib_module_names'):
                            is_stdlib = module_name in sys.stdlib_module_names
                        else:
                            # Fallback
                            try:
                                spec = importlib.util.find_spec(module_name)
                                is_stdlib = spec is not None and ('site-packages' not in (spec.origin or ''))
                            except Exception:
                                is_stdlib = False
                                
                        if not is_stdlib and module_name not in allowed_external:
                            pytest.fail(f"Forbidden import '{module_name}' in {path}")
                            
def test_qollab_main_execution():
    """Test that main.py defines main() and it runs correctly with default arguments."""
    import main
    # We call it. It should not raise any exceptions.
    main.main()
