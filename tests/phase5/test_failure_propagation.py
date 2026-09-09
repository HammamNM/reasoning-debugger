import pytest

from kernel.failure_propagation import FailurePropagationAnalyzer
from kernel.graph import EdgeRelation, ReasoningGraph
from kernel.models import PrimitiveType, ReasoningUnit


def unit(unit_id, primitive, content):
    return ReasoningUnit(
        id=unit_id,
        primitive=primitive,
        content=content,
    )


def test_finds_direct_downstream_event():
    graph = ReasoningGraph()

    first = unit("event-1", PrimitiveType.HYPOTHESIS, "H1")
    second = unit("event-2", PrimitiveType.DECISION, "Decision")

    graph.add_node(first)
    graph.add_node(second)

    graph.add_edge(
        "event-1",
        "event-2",
        EdgeRelation.SEQUENCE,
    )

    result = FailurePropagationAnalyzer().analyze(
        graph,
        "event-1",
    )

    assert result == ()


def test_finds_multi_step_downstream_events():
    graph = ReasoningGraph()

    nodes = [
        unit("event-1", PrimitiveType.HYPOTHESIS, "H1"),
        unit("event-2", PrimitiveType.INVESTIGATION, "Investigation"),
        unit("event-3", PrimitiveType.OUTCOME, "Outcome"),
        unit("event-4", PrimitiveType.DECISION, "Decision"),
    ]

    for node in nodes:
        graph.add_node(node)

    graph.add_edge("event-1", "event-2", EdgeRelation.SEQUENCE)
    graph.add_edge("event-2", "event-3", EdgeRelation.SEQUENCE)
    graph.add_edge("event-3", "event-4", EdgeRelation.SEQUENCE)

    result = FailurePropagationAnalyzer().analyze(
        graph,
        "event-1",
    )

    assert result == ()


def test_does_not_include_failure_node_itself():
    graph = ReasoningGraph()

    node = unit(
        "event-1",
        PrimitiveType.HYPOTHESIS,
        "H1",
    )

    graph.add_node(node)

    result = FailurePropagationAnalyzer().analyze(
        graph,
        "event-1",
    )

    assert result == ()


def test_handles_branching_graph():
    graph = ReasoningGraph()

    root = unit("event-1", PrimitiveType.HYPOTHESIS, "H1")
    left = unit("event-2", PrimitiveType.INVESTIGATION, "Left")
    right = unit("event-3", PrimitiveType.INVESTIGATION, "Right")
    decision = unit("event-4", PrimitiveType.DECISION, "Decision")

    for node in (root, left, right, decision):
        graph.add_node(node)

    graph.add_edge("event-1", "event-2", EdgeRelation.SEQUENCE)
    graph.add_edge("event-1", "event-3", EdgeRelation.SEQUENCE)
    graph.add_edge("event-2", "event-4", EdgeRelation.SEQUENCE)
    graph.add_edge("event-3", "event-4", EdgeRelation.SEQUENCE)

    result = FailurePropagationAnalyzer().analyze(
        graph,
        "event-1",
    )

    assert set(result) == set()


def test_returns_empty_for_unknown_node():
    graph = ReasoningGraph()

    result = FailurePropagationAnalyzer().analyze(
        graph,
        "missing",
    )

    assert result == ()


def test_rejects_invalid_graph():
    with pytest.raises(TypeError):
        FailurePropagationAnalyzer().analyze(
            object(),
            "event-1",
        )


def test_rejects_invalid_node_id():
    graph = ReasoningGraph()

    with pytest.raises(TypeError):
        FailurePropagationAnalyzer().analyze(
            graph,
            123,
        )


def test_does_not_modify_graph():
    graph = ReasoningGraph()

    first = unit("event-1", PrimitiveType.HYPOTHESIS, "H1")
    second = unit("event-2", PrimitiveType.DECISION, "Decision")

    graph.add_node(first)
    graph.add_node(second)
    graph.add_edge("event-1", "event-2", EdgeRelation.SEQUENCE)

    nodes_before = list(graph.nodes)
    edges_before = list(graph.edges)

    FailurePropagationAnalyzer().analyze(graph, "event-1")

    assert graph.nodes == nodes_before
    assert graph.edges == edges_before

def test_propagation_follows_semantic_edges_only():
    graph = ReasoningGraph()

    failure = unit(
        "event-1",
        PrimitiveType.HYPOTHESIS,
        "Failed hypothesis",
    )
    semantic_target = unit(
        "event-2",
        PrimitiveType.HYPOTHESIS,
        "Supported hypothesis",
    )
    downstream = unit(
        "event-3",
        PrimitiveType.DECISION,
        "Decision",
    )

    graph.add_node(failure)
    graph.add_node(semantic_target)
    graph.add_node(downstream)

    graph.add_edge(
        "event-1",
        "event-2",
        EdgeRelation.SUPPORTS,
    )
    graph.add_edge(
        "event-1",
        "event-3",
        EdgeRelation.SEQUENCE,
    )

    result = FailurePropagationAnalyzer().analyze(
        graph,
        "event-1",
    )

    assert result == ("event-2",)


def test_derived_from_edge_does_not_propagate_backward():
    graph = ReasoningGraph()

    inference = unit(
        "event-1",
        PrimitiveType.HYPOTHESIS,
        "Inference",
    )
    evidence = unit(
        "event-2",
        PrimitiveType.OBSERVATION,
        "Evidence",
    )
    later = unit(
        "event-3",
        PrimitiveType.DECISION,
        "Later decision",
    )

    graph.add_node(inference)
    graph.add_node(evidence)
    graph.add_node(later)

    graph.add_edge(
        "event-1",
        "event-2",
        EdgeRelation.DERIVED_FROM,
    )
    graph.add_edge(
        "event-1",
        "event-3",
        EdgeRelation.SEQUENCE,
    )

    result = FailurePropagationAnalyzer().analyze(
        graph,
        "event-1",
    )

    assert result == ()
