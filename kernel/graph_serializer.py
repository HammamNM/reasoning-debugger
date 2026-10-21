class GraphSerializer:


    def export(
        self,
        graph
    ):

        return {

            "nodes": [

                {

                    "id": node.id,

                    "primitive": str(
                        node.primitive
                    ),

                    "content": node.content

                }

                for node in graph.nodes

            ],

            "edges": [

                {

                    "source": edge.source,

                    "target": edge.target,

                    "relation": edge.relation.value

                }

                for edge in graph.edges

            ]

        }
