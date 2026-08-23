from kernel.reasoning_graph_builder import (
    ReasoningGraphBuilder
)

from kernel.events import (
    ReasoningEvent
)

from kernel.models import (
    PrimitiveType
)

from kernel.graph import (
    EdgeRelation
)


def test_event_classification():

    builder = ReasoningGraphBuilder()


    observation = ReasoningEvent(

        event_type="ACTION",

        payload={
            "action": "ASK_HISTORY"
        },

        source="TEST"

    )


    investigation = ReasoningEvent(

        event_type="ACTION",

        payload={
            "action": "ORDER_ECG"
        },

        source="TEST"

    )


    hypothesis = ReasoningEvent(

        event_type="ACTION",

        payload={
            "action": "DIAGNOSIS_NSTEMI"
        },

        source="TEST"

    )


    decision = ReasoningEvent(

        event_type="DECISION_ASSESSMENT",

        payload={
            "action": "TREAT_ACS"
        },

        source="TEST"

    )


    outcome = ReasoningEvent(

        event_type="OUTCOME_UPDATED",

        payload={
            "outcome_id": "CORRECT_MANAGEMENT"
        },

        source="TEST"

    )


    assert (
        builder.classify_event(observation)
        == PrimitiveType.OBSERVATION
    )


    assert (
        builder.classify_event(investigation)
        == PrimitiveType.INVESTIGATION
    )


    assert (
        builder.classify_event(hypothesis)
        == PrimitiveType.HYPOTHESIS
    )


    assert (
        builder.classify_event(decision)
        == PrimitiveType.DECISION
    )


    assert (
        builder.classify_event(outcome)
        == PrimitiveType.OUTCOME
    )


def test_nodes_and_sequence_edges():

    builder = ReasoningGraphBuilder()


    first_event = ReasoningEvent(

        event_type="ACTION",

        payload={
            "action": "ASK_HISTORY"
        },

        source="STUDENT"

    )


    second_event = ReasoningEvent(

        event_type="ACTION",

        payload={
            "action": "ORDER_ECG"
        },

        source="STUDENT"

    )


    first_node = (
        builder.process_event(
            first_event
        )
    )


    second_node = (
        builder.process_event(
            second_event
        )
    )


    assert first_node is not None

    assert second_node is not None

    assert len(builder.graph.nodes) == 2

    assert len(builder.graph.edges) == 1


    edge = builder.graph.edges[0]


    assert edge.source == first_node.id

    assert edge.target == second_node.id

    assert edge.relation == EdgeRelation.SEQUENCE


def test_hypothesis_tracking():

    builder = ReasoningGraphBuilder()


    event = ReasoningEvent(

        event_type="ACTION",

        payload={
            "action": "DIAGNOSIS_NSTEMI"
        },

        source="STUDENT"

    )


    node = (
        builder.process_event(
            event
        )
    )


    assert node is not None

    assert (
        node.primitive
        == PrimitiveType.HYPOTHESIS
    )


    assert (
        builder.last_hypothesis_node
        == node.id
    )


    assert (
        builder.hypothesis_nodes[
            "DIAGNOSIS_NSTEMI"
        ]
        == node.id
    )


    found = (
        builder.find_hypothesis_node(
            "DIAGNOSIS_NSTEMI"
        )
    )


    assert found is not None

    assert found.id == node.id


def test_confirmation_and_rejection_edges():

    builder = ReasoningGraphBuilder()


    hypothesis_event = ReasoningEvent(

        event_type="ACTION",

        payload={
            "action": "DIAGNOSIS_NSTEMI"
        },

        source="STUDENT"

    )


    hypothesis_node = (
        builder.process_event(
            hypothesis_event
        )
    )


    confirmation_event = ReasoningEvent(

        event_type="ACTION",

        payload={
            "action": "CONFIRM_DIAGNOSIS_NSTEMI"
        },

        source="TEST"

    )


    confirmation_node = (
        builder.process_event(
            confirmation_event
        )
    )


    assert confirmation_node is not None

    confirmation_edges = [

        edge

        for edge in builder.graph.edges

        if edge.relation
        == EdgeRelation.CONFIRMS

    ]


    assert len(confirmation_edges) == 1

    assert (
        confirmation_edges[0].source
        == confirmation_node.id
    )

    assert (
        confirmation_edges[0].target
        == hypothesis_node.id
    )


    builder = ReasoningGraphBuilder()


    hypothesis_event = ReasoningEvent(

        event_type="ACTION",

        payload={
            "action": "DIAGNOSIS_NSTEMI"
        },

        source="STUDENT"

    )


    hypothesis_node = (
        builder.process_event(
            hypothesis_event
        )
    )


    rejection_event = ReasoningEvent(

        event_type="ACTION",

        payload={
            "action": "REJECT_DIAGNOSIS_NSTEMI"
        },

        source="TEST"

    )


    rejection_node = (
        builder.process_event(
            rejection_event
        )
    )


    assert rejection_node is not None

    rejection_edges = [

        edge

        for edge in builder.graph.edges

        if edge.relation
        == EdgeRelation.REJECTS

    ]


    assert len(rejection_edges) == 1

    assert (
        rejection_edges[0].source
        == rejection_node.id
    )

    assert (
        rejection_edges[0].target
        == hypothesis_node.id
    )


def test_support_and_contradiction_edges():

    builder = ReasoningGraphBuilder()


    hypothesis_event = ReasoningEvent(

        event_type="ACTION",

        payload={
            "action": "DIAGNOSIS_NSTEMI"
        },

        source="STUDENT"

    )


    hypothesis_node = (
        builder.process_event(
            hypothesis_event
        )
    )


    evidence_event = ReasoningEvent(

        event_type="INVESTIGATION_RESULT",

        payload={
            "investigation_id": "TROPONIN",
            "result": {
                "value": 186
            }
        },

        source="INVESTIGATION_ENGINE"

    )


    evidence_node = (
        builder.process_event(
            evidence_event
        )
    )


    builder.connect_support(

        evidence_node.id,

        hypothesis_node.id

    )


    support_edges = [

        edge

        for edge in builder.graph.edges

        if edge.relation
        == EdgeRelation.SUPPORTS

    ]


    assert len(support_edges) == 1

    assert (
        support_edges[0].source
        == evidence_node.id
    )

    assert (
        support_edges[0].target
        == hypothesis_node.id
    )


    builder.connect_contradiction(

        evidence_node.id,

        hypothesis_node.id

    )


    contradiction_edges = [

        edge

        for edge in builder.graph.edges

        if edge.relation
        == EdgeRelation.CONTRADICTS

    ]


    assert len(contradiction_edges) == 1

    assert (
        contradiction_edges[0].source
        == evidence_node.id
    )

    assert (
        contradiction_edges[0].target
        == hypothesis_node.id
    )


def test_provenance_is_preserved():

    builder = ReasoningGraphBuilder()


    event = ReasoningEvent(

        event_type="INVESTIGATION_RESULT",

        payload={
            "investigation_id": "ECG"
        },

        source="INVESTIGATION_ENGINE"

    )


    node = (
        builder.process_event(
            event
        )
    )


    assert node.provenance is not None

    assert (
        node.provenance.source
        == "INVESTIGATION_ENGINE"
    )

    assert (
        node.provenance.event_type
        == "INVESTIGATION_RESULT"
    )


def test_unknown_event_is_ignored():

    builder = ReasoningGraphBuilder()


    event = ReasoningEvent(

        event_type="UNKNOWN_EVENT",

        payload={},

        source="TEST"

    )


    result = (
        builder.process_event(
            event
        )
    )


    assert result is None

    assert len(builder.graph.nodes) == 0

    assert len(builder.graph.edges) == 0


if __name__ == "__main__":

    test_event_classification()

    test_nodes_and_sequence_edges()

    test_hypothesis_tracking()

    test_confirmation_and_rejection_edges()

    test_support_and_contradiction_edges()

    test_provenance_is_preserved()

    test_unknown_event_is_ignored()

    print(
        "REASONING GRAPH TESTS PASSED"
    )

def test_evidence_supports_hypothesis_from_payload():
    builder = ReasoningGraphBuilder()

    hypothesis = builder.process_event(
        ReasoningEvent(
            event_type="ACTION",
            payload={"action": "DIAGNOSIS_NSTEMI"},
            source="STUDENT"
        )
    )

    evidence = builder.process_event(
        ReasoningEvent(
            event_type="EVIDENCE",
            payload={
                "content": "Troponin elevated",
                "supports": ["DIAGNOSIS_NSTEMI"]
            },
            source="INVESTIGATION_ENGINE"
        )
    )

    support_edges = builder.graph.edges_by_relation(
        EdgeRelation.SUPPORTS
    )

    assert len(support_edges) == 1
    assert support_edges[0].source == evidence.id
    assert support_edges[0].target == hypothesis.id


def test_evidence_contradicts_hypothesis_from_payload():
    builder = ReasoningGraphBuilder()

    hypothesis = builder.process_event(
        ReasoningEvent(
            event_type="ACTION",
            payload={"action": "DIAGNOSIS_NSTEMI"},
            source="STUDENT"
        )
    )

    evidence = builder.process_event(
        ReasoningEvent(
            event_type="EVIDENCE",
            payload={
                "content": "Normal serial troponins",
                "contradicts": ["DIAGNOSIS_NSTEMI"]
            },
            source="INVESTIGATION_ENGINE"
        )
    )

    contradiction_edges = builder.graph.edges_by_relation(
        EdgeRelation.CONTRADICTS
    )

    assert len(contradiction_edges) == 1
    assert contradiction_edges[0].source == evidence.id
    assert contradiction_edges[0].target == hypothesis.id
