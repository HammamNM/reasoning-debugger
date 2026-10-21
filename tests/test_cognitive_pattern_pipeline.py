import unittest

from kernel.events import create_event
from kernel.reasoning_graph_builder import ReasoningGraphBuilder
from analytics.cognitive_pattern_pipeline import (
    CognitivePatternPipeline
)


class TestCognitivePatternPipeline(unittest.TestCase):

    def test_pipeline_detects_unsupported_inference(self):

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

        result = CognitivePatternPipeline().analyze(
            builder.graph
        )

        patterns = result["patterns"]

        unsupported = [

            pattern

            for pattern in patterns

            if pattern["pattern_id"] == "RP-001"

        ]

        self.assertEqual(
            len(unsupported),
            1
        )



    def test_pipeline_detects_anchoring_with_reasoning_state(self):
        from kernel.reasoning_state import ReasoningState
        from kernel.hypothesis_manager import HypothesisManager

        state = ReasoningState()
        manager = HypothesisManager()

        hypothesis = manager.create(
            state,
            "DIAGNOSIS_NSTEMI",
            trigger="INITIAL_THOUGHT"
        )

        manager.add_contradicting_evidence(
            hypothesis,
            {
                "finding": "NORMAL_TROPONIN"
            }
        )

        result = CognitivePatternPipeline().analyze(
            ReasoningGraphBuilder().graph,
            state
        )

        patterns = result["patterns"]

        anchoring = [
            pattern
            for pattern in patterns
            if pattern["pattern_id"] == "CP-201"
        ]

        self.assertEqual(len(anchoring), 1)


if __name__ == "__main__":
    unittest.main()
