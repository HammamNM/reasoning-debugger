from kernel.parser.parser import Parser
from kernel.parser.target_resolver import TargetResolver
from kernel.models import PrimitiveType, ReasoningUnit


def test_parser_exposes_target_extractor():
    parser = Parser()

    assert parser.target_extractor is not None


def test_parser_and_target_resolver_can_be_composed():
    parser = Parser()
    resolver = TargetResolver()

    units = parser.parse(
        "I suspect ACS. "
        "Observation: troponin is elevated. "
        "I suspect NSTEMI."
    )

    references = parser.target_extractor.extract(
        "This hypothesis is supported."
    )

    target = resolver.resolve(references[0], units)

    assert target is units[-1]
    assert target.primitive == PrimitiveType.HYPOTHESIS


def test_target_resolution_uses_nearest_previous_hypothesis():
    parser = Parser()
    resolver = TargetResolver()

    units = parser.parse(
        "I suspect ACS. "
        "Observation: troponin is elevated. "
        "I suspect NSTEMI."
    )

    references = parser.target_extractor.extract(
        "This hypothesis is supported."
    )

    target = resolver.resolve(references[0], units)

    assert target.content == "I suspect NSTEMI."


def test_unresolved_target_returns_none():
    parser = Parser()
    resolver = TargetResolver()

    units = parser.parse(
        "Observation: chest pain."
    )

    references = parser.target_extractor.extract(
        "This hypothesis is supported."
    )

    target = resolver.resolve(references[0], units)

    assert target is None


def test_parser_does_not_build_graph():
    parser = Parser()

    units = parser.parse(
        "Observation: chest pain. "
        "I suspect ACS."
    )

    assert len(units) == 2
    assert not hasattr(parser, "graph")
    assert not hasattr(parser, "graph_builder")


def test_parser_remains_domain_agnostic():
    parser = Parser()

    units = parser.parse(
        "Observation: chest pain. "
        "I suspect ACS."
    )

    assert all(isinstance(unit, ReasoningUnit) for unit in units)
    assert all(unit.provenance is not None for unit in units)


def test_target_resolution_does_not_mutate_units():
    parser = Parser()
    resolver = TargetResolver()

    units = parser.parse(
        "I suspect ACS. "
        "Observation: troponin is elevated."
    )

    original = [
        (unit.id, unit.primitive, unit.content, unit.provenance)
        for unit in units
    ]

    reference = parser.target_extractor.extract(
        "This hypothesis is supported."
    )[0]

    resolver.resolve(reference, units)

    assert [
        (unit.id, unit.primitive, unit.content, unit.provenance)
        for unit in units
    ] == original
