from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import Any, Dict
import uuid


@dataclass(frozen=True)
class ReasoningEvent:

    event_id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    event_type: str = ""

    payload: Dict[str, Any] = field(
        default_factory=dict
    )

    source: str = ""

    timestamp: str = field(
        default_factory=lambda: datetime.now(UTC).isoformat()
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


def create_event(
    event_type,
    payload=None,
    source="SIMULATION"
):

    if payload is None:

        payload = {}


    if not isinstance(
        payload,
        dict
    ):

        if event_type == "STUDENT_ACTION":

            payload = {
                "action": payload
            }

        else:

            payload = {
                "content": payload
            }


    return ReasoningEvent(

        event_type=event_type,

        payload=payload,

        source=source

    )


class EventStream:


    def __init__(self):

        self._events = []


    def publish(
        self,
        event: ReasoningEvent
    ):

        if not isinstance(
            event,
            ReasoningEvent
        ):

            raise TypeError(
                "EventStream accepts only ReasoningEvent"
            )


        self._events.append(
            event
        )


    def get_all(
        self
    ):

        return list(
            self._events
        )


    def get_by_type(
        self,
        event_type
    ):

        return [

            event

            for event in self._events

            if event.event_type == event_type

        ]


    def get_by_source(
        self,
        source
    ):

        return [

            event

            for event in self._events

            if event.source == source

        ]


    def get_by_id(
        self,
        event_id
    ):

        for event in self._events:

            if event.event_id == event_id:

                return event


        return None


    def count(
        self
    ):

        return len(
            self._events
        )
