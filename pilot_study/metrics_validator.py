import json
from clinical_auditor.trace_extraction.extractor import TraceExtractor
from orchestrator.unified_audit import generate_unified_report

def evaluate_dataset(dataset, enable_calibration=True):
    """
    يقارن أحكام النظام بالمرجع البشري (Human Gold Standard)
    Positive (P) = وجود خطأ سريري أو استدلالي (يجب أن يعطي النظام FAIL)
    Negative (N) = مسار آمن وسليم (يجب أن يعطي النظام PASS)
    """
    tp = fp = tn = fn = 0
    extractor = TraceExtractor()
    
    for item in dataset:
        case_path = item["case_path"]
        raw_extraction = json.loads(json.dumps(item["extraction"])) # Deep copy
        gold_status = item["human_gold_verdict"] # "FAIL" (Error exists) or "PASS" (Safe)
        
        if not enable_calibration:
            # محاكاة إيقاف طبقة المعايرة (Ablation: Uncalibrated Extractor)
            for ev in raw_extraction.get("events", []):
                if ev.get("assertion_status") in ["NEGATED", "SUSPECTED"]:
                    if ev.get("event_type") == "ACTION":
                        ev["assertion_status"] = "PROPOSED"
                    elif ev.get("event_type") == "INFERENCE":
                        ev["assertion_status"] = "DEFINITIVE"
                        
        clean_trace, _ = extractor.process_llm_extraction(raw_extraction, item.get("raw_text"))
        report = generate_unified_report(case_path, clean_trace, agent_id="Ablation_Test")
        sys_verdict = report["evaluation_status"]
        
        if gold_status == "FAIL" and sys_verdict == "FAIL":
            tp += 1
        elif gold_status == "PASS" and sys_verdict == "FAIL":
            fp += 1
        elif gold_status == "PASS" and sys_verdict == "PASS":
            tn += 1
        elif gold_status == "FAIL" and sys_verdict == "PASS":
            fn += 1

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0 # Sensitivity
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    return {
        "TP": tp, "FP": fp, "TN": tn, "FN": fn,
        "Precision": precision, "Recall": recall,
        "Specificity": specificity, "F1": f1
    }

if __name__ == "__main__":
    # تجميع مجموعة التحقق المرجعية (10 حالات: 5 اصطناعية + 5 حقيقية من GPT-4o)
    validation_suite = []
    
    # 1. الحالات الاصطناعية الخمس (المعروفة مسبقاً: 001 و 003 سليمة، 002 و 004 و 005 خاطئة)
    synth_gold = {"CP_PILOT_001": "PASS", "CP_PILOT_002": "FAIL", "CP_PILOT_003": "PASS", "CP_PILOT_004": "FAIL", "CP_PILOT_005": "FAIL"}
    for cid, gold in synth_gold.items():
        with open(f"pilot_study/extracted_traces/{cid}_extraction.json") as f:
            validation_suite.append({
                "id": f"SYNTH_{cid}", "case_path": f"pilot_study/cases/{cid}.json",
                "extraction": json.load(f), "raw_text": None, "human_gold_verdict": gold
            })
            
    # 2. الحالات الخمس الحقيقية من GPT-4o (جميعها سليمة سريرياً = PASS)
    with open("pilot_study/real_runs/chatgpt_run_1.json") as f:
        real_run = json.load(f)
        for cid, data in real_run.items():
            validation_suite.append({
                "id": f"REAL_{cid}", "case_path": f"pilot_study/cases/{cid}.json",
                "extraction": data["extraction"], "raw_text": data["raw_response"], "human_gold_verdict": "PASS"
            })

    res_uncal = evaluate_dataset(validation_suite, enable_calibration=False)
    res_cal = evaluate_dataset(validation_suite, enable_calibration=True)

    print("\n" + "="*75)
    print("🔬 ABLATION STUDY: AUDITOR VALIDATION AGAINST HUMAN GOLD STANDARD (N=10)")
    print("="*75)
    print(f"{'CONFIGURATION':<32} | {'TP':<2} {'FP':<2} {'TN':<2} {'FN':<2} | {'RECALL':<7} | {'SPECIF.':<7} | {'F1-SCORE'}")
    print("-" * 75)
    print(f"{'1. Baseline (No Assertion Filt.)':<32} | {res_uncal['TP']:<2} {res_uncal['FP']:<2} {res_uncal['TN']:<2} {res_uncal['FN']:<2} | {res_uncal['Recall']*100:>5.1f}%  | {res_uncal['Specificity']*100:>5.1f}%  | {res_uncal['F1']:.3f}")
    print(f"{'2. Full Hybrid (Calibrated)':<32} | {res_cal['TP']:<2} {res_cal['FP']:<2} {res_cal['TN']:<2} {res_cal['FN']:<2} | {res_cal['Recall']*100:>5.1f}%  | {res_cal['Specificity']*100:>5.1f}%  | {res_cal['F1']:.3f}")
    print("="*75 + "\n")
