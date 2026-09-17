from kernel.graph import EdgeRelation, ReasoningGraph
from kernel.models import PrimitiveType, ReasoningUnit
from kernel.provenance import ProvenanceRecord
from kernel.reasoning_trace import ReasoningTrace

class TraceGraphAdapter:
    """
    Converts a ReasoningTrace into a ReasoningGraph.
    Preserves event order (SEQUENCE) and maps semantic dependencies (DERIVED_FROM)
    if provided in the event metadata.
    """
    EVENT_TYPE_MAP = {
        "OBSERVATION": PrimitiveType.OBSERVATION,
        "EVIDENCE": PrimitiveType.EVIDENCE,
        "INFERENCE": PrimitiveType.INFERENCE,
        "INVESTIGATION_RESULT": PrimitiveType.INVESTIGATION,
        "DECISION_ASSESSMENT": PrimitiveType.DECISION,
        "OUTCOME_UPDATED": PrimitiveType.OUTCOME,
        "observation": PrimitiveType.OBSERVATION,
        "evidence": PrimitiveType.EVIDENCE,
        "inference": PrimitiveType.INFERENCE,
        "investigation": PrimitiveType.INVESTIGATION,
        "hypothesis": PrimitiveType.HYPOTHESIS,
        "decision": PrimitiveType.DECISION,
        "outcome": PrimitiveType.OUTCOME,
    }

    def build(self, trace: ReasoningTrace) -> ReasoningGraph:
        if not isinstance(trace, ReasoningTrace):
            raise TypeError("trace must be a ReasoningTrace")

        graph = ReasoningGraph()
        previous_id = None

        for event in trace.events:
            event_type = event.event_type
            primitive = self.EVENT_TYPE_MAP.get(event_type) or self.EVENT_TYPE_MAP.get(event_type.lower())

            if primitive is None:
                primitive = PrimitiveType.GENERIC_EVENT

            unit = ReasoningUnit(
                id=event.id,
                primitive=primitive,
                content=event.content,
                provenance=ProvenanceRecord(
                    source="TRACE",
                    event_type=event.event_type,
                    metadata=dict(event.metadata or {}),
                ),
            )
            graph.add_node(unit)

            if previous_id is not None:
                graph.add_edge(previous_id, event.id, EdgeRelation.SEQUENCE)

            # Fix: DERIVED_FROM points from Child (event.id) to Parent (parent_id)
            derived_from = event.metadata.get("derived_from", [])
            if isinstance(derived_from, list):
                for parent_id in derived_from:
                    graph.add_edge(event.id, parent_id, EdgeRelation.DERIVED_FROM)

            previous_id = event.id

        return graph
