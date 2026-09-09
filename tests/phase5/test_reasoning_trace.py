import pytest

from kernel.reasoning_trace import (
    ReasoningTrace,
    ReasoningTraceEvent,
)


def test_trace_event_preserves_core_fields():
    event = ReasoningTraceEvent(
        id="event-1",
        content="Evidence indicates X.",
        event_type="evidence",
    )

    assert event.id == "event-1"
    assert event.content == "Evidence indicates X."
    assert event.event_type == "evidence"
    assert event.metadata == {}


def test_trace_event_accepts_metadata():
    event = ReasoningTraceEvent(
        id="event-1",
        content="Observation: X.",
        event_type="observation",
        metadata={"source": "agent"},
    )

    assert event.metadata["source"] == "agent"


def test_trace_requires_event_objects():
    with pytest.raises(TypeError):
        ReasoningTrace(
            events=("not-an-event",)
        )


def test_trace_requires_tuple_events():
    with pytest.raises(TypeError):
        ReasoningTrace(
            events=[]
        )


def test_trace_preserves_event_order():
    first = ReasoningTraceEvent(
        id="event-1",
        content="First.",
        event_type="observation",
    )
    second = ReasoningTraceEvent(
        id="event-2",
        content="Second.",
        event_type="hypothesis",
    )

    trace = ReasoningTrace(events=(first, second))

    assert trace.events == (first, second)
    assert trace.event_ids() == ("event-1", "event-2")


def test_trace_can_find_event_by_id():
    first = ReasoningTraceEvent(
        id="event-1",
        content="First.",
        event_type="observation",
    )
    second = ReasoningTraceEvent(
        id="event-2",
        content="Second.",
        event_type="hypothesis",
    )

    trace = ReasoningTrace(events=(first, second))

    assert trace.get_event("event-2") is second


def test_trace_returns_none_for_unknown_event():
    event = ReasoningTraceEvent(
        id="event-1",
        content="First.",
        event_type="observation",
    )

    trace = ReasoningTrace(events=(event,))

    assert trace.get_event("missing") is None
