import re


class TextSegmenter:
    """
    Splits raw reasoning text into ordered, non-empty segments.

    Segmentation is deliberately semantic-agnostic:
    it does not classify primitives or interpret meaning.
    """

    def segment(self, text):
        if text is None:
            return []

        if not isinstance(text, str):
            raise TypeError("text must be a string")

        text = text.strip()

        if not text:
            return []

        # Normalize line boundaries first.
        text = re.sub(r"\r\n?", "\n", text)

        segments = []

        for line in text.split("\n"):
            line = line.strip()

            if not line:
                continue

            # Keep sentence boundaries while avoiding empty fragments.
            parts = re.split(r"(?<=[.!?])\s+", line)

            for part in parts:
                part = part.strip()
                if part:
                    segments.append(part)

        return segments
