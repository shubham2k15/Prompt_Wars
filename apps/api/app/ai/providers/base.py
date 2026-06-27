from abc import ABC, abstractmethod


class CompanionProvider(ABC):
    @abstractmethod
    async def respond(self, *, prompt: str, context: dict) -> dict:
        raise NotImplementedError

