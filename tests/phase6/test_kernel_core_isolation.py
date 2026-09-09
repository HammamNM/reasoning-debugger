import ast
from pathlib import Path


FORBIDDEN_ROOTS = {
    "analytics",
    "backend",
    "decision_engine",
    "outcome_engine",
    "simulation",
}


CORE_MODULES = [
    "models.py",
    "graph.py",
    "events.py",
    "provenance.py",
    "query_engine.py",
    "reasoning_trace.py",
    "debug_finding.py",
    "reasoning_failure_detector.py",
    "structural_failure_detector.py",
    "failure_propagation.py",
    "trace_graph_adapter.py",
    "parser_pipeline.py",
    "unit_graph_builder.py",
]


def imported_root_names(path: Path):
    tree = ast.parse(path.read_text())
    roots = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.add(alias.name.split(".")[0])

        elif isinstance(node, ast.ImportFrom):
            if node.module:
                roots.add(node.module.split(".")[0])

    return roots


def test_kernel_core_has_no_application_domain_imports():
    kernel_root = Path("kernel")

    for filename in CORE_MODULES:
        path = kernel_root / filename
        assert path.exists(), f"Expected kernel core module missing: {path}"

        imported = imported_root_names(path)
        forbidden = imported & FORBIDDEN_ROOTS

        assert not forbidden, (
            f"{path} imports application domains directly: "
            f"{sorted(forbidden)}"
        )


def test_public_api_does_not_import_application_domains():
    imported = imported_root_names(Path("kernel/api.py"))
    forbidden = imported & FORBIDDEN_ROOTS

    assert not forbidden, (
        "kernel/api.py imports application domains directly: "
        f"{sorted(forbidden)}"
    )
