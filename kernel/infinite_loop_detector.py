class InfiniteLoopDetector:
    """Detects when an agent is stuck repeating the same action or investigation."""
    def __init__(self, threshold=3):
        self.threshold = threshold

    def detect(self, trace):
        from kernel.debug_finding import DebugFinding
        findings = []
        filtered_events = [e for e in trace.events if e.event_type in ["ACTION", "INVESTIGATION"]]
        
        count = 1
        for i in range(1, len(filtered_events)):
            if filtered_events[i].content.strip().lower() == filtered_events[i-1].content.strip().lower():
                count += 1
                if count == self.threshold:
                    findings.append(
                        DebugFinding(
                            event_id=filtered_events[i].id,
                            failure_type="INFINITE_LOOP",
                            explanation=f"Agent is stuck in a loop, repeating: '{filtered_events[i].content.strip()}'",
                            affected_event_ids=tuple(),
                            metadata={"loop_count": count}
                        )
                    )
            else:
                count = 1
                
        return findings
