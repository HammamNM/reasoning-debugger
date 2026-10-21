from analytics.cognitive_pattern_pipeline import (
    CognitivePatternPipeline
)

from analytics.performance_analyzer import (
    PerformanceAnalyzer
)

from analytics.reasoning_analyzer import (
    ReasoningAnalyzer
)

from analytics.report import (
    ReportGenerator
)


class AnalyticsEngine:


    def __init__(self):

        self.cognitive_pipeline = (
            CognitivePatternPipeline()
        )

        self.performance_analyzer = (
            PerformanceAnalyzer()
        )

        self.reasoning_analyzer = (
            ReasoningAnalyzer()
        )

        self.report_generator = (
            ReportGenerator()
        )


    def generate_report(

        self,

        session,

        reasoning_graph=None

    ):

        cognitive_data = {

            "patterns": [],

            "metrics": []

        }

        reasoning_metrics = {}

        reasoning_path = []


        if reasoning_graph is not None:

            cognitive_data = (

                self.cognitive_pipeline.analyze(
                    reasoning_graph,
                    session.reasoning_state
                )

            )


            reasoning_metrics = (

                self.reasoning_analyzer.analyze_graph(

                    reasoning_graph

                )

            )


            reasoning_path = (

                self.reasoning_analyzer.extract_reasoning_path(

                    reasoning_graph

                )

            )


        performance_data = (

            self.performance_analyzer.analyze(

                session

            )

        )


        report = (

            self.report_generator.generate(

                session=session,

                performance_data=performance_data,

                patterns=[],

                cognitive_data=cognitive_data

            )

        )


        report["reasoning"] = {

            "metrics": reasoning_metrics,

            "path": reasoning_path

        }


        return report
