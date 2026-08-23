from dataclasses import dataclass
from enum import Enum


from kernel.provenance import (
    ProvenanceRecord
)


class PrimitiveType(Enum):

    OBSERVATION = "OBSERVATION"

    EVIDENCE = "EVIDENCE"

    INVESTIGATION = "INVESTIGATION"

    HYPOTHESIS = "HYPOTHESIS"

    INFERENCE = "INFERENCE"

    HYPOTHESIS_UPDATE = "HYPOTHESIS_UPDATE"

    DECISION = "DECISION"

    OUTCOME = "OUTCOME"


@dataclass
class ReasoningUnit:

    id: str

    primitive: PrimitiveType

    content: str

    provenance: ProvenanceRecord | None = None
