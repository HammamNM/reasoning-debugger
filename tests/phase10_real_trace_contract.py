from kernel.api import DebugFinding, ReasoningDebugger
from kernel.reasoning_trace import ReasoningTrace, ReasoningTraceEvent


def test_realistic_unsupported_assumption_trace():
    trace = ReasoningTrace(
        events=(
            ReasoningTraceEvent(
                id="e1",
                content="The patient has chest pain.",
                event_type="OBSERVATION",
            ),
            ReasoningTraceEvent(
                id="e2",
                content="Troponin is normal.",
                event_type="EVIDENCE",
            ),
            ReasoningTraceEvent(
                id="e3",
                content="The conclusion assumes that a normal troponin excludes ACS.",
                event_type="unsupported_assumption",
            ),
            ReasoningTraceEvent(
                id="e4",
                content="Therefore discharge the patient.",
                event_type="DECISION",
            ),
        )
    )

    findings = ReasoningDebugger().debug(trace)

    assert isinstance(findings, list)
    assert all(isinstance(item, DebugFinding) for item in findings)

    assert findings

    first = findings[0]

    assert first.event_id == "e3"
    assert first.failure_type == "unsupported_assumption"
    assert first.explanation == (
        "The conclusion assumes that a normal troponin excludes ACS."
    )


def test_failure_propagates_to_downstream_decision():
    trace = ReasoningTrace(
        events=(
            ReasoningTraceEvent(
                id="e1",
                content="Observation.",
                event_type="OBSERVATION",
            ),
            ReasoningTraceEvent(
                id="e2",
                content="Unsupported assumption introduced.",
                event_type="unsupported_assumption",
            ),
            ReasoningTraceEvent(
                id="e3",
                content="Inference based on the assumption.",
                event_type="INFERENCE",
            ),
            ReasoningTraceEvent(
                id="e4",
                content="Decision based on the inference.",
                event_type="DECISION_ASSESSMENT",
            ),
        )
    )

    findings = ReasoningDebugger().debug(trace)

    assert len(findings) == 1

    finding = findings[0]

    assert finding.event_id == "e2"
    assert finding.failure_type == "unsupported_assumption"

    assert finding.affected_event_ids == ("e3", "e4")
