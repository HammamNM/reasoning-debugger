from kernel.reasoning_report import (
    ReasoningReport,
    HypothesisReport,
)

from kernel.query_engine import (
    QueryEngine,
)


class ReasoningReportBuilder:

    def build(
        self,
        session,
        graph,
    ):
        query = QueryEngine(graph)

        session_id = getattr(
            session,
            "session_id",
            "",
        )

        report = ReasoningReport(
            session_id=session_id
        )

        reasoning_state = getattr(
            session,
            "reasoning_state",
            None,
        )

        if reasoning_state is not None:
            for hypothesis in reasoning_state.hypotheses:

                supporting = [
                    evidence.content
                    for evidence in (
                        hypothesis.supporting_evidence
                    )
                ]

                contradicting = [
                    evidence.content
                    for evidence in (
                        hypothesis.contradicting_evidence
                    )
                ]

                history = []

                for update in (
                    hypothesis.confidence_history
                ):
                    history.append(
                        {
                            "previous": update.previous,
                            "change": update.change,
                            "current": update.current,
                            "reason": update.reason,
                            "timestamp": update.timestamp,
                        }
                    )

                hypothesis_report = HypothesisReport(
                    name=hypothesis.name,
                    confidence=hypothesis.confidence,
                    status=hypothesis.status,
                    supporting_evidence=supporting,
                    contradicting_evidence=contradicting,
                    confidence_history=history,
                )

                report.hypotheses.append(
                    hypothesis_report
                )

        report.confirmed_hypotheses = [
            node.id
            for node in query.confirmed_hypotheses()
        ]

        report.rejected_hypotheses = [
            node.id
            for node in query.rejected_hypotheses()
        ]

        report.reasoning_nodes = [
            {
                "id": node.id,
                "primitive": node.primitive.value,
                "content": node.content,
            }
            for node in graph.nodes
        ]

        report.reasoning_edges = [
            {
                "source": edge.source,
                "target": edge.target,
                "relation": edge.relation.value,
            }
            for edge in graph.edges
        ]

        # ---------------------------------------------------------
        # Reasoning path
        # ---------------------------------------------------------
        # The path MUST follow SEQUENCE edges.
        # It MUST NOT depend on graph.nodes insertion order.
        # ---------------------------------------------------------

        sequence_edges = [
            edge
            for edge in graph.edges
            if edge.relation.value == "SEQUENCE"
        ]

        if sequence_edges:

            sources = {
                edge.source
                for edge in sequence_edges
            }

            targets = {
                edge.target
                for edge in sequence_edges
            }

            # Root = source that is never a target.
            root_candidates = sources - targets

            if not root_candidates:
                raise ValueError(
                    "Cannot determine reasoning path root "
                    "from SEQUENCE edges."
                )

            # Deterministic root selection.
            root = sorted(root_candidates)[0]

            path = []
            current = root
            visited = set()

            while current is not None:

                if current in visited:
                    raise ValueError(
                        "Cycle detected in SEQUENCE graph."
                    )

                visited.add(current)
                path.append(current)

                next_edges = [
                    edge
                    for edge in sequence_edges
                    if edge.source == current
                ]

                if not next_edges:
                    break

                if len(next_edges) > 1:
                    raise ValueError(
                        "Ambiguous reasoning path: "
                        f"node {current} has multiple "
                        "SEQUENCE successors."
                    )

                current = next_edges[0].target

            report.reasoning_path = path

        else:
            report.reasoning_path = []

        # ---------------------------------------------------------
        # Evidence
        # ---------------------------------------------------------

        if hasattr(
            session,
            "evidence",
        ):
            report.evidence = [
                {
                    "id": evidence.evidence_id,
                    "source": evidence.source,
                    "content": evidence.content,
                    "strength": evidence.strength,
                    "supports": evidence.supports,
                    "contradicts": evidence.contradicts,
                }
                for evidence in session.evidence
            ]

        return report
