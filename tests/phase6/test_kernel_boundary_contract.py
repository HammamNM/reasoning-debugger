import importlib


def test_kernel_core_does_not_import_application_domains():
    forbidden_prefixes = (
        "analytics",
        "backend",
        "decision_engine",
        "outcome_engine",
        "simulation",
    )

    kernel_modules = [
        "kernel.models",
        "kernel.graph",
        "kernel.events",
        "kernel.provenance",
        "kernel.query_engine",
        "kernel.reasoning_trace",
        "kernel.debug_finding",
        "kernel.reasoning_failure_detector",
        "kernel.structural_failure_detector",
        "kernel.failure_propagation",
        "kernel.trace_graph_adapter",
        "kernel.debugger",
        "kernel.parser",
        "kernel.parser_pipeline",
        "kernel.unit_graph_builder",
    ]

    for module_name in kernel_modules:
        module = importlib.import_module(module_name)

        for loaded_name in module.__dict__.values():
            if getattr(loaded_name, "__module__", "").startswith(forbidden_prefixes):
                raise AssertionError(
                    f"{module_name} depends directly on application domain "
                    f"module {loaded_name.__module__}"
                )


def test_kernel_public_api_modules_are_importable():
    public_modules = [
        "kernel.models",
        "kernel.graph",
        "kernel.events",
        "kernel.reasoning_trace",
        "kernel.debug_finding",
        "kernel.debugger",
        "kernel.parser_pipeline",
    ]

    for module_name in public_modules:
        importlib.import_module(module_name)
