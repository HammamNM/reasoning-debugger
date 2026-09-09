from dataclasses import dataclass
from kernel.debugger import ReasoningDebugger
from kernel.reasoning_trace import ReasoningTrace

@dataclass
class BenchmarkCase:
    name: str
    trace: ReasoningTrace
    expected_root_event_id: str | None  # None indicates a Negative Case (Valid Trace)

@dataclass
class EvaluationMetrics:
    total_cases: int
    precision: float
    recall: float
    localization_accuracy: float

class DebuggerEvaluator:
    """
    Evaluates the ReasoningDebugger against annotated test cases.
    Measures Precision, Recall, and First-Failure Localization Accuracy.
    """
    def __init__(self, debugger: ReasoningDebugger):
        self.debugger = debugger

    def evaluate(self, cases: list[BenchmarkCase]) -> EvaluationMetrics:
        if not cases:
            return EvaluationMetrics(0, 0.0, 0.0, 0.0)

        true_positives = 0
        false_positives = 0
        false_negatives = 0
        correct_localization = 0

        for case in cases:
            findings = self.debugger.debug(case.trace)
            has_finding = len(findings) > 0

            if case.expected_root_event_id is not None:
                # Positive Case (Should find an error)
                if has_finding:
                    true_positives += 1
                    if findings[0].first_failure_event_id == case.expected_root_event_id:
                        correct_localization += 1
                else:
                    false_negatives += 1
            else:
                # Negative Case (Should NOT find an error)
                if has_finding:
                    false_positives += 1

        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 1.0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 1.0
        localization_accuracy = correct_localization / true_positives if true_positives > 0 else 1.0

        return EvaluationMetrics(
            total_cases=len(cases),
            precision=precision,
            recall=recall,
            localization_accuracy=localization_accuracy
        )
