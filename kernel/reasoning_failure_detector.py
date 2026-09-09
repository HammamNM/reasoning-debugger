from kernel.debug_finding import DebugFinding
from kernel.reasoning_trace import ReasoningTrace

class UnsupportedAssumptionDetector:
    """
    Detects the FIRST explicit unsupported-assumption event.
    Strictly isolates the root failure to prevent downstream confusion.
    """
    FAILURE_TYPE = "unsupported_assumption"

    def detect(self, trace: ReasoningTrace) -> list[DebugFinding]:
        if not isinstance(trace, ReasoningTrace):
            raise TypeError("trace must be a ReasoningTrace")

        findings = []

        for event in trace.events:
            explicit_unsupported = (
                event.event_type == "INFERENCE"
                and "without support" in event.content.lower()
            )

            if event.event_type != self.FAILURE_TYPE and not explicit_unsupported:
                continue

            failure_type = "unsupported_inference" if explicit_unsupported else self.FAILURE_TYPE

            findings.append(
                DebugFinding(
                    event_id=event.id,
                    failure_type=failure_type,
                    explanation=event.content,
                    affected_event_ids=(),
                    metadata={"detector": self.__class__.__name__},
                )
            )
            # Strict First-Failure Contract: Halt on first root failure.
            break

        return findings
