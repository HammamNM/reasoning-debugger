import ast
from pathlib import Path


FORBIDDEN_INTERNAL_MODULES = {
    "kernel.debug_finding",
    "kernel.debugger",
    "kernel.events",
    "kernel.failure_propagation",
    "kernel.graph",
    "kernel.models",
    "kernel.parser_pipeline",
    "kernel.reasoning_trace",
    "kernel.runtime",
    "kernel.session",
    "kernel.trace_graph_adapter",
}


CONSUMER_ROOTS = (
    Path("analytics"),
    Path("backend"),
    Path("decision_engine"),
    Path("outcome_engine"),
    Path("simulation"),
)


def imported_modules(path: Path):
    tree = ast.parse(path.read_text())
    modules = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
        elif isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)

    return modules


def test_application_consumers_do_not_import_kernel_internals():
    violations = []

    for root in CONSUMER_ROOTS:
        if not root.exists():
            continue

        for path in root.rglob("*.py"):
            for module in imported_modules(path):
                if module in FORBIDDEN_INTERNAL_MODULES:
                    violations.append((str(path), module))

    assert not violations, violations


def test_main_entrypoint_does_not_import_kernel_internals():
    path = Path("main.py")

    if not path.exists():
        return

    violations = [
        module
        for module in imported_modules(path)
        if module in FORBIDDEN_INTERNAL_MODULES
    ]

    assert not violations, violations
