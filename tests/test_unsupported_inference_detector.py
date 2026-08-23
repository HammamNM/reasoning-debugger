import unittest

from kernel.events import create_event
from kernel.reasoning_graph_builder import ReasoningGraphBuilder
from analytics.unsupported_inference_detector import (
    UnsupportedInferenceDetector
)


class TestUnsupportedInferenceDetector(unittest.TestCase):

    def test_detects_inference_without_supporting_evidence(self):

        builder = ReasoningGraphBuilder()

        builder.process_event(
            create_event(
                "EVIDENCE",
                {
                    "content":
                        "Three failed payments"
                },
                source="AGENT_TRACE"
            )
        )

        builder.process_event(
            create_event(
                "INFERENCE",
                {
                    "content":
                        "Customer is attempting fraud"
                },
                source="AGENT_TRACE"
            )
        )

        detector = UnsupportedInferenceDetector()

        patterns = detector.detect(
            builder.graph
        )

        self.assertEqual(
            len(patterns),
            1
        )

        self.assertEqual(
            patterns[0]["pattern_id"],
            "RP-001"
        )

        self.assertEqual(
            patterns[0]["name"],
            "Unsupported Inference"
        )


    def test_does_not_flag_supported_inference(self):

        builder = ReasoningGraphBuilder()

        evidence = builder.process_event(
            create_event(
                "EVIDENCE",
                {
                    "content":
                        "Gateway returned repeated fraud flags"
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

        detector = UnsupportedInferenceDetector()

        patterns = detector.detect(
            builder.graph
        )

        self.assertEqual(
            len(patterns),
            0
        )


if __name__ == "__main__":
    unittest.main()
