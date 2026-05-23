"""
Audit the project structure: list all source files, check critical paths exist,
verify imports succeed, and report the module inventory.

Run from repo root: python scripts/00_audit_project.py
"""

import sys
import os
import importlib

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def check_path(path, label):
    full = os.path.join(REPO_ROOT, path)
    exists = os.path.exists(full)
    status = "OK" if exists else "MISSING"
    print(f"  [{status}] {path}  ({label})")
    return exists


def check_import(module, label):
    try:
        importlib.import_module(module)
        print(f"  [OK] import {module}  ({label})")
        return True
    except Exception as e:
        print(f"  [FAIL] import {module}  ({label}): {e}")
        return False


def list_py_files(directory):
    full = os.path.join(REPO_ROOT, directory)
    if not os.path.isdir(full):
        print(f"  [MISSING] directory {directory}")
        return
    for fname in sorted(os.listdir(full)):
        if fname.endswith(".py"):
            fpath = os.path.join(full, fname)
            size = os.path.getsize(fpath)
            print(f"    {fname:<40} {size:>7} bytes")


def main():
    print("=" * 60)
    print("Chirality Atlas: Project Audit")
    print("=" * 60)

    print("\n--- Critical paths ---")
    required_paths = [
        ("src/chirality/__init__.py", "main package"),
        ("src/chirality/model_library/__init__.py", "model_library package"),
        ("src/chirality/model_library/fisher_kpp.py", "Fisher-KPP"),
        ("src/chirality/model_library/fitzhugh_nagumo.py", "FitzHugh-Nagumo"),
        ("src/chirality/model_library/gierer_meinhardt.py", "Gierer-Meinhardt"),
        ("src/chirality/model_library/cahn_hilliard.py", "Cahn-Hilliard"),
        ("src/chirality/model_library/gray_scott.py", "Gray-Scott"),
        ("src/chirality/model_library/active_particles.py", "active particles"),
        ("src/chirality/visualization/__init__.py", "visualization package"),
        ("src/chirality/visualization/style.py", "style constants"),
        ("src/chirality/visualization/plots.py", "plotting functions"),
        ("src/chirality/visualization/animations.py", "animation utilities"),
        ("docs/CLAUDE_CONTEXT.md", "project brief"),
        ("docs/baseline_audit.md", "baseline audit"),
        ("requirements.txt", "dependencies"),
    ]
    all_paths_ok = all(check_path(p, label) for p, label in required_paths)

    print("\n--- Source file inventory ---")
    print("  src/chirality/:")
    list_py_files("src/chirality")
    print("  src/chirality/model_library/:")
    list_py_files("src/chirality/model_library")
    print("  src/chirality/visualization/:")
    list_py_files("src/chirality/visualization")
    print("  scripts/:")
    list_py_files("scripts")

    print("\n--- Import checks ---")
    imports_to_check = [
        ("chirality.model_library", "model_library package"),
        ("chirality.model_library.fisher_kpp", "Fisher-KPP"),
        ("chirality.model_library.fitzhugh_nagumo", "FitzHugh-Nagumo"),
        ("chirality.model_library.gierer_meinhardt", "Gierer-Meinhardt"),
        ("chirality.model_library.cahn_hilliard", "Cahn-Hilliard"),
        ("chirality.model_library.gray_scott", "Gray-Scott"),
        ("chirality.model_library.active_particles", "active particles"),
        ("chirality.visualization", "visualization package"),
    ]
    all_imports_ok = all(check_import(m, label) for m, label in imports_to_check)

    print("\n--- Summary ---")
    if all_paths_ok and all_imports_ok:
        print("  PASS: all paths present and all imports succeed.")
    else:
        if not all_paths_ok:
            print("  FAIL: some required paths are missing.")
        if not all_imports_ok:
            print("  FAIL: some imports failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
