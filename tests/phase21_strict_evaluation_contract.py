from benchmarks.samples.negative_control_trace import load_negative_control_trace
from benchmarks.samples.adversarial_trace import load_adversarial_trace
from kernel.debugger import ReasoningDebugger

def test_strict_evaluation_negative_and_adversarial():
    debugger = ReasoningDebugger()

    # 1. Negative Control Test
    clean_trace = load_negative_control_trace()
    findings_clean = debugger.debug(clean_trace)
    assert len(findings_clean) == 0, f"Negative Control Failed: False positive detected {findings_clean}"

    # 2. Adversarial Test
    adv_trace = load_adversarial_trace()
    findings_adv = debugger.debug(adv_trace)

    assert len(findings_adv) == 1, "Adversarial Failed: Did not detect the isolated error."
    finding = findings_adv[0]

    assert finding.first_failure_event_id == "inf-bad", "Adversarial Failed: Pinpointed wrong root cause."
    assert len(finding.downstream_event_ids) == 0, f"Adversarial Failed: False propagation! Impacted: {finding.downstream_event_ids}"
