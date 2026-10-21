filepath = 'kernel/reasoning_failure_detector.py'

with open(filepath, 'r', encoding='utf-8') as f:
    code = f.read()

# التأكد من عدم تكرار الترقيع
if "Phase 23A Patch" not in code:
    code += """

# --- Phase 23A Patch: Unanchored Inference Detection ---
_OriginalUnsupportedAssumptionDetector = UnsupportedAssumptionDetector

class UnsupportedAssumptionDetector(_OriginalUnsupportedAssumptionDetector):
    def detect(self, trace):
        # 1. تشغيل الفحوصات الأصلية للحفاظ على التوافقية (Backward Compatibility)
        findings = super().detect(trace)
        
        # 2. إضافة الفحص الهيكلي الجديد (INVESTIGATION -> INFERENCE)
        events = getattr(trace, 'events', tuple())
        for i in range(1, len(events)):
            prev = events[i-1]
            curr = events[i]
            
            # إذا قام الوكيل بفعل ولم ينتظر أو يحصل على دليل، وقفز مباشرة لاستنتاج
            if prev.event_type == 'INVESTIGATION' and curr.event_type == 'INFERENCE':
                from kernel.api import DebugFinding
                findings.append(DebugFinding(
                    event_id=curr.id,
                    failure_type='UNSUPPORTED_REASONING',
                    explanation=f"Unsupported Cognitive Leap: Inference '{curr.id}' directly followed investigation '{prev.id}' with no intervening evidence.",
                    affected_event_ids=(curr.id,)
                ))
                
        return findings
"""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(code)
    print("Detector successfully patched with Phase 23A structural signature.")
else:
    print("Patch already applied.")
