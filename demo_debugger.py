from kernel.debugger import ReasoningDebugger
from kernel.reasoning_trace import ReasoningTrace, ReasoningTraceEvent

def run_demo():
    print("\n[1] Initializing Reasoning Debugger...")
    debugger = ReasoningDebugger()

    # محاكاة لـ Trace قادم من Agent حقيقي
    trace = ReasoningTrace(events=(
        ReasoningTraceEvent(
            id="step-1",
            content="Observation: High CPU usage detected.",
            event_type="OBSERVATION"
        ),
        ReasoningTraceEvent(
            id="step-2",
            content="assumption without support: It must be a memory leak.",
            event_type="INFERENCE"
        ),
        ReasoningTraceEvent(
            id="step-3",
            content="Decision: Restart the main server.",
            event_type="DECISION_ASSESSMENT",
            metadata={"derived_from": ["step-2"]}
        ),
    ))

    print("[2] Analyzing Trace Events...")
    findings = debugger.debug(trace)

    print("\n=== REASONING DEBUG REPORT ===")
    if not findings:
        print("Status: HEALTHY. No reasoning failures detected.")
        return

    for idx, finding in enumerate(findings, 1):
        print(f"Finding #{idx}:")
        print(f"  - Root Failure ID : {finding.first_failure_event_id}")
        print(f"  - Failure Type    : {finding.failure_type}")
        print(f"  - Explanation     : '{finding.explanation}'")

        if finding.downstream_event_ids:
            print(f"  - Cascading Impact: Corrupted decisions at {finding.downstream_event_ids}")
        else:
            print(f"  - Cascading Impact: Contained (No downstream effects)")
    print("==============================\n")

if __name__ == "__main__":
    run_demo()
