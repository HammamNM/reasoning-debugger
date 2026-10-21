from kernel.api import ReasoningDebugger
from kernel.adapters.swe_agent_adapter import SWEAgentAdapter

trace_path = 'benchmarks/samples/public_real_trace/swe_agent_broken_hallucination.traj'
trace = SWEAgentAdapter.parse_trajectory(trace_path)
debugger = ReasoningDebugger()
findings = debugger.debug(trace)

print(f"FINDINGS COUNT: {len(findings)}")
for idx, f in enumerate(findings):
    print(f"--- Finding {idx} ---")
    print(f"Type: {type(f).__name__}")
    
    # محاولة جلب كل الحقول الممكنة
    if hasattr(f, '__dataclass_fields__'):
        for field_name in f.__dataclass_fields__:
            print(f" - {field_name}: {getattr(f, field_name)}")
    else:
        print(f" - Dir: {[attr for attr in dir(f) if not attr.startswith('_')]}")
