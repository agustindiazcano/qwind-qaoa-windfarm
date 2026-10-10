import os
import ast
import sys
import pytest

def get_allowed_packages():
    """Read qollab/requirements.txt and return a set of allowed package names."""
    qollab_req_path = os.path.join(os.path.dirname(__file__), '..', 'qollab', 'requirements.txt')
    allowed = set(["qwind", "main"])
    with open(qollab_req_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('-'):
                # Extract package name (e.g., qiskit==2.5.2 -> qiskit)
                pkg = line.split('==')[0].split('>=')[0].split('<')[0].split('~=')[0].strip()
                allowed.add(pkg)
    return allowed

def test_qollab_imports():
    """Ensure qollab/ only imports allowed modules (stdlib + qollab/requirements.txt + project modules)."""
    allowed_packages = get_allowed_packages()
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
                            if not is_allowed(module_name, allowed_packages):
                                pytest.fail(f"Forbidden import '{module_name}' in {path}")
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            module_name = node.module.split('.')[0]
                            if not is_allowed(module_name, allowed_packages):
                                pytest.fail(f"Forbidden import '{module_name}' in {path}")

def is_allowed(module_name, allowed_packages):
    if hasattr(sys, 'stdlib_module_names'):
        if module_name in sys.stdlib_module_names:
            return True
    
    # Check against allowed packages
    if module_name in allowed_packages:
        return True
        
    return False

def test_qollab_requirements_pinned():
    """Ensure qollab/requirements.txt only contains strictly pinned versions (==)."""
    qollab_req_path = os.path.join(os.path.dirname(__file__), '..', 'qollab', 'requirements.txt')
    with open(qollab_req_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                assert '==' in line, f"Requirement '{line}' is not strictly pinned with '=='"
                assert '>=' not in line and '<=' not in line and '~=' not in line, f"Requirement '{line}' uses flexible pinning"

def test_qollab_main_execution():
    """Test that main.py defines main() and it runs correctly with default arguments."""
    import main
    # We call it. It should not raise any exceptions.
    main.main()


def test_qollab_main_import_has_no_side_effects():
    """Importing main must only define main(): no output, no work, no __main__ block."""
    import subprocess
    qollab_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'qollab'))
    result = subprocess.run(
        [sys.executable, "-c", "import main"],
        cwd=qollab_dir, capture_output=True, text=True, check=True,
    )
    assert result.stdout == ""

    with open(os.path.join(qollab_dir, "main.py"), "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())
    for node in tree.body:
        assert not isinstance(node, ast.If), "main.py must not have a module-level 'if' (e.g. __main__ block)"
        assert not (isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)), \
            "main.py must not call anything at module level"
