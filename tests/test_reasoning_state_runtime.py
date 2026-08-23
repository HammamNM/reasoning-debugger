import unittest

from kernel.bootstrap import KernelBootstrap
from backend.session import ClinicalSession


class TestReasoningStateRuntime(unittest.TestCase):

    def create_runtime(self):

        clinical_session = ClinicalSession(
            student_id="student_001",
            scenario_id="TEST_001"
        )

        return KernelBootstrap().create_runtime(
            clinical_session
        )

    def publish_action(
        self,
        runtime,
        action
    ):

        from kernel.events import ReasoningEvent

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

    def test_order_updates_reasoning_state(self):

        runtime = self.create_runtime()

        self.publish_action(
            runtime,
            "ORDER_ECG"
        )

        self.assertIn(
            "ORDER_ECG",
            runtime.session.reasoning_state
            .ordered_investigations
        )

    def test_diagnosis_creates_hypothesis(self):

        runtime = self.create_runtime()

        self.publish_action(
            runtime,
            "DIAGNOSIS_NSTEMI"
        )

        hypotheses = (
            runtime.session.reasoning_state
            .active_hypotheses
        )

        self.assertEqual(
            len(hypotheses),
            1
        )

        self.assertEqual(
            hypotheses[0].name,
            "DIAGNOSIS_NSTEMI"
        )

    def test_confirm_updates_confirmed_hypotheses(self):

        runtime = self.create_runtime()

        self.publish_action(
            runtime,
            "DIAGNOSIS_NSTEMI"
        )

        self.publish_action(
            runtime,
            "CONFIRM_NSTEMI"
        )

        confirmed = (
            runtime.session.reasoning_state
            .confirmed_hypotheses
        )

        self.assertEqual(
            len(confirmed),
            1
        )

        self.assertEqual(
            confirmed[0].name,
            "DIAGNOSIS_NSTEMI"
        )

        self.assertEqual(
            confirmed[0].status,
            "CONFIRMED"
        )

    def test_treatment_updates_reasoning_state(self):

        runtime = self.create_runtime()

        self.publish_action(
            runtime,
            "TREAT_ASPIRIN"
        )

        treatments = (
            runtime.session.reasoning_state
            .performed_treatments
        )

        self.assertIn(
            "TREAT_ASPIRIN",
            treatments
        )


if __name__ == "__main__":

    unittest.main()
