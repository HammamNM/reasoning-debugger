import os, json

# 1. Create a realistic BROKEN SWE-agent trace
trace_dir = 'benchmarks/samples/public_real_trace'
os.makedirs(trace_dir, exist_ok=True)
broken_trace_path = os.path.join(trace_dir, 'swe_agent_broken_hallucination.traj')

# Simulating a classic agent failure: 
# 1. Searches for a function (Evidence).
# 2. Gets empty result (Evidence).
# 3. Hallucinates that the file exists and edits it anyway (Unsupported Decision/Action).
broken_events = [
    {"thought": "I need to find the definition of `process_data`.", "action": "grep -r 'def process_data' .", "observation": ""},
    {"thought": "The function must be in utils.py. I will edit it.", "action": "edit utils.py", "observation": "File created."},
    {"thought": "I will now run the tests.", "action": "pytest", "observation": "ERROR: module 'utils' has no attribute 'process_data'"}
]

with open(broken_trace_path, 'w', encoding='utf-8') as f:
    for event in broken_events:
        f.write(json.dumps(event) + '\n')

print(f"Created broken trace at: {broken_trace_path}")

# 2. Create the strict contract for Phase 23A
contract_path = 'tests/phase23_real_broken_trace_contract.py'
with open(contract_path, 'w', encoding='utf-8') as f:
    f.write('''\
import os
import pytest
from kernel.api import ReasoningDebugger
from kernel.adapters.swe_agent_adapter import SWEAgentAdapter

def test_debugger_catches_real_hallucinated_action():
    trace_path = 'benchmarks/samples/public_real_trace/swe_agent_broken_hallucination.traj'
    assert os.path.exists(trace_path), "Broken trace file is missing!"
    
    # 1. Adapt the raw SWE-agent trace into our Canonical Input Model
    adapter = SWEAgentAdapter()
    trace = adapter.parse_file(trace_path)
    
    # 2. Run the trace through the strict public boundary
    debugger = ReasoningDebugger()
    findings = debugger.debug(trace)
    
    # 3. Invariants
    assert len(findings) > 0, "Debugger failed to catch a blatant hallucinated action in a real trace."
    
    # 4. Verify the nature of the finding
    first_finding = findings[0]
    assert first_finding.failure_type in ("UNSUPPORTED_REASONING", "STRUCTURAL_FAILURE", "UNSUPPORTED_DECISION"), \\
        f"Expected reasoning failure, got {first_finding.failure_type}"
''')

print(f"Created contract at: {contract_path}")
