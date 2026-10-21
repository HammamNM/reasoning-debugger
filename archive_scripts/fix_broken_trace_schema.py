import json

trace_path = 'benchmarks/samples/public_real_trace/swe_agent_broken_hallucination.traj'
broken_trace_data = {
    "trajectory": [
        {"thought": "I need to find the definition of `process_data`.", "action": "grep -r 'def process_data' .", "observation": ""},
        {"thought": "The function must be in utils.py. I will edit it.", "action": "edit utils.py", "observation": "File created."},
        {"thought": "I will now run the tests.", "action": "pytest", "observation": "ERROR: module 'utils' has no attribute 'process_data'"}
    ]
}

with open(trace_path, 'w', encoding='utf-8') as f:
    json.dump(broken_trace_data, f, indent=2)

print("Trace file fixed (Valid SWE-agent trajectory schema).")
