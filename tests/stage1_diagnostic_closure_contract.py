from kernel.api import ReasoningDebugger, ReasoningTrace, export_trace_to_dot
from kernel.reasoning_trace import ReasoningTraceEvent

def test_stage1_human_verifiable_export():
    # 1. Semantic Construction: Building the trace with explicit provenance markers.
    # We bypass the generic adapter here to explicitly inject the domain-semantic 
    # rule: "This specific inference requires support".
    events = (
        ReasoningTraceEvent(id="t0-action", event_type="INVESTIGATION", content="grep -r 'def process_data' ."),
        ReasoningTraceEvent(id="t1-thought", event_type="INFERENCE", content="The function must be in utils.py", 
                            metadata={"support_required": True}), # Explicit Semantic Marker
        ReasoningTraceEvent(id="t1-action", event_type="INVESTIGATION", content="edit utils.py"),
    )
    
    trace = ReasoningTrace(events=events)
    
    # 2. Debugging
    debugger = ReasoningDebugger()
    findings = debugger.debug(trace)
    
    # Invariant 1: The engine MUST catch the unsupported inference based on semantics, not sequence.
    assert len(findings) > 0, "Debugger failed to catch explicitly unsupported inference."
    
    # 3. DOT Export
    dot_output = export_trace_to_dot(trace, findings)
    
    # Invariant 2: The graphical export must highlight the exact semantic failure.
    assert "digraph ReasoningTrace" in dot_output
    assert "lightcoral" in dot_output, "Failing nodes must be highlighted"
    assert "t1-thought" in dot_output
