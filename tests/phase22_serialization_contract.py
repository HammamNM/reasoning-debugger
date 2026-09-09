import json
from kernel.api import ReasoningTrace
from kernel.api import ReasoningTraceEvent
from kernel.api import DebugFinding

def test_trace_determinism():
    event = ReasoningTraceEvent(id="evt_1", content="Testing determinism", event_type="INFERENCE")
    trace = ReasoningTrace(events=(event,))
    
    # 1. Must support to_dict()
    assert hasattr(trace, "to_dict"), "ReasoningTrace MUST implement to_dict()"
    
    dict_repr = trace.to_dict()
    
    # 2. Deterministic serialization (sorted keys)
    json1 = json.dumps(dict_repr, sort_keys=True)
    json2 = json.dumps(trace.to_dict(), sort_keys=True)
    
    assert json1 == json2, "Serialization is not deterministic!"
