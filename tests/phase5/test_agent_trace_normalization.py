from api_server import normalize_agent_trace


def test_normalize_agent_trace_common_fields():
    cases = [
        ("thought", "INFERENCE"),
        ("reasoning", "INFERENCE"),
        ("plan", "INFERENCE"),
        ("observation", "OBSERVATION"),
        ("obs", "OBSERVATION"),
        ("output", "OBSERVATION"),
        ("action", "INVESTIGATION"),
        ("tool", "INVESTIGATION"),
        ("query", "INVESTIGATION"),
        ("search", "INVESTIGATION"),
        ("tool_input", "INVESTIGATION"),
    ]

    for field, expected_type in cases:
        result = normalize_agent_trace({
            "steps": [{field: f"test {field}"}]
        })

        assert len(result["events"]) == 1
        assert result["events"][0]["event_type"] == expected_type
        assert result["events"][0]["content"] == f"test {field}"


def test_normalize_agent_trace_preserves_canonical_events():
    data = {
        "events": [{
            "id": "e1",
            "event_type": "THOUGHT",
            "content": "raw thought",
        }]
    }

    assert normalize_agent_trace(data) is data
