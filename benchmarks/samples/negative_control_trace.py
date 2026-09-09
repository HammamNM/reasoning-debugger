from kernel.reasoning_trace import ReasoningTrace, ReasoningTraceEvent

def load_negative_control_trace() -> ReasoningTrace:
    """A perfectly valid trace. No unsupported assumptions."""
    return ReasoningTrace(events=(
        ReasoningTraceEvent(id="obs-1", content="Memory usage at 95%.", event_type="OBSERVATION"),
        ReasoningTraceEvent(id="ev-1", content="Evidence: Logs show memory leak in module X.", event_type="EVIDENCE"),
        ReasoningTraceEvent(id="inf-1", content="Memory leak is causing high usage.", event_type="INFERENCE", metadata={"derived_from": ["obs-1", "ev-1"]}),
        ReasoningTraceEvent(id="dec-1", content="Decision: Restart module X.", event_type="DECISION_ASSESSMENT", metadata={"derived_from": ["inf-1"]})
    ))
