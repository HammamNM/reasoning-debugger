import pytest
from kernel.api import ReasoningDebugger

def test_input_contract_rejection():
    # Import the exception locally if it fails at module level initially
    try:
        from kernel.errors import InvalidTraceSchemaError
    except ImportError:
        pytest.fail("kernel.errors.InvalidTraceSchemaError is not implemented yet.")

    debugger = ReasoningDebugger()
    
    # SDK MUST reject raw dictionaries to force canonical Input Model (ReasoningTrace)
    raw_dict_trace = {"events": [{"id": "1", "event_type": "INFERENCE", "content": "test"}]}
    
    with pytest.raises(InvalidTraceSchemaError):
        debugger.debug(raw_dict_trace) # type: ignore
