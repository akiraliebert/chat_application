from abc import ABC, abstractmethod

class EventBus(ABC):
    @abstractmethod
    async def publish(self, event: dict) -> None:
        ...

    @abstractmethod
    async def subscribe(self, channel: str) -> None:
        ...