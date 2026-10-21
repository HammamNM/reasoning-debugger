from kernel.runtime import (
    KernelRuntime
)

from kernel.adapters.session_adapter import (
    ClinicalSessionAdapter
)

from kernel.evidence_engine import (
    EvidenceEngine
)
from simulation.investigation_engine import (
    InvestigationEngine
)


from kernel.adapters.decision_adapter import (
    DecisionEngineAdapter
)

from kernel.adapters.outcome_adapter import (
    OutcomeEngineAdapter
)

from kernel.adapters.scenario_adapter import (
    ScenarioEngineAdapter
)

from decision_engine.engine import (
    DecisionEngine
)

from outcome_engine.engine import (
    OutcomeEngine
)

from outcome_engine.mapper import (
    OutcomeMapper
)

from kernel.transition_engine import (
    TransitionEngine
)

from kernel.scenario_engine import (
    ScenarioEngine
)

from kernel.scenario import (
    Scenario
)


class KernelBootstrap:


    def create_runtime(
        self,
        clinical_session,
        scenario=None
    ):

        # -------------------------------------------------
        # Normalize scenario input
        # -------------------------------------------------

        if isinstance(
            scenario,
            dict
        ):

            scenario = self._scenario_from_dict(
                scenario
            )


        # -------------------------------------------------
        # If no explicit scenario was supplied,
        # try the ClinicalSession active_case.
        # -------------------------------------------------

        if scenario is None:

            active_case = getattr(
                clinical_session,
                "active_case",
                None
            )

            if isinstance(
                active_case,
                Scenario
            ):

                scenario = active_case

            elif isinstance(
                active_case,
                dict
            ) and active_case.get(
                "investigations"
            ):

                scenario = self._scenario_from_dict(
                    active_case,
                    scenario_id=getattr(
                        clinical_session,
                        "scenario_id",
                        "UNKNOWN"
                    )
                )


        # -------------------------------------------------
        # Session adapter
        # -------------------------------------------------

        session_adapter = ClinicalSessionAdapter(
            clinical_session,
            scenario=scenario
        )


        runtime = KernelRuntime(
            session_adapter
        )


        # -------------------------------------------------
        # Register engines
        # -------------------------------------------------


        runtime.register_engine(
            InvestigationEngine(),
            priority=20
        )

        runtime.register_engine(
            EvidenceEngine(),
            priority=30
        )

        runtime.register_engine(
            DecisionEngineAdapter(
                DecisionEngine()
            ),
            priority=40
        )

        runtime.register_engine(
            OutcomeEngineAdapter(
                OutcomeEngine(),
                OutcomeMapper()
            ),
            priority=50
        )

        runtime.register_engine(
            TransitionEngine(),
            priority=60
        )


        # -------------------------------------------------
        # Scenario Engine
        # -------------------------------------------------

        if scenario is not None:

            scenario_engine = ScenarioEngine(
                scenario
            )

            runtime.set_scenario_engine(
                scenario_engine
            )

            runtime.register_engine(
                ScenarioEngineAdapter(
                    scenario_engine
                ),
                priority=10
            )


        # -------------------------------------------------
        # Initialize runtime
        # -------------------------------------------------

        runtime.initialize()


        return runtime


    def _scenario_from_dict(
        self,
        data,
        scenario_id=None
    ):

        if isinstance(
            data,
            Scenario
        ):
            return data


        scenario_id = (
            data.get(
                "scenario_id",
                scenario_id
            )
            or "UNKNOWN"
        )


        title = data.get(
            "title",
            scenario_id
        )


        metadata = dict(
            data.get(
                "metadata",
                {}
            )
        )


        # -------------------------------------------------
        # Preserve legacy transition definitions
        # -------------------------------------------------

        if "transitions" in data:

            metadata[
                "transitions"
            ] = data[
                "transitions"
            ]


        return Scenario(

            scenario_id=scenario_id,

            title=title,

            specialty=data.get(
                "specialty",
                ""
            ),

            difficulty=data.get(
                "difficulty",
                "medium"
            ),

            patient=data.get(
                "patient",
                {}
            ),

            initial_state=data.get(
                "initial_state",
                {
                    "current_state":
                        data.get(
                            "current_state"
                        )
                }
            ),

            available_actions=data.get(
                "available_actions",
                []
            ),

            investigations=data.get(
                "investigations",
                {}
            ),

            outcomes=data.get(
                "outcomes",
                {}
            ),

            metadata=metadata
        )
