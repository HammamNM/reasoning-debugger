from kernel.models import ReasoningUnit
from kernel.graph import ReasoningGraph, EdgeRelation


class UnitGraphBuilder:
    """
    Builds a reasoning graph directly from validated ReasoningUnit objects.

    This component is deliberately structural:
    - it does not classify units
    - it does not infer meaning
    - it does not add domain knowledge
    - it preserves units and their relationships
    """

    def __init__(self, graph=None):
        self.graph = graph or ReasoningGraph()

    def add_unit(self, unit):
        if not isinstance(unit, ReasoningUnit):
            raise TypeError("unit must be a ReasoningUnit")

        self.graph.add_node(unit)

        if len(self.graph.nodes) >= 2:
            previous = self.graph.nodes[-2]
            self.graph.add_edge(
                previous.id,
                unit.id,
                EdgeRelation.SEQUENCE,
            )

        return unit

    def add_units(self, units):
        if units is None:
            raise TypeError(
                "units must be an iterable of ReasoningUnit"
            )

        for unit in units:
            self.add_unit(unit)

        return self.graph

    def add_semantic_edge(self, source_id, target_id, relation):
        """
        Add an explicit semantic relationship between two existing units.

        This method does not infer the relationship and does not mutate
        either ReasoningUnit. Both endpoints must already exist in the graph.
        """

        source_exists = any(
            node.id == source_id
            for node in self.graph.nodes
        )

        target_exists = any(
            node.id == target_id
            for node in self.graph.nodes
        )

        if not source_exists:
            raise ValueError(
                f"Unknown source unit: {source_id}"
            )

        if not target_exists:
            raise ValueError(
                f"Unknown target unit: {target_id}"
            )

        if isinstance(relation, str):
            try:
                relation = EdgeRelation(relation)
            except ValueError:
                raise ValueError(
                    f"Unknown edge relation: {relation}"
                )

        if not isinstance(relation, EdgeRelation):
            raise TypeError(
                "relation must be EdgeRelation"
            )

        if relation == EdgeRelation.SEQUENCE:
            raise ValueError(
                "add_semantic_edge cannot add SEQUENCE relation"
            )

        self.graph.add_edge(
            source_id,
            target_id,
            relation,
        )

        return self.graph.edges[-1]

    def build(self, units):
        return self.add_units(units)
