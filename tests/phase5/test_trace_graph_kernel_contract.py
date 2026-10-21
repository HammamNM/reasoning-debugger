import pytest

from kernel.models import PrimitiveType
from kernel.reasoning_trace import ReasoningTrace, ReasoningTraceEvent
from kernel.trace_graph_adapter import TraceGraphAdapter


def test_adapter_maps_real_kernel_event_types():
    trace = ReasoningTrace(
        events=(
            ReasoningTraceEvent("e1", "Observation", "OBSERVATION"),
            ReasoningTraceEvent("e2", "Evidence", "EVIDENCE"),
            ReasoningTraceEvent("e3", "Inference", "INFERENCE"),
            ReasoningTraceEvent("e4", "Investigation", "INVESTIGATION_RESULT"),
            ReasoningTraceEvent("e5", "Decision", "DECISION_ASSESSMENT"),
            ReasoningTraceEvent("e6", "Outcome", "OUTCOME_UPDATED"),
        )
    )

    graph = TraceGraphAdapter().build(trace)

    assert [node.primitive for node in graph.nodes] == [
        PrimitiveType.OBSERVATION,
        PrimitiveType.EVIDENCE,
        PrimitiveType.INFERENCE,
        PrimitiveType.INVESTIGATION,
        PrimitiveType.DECISION,
        PrimitiveType.OUTCOME,
    ]


def test_adapter_maps_unmapped_kernel_event_type_to_generic_event():
    trace = ReasoningTrace(
        events=(
            ReasoningTraceEvent(
                "e1",
                "Action",
                "ACTION",
            ),
        )
    )

    graph = TraceGraphAdapter().build(trace)
    assert graph.nodes[0].primitive == PrimitiveType.GENERIC_EVENT
    assert graph.nodes[0].provenance.event_type == "ACTION"


def test_adapter_preserves_real_kernel_event_order():
    trace = ReasoningTrace(
        events=(
            ReasoningTraceEvent("e1", "First", "OBSERVATION"),
            ReasoningTraceEvent("e2", "Second", "EVIDENCE"),
            ReasoningTraceEvent("e3", "Third", "INFERENCE"),
        )
    )

    graph = TraceGraphAdapter().build(trace)

    assert [node.id for node in graph.nodes] == ["e1", "e2", "e3"]
    assert [(e.source, e.target) for e in graph.edges] == [
        ("e1", "e2"),
        ("e2", "e3"),
    ]


def test_debugger_rejects_invalid_trace():
    from kernel.api import ReasoningDebugger, InvalidTraceSchemaError

    with pytest.raises(InvalidTraceSchemaError):
        ReasoningDebugger().debug(object())
