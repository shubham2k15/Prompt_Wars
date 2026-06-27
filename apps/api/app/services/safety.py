from __future__ import annotations

from dataclasses import dataclass


HIGH_RISK_TERMS = {
    "self-harm",
    "suicide",
    "kill myself",
    "end my life",
    "hopeless",
    "can't go on",
}


@dataclass
class SafetyResult:
    risk_level: str
    escalated: bool
    guidance: str | None = None


def assess_text(text: str) -> SafetyResult:
    lowered = text.lower()
    for term in HIGH_RISK_TERMS:
        if term in lowered:
            return SafetyResult(
                risk_level="high",
                escalated=True,
                guidance=(
                    "I am really sorry that you are carrying this much right now. "
                    "Please reach out to a trusted person nearby or a qualified mental health professional today. "
                    "If you feel in immediate danger, contact local emergency services or a crisis helpline right now."
                ),
            )

    medium_terms = ["burned out", "panic", "can't sleep", "worthless", "failure"]
    if any(term in lowered for term in medium_terms):
        return SafetyResult(risk_level="medium", escalated=False)

    return SafetyResult(risk_level="low", escalated=False)

