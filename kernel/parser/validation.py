from kernel.models import PrimitiveType, ReasoningUnit
from kernel.provenance import ProvenanceRecord


class ReasoningUnitValidator:
    """
    Structural validator for parser-generated ReasoningUnit objects.

    This validator checks structure and types only.
    It does not interpret semantic or domain-specific meaning.
    """

    def validate(self, unit):
        if not isinstance(unit, ReasoningUnit):
            return False

        if not isinstance(unit.id, str) or not unit.id.strip():
            return False

        if not isinstance(unit.primitive, PrimitiveType):
            return False

        if not isinstance(unit.content, str) or not unit.content.strip():
            return False

        if unit.provenance is not None:
            if not isinstance(unit.provenance, ProvenanceRecord):
                return False

        return True
