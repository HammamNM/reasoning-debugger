import pytest
from kernel.api import ReasoningDebugger, ReasoningTrace, InvalidTraceSchemaError
from kernel.reasoning_trace import ReasoningTraceEvent
from kernel.adapters.swe_agent_adapter import SWEAgentAdapter

def test_engine_determinism():
    """Execution must be strictly deterministic: Same trace MUST yield exact same findings."""
    trace_path = 'benchmarks/samples/public_real_trace/swe_agent_broken_hallucination.traj'
    trace = SWEAgentAdapter.parse_trajectory(trace_path)
    debugger = ReasoningDebugger()
    
    first_run = debugger.debug(trace)
    for _ in range(5):
        subsequent_run = debugger.debug(trace)
        assert first_run == subsequent_run, "Determinism violated: Findings changed across runs."

def test_massive_trace_resilience():
    """Engine must handle large traces (e.g., 5000 events) without recursion limits or crashes."""
    events = []
    for i in range(5000):
        events.append(ReasoningTraceEvent(id=f"e{i}", event_type="INVESTIGATION", content="load"))
    
    trace = ReasoningTrace(events=tuple(events))
    debugger = ReasoningDebugger()
    findings = debugger.debug(trace)
    assert isinstance(findings, list), "Failed to process massive trace."

def test_empty_trace_graceful_handling():
    """Empty traces should return 0 findings cleanly, not crash."""
    trace = ReasoningTrace(events=())
    debugger = ReasoningDebugger()
    findings = debugger.debug(trace)
    assert len(findings) == 0

def test_schema_enforcement_at_boundary():
    """Engine must enforce schema strictly at the boundary."""
    debugger = ReasoningDebugger()
    with pytest.raises(InvalidTraceSchemaError):
        debugger.debug({"events": [{"id": "1", "event_type": "INFERENCE"}]})
