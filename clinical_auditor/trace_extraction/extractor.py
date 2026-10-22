import json
import uuid

class TraceExtractor:
    """
    يستقبل البيانات المستخرجة (بواسطة LLM Parser) بصيغتها الخام، 
    ويقوم بفلترتها وتحويلها إلى الصيغة الصارمة التي يقبلها المقيّم (Evaluator).
    """
    def __init__(self):
        self.allowed_event_types = {"ACTION", "INFERENCE", "OBSERVATION", "EVIDENCE"}

    def process_llm_extraction(self, parsed_json):
        """يحول مخرجات الـ Parser إلى Agent Trace نظيف"""
        trace_events = []
        event_map = {}
        
        # 1. بناء الأحداث الأساسية
        for item in parsed_json.get("events", []):
            event_id = item.get("event_id", str(uuid.uuid4()))
            e_type = item.get("event_type", "UNKNOWN")
            
            # تجاهل أي نوع حدث غير مدعوم
            if e_type not in self.allowed_event_types:
                continue
                
            event = {
                "id": event_id,
                "event_type": e_type,
                "content": item.get("source_span", "No text provided"),
                "metadata": {}
            }
            
            # تعيين البيانات الوصفية السريرية (ACTIONS)
            if e_type == "ACTION" and "action_code" in item:
                # نأخذ فقط الإجراءات التي اقترحها أو نفذها النموذج صراحة
                if item.get("assertion_status") in ["PROPOSED", "REPORTED_PERFORMED"]:
                    event["metadata"]["action_code"] = item["action_code"]
                
            # تعيين البيانات الوصفية الاستدلالية (INFERENCES) للنواة
            if e_type == "INFERENCE":
                if "inference_code" in item:
                    event["metadata"]["inference_code"] = item["inference_code"]
                # نطلب الدعم فقط إذا كان الاستنتاج حاسماً
                if item.get("assertion_status") == "DEFINITIVE":
                    event["metadata"]["support_required"] = True
            
            trace_events.append(event)
            event_map[event_id] = event

        # 2. بناء العلاقات المدعومة (SUPPORTED_BY)
        # لا ننشئ الرابط إلا إذا صرح النموذج به في المخرجات
        for rel in parsed_json.get("relations", []):
            if rel.get("relation_type") == "CLAIMS_SUPPORT":
                src_id = rel.get("source_event_id") # الدليل
                tgt_id = rel.get("target_event_id") # الاستنتاج
                
                if tgt_id in event_map and src_id in event_map:
                    if "supported_by" not in event_map[tgt_id]["metadata"]:
                        event_map[tgt_id]["metadata"]["supported_by"] = []
                    event_map[tgt_id]["metadata"]["supported_by"].append(src_id)

        return trace_events

if __name__ == "__main__":
    # محاكاة لما سيستخرجه نموذج لغوي (LLM Parser) من نص غير مهيكل
    mock_llm_parsed_data = {
        "source_response_id": "LLM_RESP_002",
        "events": [
            {
                "event_id": "E1",
                "event_type": "OBSERVATION",
                "source_span": "ECG shows ST elevation",
                "assertion_status": "OBSERVED_RESULT"
            },
            {
                "event_id": "E2",
                "event_type": "INFERENCE",
                "inference_code": "STEMI",
                "source_span": "The patient has a confirmed STEMI.",
                "assertion_status": "DEFINITIVE"
            }
        ],
        "relations": [
            {
                "relation_type": "CLAIMS_SUPPORT",
                "source_event_id": "E1",
                "target_event_id": "E2",
                "evidence_span": "Based on the ECG, the patient has a confirmed STEMI."
            }
        ]
    }
    
    extractor = TraceExtractor()
    final_trace = extractor.process_llm_extraction(mock_llm_parsed_data)
    
    print("=== FINAL EXTRACTED AGENT TRACE ===")
    print(json.dumps(final_trace, indent=2))
