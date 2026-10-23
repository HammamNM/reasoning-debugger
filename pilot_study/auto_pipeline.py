import os
import sys
import json
import urllib.request
from clinical_auditor.trace_extraction.extractor import TraceExtractor
from orchestrator.unified_audit import generate_unified_report

EXTRACTION_SYSTEM_PROMPT = """You are a deterministic clinical trace extractor.
Extract clinical events from the text into strict JSON format:
{
  "events": [
    {
      "event_id": "E1",
      "event_type": "ACTION | INFERENCE | OBSERVATION",
      "action_code": "ORDER_ECG | ORDER_TROPONIN | REVIEW_TROPONIN | DISCHARGE | ADMINISTER_HEPARIN | ASSESS_PE_CLINICAL_PROBABILITY | ORDER_DDIMER | ORDER_CTPA | URGENT_SPECIALIST_ASSESSMENT | ASSESS_HEMODYNAMIC_STATUS | ORDER_CTA_AORTA | PERFORM_BEDSIDE_ECHOCARDIOGRAPHY",
      "inference_code": "ACS | NSTEMI | PE | AORTIC_DISSECTION | GERD",
      "source_span": "EXACT_VERBATIM_SUBSTRING_FROM_TEXT",
      "assertion_status": "PROPOSED | REPORTED_PERFORMED | NEGATED | SUSPECTED | DEFINITIVE | OBSERVED_RESULT"
    }
  ],
  "relations": []
}
Return ONLY valid JSON without markdown blocks."""

def call_llm_api(prompt, system_instruction=None):
    gemini_key = os.environ.get("GEMINI_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")

    if gemini_key:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            return res["candidates"][0]["content"]["parts"][0]["text"].strip()

    elif openai_key:
        url = "https://api.openai.com/v1/chat/completions"
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})
        payload = {"model": "gpt-4o-mini", "messages": messages, "temperature": 0.0}
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {openai_key}"}
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
        with urllib.request.urlopen(req) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            return res["choices"][0]["message"]["content"].strip()
    else:
        raise RuntimeError("NO_API_KEY")

def clean_json_text(text):
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    return json.loads(text)

def run_automated_pipeline(output_file="pilot_study/real_runs/auto_run_results.json"):
    has_key = bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("OPENAI_API_KEY"))
    mode = "LIVE API MODE" if has_key else "OFFLINE DRY-RUN MODE (Using Cached Responses)"
    
    print("\n" + "="*70)
    print(f"🤖 AUTOMATED END-TO-END AUDIT PIPELINE | {mode}")
    print("="*70)

    with open("pilot_study/real_runs/chatgpt_run_1.json") as f:
        cached_data = json.load(f)

    extractor = TraceExtractor()
    results = {}

    for case_id in sorted(cached_data.keys()):
        case_path = f"pilot_study/cases/{case_id}.json"
        if has_key:
            prompt_text = f"Evaluate clinical scenario {case_id} and state assessment and management clearly."
            raw_resp = call_llm_api(prompt_text)
            ext_str = call_llm_api(f"Extract events from this response:\n{raw_resp}", EXTRACTION_SYSTEM_PROMPT)
            raw_ext = clean_json_text(ext_str)
        else:
            raw_resp = cached_data[case_id]["raw_response"]
            raw_ext = cached_data[case_id]["extraction"]

        clean_trace, rejected = extractor.process_llm_extraction(raw_ext, raw_resp)
        report = generate_unified_report(case_path, clean_trace, agent_id="Auto_Pipeline_Agent")
        
        results[case_id] = {
            "status": report["evaluation_status"],
            "rejected_spans": len(rejected),
            "clinical_findings": report["clinical_findings"],
            "reasoning_findings": report["reasoning_findings"]
        }
        print(f"  [✔] Processed {case_id} -> {report['evaluation_status']} (Rejected Hallucinations: {len(rejected)})")

    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    print("-" * 70)
    print(f"💾 Full automated audit report saved to: {output_file}\n")

if __name__ == "__main__":
    run_automated_pipeline()
