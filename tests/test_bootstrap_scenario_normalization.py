from kernel.bootstrap import KernelBootstrap
from backend.session import ClinicalSession


def test_bootstrap_accepts_scenario_dict():

    scenario = {
        "scenario_id": "NSTEMI_001",
        "title": "NSTEMI Test",
        "initial_state": {
            "stage": "INITIAL_ASSESSMENT"
        },
        "metadata": {
            "initial_stage": "INITIAL_ASSESSMENT"
        }
    }

    clinical_session = ClinicalSession(
        scenario_id="NSTEMI_001",
        active_case={}
    )

    runtime = KernelBootstrap().create_runtime(
        clinical_session,
        scenario
    )

    assert runtime.scenario_engine is not None
    assert runtime.session.scenario_id == "NSTEMI_001"
