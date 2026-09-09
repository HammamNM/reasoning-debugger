from benchmarks.evaluator import DebuggerEvaluator, BenchmarkCase
from benchmarks.samples.coding_agent_trace import load_coding_agent_failure_trace
from benchmarks.samples.data_agent_trace import load_data_agent_failure_trace
from kernel.debugger import ReasoningDebugger

def test_debugger_isolates_failures_across_diverse_domains():
    coding_trace = load_coding_agent_failure_trace()
    data_trace = load_data_agent_failure_trace()

    cases = [
        BenchmarkCase(
            name="Coding Agent Fix Assumption",
            trace=coding_trace,
            expected_root_event_id="inf-assumption-1"
        ),
        BenchmarkCase(
            name="Data Agent Drop Assumption",
            trace=data_trace,
            expected_root_event_id="inf-assumption-2"
        ),
    ]

    evaluator = DebuggerEvaluator(ReasoningDebugger())
    metrics = evaluator.evaluate(cases)

    assert metrics.precision == 1.0, f"False positive detected. Precision: {metrics.precision}"
    assert metrics.recall == 1.0, f"Missed a real-world failure. Recall: {metrics.recall}"
    assert metrics.localization_accuracy == 1.0, f"Failed to pinpoint the exact root cause. Accuracy: {metrics.localization_accuracy}"
