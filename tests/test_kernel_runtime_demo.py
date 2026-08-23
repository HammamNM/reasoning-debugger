from backend.session import ClinicalSession
from kernel.bootstrap import KernelBootstrap
from kernel.events import ReasoningEvent


def test_runtime_flow():

    clinical_session = ClinicalSession(
        student_id="student_001",
        scenario_id="TEST_001"
    )

    runtime = (
        KernelBootstrap()
        .create_runtime(
            clinical_session
        )
    )

    event = ReasoningEvent(
        event_type="ACTION",
        payload={
            "action": "ORDER_ECG"
        },
        source="STUDENT"
    )

    runtime.publish(
        event
    )

    runtime.run_cycle()

    print("\nEVENT STREAM:")

    for item in (
        runtime.session
        .event_stream
        .get_all()
    ):
        print(item)


if __name__ == "__main__":
    test_runtime_flow()
