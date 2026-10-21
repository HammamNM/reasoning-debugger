import pytest

from kernel.debug_finding import DebugFinding
from kernel.debugger import ReasoningDebugger
from kernel.reasoning_trace import ReasoningTrace, ReasoningTraceEvent


def make_trace(*events):
    return ReasoningTrace(events=tuple(events))


def test_debugger_accepts_real_kernel_event_flow():
    trace = make_trace(
        ReasoningTraceEvent(
            "event-1",
            "Patient observation.",
            "OBSERVATION",
        ),
        ReasoningTraceEvent(
            "event-2",
            "Supporting evidence.",
            "EVIDENCE",
        ),
        ReasoningTraceEvent(
            "event-3",
            "Reasoning inference.",
            "INFERENCE",
        ),
        ReasoningTraceEvent(
            "event-4",
            "Investigation completed.",
            "INVESTIGATION_RESULT",
        ),
        ReasoningTraceEvent(
            "event-5",
            "Decision assessed.",
            "DECISION_ASSESSMENT",
        ),
        ReasoningTraceEvent(
            "event-6",
            "Outcome updated.",
            "OUTCOME_UPDATED",
        ),
    )

    result = ReasoningDebugger().debug(trace)

    assert result == []


def test_debugger_preserves_real_kernel_event_ids_through_graph():
    trace = make_trace(
        ReasoningTraceEvent(
            "obs-1",
            "Observation.",
            "OBSERVATION",
        ),
        ReasoningTraceEvent(
            "evidence-1",
            "Evidence.",
            "EVIDENCE",
        ),
        ReasoningTraceEvent(
            "inference-1",
            "Inference.",
            "INFERENCE",
        ),
        ReasoningTraceEvent(
            "investigation-1",
            "Investigation result.",
            "INVESTIGATION_RESULT",
        ),
        ReasoningTraceEvent(
            "decision-1",
            "Decision assessment.",
            "DECISION_ASSESSMENT",
        ),
        ReasoningTraceEvent(
            "outcome-1",
            "Outcome updated.",
            "OUTCOME_UPDATED",
        ),
    )

    debugger = ReasoningDebugger()

    captured = {}
    original_build = debugger.trace_graph_adapter.build

    def capture_build(input_trace):
        graph = original_build(input_trace)
        captured["graph"] = graph
        return graph

    debugger.trace_graph_adapter.build = capture_build

    debugger.debug(trace)

    graph = captured["graph"]

    assert [node.id for node in graph.nodes] == [
        "obs-1",
        "evidence-1",
        "inference-1",
        "investigation-1",
        "decision-1",
        "outcome-1",
    ]

    assert [
        (edge.source, edge.target)
        for edge in graph.edges
    ] == [
        ("obs-1", "evidence-1"),
        ("evidence-1", "inference-1"),
        ("inference-1", "investigation-1"),
        ("investigation-1", "decision-1"),
        ("decision-1", "outcome-1"),
    ]


def test_debugger_propagates_real_kernel_graph_failure():
    from kernel.graph import EdgeRelation
    from kernel.models import PrimitiveType, ReasoningUnit

    class StructuralDetector:
        def detect(self, graph):
            finding = DebugFinding(
                event_id="inference-1",
                failure_type="test_structural_failure",
                explanation="Synthetic structural failure.",
            )

            return [finding]

    debugger = ReasoningDebugger(
        reasoning_failure_detector=type(
            "EmptyReasoningDetector",
            (),
            {"detect": lambda self, trace: []},
        )(),
        structural_failure_detector=StructuralDetector(),
    )

    trace = make_trace(
        ReasoningTraceEvent(
            "obs-1",
            "Observation.",
            "OBSERVATION",
        ),
        ReasoningTraceEvent(
            "inference-1",
            "Inference.",
            "INFERENCE",
        ),
        ReasoningTraceEvent(
            "decision-1",
            "Decision.",
            "DECISION_ASSESSMENT",
        ),
        ReasoningTraceEvent(
            "outcome-1",
            "Outcome.",
            "OUTCOME_UPDATED",
        ),
    )

    original_analyze = debugger.propagation_analyzer.analyze

    captured = {}

    def capture_analyze(graph, failure_node_id):
        captured["graph"] = graph
        captured["failure_node_id"] = failure_node_id
        return original_analyze(graph, failure_node_id)

    debugger.propagation_analyzer.analyze = capture_analyze

    result = debugger.debug(trace)

    assert len(result) == 1
    assert result[0].event_id == "inference-1"
    assert captured["failure_node_id"] == "inference-1"
    assert result[0].affected_event_ids == ()


def test_debugger_accepts_unknown_kernel_event_as_generic_event():
    trace = make_trace(
        ReasoningTraceEvent(
            "event-1",
            "Unknown event.",
            "SOMETHING_UNKNOWN",
        )
    )

    result = ReasoningDebugger().debug(trace)
    assert result == []
