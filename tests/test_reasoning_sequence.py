import unittest

from backend.session import ClinicalSession
from kernel.bootstrap import KernelBootstrap
from kernel.events import ReasoningEvent


class TestReasoningSequence(unittest.TestCase):

    def create_runtime(self):

        session = ClinicalSession(
            student_id="student_001",
            scenario_id="TEST_SEQUENCE"
        )

        return KernelBootstrap().create_runtime(
            session
        )

    def action(
        self,
        runtime,
        action
    ):

        runtime.publish(
            ReasoningEvent(
                event_type="ACTION",
                payload={
                    "action": action
                },
                source="STUDENT"
            )
        )

        runtime.run_cycle()

    def test_complete_reasoning_sequence(self):

        runtime = self.create_runtime()

        self.action(
            runtime,
            "ASK_CHEST_PAIN"
        )

        self.action(
            runtime,
            "ORDER_ECG"
        )

        self.action(
            runtime,
            "DIAGNOSIS_NSTEMI"
        )

        self.assertIn(
            "ASK_CHEST_PAIN",
            runtime.session.reasoning_state
            .collected_information
        )

        self.assertIn(
            "ORDER_ECG",
            runtime.session.reasoning_state
            .ordered_investigations
        )

        self.assertEqual(
            len(
                runtime.session.reasoning_state
                .active_hypotheses
            ),
            1
        )

        self.action(
            runtime,
            "CONFIRM_NSTEMI"
        )

        state = runtime.session.reasoning_state

        self.assertEqual(
            len(state.active_hypotheses),
            1
        )

        self.assertEqual(
            len(state.confirmed_hypotheses),
            1
        )

        self.assertEqual(
            state.confirmed_hypotheses[0].status,
            "CONFIRMED"
        )

        self.action(
            runtime,
            "TREAT_ASPIRIN"
        )

        self.assertIn(
            "TREAT_ASPIRIN",
            state.performed_treatments
        )


if __name__ == "__main__":
    unittest.main()
