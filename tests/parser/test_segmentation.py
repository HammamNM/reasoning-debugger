import pytest

from kernel.parser.segmentation import TextSegmenter


class TestTextSegmenter:

    def setup_method(self):
        self.segmenter = TextSegmenter()

    def test_empty_text_returns_empty_list(self):
        assert self.segmenter.segment("") == []

    def test_whitespace_returns_empty_list(self):
        assert self.segmenter.segment("   \n  ") == []

    def test_single_statement(self):
        text = "The patient has chest pain."
        assert self.segmenter.segment(text) == [
            "The patient has chest pain."
        ]

    def test_multiple_sentences(self):
        text = (
            "The patient has chest pain. "
            "Troponin is elevated. "
            "NSTEMI is suspected."
        )

        assert self.segmenter.segment(text) == [
            "The patient has chest pain.",
            "Troponin is elevated.",
            "NSTEMI is suspected.",
        ]

    def test_multiple_lines(self):
        text = """
        The patient has chest pain.
        Troponin is elevated.

        NSTEMI is suspected.
        """

        assert self.segmenter.segment(text) == [
            "The patient has chest pain.",
            "Troponin is elevated.",
            "NSTEMI is suspected.",
        ]

    def test_preserves_order(self):
        text = "Observation. Evidence. Hypothesis. Decision."

        assert self.segmenter.segment(text) == [
            "Observation.",
            "Evidence.",
            "Hypothesis.",
            "Decision.",
        ]

    def test_non_string_input_is_rejected(self):
        with pytest.raises(TypeError):
            self.segmenter.segment(123)
