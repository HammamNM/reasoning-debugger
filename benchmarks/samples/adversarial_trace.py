from kernel.reasoning_trace import ReasoningTrace, ReasoningTraceEvent

def load_adversarial_trace() -> ReasoningTrace:
    """
    An adversarial trace. The agent makes a bad assumption, but
    does NOT use it for the final decision.
    Tests strict dependency propagation.
    """
    return ReasoningTrace(events=(
        ReasoningTraceEvent(id="obs-1", content="User login failed.", event_type="OBSERVATION"),
        ReasoningTraceEvent(id="inf-bad", content="assumption without support: User is a hacker.", event_type="INFERENCE"),
        ReasoningTraceEvent(id="ev-1", content="Evidence: Password expired in DB.", event_type="EVIDENCE"),
        ReasoningTraceEvent(id="dec-1", content="Decision: Prompt password reset.", event_type="DECISION_ASSESSMENT", metadata={"derived_from": ["ev-1"]})
    ))
