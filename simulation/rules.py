from dataclasses import dataclass

from kernel.events import create_event


@dataclass
class SimulationRule:

    trigger_action: str

    effect: str


class RuleEngine:


    def __init__(self):

        self.rules = []

        self.events = []


    def add_rule(
        self,
        rule
    ):

        self.rules.append(
            rule
        )


    def process_action(
        self,
        action,
        state
    ):

        generated_events = []


        for rule in self.rules:

            if rule.trigger_action != action:

                continue


            if rule.effect == "REVEAL_ECG":

                state.reveal_ecg()


                event = create_event(

                    "INFORMATION_REVEALED",

                    {
                        "action": action,

                        "information":
                            "ECG result revealed"
                    },

                    source="RULE_ENGINE"

                )


                self.events.append(
                    event
                )

                generated_events.append(
                    event
                )


            elif rule.effect == "REVEAL_TROPONIN":

                state.reveal_troponin()


                event = create_event(

                    "INFORMATION_REVEALED",

                    {
                        "action": action,

                        "information":
                            "Troponin result revealed"
                    },

                    source="RULE_ENGINE"

                )


                self.events.append(
                    event
                )

                generated_events.append(
                    event
                )


        state.add_action(
            action
        )


        action_event = create_event(

            "STUDENT_ACTION",

            {
                "action": action
            },

            source="STUDENT"

        )


        self.events.append(
            action_event
        )


        generated_events.append(
            action_event
        )


        return generated_events
