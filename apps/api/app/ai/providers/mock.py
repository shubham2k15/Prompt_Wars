from __future__ import annotations

from collections import Counter

from .base import CompanionProvider


class MockCompanionProvider(CompanionProvider):
    async def respond(self, *, prompt: str, context: dict) -> dict:
        preferences = context.get("profile", {})
        exam = preferences.get("exam_type") or "your exam"
        style = preferences.get("motivation_style") or "gentle"
        recent_triggers = context.get("recent_triggers") or []
        memory = context.get("memories") or []
        words = [word.strip(".,!?").lower() for word in prompt.split() if len(word) > 4]
        top_words = [item for item, _ in Counter(words).most_common(2)]

        opening = {
            "gentle": "You have been carrying a lot, and it makes sense that this feels heavy.",
            "direct": "You are under pressure, but we can turn this into a clear next step.",
            "energetic": "This looks tough, but there is still momentum available today.",
        }.get(style, "I am with you in this moment.")

        trigger_line = (
            f"I also notice {', '.join(recent_triggers[:2])} showing up as possible pressure points. "
            if recent_triggers
            else ""
        )
        memory_line = (
            f"Last time, what helped was {memory[0]}. "
            if memory
            else "We can learn what helps you and build on it together. "
        )
        action = (
            f"For the next 20 minutes, focus on one small block for {exam}, preferably around "
            f"{top_words[0] if top_words else 'the topic that feels most avoidable'}."
        )
        reframe = "Feeling overwhelmed does not mean you are failing. It usually means your load needs to become smaller and clearer."

        return {
            "content": "\n".join(
                [
                    opening,
                    f"- What I notice: {trigger_line or 'There is real pressure here, and it makes sense that your system is reacting.'}".strip(),
                    f"- What to try next: {action}",
                    f"- What to remember: {memory_line.strip()}",
                    f"- Gentle reframe: {reframe}",
                    "I am with you. After that small step, come back and we will adjust together.",
                ]
            ),
            "sentiment": "supportive",
            "emotions": ["stressed" if "stress" in prompt.lower() else "reflective"],
            "memory_candidates": top_words,
        }
