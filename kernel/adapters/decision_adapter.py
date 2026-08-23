from kernel.events import ReasoningEvent


class DecisionEngineAdapter:
    def __init__(self, decision_engine):
        self.decision_engine = decision_engine

    def process_event(self, event, session):
        if event.event_type != "ACTION":
            return None

        action = event.payload.get("action", "")

        # Information-gathering actions are not decisions.
        if action.startswith("ASK_"):
            return None

        # Investigations are handled by the Scenario/Evidence flow.
        if action.startswith("ORDER_"):
            return None

        # Diagnosis creates a hypothesis in the reasoning graph.
        # It must not be converted into a Decision Assessment.
        if action.startswith("DIAGNOSIS_"):
            return None

        profile = self.decision_engine.evaluate_decision(
            session,
            action,
        )

        session.decision_history.append(profile)

        return ReasoningEvent(
            event_type="DECISION_ASSESSMENT",
            payload={
                "action": action,
                "profile": profile,
            },
            source="DECISION_ADAPTER",
        )
