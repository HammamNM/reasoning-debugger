import json
import sys
from clinical_auditor.evaluator import ClinicalRuleEvaluator

def generate_unified_report(case_path, trace_data, agent_id="LLM_Pilot_v1"):
    evaluator = ClinicalRuleEvaluator(case_path=case_path)
    result = evaluator.evaluate_trace(trace_data)
    
    report = {
        "case_id": evaluator.case_data.get("case_id", "UNKNOWN"),
        "target_rule": evaluator.case_data.get("target_rule", "UNKNOWN"),
        "agent_id": agent_id,
        "evaluation_status": result.get("status", "ERROR"),
        "clinical_findings": [],
        "reasoning_findings": [],
        "evidence_mapped": result.get("evidence", {}).get("found_actions", {})
    }
    
    # فصل النتائج بناءً على نوع التقييم
    if evaluator.require_kernel_validation:
        if result.get("status") == "FAIL":
            report["reasoning_findings"].append({
                "type": result.get("finding"),
                "method": result.get("evaluation_method"),
                "details": result.get("kernel_result")
            })
    else:
        if result.get("status") == "FAIL":
            report["clinical_findings"] = result.get("failures", [])
            
    return report

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python orchestrator/unified_audit.py <case_file.json> <trace_file.json>")
        sys.exit(1)
        
    case_file = sys.argv[1]
    trace_file = sys.argv[2]
    
    with open(trace_file, 'r') as f:
        trace_data = json.load(f)
        
    report = generate_unified_report(case_file, trace_data)
    print(json.dumps(report, indent=2))
