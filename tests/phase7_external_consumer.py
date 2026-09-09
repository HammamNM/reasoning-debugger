import subprocess
import sys


def test_external_consumer_uses_only_public_kernel_api():
    code = """
from kernel.api import (
    DebugFinding,
    PrimitiveType,
    ReasoningDebugger,
    ReasoningTrace,
    ReasoningTraceEvent,
)

trace = ReasoningTrace(
    events=(
        ReasoningTraceEvent(
            "external-event-1",
            "Observation.",
            "OBSERVATION",
        ),
    )
)

assert PrimitiveType.OBSERVATION.name == "OBSERVATION"

findings = ReasoningDebugger().debug(trace)

assert isinstance(findings, list)
assert all(isinstance(item, DebugFinding) for item in findings)
assert len(trace.events) == 1
"""

    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr


def test_external_consumer_cannot_import_kernel_internals_from_public_api():
    forbidden_symbols = [
        "ReasoningEvent",
        "EventStream",
        "create_event",
        "Edge",
        "EdgeRelation",
        "ReasoningGraph",
        "ReasoningUnit",
        "ParserPipeline",
        "QueryEngine",
        "KernelRuntime",
        "KernelSession",
    ]

    for symbol in forbidden_symbols:
        code = f"from kernel.api import {symbol}"

        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0, (
            f"{symbol} leaked through kernel.api"
        )
