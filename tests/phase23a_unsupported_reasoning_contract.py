from kernel.api import (
    DebugFinding,
    ReasoningTrace,
    ReasoningTraceEvent,
)
from kernel.trace_graph_adapter import TraceGraphAdapter
from kernel.failure_propagation import FailurePropagationAnalyzer
from kernel.graph import EdgeRelation


def build_unsupported_trace():
    return ReasoningTrace(
        events=(
            ReasoningTraceEvent(
                id="evidence-1",
                content="Search returned no definition of process_data.",
                event_type="EVIDENCE",
                metadata={},
            ),
            ReasoningTraceEvent(
                id="inference-1",
                content="The function must be in utils.py.",
                event_type="INFERENCE",
                metadata={"support_required": True},
            ),
            ReasoningTraceEvent(
                id="action-1",
                content="edit utils.py",
                event_type="INVESTIGATION",
                metadata={
                    "derived_from": ["inference-1"],
                },
            ),
        )
    )


def test_causal_dependency_is_explicit_and_not_temporal():
    trace = build_unsupported_trace()

    graph = TraceGraphAdapter().build(trace)

    derived_edges = [
        edge
        for edge in graph.edges
        if edge.relation == EdgeRelation.DERIVED_FROM
    ]

    assert len(derived_edges) == 1

    edge = derived_edges[0]

    assert edge.source == "action-1"
    assert edge.target == "inference-1"


def test_temporal_sequence_is_not_treated_as_causal_dependency():
    trace = build_unsupported_trace()

    graph = TraceGraphAdapter().build(trace)

    propagation = FailurePropagationAnalyzer()

    affected = propagation.analyze(
        graph,
        "inference-1",
    )

    assert "action-1" in affected


def test_unsupported_inference_is_not_supported_by_temporal_order():
    trace = ReasoningTrace(
        events=(
            ReasoningTraceEvent(
                id="evidence-1",
                content="Search returned no definition of process_data.",
                event_type="EVIDENCE",
                metadata={},
            ),
            ReasoningTraceEvent(
                id="inference-1",
                content="The function must be in utils.py.",
                event_type="INFERENCE",
                metadata={"support_required": True},
            ),
            ReasoningTraceEvent(
                id="action-1",
                content="edit utils.py",
                event_type="INVESTIGATION",
                metadata={
                    "derived_from": ["inference-1"],
                },
            ),
        )
    )

    graph = TraceGraphAdapter().build(trace)

    from kernel.unsupported_inference_detector import UnsupportedInferenceDetector

    findings = UnsupportedInferenceDetector().detect(graph)

    assert len(findings) == 1
    assert findings[0].event_id == "inference-1"
    assert findings[0].failure_type == "unsupported_inference"

    propagation = FailurePropagationAnalyzer()
    assert propagation.analyze(graph, "inference-1") == ("action-1",)


def test_supported_inference_has_explicit_evidence_provenance():
    trace = ReasoningTrace(
        events=(
            ReasoningTraceEvent(
                id="evidence-1",
                content="Search identified process_data in utils.py.",
                event_type="EVIDENCE",
                metadata={},
            ),
            ReasoningTraceEvent(
                id="inference-1",
                content="The function is in utils.py.",
                event_type="INFERENCE",
                metadata={
                    "derived_from": ["evidence-1"],
                },
            ),
            ReasoningTraceEvent(
                id="action-1",
                content="edit utils.py",
                event_type="INVESTIGATION",
                metadata={
                    "derived_from": ["inference-1"],
                },
            ),
        )
    )

    graph = TraceGraphAdapter().build(trace)

    derived_edges = [
        edge
        for edge in graph.edges
        if edge.relation == EdgeRelation.DERIVED_FROM
    ]

    assert ("inference-1", "evidence-1") in {
        (edge.source, edge.target)
        for edge in derived_edges
    }

    assert ("action-1", "inference-1") in {
        (edge.source, edge.target)
        for edge in derived_edges
    }


def test_unsupported_inference_detector_finds_first_unsupported_inference():
    from kernel.unsupported_inference_detector import UnsupportedInferenceDetector

    trace = ReasoningTrace(
        events=(
            ReasoningTraceEvent(
                id="evidence-1",
                content="Search returned no definition of process_data.",
                event_type="EVIDENCE",
                metadata={},
            ),
            ReasoningTraceEvent(
                id="inference-1",
                content="The function must be in utils.py.",
                event_type="INFERENCE",
                metadata={"support_required": True},
            ),
            ReasoningTraceEvent(
                id="action-1",
                content="edit utils.py",
                event_type="INVESTIGATION",
                metadata={
                    "derived_from": ["inference-1"],
                },
            ),
        )
    )

    graph = TraceGraphAdapter().build(trace)

    findings = UnsupportedInferenceDetector().detect(graph)

    assert len(findings) == 1
    assert findings[0].event_id == "inference-1"
    assert findings[0].failure_type == "unsupported_inference"
    assert findings[0].affected_event_ids == ()


def test_unsupported_inference_detector_ignores_temporal_sequence():
    from kernel.unsupported_inference_detector import UnsupportedInferenceDetector

    trace = ReasoningTrace(
        events=(
            ReasoningTraceEvent(
                id="evidence-1",
                content="The search found process_data in utils.py.",
                event_type="EVIDENCE",
                metadata={},
            ),
            ReasoningTraceEvent(
                id="inference-1",
                content="The function is in utils.py.",
                event_type="INFERENCE",
                metadata={"support_required": True},
            ),
        )
    )

    graph = TraceGraphAdapter().build(trace)

    findings = UnsupportedInferenceDetector().detect(graph)

    assert len(findings) == 1
    assert findings[0].event_id == "inference-1"


def test_unsupported_inference_detector_accepts_explicit_evidence_support():
    from kernel.unsupported_inference_detector import UnsupportedInferenceDetector

    trace = ReasoningTrace(
        events=(
            ReasoningTraceEvent(
                id="evidence-1",
                content="The search found process_data in utils.py.",
                event_type="EVIDENCE",
                metadata={},
            ),
            ReasoningTraceEvent(
                id="inference-1",
                content="The function is in utils.py.",
                event_type="INFERENCE",
                metadata={
                    "support_required": True,
                    "derived_from": ["evidence-1"],
                },
            ),
        )
    )

    graph = TraceGraphAdapter().build(trace)

    findings = UnsupportedInferenceDetector().detect(graph)

    assert findings == []


def test_unsupported_inference_detector_stops_at_first_failure():
    from kernel.unsupported_inference_detector import UnsupportedInferenceDetector

    trace = ReasoningTrace(
        events=(
            ReasoningTraceEvent(
                id="inference-1",
                content="Unsupported inference one.",
                event_type="INFERENCE",
                metadata={"support_required": True},
            ),
            ReasoningTraceEvent(
                id="inference-2",
                content="Unsupported inference two.",
                event_type="INFERENCE",
                metadata={},
            ),
        )
    )

    graph = TraceGraphAdapter().build(trace)

    findings = UnsupportedInferenceDetector().detect(graph)

    assert len(findings) == 1
    assert findings[0].event_id == "inference-1"


def test_debugger_reports_unsupported_inference_and_propagates_to_dependent_action():
    from kernel.api import ReasoningDebugger

    trace = ReasoningTrace(
        events=(
            ReasoningTraceEvent(
                id="evidence-1",
                content="Search returned no definition of process_data.",
                event_type="EVIDENCE",
                metadata={},
            ),
            ReasoningTraceEvent(
                id="inference-1",
                content="The function must be in utils.py.",
                event_type="INFERENCE",
                metadata={"support_required": True},
            ),
            ReasoningTraceEvent(
                id="action-1",
                content="edit utils.py",
                event_type="INVESTIGATION",
                metadata={
                    "derived_from": ["inference-1"],
                },
            ),
        )
    )

    findings = ReasoningDebugger().debug(trace)

    assert len(findings) >= 1

    failure = next(
        finding
        for finding in findings
        if finding.event_id == "inference-1"
    )

    assert failure.failure_type == "unsupported_inference"
    assert "action-1" in failure.affected_event_ids


def test_debugger_does_not_treat_temporal_order_as_causal_support():
    from kernel.api import ReasoningDebugger

    trace = ReasoningTrace(
        events=(
            ReasoningTraceEvent(
                id="evidence-1",
                content="Search returned no definition of process_data.",
                event_type="EVIDENCE",
                metadata={},
            ),
            ReasoningTraceEvent(
                id="inference-1",
                content="The function must be in utils.py.",
                event_type="INFERENCE",
                metadata={"support_required": True},
            ),
            ReasoningTraceEvent(
                id="unrelated-1",
                content="An unrelated later operation.",
                event_type="INVESTIGATION",
                metadata={},
            ),
        )
    )

    findings = ReasoningDebugger().debug(trace)

    failure = next(
        (
            finding
            for finding in findings
            if finding.event_id == "inference-1"
        ),
        None,
    )

    assert failure is not None
    assert failure.failure_type == "unsupported_inference"
    assert "unrelated-1" not in failure.affected_event_ids


def test_real_swe_agent_trace_does_not_fail_only_from_missing_provenance():
    from kernel.api import ReasoningDebugger
    from kernel.adapters.swe_agent_adapter import SWEAgentAdapter

    path = "benchmarks/samples/public_real_trace/swe_agent_marshmallow.traj"

    trace = SWEAgentAdapter.parse_trajectory(path)
    findings = ReasoningDebugger().debug(trace)

    unsupported = [
        finding
        for finding in findings
        if finding.failure_type == "unsupported_inference"
    ]

    assert unsupported == []
