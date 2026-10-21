import json
from kernel.adapters.swe_agent_adapter import SWEAgentAdapter

# 1. قراءة مسار SWE-agent وتحويله إلى Canonical Schema
trace = SWEAgentAdapter.parse_trajectory('benchmarks/samples/public_real_trace/swe_agent_broken_hallucination.traj')

# 2. تصديره كـ JSON قياسي يمثل ما سيتلقاه الـ CLI في بيئة الإنتاج
with open('test_trace.json', 'w') as f:
    json.dump(trace.to_dict(), f, indent=2)
print("Standard JSON trace generated for CLI testing.")
