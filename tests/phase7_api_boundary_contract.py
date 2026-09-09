import ast
from pathlib import Path


def test_public_api_exports_are_explicit():
    api_path = Path("kernel/api.py")
    tree = ast.parse(api_path.read_text())

    all_values = None

    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    all_values = ast.literal_eval(node.value)

    assert all_values is not None
    assert isinstance(all_values, list)
    assert all_values
    assert len(all_values) == len(set(all_values))


def test_public_api_exports_only_existing_symbols():
    from kernel import api

    for name in api.__all__:
        assert hasattr(api, name), (
            f"Public API declares missing symbol: {name}"
        )


def test_public_api_has_no_private_exports():
    from kernel import api

    for name in api.__all__:
        assert not name.startswith("_"), (
            f"Private symbol exposed through public API: {name}"
        )


def test_public_api_does_not_expose_module_objects():
    from kernel import api

    for name in api.__all__:
        value = getattr(api, name)

        assert getattr(value, "__name__", None) != "kernel", (
            f"Kernel package object exposed as public symbol: {name}"
        )
