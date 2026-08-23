from kernel.reasoning_transition import (
    TransitionRecorder
)


class TransitionEngine:

    def __init__(self):
        self.recorders = {}

    def process_event(
        self,
        event,
        state_or_session
    ):

        reasoning_state = self._resolve_reasoning_state(
            state_or_session
        )

        if reasoning_state is None:
            return None

        to_state = self.detect_state(
            event
        )

        if to_state is None:
            return None

        from_state = self.get_previous_state(
            reasoning_state
        )

        reasoning_state.transitions.record(
            from_state,
            to_state,
            event.event_type
        )

        return None

    # -------------------------------------------------
    # Resolve the reasoning state
    # -------------------------------------------------

    def _resolve_reasoning_state(
        self,
        state_or_session
    ):

        # Direct ReasoningState usage.
        if hasattr(
            state_or_session,
            "transitions"
        ):

            return state_or_session

        # KernelSession usage.
        reasoning_state = getattr(
            state_or_session,
            "reasoning_state",
            None
        )

        if reasoning_state is None:
            return None

        if not hasattr(
            reasoning_state,
            "transitions"
        ):

            return None

        return reasoning_state

    # -------------------------------------------------
    # Detect reasoning state represented by an event
    # -------------------------------------------------

    def detect_state(
        self,
        event
    ):

        event_type = getattr(
            event,
            "event_type",
            None
        )

        generic_states = {

            "OBSERVATION":
                "OBSERVATION",

            "EVIDENCE":
                "EVIDENCE",

            "INVESTIGATION":
                "INVESTIGATION",

            "INVESTIGATION_RESULT":
                "EVIDENCE",

            "INFERENCE":
                "INFERENCE",

            "HYPOTHESIS":
                "HYPOTHESIS",

            "HYPOTHESIS_UPDATE":
                "HYPOTHESIS_UPDATE",

            "DECISION":
                "DECISION",

            "DECISION_ASSESSMENT":
                "DECISION",

            "OUTCOME":
                "OUTCOME",

            "OUTCOME_UPDATED":
                "OUTCOME"

        }

        return generic_states.get(
            event_type
        )

    # -------------------------------------------------
    # Determine the previous reasoning state
    # -------------------------------------------------

    def get_previous_state(
        self,
        reasoning_state
    ):

        transitions = (
            reasoning_state
            .transitions
            .transitions
        )

        if not transitions:
            return "START"

        return transitions[-1].to_state
