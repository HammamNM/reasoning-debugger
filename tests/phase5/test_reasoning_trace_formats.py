from kernel.reasoning_trace import ReasoningTrace


def test_reasoning_trace_accepts_common_container_formats():
    for key in ("events", "runs", "trajectory", "steps"):
        trace = ReasoningTrace.from_dict({
            key: [{
                "id": "e1",
                "content": "test",
                "event_type": "OBSERVATION",
            }]
        })

        assert len(trace.events) == 1
        assert trace.events[0].id == "e1"


def test_reasoning_trace_defaults_missing_event_type_to_generic_event():
    trace = ReasoningTrace.from_dict({
        "steps": [{
            "id": "e1",
            "content": "unknown event",
        }]
    })

    assert trace.events[0].event_type == "GENERIC_EVENT"
