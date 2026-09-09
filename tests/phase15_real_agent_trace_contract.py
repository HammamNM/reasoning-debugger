import pytest
from kernel.models import PrimitiveType
from kernel.reasoning_trace import ReasoningTrace, ReasoningTraceEvent
from kernel.trace_graph_adapter import TraceGraphAdapter

def test_trace_adapter_preserves_event_identity_and_provenance():
    adapter = TraceGraphAdapter()
    trace = ReasoningTrace(events=(
        ReasoningTraceEvent(id="trace_event_001", content="Data", event_type="OBSERVATION"),
    ))
    graph = adapter.build(trace)

    assert len(graph.nodes) == 1
    assert graph.nodes[0].id == "trace_event_001"
    assert graph.nodes[0].primitive == PrimitiveType.OBSERVATION

def test_trace_adapter_rejects_debug_annotations_as_primitives():
    adapter = TraceGraphAdapter()
    trace = ReasoningTrace(events=(
        ReasoningTraceEvent(id="e1", content="Failed inference", event_type="unsupported_assumption"),
    ))

    # Contract: The kernel must reject debug labels mixed into reasoning traces
    with pytest.raises(ValueError, match="Unknown trace event_type"):
        adapter.build(trace)

def test_trace_event_metadata_preserves_real_agent_context():
    event = ReasoningTraceEvent(
        id="e1",
        content="Agent thinking...",
        event_type="INFERENCE",
        metadata={"agent_model": "gpt-4", "execution_time_ms": 150}
    )

    assert event.metadata["agent_model"] == "gpt-4"
    assert event.metadata["execution_time_ms"] == 150
