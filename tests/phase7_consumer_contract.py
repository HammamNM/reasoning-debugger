from kernel.api import (
    DebugFinding,
    ReasoningDebugger,
    ReasoningEvent,
    EventStream,
    Edge,
    EdgeRelation,
    ReasoningGraph,
    PrimitiveType,
    ReasoningUnit,
    ParserPipeline,
    ReasoningTrace,
    ReasoningTraceEvent,
    KernelRuntime,
    KernelSession,
)


def test_external_consumer_can_construct_core_objects():
    graph = ReasoningGraph()

    unit = ReasoningUnit(
        id="unit-1",
        primitive=PrimitiveType.OBSERVATION,
        content="Patient observed.",
    )

    graph.add_node(unit)

    assert graph.nodes[0].id == "unit-1"
    assert graph.nodes[0].primitive == PrimitiveType.OBSERVATION


def test_external_consumer_can_build_parser_pipeline():
    pipeline = ParserPipeline()

    result = pipeline.process(
        "Patient observed. Evidence collected."
    )

    assert result.units
    assert result.graph is not None


def test_external_consumer_can_build_trace():
    trace = ReasoningTrace(
        events=(
            ReasoningTraceEvent(
                "event-1",
                "Observation.",
                "OBSERVATION",
            ),
        )
    )

    assert len(trace.events) == 1
    assert trace.events[0].id == "event-1"


def test_external_consumer_can_use_debugger():
    trace = ReasoningTrace(
        events=(
            ReasoningTraceEvent(
                "event-1",
                "Observation.",
                "OBSERVATION",
            ),
        )
    )

    result = ReasoningDebugger().debug(trace)

    assert isinstance(result, list)
    assert all(isinstance(item, DebugFinding) for item in result)


def test_external_consumer_can_create_runtime():
    session = KernelSession()
    runtime = KernelRuntime(session)

    assert runtime.session is session
    assert runtime.event_queue == []
