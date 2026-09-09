from kernel.debug_finding import DebugFinding
from kernel.graph import EdgeRelation, ReasoningGraph
from kernel.models import PrimitiveType


class StructuralFailureDetector:
    """Detects structural reasoning failures from a ReasoningGraph."""

    FAILURE_TYPE = "unsupported_hypothesis"

    def detect(self, graph: ReasoningGraph) -> list[DebugFinding]:
        if not isinstance(graph, ReasoningGraph):
            raise TypeError("graph must be a ReasoningGraph")

        findings = []

        for node in graph.nodes:
            if node.primitive != PrimitiveType.HYPOTHESIS:
                continue

            incoming = graph.incoming_edges(node.id)

            supporting_edges = [
                edge
                for edge in incoming
                if edge.relation == EdgeRelation.SUPPORTS
            ]

            if supporting_edges:
                continue

            findings.append(
                DebugFinding(
                    event_id=node.id,
                    failure_type=self.FAILURE_TYPE,
                    explanation=(
                        "Hypothesis has no incoming SUPPORTS relationship "
                        "from available reasoning units."
                    ),
                    affected_event_ids=(),
                    metadata={
                        "detector": self.__class__.__name__,
                        "reason": "no_supporting_edge",
                    },
                )
            )

        return findings
