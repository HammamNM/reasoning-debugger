import sys

import kernel.api

from kernel.api import (
    DebugFinding,
    InvalidTraceSchemaError,
    PrimitiveType,
    ReasoningDebugger,
    ReasoningKernelError,
    ReasoningTrace,
    ReasoningTraceEvent,
)


EXPECTED_PUBLIC_API = {
    "ReasoningTrace",
    "ReasoningTraceEvent",
    "DebugFinding",
    "PrimitiveType",
    "ReasoningDebugger",
    "ReasoningKernelError",
    "InvalidTraceSchemaError",
}


def test_public_api_exactly_matches_sdk_contract():
    assert set(kernel.api.__all__) == EXPECTED_PUBLIC_API


def test_public_api_symbols_are_available():
    for symbol in EXPECTED_PUBLIC_API:
        assert hasattr(kernel.api, symbol), (
            f"Missing public API symbol: {symbol}"
        )


def test_public_api_trace_capability_is_usable():
    event = ReasoningTraceEvent(
        id="e1",
        content="Observation",
        event_type="OBSERVATION",
    )

    trace = ReasoningTrace(events=(event,))

    assert len(trace.events) == 1
    assert trace.events[0] is event


def test_public_api_trace_serialization_is_lossless():
    trace = ReasoningTrace(
        events=(
            ReasoningTraceEvent(
                id="e1",
                content="Observation",
                event_type="OBSERVATION",
            ),
        )
    )

    serialized = trace.to_dict()
    restored = ReasoningTrace.from_dict(serialized)

    assert restored.to_dict() == serialized


def test_public_api_debugger_accepts_public_trace():
    trace = ReasoningTrace(
        events=(
            ReasoningTraceEvent(
                id="e1",
                content="Observation.",
                event_type="OBSERVATION",
            ),
        )
    )

    findings = ReasoningDebugger().debug(trace)

    assert isinstance(findings, list)
    assert all(isinstance(item, DebugFinding) for item in findings)


def test_public_api_error_hierarchy_is_stable():
    assert issubclass(InvalidTraceSchemaError, ReasoningKernelError)
    assert issubclass(ReasoningKernelError, Exception)


def test_public_api_does_not_load_application_layers():
    forbidden = {
        "analytics",
        "backend",
        "decision_engine",
        "outcome_engine",
        "simulation",
    }

    loaded_forbidden = [
        mod
        for mod in sys.modules
        if any(
            mod == prefix or mod.startswith(prefix + ".")
            for prefix in forbidden
        )
    ]

    assert not loaded_forbidden, (
        f"Application layers leaked into kernel API: {loaded_forbidden}"
    )


def test_public_api_does_not_expose_internal_symbols():
    forbidden = {
        "ReasoningEvent",
        "EventStream",
        "create_event",
        "Edge",
        "EdgeRelation",
        "ReasoningGraph",
        "ReasoningUnit",
        "ParserPipeline",
        "QueryEngine",
        "KernelRuntime",
        "KernelSession",
    }

    leaked = [
        symbol
        for symbol in forbidden
        if hasattr(kernel.api, symbol)
    ]

    assert leaked == [], (
        f"Internal symbols leaked through kernel.api: {leaked}"
    )
