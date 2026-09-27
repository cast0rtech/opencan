import asyncio
import logging
from collections import defaultdict
from datetime import datetime
from typing import Dict, List
from app.config import settings
from app.core.bus import metric_bus
from app.core.database import AsyncSessionLocal
from app.models.db import MetricAggregateMinute
from app.models.metrics import InverterMetrics

logger = logging.getLogger(__name__)


class MetricsAggregator:
    """Consume del bus en memoria y persiste métricas agregadas por minuto en SQLite."""

    def __init__(self):
        self._running = False
        self._task: asyncio.Task | None = None
        self._buffer: Dict[str, List[InverterMetrics]] = defaultdict(list)

    def start(self):
        self._running = True
        self._task = asyncio.create_task(self._run(), name="metrics_aggregator")

    async def stop(self):
        self._running = False
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _run(self):
        queue = metric_bus.subscribe()
        flush_interval = settings.storage.buffer_flush_seconds
        last_flush = asyncio.get_event_loop().time()

        try:
            while self._running:
                try:
                    metrics: InverterMetrics = await asyncio.wait_for(queue.get(), timeout=2.0)
                    if metrics.is_connected:
                        self._buffer[metrics.inverter_id].append(metrics)
                except asyncio.TimeoutError:
                    pass

                now = asyncio.get_event_loop().time()
                if (now - last_flush) >= flush_interval:
                    await self._flush()
                    last_flush = now
        finally:
            metric_bus.unsubscribe(queue)
            await self._flush()

    async def _flush(self):
        if not self._buffer:
            return

        current_data = dict(self._buffer)
        self._buffer.clear()

        aggregates: List[MetricAggregateMinute] = []
        now = datetime.utcnow()

        for inv_id, samples in current_data.items():
            if not samples:
                continue

            powers = [s.active_power_w for s in samples]
            voltages = [s.grid_voltage_v.l1 for s in samples if s.grid_voltage_v.l1 > 0] or [230.0]
            freqs = [s.grid_frequency_hz for s in samples if s.grid_frequency_hz > 0] or [50.0]
            last_sample = samples[-1]

            agg = MetricAggregateMinute(
                inverter_id=inv_id,
                timestamp=now,
                avg_power=sum(powers) / len(powers),
                max_power=max(powers),
                min_power=min(powers),
                avg_voltage=sum(voltages) / len(voltages),
                avg_frequency=sum(freqs) / len(freqs),
                accumulated_energy=last_sample.total_energy_kwh
            )
            aggregates.append(agg)

        if aggregates:
            try:
                async with AsyncSessionLocal() as session:
                    session.add_all(aggregates)
                    await session.commit()
                logger.debug(f"Guardados {len(aggregates)} registros agregados en SQLite.")
            except Exception as e:
                logger.error(f"Error persistiendo agregados en SQLite: {e}", exc_info=True)
