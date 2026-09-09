from kernel.reasoning_trace import ReasoningTrace, ReasoningTraceEvent

def load_coding_agent_failure_trace() -> ReasoningTrace:
    """
    Represents a coding-agent trace where an external library capability is assumed without verification.
    """
    return ReasoningTrace(events=(
        ReasoningTraceEvent(
            id="obs-code-1",
            content="Read file main.py, identified index out of bounds error.",
            event_type="OBSERVATION"
        ),
        ReasoningTraceEvent(
            id="inf-assumption-1",
            content="assumption without support: the standard library 'utils' module has a safe_get helper.",
            event_type="INFERENCE"
        ),
        ReasoningTraceEvent(
            id="inv-search-1",
            content="Searched local workspace files for 'utils'.",
            event_type="INVESTIGATION",
            metadata={"derived_from": ["inf-assumption-1"]}
        ),
        ReasoningTraceEvent(
            id="dec-fix-1",
            content="Decision: Patch main.py to import utils.safe_get.",
            event_type="DECISION_ASSESSMENT",
            metadata={"derived_from": ["inf-assumption-1"]}
        )
    ))
