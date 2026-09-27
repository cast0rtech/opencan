from abc import ABC, abstractmethod
import logging
from typing import Optional
from pymodbus.client import AsyncModbusTcpClient
from app.config import InverterConfig
from app.models.metrics import InverterMetrics

logger = logging.getLogger(__name__)


class BaseInverterDriver(ABC):
    def __init__(self, config: InverterConfig):
        self.config = config
        self.client: Optional[AsyncModbusTcpClient] = None

    async def connect(self) -> bool:
        """Crea el socket Modbus TCP y valida conexión inicial."""
        if self.client is None or not self.client.connected:
            self.client = AsyncModbusTcpClient(
                host=self.config.host,
                port=self.config.port,
                timeout=self.config.timeout
            )
            connected = await self.client.connect()
            if not connected:
                logger.warning(f"[{self.config.id}] No se pudo conectar a {self.config.host}:{self.config.port}")
                return False
            logger.info(f"[{self.config.id}] Conexión Modbus establecida ({self.config.host}:{self.config.port}).")
        return True

    def disconnect(self) -> None:
        """Cierra el socket de red y limpia recursos."""
        if self.client:
            self.client.close()
            self.client = None

    async def health_check(self) -> bool:
        """Verifica si el enlace Modbus responde a un frame básico."""
        if not self.client or not self.client.connected:
            return False
        try:
            rr = await self.client.read_holding_registers(
                address=self.config.base_address,
                count=1,
                slave=self.config.unit_id
            )
            return not rr.isError()
        except Exception:
            return False

    @abstractmethod
    async def read_telemetry(self) -> InverterMetrics:
        """Lectura e interpretación de registros específicos del fabricante."""
        pass
