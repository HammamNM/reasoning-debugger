import pytest

from kernel.models import PrimitiveType, ReasoningUnit
from kernel.parser.parser import Parser


class TestParser:

    def setup_method(self):
        self.parser = Parser()

    def test_parse_returns_reasoning_units(self):
        result = self.parser.parse(
            "Observation: chest pain. I suspect ACS."
        )

        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(unit, ReasoningUnit) for unit in result)

    def test_parse_classifies_segments(self):
        result = self.parser.parse(
            "Observation: chest pain. I suspect ACS."
        )

        assert result[0].primitive == PrimitiveType.OBSERVATION
        assert result[1].primitive == PrimitiveType.HYPOTHESIS

    def test_parse_preserves_content(self):
        result = self.parser.parse(
            "Observation: chest pain."
        )

        assert result[0].content == "Observation: chest pain."

    def test_parse_adds_provenance(self):
        result = self.parser.parse(
            "Observation: chest pain."
        )

        assert result[0].provenance is not None
        assert result[0].provenance.source == "PARSER"
        assert result[0].provenance.event_type == "TEXT_SEGMENT"

    def test_parse_unknown_segment_is_not_forced(self):
        result = self.parser.parse(
            "The patient arrived yesterday."
        )

        assert result == []

    def test_parse_empty_text(self):
        assert self.parser.parse("") == []

    def test_parse_none(self):
        assert self.parser.parse(None) == []

    def test_parse_non_string_input(self):
        with pytest.raises(TypeError):
            self.parser.parse(123)
