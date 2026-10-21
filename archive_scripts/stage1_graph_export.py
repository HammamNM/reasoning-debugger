import os

filepath = 'kernel/api.py'
with open(filepath, 'r', encoding='utf-8') as f:
    code = f.read()

if "def export_trace_to_dot" not in code:
    code += """

def export_trace_to_dot(trace: ReasoningTrace, findings: list = None) -> str:
    \"\"\"Generates a Graphviz DOT string representation of the trace for human verification.\"\"\"
    lines = ["digraph ReasoningTrace {", "  rankdir=TB;", "  node [shape=box, style=filled, fontname=Arial];"]
    
    error_ids = set()
    if findings:
        for f in findings:
            error_ids.update(f.affected_event_ids)
            
    for event in trace.events:
        color = "lightcoral" if event.id in error_ids else "lightblue"
        label = f"[{event.event_type}] {event.id}\\n{event.content[:30]}..."
        label = label.replace('"', '\\"')
        lines.append(f'  "{event.id}" [label="{label}", fillcolor="{color}"];')
        
    for i in range(len(trace.events) - 1):
        source = trace.events[i].id
        target = trace.events[i+1].id
        lines.append(f'  "{source}" -> "{target}" [style=dotted, color=gray];')
        
    lines.append("}")
    return "\\n".join(lines)
"""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(code)

contract_path = 'tests/stage1_diagnostic_closure_contract.py'
with open(contract_path, 'w', encoding='utf-8') as f:
    f.write('''\
from kernel.api import ReasoningDebugger, export_trace_to_dot
from kernel.adapters.swe_agent_adapter import SWEAgentAdapter

def test_stage1_human_verifiable_export():
    trace_path = 'benchmarks/samples/public_real_trace/swe_agent_broken_hallucination.traj'
    trace = SWEAgentAdapter.parse_trajectory(trace_path)
    debugger = ReasoningDebugger()
    findings = debugger.debug(trace)
    
    dot_output = export_trace_to_dot(trace, findings)
    
    assert "digraph ReasoningTrace" in dot_output
    assert "lightcoral" in dot_output, "Failing nodes must be highlighted"
    assert "dotted" in dot_output
''')
