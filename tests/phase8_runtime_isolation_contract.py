import subprocess
import sys


APPLICATION_ROOTS = (
    "analytics",
    "backend",
    "decision_engine",
    "outcome_engine",
    "simulation",
)


def run_import_check(code):
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    return result.stdout


def assert_no_application_modules_loaded(output):
    leaks = [
        line
        for line in output.splitlines()
        if line.startswith("LEAK:")
    ]

    assert not leaks, leaks


def test_import_kernel_package_isolated():
    output = run_import_check(
        """
import sys
import kernel

for name in sorted(sys.modules):
    if name.startswith((
        "analytics",
        "backend",
        "decision_engine",
        "outcome_engine",
        "simulation",
    )):
        print("LEAK:", name)
"""
    )

    assert_no_application_modules_loaded(output)


def test_import_kernel_api_isolated():
    output = run_import_check(
        """
import sys
from kernel import api

for name in sorted(sys.modules):
    if name.startswith((
        "analytics",
        "backend",
        "decision_engine",
        "outcome_engine",
        "simulation",
    )):
        print("LEAK:", name)
"""
    )

    assert_no_application_modules_loaded(output)


def test_import_kernel_core_modules_isolated():
    output = run_import_check(
        """
import sys

modules = [
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
    "kernel.parser_pipeline",
    "kernel.unit_graph_builder",
]

for module_name in modules:
    __import__(module_name)

for name in sorted(sys.modules):
    if name.startswith((
        "analytics",
        "backend",
        "decision_engine",
        "outcome_engine",
        "simulation",
    )):
        print("LEAK:", name)
"""
    )

    assert_no_application_modules_loaded(output)
