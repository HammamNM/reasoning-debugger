from kernel.bootstrap import KernelBootstrap

from kernel.events import (
    create_event
)

from backend.session import ClinicalSession


def test_full_kernel_flow():

    session = ClinicalSession(
        scenario_id="TEST_001"
    )


    runtime = KernelBootstrap().create_runtime(
        session
    )


    runtime.publish(

        create_event(

            "ACTION",

            {
                "action": "ASK_CHEST_PAIN"
            },

            source="TEST"

        )

    )


    runtime.run_cycle()


    runtime.publish(

        create_event(

            "ACTION",

            {
                "action": "DIAGNOSIS_NSTEMI"
            },

            source="TEST"

        )

    )


    runtime.run_cycle()


    graph = runtime.graph_builder.graph


    assert len(
        graph.nodes
    ) == 2


    assert len(
        graph.edges
    ) == 1


    transitions = (

        runtime.session

        .reasoning_state

        .transitions

        .transitions

    )


    assert len(
        transitions
    ) > 0
