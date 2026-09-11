from kernel.failure_propagation import FailurePropagationAnalyzer
from kernel.reasoning_failure_detector import UnsupportedAssumptionDetector
from kernel.structural_failure_detector import StructuralFailureDetector
from kernel.trace_graph_adapter import TraceGraphAdapter
from kernel.unsupported_inference_detector import UnsupportedInferenceDetector
from kernel.reasoning_trace import ReasoningTrace
from kernel.infinite_loop_detector import InfiniteLoopDetector

class ReasoningDebugger:
    def __init__(
        self,
        reasoning_failure_detector=None,
        structural_failure_detector=None,
        propagation_analyzer=None,
        trace_graph_adapter=None,
        unsupported_inference_detector=None,
        infinite_loop_detector=None,
    ):
        self.reasoning_failure_detector = reasoning_failure_detector or UnsupportedAssumptionDetector()
        self.structural_failure_detector = structural_failure_detector or StructuralFailureDetector()
        self.propagation_analyzer = propagation_analyzer or FailurePropagationAnalyzer()
        self.trace_graph_adapter = trace_graph_adapter or TraceGraphAdapter()
        self.unsupported_inference_detector = unsupported_inference_detector or UnsupportedInferenceDetector()
        self.infinite_loop_detector = infinite_loop_detector or InfiniteLoopDetector()

        self._validate_dependency(self.reasoning_failure_detector, "reasoning_failure_detector", ("detect",))
        self._validate_dependency(self.structural_failure_detector, "structural_failure_detector", ("detect",))
        self._validate_dependency(self.propagation_analyzer, "propagation_analyzer", ("analyze",))
        self._validate_dependency(self.trace_graph_adapter, "trace_graph_adapter", ("build",))
        self._validate_dependency(self.unsupported_inference_detector, "unsupported_inference_detector", ("detect",))
        self._validate_dependency(self.infinite_loop_detector, "infinite_loop_detector", ("detect",))

    @staticmethod
    def _validate_findings(findings, detector_name):
        from kernel.debug_finding import DebugFinding
        if not isinstance(findings, list):
            raise TypeError(f"{detector_name} must return a list of DebugFinding")
        if not all(isinstance(finding, DebugFinding) for finding in findings):
            raise TypeError(f"{detector_name} must return only DebugFinding objects")

    @staticmethod
    def _validate_dependency(dependency, name, methods):
        if dependency is None:
            raise TypeError(f"{name} must not be None")
        for method in methods:
            if not callable(getattr(dependency, method, None)):
                raise TypeError(f"{name} must provide callable {method}()")

    def debug(self, trace):
        from kernel.reasoning_trace import ReasoningTrace
        from kernel.errors import InvalidTraceSchemaError
        
        if not isinstance(trace, ReasoningTrace):
            raise InvalidTraceSchemaError(f'Expected ReasoningTrace, got {type(trace)}')

        findings = list(self.reasoning_failure_detector.detect(trace))
        self._validate_findings(findings, "reasoning_failure_detector")

        loop_findings = self.infinite_loop_detector.detect(trace)
        self._validate_findings(loop_findings, "infinite_loop_detector")
        findings.extend(loop_findings)

        graph = self.trace_graph_adapter.build(trace)

        unsupported_inference_findings = self.unsupported_inference_detector.detect(graph)
        self._validate_findings(unsupported_inference_findings, "unsupported_inference_detector")
        findings.extend(unsupported_inference_findings)

        structural_findings = self.structural_failure_detector.detect(graph)
        self._validate_findings(structural_findings, "structural_failure_detector")
        findings.extend(structural_findings)

        enriched_findings = []
        for finding in findings:
            affected_event_ids = self.propagation_analyzer.analyze(graph, finding.event_id)
            enriched_findings.append(
                type(finding)(
                    event_id=finding.event_id,
                    failure_type=finding.failure_type,
                    explanation=finding.explanation,
                    affected_event_ids=affected_event_ids,
                    metadata=finding.metadata,
                )
            )

        return enriched_findings
