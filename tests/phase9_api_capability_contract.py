from kernel import api


EXPECTED_PUBLIC_API = {
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

    "QueryEngine",

    "ReasoningTrace",
    "ReasoningTraceEvent",

    "KernelRuntime",
    "KernelSession",
}


def test_public_api_matches_kernel_capability_contract():
    assert set(api.__all__) == EXPECTED_PUBLIC_API


def test_public_api_contains_reasoning_model_capabilities():
    required = {
        "PrimitiveType",
        "ReasoningUnit",
        "ReasoningGraph",
        "Edge",
        "EdgeRelation",
    }

    assert required <= set(api.__all__)


def test_public_api_contains_event_capabilities():
    required = {
        "ReasoningEvent",
        "EventStream",
        "create_event",
    }

    assert required <= set(api.__all__)


def test_public_api_contains_parser_capabilities():
    required = {
        "ParserPipeline",
        "ParserPipelineResult",
    }

    assert required <= set(api.__all__)


def test_public_api_contains_query_capability():
    assert "QueryEngine" in api.__all__


def test_public_api_contains_debugging_capabilities():
    required = {
        "ReasoningTrace",
        "ReasoningTraceEvent",
        "DebugFinding",
        "ReasoningDebugger",
    }

    assert required <= set(api.__all__)


def test_public_api_contains_runtime_capabilities():
    required = {
        "KernelRuntime",
        "KernelSession",
    }

    assert required <= set(api.__all__)
