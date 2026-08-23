from kernel.reasoning_state import ReasoningState


class ClinicalSessionAdapter:

    def __init__(
        self,
        clinical_session,
        scenario=None
    ):
        self.clinical_session = clinical_session

        self.event_stream = (
            clinical_session.event_stream
        )

        self.reasoning_state = ReasoningState()

        self.scenario = scenario

    @property
    def session_id(
        self
    ):
        return self.clinical_session.session_id

    @property
    def student_id(
        self
    ):
        return self.clinical_session.student_id

    @property
    def scenario_id(
        self
    ):
        return self.clinical_session.scenario_id

    @scenario_id.setter
    def scenario_id(
        self,
        value
    ):
        self.clinical_session.scenario_id = value

    @property
    def active_case(
        self
    ):
        return self.clinical_session.active_case

    @property
    def outcome(
        self
    ):
        return self.clinical_session.outcome

    @property
    def decision_history(
        self
    ):
        return self.clinical_session.decision_history

    @property
    def state(
        self
    ):
        return self.clinical_session.state

    @property
    def clock(
        self
    ):
        return self.clinical_session.clock

    @property
    def finished(
        self
    ):
        return self.clinical_session.finished

    @property
    def metadata(
        self
    ):
        return getattr(
            self.clinical_session,
            "metadata",
            {}
        )
