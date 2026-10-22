import pytest
from clinical_auditor.evaluator import ClinicalRuleEvaluator

@pytest.fixture
def kernel_case():
    return {
        "target_rule": "RULE_05_UNSUPPORTED_INFERENCE",
        "ground_truth": {"require_kernel_validation": True}
    }

def test_kernel_integration_supported_inference(kernel_case):
    evaluator = ClinicalRuleEvaluator(case_data=kernel_case)
    trace = [
        {"id": "ev1", "event_type": "EVIDENCE", "content": "ECG shows ST elevation"},
        {"id": "inf1", "event_type": "INFERENCE", "content": "Patient has STEMI", "metadata": {"supported_by": ["ev1"], "support_required": True}}
    ]
    result = evaluator.evaluate_trace(trace)
    assert result["status"] == "PASS"
    assert result["evaluation_method"] == "KERNEL_STRUCTURAL_DETECTION"

def test_kernel_integration_unsupported_inference(kernel_case):
    evaluator = ClinicalRuleEvaluator(case_data=kernel_case)
    trace = [
        {"id": "inf1", "event_type": "INFERENCE", "content": "Patient has STEMI", "metadata": {"support_required": True}}
    ]
    result = evaluator.evaluate_trace(trace)
    assert result["status"] == "FAIL"
    assert result["finding"] == "UNSUPPORTED_INFERENCE"
    assert result["kernel_result"]["pattern_id"] == "RP-001"

def test_kernel_adapter_preserves_attributes(kernel_case):
    evaluator = ClinicalRuleEvaluator(case_data=kernel_case)
    trace = [
        {"id": "custom_id_99", "event_type": "INVESTIGATION", "content": "Lab test"}
    ]
    result = evaluator.evaluate_trace(trace)
    assert result["status"] == "PASS"

def test_kernel_integration_malformed_trace(kernel_case):
    evaluator = ClinicalRuleEvaluator(case_data=kernel_case)
    trace = [
        "not a dict",
        {"event_type": "INFERENCE", "metadata": {"support_required": True}}
    ]
    result = evaluator.evaluate_trace(trace)
    assert result["status"] == "FAIL"
    assert result["finding"] == "UNSUPPORTED_INFERENCE"
