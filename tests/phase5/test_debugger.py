import pytest

from kernel.debug_finding import DebugFinding
from kernel.debugger import ReasoningDebugger
from kernel.reasoning_trace import ReasoningTrace, ReasoningTraceEvent


def make_trace(*events):
    return ReasoningTrace(events=tuple(events))


class FakeReasoningDetector:
    def __init__(self, findings=None):
        self.findings = findings or []
        self.calls = []

    def detect(self, trace):
        self.calls.append(trace)
        return list(self.findings)


class FakeStructuralDetector:
    def __init__(self, findings=None):
        self.findings = findings or []
        self.calls = []

    def detect(self, graph):
        self.calls.append(graph)
        return list(self.findings)


class FakePropagation:
    def __init__(self, result=()):
        self.result = result
        self.calls = []

    def analyze(self, graph, failure_node_id):
        self.calls.append((graph, failure_node_id))
        return self.result


def test_debugger_rejects_invalid_reasoning_detector():
    with pytest.raises(TypeError):
        ReasoningDebugger(reasoning_failure_detector=object())


def test_debugger_rejects_invalid_structural_detector():
    with pytest.raises(TypeError):
        ReasoningDebugger(structural_failure_detector=object())


def test_debugger_rejects_invalid_propagation_analyzer():
    with pytest.raises(TypeError):
        ReasoningDebugger(propagation_analyzer=object())


def test_debugger_runs_reasoning_detector():
    detector = FakeReasoningDetector()

    debugger = ReasoningDebugger(
        reasoning_failure_detector=detector,
        structural_failure_detector=FakeStructuralDetector(),
        propagation_analyzer=FakePropagation(),
    )

    trace = make_trace(
        ReasoningTraceEvent(
            id="event-1",
            content="Observation.",
            event_type="observation",
        )
    )

    debugger.debug(trace)

    assert detector.calls == [trace]


def test_debugger_runs_structural_detector_on_graph():
    detector = FakeStructuralDetector()

    debugger = ReasoningDebugger(
        reasoning_failure_detector=FakeReasoningDetector(),
        structural_failure_detector=detector,
        propagation_analyzer=FakePropagation(),
    )

    trace = make_trace(
        ReasoningTraceEvent(
            id="event-1",
            content="Observation.",
            event_type="observation",
        ),
        ReasoningTraceEvent(
            id="event-2",
            content="Hypothesis.",
            event_type="hypothesis",
        ),
    )

    debugger.debug(trace)

    assert len(detector.calls) == 1
    graph = detector.calls[0]

    assert [node.id for node in graph.nodes] == [
        "event-1",
        "event-2",
    ]


def test_debugger_propagates_structural_findings():
    finding = DebugFinding(
        event_id="event-2",
        failure_type="unsupported_hypothesis",
        explanation="No supporting edge.",
    )

    structural_detector = FakeStructuralDetector([finding])
    propagation = FakePropagation(("event-3", "event-4"))

    debugger = ReasoningDebugger(
        reasoning_failure_detector=FakeReasoningDetector(),
        structural_failure_detector=structural_detector,
        propagation_analyzer=propagation,
    )

    trace = make_trace(
        ReasoningTraceEvent(
            id="event-1",
            content="Observation.",
            event_type="observation",
        ),
        ReasoningTraceEvent(
            id="event-2",
            content="Hypothesis.",
            event_type="hypothesis",
        ),
    )

    result = debugger.debug(trace)

    assert len(result) == 1
    assert result[0].event_id == "event-2"
    assert result[0].failure_type == "unsupported_hypothesis"
    assert result[0].affected_event_ids == ("event-3", "event-4")

    graph, failure_node_id = propagation.calls[0]

    assert failure_node_id == "event-2"
    assert propagation.result == ("event-3", "event-4")


def test_debugger_combines_detector_results():
    first = DebugFinding(
        event_id="event-1",
        failure_type="unsupported_assumption",
        explanation="Unsupported assumption.",
    )

    second = DebugFinding(
        event_id="event-2",
        failure_type="unsupported_hypothesis",
        explanation="No support.",
    )

    debugger = ReasoningDebugger(
        reasoning_failure_detector=FakeReasoningDetector([first]),
        structural_failure_detector=FakeStructuralDetector([second]),
        propagation_analyzer=FakePropagation(),
    )

    trace = make_trace(
        ReasoningTraceEvent(
            id="event-1",
            content="Observation.",
            event_type="observation",
        ),
        ReasoningTraceEvent(
            id="event-2",
            content="Hypothesis.",
            event_type="hypothesis",
        ),
    )

    assert debugger.debug(trace) == [first, second]


def test_debugger_returns_empty_result_when_no_failures():
    debugger = ReasoningDebugger(
        reasoning_failure_detector=FakeReasoningDetector(),
        structural_failure_detector=FakeStructuralDetector(),
        propagation_analyzer=FakePropagation(),
    )

    trace = make_trace(
        ReasoningTraceEvent(
            id="event-1",
            content="Observation.",
            event_type="observation",
        )
    )

    assert debugger.debug(trace) == []

def test_debugger_does_not_modify_trace():
    trace = make_trace(
        ReasoningTraceEvent(
            id="event-1",
            content="Observation.",
            event_type="observation",
        ),
        ReasoningTraceEvent(
            id="event-2",
            content="Hypothesis.",
            event_type="hypothesis",
        ),
    )

    original_events = trace.events

    debugger = ReasoningDebugger(
        reasoning_failure_detector=FakeReasoningDetector(),
        structural_failure_detector=FakeStructuralDetector(),
        propagation_analyzer=FakePropagation(),
    )

    debugger.debug(trace)

    assert trace.events == original_events


def test_debugger_preserves_finding_order():
    first = DebugFinding(
        event_id="event-1",
        failure_type="failure_a",
        explanation="First.",
    )
    second = DebugFinding(
        event_id="event-2",
        failure_type="failure_b",
        explanation="Second.",
    )

    debugger = ReasoningDebugger(
        reasoning_failure_detector=FakeReasoningDetector([first, second]),
        structural_failure_detector=FakeStructuralDetector(),
        propagation_analyzer=FakePropagation(),
    )

    trace = make_trace(
        ReasoningTraceEvent(
            id="event-1",
            content="First.",
            event_type="observation",
        ),
        ReasoningTraceEvent(
            id="event-2",
            content="Second.",
            event_type="observation",
        ),
    )

    result = debugger.debug(trace)

    assert [finding.event_id for finding in result] == [
        "event-1",
        "event-2",
    ]


def test_debugger_preserves_metadata():
    finding = DebugFinding(
        event_id="event-1",
        failure_type="unsupported_assumption",
        explanation="Unsupported assumption.",
        metadata={"source": "reasoning_detector", "confidence": 0.9},
    )

    debugger = ReasoningDebugger(
        reasoning_failure_detector=FakeReasoningDetector([finding]),
        structural_failure_detector=FakeStructuralDetector(),
        propagation_analyzer=FakePropagation(),
    )

    trace = make_trace(
        ReasoningTraceEvent(
            id="event-1",
            content="Observation.",
            event_type="observation",
        )
    )

    result = debugger.debug(trace)

    assert result[0].metadata == {
        "source": "reasoning_detector",
        "confidence": 0.9,
    }


def test_debugger_rejects_non_debug_finding_from_reasoning_detector():
    debugger = ReasoningDebugger(
        reasoning_failure_detector=FakeReasoningDetector(
            ["not-a-debug-finding"]
        ),
        structural_failure_detector=FakeStructuralDetector(),
        propagation_analyzer=FakePropagation(),
    )

    trace = make_trace(
        ReasoningTraceEvent(
            id="event-1",
            content="Observation.",
            event_type="observation",
        )
    )

    with pytest.raises(TypeError):
        debugger.debug(trace)


def test_debugger_rejects_non_debug_finding_from_structural_detector():
    debugger = ReasoningDebugger(
        reasoning_failure_detector=FakeReasoningDetector(),
        structural_failure_detector=FakeStructuralDetector(
            ["not-a-debug-finding"]
        ),
        propagation_analyzer=FakePropagation(),
    )

    trace = make_trace(
        ReasoningTraceEvent(
            id="event-1",
            content="Observation.",
            event_type="observation",
        )
    )

    with pytest.raises(TypeError):
        debugger.debug(trace)


def test_debugger_rejects_invalid_propagation_result():
    finding = DebugFinding(
        event_id="event-1",
        failure_type="unsupported_assumption",
        explanation="Unsupported assumption.",
    )

    debugger = ReasoningDebugger(
        reasoning_failure_detector=FakeReasoningDetector([finding]),
        structural_failure_detector=FakeStructuralDetector(),
        propagation_analyzer=FakePropagation("event-2"),
    )

    trace = make_trace(
        ReasoningTraceEvent(
            id="event-1",
            content="Observation.",
            event_type="observation",
        )
    )

    with pytest.raises(TypeError):
        debugger.debug(trace)
