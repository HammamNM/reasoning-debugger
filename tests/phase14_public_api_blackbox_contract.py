import sys
import kernel.api

from kernel.api import (
    DebugFinding,
    ReasoningDebugger,
    ReasoningEvent,
    EventStream,
    create_event,
    Edge,
    EdgeRelation,
    ReasoningGraph,
    PrimitiveType,
    ReasoningUnit,
    ParserPipeline,
    QueryEngine,
    ReasoningTrace,
    ReasoningTraceEvent,
    KernelRuntime,
    KernelSession,
)

def test_public_api_core_models_are_constructible():
    unit = ReasoningUnit(id="u1", primitive=PrimitiveType.OBSERVATION, content="Observation")
    graph = ReasoningGraph()
    graph.add_node(unit)
    assert graph.nodes == [unit]
    assert unit.primitive == PrimitiveType.OBSERVATION

def test_public_api_graph_relationships_are_usable():
    graph = ReasoningGraph()
    first = ReasoningUnit(id="u1", primitive=PrimitiveType.OBSERVATION, content="First")
    second = ReasoningUnit(id="u2", primitive=PrimitiveType.INFERENCE, content="Second")
    graph.add_node(first)
    graph.add_node(second)
    graph.add_edge("u1", "u2", EdgeRelation.SEQUENCE)
    edges = graph.edges_by_relation(EdgeRelation.SEQUENCE)
    assert len(edges) == 1
    assert edges[0].source == "u1"
    assert edges[0].target == "u2"

def test_public_api_event_capability_is_usable():
    event = create_event(event_type="TEST_EVENT", payload={"value": 1}, source="PUBLIC_CONSUMER")
    stream = EventStream()
    stream.publish(event)
    assert stream.get_all() == [event]

def test_public_api_trace_capability_is_usable():
    event = ReasoningTraceEvent(id="e1", content="Observation", event_type="OBSERVATION")
    trace = ReasoningTrace(events=(event,))
    assert trace.event_ids() == ("e1",)
    assert trace.get_event("e1") is event

def test_public_api_parser_capability_is_usable():
    pipeline = ParserPipeline()
    # Using domain-agnostic markers recognized by PrimitiveClassifier
    result = pipeline.process("Observation: CPU spike. Therefore, I suspect a memory leak.")
    assert hasattr(result, "units")
    assert hasattr(result, "graph")
    assert result.units
    assert result.graph.nodes

def test_public_api_query_capability_is_usable():
    graph = ReasoningGraph()
    unit = ReasoningUnit(id="u1", primitive=PrimitiveType.HYPOTHESIS, content="Hypothesis")
    graph.add_node(unit)
    query = QueryEngine(graph)
    assert query.nodes_by_primitive(PrimitiveType.HYPOTHESIS) == [unit]

def test_public_api_debugger_accepts_public_trace():
    trace = ReasoningTrace(events=(ReasoningTraceEvent(id="e1", content="Observation.", event_type="OBSERVATION"),))
    findings = ReasoningDebugger().debug(trace)
    assert isinstance(findings, list)

def test_public_api_runtime_can_execute_public_event():
    session = KernelSession()
    runtime = KernelRuntime(session)
    event = ReasoningEvent(event_type="PUBLIC_TEST", payload={"value": 42}, source="PUBLIC_CONSUMER")
    runtime.publish(event)
    runtime.run_cycle()
    assert session.event_stream.get_all() == [event]

def test_public_api_runtime_preserves_session_identity():
    session = KernelSession()
    runtime = KernelRuntime(session)
    assert runtime.session is session

def test_public_api_has_no_application_layer_requirement():
    forbidden = {"analytics", "backend", "decision_engine", "outcome_engine", "simulation"}
    loaded_forbidden = [mod for mod in sys.modules if any(mod == f or mod.startswith(f + ".") for f in forbidden)]
    assert not loaded_forbidden, f"Application layers leaked into kernel API: {loaded_forbidden}"
