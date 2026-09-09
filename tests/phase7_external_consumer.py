import subprocess
import sys


def test_external_consumer_uses_only_public_kernel_api():
    code = """
from kernel.api import ( # fallback
    ReasoningGraph,
    ReasoningUnit,
    PrimitiveType,
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
    content="External consumer observation.",
)

graph.add_node(unit)

pipeline = ParserPipeline()
parsed = pipeline.process("Observation. Evidence.")

trace = ReasoningTrace(
    events=(
        ReasoningTraceEvent(
            "external-event-1",
            "Observation.",
            "OBSERVATION",
        ),
    )
)

findings = ReasoningDebugger().debug(trace)

session = KernelSession()
runtime = KernelRuntime(session)

assert graph.nodes[0].id == "external-1"
assert parsed.units
assert len(trace.events) == 1
assert isinstance(findings, list)
assert runtime.session is session
"""

    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
