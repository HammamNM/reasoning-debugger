from kernel.events import ReasoningEvent


class ActionProcessor:


    def process(
        self,
        action,
        payload=None
    ):

        if payload is None:

            payload = {}


        event_payload = {

            "action": action

        }


        event_payload.update(
            payload
        )


        return ReasoningEvent(

            event_type="ACTION",

            payload=event_payload,

            source="STUDENT"

        )
