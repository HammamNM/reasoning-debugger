from kernel.adapters.swe_agent_adapter import SWEAgentAdapter
import importlib

trace_path = 'benchmarks/samples/public_real_trace/swe_agent_broken_hallucination.traj'
trace = SWEAgentAdapter.parse_trajectory(trace_path)

print(f"--- TRACE EVENTS ({len(trace.events)}) ---")
for e in trace.events:
    print(f"[{e.event_type}] {e.id}: {e.content}")

print("\n--- GRAPH EDGES ---")
try:
    # Attempt to load the internal graph builder based on our architecture
    from kernel.adapters.swe_agent_adapter import SWEAgentAdapter
    
    # We need to see how the trace is mapped to the graph. 
    # Since I don't want to guess the exact graph module name, 
    # let's instantiate the debugger and inspect its internals if possible.
    from kernel.debugger import ReasoningDebugger
    debugger = ReasoningDebugger()
    
    # Check if debugger exposes the graph builder internally
    if hasattr(debugger, 'graph_builder'):
        graph = debugger.graph_builder.build(trace)
        for edge in graph.edges:
            print(f"{edge.source_id} -> {edge.target_id} ({edge.relation})")
    elif hasattr(debugger, '_adapter'):
        graph = debugger._adapter.adapt(trace)
        for edge in graph.edges:
            print(f"{edge.source_id} -> {edge.target_id} ({edge.relation})")
    else:
        print("Could not automatically locate the internal graph inside the debugger.")
except Exception as ex:
    print(f"Graph extraction failed: {ex}")
