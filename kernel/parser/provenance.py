from kernel.provenance import ProvenanceRecord


class ProvenanceBuilder:
    """Builds provenance records for parser-generated text segments."""

    def build(self, text, segment_index):
        if not isinstance(text, str):
            raise TypeError("text must be a string")

        if not isinstance(segment_index, int):
            raise TypeError("segment_index must be an integer")

        if segment_index < 0:
            raise ValueError("segment_index must be non-negative")

        return ProvenanceRecord(
            source="PARSER",
            event_type="TEXT_SEGMENT",
            metadata={
                "text": text,
                "segment_index": segment_index,
            },
        )
