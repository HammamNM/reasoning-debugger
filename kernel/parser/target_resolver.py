from kernel.models import ReasoningUnit, PrimitiveType
from kernel.parser.targets import TargetReference


class TargetResolver:
    """
    Resolves explicit TargetReference objects against existing
    ReasoningUnit objects.

    This component is deliberately conservative:
    - it does not infer targets
    - it does not mutate units
    - it does not create units
    - unresolved targets return None
    """

    _KIND_TO_PRIMITIVES = {
        "hypothesis": {
            PrimitiveType.HYPOTHESIS,
        },
        "diagnosis": {
            PrimitiveType.HYPOTHESIS,
        },
    }

    def resolve(self, reference, units):
        if reference is None:
            return None

        if not isinstance(reference, TargetReference):
            raise TypeError(
                "reference must be a TargetReference"
            )

        if units is None:
            return None

        allowed_primitives = self._KIND_TO_PRIMITIVES.get(
            reference.kind
        )

        if allowed_primitives is None:
            return None

        candidates = []

        for unit in units:
            if not isinstance(unit, ReasoningUnit):
                raise TypeError(
                    "units must contain only ReasoningUnit objects"
                )

            if unit.primitive not in allowed_primitives:
                continue

            if self._matches(reference, unit):
                candidates.append(unit)

        if not candidates:
            return None

        return candidates[-1]

    def resolve_all(self, references, units):
        if references is None:
            return []

        results = []

        for reference in references:
            resolved = self.resolve(reference, units)

            if resolved is not None:
                results.append(resolved)

        return results

    @staticmethod
    def _matches(reference, unit):
        reference_text = reference.text.strip().lower()
        content = unit.content.strip().lower()

        if not reference_text or not content:
            return False

        if reference.kind == "hypothesis":
            return unit.primitive == PrimitiveType.HYPOTHESIS

        if reference.kind == "diagnosis":
            return unit.primitive == PrimitiveType.HYPOTHESIS

        return False
