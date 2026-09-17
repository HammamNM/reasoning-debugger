from kernel.api import (
    ReasoningTrace,
    ReasoningTraceEvent,
    DebugFinding,
    export_trace_to_dot,
    export_compact_trace_to_dot,
)


def make_trace(count):
    return ReasoningTrace(
        events=tuple(
            ReasoningTraceEvent(
                id=f"e{i}",
                event_type="INVESTIGATION",
                content=f"routine event {i}",
            )
            for i in range(count)
        )
    )


def test_full_export_contract_remains_unchanged():
    trace = make_trace(600)
    dot = export_trace_to_dot(trace, [])

    assert "digraph ReasoningTrace" in dot
    assert '"e0"' in dot
    assert '"e599"' in dot


def test_compact_export_preserves_failure_and_downstream_events():
    trace = make_trace(600)
    finding = DebugFinding(
        event_id="e300",
        failure_type="unsupported_inference",
        explanation="Inference lacks valid evidence.",
        affected_event_ids=("e301", "e302"),
    )

    dot = export_compact_trace_to_dot(trace, [finding])

    assert "digraph ReasoningTrace" in dot
    assert '"e300"' in dot
    assert '"e301"' in dot
    assert '"e302"' in dot
    assert "unsupported_inference" in dot
    assert "routine events" in dot


def test_compact_export_does_not_remove_small_traces():
    trace = make_trace(100)
    dot = export_compact_trace_to_dot(trace, [])

    assert '"e0"' in dot
    assert '"e99"' in dot
    assert "collapsed" not in dot


def test_compact_export_preserves_causal_ancestors():
    events = (
        ReasoningTraceEvent(
            id="e0",
            event_type="OBSERVATION",
            content="important observation",
        ),
        ReasoningTraceEvent(
            id="e1",
            event_type="INFERENCE",
            content="bad inference",
            metadata={"derived_from": ["e0"]},
        ),
    ) + tuple(
        ReasoningTraceEvent(
            id=f"e{i}",
            event_type="INVESTIGATION",
            content=f"routine event {i}",
        )
        for i in range(2, 600)
    )

    trace = ReasoningTrace(events=events)

    finding = DebugFinding(
        event_id="e1",
        failure_type="unsupported_inference",
        explanation="Inference lacks valid evidence.",
    )

    dot = export_compact_trace_to_dot(trace, [finding])

    assert '"e0"' in dot
    assert '"e1"' in dot
    assert '"e0" -> "e1"' in dot


def test_debug_endpoint_uses_compact_renderer_only_for_large_traces(monkeypatch):
    import api_server

    calls = {"full": 0, "compact": 0, "debug_events": 0}

    original_full = api_server.export_trace_to_dot
    original_compact = api_server.export_compact_trace_to_dot

    def full_renderer(trace, findings=None):
        calls["full"] += 1
        return original_full(trace, findings)

    def compact_renderer(trace, findings=None):
        calls["compact"] += 1
        return original_compact(trace, findings)

    class FakeDebugger:
        def debug(self, trace):
            calls["debug_events"] = len(trace.events)
            return [
                DebugFinding(
                    event_id="e300",
                    failure_type="unsupported_inference",
                    explanation="Inference lacks valid evidence.",
                    affected_event_ids=("e301",),
                )
            ]

    monkeypatch.setattr(api_server, "export_trace_to_dot", full_renderer)
    monkeypatch.setattr(api_server, "export_compact_trace_to_dot", compact_renderer)
    monkeypatch.setattr(api_server, "ReasoningDebugger", FakeDebugger)

    client = api_server.app.test_client()

    small_payload = {
        "events": [
            {
                "id": f"e{i}",
                "event_type": "INVESTIGATION",
                "content": f"routine {i}",
            }
            for i in range(100)
        ]
    }

    response = client.post("/debug", json=small_payload)

    assert response.status_code == 200
    assert calls["full"] == 1
    assert calls["compact"] == 0
    assert calls["debug_events"] == 100

    calls["full"] = 0
    calls["compact"] = 0
    calls["debug_events"] = 0

    large_payload = {
        "events": [
            {
                "id": f"e{i}",
                "event_type": "INVESTIGATION",
                "content": f"routine {i}",
            }
            for i in range(600)
        ]
    }

    response = client.post("/debug", json=large_payload)

    assert response.status_code == 200
    assert calls["full"] == 0
    assert calls["compact"] == 1
    assert calls["debug_events"] == 600
