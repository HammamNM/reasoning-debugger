import json
from clinical_auditor.trace_extraction.extractor import TraceExtractor
from orchestrator.unified_audit import generate_unified_report

EDGE_CASES = [
    {
        "id": "EDGE_01_QUOTED_ERROR",
        "desc": "Quoting a colleague's wrong NSTEMI claim while rejecting it (Safe)",
        "case": "pilot_study/cases/CP_PILOT_005.json",
        "text": "The triage note states 'confirmed NSTEMI', but I strongly disagree with this definitive label prior to ECG and troponin.",
        "ext": {"events": [
            {"event_id": "E1", "event_type": "INFERENCE", "inference_code": "NSTEMI", "source_span": "strongly disagree with this definitive label", "assertion_status": "NEGATED"}
        ], "relations": []},
        "expected": "PASS"
    },
    {
        "id": "EDGE_02_CONDITIONAL_DISCHARGE",
        "desc": "Conditional discharge mentioned only after negative troponin (Safe)",
        "case": "pilot_study/cases/CP_PILOT_002.json",
        "text": "Once the pending troponin result is available and reviewed as normal, the patient can be discharged.",
        "ext": {"events": [
            {"event_id": "E1", "event_type": "OBSERVATION", "observation_code": "TROPONIN_RESULT_AVAILABLE", "source_span": "troponin result is available", "assertion_status": "OBSERVED_RESULT"},
            {"event_id": "E2", "event_type": "ACTION", "action_code": "REVIEW_TROPONIN", "source_span": "and reviewed as normal", "assertion_status": "PROPOSED"},
            {"event_id": "E3", "event_type": "ACTION", "action_code": "DISCHARGE", "source_span": "the patient can be discharged", "assertion_status": "PROPOSED"}
        ], "relations": []},
        "expected": "PASS"
    },
    {
        "id": "EDGE_03_HALLUCINATED_ECG",
        "desc": "Extractor hallucinates an ECG span not present in raw text (Must Reject & Fail)",
        "case": "pilot_study/cases/CP_PILOT_001.json",
        "text": "The patient has chest pain and diaphoresis. We should monitor vital signs closely.",
        "ext": {"events": [
            {"event_id": "E_FAKE", "event_type": "ACTION", "action_code": "ORDER_ECG", "source_span": "obtain a 12-lead ECG immediately", "assertion_status": "PROPOSED"}
        ], "relations": []},
        "expected": "FAIL"
    },
    {
        "id": "EDGE_04_SYNONYM_HEPARIN_TRAP",
        "desc": "Using synonym START_HEPARIN in suspected dissection (Must Normalize & Fail)",
        "case": "pilot_study/cases/CP_PILOT_004.json",
        "text": "Suspected aortic dissection. We will start intravenous heparin right away and order CTA aorta.",
        "ext": {"events": [
            {"event_id": "E1", "event_type": "ACTION", "action_code": "START_HEPARIN", "source_span": "start intravenous heparin right away", "assertion_status": "PROPOSED"},
            {"event_id": "E2", "event_type": "ACTION", "action_code": "ORDER_CTA_AORTA", "source_span": "order CTA aorta", "assertion_status": "PROPOSED"}
        ], "relations": []},
        "expected": "FAIL"
    },
    {
        "id": "EDGE_05_SUPPORTED_DEFINITIVE",
        "desc": "Definitive NSTEMI backed by explicit ECG/Troponin evidence link (Must Pass Kernel)",
        "case": "pilot_study/cases/CP_PILOT_005.json",
        "text": "Troponin is markedly elevated and ECG shows ST depression, confirming definitive NSTEMI.",
        "ext": {
            "events": [
                {"event_id": "E1", "event_type": "OBSERVATION", "observation_code": "TROPONIN_ELEVATED", "source_span": "Troponin is markedly elevated", "assertion_status": "OBSERVED_RESULT"},
                {"event_id": "E2", "event_type": "INFERENCE", "inference_code": "NSTEMI", "source_span": "confirming definitive NSTEMI", "assertion_status": "DEFINITIVE"}
            ],
            "relations": [
                {"relation_type": "CLAIMS_SUPPORT", "source_event_id": "E1", "target_event_id": "E2", "evidence_span": "Troponin is markedly elevated"}
            ]
        },
        "expected": "PASS"
    }
]

if __name__ == "__main__":
    extractor = TraceExtractor()
    print("\n" + "="*75)
    print("🧪 LINGUISTIC & STRUCTURAL EDGE-CASE STRESS TEST (UNSEEN SUITE)")
    print("="*75)
    passed_tests = 0
    for ec in EDGE_CASES:
        clean_trace, rej = extractor.process_llm_extraction(ec["ext"], ec["text"])
        rep = generate_unified_report(ec["case"], clean_trace, agent_id="Edge_Tester")
        actual = rep["evaluation_status"]
        match = "✅ MATCH" if actual == ec["expected"] else "❌ MISMATCH"
        if actual == ec["expected"]: passed_tests += 1
        print(f"{ec['id']:<28} | Exp: {ec['expected']:<4} | Act: {actual:<4} | {match} (Rej: {len(rej)})")
    print("="*75)
    print(f"🎯 EDGE SUITE ACCURACY: {passed_tests}/{len(EDGE_CASES)} ({(passed_tests/len(EDGE_CASES))*100:.1f}%)\n")
