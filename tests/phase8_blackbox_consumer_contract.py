import subprocess
import sys


def test_kernel_can_be_consumed_as_black_box():
    code = r"""
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
            "External observation.",
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


def test_black_box_consumer_cannot_access_internal_symbols():
    forbidden = (
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
    )

    for symbol in forbidden:
        code = f"""
from kernel.api import {symbol}
"""

        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0, (
            f"Internal symbol leaked: {symbol}"
        )


def test_consumer_source_contains_no_internal_module_imports():
    consumer_code = r"""
from kernel.api import (
    DebugFinding,
    PrimitiveType,
    ReasoningDebugger,
    ReasoningTrace,
    ReasoningTraceEvent,
)
"""

    forbidden_modules = (
        "from kernel.models",
        "from kernel.graph",
        "from kernel.events",
        "from kernel.runtime",
        "from kernel.session",
        "from kernel.debugger",
        "from kernel.reasoning_trace",
        "from kernel.parser_pipeline",
        "from kernel.query_engine",
    )

    assert not any(
        statement in consumer_code
        for statement in forbidden_modules
    )
