from kernel import api


EXPECTED_PUBLIC_SYMBOLS = {
    "DebugFinding",
    "ReasoningDebugger",
    "ReasoningEvent",
    "EventStream",
    "create_event",
    "Edge",
    "EdgeRelation",
    "ReasoningGraph",
    "PrimitiveType",
    "ReasoningUnit",
    "ParserPipeline",
    "ParserPipelineResult",
    "ReasoningTrace",
    "ReasoningTraceEvent",
    "KernelRuntime",
    "KernelSession",
}


def test_public_api_symbol_set_is_stable():
    assert set(api.__all__) == EXPECTED_PUBLIC_SYMBOLS


def test_public_api_order_is_stable():
    assert api.__all__ == [
        "DebugFinding",
        "ReasoningDebugger",
        "ReasoningEvent",
        "EventStream",
        "create_event",
        "Edge",
        "EdgeRelation",
        "ReasoningGraph",
        "PrimitiveType",
        "ReasoningUnit",
        "ParserPipeline",
        "ParserPipelineResult",
        "ReasoningTrace",
        "ReasoningTraceEvent",
        "KernelRuntime",
        "KernelSession",
    ]


def test_public_symbols_are_not_none():
    for name in api.__all__:
        assert getattr(api, name) is not None


def test_public_api_does_not_expose_internal_modules():
    for name in api.__all__:
        value = getattr(api, name)
        module = getattr(value, "__module__", "")

        assert module.startswith("kernel.")
        assert not module.endswith(".bak")
