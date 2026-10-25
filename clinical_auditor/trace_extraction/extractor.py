import re

class TraceExtractor:
    """
    Tier 1: Deterministic Span Verification Firewall & Epistemic Assertion Calibrator.
    """
    def __init__(self):
        self.canonical_actions = {
            # ECG Synonyms
            "PERFORM_ECG": "ORDER_ECG",
            "OBTAIN_ECG": "ORDER_ECG",
            "12_LEAD_ECG": "ORDER_ECG",
            "STAT_ECG": "ORDER_ECG",
            # Troponin Synonyms
            "CHECK_TROPONIN": "ORDER_TROPONIN",
            "SERIAL_TROPONIN": "ORDER_TROPONIN",
            "HIGH_SENSITIVITY_TROPONIN": "ORDER_TROPONIN",
            # Discharge Synonyms
            "SEND_HOME": "DISCHARGE",
            "DISCHARGE_PATIENT": "DISCHARGE",
            # Anticoagulation / Thrombolysis Synonyms
            "START_HEPARIN": "ADMINISTER_HEPARIN",
            "IV_HEPARIN": "ADMINISTER_HEPARIN",
            "HEPARIN_BOLUS": "ADMINISTER_HEPARIN",
            "GIVE_THROMBOLYTICS": "ADMINISTER_THROMBOLYTICS",
            "FIBRINOLYTIC_THERAPY": "ADMINISTER_THROMBOLYTICS",
            "SYSTEMIC_THROMBOLYSIS": "ADMINISTER_THROMBOLYTICS",
            # Nitrates & Vasodilators
            "GIVE_NITROGLYCERIN": "ADMINISTER_NITROGLYCERIN",
            "SUBLINGUAL_NITROGLYCERIN": "ADMINISTER_NITROGLYCERIN",
            "GIVE_NITROPRUSSIDE": "ADMINISTER_VASODILATOR",
            "IV_NITROPRUSSIDE": "ADMINISTER_VASODILATOR",
            # Beta-Blockers & Benzodiazepines & Diuretics
            "GIVE_BETA_BLOCKER": "ADMINISTER_BETA_BLOCKER",
            "IV_METOPROLOL": "ADMINISTER_BETA_BLOCKER",
            "ORAL_METOPROLOL": "ADMINISTER_BETA_BLOCKER",
            "IV_LORAZEPAM": "ADMINISTER_BENZODIAZEPINES",
            "IV_DIAZEPAM": "ADMINISTER_BENZODIAZEPINES",
            "GIVE_BENZODIAZEPINES": "ADMINISTER_BENZODIAZEPINES",
            "GIVE_FUROSEMIDE": "ADMINISTER_DIURETICS",
            # Procedures & Advanced Imaging
            "NEEDLE_DECOMPRESSION": "IMMEDIATE_PLEURAL_DECOMPRESSION",
            "FINGER_THORACOSTOMY": "IMMEDIATE_PLEURAL_DECOMPRESSION",
            "CHEST_TUBE_DECOMPRESSION": "IMMEDIATE_PLEURAL_DECOMPRESSION",
            "EMERGENCY_PERICARDIOCENTESIS": "URGENT_PERICARDIOCENTESIS",
            "PERFORM_PERICARDIOCENTESIS": "URGENT_PERICARDIOCENTESIS",
            "CT_ESOPHAGRAM": "ORDER_CT_ESOPHAGRAM",
            "CT_CHEST_CONTRAST": "ORDER_CT_ESOPHAGRAM"
        }

    def normalize_text(self, text: str) -> str:
        if not text:
            return ""
        return re.sub(r"\s+", " ", text.strip().lower())

    def verify_span(self, span: str, raw_text: str) -> bool:
        if raw_text is None:
            return True
        if not span or not span.strip():
            return False
        return self.normalize_text(span) in self.normalize_text(raw_text)

    def normalize_action(self, code: str) -> str:
        if not code:
            return code
        code_upper = code.strip().upper()
        return self.canonical_actions.get(code_upper, code_upper)

    def process_llm_extraction(self, extraction_json: dict, raw_text: str = None):
        clean_trace = []
        rejected_events = []

        events = extraction_json.get("events", [])
        relations = extraction_json.get("relations", [])

        # Map support relations targeting inference events
        supported_targets = {}
        for rel in relations:
            if rel.get("relation_type") == "CLAIMS_SUPPORT":
                tgt = rel.get("target_event_id")
                src = rel.get("source_event_id")
                if tgt and src:
                    supported_targets.setdefault(tgt, []).append(src)

        for idx, ev in enumerate(events):
            span = ev.get("source_span", "")
            if not self.verify_span(span, raw_text):
                rejected_events.append({
                    "event_id": ev.get("event_id", f"E_{idx}"),
                    "reason": "SPAN_NOT_IN_SOURCE",
                    "attempted_span": span
                })
                continue

            assertion = ev.get("assertion_status", "PROPOSED").upper()
            # Filter out negated statements so warnings are not penalized as executed actions
            if assertion == "NEGATED":
                continue

            ev_type = ev.get("event_type", "ACTION").upper()
            ev_id = ev.get("event_id", f"e_{idx+1}")
            metadata = {"assertion_status": assertion, "source_span": span}

            if ev_type == "ACTION":
                raw_code = ev.get("action_code", "")
                norm_code = self.normalize_action(raw_code)
                metadata["action_code"] = norm_code
                content = f"Action: {norm_code}"
            elif ev_type == "OBSERVATION":
                obs_code = ev.get("observation_code") or ev.get("action_code", "")
                metadata["action_code"] = obs_code
                content = f"Observation: {obs_code}"
                ev_type = "ACTION"  # Compatible with temporal ordering checks
            elif ev_type == "INFERENCE":
                inf_code = ev.get("inference_code", "UNKNOWN_INFERENCE")
                metadata["inference_code"] = inf_code
                # Only DEFINITIVE diagnostic claims require strict graph proof
                metadata["support_required"] = (assertion == "DEFINITIVE")
                if ev_id in supported_targets:
                    metadata["supports"] = supported_targets[ev_id]
                content = f"Inference: {inf_code} ({assertion})"
            else:
                content = span

            clean_trace.append({
                "id": ev_id,
                "event_type": ev_type,
                "content": content,
                "metadata": metadata
            })

        return clean_trace, rejected_events
