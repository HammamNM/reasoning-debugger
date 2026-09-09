from dataclasses import dataclass, field
from typing import Any, Mapping
from types import MappingProxyType

@dataclass(frozen=True)
class DebugFinding:
    """
    Structured, domain-agnostic representation of a reasoning failure.
    The finding identifies the earliest known failure, explains the
    structural reason for the failure, and records downstream impact.
    """
    event_id: str
    failure_type: str
    explanation: str
    affected_event_ids: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.event_id, str) or not self.event_id.strip():
            raise TypeError("event_id must be a non-empty string")
        if not isinstance(self.failure_type, str) or not self.failure_type.strip():
            raise TypeError("failure_type must be a non-empty string")
        if not isinstance(self.explanation, str) or not self.explanation.strip():
            raise TypeError("explanation must be a non-empty string")
        if not isinstance(self.affected_event_ids, tuple):
            raise TypeError("affected_event_ids must be a tuple")
        if not all(isinstance(event_id, str) and event_id.strip() for event_id in self.affected_event_ids):
            raise TypeError("affected_event_ids must contain non-empty strings")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")

        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @property
    def first_failure_event_id(self) -> str:
        return self.event_id

    @property
    def downstream_event_ids(self) -> tuple[str, ...]:
        return self.affected_event_ids
