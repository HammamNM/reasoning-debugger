import pytest

from kernel.models import PrimitiveType
from kernel.parser.classification import PrimitiveClassifier


class TestPrimitiveClassifier:

    def setup_method(self):
        self.classifier = PrimitiveClassifier()

    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            ("Observation: chest pain", PrimitiveType.OBSERVATION),
            ("Observed abnormal behavior", PrimitiveType.OBSERVATION),
            ("Evidence: three failed payments", PrimitiveType.EVIDENCE),
            ("I suspect fraud", PrimitiveType.HYPOTHESIS),
            ("Possible fraud", PrimitiveType.HYPOTHESIS),
            ("Therefore the hypothesis is supported", PrimitiveType.INFERENCE),
            ("This suggests fraud", PrimitiveType.INFERENCE),
            ("Order ECG", PrimitiveType.INVESTIGATION),
            ("Request additional testing", PrimitiveType.INVESTIGATION),
            ("I will treat the patient", PrimitiveType.DECISION),
            ("Decision: proceed", PrimitiveType.DECISION),
            ("Outcome: patient improved", PrimitiveType.OUTCOME),
            ("Confirmed hypothesis", PrimitiveType.HYPOTHESIS_UPDATE),
            ("Reject the previous hypothesis", PrimitiveType.HYPOTHESIS_UPDATE),
        ],
    )
    def test_explicit_markers_are_classified(self, text, expected):
        assert self.classifier.classify(text) == expected

    def test_unknown_segment_returns_none(self):
        assert self.classifier.classify("The patient arrived yesterday.") is None

    def test_empty_segment_returns_none(self):
        assert self.classifier.classify("") is None

    def test_whitespace_segment_returns_none(self):
        assert self.classifier.classify("   ") is None

    def test_none_returns_none(self):
        assert self.classifier.classify(None) is None

    def test_non_string_input_is_rejected(self):
        with pytest.raises(TypeError):
            self.classifier.classify(123)


class TestClassificationContract:

    def setup_method(self):
        self.classifier = PrimitiveClassifier()

    def test_hypothesis_update_has_priority_over_hypothesis(self):
        assert (
            self.classifier.classify("Confirmed hypothesis")
            == PrimitiveType.HYPOTHESIS_UPDATE
        )

    def test_rejection_is_hypothesis_update(self):
        assert (
            self.classifier.classify("Reject the suspected hypothesis")
            == PrimitiveType.HYPOTHESIS_UPDATE
        )

    def test_inference_marker_is_not_treated_as_hypothesis(self):
        assert (
            self.classifier.classify("Therefore the hypothesis is supported")
            == PrimitiveType.INFERENCE
        )

    def test_inference_can_be_detected_inside_statement(self):
        assert (
            self.classifier.classify(
                "The finding suggests a different explanation."
            )
            == PrimitiveType.INFERENCE
        )

    def test_unknown_text_is_not_forced_into_observation(self):
        assert (
            self.classifier.classify(
                "The patient arrived yesterday."
            )
            is None
        )

    def test_case_is_ignored(self):
        assert (
            self.classifier.classify("ORDER additional testing")
            == PrimitiveType.INVESTIGATION
        )

    def test_leading_whitespace_is_ignored(self):
        assert (
            self.classifier.classify("   Evidence: positive")
            == PrimitiveType.EVIDENCE
        )
