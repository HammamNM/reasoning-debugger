import unittest

from kernel.bootstrap import KernelBootstrap
from kernel.events import ReasoningEvent
from kernel.graph import EdgeRelation
from backend.session import ClinicalSession


class TestEvidenceRuntime(unittest.TestCase):

    def create_runtime(self):
        clinical_session = ClinicalSession(
            student_id="student_001",
            scenario_id="EVIDENCE_TEST_001"
        )

        return KernelBootstrap().create_runtime(
            clinical_session
        )

    def publish(self, runtime, event):
        runtime.publish(event)
        runtime.run_cycle()

    def test_supporting_evidence_updates_hypothesis(self):

        runtime = self.create_runtime()

        # 1. Create hypothesis
        self.publish(
            runtime,
            ReasoningEvent(
                event_type="ACTION",
                payload={
                    "action": "DIAGNOSIS_NSTEMI"
                },
                source="STUDENT"
            )
        )

        state = runtime.session.reasoning_state

        self.assertEqual(
            len(state.active_hypotheses),
            1
        )

        hypothesis = state.active_hypotheses[0]

        self.assertEqual(
            hypothesis.name,
            "DIAGNOSIS_NSTEMI"
        )

        self.assertEqual(
            hypothesis.confidence,
            0.50
        )

        # 2. Investigation result provides supporting evidence
        self.publish(
            runtime,
            ReasoningEvent(
                event_type="INVESTIGATION_RESULT",
                payload={
                    "investigation_id": "ECG_001",
                    "result": {
                        "result": "ST depression"
                    },
                    "supports": [
                        "DIAGNOSIS_NSTEMI"
                    ],
                    "strength": 1.0
                },
                source="SCENARIO_ENGINE"
            )
        )

        # 3. Evidence should exist
        self.assertTrue(
            hasattr(
                runtime.session,
                "evidence"
            )
        )

        self.assertEqual(
            len(runtime.session.evidence),
            1
        )

        evidence = runtime.session.evidence[0]

        self.assertIn(
            evidence,
            hypothesis.supporting_evidence
        )

        self.assertIn(
            "DIAGNOSIS_NSTEMI",
            evidence.supports
        )

        # 4. Confidence should increase
        self.assertEqual(
            hypothesis.confidence,
            0.65
        )

        # 5. Confidence history should contain the update
        self.assertEqual(
            len(hypothesis.confidence_history),
            1
        )

        update = hypothesis.confidence_history[0]

        self.assertEqual(
            update.previous,
            0.50
        )

        self.assertEqual(
            update.change,
            0.15
        )

        self.assertEqual(
            update.current,
            0.65
        )

        self.assertEqual(
            update.reason,
            "SUPPORTING_EVIDENCE"
        )

    def test_contradicting_evidence_updates_hypothesis(self):

        runtime = self.create_runtime()

        # Create hypothesis
        self.publish(
            runtime,
            ReasoningEvent(
                event_type="ACTION",
                payload={
                    "action": "DIAGNOSIS_NSTEMI"
                },
                source="STUDENT"
            )
        )

        hypothesis = (
            runtime.session.reasoning_state
            .active_hypotheses[0]
        )

        # Contradicting evidence
        self.publish(
            runtime,
            ReasoningEvent(
                event_type="INVESTIGATION_RESULT",
                payload={
                    "investigation_id": "TROPONIN_001",
                    "result": {
                        "result": "Troponin negative"
                    },
                    "contradicts": [
                        "DIAGNOSIS_NSTEMI"
                    ],
                    "strength": 1.0
                },
                source="SCENARIO_ENGINE"
            )
        )

        self.assertEqual(
            hypothesis.confidence,
            0.30
        )

        self.assertEqual(
            len(
                hypothesis.contradicting_evidence
            ),
            1
        )

        self.assertEqual(
            len(
                hypothesis.confidence_history
            ),
            1
        )

        update = (
            hypothesis.confidence_history[0]
        )

        self.assertEqual(
            update.previous,
            0.50
        )

        self.assertEqual(
            update.change,
            -0.20
        )

        self.assertEqual(
            update.current,
            0.30
        )

        self.assertEqual(
            update.reason,
            "CONTRADICTING_EVIDENCE"
        )
    def test_runtime_evidence_supports_hypothesis_in_state_and_graph(self):
        runtime = self.create_runtime()

        self.publish(
            runtime,
            ReasoningEvent(
                event_type="ACTION",
                payload={"action": "DIAGNOSIS_NSTEMI"},
                source="STUDENT"
            )
        )

        runtime.publish(
            ReasoningEvent(
                event_type="EVIDENCE",
                payload={
                    "content": "Troponin elevated",
                    "supports": ["DIAGNOSIS_NSTEMI"],
                    "strength": 1.0
                },
                source="INVESTIGATION_ENGINE"
            )
        )

        runtime.run_cycle()

        hypothesis = runtime.session.reasoning_state.hypotheses[0]

        self.assertEqual(
            len(hypothesis.supporting_evidence),
            1
        )

        support_edges = [
            edge
            for edge in runtime.graph_builder.graph.edges
            if edge.relation == EdgeRelation.SUPPORTS
        ]

        self.assertEqual(
            len(support_edges),
            1
        )

    def test_runtime_investigation_result_supports_hypothesis_in_state_and_graph(self):
        from kernel.events import ReasoningEvent
        from kernel.graph import EdgeRelation
        runtime = self.create_runtime()

        self.publish(
            runtime,
            ReasoningEvent(
                event_type="ACTION",
                payload={"action": "DIAGNOSIS_NSTEMI"},
                source="STUDENT"
            )
        )

        runtime.publish(
            ReasoningEvent(
                event_type="INVESTIGATION_RESULT",
                payload={
                    "investigation_id": "TROPONIN_001",
                    "result": "Troponin elevated",
                    "supports": ["DIAGNOSIS_NSTEMI"],
                    "strength": 1.0
                },
                source="INVESTIGATION_ENGINE"
            )
        )

        runtime.run_cycle()

        hypothesis = runtime.session.reasoning_state.hypotheses[0]

        self.assertEqual(
            len(hypothesis.supporting_evidence),
            1
        )

        support_edges = [
            edge
            for edge in runtime.graph_builder.graph.edges
            if edge.relation == EdgeRelation.SUPPORTS
        ]

        self.assertEqual(
            len(support_edges),
            1
        )

        target_node = next(
            node
            for node in runtime.graph_builder.graph.nodes
            if node.id == support_edges[0].target
        )

        self.assertEqual(
            target_node.primitive.value,
            "HYPOTHESIS"
        )

        self.assertIn(
            "DIAGNOSIS_NSTEMI",
            target_node.content
        )


    def test_runtime_supporting_and_contradicting_evidence_create_correct_graph_edges(self):
        runtime = self.create_runtime()

        self.publish(
            runtime,
            ReasoningEvent(
                event_type="ACTION",
                payload={
                    "action": "DIAGNOSIS_NSTEMI",
                },
                source="STUDENT",
            ),
        )

        self.publish(
            runtime,
            ReasoningEvent(
                event_type="EVIDENCE",
                payload={
                    "content": "Troponin elevated",
                    "supports": ["DIAGNOSIS_NSTEMI"],
                    "strength": 1.0,
                },
                source="INVESTIGATION_ENGINE",
            ),
        )

        self.publish(
            runtime,
            ReasoningEvent(
                event_type="EVIDENCE",
                payload={
                    "content": "Alternative finding",
                    "contradicts": ["DIAGNOSIS_NSTEMI"],
                    "strength": 1.0,
                },
                source="INVESTIGATION_ENGINE",
            ),
        )

        graph = runtime.graph_builder.graph

        support_edges = [
            edge
            for edge in graph.edges
            if edge.relation == EdgeRelation.SUPPORTS
        ]

        contradiction_edges = [
            edge
            for edge in graph.edges
            if edge.relation == EdgeRelation.CONTRADICTS
        ]

        self.assertEqual(len(support_edges), 1)
        self.assertEqual(len(contradiction_edges), 1)

        hypothesis_node = next(
            node
            for node in graph.nodes
            if node.primitive.value == "HYPOTHESIS"
            and "DIAGNOSIS_NSTEMI" in node.content
        )

        self.assertEqual(
            support_edges[0].target,
            hypothesis_node.id,
        )

        self.assertEqual(
            contradiction_edges[0].target,
            hypothesis_node.id,
        )

if __name__ == "__main__":
    unittest.main()

