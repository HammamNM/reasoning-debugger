from simulation.orchestrator import (
    SimulationOrchestrator
)

from kernel.bootstrap import (
    KernelBootstrap
)

from backend.session import (
    ClinicalSession
)



def test_investigation_flow():


    clinical_session = ClinicalSession(

        scenario_id="NSTEMI_001",

        active_case={

            "investigations": {

                "ORDER_ECG": {

                    "title": "ECG",

                    "result":
                        "ST depression in lateral leads"

                }

            }

        }

    )


    bootstrap = KernelBootstrap()


    runtime = bootstrap.create_runtime(
        clinical_session
    )


    orchestrator = SimulationOrchestrator(
        runtime
    )


    session = orchestrator.run_session(

        [

            "ORDER_ECG"

        ]

    )


    events = (
        session.event_stream.get_all()
    )


    assert len(events) >= 3

    action_events = [
        event for event in events
        if event.event_type == "ACTION"
    ]

    investigation_events = [
        event for event in events
        if event.event_type == "INVESTIGATION_RESULT"
    ]

    assert len(action_events) >= 1
    assert len(investigation_events) >= 1





    assert action_events[0].payload["action"] == "ORDER_ECG"

    investigation = investigation_events[0]

    assert investigation.payload["investigation_id"] == "ORDER_ECG"

    assert (
        investigation.payload["result"]["result"]
        == "ST depression in lateral leads"
    )
