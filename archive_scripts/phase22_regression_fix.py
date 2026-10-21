import re

print("1. Restoring Validation and Helpers to kernel/reasoning_trace.py...")
with open('kernel/reasoning_trace.py', 'w', encoding='utf-8') as f:
    f.write('''\
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
        for e_data in data.get("events", []):
            events.append(ReasoningTraceEvent(
                id=e_data["id"],
                content=e_data["content"],
                event_type=e_data["event_type"],
                metadata=e_data.get("metadata", {})
            ))
        return cls(events=tuple(events))

    def event_ids(self) -> Tuple[str, ...]:
        return tuple(e.id for e in self.events)

    def get_event(self, event_id: str) -> Optional[ReasoningTraceEvent]:
        for e in self.events:
            if e.id == event_id:
                return e
        return None
''')

print("2. Upgrading Error Semantics in Phase 5 Test...")
filepath = 'tests/phase5/test_trace_graph_kernel_contract.py'
with open(filepath, 'r', encoding='utf-8') as f:
    test_code = f.read()

# Replace TypeError with InvalidTraceSchemaError in the specific test
test_code = test_code.replace('pytest.raises(TypeError)', 'pytest.raises(InvalidTraceSchemaError)')
test_code = test_code.replace('from kernel.debugger import ReasoningDebugger', 'from kernel.api import ReasoningDebugger, InvalidTraceSchemaError')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(test_code)

print("Done.")
