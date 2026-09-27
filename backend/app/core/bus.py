import asyncio
from typing import Set
from app.models.metrics import InverterMetrics


class MetricBus:
    """In-memory PubSub Event Bus para desacoplar el polling Modbus de WebSockets y DB."""

    def __init__(self):
        self._subscribers: Set[asyncio.Queue] = set()

    def subscribe(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue(maxsize=100)
        self._subscribers.add(q)
        return q

    def unsubscribe(self, q: asyncio.Queue) -> None:
        self._subscribers.discard(q)

    async def publish(self, metrics: InverterMetrics) -> None:
        for q in list(self._subscribers):
            try:
                q.put_nowait(metrics)
            except asyncio.QueueFull:
                try:
                    _ = q.get_nowait()
                    q.put_nowait(metrics)
                except (asyncio.QueueEmpty, asyncio.QueueFull):
                    pass


metric_bus = MetricBus()
