from typing import Dict, Type
from app.config import InverterConfig
from app.models.enums import DriverType
from app.drivers.base import BaseInverterDriver
from app.drivers.fronius import FroniusDriver
from app.drivers.huawei import HuaweiDriver
from app.drivers.sma import SmaDriver
from app.drivers.solaredge import SolarEdgeDriver
from app.drivers.victron import VictronDriver

DRIVER_REGISTRY: Dict[DriverType, Type[BaseInverterDriver]] = {
    DriverType.FRONIUS: FroniusDriver,
    DriverType.HUAWEI: HuaweiDriver,
    DriverType.SMA: SmaDriver,
    DriverType.SOLAREDGE: SolarEdgeDriver,
    DriverType.VICTRON: VictronDriver,
}


def create_inverter_driver(config: InverterConfig) -> BaseInverterDriver:
    """Instancia el driver correspondiente según la configuración validada."""
    driver_cls = DRIVER_REGISTRY.get(config.driver)
    if not driver_cls:
        raise ValueError(f"Driver '{config.driver}' no soportado en el sistema.")
    return driver_cls(config)
