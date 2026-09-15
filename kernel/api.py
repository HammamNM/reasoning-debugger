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
    """Generates a Causal Graphviz DOT string representation of the trace."""
    lines = ["digraph ReasoningTrace {", "  rankdir=TB;", "  node [shape=box, style=filled, fontname=Arial, margin=0.2, penwidth=1];"]

    error_ids = set()
    if findings:
        for f in findings:
            if hasattr(f, 'first_failure_event_id') and f.first_failure_event_id:
                error_ids.add(f.first_failure_event_id)
            if hasattr(f, 'event_id') and f.event_id:
                error_ids.add(f.event_id)
            if hasattr(f, 'affected_event_ids') and f.affected_event_ids:
                error_ids.update(f.affected_event_ids)

    # ألوان مخصصة لكل نوع حدث لزيادة وضوح المخطط
    type_colors = {
        "INFERENCE": '"#FFF2CC"',     # أصفر فاتح
        "OBSERVATION": '"#D5E8D4"',   # أخضر فاتح
        "INVESTIGATION": '"#DAE8FC"', # أزرق فاتح
        "ACTION": '"#E1D5E7"',        # بنفسجي فاتح
        "GENERIC_EVENT": '"#F5F5F5"'  # رمادي فاتح
    }

    for event in getattr(trace, 'events', []):
        is_error = event.id in error_ids
        
        # تحديد اللون والإطار
        base_color = type_colors.get(event.event_type.upper(), '"white"')
        color = '"lightcoral"' if is_error else base_color
        border = '"red"' if is_error else '"black"'
        penwidth = "2" if is_error else "1"
        
        # تنظيف النص وتنسيقه بأسلوب HTML-like 
        clean_content = str(event.content).replace('"', "'").replace('\n', ' ')
        short_content = clean_content[:45] + "..." if len(clean_content) > 45 else clean_content
        
        label = f"<<B>{event.event_type}</B><BR/><FONT POINT-SIZE='10'>{event.id}</FONT><BR/><I>{short_content}</I>>"
        
        lines.append(f'  "{event.id}" [label={label}, fillcolor={color}, color={border}, penwidth={penwidth}];')

        # رسم الأسهم السببية (الأساس الهندسي للأداة)
        metadata = getattr(event, 'metadata', {})
        derived_from = metadata.get("derived_from", [])
        
        if derived_from:
            for source_id in derived_from:
                lines.append(f'  "{source_id}" -> "{event.id}" [style=solid, color=black, weight=2];')

    # خطة بديلة: إذا لم يضع العميل أي اعتمادات، نرسم خطوطاً متقطعة حتى لا يبدو المخطط مفككاً
    has_any_links = any(getattr(e, 'metadata', {}).get("derived_from") for e in getattr(trace, 'events', []))
    if not has_any_links:
        for i in range(len(trace.events) - 1):
            source = trace.events[i].id
            target = trace.events[i+1].id
            lines.append(f'  "{source}" -> "{target}" [style=dotted, color=gray];')

    lines.append("}")
    return "\n".join(lines)
