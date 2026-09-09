import re

from kernel.models import PrimitiveType


class PrimitiveClassifier:
    """
    Deterministic, domain-agnostic classifier for reasoning segments.

    The classifier recognizes explicit linguistic/action markers only.
    It does not contain medical, legal, or domain-specific knowledge.
    """

    _PATTERNS = (
        (
            PrimitiveType.HYPOTHESIS_UPDATE,
            (
                r"^\s*(?:confirm|confirmed|reject|rejected)\b",
                r"^\s*(?:i\s+)?(?:confirm|reject)\b",
            ),
        ),
        (
            PrimitiveType.HYPOTHESIS,
            (
                r"^\s*(?:i\s+)?(?:suspect|hypothesize|hypothesis)\b",
                r"^\s*(?:possible|likely|probable)\b",
            ),
        ),
        (
            PrimitiveType.INFERENCE,
            (
                r"^\s*(?:therefore|thus|hence|so)\b",
                r"\b(?:suggests|indicates|implies)\b",
            ),
        ),
        (
            PrimitiveType.INVESTIGATION,
            (
                r"^\s*(?:order|request|check|measure|test)\b",
                r"^\s*(?:investigate|investigation)\b",
            ),
        ),
        (
            PrimitiveType.DECISION,
            (
                r"^\s*(?:i\s+will|we\s+will|decide|decision)\b",
                r"^\s*(?:treat|start|stop|perform)\b",
            ),
        ),
        (
            PrimitiveType.OUTCOME,
            (
                r"^\s*(?:outcome|result|response)\b",
                r"^\s*(?:improved|worsened|failed|succeeded)\b",
            ),
        ),
        (
            PrimitiveType.EVIDENCE,
            (
                r"^\s*(?:evidence|finding|finding:)\b",
            ),
        ),
        (
            PrimitiveType.OBSERVATION,
            (
                r"^\s*(?:observation|observed|reports?|reported)\b",
            ),
        ),
    )

    def classify(self, segment):
        if segment is None:
            return None

        if not isinstance(segment, str):
            raise TypeError("segment must be a string")

        segment = segment.strip()

        if not segment:
            return None

        for primitive, patterns in self._PATTERNS:
            for pattern in patterns:
                if re.search(pattern, segment, flags=re.IGNORECASE):
                    return primitive

        return None
