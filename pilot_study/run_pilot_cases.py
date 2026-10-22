import json
from clinical_auditor.trace_extraction.extractor import TraceExtractor
from orchestrator.unified_audit import generate_unified_report

def run_pilot_case(case_id):
    print(f"\n{'='*40}\n[ EVALUATING ] {case_id}")
    
    case_path = f"pilot_study/cases/{case_id}.json"
    extraction_path = f"pilot_study/extracted_traces/{case_id}_extraction.json"
    
    with open(extraction_path) as f: raw_extraction = json.load(f)
    
    extractor = TraceExtractor()
    clean_trace, _ = extractor.process_llm_extraction(raw_extraction, original_text=None) 
    report = generate_unified_report(case_path, clean_trace, agent_id="Synthetic_Test")
    
    if report['evaluation_status'] == 'PASS':
        print("  -> Verdict: ✅ PASS")
    else:
        print("  -> Verdict: ❌ FAIL")
        for cf in report['clinical_findings']:
            print(f"     - CLINICAL: {cf['finding']} -> {cf['details']}")
        for rf in report['reasoning_findings']:
            print(f"     - KERNEL:   {rf['type']}")

if __name__ == "__main__":
    for case in ["CP_PILOT_001", "CP_PILOT_002", "CP_PILOT_003", "CP_PILOT_004", "CP_PILOT_005"]:
        run_pilot_case(case)
    print("\n")
