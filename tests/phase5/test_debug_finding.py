import pytest

from kernel.debug_finding import DebugFinding


def test_debug_finding_preserves_core_fields():
    finding = DebugFinding(
        event_id="event-7",
        failure_type="unsupported_assumption",
        explanation="The assumption is not supported by the available evidence.",
    )

    assert finding.event_id == "event-7"
    assert finding.failure_type == "unsupported_assumption"
    assert (
        finding.explanation
        == "The assumption is not supported by the available evidence."
    )
    assert finding.affected_event_ids == ()
    assert finding.metadata == {}


def test_debug_finding_exposes_first_failure_event():
    finding = DebugFinding(
        event_id="event-7",
        failure_type="unsupported_assumption",
        explanation="Unsupported assumption.",
    )

    assert finding.first_failure_event_id == "event-7"


def test_debug_finding_preserves_downstream_impact():
    finding = DebugFinding(
        event_id="event-7",
        failure_type="unsupported_assumption",
        explanation="Unsupported assumption.",
        affected_event_ids=("event-9", "event-10", "decision-1"),
    )

    assert finding.downstream_event_ids == (
        "event-9",
        "event-10",
        "decision-1",
    )


def test_debug_finding_accepts_metadata():
    finding = DebugFinding(
        event_id="event-7",
        failure_type="unsupported_assumption",
        explanation="Unsupported assumption.",
        metadata={"source": "detector"},
    )

    assert finding.metadata["source"] == "detector"


def test_debug_finding_rejects_empty_event_id():
    with pytest.raises(TypeError):
        DebugFinding(
            event_id="",
            failure_type="unsupported_assumption",
            explanation="Unsupported assumption.",
        )


def test_debug_finding_rejects_empty_failure_type():
    with pytest.raises(TypeError):
        DebugFinding(
            event_id="event-7",
            failure_type="",
            explanation="Unsupported assumption.",
        )


def test_debug_finding_rejects_empty_explanation():
    with pytest.raises(TypeError):
        DebugFinding(
            event_id="event-7",
            failure_type="unsupported_assumption",
            explanation="",
        )


def test_debug_finding_rejects_non_tuple_downstream_ids():
    with pytest.raises(TypeError):
        DebugFinding(
            event_id="event-7",
            failure_type="unsupported_assumption",
            explanation="Unsupported assumption.",
            affected_event_ids=["event-9"],
        )


def test_debug_finding_rejects_invalid_downstream_ids():
    with pytest.raises(TypeError):
        DebugFinding(
            event_id="event-7",
            failure_type="unsupported_assumption",
            explanation="Unsupported assumption.",
            affected_event_ids=("event-9", ""),
        )


def test_debug_finding_rejects_non_dict_metadata():
    with pytest.raises(TypeError):
        DebugFinding(
            event_id="event-7",
            failure_type="unsupported_assumption",
            explanation="Unsupported assumption.",
            metadata=[],
        )

def test_debug_finding_rejects_field_reassignment():
    finding = DebugFinding(
        event_id="event-7",
        failure_type="unsupported_assumption",
        explanation="Unsupported assumption.",
    )

    with pytest.raises((AttributeError, TypeError)):
        finding.event_id = "event-8"


def test_debug_finding_metadata_is_immutable():
    finding = DebugFinding(
        event_id="event-7",
        failure_type="unsupported_assumption",
        explanation="Unsupported assumption.",
        metadata={"source": "detector"},
    )

    with pytest.raises(TypeError):
        finding.metadata["source"] = "modified"


def test_debug_finding_copies_metadata_on_construction():
    metadata = {"source": "detector"}

    finding = DebugFinding(
        event_id="event-7",
        failure_type="unsupported_assumption",
        explanation="Unsupported assumption.",
        metadata=metadata,
    )

    metadata["source"] = "modified"

    assert finding.metadata["source"] == "detector"
