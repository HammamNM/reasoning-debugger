from dataclasses import dataclass, field
from datetime import datetime, UTC


@dataclass
class ConfidenceUpdate:

    previous: float

    change: float

    current: float

    reason: str

    evidence: object = None

    timestamp: str = field(
        default_factory=lambda: datetime.now(UTC).isoformat()
    )


class ConfidenceTracker:


    def update(
        self,
        hypothesis,
        change,
        reason,
        evidence=None
    ):

        previous = hypothesis.confidence


        current = previous + change


        current = max(
            0.0,
            min(
                1.0,
                current
            )
        )


        hypothesis.confidence = current


        if not hasattr(
            hypothesis,
            "confidence_history"
        ):

            hypothesis.confidence_history = []


        update = ConfidenceUpdate(

            previous=previous,

            change=change,

            current=current,

            reason=reason,

            evidence=evidence

        )


        hypothesis.confidence_history.append(
            update
        )


        return update
