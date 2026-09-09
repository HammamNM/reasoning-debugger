from kernel.reasoning_trace import ReasoningTrace, ReasoningTraceEvent

def load_data_agent_failure_trace() -> ReasoningTrace:
    """
    Represents a data analysis agent that makes a critical unverified assumption
    about missing data, corrupting the final dataset.
    """
    return ReasoningTrace(events=(
        ReasoningTraceEvent(
            id="obs-data-1",
            content="Loaded sales.csv. 500 rows have missing 'revenue' fields.",
            event_type="OBSERVATION"
        ),
        ReasoningTraceEvent(
            id="inf-assumption-2",
            content="assumption without support: Missing revenue means the transaction was cancelled.",
            event_type="INFERENCE"
        ),
        ReasoningTraceEvent(
            id="dec-drop-1",
            content="Decision: Drop all 500 rows from the training dataset.",
            event_type="DECISION_ASSESSMENT",
            metadata={"derived_from": ["inf-assumption-2"]}
        ),
        ReasoningTraceEvent(
            id="out-report-1",
            content="Outcome: Dataset cleaned. Final row count reduced.",
            event_type="OUTCOME_UPDATED",
            metadata={"derived_from": ["dec-drop-1"]}
        )
    ))
