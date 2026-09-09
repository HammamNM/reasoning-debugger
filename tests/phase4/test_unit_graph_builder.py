import pytest

from kernel.models import ReasoningUnit, PrimitiveType
from kernel.graph import ReasoningGraph, EdgeRelation
from kernel.unit_graph_builder import UnitGraphBuilder


def make_unit(unit_id, primitive=PrimitiveType.OBSERVATION, content="Observation"):
    return ReasoningUnit(
        id=unit_id,
        primitive=primitive,
        content=content,
    )


def test_add_unit_adds_reasoning_unit_to_graph():
    builder = UnitGraphBuilder()
    unit = make_unit("u1")

    result = builder.add_unit(unit)

    assert result is unit
    assert len(builder.graph.nodes) == 1
    assert builder.graph.nodes[0] is unit


def test_add_unit_preserves_unit_identity():
    builder = UnitGraphBuilder()
    unit = make_unit("u1")

    builder.add_unit(unit)

    assert builder.graph.nodes[0] is unit
    assert builder.graph.nodes[0].id == "u1"
    assert builder.graph.nodes[0].content == "Observation"


def test_first_unit_has_no_sequence_edge():
    builder = UnitGraphBuilder()
    builder.add_unit(make_unit("u1"))

    assert builder.graph.edges == []


def test_second_unit_creates_sequence_edge():
    builder = UnitGraphBuilder()

    first = make_unit("u1")
    second = make_unit("u2")

    builder.add_unit(first)
    builder.add_unit(second)

    assert len(builder.graph.edges) == 1
    edge = builder.graph.edges[0]

    assert edge.source == "u1"
    assert edge.target == "u2"
    assert edge.relation == EdgeRelation.SEQUENCE


def test_add_units_preserves_order():
    builder = UnitGraphBuilder()

    units = [
        make_unit("u1"),
        make_unit("u2"),
        make_unit("u3"),
    ]

    graph = builder.add_units(units)

    assert graph is builder.graph
    assert [node.id for node in graph.nodes] == ["u1", "u2", "u3"]

    assert [
        (edge.source, edge.target, edge.relation)
        for edge in graph.edges
    ] == [
        ("u1", "u2", EdgeRelation.SEQUENCE),
        ("u2", "u3", EdgeRelation.SEQUENCE),
    ]


def test_build_is_equivalent_to_add_units():
    units = [
        make_unit("u1"),
        make_unit("u2"),
    ]

    builder = UnitGraphBuilder()

    graph = builder.build(units)

    assert [node.id for node in graph.nodes] == ["u1", "u2"]
    assert len(graph.edges) == 1


def test_non_reasoning_unit_is_rejected():
    builder = UnitGraphBuilder()

    with pytest.raises(TypeError):
        builder.add_unit("not a reasoning unit")


def test_builder_can_use_existing_graph():
    graph = ReasoningGraph()
    builder = UnitGraphBuilder(graph=graph)

    unit = make_unit("u1")

    builder.add_unit(unit)

    assert builder.graph is graph
    assert graph.nodes[0] is unit
