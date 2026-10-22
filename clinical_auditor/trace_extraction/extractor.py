import json
import uuid

class TraceExtractor:
    def __init__(self):
        self.allowed_event_types = {"ACTION", "INFERENCE", "OBSERVATION", "EVIDENCE"}
        
        # قاموس توحيد المصطلحات لمنع فشل التقييم بسبب المرادفات
        self.canonical_actions = {
            "PERFORM_ECG": "ORDER_ECG",
            "OBTAIN_ECG": "ORDER_ECG",
            "12_LEAD_ECG": "ORDER_ECG",
            "GIVE_HEPARIN": "ADMINISTER_HEPARIN",
            "START_HEPARIN": "ADMINISTER_HEPARIN",
            "SEND_HOME": "DISCHARGE",
            "DISCHARGE_PATIENT": "DISCHARGE",
            "CHECK_TROPONIN": "ORDER_TROPONIN"
        }

    def verify_span(self, span_text, original_text):
        """يتحقق برمجياً من أن المقطع المقتبس موجود فعلياً في النص الأصلي"""
        if not original_text:
            return True # تجاوز الفحص إذا لم يتم تمرير النص الأصلي
        clean_span = " ".join(span_text.lower().split())
        clean_orig = " ".join(original_text.lower().split())
        return clean_span in clean_orig

    def process_llm_extraction(self, parsed_json, original_text=None):
        trace_events = []
        event_map = {}
        rejected_events = []
        
        for item in parsed_json.get("events", []):
            event_id = item.get("event_id", str(uuid.uuid4()))
            e_type = item.get("event_type", "UNKNOWN")
            span = item.get("source_span", "")
            
            if e_type not in self.allowed_event_types:
                continue
                
            # الضمانة الأولى: رفض الحدث إذا اخترعه المستخرج ولم يكن في النص الأصلي
            if original_text and not self.verify_span(span, original_text):
                rejected_events.append({"id": event_id, "reason": "SPAN_NOT_IN_SOURCE", "span": span})
                continue
                
            event = {
                "id": event_id,
                "event_type": e_type,
                "content": span,
                "metadata": {}
            }
            
            # معالجة الإجراءات والملاحظات السريرية
            if e_type in ["ACTION", "OBSERVATION"]:
                raw_code = item.get("action_code") or item.get("observation_code")
                if raw_code:
                    # توحيد الكود مع القاموس القياسي
                    normalized_code = self.canonical_actions.get(raw_code, raw_code)
                    
                    if e_type == "ACTION" and item.get("assertion_status") in ["PROPOSED", "REPORTED_PERFORMED"]:
                        event["metadata"]["action_code"] = normalized_code
                    elif e_type == "OBSERVATION" and item.get("assertion_status") == "OBSERVED_RESULT":
                        # نضعها في action_code أيضاً لكي يلتقطها المقيّم السريري في الترتيب الزمني
                        event["metadata"]["action_code"] = normalized_code
                
            # معالجة الاستنتاجات للنواة
            if e_type == "INFERENCE":
                if "inference_code" in item:
                    event["metadata"]["inference_code"] = item["inference_code"]
                if item.get("assertion_status") == "DEFINITIVE":
                    event["metadata"]["support_required"] = True
            
            trace_events.append(event)
            event_map[event_id] = event

        # بناء العلاقات المدعومة (فقط إذا كانت موثقة بنص موجود فعلياً)
        for rel in parsed_json.get("relations", []):
            if rel.get("relation_type") == "CLAIMS_SUPPORT":
                src_id = rel.get("source_event_id")
                tgt_id = rel.get("target_event_id")
                ev_span = rel.get("evidence_span", "")
                
                if original_text and ev_span and not self.verify_span(ev_span, original_text):
                    continue
                    
                if tgt_id in event_map and src_id in event_map:
                    if "supported_by" not in event_map[tgt_id]["metadata"]:
                        event_map[tgt_id]["metadata"]["supported_by"] = []
                    event_map[tgt_id]["metadata"]["supported_by"].append(src_id)

        return trace_events, rejected_events
