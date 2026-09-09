import pytest

from kernel.api import KernelRuntime, KernelSession, ReasoningEvent


class ExternalEngine:
    def __init__(self):
        self.received = []

    def process_event(self, event, session):
        self.received.append((event, session))

        if event.event_type != "INPUT_EVENT":
            return None

        return ReasoningEvent(
            event_type="ENGINE_RESULT",
            payload={"source_event": event.event_type},
            source="EXTERNAL_ENGINE",
        )


def test_runtime_is_constructible_from_public_api():
    session = KernelSession()
    runtime = KernelRuntime(session)

    assert isinstance(runtime, KernelRuntime)
    assert runtime.session is session


def test_runtime_accepts_public_reasoning_event():
    runtime = KernelRuntime()

    event = ReasoningEvent(
        event_type="TEST_EVENT",
        payload={"value": 42},
        source="EXTERNAL_CONSUMER",
    )

    runtime.publish(event)
    runtime.run_cycle()

    events = runtime.session.event_stream.get_all()

    assert len(events) == 1
    assert events[0] is event


def test_runtime_rejects_non_reasoning_event():
    runtime = KernelRuntime()

    with pytest.raises(TypeError):
        runtime.publish(
            {
                "event_type": "INVALID",
                "payload": {},
            }
        )


def test_external_engine_can_be_registered_through_runtime_boundary():
    runtime = KernelRuntime()
    engine = ExternalEngine()

    runtime.register_engine(engine)

    assert engine in runtime.registry.get_engines()


def test_registered_external_engine_receives_events():
    runtime = KernelRuntime()
    engine = ExternalEngine()

    runtime.register_engine(engine)

    event = ReasoningEvent(
        event_type="INPUT_EVENT",
        payload={"value": 1},
        source="EXTERNAL_CONSUMER",
    )

    runtime.publish(event)
    runtime.run_cycle()

    assert len(engine.received) == 2

    received_event, received_session = engine.received[0]

    assert received_event is event
    assert received_session is runtime.session

    generated_event, generated_session = engine.received[1]

    assert generated_event.event_type == "ENGINE_RESULT"
    assert generated_session is runtime.session


def test_engine_generated_events_reenter_runtime_pipeline():
    runtime = KernelRuntime()
    engine = ExternalEngine()

    runtime.register_engine(engine)

    runtime.publish(
        ReasoningEvent(
            event_type="INPUT_EVENT",
            payload={},
            source="EXTERNAL_CONSUMER",
        )
    )

    runtime.run_cycle()

    events = runtime.session.event_stream.get_all()

    assert [event.event_type for event in events] == [
        "INPUT_EVENT",
        "ENGINE_RESULT",
    ]

    generated = events[1]

    assert generated.source == "EXTERNAL_ENGINE"
    assert generated.payload["source_event"] == "INPUT_EVENT"


def test_runtime_does_not_require_external_engine_to_know_kernel_internals():
    runtime = KernelRuntime()
    engine = ExternalEngine()

    runtime.register_engine(engine)

    runtime.publish(
        ReasoningEvent(
            event_type="BOUNDARY_TEST",
            payload={},
            source="EXTERNAL_CONSUMER",
        )
    )

    runtime.run_cycle()

    assert engine.received[0][1] is runtime.session


def test_runtime_session_is_kernel_session_by_default():
    runtime = KernelRuntime()

    assert isinstance(runtime.session, KernelSession)


def test_runtime_initialize_returns_runtime():
    runtime = KernelRuntime()

    result = runtime.initialize()

    assert result is runtime


def test_runtime_processes_generated_events_until_queue_is_empty():
    class ChainedEngine:
        def __init__(self):
            self.count = 0

        def process_event(self, event, session):
            if event.event_type == "START":
                self.count += 1

                return ReasoningEvent(
                    event_type="SECOND",
                    payload={},
                    source="CHAIN_ENGINE",
                )

            return None

    runtime = KernelRuntime()
    engine = ChainedEngine()

    runtime.register_engine(engine)

    runtime.publish(
        ReasoningEvent(
            event_type="START",
            payload={},
            source="EXTERNAL",
        )
    )

    runtime.run_cycle()

    events = runtime.session.event_stream.get_all()

    assert [event.event_type for event in events] == [
        "START",
        "SECOND",
    ]

    assert engine.count == 1
