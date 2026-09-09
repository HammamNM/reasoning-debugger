import kernel.api as api

def test_api_strict_boundary():
    # 1. Verify exact __all__ exposure
    expected_public_api = {
        "ReasoningTrace", 
        "ReasoningTraceEvent", 
        "DebugFinding",
        "PrimitiveType", 
        "ReasoningDebugger",
        "ReasoningKernelError",
        "InvalidTraceSchemaError"
    }
    
    assert hasattr(api, "__all__"), "kernel.api MUST define __all__ to prevent implicit leakage."
    actual_public_api = set(api.__all__)
    
    leakage = actual_public_api - expected_public_api
    missing = expected_public_api - actual_public_api
    
    assert not leakage, f"API Leakage detected! Internal modules exposed: {leakage}"
    assert not missing, f"Missing required Public API elements: {missing}"

    # 2. Explicitly forbid legacy or internal classes in the public namespace
    forbidden_internals = [
        "ParserPipeline", "QueryEngine", "ReasoningGraph", 
        "EventStream", "KernelRuntime", "Edge", "ReasoningUnit"
    ]
    
    for forbidden in forbidden_internals:
        assert not hasattr(api, forbidden), f"Critical Leakage: {forbidden} is accessible via kernel.api"
