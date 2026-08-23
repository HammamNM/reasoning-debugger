from kernel.models import (
    ReasoningUnit,
    PrimitiveType
)

from kernel.graph import (
    ReasoningGraph,
    EdgeRelation
)

from kernel.provenance import (
    ProvenanceRecord
)


class ReasoningGraphBuilder:

    def __init__(
        self
    ):

        self.graph = ReasoningGraph()

        self.counter = 0

        self.last_hypothesis_node = None

        self.last_investigation_node = None

        self.last_evidence_node = None

        self.hypothesis_nodes = {}


    def create_node_id(
        self
    ):

        self.counter += 1

        return str(
            self.counter
        )


    def process_event(
        self,
        event
    ):

        primitive = (
            self.classify_event(
                event
            )
        )


        if primitive is None:

            return None


        node = ReasoningUnit(

            id=self.create_node_id(),

            primitive=primitive,

            content=str(
                event.payload
            ),

            provenance=ProvenanceRecord(

                source=event.source,

                event_type=event.event_type

            )

        )


        self.graph.add_node(
            node
        )


        if primitive in (
            PrimitiveType.EVIDENCE,
            PrimitiveType.INVESTIGATION
        ):

            if primitive == PrimitiveType.EVIDENCE:

                self.last_evidence_node = node.id

            supports = event.payload.get(
                "supports",
                []
            )

            contradicts = event.payload.get(
                "contradicts",
                []
            )

            for hypothesis_name in supports:

                hypothesis_node = self.find_hypothesis_node(
                    hypothesis_name
                )

                if hypothesis_node is not None:

                    self.connect_support(
                        node.id,
                        hypothesis_node.id
                    )

            for hypothesis_name in contradicts:

                hypothesis_node = self.find_hypothesis_node(
                    hypothesis_name
                )

                if hypothesis_node is not None:

                    self.connect_contradiction(
                        node.id,
                        hypothesis_node.id
                    )


        if primitive == PrimitiveType.HYPOTHESIS:

            self.last_hypothesis_node = node.id

            hypothesis_name = (
                event.payload.get(
                    "action"
                )
            )

            if hypothesis_name:

                self.hypothesis_nodes[
                    hypothesis_name
                ] = node.id


        if primitive == PrimitiveType.INVESTIGATION:

            self.last_investigation_node = node.id


        self.connect_previous(
            node.id
        )


        if primitive == PrimitiveType.INFERENCE:

            self.connect_inference_from_evidence(
                node.id
            )


        if primitive == PrimitiveType.HYPOTHESIS_UPDATE:

            action = event.payload.get(
                "action",
                ""
            )


            if action.startswith(
                "CONFIRM_"
            ):

                hypothesis_name = action[
                    len("CONFIRM_"):
                ]


                hypothesis_node = (
                    self.find_hypothesis_node(
                        hypothesis_name
                    )
                )


                if hypothesis_node is not None:

                    self.connect_confirmation(

                        node.id,

                        hypothesis_node.id

                    )


            elif action.startswith(
                "REJECT_"
            ):

                hypothesis_name = action[
                    len("REJECT_"):
                ]


                hypothesis_node = (
                    self.find_hypothesis_node(
                        hypothesis_name
                    )
                )


                if hypothesis_node is not None:

                    self.connect_rejection(

                        node.id,

                        hypothesis_node.id

                    )


        return node


    def classify_event(
        self,
        event
    ):

        payload = getattr(
            event,
            "payload",
            {}
        )


        action = payload.get(
            "action",
            ""
        )


        event_type = event.event_type


        # Generic reasoning primitives

        if event_type == "HISTORY_RESPONSE_REQUEST":
            return PrimitiveType.OBSERVATION

        if event_type == "OBSERVATION":

            return PrimitiveType.OBSERVATION


        if event_type == "EVIDENCE":

            return PrimitiveType.EVIDENCE


        if event_type == "INFERENCE":

            return PrimitiveType.INFERENCE


        # Existing kernel primitives

        if event_type == "OUTCOME_UPDATED":

            return PrimitiveType.OUTCOME


        if event_type == "INVESTIGATION_RESULT":

            return PrimitiveType.INVESTIGATION


        if event_type == "DECISION_ASSESSMENT":

            return PrimitiveType.DECISION


        if event_type == "ACTION":

            if action.startswith(
                "ASK_"
            ):

                return PrimitiveType.OBSERVATION


            if action.startswith(
                "ORDER_"
            ):

                return PrimitiveType.INVESTIGATION


            if action.startswith(
                "DIAGNOSIS_"
            ):

                return PrimitiveType.HYPOTHESIS


            if action.startswith(
                "CONFIRM_"
            ):

                return PrimitiveType.HYPOTHESIS_UPDATE


            if action.startswith(
                "REJECT_"
            ):

                return PrimitiveType.HYPOTHESIS_UPDATE


            if action.startswith(
                "TREAT_"
            ):

                return PrimitiveType.DECISION


        return None


    def connect_previous(
        self,
        current_id
    ):

        nodes = self.graph.nodes


        if len(nodes) < 2:

            return


        previous = nodes[-2]


        self.graph.add_edge(

            previous.id,

            current_id,

            EdgeRelation.SEQUENCE

        )


    def connect_inference_from_evidence(
        self,
        inference_node_id
    ):

        if self.last_evidence_node is None:

            return


        self.graph.add_edge(

            self.last_evidence_node,

            inference_node_id,

            EdgeRelation.DERIVED_FROM

        )


    def find_hypothesis_node(
        self,
        hypothesis_name
    ):

        node_id = (
            self.hypothesis_nodes.get(
                hypothesis_name
            )
        )


        if node_id is None:

            return None


        for node in self.graph.nodes:

            if node.id == node_id:

                return node


        return None


    def connect_support(
        self,
        evidence_node_id,
        hypothesis_node_id
    ):

        self.graph.add_edge(

            evidence_node_id,

            hypothesis_node_id,

            EdgeRelation.SUPPORTS

        )


    def connect_contradiction(
        self,
        evidence_node_id,
        hypothesis_node_id
    ):

        self.graph.add_edge(

            evidence_node_id,

            hypothesis_node_id,

            EdgeRelation.CONTRADICTS

        )


    def connect_confirmation(
        self,
        action_node_id,
        hypothesis_node_id
    ):

        self.graph.add_edge(

            action_node_id,

            hypothesis_node_id,

            EdgeRelation.CONFIRMS

        )


    def connect_rejection(
        self,
        action_node_id,
        hypothesis_node_id
    ):

        self.graph.add_edge(

            action_node_id,

            hypothesis_node_id,

            EdgeRelation.REJECTS

        )
