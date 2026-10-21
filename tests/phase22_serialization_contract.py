import json
from kernel.api import ReasoningTrace
from kernel.api import ReasoningTraceEvent
from kernel.api import DebugFinding

def test_trace_determinism():
    event = ReasoningTraceEvent(id="evt_1", content="Testing determinism", event_type="INFERENCE")
    trace = ReasoningTrace(events=(event,))
    
    # 1. Must support to_dict()
    assert hasattr(trace, "to_dict"), "ReasoningTrace MUST implement to_dict()"
    
    dict_repr = trace.to_dict()
    
    # 2. Deterministic serialization (sorted keys)
    json1 = json.dumps(dict_repr, sort_keys=True)
    json2 = json.dumps(trace.to_dict(), sort_keys=True)
    
    assert json1 == json2, "Serialization is not deterministic!"

from kernel.graph import EdgeRelation, ReasoningGraph
from kernel.graph_serializer import GraphSerializer


def test_graph_serializer_matches_current_edge_contract():
    graph = ReasoningGraph()

    graph.add_edge(
        source="node_1",
        target="node_2",
        relation=EdgeRelation.SUPPORTS,
    )

    data = GraphSerializer().export(graph)

    assert data["edges"] == [
        {
            "source": "node_1",
            "target": "node_2",
            "relation": "SUPPORTS",
        }
    ]

    json.dumps(data, default=lambda value: value.value)
