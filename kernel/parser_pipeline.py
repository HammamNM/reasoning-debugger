from dataclasses import dataclass

from kernel.models import ReasoningUnit
from kernel.graph import ReasoningGraph
from kernel.parser.parser import Parser
from kernel.parser.targets import TargetReference
from kernel.parser.target_resolver import TargetResolver
from kernel.unit_graph_builder import UnitGraphBuilder


@dataclass
class ParserPipelineResult:
    units: list[ReasoningUnit]
    graph: ReasoningGraph
    references: list[TargetReference]


class ParserPipeline:
    """
    Structural orchestration layer for parser and graph components.

    Responsibilities:
    - parse raw reasoning text
    - insert parsed units into a structural graph
    - expose explicit target extraction
    - expose explicit target resolution

    It does not:
    - infer semantic relationships
    - add domain knowledge
    - generate recommendations
    - modify ReasoningUnit objects
    """

    def __init__(
        self,
        parser=None,
        resolver=None,
        graph_builder=None,
    ):
        self.parser = parser or Parser()
        self.resolver = resolver or TargetResolver()
        self.graph_builder = graph_builder or UnitGraphBuilder()

    def process(self, text):
        units = self.parser.parse(text)

        self.graph_builder.add_units(units)

        return ParserPipelineResult(
            units=units,
            graph=self.graph_builder.graph,
            references=[],
        )

    def extract_references(self, text):
        return self.parser.target_extractor.extract(text)

    def resolve_target(self, reference, units):
        return self.resolver.resolve(reference, units)
