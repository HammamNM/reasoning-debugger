import pytest

from kernel.graph import EdgeRelation, ReasoningGraph
from kernel.models import PrimitiveType, ReasoningUnit
from kernel.structural_failure_detector import StructuralFailureDetector


def make_unit(unit_id, primitive, content):
    return ReasoningUnit(
        id=unit_id,
        primitive=primitive,
        content=content,
    )


def test_unsupported_hypothesis_is_detected():
    graph = ReasoningGraph()

    observation = make_unit(
        "event-1",
        PrimitiveType.OBSERVATION,
        "Observation: chest pain.",
    )

    hypothesis = make_unit(
        "event-2",
        PrimitiveType.HYPOTHESIS,
        "I suspect ACS.",
    )

    graph.add_node(observation)
    graph.add_node(hypothesis)

    findings = StructuralFailureDetector().detect(graph)

    assert len(findings) == 1
    assert findings[0].event_id == "event-2"
    assert findings[0].failure_type == "unsupported_hypothesis"


def test_supported_hypothesis_is_not_detected():
    graph = ReasoningGraph()

    observation = make_unit(
        "event-1",
        PrimitiveType.OBSERVATION,
        "Observation: troponin is elevated.",
    )

    hypothesis = make_unit(
        "event-2",
        PrimitiveType.HYPOTHESIS,
        "I suspect ACS.",
    )

    graph.add_node(observation)
    graph.add_node(hypothesis)

    graph.add_edge(
        observation.id,
        hypothesis.id,
        EdgeRelation.SUPPORTS,
    )

    findings = StructuralFailureDetector().detect(graph)

    assert findings == []


def test_sequence_edge_is_not_treated_as_support():
    graph = ReasoningGraph()

    observation = make_unit(
        "event-1",
        PrimitiveType.OBSERVATION,
        "Observation.",
    )

    hypothesis = make_unit(
        "event-2",
        PrimitiveType.HYPOTHESIS,
        "Hypothesis.",
    )

    graph.add_node(observation)
    graph.add_node(hypothesis)

    graph.add_edge(
        observation.id,
        hypothesis.id,
        EdgeRelation.SEQUENCE,
    )

    findings = StructuralFailureDetector().detect(graph)

    assert len(findings) == 1
    assert findings[0].event_id == "event-2"


def test_multiple_hypotheses_are_evaluated_independently():
    graph = ReasoningGraph()

    observation = make_unit(
        "event-1",
        PrimitiveType.OBSERVATION,
        "Evidence.",
    )

    supported = make_unit(
        "event-2",
        PrimitiveType.HYPOTHESIS,
        "Supported hypothesis.",
    )

    unsupported = make_unit(
        "event-3",
        PrimitiveType.HYPOTHESIS,
        "Unsupported hypothesis.",
    )

    graph.add_node(observation)
    graph.add_node(supported)
    graph.add_node(unsupported)

    graph.add_edge(
        observation.id,
        supported.id,
        EdgeRelation.SUPPORTS,
    )

    findings = StructuralFailureDetector().detect(graph)

    assert len(findings) == 1
    assert findings[0].event_id == "event-3"


def test_detector_does_not_modify_graph():
    graph = ReasoningGraph()

    hypothesis = make_unit(
        "event-1",
        PrimitiveType.HYPOTHESIS,
        "Hypothesis.",
    )

    graph.add_node(hypothesis)

    original_nodes = list(graph.nodes)
    original_edges = list(graph.edges)

    StructuralFailureDetector().detect(graph)

    assert graph.nodes == original_nodes
    assert graph.edges == original_edges


def test_detector_rejects_invalid_graph():
    with pytest.raises(TypeError):
        StructuralFailureDetector().detect(object())
