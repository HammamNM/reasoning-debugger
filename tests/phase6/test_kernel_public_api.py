from kernel.api import (
    DebugFinding,
    ReasoningDebugger,
    ReasoningEvent,
    EventStream,
    Edge,
    EdgeRelation,
    ReasoningGraph,
    PrimitiveType,
    ReasoningUnit,
    ParserPipeline,
    ParserPipelineResult,
    QueryEngine,
    ReasoningTrace,
    ReasoningTraceEvent,
    KernelRuntime,
    KernelSession,
    create_event,
)


def test_public_api_exports_expected_symbols():
    expected = {
        DebugFinding,
        ReasoningDebugger,
        ReasoningEvent,
        EventStream,
        Edge,
        EdgeRelation,
        ReasoningGraph,
        PrimitiveType,
        ReasoningUnit,
        ParserPipeline,
        ParserPipelineResult,
        QueryEngine,
        ReasoningTrace,
        ReasoningTraceEvent,
        KernelRuntime,
        KernelSession,
        create_event,
    }

    from kernel import api

    assert set(api.__all__) == {
        symbol.__name__ for symbol in expected
    }


def test_public_api_symbols_are_importable():
    assert ReasoningGraph is not None
    assert ReasoningUnit is not None
    assert PrimitiveType is not None
    assert KernelRuntime is not None
    assert ParserPipeline is not None
    assert ReasoningDebugger is not None
