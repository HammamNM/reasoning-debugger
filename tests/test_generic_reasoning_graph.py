import unittest

from kernel.events import create_event
from kernel.reasoning_graph_builder import ReasoningGraphBuilder
from kernel.models import PrimitiveType
from kernel.graph import EdgeRelation


class TestGenericReasoningGraph(unittest.TestCase):

    def test_evidence_event_creates_evidence_node(self):

        builder = ReasoningGraphBuilder()

        event = create_event(
            "EVIDENCE",
            {
                "content": "Three failed payments"
            },
            source="AGENT_TRACE"
        )

        node = builder.process_event(event)

        self.assertIsNotNone(node)

        self.assertEqual(
            node.primitive,
            PrimitiveType.EVIDENCE
        )


    def test_inference_event_creates_inference_node(self):

        builder = ReasoningGraphBuilder()

        event = create_event(
            "INFERENCE",
            {
                "content":
                    "Customer is attempting fraud"
            },
            source="AGENT_TRACE"
        )

        node = builder.process_event(event)

        self.assertIsNotNone(node)

        self.assertEqual(
            node.primitive,
            PrimitiveType.INFERENCE
        )


    def test_reasoning_chain_creates_sequence_edges(self):

        builder = ReasoningGraphBuilder()

        evidence = builder.process_event(

            create_event(

                "EVIDENCE",

                {
                    "content":
                        "Three failed payments"
                },

                source="AGENT_TRACE"

            )

        )

        inference = builder.process_event(

            create_event(

                "INFERENCE",

                {
                    "content":
                        "Customer is attempting fraud"
                },

                source="AGENT_TRACE"

            )

        )

        decision = builder.process_event(

            create_event(

                "ACTION",

                {
                    "action":
                        "TREAT_CUSTOMER"
                },

                source="AGENT_TRACE"

            )

        )

        sequence_edges = (
            builder.graph.edges_by_relation(
                EdgeRelation.SEQUENCE
            )
        )

        self.assertEqual(
            len(sequence_edges),
            2
        )


    def test_inference_is_automatically_derived_from_evidence(self):

        builder = ReasoningGraphBuilder()

        evidence = builder.process_event(

            create_event(

                "EVIDENCE",

                {
                    "content":
                        "Three failed payments"
                },

                source="AGENT_TRACE"

            )

        )

        inference = builder.process_event(

            create_event(

                "INFERENCE",

                {
                    "content":
                        "Customer is attempting fraud"
                },

                source="AGENT_TRACE"

            )

        )

        derived_edges = (
            builder.graph.edges_by_relation(
                EdgeRelation.DERIVED_FROM
            )
        )

        self.assertEqual(
            len(derived_edges),
            1
        )

        self.assertEqual(
            derived_edges[0].source,
            evidence.id
        )

        self.assertEqual(
            derived_edges[0].target,
            inference.id
        )

        self.assertEqual(
            derived_edges[0].relation,
            EdgeRelation.DERIVED_FROM
        )


    def test_evidence_can_support_inference(self):

        builder = ReasoningGraphBuilder()

        evidence = builder.process_event(

            create_event(

                "EVIDENCE",

                {
                    "content":
                        "Payment gateway returned repeated fraud flags"
                },

                source="AGENT_TRACE"

            )

        )

        inference = builder.process_event(

            create_event(

                "INFERENCE",

                {
                    "content":
                        "Customer may be attempting fraud"
                },

                source="AGENT_TRACE"

            )

        )

        builder.connect_support(
            evidence.id,
            inference.id
        )

        support_edges = (
            builder.graph.edges_by_relation(
                EdgeRelation.SUPPORTS
            )
        )

        self.assertEqual(
            len(support_edges),
            1
        )

        self.assertEqual(
            support_edges[0].source,
            evidence.id
        )

        self.assertEqual(
            support_edges[0].target,
            inference.id
        )


if __name__ == "__main__":
    unittest.main()
