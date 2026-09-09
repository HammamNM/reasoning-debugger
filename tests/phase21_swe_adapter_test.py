from kernel.adapters.swe_agent_adapter import SWEAgentAdapter

def test_swe_agent_blind_translation():
    filepath = "benchmarks/samples/public_real_trace/swe_agent_marshmallow.traj"
    trace = SWEAgentAdapter.parse_trajectory(filepath)

    assert len(trace.events) > 0, "Failed to extract events from trajectory"

    # Verify strict typing without causal assumptions
    types = {e.event_type for e in trace.events}
    assert "INFERENCE" in types
    assert "INVESTIGATION" in types
    assert "EVIDENCE" in types

    # Verify NO derived_from metadata was hallucinated by the adapter
    for event in trace.events:
        assert "derived_from" not in (event.metadata or {}), "Adapter hallucinated causal links!"

    print(f"SUCCESS: Extracted {len(trace.events)} events blindly.")

if __name__ == "__main__":
    test_swe_agent_blind_translation()
