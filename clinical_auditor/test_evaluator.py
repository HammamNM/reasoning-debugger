import pytest
from clinical_auditor.evaluator import ClinicalRuleEvaluator

@pytest.fixture
def base_case():
    return {
        "ground_truth": {"must_include": ["ORDER_ECG"]}
    }

def test_null_and_malformed_metadata_handled_gracefully(base_case):
    evaluator = ClinicalRuleEvaluator(case_data=base_case)
    trace = [
        {"id": "e1", "event_type": "ACTION"},                           # Missing metadata
        {"id": "e2", "event_type": "ACTION", "metadata": None},         # Null metadata
        {"id": "e3", "event_type": "ACTION", "metadata": "invalid"},    # String metadata
        {"id": "e4", "event_type": "ACTION", "metadata": ["list"]},     # List metadata
        {"id": "e5", "event_type": "ACTION", "metadata": {"action_code": "ORDER_ECG"}}
    ]
    result = evaluator.evaluate_trace(trace)
    assert result["status"] == "PASS"
    assert result["evidence"]["found_actions"] == {"ORDER_ECG": ["e5"]}
    assert result["evidence"]["missing_actions"] == []

def test_action_in_different_position_and_repeated(base_case):
    evaluator = ClinicalRuleEvaluator(case_data=base_case)
    trace = [
        {"id": "e1", "event_type": "ACTION", "metadata": {"action_code": "HISTORY"}},
        {"id": "e2", "event_type": "ACTION", "metadata": {"action_code": "ORDER_ECG"}},
        {"id": "e3", "event_type": "ACTION", "metadata": {"action_code": "BLOODS"}},
        {"id": "e4", "event_type": "ACTION", "metadata": {"action_code": "ORDER_ECG"}}
    ]
    result = evaluator.evaluate_trace(trace)
    assert result["status"] == "PASS"
    assert result["evidence"]["found_actions"]["ORDER_ECG"] == ["e2", "e4"]

def test_malformed_events_ignored(base_case):
    evaluator = ClinicalRuleEvaluator(case_data=base_case)
    trace = [
        "not a dictionary",
        None,
        123,
        {"id": "e1", "event_type": "INFERENCE", "metadata": {"action_code": "ORDER_ECG"}},
        {"id": "e2", "event_type": "ACTION", "metadata": {"action_code": "ORDER_ECG"}}
    ]
    result = evaluator.evaluate_trace(trace)
    assert result["status"] == "PASS"
    assert result["evidence"]["found_actions"] == {"ORDER_ECG": ["e2"]}

def test_critical_omission_structured_evidence(base_case):
    evaluator = ClinicalRuleEvaluator(case_data=base_case)
    trace = [
        {"id": "e1", "event_type": "ACTION", "metadata": {"action_code": "OXYGEN"}}
    ]
    result = evaluator.evaluate_trace(trace)
    assert result["status"] == "FAIL"
    assert result["finding"] == "CRITICAL_OMISSION"
    assert result["evidence"]["missing_actions"] == ["ORDER_ECG"]
    assert result["evidence"]["found_actions"] == {"OXYGEN": ["e1"]}
