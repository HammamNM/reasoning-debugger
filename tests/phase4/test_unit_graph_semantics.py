from kernel.models import ReasoningUnit, PrimitiveType
from kernel.graph import EdgeRelation
from kernel.unit_graph_builder import UnitGraphBuilder


def unit(unit_id, primitive, content):
    return ReasoningUnit(
        id=unit_id,
        primitive=primitive,
        content=content,
    )


def test_explicit_support_relation():
    builder = UnitGraphBuilder()

    hypothesis = unit(
        "h1",
        PrimitiveType.HYPOTHESIS,
        "Hypothesis: condition A",
    )

    evidence = unit(
        "e1",
        PrimitiveType.EVIDENCE,
        "Evidence supports the previous hypothesis",
    )

    builder.add_units([hypothesis, evidence])

    edge = builder.add_semantic_edge(
        evidence.id,
        hypothesis.id,
        EdgeRelation.SUPPORTS,
    )

    assert edge.source == evidence.id
    assert edge.target == hypothesis.id
    assert edge.relation == EdgeRelation.SUPPORTS


def test_explicit_contradiction_relation():
    builder = UnitGraphBuilder()

    hypothesis = unit(
        "h1",
        PrimitiveType.HYPOTHESIS,
        "Hypothesis: condition A",
    )

    evidence = unit(
        "e1",
        PrimitiveType.EVIDENCE,
        "Evidence contradicts the previous hypothesis",
    )

    builder.add_units([hypothesis, evidence])

    edge = builder.add_semantic_edge(
        evidence.id,
        hypothesis.id,
        EdgeRelation.CONTRADICTS,
    )

    assert edge.relation == EdgeRelation.CONTRADICTS


def test_confirmation_relation():
    builder = UnitGraphBuilder()

    hypothesis = unit(
        "h1",
        PrimitiveType.HYPOTHESIS,
        "Hypothesis: condition A",
    )

    update = unit(
        "u1",
        PrimitiveType.HYPOTHESIS_UPDATE,
        "Confirm the current hypothesis",
    )

    builder.add_units([hypothesis, update])

    edge = builder.add_semantic_edge(
        update.id,
        hypothesis.id,
        EdgeRelation.CONFIRMS,
    )

    assert edge.source == update.id
    assert edge.target == hypothesis.id
    assert edge.relation == EdgeRelation.CONFIRMS


def test_rejection_relation():
    builder = UnitGraphBuilder()

    hypothesis = unit(
        "h1",
        PrimitiveType.HYPOTHESIS,
        "Hypothesis: condition A",
    )

    update = unit(
        "u1",
        PrimitiveType.HYPOTHESIS_UPDATE,
        "Reject the current hypothesis",
    )

    builder.add_units([hypothesis, update])

    edge = builder.add_semantic_edge(
        update.id,
        hypothesis.id,
        EdgeRelation.REJECTS,
    )

    assert edge.relation == EdgeRelation.REJECTS


def test_derived_from_relation():
    builder = UnitGraphBuilder()

    evidence = unit(
        "e1",
        PrimitiveType.EVIDENCE,
        "Evidence: finding A",
    )

    inference = unit(
        "i1",
        PrimitiveType.INFERENCE,
        "Therefore condition A is likely",
    )

    builder.add_units([evidence, inference])

    edge = builder.add_semantic_edge(
        inference.id,
        evidence.id,
        EdgeRelation.DERIVED_FROM,
    )

    assert edge.source == inference.id
    assert edge.target == evidence.id
    assert edge.relation == EdgeRelation.DERIVED_FROM


def test_semantic_edge_rejects_unknown_source():
    builder = UnitGraphBuilder()

    target = unit(
        "u1",
        PrimitiveType.HYPOTHESIS,
        "Hypothesis",
    )

    builder.add_unit(target)

    try:
        builder.add_semantic_edge(
            "missing",
            target.id,
            EdgeRelation.SUPPORTS,
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")


def test_semantic_edge_rejects_unknown_target():
    builder = UnitGraphBuilder()

    source = unit(
        "u1",
        PrimitiveType.EVIDENCE,
        "Evidence",
    )

    builder.add_unit(source)

    try:
        builder.add_semantic_edge(
            source.id,
            "missing",
            EdgeRelation.SUPPORTS,
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")


def test_semantic_edges_do_not_mutate_units():
    builder = UnitGraphBuilder()

    evidence = unit(
        "e1",
        PrimitiveType.EVIDENCE,
        "Evidence",
    )

    hypothesis = unit(
        "h1",
        PrimitiveType.HYPOTHESIS,
        "Hypothesis",
    )

    builder.add_units([evidence, hypothesis])

    original_evidence = evidence.content
    original_hypothesis = hypothesis.content

    builder.add_semantic_edge(
        evidence.id,
        hypothesis.id,
        EdgeRelation.SUPPORTS,
    )

    assert evidence.content == original_evidence
    assert hypothesis.content == original_hypothesis
