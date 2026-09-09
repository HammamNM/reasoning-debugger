import pytest
from kernel.api import ReasoningDebugger, ReasoningTrace, InvalidTraceSchemaError
from kernel.reasoning_trace import ReasoningTraceEvent
from kernel.adapters.swe_agent_adapter import SWEAgentAdapter

def test_golden_trace_yields_zero_findings():
    """Real successful traces must not generate false positives."""
    trace_path = 'benchmarks/samples/public_real_trace/swe_agent_marshmallow.traj'
    trace = SWEAgentAdapter.parse_trajectory(trace_path)
    debugger = ReasoningDebugger()
    findings = debugger.debug(trace)
    
    assert len(findings) == 0, f"Golden trace produced unexpected findings: {findings}"

def test_positive_control_detects_semantic_failure():
    """Synthetic trace with explicit required support must be caught."""
    events = (
        ReasoningTraceEvent(id="e1", event_type="INVESTIGATION", content="query db"),
        ReasoningTraceEvent(id="e2", event_type="INFERENCE", content="user exists", metadata={"support_required": True}),
    )
    trace = ReasoningTrace(events=events)
    debugger = ReasoningDebugger()
    findings = debugger.debug(trace)
    
    assert len(findings) == 1
    assert findings[0].failure_type == "unsupported_inference"
    assert findings[0].event_id == "e2"

def test_debugger_rejects_invalid_schema():
    """Engine must gracefully reject raw dicts or invalid objects, enforcing strict SDK boundaries."""
    debugger = ReasoningDebugger()
    malformed_trace = {"events": [{"id": "1", "type": "INFERENCE"}]}
    
    with pytest.raises(InvalidTraceSchemaError):
        debugger.debug(malformed_trace)
