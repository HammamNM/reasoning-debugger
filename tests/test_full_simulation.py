from backend.session import ClinicalSession
from kernel.bootstrap import KernelBootstrap
from kernel.scenario import Scenario
from simulation.orchestrator import SimulationOrchestrator


scenario = Scenario(
    scenario_id="NSTEMI_001",
    title="NSTEMI Test Scenario",
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
            "result": "ST depression"
        }
    }
)


session = ClinicalSession(
    student_id="student_001",
    scenario_id="NSTEMI_001"
)

runtime = KernelBootstrap().create_runtime(
    session,
    scenario=scenario
)

orchestrator = SimulationOrchestrator(
    runtime
)

print("TIME:", session.clock.get_time())

orchestrator.process_student_action(
    "ORDER_ECG"
)

print("EVENTS:")

for event in session.event_stream.get_all():
    print(event.event_type, event.payload)
