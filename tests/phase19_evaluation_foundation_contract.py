from benchmarks.evaluator import DebuggerEvaluator, BenchmarkCase
from kernel.debugger import ReasoningDebugger
from kernel.reasoning_trace import ReasoningTrace, ReasoningTraceEvent

def test_debugger_evaluation_metrics_are_accurate():
    # 1. Clean Negative Case (Valid Reasoning)
    clean_trace = ReasoningTrace(events=(
        ReasoningTraceEvent(id="e1", content="Observation", event_type="OBSERVATION"),
        ReasoningTraceEvent(id="e2", content="Evidence", event_type="EVIDENCE"),
    ))

    # 2. Positive Case (Unsupported Assumption)
    faulty_trace = ReasoningTrace(events=(
        ReasoningTraceEvent(id="e1", content="Observation", event_type="OBSERVATION"),
        ReasoningTraceEvent(id="e2", content="assumption without support", event_type="INFERENCE"),
        ReasoningTraceEvent(id="e3", content="Decision", event_type="DECISION_ASSESSMENT", metadata={"derived_from": ["e2"]}),
    ))

    cases = [
        BenchmarkCase(name="Clean Flow", trace=clean_trace, expected_root_event_id=None),
        BenchmarkCase(name="Faulty Flow", trace=faulty_trace, expected_root_event_id="e2"),
    ]

    evaluator = DebuggerEvaluator(ReasoningDebugger())
    metrics = evaluator.evaluate(cases)

    # 100% Precision (No False Positives)
    assert metrics.precision == 1.0
    # 100% Recall (Caught the actual failure)
    assert metrics.recall == 1.0
    # 100% Localization Accuracy (Pinpointed 'e2' as the root)
    assert metrics.localization_accuracy == 1.0
