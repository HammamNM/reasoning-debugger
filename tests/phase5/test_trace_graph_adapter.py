import pytest

from kernel.graph import EdgeRelation
from kernel.models import PrimitiveType
from kernel.reasoning_trace import ReasoningTrace, ReasoningTraceEvent
from kernel.trace_graph_adapter import TraceGraphAdapter


def event(event_id, content, event_type):
    return ReasoningTraceEvent(
        id=event_id,
        content=content,
        event_type=event_type,
    )


def test_adapter_preserves_event_order_and_ids():
    trace = ReasoningTrace(
        events=(
            event("event-1", "Observation.", "observation"),
            event("event-2", "Hypothesis.", "hypothesis"),
            event("event-3", "Decision.", "decision"),
        )
    )

    graph = TraceGraphAdapter().build(trace)

    assert [node.id for node in graph.nodes] == [
        "event-1",
        "event-2",
        "event-3",
    ]


def test_adapter_maps_event_types_to_primitives():
    trace = ReasoningTrace(
        events=(
            event("event-1", "Evidence.", "evidence"),
            event("event-2", "Hypothesis.", "hypothesis"),
            event("event-3", "Decision.", "decision"),
        )
    )

    graph = TraceGraphAdapter().build(trace)

    assert graph.nodes[0].primitive == PrimitiveType.EVIDENCE
    assert graph.nodes[1].primitive == PrimitiveType.HYPOTHESIS
    assert graph.nodes[2].primitive == PrimitiveType.DECISION


def test_adapter_creates_only_sequence_edges():
    trace = ReasoningTrace(
        events=(
            event("event-1", "First.", "observation"),
            event("event-2", "Second.", "hypothesis"),
            event("event-3", "Third.", "decision"),
        )
    )

    graph = TraceGraphAdapter().build(trace)

    assert len(graph.edges) == 2
    assert all(
        edge.relation == EdgeRelation.SEQUENCE
        for edge in graph.edges
    )


def test_adapter_rejects_invalid_trace():
    with pytest.raises(TypeError):
        TraceGraphAdapter().build(object())


def test_adapter_rejects_unknown_event_type():
    trace = ReasoningTrace(
        events=(
            event("event-1", "Unknown.", "something_unknown"),
        )
    )

    with pytest.raises(ValueError):
        TraceGraphAdapter().build(trace)


def test_adapter_does_not_modify_trace():
    trace = ReasoningTrace(
        events=(
            event("event-1", "Observation.", "observation"),
        )
    )

    original_events = trace.events

    TraceGraphAdapter().build(trace)

    assert trace.events == original_events
