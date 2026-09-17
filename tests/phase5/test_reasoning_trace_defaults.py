from kernel.reasoning_trace import ReasoningTrace


def test_missing_smart_defaults_are_conservative():
    trace = ReasoningTrace.from_dict({
        "events": [
            {
                "id": "e1",
                "content": "An inference without explicit support requirement.",
                "event_type": "INFERENCE",
            }
        ]
    })

    event = trace.events[0]

    assert event.metadata["derived_from"] == []
    assert event.metadata["support_required"] is False


def test_explicit_support_required_is_preserved():
    trace = ReasoningTrace.from_dict({
        "events": [
            {
                "id": "e1",
                "content": "An inference explicitly requiring support.",
                "event_type": "INFERENCE",
                "metadata": {
                    "support_required": True,
                    "derived_from": ["e0"],
                },
            }
        ]
    })

    event = trace.events[0]

    assert event.metadata["support_required"] is True
    assert event.metadata["derived_from"] == ["e0"]


def test_explicit_false_support_required_is_preserved():
    trace = ReasoningTrace.from_dict({
        "events": [
            {
                "id": "e1",
                "content": "An inference explicitly not requiring support.",
                "event_type": "INFERENCE",
                "metadata": {
                    "support_required": False,
                },
            }
        ]
    })

    event = trace.events[0]

    assert event.metadata["support_required"] is False
    assert event.metadata["derived_from"] == []
