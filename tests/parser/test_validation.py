import pytest

from kernel.models import PrimitiveType, ReasoningUnit
from kernel.parser.validation import ReasoningUnitValidator
from kernel.provenance import ProvenanceRecord


class TestReasoningUnitValidator:

    def setup_method(self):
        self.validator = ReasoningUnitValidator()

    def test_valid_reasoning_unit(self):
        unit = ReasoningUnit(
            id="1",
            primitive=PrimitiveType.OBSERVATION,
            content="Chest pain",
        )

        assert self.validator.validate(unit) is True

    def test_valid_reasoning_unit_with_provenance(self):
        unit = ReasoningUnit(
            id="1",
            primitive=PrimitiveType.EVIDENCE,
            content="Finding",
            provenance=ProvenanceRecord(
                source="PARSER",
                event_type="TEXT_SEGMENT",
            ),
        )

        assert self.validator.validate(unit) is True

    def test_none_is_invalid(self):
        assert self.validator.validate(None) is False

    def test_non_reasoning_unit_is_invalid(self):
        assert self.validator.validate("not a reasoning unit") is False

    def test_empty_id_is_invalid(self):
        unit = ReasoningUnit(
            id="",
            primitive=PrimitiveType.OBSERVATION,
            content="Observation",
        )

        assert self.validator.validate(unit) is False

    def test_missing_primitive_is_invalid(self):
        unit = ReasoningUnit(
            id="1",
            primitive=None,
            content="Observation",
        )

        assert self.validator.validate(unit) is False

    def test_invalid_primitive_type_is_invalid(self):
        unit = ReasoningUnit(
            id="1",
            primitive="OBSERVATION",
            content="Observation",
        )

        assert self.validator.validate(unit) is False

    def test_empty_content_is_invalid(self):
        unit = ReasoningUnit(
            id="1",
            primitive=PrimitiveType.OBSERVATION,
            content="",
        )

        assert self.validator.validate(unit) is False

    def test_whitespace_content_is_invalid(self):
        unit = ReasoningUnit(
            id="1",
            primitive=PrimitiveType.OBSERVATION,
            content="   ",
        )

        assert self.validator.validate(unit) is False

    def test_invalid_provenance_is_invalid(self):
        unit = ReasoningUnit(
            id="1",
            primitive=PrimitiveType.OBSERVATION,
            content="Observation",
            provenance="invalid",
        )

        assert self.validator.validate(unit) is False
