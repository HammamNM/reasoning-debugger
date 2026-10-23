import json
import sys
from clinical_auditor.trace_extraction.extractor import TraceExtractor
from orchestrator.unified_audit import generate_unified_report

def run_full_benchmark(batch_file, model_name="Target_LLM"):
    with open(batch_file, 'r') as f:
        batch_data = json.load(f)
        
    extractor = TraceExtractor()
    
    print(f"\n{'='*65}")
    print(f"📊 CLINICAL & STRUCTURAL BENCHMARK REPORT: {model_name}")
    print(f"{'='*65}")
    print(f"{'CASE ID':<15} | {'STATUS':<8} | {'REJECTED':<8} | {'DETECTED VIOLATIONS / FINDINGS'}")
    print(f"{'-'*65}")
    
    passed = 0
    total = len(batch_data)
    
    for case_id in sorted(batch_data.keys()):
        item = batch_data[case_id]
        orig_text = item.get("raw_response", "")
        raw_extraction = item.get("extraction", {})
        case_path = f"pilot_study/cases/{case_id}.json"
        
        clean_trace, rejected = extractor.process_llm_extraction(raw_extraction, orig_text)
        report = generate_unified_report(case_path, clean_trace, agent_id=model_name)
        
        status = report['evaluation_status']
        if status == 'PASS':
            passed += 1
            status_str = "✅ PASS"
        else:
            status_str = "❌ FAIL"
            
        findings = []
        for cf in report.get('clinical_findings', []):
            findings.append(f"CLINICAL:{cf['finding']}")
        for rf in report.get('reasoning_findings', []):
            pat = rf.get('details', {}).get('pattern_id', 'RP-001')
            findings.append(f"KERNEL:{rf['type']}({pat})")
            
        findings_str = ", ".join(findings) if findings else "None (Adhered to Protocol)"
        rej_str = f"{len(rejected)} spans" if rejected else "0"
        
        print(f"{case_id:<15} | {status_str:<8} | {rej_str:<8} | {findings_str}")
        
    print(f"{'='*65}")
    print(f"🎯 FINAL SAFETY & REASONING SCORE: {passed}/{total} ({(passed/total)*100:.1f}%)")
    print(f"{'='*65}\n")

if __name__ == "__main__":
    file_path = sys.argv[1] if len(sys.argv[1:]) > 0 else "pilot_study/real_runs/chatgpt_run_1.json"
    model = sys.argv[2] if len(sys.argv) > 2 else "ChatGPT_Pilot"
    run_full_benchmark(file_path, model)
