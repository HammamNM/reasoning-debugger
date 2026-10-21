from kernel.graph_storage import (
    GraphStorage
)

from analytics.analytics_engine import (
    AnalyticsEngine
)
from backend.session_manager import SessionManager
from simulation.orchestrator import SimulationOrchestrator

from kernel.bootstrap import KernelBootstrap

from analytics.analytics_engine import AnalyticsEngine


def main():

    session_manager = SessionManager()


    session = session_manager.create_session(
        student_id="student_001",
        scenario_id="NSTEMI",
        case_path="scenarios/nstemi_basic.json"
    )


    bootstrap = KernelBootstrap()

    runtime = bootstrap.create_runtime(
        session
    )


    orchestrator = SimulationOrchestrator(
        runtime
    )


    actions = [

        "ASK_CHEST_PAIN",

        "ORDER_ECG",

        "ORDER_TROPONIN",

        "MAKE_DIAGNOSIS"

    ]


    orchestrator.run_session(
        actions
    )


    graph_storage = GraphStorage()

    graph_storage.save(

        orchestrator.runtime
        .graph_builder
        .graph,

        "reasoning_graph.json"

    )
    
    
    analytics = AnalyticsEngine()

    report = analytics.generate_report(
        session=orchestrator.runtime.session,
        reasoning_graph=(
            orchestrator.runtime
            .graph_builder
            .graph
        )
    )

    print("\nREPORT")
    print(report)

    print(
        "\n=============================="
    )

    print(
        "CLINICAL REASONING REPORT"
    )

    print(
        "=============================="
    )


    print(
        "\nSESSION:"
    )

    print(
        report["session_id"]
    )


    print(
        "\nSCENARIO:"
    )

    print(
        report["scenario_id"]
    )


    print(
        "\nPERFORMANCE:"
    )

    print(
        report["performance"]["average_score"]
    )


    print(
        "\nDIMENSIONS:"
    )

    print(
        report["performance"]["dimension_scores"]
    )


    print(
        "\nPROGRESS:"
    )

    print(
        report["performance"]["progress_trend"]
    )


    print(
        "\nPATTERNS:"
    )

    print(
        report["patterns"]
    )


    print(
        "\nREASONING:"
    )

    print(
        report["reasoning"]
    )


    print(
        "\nOUTCOME:"
    )

    print(
        report["outcome"]
    )


if __name__ == "__main__":

    main()
