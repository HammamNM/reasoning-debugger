from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ReasoningTraceEvent:
    id: str
    content: str
    event_type: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ReasoningTrace:
    events: tuple[ReasoningTraceEvent, ...]

    def __post_init__(self):
        if not isinstance(self.events, tuple):
            raise TypeError("events must be a tuple")

        for event in self.events:
            if not isinstance(event, ReasoningTraceEvent):
                raise TypeError(
                    "all trace events must be ReasoningTraceEvent instances"
                )

    def event_ids(self) -> tuple[str, ...]:
        return tuple(event.id for event in self.events)

    def get_event(self, event_id: str):
        for event in self.events:
            if event.id == event_id:
                return event
        return None
