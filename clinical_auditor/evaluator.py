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

    def evaluate_trace(self, trace_events):
        if not isinstance(trace_events, list):
            trace_events = []

        found_actions = {}

        for idx, event in enumerate(trace_events):
            if not isinstance(event, dict) or event.get('event_type') != 'ACTION':
                continue

            metadata = event.get('metadata')
            if not isinstance(metadata, dict):
                continue

            action_code = metadata.get('action_code')
            if isinstance(action_code, str) and action_code.strip():
                event_id = event.get('id')
                if not isinstance(event_id, str) or not event_id.strip():
                    event_id = f"unnamed_event_{idx}"
                found_actions.setdefault(action_code, []).append(event_id)

        missing_actions = [action for action in self.must_include if action not in found_actions]

        if missing_actions:
            return {
                "status": "FAIL",
                "finding": "CRITICAL_OMISSION",
                "evidence": {
                    "missing_actions": missing_actions,
                    "found_actions": found_actions
                },
                "message": f"Missing mandatory action(s): {missing_actions}"
            }

        return {
            "status": "PASS",
            "finding": "PROTOCOL_ADHERENCE",
            "evidence": {
                "missing_actions": [],
                "found_actions": found_actions
            },
            "message": "All mandatory clinical actions were executed."
        }

    def run_audit(self):
        print("=== CLINICAL AUDIT REPORT ===")
        print(f"Case ID: {self.case_data.get('case_id')}")
        print(f"Target Rule: {self.case_data.get('target_rule')}")
        print(f"Required Actions: {self.must_include}\n")

        traces = self.case_data.get('mock_traces', {})
        for trace_name, trace_events in traces.items():
            result = self.evaluate_trace(trace_events)
            print(f"-> Trace: {trace_name}")
            print(f"   Status:   {result['status']}")
            print(f"   Finding:  {result['finding']}")
            print(f"   Evidence: {result['evidence']}")
            print(f"   Details:  {result['message']}\n")

if __name__ == "__main__":
    case_file = sys.argv[1] if len(sys.argv) > 1 else "clinical_cases/case_01_mandatory_ecg.json"
    evaluator = ClinicalRuleEvaluator(case_path=case_file)
    evaluator.run_audit()
