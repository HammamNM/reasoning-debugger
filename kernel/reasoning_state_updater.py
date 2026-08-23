from kernel.hypothesis_manager import HypothesisManager


class ReasoningStateUpdater:

    def __init__(self):
        self.hypothesis_manager = HypothesisManager()

    def update(self, reasoning_state, event):

        event_type = getattr(
            event,
            "event_type",
            ""
        )

        payload = getattr(
            event,
            "payload",
            {}
        )

        if not isinstance(payload, dict):
            return

        if event_type not in (
            "ACTION",
            "STUDENT_ACTION",
        ):
            return

        action = payload.get("action")

        if not isinstance(action, str):
            return

        # -------------------------------------------------
        # Information gathering
        # -------------------------------------------------

        if action.startswith("ASK_"):

            if action not in reasoning_state.collected_information:
                reasoning_state.collected_information.append(action)

            reasoning_state.transitions.record(
                from_state="INITIAL",
                to_state="INFORMATION_GATHERING",
                trigger=action,
            )

            return

        # -------------------------------------------------
        # Investigation ordering
        # -------------------------------------------------

        if action.startswith("ORDER_"):

            if action not in reasoning_state.ordered_investigations:
                reasoning_state.ordered_investigations.append(action)

            return

        # -------------------------------------------------
        # Hypothesis formation
        # -------------------------------------------------

        if action.startswith("DIAGNOSIS_"):

            reasoning_state.transitions.record(
                from_state="INFORMATION_GATHERING",
                to_state="HYPOTHESIS_FORMATION",
                trigger=action,
            )

            hypothesis = self.hypothesis_manager.find(
                reasoning_state,
                action,
            )

            if hypothesis is None:
                self.hypothesis_manager.create(
                    reasoning_state,
                    action,
                    trigger=action,
                )

            return

        # -------------------------------------------------
        # Hypothesis confirmation
        # -------------------------------------------------

        if action.startswith("CONFIRM_"):

            hypothesis_name = action.replace(
                "CONFIRM_",
                "DIAGNOSIS_",
                1,
            )

            hypothesis = self.hypothesis_manager.find(
                reasoning_state,
                hypothesis_name,
            )

            if hypothesis is None:
                return

            confirmed = self.hypothesis_manager.confirm(
                hypothesis
            )

            if confirmed:
                if hypothesis not in reasoning_state.confirmed_hypotheses:
                    reasoning_state.confirmed_hypotheses.append(
                        hypothesis
                    )

            return

        # -------------------------------------------------
        # Hypothesis rejection
        # -------------------------------------------------

        if action.startswith("REJECT_"):

            hypothesis_name = action.replace(
                "REJECT_",
                "DIAGNOSIS_",
                1,
            )

            hypothesis = self.hypothesis_manager.find(
                reasoning_state,
                hypothesis_name,
            )

            if hypothesis is None:
                return

            self.hypothesis_manager.reject(
                reasoning_state,
                hypothesis,
            )

            return

        # -------------------------------------------------
        # Treatment / decision action
        # -------------------------------------------------

        if action.startswith("TREAT_"):

            if action not in reasoning_state.performed_treatments:
                reasoning_state.performed_treatments.append(action)

            return
