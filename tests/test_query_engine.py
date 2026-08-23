import unittest

from kernel.models import ReasoningUnit, PrimitiveType
from kernel.graph import ReasoningGraph, EdgeRelation
from kernel.query_engine import QueryEngine


class TestQueryEngine(unittest.TestCase):

    def setUp(self):
        graph = ReasoningGraph()

        self.observation = ReasoningUnit(
            id="1",
            primitive=PrimitiveType.OBSERVATION,
            content="Chest pain"
        )

        self.hypothesis_1 = ReasoningUnit(
            id="2",
            primitive=PrimitiveType.HYPOTHESIS,
            content="DIAGNOSIS_NSTEMI"
        )

        self.hypothesis_2 = ReasoningUnit(
            id="3",
            primitive=PrimitiveType.HYPOTHESIS,
            content="DIAGNOSIS_PE"
        )

        self.evidence_1 = ReasoningUnit(
            id="4",
            primitive=PrimitiveType.EVIDENCE,
            content="Troponin elevated"
        )

        self.evidence_2 = ReasoningUnit(
            id="5",
            primitive=PrimitiveType.EVIDENCE,
            content="D-dimer negative"
        )

        for node in (
            self.observation,
            self.hypothesis_1,
            self.hypothesis_2,
            self.evidence_1,
            self.evidence_2,
        ):
            graph.add_node(node)

        graph.add_edge(
            "1",
            "2",
            EdgeRelation.SEQUENCE
        )

        graph.add_edge(
            "2",
            "3",
            EdgeRelation.SEQUENCE
        )

        graph.add_edge(
            "4",
            "2",
            EdgeRelation.SUPPORTS
        )

        graph.add_edge(
            "5",
            "2",
            EdgeRelation.CONTRADICTS
        )

        graph.add_edge(
            "4",
            "2",
            EdgeRelation.CONFIRMS
        )

        graph.add_edge(
            "5",
            "3",
            EdgeRelation.REJECTS
        )

        self.query = QueryEngine(graph)

    def test_nodes_by_primitive(self):
        hypotheses = self.query.nodes_by_primitive(
            PrimitiveType.HYPOTHESIS
        )

        self.assertEqual(len(hypotheses), 2)
        self.assertIn(self.hypothesis_1, hypotheses)
        self.assertIn(self.hypothesis_2, hypotheses)

    def test_node_by_id(self):
        node = self.query.node_by_id("2")

        self.assertIs(node, self.hypothesis_1)

        self.assertIsNone(
            self.query.node_by_id("999")
        )

    def test_edges_by_relation(self):
        edges = self.query.edges_by_relation(
            EdgeRelation.SUPPORTS
        )

        self.assertEqual(len(edges), 1)
        self.assertEqual(edges[0].source, "4")
        self.assertEqual(edges[0].target, "2")

    def test_edges_by_relation_accepts_string(self):
        edges = self.query.edges_by_relation("SUPPORTS")

        self.assertEqual(len(edges), 1)
        self.assertEqual(
            edges[0].relation,
            EdgeRelation.SUPPORTS
        )

    def test_outgoing(self):
        edges = self.query.outgoing("2")

        self.assertEqual(len(edges), 1)
        self.assertEqual(edges[0].target, "3")

    def test_incoming(self):
        edges = self.query.incoming("2")

        self.assertEqual(len(edges), 4)

    def test_outgoing_by_relation(self):
        edges = self.query.outgoing_by_relation(
            "4",
            EdgeRelation.SUPPORTS
        )

        self.assertEqual(len(edges), 1)
        self.assertEqual(edges[0].target, "2")

    def test_incoming_by_relation(self):
        edges = self.query.incoming_by_relation(
            "2",
            EdgeRelation.SUPPORTS
        )

        self.assertEqual(len(edges), 1)
        self.assertEqual(edges[0].source, "4")

    def test_next_nodes(self):
        next_nodes = self.query.next_nodes("1")

        self.assertEqual(len(next_nodes), 1)
        self.assertIs(
            next_nodes[0],
            self.hypothesis_1
        )

    def test_previous_nodes(self):
        previous_nodes = self.query.previous_nodes("2")

        self.assertEqual(len(previous_nodes), 1)
        self.assertIs(
            previous_nodes[0],
            self.observation
        )

    def test_hypotheses_supported_by(self):
        supported = self.query.hypotheses_supported_by(
            minimum_support=1
        )

        self.assertIn(
            self.hypothesis_1,
            supported
        )

    def test_hypotheses_supported_by_minimum_support(self):
        supported = self.query.hypotheses_supported_by(
            minimum_support=2
        )

        self.assertEqual(
            supported,
            []
        )

    def test_hypotheses_with_contradictions(self):
        contradicted = (
            self.query.hypotheses_with_contradictions()
        )

        self.assertIn(
            self.hypothesis_1,
            contradicted
        )

    def test_confirmed_hypotheses(self):
        confirmed = (
            self.query.confirmed_hypotheses()
        )

        self.assertIn(
            self.hypothesis_1,
            confirmed
        )

    def test_rejected_hypotheses(self):
        rejected = (
            self.query.rejected_hypotheses()
        )

        self.assertIn(
            self.hypothesis_2,
            rejected
        )


if __name__ == "__main__":
    unittest.main()
