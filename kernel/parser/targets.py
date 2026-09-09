from dataclasses import dataclass
import re


@dataclass(frozen=True)
class TargetReference:
    text: str
    kind: str


class TargetExtractor:
    """Extracts only explicit target references from reasoning text."""

    _PATTERNS = (
        ("hypothesis", r"\b(?:the|this|that|previous|current)\s+hypothesis\b"),
        ("diagnosis", r"\b(?:the|this|that|previous|current)\s+diagnosis\b"),
    )

    def extract(self, text):
        if text is None:
            return []

        if not isinstance(text, str):
            raise TypeError("text must be a string")

        text = text.strip()

        if not text:
            return []

        results = []

        for kind, pattern in self._PATTERNS:
            for match in re.finditer(pattern, text, flags=re.IGNORECASE):
                results.append(
                    TargetReference(
                        text=match.group(0),
                        kind=kind,
                    )
                )

        return results
