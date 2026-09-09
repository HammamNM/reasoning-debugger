import pytest

from kernel.debug_finding import DebugFinding
from kernel.reasoning_failure_detector import UnsupportedAssumptionDetector
from kernel.reasoning_trace import ReasoningTrace, ReasoningTraceEvent


def make_event(event_id, content, event_type):
    return ReasoningTraceEvent(
        id=event_id,
        content=content,
        event_type=event_type,
    )


def test_detector_returns_empty_for_clean_trace():
    trace = ReasoningTrace(
        events=(
            make_event("event-1", "Evidence E1.", "evidence"),
            make_event("event-2", "Hypothesis H1.", "hypothesis"),
            make_event("event-3", "Decision D1.", "decision"),
        )
    )

    detector = UnsupportedAssumptionDetector()

    assert detector.detect(trace) == []


def test_detector_detects_unsupported_assumption():
    trace = ReasoningTrace(
        events=(
            make_event("event-1", "Evidence E1.", "evidence"),
            make_event(
                "event-2",
                "Assumption A1 is introduced without support.",
                "unsupported_assumption",
            ),
            make_event("event-3", "Decision D1.", "decision"),
        )
    )

    detector = UnsupportedAssumptionDetector()

    findings = detector.detect(trace)

    assert len(findings) == 1
    assert isinstance(findings[0], DebugFinding)
    assert findings[0].event_id == "event-2"
    assert findings[0].failure_type == "unsupported_assumption"
    assert (
        findings[0].explanation
        == "Assumption A1 is introduced without support."
    )


def test_detector_preserves_multiple_failures_in_trace_order():
    trace = ReasoningTrace(
        events=(
            make_event(
                "event-1",
                "First unsupported assumption.",
                "unsupported_assumption",
            ),
            make_event("event-2", "Observation.", "observation"),
            make_event(
                "event-3",
                "Second unsupported assumption.",
                "unsupported_assumption",
            ),
        )
    )

    detector = UnsupportedAssumptionDetector()

    findings = detector.detect(trace)

    assert [finding.event_id for finding in findings] == ["event-1"]


def test_detector_does_not_modify_trace():
    event = make_event(
        "event-1",
        "Unsupported assumption.",
        "unsupported_assumption",
    )
    trace = ReasoningTrace(events=(event,))

    original_events = trace.events

    UnsupportedAssumptionDetector().detect(trace)

    assert trace.events == original_events
    assert trace.events[0] is event


def test_detector_rejects_invalid_trace():
    with pytest.raises(TypeError):
        UnsupportedAssumptionDetector().detect(object())


def test_detector_does_not_treat_other_event_types_as_failures():
    trace = ReasoningTrace(
        events=(
            make_event(
                "event-1",
                "Hypothesis under consideration.",
                "hypothesis",
            ),
            make_event(
                "event-2",
                "Normal assumption with explicit support.",
                "assumption",
            ),
        )
    )

    assert UnsupportedAssumptionDetector().detect(trace) == []
