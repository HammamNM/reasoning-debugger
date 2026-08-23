import unittest

from backend.session import ClinicalSession
from kernel.bootstrap import KernelBootstrap
from kernel.events import ReasoningEvent
from kernel.reasoning_report_builder import ReasoningReportBuilder
from kernel.graph import EdgeRelation


class TestReasoningReportBuilder(unittest.TestCase):

    def create_runtime(self):
        session = ClinicalSession(
            student_id="student_001",
            scenario_id="REPORT_TEST_001",
        )
        return KernelBootstrap().create_runtime(session)

    def publish(self, runtime, event):
        runtime.publish(event)
        runtime.run_cycle()

    def test_build_contains_hypothesis_report(self):
        runtime = self.create_runtime()

        self.publish(
            runtime,
            ReasoningEvent(
                event_type="ACTION",
                payload={"action": "DIAGNOSIS_NSTEMI"},
                source="STUDENT",
            ),
        )

        report = ReasoningReportBuilder().build(
            runtime.session,
            runtime.graph_builder.graph,
        )

        self.assertEqual(report.session_id, runtime.session.session_id)

        self.assertEqual(len(report.hypotheses), 1)

        hypothesis = report.hypotheses[0]

        self.assertEqual(hypothesis.name, "DIAGNOSIS_NSTEMI")
        self.assertEqual(hypothesis.confidence, 0.50)
        self.assertEqual(hypothesis.status, "ACTIVE")

    def test_build_transfers_supporting_and_contradicting_evidence(self):
        runtime = self.create_runtime()

        self.publish(
            runtime,
            ReasoningEvent(
                event_type="ACTION",
                payload={"action": "DIAGNOSIS_NSTEMI"},
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

        report = ReasoningReportBuilder().build(
            runtime.session,
            runtime.graph_builder.graph,
        )

        hypothesis = report.hypotheses[0]

        self.assertEqual(
            hypothesis.supporting_evidence,
            ["Troponin elevated"],
        )

        self.assertEqual(
            hypothesis.contradicting_evidence,
            ["Alternative finding"],
        )

    def test_build_transfers_confidence_history(self):
        runtime = self.create_runtime()

        self.publish(
            runtime,
            ReasoningEvent(
                event_type="ACTION",
                payload={"action": "DIAGNOSIS_NSTEMI"},
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

        report = ReasoningReportBuilder().build(
            runtime.session,
            runtime.graph_builder.graph,
        )

        history = report.hypotheses[0].confidence_history

        self.assertEqual(len(history), 1)

        self.assertEqual(history[0]["previous"], 0.50)
        self.assertEqual(history[0]["change"], 0.15)
        self.assertEqual(history[0]["current"], 0.65)
        self.assertEqual(
            history[0]["reason"],
            "SUPPORTING_EVIDENCE",
        )

    def test_build_transfers_graph_and_evidence(self):
        runtime = self.create_runtime()

        self.publish(
            runtime,
            ReasoningEvent(
                event_type="ACTION",
                payload={"action": "DIAGNOSIS_NSTEMI"},
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

        report = ReasoningReportBuilder().build(
            runtime.session,
            runtime.graph_builder.graph,
        )

        self.assertEqual(
            len(report.evidence),
            1,
        )

        evidence = report.evidence[0]

        self.assertEqual(
            evidence["content"],
            "Troponin elevated",
        )

        self.assertEqual(
            evidence["source"],
            "INVESTIGATION_ENGINE",
        )

        self.assertEqual(
            evidence["strength"],
            1.0,
        )

        self.assertIn(
            "DIAGNOSIS_NSTEMI",
            evidence["supports"],
        )

        self.assertGreater(
            len(report.reasoning_nodes),
            0,
        )

        self.assertGreaterEqual(
            len(report.reasoning_edges),
            1,
        )

        self.assertEqual(
            len(report.reasoning_path),
            len(report.reasoning_nodes),
        )



    def test_reasoning_path_follows_sequence_edges_not_node_order(self):
        runtime = self.create_runtime()

        self.publish(
            runtime,
            ReasoningEvent(
                event_type="ACTION",
                payload={"action": "DIAGNOSIS_NSTEMI"},
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

        graph = runtime.graph_builder.graph

        sequence_edges = [
            edge
            for edge in graph.edges
            if edge.relation == EdgeRelation.SEQUENCE
        ]

        expected_path = [
            sequence_edges[0].source,
            sequence_edges[0].target,
        ]

        current = expected_path[-1]

        while True:
            next_edges = [
                edge
                for edge in sequence_edges
                if edge.source == current
            ]

            if not next_edges:
                break

            current = next_edges[0].target
            expected_path.append(current)

        graph.nodes.reverse()

        report = ReasoningReportBuilder().build(
            runtime.session,
            graph,
        )

        self.assertEqual(
            report.reasoning_path,
            expected_path,
        )

if __name__ == "__main__":
    unittest.main()
