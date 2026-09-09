from kernel.parser.provenance import ProvenanceBuilder
from kernel.provenance import ProvenanceRecord


class TestProvenanceBuilder:

    def setup_method(self):
        self.builder = ProvenanceBuilder()

    def test_build_returns_provenance_record(self):
        record = self.builder.build(
            "Chest pain",
            segment_index=0,
        )

        assert isinstance(record, ProvenanceRecord)

    def test_source_is_parser(self):
        record = self.builder.build(
            "Chest pain",
            segment_index=0,
        )

        assert record.source == "PARSER"

    def test_event_type_identifies_text_segment(self):
        record = self.builder.build(
            "Chest pain",
            segment_index=0,
        )

        assert record.event_type == "TEXT_SEGMENT"

    def test_segment_metadata_is_preserved(self):
        record = self.builder.build(
            "Chest pain",
            segment_index=2,
        )

        assert record.metadata["text"] == "Chest pain"
        assert record.metadata["segment_index"] == 2

    def test_none_text_is_rejected(self):
        import pytest

        with pytest.raises(TypeError):
            self.builder.build(None, segment_index=0)

    def test_non_string_text_is_rejected(self):
        import pytest

        with pytest.raises(TypeError):
            self.builder.build(123, segment_index=0)

    def test_segment_index_must_be_non_negative(self):
        import pytest

        with pytest.raises(ValueError):
            self.builder.build("Chest pain", segment_index=-1)
