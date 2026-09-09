import ast
from pathlib import Path


PUBLIC_API = Path("kernel/api.py")


def imported_modules(path):
    tree = ast.parse(path.read_text())
    modules = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
        elif isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)

    return modules


def test_public_api_has_no_application_dependencies():
    forbidden = {
        "analytics",
        "backend",
        "decision_engine",
        "outcome_engine",
        "simulation",
    }

    roots = {
        module.split(".")[0]
        for module in imported_modules(PUBLIC_API)
    }

    assert not (roots & forbidden), roots & forbidden


def test_public_api_exports_only_explicit_symbols():
    tree = ast.parse(PUBLIC_API.read_text())

    all_values = None

    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    all_values = ast.literal_eval(node.value)

    assert isinstance(all_values, list)
    assert all_values
    assert len(all_values) == len(set(all_values))

    for name in all_values:
        assert isinstance(name, str)
        assert not name.startswith("_")


def test_public_api_symbols_resolve():
    from kernel import api

    for name in api.__all__:
        assert hasattr(api, name), name
        value = getattr(api, name)

        assert getattr(value, "__module__", None)
        assert getattr(value, "__name__", None)
