from kernel.api import DebugFinding, ReasoningDebugger
from kernel.reasoning_trace import ReasoningTrace, ReasoningTraceEvent


def event(event_id, content, event_type):
    return ReasoningTraceEvent(
        id=event_id,
        content=content,
        event_type=event_type,
    )


def test_debugger_finds_unsupported_assumption_without_domain_knowledge():
    trace = ReasoningTrace(
        events=(
            event("e1", "Observation.", "OBSERVATION"),
            event("e2", "Unsupported assumption.", "unsupported_assumption"),
            event("e3", "Inference.", "INFERENCE"),
        )
    )

    findings = ReasoningDebugger().debug(trace)

    assert len(findings) == 1
    assert isinstance(findings[0], DebugFinding)
    assert findings[0].event_id == "e2"
    assert findings[0].failure_type == "unsupported_assumption"


def test_debugger_propagates_failure_through_sequence():
    trace = ReasoningTrace(
        events=(
            event("e1", "Observation.", "OBSERVATION"),
            event("e2", "Failure.", "unsupported_assumption"),
            event("e3", "Inference.", "INFERENCE"),
            event("e4", "Decision.", "DECISION_ASSESSMENT"),
            event("e5", "Outcome.", "OUTCOME_UPDATED"),
        )
    )

    findings = ReasoningDebugger().debug(trace)

    assert len(findings) == 1
    assert findings[0].affected_event_ids == ("e3", "e4", "e5")


def test_debugger_preserves_trace_immutability():
    trace = ReasoningTrace(
        events=(
            event("e1", "Observation.", "OBSERVATION"),
            event("e2", "Failure.", "unsupported_assumption"),
            event("e3", "Decision.", "DECISION_ASSESSMENT"),
        )
    )

    original = trace.events

    ReasoningDebugger().debug(trace)

    assert trace.events == original
    assert trace.events[1].id == "e2"


def test_debugger_preserves_multiple_failure_order():
    trace = ReasoningTrace(
        events=(
            event("e1", "First failure.", "unsupported_assumption"),
            event("e2", "Inference.", "INFERENCE"),
            event("e3", "Second failure.", "unsupported_assumption"),
            event("e4", "Decision.", "DECISION_ASSESSMENT"),
        )
    )

    findings = ReasoningDebugger().debug(trace)

    assert [f.event_id for f in findings] == ["e1", "e3"]


def test_debugger_returns_no_findings_for_clean_trace():
    trace = ReasoningTrace(
        events=(
            event("e1", "Observation.", "OBSERVATION"),
            event("e2", "Evidence.", "EVIDENCE"),
            event("e3", "Inference.", "INFERENCE"),
            event("e4", "Decision.", "DECISION_ASSESSMENT"),
        )
    )

    assert ReasoningDebugger().debug(trace) == []



def test_debugger_finds_unsupported_inference():
    trace = ReasoningTrace(
        events=(
            event("e1", "Observation.", "OBSERVATION"),
            event("e2", "Inference without support.", "INFERENCE"),
            event("e3", "Decision.", "DECISION_ASSESSMENT"),
        )
    )

    findings = ReasoningDebugger().debug(trace)

    assert len(findings) == 1
    assert findings[0].event_id == "e2"
    assert findings[0].failure_type == "unsupported_inference"
    assert findings[0].affected_event_ids == ("e3",)


def test_supported_inference_is_not_detected():
    trace = ReasoningTrace(
        events=(
            event("e1", "Evidence.", "EVIDENCE"),
            event("e2", "Inference.", "INFERENCE"),
            event("e3", "Decision.", "DECISION_ASSESSMENT"),
        )
    )

    # The current trace adapter builds SEQUENCE edges only.
    # This contract therefore verifies that the structural detector
    # itself distinguishes an explicitly supported inference.
    from kernel.graph import EdgeRelation, ReasoningGraph
    from kernel.models import PrimitiveType, ReasoningUnit
    from kernel.structural_failure_detector import StructuralFailureDetector

    graph = ReasoningGraph()
    evidence = ReasoningUnit("e1", PrimitiveType.EVIDENCE, "Evidence.")
    inference = ReasoningUnit("e2", PrimitiveType.INFERENCE, "Inference.")

    graph.add_node(evidence)
    graph.add_node(inference)
    graph.add_edge("e1", "e2", EdgeRelation.SUPPORTS)

    assert StructuralFailureDetector().detect(graph) == []
