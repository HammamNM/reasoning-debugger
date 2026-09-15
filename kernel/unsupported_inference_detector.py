from kernel.debug_finding import DebugFinding
from kernel.graph import EdgeRelation, ReasoningGraph
from kernel.models import PrimitiveType


class UnsupportedInferenceDetector:
    """
    Detects the first inference that has no explicit semantic support.

    Support is established only through explicit DERIVED_FROM relationships
    to an EVIDENCE or INFERENCE node.

    Temporal SEQUENCE edges are never treated as causal or evidentiary
    support.
    """

    FAILURE_TYPE = "unsupported_inference"

    def detect(self, graph: ReasoningGraph) -> list[DebugFinding]:
        if not isinstance(graph, ReasoningGraph):
            raise TypeError("graph must be a ReasoningGraph")

        for node in graph.nodes:
            if node.primitive != PrimitiveType.INFERENCE:
                continue

            # Missing provenance alone is not evidence of failure.
            # An inference is eligible for unsupported-reasoning detection
            # only when the source explicitly marks that support is required.
            if node.provenance is None or node.provenance.metadata.get("support_required") is not True:
                continue

            supporting_parents = []

            for edge in graph.outgoing_edges(node.id):
                if edge.relation != EdgeRelation.DERIVED_FROM:
                    continue

                parent = next(
                    (candidate for candidate in graph.nodes
                     if candidate.id == edge.target),
                    None,
                )

                if parent is None:
                    continue

                if parent.primitive in (
                    PrimitiveType.EVIDENCE,
                    PrimitiveType.OBSERVATION,
                    PrimitiveType.INFERENCE,
                ):
                    supporting_parents.append(parent.id)

            if supporting_parents:
                continue

            return [
                DebugFinding(
                    event_id=node.id,
                    failure_type=self.FAILURE_TYPE,
                    explanation=(
                        "Inference has no explicit DERIVED_FROM relationship "
                        "to supporting evidence or inference."
                    ),
                    affected_event_ids=(),
                    metadata={
                        "detector": self.__class__.__name__,
                        "reason": "no_explicit_support",
                    },
                )
            ]

        return []
