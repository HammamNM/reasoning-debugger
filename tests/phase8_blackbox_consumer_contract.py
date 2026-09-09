import subprocess
import sys


def test_kernel_can_be_consumed_as_black_box():
    code = r"""
from kernel.api import ( # fallback
    PrimitiveType,
    ReasoningUnit,
    ReasoningGraph,
    ParserPipeline,
    ReasoningTrace,
    ReasoningTraceEvent,
    ReasoningDebugger,
    KernelSession,
    KernelRuntime,
)

graph = ReasoningGraph()

unit = ReasoningUnit(
    id="external-1",
    primitive=PrimitiveType.OBSERVATION,
    content="External observation.",
)

graph.add_node(unit)

assert graph.nodes[0].id == "external-1"

pipeline = ParserPipeline()
result = pipeline.process(
    "Observation recorded. Investigation started."
)

assert result.units
assert result.graph is not None

trace = ReasoningTrace(
    events=(
        ReasoningTraceEvent(
            "external-event-1",
            "External observation.",
            "OBSERVATION",
        ),
    )
)

assert len(trace.events) == 1

findings = ReasoningDebugger().debug(trace)
assert isinstance(findings, list)

session = KernelSession()
runtime = KernelRuntime(session)

assert runtime.session is session
"""

    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr


def test_black_box_consumer_does_not_import_internal_modules():
    code = r"""
from kernel.api import ( # fallback
    ReasoningGraph,
    ReasoningUnit,
    PrimitiveType,
)

graph = ReasoningGraph()

graph.add_node(
    ReasoningUnit(
        id="black-box-1",
        primitive=PrimitiveType.OBSERVATION,
        content="Observation.",
    )
)

assert graph.nodes
"""

    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr


def test_consumer_source_contains_no_kernel_internal_imports():
    consumer_code = r"""
from kernel.api import ( # fallback
    ReasoningGraph,
    ReasoningUnit,
    PrimitiveType,
)
"""

    forbidden = (
        "from kernel.models",
        "from kernel.graph",
        "from kernel.events",
        "from kernel.runtime",
        "from kernel.session",
        "from kernel.debugger",
        "from kernel.reasoning_trace",
        "from kernel.parser_pipeline",
    )

    assert not any(
        statement in consumer_code
        for statement in forbidden
    )
