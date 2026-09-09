# Architecture & Pipeline

Reasoning IR is built on a strict separation of concerns. It enforces a clear boundary between the agent's representation (the Trace) and the debugger's analysis (the Findings). The Debugger never rewrites or alters the agent's reasoning to make the outcome look better.

## Core Pipeline

Structured Agent Trace
        ↓
ReasoningTrace
        ↓
TraceGraphAdapter
        ↓
Reasoning Graph
        ↓
First-Failure Detection
        ↓
Failure Propagation
        ↓
DebugFinding

### 1. ReasoningTrace
ReasoningTrace represents a structured event log, treated as a fixed input for analysis. It captures the chronological sequence of structured reasoning events provided by the agent or trace producer.

### 2. TraceGraphAdapter
Converts the sequential trace into a structured ReasoningGraph. It maps explicit semantic dependencies (if provided) and structural relationships.

### 3. First-Failure Detection
Scans the graph structurally. It is designed to isolate the first root failure, preventing a single early mistake from generating a flood of confusing downstream error alerts.

### 4. Failure Propagation
Propagation follows explicit semantic dependency relationships preserved in the reasoning graph. It differentiates between events that merely occurred after the failure (chronological sequence) and events that were actively based on the failure (semantic dependency).

### 5. DebugFinding
The final output is a structural, human-verifiable finding. It links directly back to the original trace event IDs, allowing a human reviewer to prove exactly why the failure was flagged without relying on opaque AI judgments.
