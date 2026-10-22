import json
import sys
import dataclasses

class ClinicalRuleEvaluator:
    def __init__(self, case_path=None, case_data=None):
        if case_data is not None:
            self.case_data = case_data
        elif case_path is not None:
            with open(case_path, 'r') as f:
                self.case_data = json.load(f)
        else:
            raise ValueError("Must provide either case_path or case_data")

        ground_truth = self.case_data.get('ground_truth', {})
        if not isinstance(ground_truth, dict):
            ground_truth = {}
            
        self.must_include = ground_truth.get('must_include', [])
        self.must_avoid = ground_truth.get('must_avoid', [])
        self.must_include_any = ground_truth.get('must_include_any', [])
        self.prerequisites = ground_truth.get('prerequisites', {})
        self.require_kernel_validation = ground_truth.get('require_kernel_validation', False)

    def _evaluate_via_kernel(self, trace_events):
        try:
            from kernel.events import create_event
            from kernel.reasoning_graph_builder import ReasoningGraphBuilder
            try:
                from kernel.unsupported_inference_detector import UnsupportedInferenceDetector
            except ImportError:
                from analytics.unsupported_inference_detector import UnsupportedInferenceDetector
        except ImportError as e:
            return {"status": "ERROR", "finding": "KERNEL_INTEGRATION_FAILED", "details": str(e)}

        builder = ReasoningGraphBuilder()
        event_map = {}

        for idx, event_dict in enumerate(trace_events):
            if not isinstance(event_dict, dict): continue
            
            e_type = event_dict.get('event_type', 'UNKNOWN')
            content = event_dict.get('content', '')
            original_id = event_dict.get('id', f"e_{idx}")
            metadata = event_dict.get('metadata', {})
            
            ev = create_event(e_type, {"content": content}, source="CLINICAL_TRACE")
            # Create a new immutable instance with the mapped ID and metadata
            ev = dataclasses.replace(ev, event_id=original_id, metadata=metadata)
            
            builder.process_event(ev)
            event_map[original_id] = ev

        for event_dict in trace_events:
            if not isinstance(event_dict, dict): continue
            original_id = event_dict.get('id')
            supported_by = event_dict.get('metadata', {}).get('supported_by', [])
            for support_id in supported_by:
                if support_id in event_map and original_id in event_map:
                    builder.connect_support(support_id, original_id)

        detector = UnsupportedInferenceDetector()
        patterns = detector.detect(builder.graph)

        if patterns:
            return {
                "status": "FAIL",
                "finding": "UNSUPPORTED_INFERENCE",
                "evaluation_method": "KERNEL_STRUCTURAL_DETECTION",
                "kernel_result": patterns[0]
            }

        return {
            "status": "PASS",
            "finding": "VALID_INFERENCE",
            "evaluation_method": "KERNEL_STRUCTURAL_DETECTION"
        }

    def evaluate_trace(self, trace_events):
        if not isinstance(trace_events, list):
            trace_events = []

        if self.require_kernel_validation:
            return self._evaluate_via_kernel(trace_events)

        ordered_actions = []
        found_actions_map = {}

        for idx, event in enumerate(trace_events):
            if not isinstance(event, dict) or event.get('event_type') != 'ACTION':
                continue
            metadata = event.get('metadata')
            if not isinstance(metadata, dict): continue
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

        for target_action, prereqs in self.prerequisites.items():
            if target_action not in found_actions_map:
                continue
            first_target_idx = ordered_actions.index(target_action)
            for prereq in prereqs:
                prereq_indices = [i for i, a in enumerate(ordered_actions) if a == prereq]
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
            if self.require_kernel_validation:
                print(f"   [!] Finding: {result.get('finding')} (via {result.get('evaluation_method')})")
            else:
                for failure in result.get('failures', []):
                    print(f"   [!] {failure['finding']}: {failure['details']}")
            print("")
