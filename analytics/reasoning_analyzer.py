from kernel.models import PrimitiveType


class ReasoningAnalyzer:


    def analyze_graph(
        self,
        reasoning_graph
    ):

        node_count = len(
            reasoning_graph.nodes
        )

        edge_count = len(
            reasoning_graph.edges
        )


        primitive_counts = {}


        for node in reasoning_graph.nodes:

            primitive = node.primitive.value

            primitive_counts.setdefault(
                primitive,
                0
            )

            primitive_counts[primitive] += 1



        metrics = {

            "nodes":
                node_count,

            "edges":
                edge_count,

            "observations":
                primitive_counts.get(
                    "OBSERVATION",
                    0
                ),

            "investigations":
                primitive_counts.get(
                    "INVESTIGATION",
                    0
                ),

            "hypotheses":
                primitive_counts.get(
                    "HYPOTHESIS",
                    0
                ),

            "decisions":
                primitive_counts.get(
                    "DECISION",
                    0
                ),

            "outcomes":
                primitive_counts.get(
                    "OUTCOME",
                    0
                ),

            "reasoning_features":
                self.extract_reasoning_features(
                    reasoning_graph
                )

        }


        return metrics



    def extract_reasoning_features(
        self,
        reasoning_graph
    ):

        features = {

            "first_hypothesis_step":
                None,

            "first_decision_step":
                None,

            "investigations_before_decision":
                0,

            "hypothesis_count_before_decision":
                0

        }


        for index, node in enumerate(
            reasoning_graph.nodes,
            start=1
        ):


            if (

                node.primitive == PrimitiveType.HYPOTHESIS

                and

                features["first_hypothesis_step"] is None

            ):

                features["first_hypothesis_step"] = index



            if (

                node.primitive == PrimitiveType.DECISION

                and

                features["first_decision_step"] is None

            ):

                features["first_decision_step"] = index



        decision_step = features[
            "first_decision_step"
        ]


        if decision_step is not None:


            for node in reasoning_graph.nodes[

                :decision_step - 1

            ]:


                if node.primitive == PrimitiveType.INVESTIGATION:

                    features[
                        "investigations_before_decision"
                    ] += 1


                if node.primitive == PrimitiveType.HYPOTHESIS:

                    features[
                        "hypothesis_count_before_decision"
                    ] += 1



        return features



    def extract_reasoning_path(
        self,
        reasoning_graph
    ):

        path = []


        for index, node in enumerate(
            reasoning_graph.nodes,
            start=1
        ):

            incoming = [

                edge.relation

                for edge in reasoning_graph.incoming_edges(
                    node.id
                )

            ]


            outgoing = [

                edge.relation

                for edge in reasoning_graph.outgoing_edges(
                    node.id
                )

            ]


            path.append({

                "step":
                    index,

                "id":
                    node.id,

                "primitive":
                    node.primitive.value,

                "content":
                    node.content,

                "incoming_relations":
                    incoming,

                "outgoing_relations":
                    outgoing

            })


        return path
