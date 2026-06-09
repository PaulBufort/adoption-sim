"""Dependency policy enforcement (spec §3): the core engine imports nothing
beyond networkx, numpy, and the standard library. Streamlit lives in /demo,
matplotlib in /experiments — never here. This test is the policy."""

import ast
import pathlib
import sys

ALLOWED_THIRD_PARTY = {"networkx", "numpy"}
CORE = pathlib.Path(__file__).resolve().parent.parent / "core"


def imported_roots(path: pathlib.Path) -> set[str]:
    tree = ast.parse(path.read_text())
    roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            roots.add(node.module.split(".")[0])
    return roots


def test_core_imports_only_networkx_numpy_stdlib():
    offenders = {}
    for py in sorted(CORE.glob("*.py")):
        bad = {
            r for r in imported_roots(py)
            if r not in ALLOWED_THIRD_PARTY
            and r != "core"
            and r not in sys.stdlib_module_names
        }
        if bad:
            offenders[py.name] = sorted(bad)
    assert not offenders, f"core/ stack policy violated: {offenders}"


def test_core_has_meaningful_surface():
    files = {p.name for p in CORE.glob("*.py")}
    assert {"orggen.py", "dynamics.py", "seeding.py", "metrics.py",
            "sweep.py", "scenario.py", "ingest.py"} <= files
