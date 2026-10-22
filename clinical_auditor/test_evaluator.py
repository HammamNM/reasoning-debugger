import pytest
from clinical_auditor.evaluator import ClinicalRuleEvaluator

@pytest.fixture
def base_case():
    return {"ground_truth": {"must_include": ["ORDER_ECG"]}}

def create_trace(*action_codes):
    return [{"id": f"e{i}", "event_type": "ACTION", "metadata": {"action_code": code}} for i, code in enumerate(action_codes)]

# --- Robustness Tests ---
def test_null_and_malformed_metadata_handled_gracefully(base_case):
    evaluator = ClinicalRuleEvaluator(case_data=base_case)
    trace = [
        {"id": "e1", "event_type": "ACTION"},
        {"id": "e2", "event_type": "ACTION", "metadata": None},
        {"id": "e3", "event_type": "ACTION", "metadata": "invalid"},
        {"id": "e5", "event_type": "ACTION", "metadata": {"action_code": "ORDER_ECG"}}
    ]
    assert evaluator.evaluate_trace(trace)["status"] == "PASS"

def test_malformed_events_ignored(base_case):
    evaluator = ClinicalRuleEvaluator(case_data=base_case)
    trace = ["not dict", None, {"id": "e2", "event_type": "ACTION", "metadata": {"action_code": "ORDER_ECG"}}]
    assert evaluator.evaluate_trace(trace)["status"] == "PASS"

# --- Clinical Rule Tests ---
def test_must_avoid_detects_contraindication():
    case = {"target_rule": "RULE_03", "ground_truth": {"must_avoid": ["HEPARIN"]}}
    evaluator = ClinicalRuleEvaluator(case_data=case)
    assert evaluator.evaluate_trace(create_trace("ORDER_ECG", "ORDER_CTA_AORTA"))["status"] == "PASS"
    assert evaluator.evaluate_trace(create_trace("ORDER_ECG", "HEPARIN"))["status"] == "FAIL"

def test_prerequisites_detects_premature_closure():
    case = {"target_rule": "RULE_02", "ground_truth": {"prerequisites": {"DISCHARGE": ["ORDER_ECG", "ORDER_TROPONIN"]}}}
    evaluator = ClinicalRuleEvaluator(case_data=case)
    
    # 1. Valid
    assert evaluator.evaluate_trace(create_trace("ORDER_ECG", "ORDER_TROPONIN", "DISCHARGE"))["status"] == "PASS"
    
    # 2. Invalid: Discharge BEFORE Troponin (even if Troponin is ordered later)
    fail_order = evaluator.evaluate_trace(create_trace("ORDER_ECG", "DISCHARGE", "ORDER_TROPONIN"))
    assert fail_order["status"] == "FAIL"
    assert "BEFORE required prerequisite" in fail_order["failures"][0]["details"]

    # 3. Invalid: Multiple discharges, the first one is premature
    fail_multi = evaluator.evaluate_trace(create_trace("DISCHARGE", "ORDER_ECG", "ORDER_TROPONIN", "DISCHARGE"))
    assert fail_multi["status"] == "FAIL"

def test_must_include_any_detects_missing_alternatives():
    case = {"target_rule": "RULE_04", "ground_truth": {"must_include_any": ["ORDER_CTPA", "ORDER_DDIMER"]}}
    evaluator = ClinicalRuleEvaluator(case_data=case)
    assert evaluator.evaluate_trace(create_trace("ORDER_CTPA"))["status"] == "PASS"
    assert evaluator.evaluate_trace(create_trace("ORDER_ECG"))["status"] == "FAIL"
