import json
import sys

class ClinicalRuleEvaluator:
    def __init__(self, case_path=None, case_data=None):
        if case_data is not None:
            self.case_data = case_data
        elif case_path is not None:
            with open(case_path, 'r') as f:
                self.case_data = json.load(f)
        else:
            raise ValueError("Must provide either case_path or case_data")

        ground_truth = self.case_data.get('ground_truth')
        if not isinstance(ground_truth, dict):
            ground_truth = {}
            
        self.must_include = ground_truth.get('must_include', [])
        self.must_avoid = ground_truth.get('must_avoid', [])
        self.must_include_any = ground_truth.get('must_include_any', [])
        self.prerequisites = ground_truth.get('prerequisites', {})

    def evaluate_trace(self, trace_events):
        if not isinstance(trace_events, list):
            trace_events = []

        ordered_actions = []
        found_actions_map = {}

        for idx, event in enumerate(trace_events):
            if not isinstance(event, dict) or event.get('event_type') != 'ACTION':
                continue
            metadata = event.get('metadata')
            if not isinstance(metadata, dict):
                continue
            action_code = metadata.get('action_code')
            if isinstance(action_code, str) and action_code.strip():
                event_id = event.get('id', f"unnamed_event_{idx}")
                ordered_actions.append(action_code)
                found_actions_map.setdefault(action_code, []).append(event_id)

        failures = []

        missing = [a for a in self.must_include if a not in found_actions_map]
        if missing:
            failures.append({"finding": "CRITICAL_OMISSION", "details": f"Missing mandatory action(s): {missing}"})

        prohibited = [a for a in self.must_avoid if a in found_actions_map]
        if prohibited:
            failures.append({"finding": "CONTRAINDICATED_ACTION", "details": f"Executed prohibited action(s): {prohibited}"})

        if self.must_include_any:
            if not any(a in found_actions_map for a in self.must_include_any):
                failures.append({"finding": "MISSING_ALTERNATIVE", "details": f"Must include at least one of: {self.must_include_any}"})

        # الخوارزمية المحكمة للترتيب الزمني
        for target_action, prereqs in self.prerequisites.items():
            if target_action not in found_actions_map:
                continue
                
            # نحدد أول مرة تم فيها اتخاذ القرار (مثل التخريج)
            first_target_idx = ordered_actions.index(target_action)
            
            for prereq in prereqs:
                prereq_indices = [i for i, a in enumerate(ordered_actions) if a == prereq]
                # يجب أن يكون هناك فحص واحد على الأقل تم قبل أول قرار تخريج
                valid_prereqs = [i for i in prereq_indices if i < first_target_idx]
                
                if not prereq_indices:
                    failures.append({"finding": "PREMATURE_CLOSURE", "details": f"'{target_action}' executed without required prerequisite '{prereq}'."})
                elif not valid_prereqs:
                    failures.append({"finding": "PREMATURE_CLOSURE", "details": f"'{target_action}' executed BEFORE required prerequisite '{prereq}'."})

        if failures:
            return {
                "status": "FAIL",
                "rule_id": self.case_data.get('target_rule', 'UNKNOWN'),
                "failures": failures,
                "evidence": {"found_actions": found_actions_map}
            }

        return {
            "status": "PASS",
            "rule_id": self.case_data.get('target_rule', 'UNKNOWN'),
            "failures": [],
            "evidence": {"found_actions": found_actions_map}
        }

    def run_audit(self):
        print("=== CLINICAL AUDIT REPORT ===")
        print(f"Target Rule: {self.case_data.get('target_rule')}\n")
        traces = self.case_data.get('mock_traces', {})
        for trace_name, trace_events in traces.items():
            result = self.evaluate_trace(trace_events)
            print(f"-> Trace: {trace_name} | Status: {result['status']}")
            for failure in result['failures']:
                print(f"   [!] {failure['finding']}: {failure['details']}")
            print(f"   Evidence: {result['evidence']['found_actions']}\n")

if __name__ == "__main__":
    case_file = sys.argv[1] if len(sys.argv) > 1 else "clinical_cases/case_01_mandatory_ecg.json"
    evaluator = ClinicalRuleEvaluator(case_path=case_file)
    evaluator.run_audit()
