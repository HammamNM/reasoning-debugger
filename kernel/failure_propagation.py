from kernel.graph import EdgeRelation, ReasoningGraph

class FailurePropagationAnalyzer:
    """
    Finds downstream reasoning units reachable from a failed node.
    Strictly follows semantic dependencies (SUPPORTS, DERIVED_FROM),
    ignoring chronological SEQUENCE.
    """
    def analyze(self, graph: ReasoningGraph, failure_node_id: str) -> tuple[str, ...]:
        if not isinstance(graph, ReasoningGraph):
            raise TypeError("graph must be a ReasoningGraph")
        if not isinstance(failure_node_id, str):
            raise TypeError("failure_node_id must be a string")
        if not any(node.id == failure_node_id for node in graph.nodes):
            return ()

        affected = []
        visited = {failure_node_id}
        queue = [failure_node_id]

        while queue:
            current_id = queue.pop(0)

            # 1. Nodes that current_id SUPPORTS / CONFIRMS / REJECTS
            for edge in graph.outgoing_edges(current_id):
                if edge.relation in (EdgeRelation.SUPPORTS, EdgeRelation.CONFIRMS, EdgeRelation.REJECTS):
                    if edge.target not in visited:
                        visited.add(edge.target)
                        affected.append(edge.target)
                        queue.append(edge.target)

            # 2. Nodes DERIVED_FROM current_id
            for edge in graph.incoming_edges(current_id):
                if edge.relation == EdgeRelation.DERIVED_FROM:
                    if edge.source not in visited:
                        visited.add(edge.source)
                        affected.append(edge.source)
                        queue.append(edge.source)

        return tuple(affected)
