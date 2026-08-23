from kernel.bootstrap import KernelBootstrap

from backend.session import ClinicalSession

from simulation.engine import SimulationEngine



def test_nstemi_full_flow():


    scenario = {

        "scenario_id": "NSTEMI_001",

        "current_state": "INITIAL_ASSESSMENT",

        "investigations": {

            "ORDER_ECG": {

                "title": "ECG",

                "result": "ST depression in lateral leads"

            },

            "ORDER_TROPONIN": {

                "title": "Troponin",

                "result": "Positive"

            }

        },

        "transitions": [

            {

                "trigger": "ORDER_ECG",

                "next_state": "ECG_AVAILABLE"

            },

            {

                "trigger": "ORDER_TROPONIN",

                "next_state": "TROPONIN_AVAILABLE"

            }

        ]

    }



    clinical_session = ClinicalSession(

        scenario_id="NSTEMI_001",

        active_case=scenario

    )



    runtime = KernelBootstrap().create_runtime(

        clinical_session,

        scenario

    )


    simulation = SimulationEngine(
        runtime
    )


    simulation.execute_action(
        "ORDER_ECG"
    )


    simulation.execute_action(
        "ORDER_TROPONIN"
    )



    graph = (

        runtime.graph_builder.graph

    )



    assert len(
        graph.nodes
    ) > 0



    events = (

        runtime.session.event_stream.get_all()

    )


    event_types = [

        event.event_type

        for event in events

    ]



    assert "ACTION" in event_types


    assert "INVESTIGATION_RESULT" in event_types



    assert (

        runtime.session.reasoning_state

        .ordered_investigations

    )
