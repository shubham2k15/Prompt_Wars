from __future__ import annotations

from typing import Any

import httpx

from ...config import get_settings
from .base import CompanionProvider


class GeminiProvider(CompanionProvider):
    def __init__(self) -> None:
        self.settings = get_settings()
        self.base_url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.settings.gemini_model}:generateContent"
        )

    async def respond(self, *, prompt: str, context: dict) -> dict[str, Any]:
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": (
                                "You are MindGarden, an empathetic AI wellness companion for exam students. "
                                "Do not diagnose. Be concise, warm, actionable, and personalized. "
                                "Always respond in this format: one validating opening sentence, then 3 to 4 bullet points, then one short supportive closing sentence. "
                                "The bullet points should cover what you notice, the best next step, and one gentle reframe. "
                                "Keep the tone emotionally supportive and practical.\n\n"
                                f"Context:\n{context}\n\nUser:\n{prompt}"
                            )
                        }
                    ]
                }
            ]
        }
        params = {"key": self.settings.gemini_api_key}
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(self.base_url, headers=headers, params=params, json=payload)
            response.raise_for_status()
            data = response.json()

        text = ""
        candidates = data.get("candidates", [])
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            text = "".join(part.get("text", "") for part in parts)

        if not text:
            text = "I am here with you. Tell me a little more about what feels heaviest today."

        return {
            "content": text.strip(),
            "sentiment": "supportive",
            "emotions": ["reflective"],
            "memory_candidates": [],
        }
