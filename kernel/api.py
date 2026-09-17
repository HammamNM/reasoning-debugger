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
    "InvalidTraceSchemaError",
    "export_compact_trace_to_dot"
]

def export_compact_trace_to_dot(trace, findings: list = None) -> str:
    """Generates a compact causal graph for large traces without changing analysis."""
    events = list(getattr(trace, "events", []))
    findings = findings or []

    if len(events) <= 500:
        return export_trace_to_dot(trace, findings)

    event_by_id = {event.id: event for event in events}
    important_ids = set()

    for finding in findings:
        if getattr(finding, "event_id", None):
            important_ids.add(finding.event_id)
        important_ids.update(getattr(finding, "affected_event_ids", ()) or ())

    # Preserve causal ancestors of important events.
    pending = list(important_ids)
    while pending:
        event_id = pending.pop()
        event = event_by_id.get(event_id)
        if not event:
            continue

        for source_id in getattr(event, "metadata", {}).get("derived_from", []) or []:
            if source_id in event_by_id and source_id not in important_ids:
                important_ids.add(source_id)
                pending.append(source_id)

    important_positions = sorted(
        i for i, event in enumerate(events) if event.id in important_ids
    )

    keep_indices = set(important_positions)

    # Keep a small chronological context around important events.
    for position in important_positions:
        for offset in (-2, -1, 0, 1, 2):
            index = position + offset
            if 0 <= index < len(events):
                keep_indices.add(index)

    lines = [
        "digraph ReasoningTrace {",
        "  rankdir=TB;",
        '  node [shape=box, style=filled, fontname=Arial, margin=0.2, penwidth=1];',
    ]

    error_ids = set()
    for finding in findings:
        if getattr(finding, "event_id", None):
            error_ids.add(finding.event_id)
        error_ids.update(getattr(finding, "affected_event_ids", ()) or ())

    type_colors = {
        "INFERENCE": '"#FFF2CC"',
        "OBSERVATION": '"#D5E8D4"',
        "INVESTIGATION": '"#DAE8FC"',
        "ACTION": '"#E1D5E7"',
        "GENERIC_EVENT": '"#F5F5F5"',
    }

    def add_event(event):
        is_error = event.id in error_ids
        base_color = type_colors.get(event.event_type.upper(), '"white"')
        color = '"lightcoral"' if is_error else base_color
        border = '"red"' if is_error else '"black"'
        penwidth = "2" if is_error else "1"

        clean_content = str(event.content).replace('"', "'").replace("\n", " ")
        short_content = clean_content[:45] + "..." if len(clean_content) > 45 else clean_content

        label = (
            f"<<B>{event.event_type}</B><BR/>"
            f"<FONT POINT-SIZE='10'>{event.id}</FONT><BR/>"
            f"<I>{short_content}</I>>"
        )
        lines.append(
            f'  "{event.id}" [label={label}, fillcolor={color}, '
            f'color={border}, penwidth={penwidth}];'
        )

    def add_finding_note(finding):
        note_id = f"finding_{finding.event_id}"
        clean_type = str(finding.failure_type).replace('"', "'")
        lines.append(
            f'  "{note_id}" [shape=note, style=filled, fillcolor="lightcoral", '
            f'color="red", label="{clean_type}"];'
        )
        lines.append(
            f'  "{finding.event_id}" -> "{note_id}" '
            '[style=dashed, color=red, weight=2];'
        )

    collapsed_ranges = []

    i = 0
    while i < len(events):
        if i in keep_indices:
            add_event(events[i])
            i += 1
            continue

        start = i
        while i < len(events) and i not in keep_indices:
            i += 1

        count = i - start
        if count:
            node_id = f"collapsed_{start}_{i - 1}"
            collapsed_ranges.append((start, i - 1, node_id))
            lines.append(
                f'  "{node_id}" [shape=box, style="rounded,dashed", '
                f'fillcolor="white", color="gray", fontcolor="gray", '
                f'label="... {count} routine events ..."];'
            )

    # Reconstruct causal edges whose endpoints are represented.
    represented_ids = {
        events[i].id for i in keep_indices
    }

    for event in events:
        if event.id not in represented_ids:
            continue
        for source_id in getattr(event, "metadata", {}).get("derived_from", []) or []:
            if source_id in represented_ids:
                lines.append(
                    f'  "{source_id}" -> "{event.id}" '
                    '[style=solid, color=black, weight=2];'
                )

    # Preserve chronological continuity across collapsed routine-event ranges.
    for start, end, node_id in collapsed_ranges:
        if start > 0 and (start - 1) in keep_indices:
            previous_id = events[start - 1].id
            lines.append(
                f'  "{previous_id}" -> "{node_id}" '
                '[style=dotted, color=gray, weight=1];'
            )

        if end + 1 < len(events) and (end + 1) in keep_indices:
            next_id = events[end + 1].id
            lines.append(
                f'  "{node_id}" -> "{next_id}" '
                '[style=dotted, color=gray, weight=1];'
            )

    for finding in findings:
        if finding.event_id in represented_ids:
            add_finding_note(finding)

    lines.append("}")
    return "\n".join(lines)

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
