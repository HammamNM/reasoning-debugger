from kernel.graph import EdgeRelation, ReasoningGraph
from kernel.models import PrimitiveType, ReasoningUnit
from kernel.failure_propagation import FailurePropagationAnalyzer
from kernel.reasoning_failure_detector import UnsupportedAssumptionDetector
from kernel.reasoning_trace import ReasoningTrace, ReasoningTraceEvent

def test_propagation_ignores_sequence_and_follows_semantics():
    graph = ReasoningGraph()
    for i in range(1, 4):
        graph.add_node(ReasoningUnit(id=f"u{i}", primitive=PrimitiveType.INFERENCE, content=""))

    # Chronological sequence (should be ignored)
    graph.add_edge("u1", "u2", EdgeRelation.SEQUENCE)
    # Semantic dependency (should propagate)
    graph.add_edge("u1", "u3", EdgeRelation.SUPPORTS)

    affected = FailurePropagationAnalyzer().analyze(graph, "u1")
    assert "u2" not in affected, "Failure leaked across chronological SEQUENCE"
    assert "u3" in affected, "Failure failed to propagate across SUPPORTS"

def test_detector_isolates_first_root_failure_only():
    trace = ReasoningTrace(events=(
        ReasoningTraceEvent(id="e1", content="Good", event_type="OBSERVATION"),
        ReasoningTraceEvent(id="e2", content="assumption without support", event_type="INFERENCE"),
        ReasoningTraceEvent(id="e3", content="another assumption without support", event_type="INFERENCE"),
    ))

    findings = UnsupportedAssumptionDetector().detect(trace)
    assert len(findings) == 1, "Detector reported multiple failures instead of isolating the first"
    assert findings[0].event_id == "e2", "Detector identified the wrong root failure"
