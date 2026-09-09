from kernel.events import ReasoningEvent
from kernel.registry import EngineRegistry


class NoneEngine:
    def process_event(self, event, session):
        return None


class SingleEventEngine:
    def process_event(self, event, session):
        return ReasoningEvent(
            event_type="TEST_GENERATED",
            payload={"ok": True},
            source="TEST_ENGINE",
        )


class ListEventEngine:
    def process_event(self, event, session):
        return [
            ReasoningEvent(
                event_type="TEST_A",
                source="TEST_ENGINE",
            ),
            ReasoningEvent(
                event_type="TEST_B",
                source="TEST_ENGINE",
            ),
        ]


def test_registry_accepts_none_single_event_and_event_list():
    registry = EngineRegistry()

    registry.register(NoneEngine(), priority=10)
    registry.register(SingleEventEngine(), priority=20)
    registry.register(ListEventEngine(), priority=30)

    event = ReasoningEvent(
        event_type="TEST_INPUT",
        source="TEST",
    )

    generated = registry.dispatch(event, object())

    assert len(generated) == 3
    assert [e.event_type for e in generated] == [
        "TEST_GENERATED",
        "TEST_A",
        "TEST_B",
    ]
    assert all(isinstance(e, ReasoningEvent) for e in generated)


def test_registry_preserves_priority_order():
    registry = EngineRegistry()

    first = SingleEventEngine()
    second = ListEventEngine()

    registry.register(second, priority=30)
    registry.register(first, priority=20)

    engines = registry.get_engines()

    assert engines == [first, second]
