import uuid

from kernel.models import ReasoningUnit
from kernel.parser.segmentation import TextSegmenter
from kernel.parser.classification import PrimitiveClassifier
from kernel.parser.provenance import ProvenanceBuilder
from kernel.parser.targets import TargetExtractor
from kernel.parser.validation import ReasoningUnitValidator


class Parser:
    """
    Facade for deterministic reasoning-text parsing.

    Pipeline:

        raw text
            ↓
        segmentation
            ↓
        primitive classification
            ↓
        provenance construction
            ↓
        ReasoningUnit construction
            ↓
        validation

    The parser is domain-agnostic.
    It does not build reasoning graphs, infer domain knowledge,
    or make recommendations.
    """

    def __init__(
        self,
        segmenter=None,
        classifier=None,
        provenance_builder=None,
        target_extractor=None,
        validator=None,
    ):
        self.segmenter = segmenter or TextSegmenter()
        self.classifier = classifier or PrimitiveClassifier()
        self.provenance_builder = (
            provenance_builder or ProvenanceBuilder()
        )
        self.target_extractor = (
            target_extractor or TargetExtractor()
        )
        self.validator = validator or ReasoningUnitValidator()

    def parse(self, text):
        if text is None:
            return []

        if not isinstance(text, str):
            raise TypeError("text must be a string")

        segments = self.segmenter.segment(text)

        units = []

        for index, segment in enumerate(segments):
            primitive = self.classifier.classify(segment)

            # Unknown text is not forcibly assigned
            # to a reasoning primitive.
            if primitive is None:
                continue

            provenance = self.provenance_builder.build(
                segment,
                index,
            )

            unit = ReasoningUnit(
                id=str(uuid.uuid4()),
                primitive=primitive,
                content=segment,
                provenance=provenance,
            )

            if not self.validator.validate(unit):
                continue

            units.append(unit)

        return units
