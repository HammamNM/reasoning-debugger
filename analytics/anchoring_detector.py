class AnchoringDetector:

    def detect(self, reasoning_state):
        detected = []

        hypotheses = getattr(
            reasoning_state,
            "hypotheses",
            [],
        )

        for hypothesis in hypotheses:
            evidence = self.get_contradicting_evidence(hypothesis)

            if len(evidence) == 0:
                continue

            detected.append({
                "pattern_id": "CP-201",
                "name": "Anchoring Bias",
                "hypothesis": hypothesis.name,
                "reason": (
                    "Hypothesis remained active despite "
                    "contradictory evidence"
                ),
                "severity": self.calculate_severity(evidence),
                "evidence": evidence,
            })

        return detected

    def get_contradicting_evidence(self, hypothesis):
        return list(
            getattr(
                hypothesis,
                "contradicting_evidence",
                [],
            )
        )

    def calculate_severity(self, evidence):
        count = len(evidence)

        if count >= 3:
            return "HIGH"

        if count >= 2:
            return "MEDIUM"

        return "LOW"
