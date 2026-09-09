from kernel.models import ReasoningUnit, PrimitiveType
from kernel.provenance import ProvenanceRecord
from kernel.graph import ReasoningGraph, EdgeRelation


def test_reasoning_unit_has_required_contract():
    unit = ReasoningUnit(
        id="u1",
        primitive=PrimitiveType.OBSERVATION,
        content="Patient reports chest pain",
    )

    assert unit.id == "u1"
    assert unit.primitive == PrimitiveType.OBSERVATION
    assert unit.content == "Patient reports chest pain"
    assert unit.provenance is None


def test_reasoning_unit_accepts_provenance():
    provenance = ProvenanceRecord(
        source="PARSER",
        event_type="TEXT_SEGMENT",
    )

    unit = ReasoningUnit(
        id="u1",
        primitive=PrimitiveType.OBSERVATION,
        content="Observed finding",
        provenance=provenance,
    )

    assert unit.provenance is provenance
    assert unit.provenance.source == "PARSER"


def test_graph_accepts_reasoning_unit():
    graph = ReasoningGraph()

    unit = ReasoningUnit(
        id="u1",
        primitive=PrimitiveType.OBSERVATION,
        content="Observation",
    )

    graph.add_node(unit)

    assert len(graph.nodes) == 1
    assert graph.nodes[0] is unit


def test_graph_preserves_unit_identity():
    graph = ReasoningGraph()

    first = ReasoningUnit(
        id="u1",
        primitive=PrimitiveType.OBSERVATION,
        content="Observation",
    )

    second = ReasoningUnit(
        id="u2",
        primitive=PrimitiveType.INFERENCE,
        content="Inference",
    )

    graph.add_node(first)
    graph.add_node(second)

    assert graph.nodes[0].id == "u1"
    assert graph.nodes[1].id == "u2"


def test_graph_connects_units_without_mutating_them():
    graph = ReasoningGraph()

    first = ReasoningUnit(
        id="u1",
        primitive=PrimitiveType.OBSERVATION,
        content="Observation",
    )

    second = ReasoningUnit(
        id="u2",
        primitive=PrimitiveType.INFERENCE,
        content="Inference",
    )

    graph.add_node(first)
    graph.add_node(second)

    graph.add_edge(
        first.id,
        second.id,
        EdgeRelation.SEQUENCE,
    )

    assert len(graph.edges) == 1
    assert graph.edges[0].source == "u1"
    assert graph.edges[0].target == "u2"
    assert graph.edges[0].relation == EdgeRelation.SEQUENCE

    assert first.content == "Observation"
    assert second.content == "Inference"


def test_graph_supports_semantic_edge_contract():
    graph = ReasoningGraph()

    evidence = ReasoningUnit(
        id="e1",
        primitive=PrimitiveType.EVIDENCE,
        content="Evidence",
    )

    hypothesis = ReasoningUnit(
        id="h1",
        primitive=PrimitiveType.HYPOTHESIS,
        content="Hypothesis",
    )

    graph.add_node(evidence)
    graph.add_node(hypothesis)

    graph.add_edge(
        evidence.id,
        hypothesis.id,
        EdgeRelation.SUPPORTS,
    )

    edges = graph.edges_by_relation(EdgeRelation.SUPPORTS)

    assert len(edges) == 1
    assert edges[0].source == evidence.id
    assert edges[0].target == hypothesis.id


def test_provenance_survives_graph_insertion():
    graph = ReasoningGraph()

    provenance = ProvenanceRecord(
        source="PARSER",
        event_type="TEXT_SEGMENT",
        metadata={"segment_index": 0},
    )

    unit = ReasoningUnit(
        id="u1",
        primitive=PrimitiveType.OBSERVATION,
        content="Observation",
        provenance=provenance,
    )

    graph.add_node(unit)

    stored = graph.nodes[0]

    assert stored.provenance is provenance
    assert stored.provenance.metadata["segment_index"] == 0
