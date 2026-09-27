from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.enums import InverterStatus


class GridVoltage(BaseModel):
    l1: float = Field(0.0, description="Tensión fase L1 en Voltios (V)")
    l2: float = Field(0.0, description="Tensión fase L2 en Voltios (V)")
    l3: float = Field(0.0, description="Tensión fase L3 en Voltios (V)")


class InverterMetrics(BaseModel):
    inverter_id: str
    manufacturer: str
    model: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    is_connected: bool = True

    # Potencia y Energía
    active_power_w: float = Field(0.0, description="Potencia activa (W)")
    reactive_power_var: Optional[float] = Field(None, description="Potencia reactiva (VAr)")
    daily_yield_wh: Optional[float] = Field(None, description="Producción del día (Wh)")
    total_energy_kwh: float = Field(0.0, description="Energía total acumulada (kWh)")

    # Red eléctrica AC
    grid_voltage_v: GridVoltage = Field(default_factory=GridVoltage)
    grid_frequency_hz: float = Field(0.0, description="Frecuencia de red (Hz)")

    # Estado operativo
    inverter_status: InverterStatus = InverterStatus.STANDBY
    internal_temperature_c: Optional[float] = Field(None, description="Temperatura interna (°C)")

    # Subsistema de Batería (Opcional para Híbridos / Victron / Huawei LUNA)
    battery_soc_pct: Optional[float] = Field(None, description="Estado de carga batería (0-100%)")
    battery_power_w: Optional[float] = Field(None, description="Potencia batería (W, +carga, -descarga)")

    error_message: Optional[str] = None
