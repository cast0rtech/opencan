import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional
from app.config import InverterConfig
from app.core.bus import metric_bus
from app.drivers.base import BaseInverterDriver
from app.drivers.factory import create_inverter_driver
from app.models.metrics import InverterMetrics, InverterStatus

logger = logging.getLogger(__name__)


class InverterWorkerTask:
    """Supervisa el polling independiente de un inversor con backoff individual."""

    def __init__(self, config: InverterConfig):
        self.config = config
        self.driver: BaseInverterDriver = create_inverter_driver(config)
        self.last_metrics: Optional[InverterMetrics] = None
        self._running = False
        self._task: Optional[asyncio.Task] = None

    def start(self) -> None:
        self._running = True
        self._task = asyncio.create_task(self._run_loop(), name=f"poll_{self.config.id}")

    async def stop(self) -> None:
        self._running = False
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        self.driver.disconnect()

    async def _run_loop(self) -> None:
        backoff = 1.0
        max_backoff = 60.0

        logger.info(f"[{self.config.id}] Worker iniciado ({self.config.driver.value}) -> {self.config.host}:{self.config.port}")

        while self._running:
            try:
                # 1. Asegurar socket conectado
                connected = await self.driver.connect()
                if not connected:
                    raise ConnectionError(f"Fallo de conexión Modbus hacia {self.config.host}:{self.config.port}")

                # 2. Leer telemetría
                metrics = await self.driver.read_telemetry()
                self.last_metrics = metrics
                await metric_bus.publish(metrics)

                # Reset de backoff al completar ciclo válido
                backoff = 1.0
                await asyncio.sleep(self.config.poll_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.driver.disconnect()
                error_msg = f"{type(e).__name__}: {str(e)}"
                logger.warning(f"[{self.config.id}] Error en polling. Reintento en {backoff:.1f}s. Detalle: {error_msg}")

                # Emitir estado OFFLINE inmediato al dashboard WebSocket
                offline_metrics = InverterMetrics(
                    inverter_id=self.config.id,
                    manufacturer=self.config.driver.value,
                    model=self.config.name,
                    timestamp=datetime.utcnow(),
                    is_connected=False,
                    inverter_status=InverterStatus.OFFLINE,
                    error_message=error_msg
                )
                self.last_metrics = offline_metrics
                await metric_bus.publish(offline_metrics)

                await asyncio.sleep(backoff)
                backoff = min(backoff * 2.0, max_backoff)

        logger.info(f"[{self.config.id}] Worker finalizado.")


class InverterOrchestrator:
    """Gestiona el ciclo de vida del pool completo de inversores."""

    def __init__(self, configs: List[InverterConfig]):
        self.configs = configs
        self.workers: Dict[str, InverterWorkerTask] = {}

    def start(self) -> None:
        for conf in self.configs:
            if conf.enabled:
                worker = InverterWorkerTask(conf)
                worker.start()
                self.workers[conf.id] = worker
            else:
                logger.info(f"[{conf.id}] Inversor deshabilitado en configuración.")

    async def stop(self) -> None:
        logger.info("Deteniendo todos los workers del orquestador...")
        tasks = [w.stop() for w in self.workers.values()]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        self.workers.clear()

    def get_status_summary(self) -> Dict:
        return {
            inv_id: {
                "name": w.config.name,
                "driver": w.config.driver.value,
                "host": w.config.host,
                "port": w.config.port,
                "connected": w.last_metrics.is_connected if w.last_metrics else False,
                "metrics": w.last_metrics.model_dump() if w.last_metrics else None
            }
            for inv_id, w in self.workers.items()
        }
