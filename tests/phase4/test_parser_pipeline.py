from kernel.models import PrimitiveType
from kernel.parser_pipeline import ParserPipeline


def test_pipeline_returns_parsed_units():
    pipeline = ParserPipeline()

    result = pipeline.process(
        "Observation: chest pain. I suspect ACS."
    )

    assert len(result.units) == 2
    assert result.units[0].primitive == PrimitiveType.OBSERVATION
    assert result.units[1].primitive == PrimitiveType.HYPOTHESIS


def test_pipeline_builds_graph_from_parsed_units():
    pipeline = ParserPipeline()

    result = pipeline.process(
        "Observation: chest pain. I suspect ACS."
    )

    assert len(result.graph.nodes) == 2
    assert result.graph.nodes[0] is result.units[0]
    assert result.graph.nodes[1] is result.units[1]


def test_pipeline_extracts_target_references():
    pipeline = ParserPipeline()

    result = pipeline.process(
        "I suspect ACS. "
        "Observation: troponin is elevated."
    )

    assert len(result.references) == 0

    references = pipeline.extract_references(
        "This hypothesis is supported."
    )

    assert len(references) == 1
    assert references[0].kind == "hypothesis"


def test_pipeline_can_resolve_target_against_units():
    pipeline = ParserPipeline()

    result = pipeline.process(
        "I suspect ACS. "
        "Observation: troponin is elevated."
    )

    references = pipeline.extract_references(
        "This hypothesis is supported."
    )

    target = pipeline.resolve_target(
        references[0],
        result.units,
    )

    assert target is result.units[0]
    assert target.primitive == PrimitiveType.HYPOTHESIS


def test_pipeline_exposes_explicit_graph_builder():
    pipeline = ParserPipeline()

    result = pipeline.process(
        "I suspect ACS. "
        "Observation: troponin is elevated."
    )

    assert result.graph is pipeline.graph_builder.graph


def test_pipeline_does_not_mutate_units():
    pipeline = ParserPipeline()

    result = pipeline.process(
        "I suspect ACS. "
        "Observation: troponin is elevated."
    )

    original = [
        (unit.id, unit.primitive, unit.content, unit.provenance)
        for unit in result.units
    ]

    references = pipeline.extract_references(
        "This hypothesis is supported."
    )

    pipeline.resolve_target(
        references[0],
        result.units,
    )

    assert [
        (unit.id, unit.primitive, unit.content, unit.provenance)
        for unit in result.units
    ] == original


def test_pipeline_keeps_graph_construction_structural():
    pipeline = ParserPipeline()

    result = pipeline.process(
        "I suspect ACS. "
        "Observation: troponin is elevated."
    )

    assert len(result.graph.edges) == 1
    assert result.graph.edges[0].relation.value == "SEQUENCE"

def test_pipeline_preserves_graph_across_multiple_process_calls():
    pipeline = ParserPipeline()

    first = pipeline.process(
        "Observation: chest pain. I suspect ACS."
    )

    second = pipeline.process(
        "Observation: troponin is elevated."
    )

    assert first.graph is second.graph
    assert len(second.graph.nodes) == 3
    assert second.graph.nodes[0] is first.units[0]
    assert second.graph.nodes[1] is first.units[1]
    assert second.graph.nodes[2] is second.units[0]


def test_pipeline_sequences_units_across_process_calls():
    pipeline = ParserPipeline()

    first = pipeline.process(
        "I suspect ACS."
    )

    second = pipeline.process(
        "Observation: troponin is elevated."
    )

    assert len(second.graph.edges) == 1
    edge = second.graph.edges[0]

    assert edge.source == first.units[0].id
    assert edge.target == second.units[0].id
    assert edge.relation.value == "SEQUENCE"


def test_pipeline_process_does_not_create_semantic_edges():
    pipeline = ParserPipeline()

    result = pipeline.process(
        "I suspect ACS. "
        "Observation: troponin is elevated."
    )

    assert all(
        edge.relation.value == "SEQUENCE"
        for edge in result.graph.edges
    )

def test_pipeline_process_none_returns_empty_result():
    pipeline = ParserPipeline()

    result = pipeline.process(None)

    assert result.units == []
    assert result.references == []
    assert result.graph is pipeline.graph_builder.graph


def test_pipeline_preserves_unit_identity():
    pipeline = ParserPipeline()

    result = pipeline.process(
        "Observation: chest pain. I suspect ACS."
    )

    assert result.units[0] is result.graph.nodes[0]
    assert result.units[1] is result.graph.nodes[1]


def test_pipeline_does_not_modify_parser_output():
    pipeline = ParserPipeline()

    result = pipeline.process(
        "Observation: chest pain. I suspect ACS."
    )

    original = [
        (unit.id, unit.primitive, unit.content, unit.provenance)
        for unit in result.units
    ]

    pipeline.extract_references(
        "This hypothesis is supported."
    )

    assert [
        (unit.id, unit.primitive, unit.content, unit.provenance)
        for unit in result.units
    ] == original


def test_pipeline_resolution_is_explicit():
    pipeline = ParserPipeline()

    result = pipeline.process(
        "I suspect ACS."
    )

    references = pipeline.extract_references(
        "This hypothesis is supported."
    )

    target = pipeline.resolve_target(
        references[0],
        result.units,
    )

    assert target is result.units[0]


def test_pipeline_does_not_implicitly_resolve_targets():
    pipeline = ParserPipeline()

    result = pipeline.process(
        "I suspect ACS. This hypothesis is supported."
    )

    assert result.references == []


def test_pipeline_does_not_create_semantic_relationships_implicitly():
    pipeline = ParserPipeline()

    result = pipeline.process(
        "I suspect ACS. "
        "Observation: troponin is elevated. "
        "This hypothesis is supported."
    )

    assert all(
        edge.relation.value == "SEQUENCE"
        for edge in result.graph.edges
    )
