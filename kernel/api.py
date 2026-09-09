from kernel.reasoning_trace import ReasoningTrace, ReasoningTraceEvent
from kernel.debug_finding import DebugFinding
from kernel.models import PrimitiveType
from kernel.debugger import ReasoningDebugger
from kernel.errors import ReasoningKernelError, InvalidTraceSchemaError

__all__ = [
    "ReasoningTrace",
    "ReasoningTraceEvent",
    "DebugFinding",
    "PrimitiveType",
    "ReasoningDebugger",
    "ReasoningKernelError",
    "InvalidTraceSchemaError"
]



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
        label = f"[{event.event_type}] {event.id}\n{event.content[:30]}..."
        label = label.replace('"', '\"')
        lines.append(f'  "{event.id}" [label="{label}", fillcolor="{color}"];')
        
    for i in range(len(trace.events) - 1):
        source = trace.events[i].id
        target = trace.events[i+1].id
        lines.append(f'  "{source}" -> "{target}" [style=dotted, color=gray];')
        
    lines.append("}")
    return "\n".join(lines)
