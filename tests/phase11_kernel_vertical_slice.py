from kernel.api import (
    ParserPipeline,
    ReasoningDebugger,
    ReasoningTrace,
    ReasoningTraceEvent,
    PrimitiveType,
    DebugFinding,
)


def test_kernel_vertical_slice_from_trace_to_debug_finding():
    trace = ReasoningTrace(
        events=(
            ReasoningTraceEvent(
                id="e1",
                content="The patient has chest pain.",
                event_type="OBSERVATION",
            ),
            ReasoningTraceEvent(
                id="e2",
                content="The conclusion assumes that the normal test excludes the disease.",
                event_type="unsupported_assumption",
            ),
            ReasoningTraceEvent(
                id="e3",
                content="Therefore the patient is safe to discharge.",
                event_type="DECISION_ASSESSMENT",
            ),
        )
    )

    findings = ReasoningDebugger().debug(trace)

    assert findings
    assert all(isinstance(finding, DebugFinding) for finding in findings)

    finding = findings[0]

    assert finding.event_id == "e2"
    assert finding.failure_type == "unsupported_assumption"
    assert finding.affected_event_ids == ("e3",)


def test_kernel_parser_pipeline_produces_structural_units():
    pipeline = ParserPipeline()

    result = pipeline.process(
        "Patient has chest pain. "
        "Troponin is normal. "
        "Therefore discharge the patient."
    )

    assert result.units
    assert all(hasattr(unit, "id") for unit in result.units)
    assert all(hasattr(unit, "primitive") for unit in result.units)
    assert all(hasattr(unit, "content") for unit in result.units)

    assert result.graph.nodes
    assert len(result.graph.nodes) == len(result.units)

    assert all(
        unit.primitive in PrimitiveType
        for unit in result.units
    )


def test_debugger_preserves_trace_immutability():
    trace = ReasoningTrace(
        events=(
            ReasoningTraceEvent(
                id="e1",
                content="Observation.",
                event_type="OBSERVATION",
            ),
            ReasoningTraceEvent(
                id="e2",
                content="Unsupported assumption.",
                event_type="unsupported_assumption",
            ),
            ReasoningTraceEvent(
                id="e3",
                content="Decision.",
                event_type="DECISION_ASSESSMENT",
            ),
        )
    )

    original_events = trace.events

    ReasoningDebugger().debug(trace)

    assert trace.events == original_events
    assert trace.events[1].id == "e2"
