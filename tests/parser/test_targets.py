import pytest

from kernel.parser.targets import TargetExtractor, TargetReference


class TestTargetExtractor:

    def setup_method(self):
        self.extractor = TargetExtractor()

    def test_extracts_hypothesis_reference(self):
        result = self.extractor.extract(
            "This supports the previous hypothesis."
        )

        assert len(result) == 1
        assert isinstance(result[0], TargetReference)
        assert result[0].kind == "hypothesis"

    def test_extracts_diagnosis_reference(self):
        result = self.extractor.extract(
            "Confirm the current diagnosis."
        )

        assert len(result) == 1
        assert result[0].kind == "diagnosis"

    def test_unknown_text_returns_empty_list(self):
        assert self.extractor.extract(
            "The patient arrived yesterday."
        ) == []

    def test_empty_text_returns_empty_list(self):
        assert self.extractor.extract("") == []

    def test_none_returns_empty_list(self):
        assert self.extractor.extract(None) == []

    def test_non_string_input_is_rejected(self):
        with pytest.raises(TypeError):
            self.extractor.extract(123)
