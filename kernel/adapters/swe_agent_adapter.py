import json
from typing import List
from kernel.reasoning_trace import ReasoningTrace, ReasoningTraceEvent

class SWEAgentAdapter:
    """
    Blindly translates SWE-agent .traj JSON files into ReasoningTrace format.
    Strictly avoids inferring causal links (derived_from).
    Preserves original sequence via step_index metadata.
    """
    @staticmethod
    def parse_trajectory(filepath: str) -> ReasoningTrace:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        events: List[ReasoningTraceEvent] = []

        for idx, step in enumerate(data.get("trajectory", [])):
            if step.get("thought"):
                events.append(ReasoningTraceEvent(
                    id=f"t{idx}-thought",
                    content=step["thought"],
                    event_type="INFERENCE",
                    metadata={"step_index": idx, "state": step.get("state")}
                ))

            if step.get("action"):
                events.append(ReasoningTraceEvent(
                    id=f"t{idx}-action",
                    content=step["action"],
                    event_type="INVESTIGATION",
                    metadata={"step_index": idx}
                ))

            if step.get("observation"):
                events.append(ReasoningTraceEvent(
                    id=f"t{idx}-obs",
                    content=step["observation"],
                    event_type="EVIDENCE",
                    metadata={"step_index": idx}
                ))

        return ReasoningTrace(events=tuple(events))
