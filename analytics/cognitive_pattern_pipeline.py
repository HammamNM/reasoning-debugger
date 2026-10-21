from analytics.anchoring_detector import (
    AnchoringDetector
)

from analytics.premature_closure_detector import (
    PrematureClosureDetector
)

from analytics.confirmation_bias_detector import (
    ConfirmationBiasDetector
)

from analytics.unsupported_inference_detector import (
    UnsupportedInferenceDetector
)

from analytics.cognitive_metrics import (
    CognitiveMetricEngine
)


class CognitivePatternPipeline:

    def __init__(self):

        self.detectors = [

            AnchoringDetector(),

            PrematureClosureDetector(),

            ConfirmationBiasDetector(),

            UnsupportedInferenceDetector()

        ]

        self.metric_engine = (
            CognitiveMetricEngine()
        )


    def analyze(
        self,
        reasoning_graph,
        reasoning_state=None
    ):
        patterns = []

        for detector in self.detectors:
            if isinstance(detector, AnchoringDetector):
                if reasoning_state is None:
                    continue

                detected_patterns = detector.detect(
                    reasoning_state
                )
            else:
                detected_patterns = detector.detect(
                    reasoning_graph
                )

            patterns.extend(
                detected_patterns
            )

        metrics = self.metric_engine.evaluate(
            patterns
        )

        return {
            "patterns": patterns,
            "metrics": metrics
        }
