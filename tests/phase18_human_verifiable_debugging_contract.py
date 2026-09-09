from kernel.debugger import ReasoningDebugger
from kernel.reasoning_trace import ReasoningTrace, ReasoningTraceEvent

def test_debug_finding_is_strictly_human_verifiable():
    # 1. Setup Trace
    trace = ReasoningTrace(events=(
        ReasoningTraceEvent(id="e1", content="Observation: User is logged in.", event_type="OBSERVATION"),
        ReasoningTraceEvent(id="e2", content="assumption without support: user is admin.", event_type="INFERENCE"),
        ReasoningTraceEvent(id="e3", content="Decision: grant access.", event_type="DECISION_ASSESSMENT", metadata={"derived_from": ["e2"]})
    ))

    debugger = ReasoningDebugger()
    findings = debugger.debug(trace)
    finding = findings[0]

    # 2. Verification Step: Can a human reviewer trace it back?
    root_event = trace.get_event(finding.first_failure_event_id)
    assert root_event is not None
    assert root_event.content == "assumption without support: user is admin."

    # 3. Verify Downstream Impact Mapping
    affected_events = [trace.get_event(eid) for eid in finding.downstream_event_ids]
    assert len(affected_events) == 1
    assert affected_events[0].content == "Decision: grant access."

    # 4. Generate Human Report solely from structural evidence
    report = f"Failure: '{root_event.content}' led to invalid downstream action: '{affected_events[0].content}'"
    assert "user is admin" in report
    assert "grant access" in report
