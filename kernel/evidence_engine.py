from kernel.evidence import (
    Evidence
)

from kernel.hypothesis_manager import (
    HypothesisManager
)


class EvidenceEngine:


    def __init__(self):

        self.hypothesis_manager = (
            HypothesisManager()
        )


    def process_event(
        self,
        event,
        session
    ):

        if event.event_type not in (
            "EVIDENCE",
            "INVESTIGATION_RESULT"
        ):
            return None


        payload = getattr(
            event,
            "payload",
            {}
        )


        if event.event_type == "EVIDENCE":



            content = payload.get(



                "content",



                ""



            )



        else:



            result = payload.get(



                "result",



                ""



            )



            if isinstance(result, dict):



                content = result.get(



                    "result",



                    str(result)



                )



            else:



                content = result




        supports = payload.get(
            "supports",
            []
        )


        contradicts = payload.get(
            "contradicts",
            []
        )


        strength = payload.get(
            "strength",
            1.0
        )


        evidence = Evidence(

            source=event.source,

            content=str(content),

            supports=list(
                supports
            ),

            contradicts=list(
                contradicts
            ),

            strength=float(
                strength
            )

        )


        if not hasattr(
            session,
            "evidence"
        ):

            session.evidence = []


        session.evidence.append(
            evidence
        )


        for hypothesis_name in supports:

            hypothesis = next(
                (
                    h
                    for h in getattr(
                        session.reasoning_state,
                        "hypotheses",
                        []
                    )
                    if h.name == hypothesis_name
                ),
                None
            )


            if hypothesis is not None:

                self.hypothesis_manager.add_supporting_evidence(

                    hypothesis,

                    evidence

                )


        for hypothesis_name in contradicts:

            hypothesis = next(
                (
                    h
                    for h in getattr(
                        session.reasoning_state,
                        "hypotheses",
                        []
                    )
                    if h.name == hypothesis_name
                ),
                None
            )


            if hypothesis is not None:

                self.hypothesis_manager.add_contradicting_evidence(

                    hypothesis,

                    evidence

                )


        return None
