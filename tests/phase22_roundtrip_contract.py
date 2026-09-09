from kernel.api import ReasoningTrace, ReasoningTraceEvent

def test_serialization_roundtrip():
    # Setup test event with metadata
    event = ReasoningTraceEvent(id="e1", content="test", event_type="OBSERVATION", metadata={"key": "val"})
    original = ReasoningTrace(events=(event,))
    
    # Serialize to dictionary
    data_dict = original.to_dict()
    
    # Deserialize back to object
    reconstructed = ReasoningTrace.from_dict(data_dict)
    
    # Assert complete round-trip fidelity
    assert original == reconstructed, "Round-trip failed: Object state mutated during serialization cycle."
    assert original.events[0].metadata == reconstructed.events[0].metadata, "Metadata lost in round-trip!"
