from dataclasses import dataclass, field
from typing import Dict, Any, Tuple, Optional

@dataclass(frozen=True)
class ReasoningTraceEvent:
    id: str
    content: str
    event_type: str
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "event_type": self.event_type,
            "metadata": self.metadata or {}
        }

@dataclass(frozen=True)
class ReasoningTrace:
    events: Tuple[ReasoningTraceEvent, ...]

    def __post_init__(self):
        if not isinstance(self.events, tuple):
            raise TypeError(f"events must be a tuple, got {type(self.events)}")
        for e in self.events:
            if not isinstance(e, ReasoningTraceEvent):
                raise TypeError(f"All events must be ReasoningTraceEvent instances, got {type(e)}")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "events": [e.to_dict() for e in self.events]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReasoningTrace":
        events = []
        # 1. التسامح مع ملفات LangChain و SWE-agent
        raw_events = data.get("events") or data.get("runs") or data.get("trajectory") or data.get("steps") or []
        
        for i, e_data in enumerate(raw_events):
            # 2. قيم افتراضية ذكية للحقول الأساسية لمنع الانهيار
            event_id = e_data.get("id", f"auto_id_{i}")
            event_type = e_data.get("event_type", e_data.get("type", "GENERIC_EVENT"))
            content = e_data.get("content", e_data.get("text", "No content provided"))
            
            # 3. تجميع أي حقول إضافية غريبة ووضعها في metadata بأمان
            metadata = e_data.get("metadata", {})
            if not isinstance(metadata, dict):
                metadata = {}
                
            for key, value in e_data.items():
                if key not in ["id", "event_type", "content", "metadata"]:
                    metadata[key] = value

            # 4. قيم افتراضية ذكية للتحليل السببي (Causal Analysis)
            if "derived_from" not in metadata:
                metadata["derived_from"] = []
            if "support_required" not in metadata:
                metadata["support_required"] = False

            events.append(ReasoningTraceEvent(
                id=event_id,
                content=content,
                event_type=event_type,
                metadata=metadata
            ))
        return cls(events=tuple(events))

    def event_ids(self) -> Tuple[str, ...]:
        return tuple(e.id for e in self.events)

    def get_event(self, event_id: str) -> Optional[ReasoningTraceEvent]:
        for e in self.events:
            if e.id == event_id:
                return e
        return None
