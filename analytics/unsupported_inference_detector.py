from kernel.query_engine import QueryEngine
from kernel.models import PrimitiveType


class UnsupportedInferenceDetector:

    def detect(
        self,
        reasoning_graph
    ):

        query = QueryEngine(
            reasoning_graph
        )

        detected = []

        inferences = query.nodes_by_primitive(
            PrimitiveType.INFERENCE
        )

        for inference in inferences:

            support_edges = (
                query.edges_by_relation(
                    "SUPPORTS"
                )
            )

            supported = False

            for edge in support_edges:

                if edge.target == inference.id:

                    supported = True

                    break

            if supported:
                continue

            detected.append({

                "pattern_id":
                    "RP-001",

                "name":
                    "Unsupported Inference",

                "inference":
                    inference.content,

                "reason":
                    "Inference has no supporting evidence",

                "severity":
                    "MEDIUM"

            })

        return detected
