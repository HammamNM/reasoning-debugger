from kernel.parser.parser import Parser
from kernel.parser.target_resolver import TargetResolver
from kernel.unit_graph_builder import UnitGraphBuilder
from kernel.models import PrimitiveType
from kernel.graph import EdgeRelation


def test_phase47_parser_to_graph_contract():
    parser = Parser()
    resolver = TargetResolver()
    builder = UnitGraphBuilder()

    units = parser.parse(
        "Observation: chest pain. "
        "I suspect ACS. "
        "Observation: troponin is elevated."
    )

    assert len(units) == 3
    assert units[0].primitive == PrimitiveType.OBSERVATION
    assert units[1].primitive == PrimitiveType.HYPOTHESIS
    assert units[2].primitive == PrimitiveType.OBSERVATION

    references = parser.target_extractor.extract(
        "This hypothesis is supported."
    )

    assert len(references) == 1

    target = resolver.resolve(references[0], units)

    assert target is units[1]

    graph = builder.add_units(units)

    assert len(graph.nodes) == 3
    assert graph.nodes[0] is units[0]
    assert graph.nodes[1] is units[1]
    assert graph.nodes[2] is units[2]

    evidence = units[2]

    edge = builder.add_semantic_edge(
        evidence.id,
        target.id,
        EdgeRelation.SUPPORTS,
    )

    assert edge.source == evidence.id
    assert edge.target == target.id
    assert edge.relation == EdgeRelation.SUPPORTS


def test_phase47_integration_preserves_unit_identity_and_provenance():
    parser = Parser()
    resolver = TargetResolver()
    builder = UnitGraphBuilder()

    units = parser.parse(
        "Observation: chest pain. "
        "I suspect ACS."
    )

    original = [
        (id(unit), unit.id, unit.primitive, unit.content, unit.provenance)
        for unit in units
    ]

    references = parser.target_extractor.extract(
        "This hypothesis is being considered."
    )

    target = resolver.resolve(references[0], units)

    builder.add_units(units)

    assert target is units[1]

    assert [
        (id(unit), unit.id, unit.primitive, unit.content, unit.provenance)
        for unit in units
    ] == original


def test_phase47_sequence_edges_are_created_only_by_graph_insertion():
    parser = Parser()
    builder = UnitGraphBuilder()

    units = parser.parse(
        "Observation: chest pain. "
        "I suspect ACS. "
        "Observation: troponin is elevated."
    )

    graph = builder.add_units(units)

    assert len(graph.edges) == 2

    assert all(
        edge.relation == EdgeRelation.SEQUENCE
        for edge in graph.edges
    )


def test_phase47_semantic_edges_are_explicit():
    parser = Parser()
    resolver = TargetResolver()
    builder = UnitGraphBuilder()

    units = parser.parse(
        "I suspect ACS. "
        "Observation: troponin is elevated."
    )

    builder.add_units(units)

    reference = parser.target_extractor.extract(
        "This hypothesis is supported."
    )[0]

    target = resolver.resolve(reference, units)

    evidence = next(
        unit
        for unit in units
        if unit.primitive == PrimitiveType.OBSERVATION
    )

    semantic_edge = builder.add_semantic_edge(
        evidence.id,
        target.id,
        EdgeRelation.SUPPORTS,
    )

    assert semantic_edge.relation == EdgeRelation.SUPPORTS

    sequence_edges = [
        edge
        for edge in builder.graph.edges
        if edge.relation == EdgeRelation.SEQUENCE
    ]

    assert len(sequence_edges) == 1
