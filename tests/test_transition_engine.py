import unittest

from kernel.events import create_event
from kernel.reasoning_state import ReasoningState
from kernel.transition_engine import TransitionEngine


class TestTransitionEngine(unittest.TestCase):

    def test_observation_event_creates_observation_transition(self):

        state = ReasoningState()

        event = create_event(
            "OBSERVATION",
            {
                "content": "Customer reports repeated failed payments"
            },
            source="AGENT_TRACE"
        )

        engine = TransitionEngine()

        engine.process_event(
            event,
            state
        )

        self.assertEqual(
            len(state.transitions.transitions),
            1
        )

        transition = state.transitions.transitions[0]

        self.assertEqual(
            transition.from_state,
            "START"
        )

        self.assertEqual(
            transition.to_state,
            "OBSERVATION"
        )

    def test_inference_event_creates_inference_transition(self):

        state = ReasoningState()

        event = create_event(
            "INFERENCE",
            {
                "content": "Customer may be attempting fraud"
            },
            source="AGENT_TRACE"
        )

        engine = TransitionEngine()

        engine.process_event(
            event,
            state
        )

        self.assertEqual(
            len(state.transitions.transitions),
            1
        )

        transition = state.transitions.transitions[0]

        self.assertEqual(
            transition.from_state,
            "START"
        )

        self.assertEqual(
            transition.to_state,
            "INFERENCE"
        )


if __name__ == "__main__":
    unittest.main()
