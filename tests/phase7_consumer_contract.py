from kernel.api import (
    DebugFinding,
    InvalidTraceSchemaError,
    PrimitiveType,
    ReasoningDebugger,
    ReasoningKernelError,
    ReasoningTrace,
    ReasoningTraceEvent,
)


def test_external_consumer_can_construct_public_trace():
    trace = ReasoningTrace(
        events=(
            ReasoningTraceEvent(
                "event-1",
                "Observation.",
                "OBSERVATION",
            ),
        )
    )

    assert len(trace.events) == 1
    assert trace.events[0].id == "event-1"


def test_external_consumer_can_use_public_primitive_types():
    assert PrimitiveType.OBSERVATION.name == "OBSERVATION"
    assert PrimitiveType.INFERENCE.name == "INFERENCE"


def test_external_consumer_can_use_debugger():
    trace = ReasoningTrace(
        events=(
            ReasoningTraceEvent(
                "event-1",
                "Observation.",
                "OBSERVATION",
            ),
        )
    )

    result = ReasoningDebugger().debug(trace)

    assert isinstance(result, list)
    assert all(isinstance(item, DebugFinding) for item in result)


def test_external_consumer_can_roundtrip_trace():
    trace = ReasoningTrace(
        events=(
            ReasoningTraceEvent(
                "event-1",
                "Observation.",
                "OBSERVATION",
            ),
        )
    )

    restored = ReasoningTrace.from_dict(trace.to_dict())

    assert restored.to_dict() == trace.to_dict()


def test_public_error_types_are_constructible():
    assert issubclass(InvalidTraceSchemaError, ReasoningKernelError)
    assert issubclass(ReasoningKernelError, Exception)
