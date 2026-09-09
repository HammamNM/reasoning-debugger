import pytest

from kernel.models import PrimitiveType, ReasoningUnit
from kernel.parser.targets import TargetReference
from kernel.parser.target_resolver import TargetResolver


def unit(unit_id, primitive, content):
    return ReasoningUnit(
        id=unit_id,
        primitive=primitive,
        content=content,
    )


class TestTargetResolver:

    def setup_method(self):
        self.resolver = TargetResolver()

    def test_resolves_hypothesis_reference(self):
        hypothesis = unit(
            "h1",
            PrimitiveType.HYPOTHESIS,
            "I suspect ACS",
        )

        reference = TargetReference(
            text="previous hypothesis",
            kind="hypothesis",
        )

        result = self.resolver.resolve(
            reference,
            [hypothesis],
        )

        assert result is hypothesis

    def test_resolves_diagnosis_reference(self):
        diagnosis = unit(
            "h1",
            PrimitiveType.HYPOTHESIS,
            "Diagnosis: NSTEMI",
        )

        reference = TargetReference(
            text="current diagnosis",
            kind="diagnosis",
        )

        result = self.resolver.resolve(
            reference,
            [diagnosis],
        )

        assert result is diagnosis

    def test_unresolved_reference_returns_none(self):
        reference = TargetReference(
            text="previous hypothesis",
            kind="hypothesis",
        )

        assert self.resolver.resolve(
            reference,
            [],
        ) is None

    def test_wrong_primitive_is_not_resolved(self):
        observation = unit(
            "o1",
            PrimitiveType.OBSERVATION,
            "Patient has chest pain",
        )

        reference = TargetReference(
            text="previous hypothesis",
            kind="hypothesis",
        )

        assert self.resolver.resolve(
            reference,
            [observation],
        ) is None

    def test_none_reference_returns_none(self):
        assert self.resolver.resolve(
            None,
            [],
        ) is None

    def test_unknown_reference_kind_returns_none(self):
        reference = TargetReference(
            text="previous finding",
            kind="unknown",
        )

        hypothesis = unit(
            "h1",
            PrimitiveType.HYPOTHESIS,
            "Hypothesis",
        )

        assert self.resolver.resolve(
            reference,
            [hypothesis],
        ) is None

    def test_invalid_reference_type_is_rejected(self):
        with pytest.raises(TypeError):
            self.resolver.resolve(
                "previous hypothesis",
                [],
            )

    def test_invalid_unit_type_is_rejected(self):
        reference = TargetReference(
            text="previous hypothesis",
            kind="hypothesis",
        )

        with pytest.raises(TypeError):
            self.resolver.resolve(
                reference,
                ["not a unit"],
            )

    def test_previous_hypothesis_resolves_to_nearest_previous_hypothesis(self):
        hypothesis_1 = unit(
            "h1",
            PrimitiveType.HYPOTHESIS,
            "I suspect ACS",
        )

        observation = unit(
            "o1",
            PrimitiveType.OBSERVATION,
            "Troponin is elevated",
        )

        hypothesis_2 = unit(
            "h2",
            PrimitiveType.HYPOTHESIS,
            "I suspect NSTEMI",
        )

        reference = TargetReference(
            text="previous hypothesis",
            kind="hypothesis",
        )

        result = self.resolver.resolve(
            reference,
            [hypothesis_1, observation, hypothesis_2],
        )

        assert result is hypothesis_2

    def test_previous_hypothesis_does_not_resolve_to_oldest_hypothesis(self):
        hypothesis_1 = unit(
            "h1",
            PrimitiveType.HYPOTHESIS,
            "I suspect ACS",
        )

        hypothesis_2 = unit(
            "h2",
            PrimitiveType.HYPOTHESIS,
            "I suspect NSTEMI",
        )

        reference = TargetReference(
            text="previous hypothesis",
            kind="hypothesis",
        )

        result = self.resolver.resolve(
            reference,
            [hypothesis_1, hypothesis_2],
        )

        assert result is hypothesis_2
