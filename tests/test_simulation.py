from backend.session import ClinicalSession
from kernel.bootstrap import KernelBootstrap
from kernel.scenario import Scenario
from simulation.orchestrator import SimulationOrchestrator


def test_simulation_to_kernel_runtime():

    scenario = Scenario(
        scenario_id="SIM_001",
        title="Simulation Test",
        metadata={
            "initial_stage": "INITIAL",
            "actions": {
                "ORDER_ECG": {
                    "event_type": "INVESTIGATION_ORDERED",
                    "investigation_id": "ECG_001",
                    "next_stage": "INVESTIGATION"
                }
            }
        },
        investigations={
            "ECG_001": {
                "result": "Normal ECG"
            }
        }
    )

    session = ClinicalSession(
        student_id="student_001",
        scenario_id="SIM_001"
    )

    runtime = KernelBootstrap().create_runtime(
        session,
        scenario=scenario
    )

    orchestrator = SimulationOrchestrator(
        runtime
    )

    orchestrator.process_student_action(
        "ORDER_ECG"
    )

    events = (
        session.event_stream
        .get_all()
    )

    assert len(events) > 0

    assert any(
        event.event_type == "ACTION"
        for event in events
    )


if __name__ == "__main__":
    test_simulation_to_kernel_runtime()
