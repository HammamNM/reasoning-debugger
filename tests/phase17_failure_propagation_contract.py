from kernel.debugger import ReasoningDebugger
from kernel.reasoning_trace import ReasoningTrace, ReasoningTraceEvent

def test_debugger_propagates_failure_via_semantic_metadata():
    debugger = ReasoningDebugger()

    trace = ReasoningTrace(events=(
        ReasoningTraceEvent(
            id="obs-1", content="Observation", event_type="OBSERVATION"
        ),
        ReasoningTraceEvent(
            id="fail-1", content="assumption without support", event_type="INFERENCE"
        ),
        ReasoningTraceEvent(
            id="safe-1", content="Unrelated independent decision", event_type="DECISION_ASSESSMENT"
        ),
        ReasoningTraceEvent(
            id="downstream-1",
            content="Decision based on assumption",
            event_type="DECISION_ASSESSMENT",
            metadata={"derived_from": ["fail-1"]}
        ),
    ))

    findings = debugger.debug(trace)

    assert len(findings) == 1, "Expected exactly one root finding"
    finding = findings[0]

    assert finding.event_id == "fail-1", "Root failure localized incorrectly"
    assert "downstream-1" in finding.affected_event_ids, "Failed to propagate to semantically dependent event"
    assert "safe-1" not in finding.affected_event_ids, "Propagated to chronologically subsequent but semantically independent event"
