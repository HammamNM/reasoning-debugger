from kernel.parser.parser import Parser
from kernel.parser.target_resolver import TargetResolver
from kernel.unit_graph_builder import UnitGraphBuilder
from kernel.models import PrimitiveType
from kernel.graph import EdgeRelation


def test_parser_units_can_be_inserted_into_unit_graph():
    parser = Parser()
    builder = UnitGraphBuilder()

    units = parser.parse(
        "Observation: chest pain. I suspect ACS."
    )

    graph = builder.add_units(units)

    assert len(graph.nodes) == 2
    assert graph.nodes[0] is units[0]
    assert graph.nodes[1] is units[1]


def test_parser_preserves_provenance_through_graph_insertion():
    parser = Parser()
    builder = UnitGraphBuilder()

    units = parser.parse(
        "Observation: chest pain."
    )

    builder.add_units(units)

    assert builder.graph.nodes[0].provenance is units[0].provenance
    assert builder.graph.nodes[0].provenance.source == "PARSER"


def test_target_reference_can_resolve_against_parsed_units():
    parser = Parser()
    resolver = TargetResolver()

    units = parser.parse(
        "I suspect ACS."
    )

    reference = parser.target_extractor.extract(
        "This hypothesis is still being considered."
    )[0]

    result = resolver.resolve(reference, units)

    assert result is units[0]
    assert result.primitive == PrimitiveType.HYPOTHESIS


def test_resolved_target_can_be_used_for_explicit_graph_edge():
    parser = Parser()
    resolver = TargetResolver()
    builder = UnitGraphBuilder()

    units = parser.parse(
        "I suspect ACS. "
        "Observation: troponin is elevated."
    )

    builder.add_units(units)

    references = parser.target_extractor.extract(
        "This hypothesis is supported."
    )

    target = resolver.resolve(references[0], units)

    assert target is not None

    evidence = next(
        unit for unit in units
        if unit.primitive == PrimitiveType.OBSERVATION
    )

    edge = builder.add_semantic_edge(
        evidence.id,
        target.id,
        EdgeRelation.SUPPORTS,
    )

    assert edge.source == evidence.id
    assert edge.target == target.id
    assert edge.relation == EdgeRelation.SUPPORTS


def test_integration_does_not_mutate_parsed_units():
    parser = Parser()
    builder = UnitGraphBuilder()

    units = parser.parse(
        "I suspect ACS. Observation: troponin is elevated."
    )

    original = [
        (unit.id, unit.primitive, unit.content, unit.provenance)
        for unit in units
    ]

    builder.add_units(units)

    assert [
        (unit.id, unit.primitive, unit.content, unit.provenance)
        for unit in units
    ] == original
