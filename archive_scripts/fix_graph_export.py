import os

filepath = 'kernel/api.py'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# إزالة الدالة القديمة وإعادة كتابتها بشكل أقوى
out_lines = []
for line in lines:
    if line.startswith('def export_trace_to_dot'):
        break
    out_lines.append(line)

out_lines.append('''
def export_trace_to_dot(trace, findings: list = None) -> str:
    """Generates a Graphviz DOT string representation of the trace for human verification."""
    lines = ["digraph ReasoningTrace {", "  rankdir=TB;", "  node [shape=box, style=filled, fontname=Arial];"]
    
    error_ids = set()
    if findings:
        for f in findings:
            # تغطية كافة احتمالات أسماء الحقول لضمان التقاط الـ ID
            if hasattr(f, 'first_failure_event_id') and f.first_failure_event_id:
                error_ids.add(f.first_failure_event_id)
            if hasattr(f, 'event_id') and f.event_id:
                error_ids.add(f.event_id)
            if hasattr(f, 'affected_event_ids') and f.affected_event_ids:
                error_ids.update(f.affected_event_ids)
                
    for event in getattr(trace, 'events', []):
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
''')

with open(filepath, 'w', encoding='utf-8') as f:
    f.writelines(out_lines)

print("Graph export function patched successfully.")
