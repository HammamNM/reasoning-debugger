from kernel.runtime import KernelRuntime
from kernel.events import ReasoningEvent
from kernel.graph import EdgeRelation


def test_runtime_publishes_event():

    runtime = KernelRuntime()

    event = ReasoningEvent(
        event_type="TEST_EVENT",
        payload={
            "value": 1
        },
        source="TEST"
    )

    runtime.publish(event)

    runtime.run_cycle()

    events = runtime.session.event_stream.get_all()

    assert len(events) == 1

    assert events[0].event_type == "TEST_EVENT"

    assert events[0].payload["value"] == 1


def test_runtime_rejects_invalid_event():

    runtime = KernelRuntime()

    try:

        runtime.publish(
            "INVALID_EVENT"
        )

        assert False

    except TypeError:

        assert True


def test_runtime_initialize_without_scenario():

    runtime = KernelRuntime()

    result = runtime.initialize()

    assert result is runtime

    assert runtime.last_report is None

def test_runtime_build_report():
    from backend.session import ClinicalSession
    from kernel.bootstrap import KernelBootstrap

    session = ClinicalSession(
        student_id="student_001",
        scenario_id="RUNTIME_REPORT_TEST_001",
    )

    runtime = KernelBootstrap().create_runtime(session)

    runtime.publish(
        ReasoningEvent(
            event_type="ACTION",
            payload={"action": "DIAGNOSIS_NSTEMI"},
            source="STUDENT",
        )
    )
    runtime.run_cycle()

    runtime.publish(
        ReasoningEvent(
            event_type="EVIDENCE",
            payload={
                "content": "Troponin elevated",
                "supports": ["DIAGNOSIS_NSTEMI"],
                "strength": 1.0,
            },
            source="INVESTIGATION_ENGINE",
        )
    )
    runtime.run_cycle()

    report = runtime.build_report()

    assert report is runtime.last_report
    assert report.session_id == session.session_id

    assert len(report.hypotheses) == 1

    hypothesis = report.hypotheses[0]

    assert hypothesis.name == "DIAGNOSIS_NSTEMI"
    assert hypothesis.confidence == 0.65
    assert hypothesis.status == "ACTIVE"

    assert hypothesis.supporting_evidence == [
        "Troponin elevated"
    ]

    assert len(report.evidence) == 1
    assert report.evidence[0]["content"] == "Troponin elevated"

    assert len(report.reasoning_nodes) > 0
    assert len(report.reasoning_edges) >= 1
    assert len(report.reasoning_path) == len(report.reasoning_nodes)

def test_runtime_full_reasoning_cycle_is_consistent():
    from backend.session import ClinicalSession
    from kernel.bootstrap import KernelBootstrap

    session = ClinicalSession(
        student_id="student_001",
        scenario_id="RUNTIME_FULL_CYCLE_001",
    )

    runtime = KernelBootstrap().create_runtime(session)

    # 1. Student proposes a hypothesis
    runtime.publish(
        ReasoningEvent(
            event_type="ACTION",
            payload={
                "action": "DIAGNOSIS_NSTEMI",
            },
            source="STUDENT",
        )
    )
    runtime.run_cycle()

    state = runtime.session.reasoning_state

    assert len(state.hypotheses) == 1

    hypothesis = state.hypotheses[0]

    assert hypothesis.name == "DIAGNOSIS_NSTEMI"
    assert hypothesis.confidence == 0.50

    # 2. Evidence supports the hypothesis
    runtime.publish(
        ReasoningEvent(
            event_type="EVIDENCE",
            payload={
                "content": "Troponin elevated",
                "supports": ["DIAGNOSIS_NSTEMI"],
                "strength": 1.0,
            },
            source="INVESTIGATION_ENGINE",
        )
    )
    runtime.run_cycle()

    # 3. State must contain the evidence effect
    assert hypothesis.confidence == 0.65
    assert len(hypothesis.supporting_evidence) == 1
    assert hypothesis.supporting_evidence[0].content == "Troponin elevated"

    # 4. Session evidence must contain the same evidence
    assert hasattr(runtime.session, "evidence")
    assert len(runtime.session.evidence) == 1

    evidence = runtime.session.evidence[0]

    assert evidence.content == "Troponin elevated"
    assert evidence.source == "INVESTIGATION_ENGINE"
    assert "DIAGNOSIS_NSTEMI" in evidence.supports

    # 5. Graph must contain the support relation
    support_edges = [
        edge
        for edge in runtime.graph_builder.graph.edges
        if edge.relation == EdgeRelation.SUPPORTS
    ]

    assert len(support_edges) == 1

    # 6. Report must reflect the same state
    report = runtime.build_report()

    assert len(report.hypotheses) == 1

    report_hypothesis = report.hypotheses[0]

    assert report_hypothesis.name == "DIAGNOSIS_NSTEMI"
    assert report_hypothesis.confidence == 0.65

    assert report_hypothesis.supporting_evidence == [
        "Troponin elevated"
    ]

    assert len(report.evidence) == 1
    assert report.evidence[0]["content"] == "Troponin elevated"

    assert any(
        edge["relation"] == "SUPPORTS"
        for edge in report.reasoning_edges
    )

def test_runtime_full_reasoning_report_with_support_and_contradiction():
    from backend.session import ClinicalSession
    from kernel.bootstrap import KernelBootstrap
    from kernel.events import ReasoningEvent

    session = ClinicalSession(
        student_id="student_001",
        scenario_id="RUNTIME_FULL_REPORT_001",
    )

    runtime = KernelBootstrap().create_runtime(session)

    # 1. Student proposes hypothesis
    runtime.publish(
        ReasoningEvent(
            event_type="ACTION",
            payload={"action": "DIAGNOSIS_NSTEMI"},
            source="STUDENT",
        )
    )
    runtime.run_cycle()

    # 2. Supporting evidence
    runtime.publish(
        ReasoningEvent(
            event_type="EVIDENCE",
            payload={
                "content": "Troponin elevated",
                "supports": ["DIAGNOSIS_NSTEMI"],
                "strength": 1.0,
            },
            source="INVESTIGATION_ENGINE",
        )
    )
    runtime.run_cycle()

    # 3. Contradicting evidence
    runtime.publish(
        ReasoningEvent(
            event_type="EVIDENCE",
            payload={
                "content": "Alternative finding",
                "contradicts": ["DIAGNOSIS_NSTEMI"],
                "strength": 1.0,
            },
            source="INVESTIGATION_ENGINE",
        )
    )
    runtime.run_cycle()

    # 4. Build final report
    report = runtime.build_report()

    # Hypothesis state
    assert len(report.hypotheses) == 1

    hypothesis = report.hypotheses[0]

    assert hypothesis.name == "DIAGNOSIS_NSTEMI"
    assert hypothesis.confidence == 0.45
    assert hypothesis.status == "ACTIVE"

    # Evidence reflected in report
    assert hypothesis.supporting_evidence == [
        "Troponin elevated"
    ]

    assert hypothesis.contradicting_evidence == [
        "Alternative finding"
    ]

    # Confidence history
    assert len(hypothesis.confidence_history) == 2

    assert hypothesis.confidence_history[0]["previous"] == 0.50
    assert hypothesis.confidence_history[0]["change"] == 0.15
    assert hypothesis.confidence_history[0]["current"] == 0.65
    assert hypothesis.confidence_history[0]["reason"] == "SUPPORTING_EVIDENCE"

    assert hypothesis.confidence_history[1]["previous"] == 0.65
    assert hypothesis.confidence_history[1]["change"] == -0.20
    assert hypothesis.confidence_history[1]["current"] == 0.45
    assert hypothesis.confidence_history[1]["reason"] == "CONTRADICTING_EVIDENCE"

    # Evidence collection
    assert len(report.evidence) == 2

    contents = {
        evidence["content"]
        for evidence in report.evidence
    }

    assert contents == {
        "Troponin elevated",
        "Alternative finding",
    }

    # Graph consistency
    relations = {
        edge["relation"]
        for edge in report.reasoning_edges
    }

    assert "SUPPORTS" in relations
    assert "CONTRADICTS" in relations

    # Report path must correspond to graph nodes
    assert len(report.reasoning_path) == len(report.reasoning_nodes)

def test_runtime_report_reflects_confirm_and_reject_edges():
    from backend.session import ClinicalSession
    from kernel.bootstrap import KernelBootstrap
    from kernel.events import ReasoningEvent
    from kernel.graph import EdgeRelation

    session = ClinicalSession(
        student_id="student_001",
        scenario_id="RUNTIME_CONFIRM_REJECT_001",
    )

    runtime = KernelBootstrap().create_runtime(session)

    runtime.publish(
        ReasoningEvent(
            event_type="ACTION",
            payload={"action": "DIAGNOSIS_NSTEMI"},
            source="STUDENT",
        )
    )
    runtime.run_cycle()

    hypothesis_node = next(
        node
        for node in runtime.graph_builder.graph.nodes
        if node.primitive.value == "HYPOTHESIS"
    )

    graph = runtime.graph_builder.graph

    graph.add_edge(
        hypothesis_node.id,
        hypothesis_node.id,
        EdgeRelation.CONFIRMS,
    )

    graph.add_edge(
        hypothesis_node.id,
        hypothesis_node.id,
        EdgeRelation.REJECTS,
    )

    report = runtime.build_report()

    assert hypothesis_node.id in report.confirmed_hypotheses
    assert hypothesis_node.id in report.rejected_hypotheses

    assert any(
        edge["relation"] == "CONFIRMS"
        for edge in report.reasoning_edges
    )

    assert any(
        edge["relation"] == "REJECTS"
        for edge in report.reasoning_edges
    )
