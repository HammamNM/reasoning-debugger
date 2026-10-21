from kernel.events import ReasoningEvent


class InvestigationEngine:

    def process_event(
        self,
        event,
        session
    ):

        if event.event_type != "ACTION":
            return None

        action = event.payload.get(
            "action"
        )

        if not action:
            return None

        scenario = getattr(
            session,
            "scenario",
            None
        )

        if scenario is None:
            return None

        investigations = getattr(
            scenario,
            "investigations",
            {}
        )

        investigation_id = (
            self.get_investigation_id(
                action,
                scenario
            )
        )

        if investigation_id is None:
            return None

        investigation = investigations.get(
            investigation_id
        )

        if investigation is None:
            return None

        return ReasoningEvent(
            event_type="INVESTIGATION_RESULT",

            payload={
                "action": action,

                "investigation_id":
                    investigation_id,

                "result":
                    investigation
            },

            source="INVESTIGATION_ENGINE"
        )


    def get_investigation_id(
        self,
        action,
        scenario
    ):

        metadata = getattr(
            scenario,
            "metadata",
            {}
        )

        action_config = (
            metadata
            .get(
                "actions",
                {}
            )
            .get(
                action
            )
        )

        if action_config is not None:

            investigation_id = (
                action_config.get(
                    "investigation_id"
                )
            )

            if investigation_id:
                return investigation_id

        # -------------------------------------------------
        # Fallback:
        # If the action itself is the investigation key.
        # Example: ORDER_ECG -> investigations["ORDER_ECG"]
        # -------------------------------------------------

        investigations = getattr(
            scenario,
            "investigations",
            {}
        )

        if action in investigations:
            return action

        return None
