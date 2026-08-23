from kernel.events import ReasoningEvent


class OutcomeEngineAdapter:
    def __init__(
        self,
        outcome_engine,
        outcome_mapper,
    ):
        self.outcome_engine = outcome_engine
        self.outcome_mapper = outcome_mapper

    def process_event(self, event, session):
        if event.event_type != "ACTION":
            return None

        action = event.payload.get("action")

        # Investigation and information-gathering actions
        # must not generate outcome events directly.
        if action and action.startswith("ORDER_"):
            return None

        if action and action.startswith("ASK_"):
            return None

        # Only explicitly mapped actions can produce outcomes.
        outcome_event_type = self.outcome_mapper.map_action(action)

        if not outcome_event_type:
            return None

        self.outcome_engine.process_event(
            ReasoningEvent(
                event_type=outcome_event_type,
                payload={
                    "action": action,
                },
                source="OUTCOME_ADAPTER",
            ),
            session.outcome,
        )

        return ReasoningEvent(
            event_type="OUTCOME_UPDATED",
            payload={
                "action": action,
                "outcome": session.outcome,
            },
            source="OUTCOME_ADAPTER",
        )
