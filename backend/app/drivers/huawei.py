from app.drivers.base import BaseInverterDriver
from app.drivers.codec import ModbusCodec
from app.models.metrics import InverterMetrics, InverterStatus, GridVoltage


class HuaweiDriver(BaseInverterDriver):
    """Huawei SUN2000 V200/V300 vía SDongleA o SmartLogger."""

    HUAWEI_STATE_MAP = {
        0x0000: InverterStatus.STANDBY,
        0x0001: InverterStatus.STANDBY,
        0x0002: InverterStatus.RUNNING,
        0x0003: InverterStatus.RUNNING,
        0x0200: InverterStatus.STANDBY,
        0x0201: InverterStatus.FAULT,
        0x0401: InverterStatus.OFFLINE
    }

    async def read_telemetry(self) -> InverterMetrics:
        # 32066: V_AB, 32069: Hz, 32080: W, 32089: Status, 32106: Energy
        rr = await self.client.read_holding_registers(
            address=self.config.base_address,  # default 32066
            count=45,
            slave=self.config.unit_id
        )
        if rr.isError():
            raise IOError(f"Error Huawei SUN2000: {rr}")

        regs = rr.registers

        v_l1 = regs[0] * 0.1
        freq = regs[3] * 0.01
        power_w = ModbusCodec.decode_int32(regs[14:16])
        status_code = regs[23]
        status = self.HUAWEI_STATE_MAP.get(status_code, InverterStatus.RUNNING)
        energy_kwh = ModbusCodec.decode_uint32(regs[40:42]) * 0.01

        return InverterMetrics(
            inverter_id=self.config.id,
            manufacturer="Huawei",
            model="SUN2000",
            active_power_w=float(power_w),
            grid_voltage_v=GridVoltage(l1=v_l1, l2=0.0, l3=0.0),
            grid_frequency_hz=freq,
            total_energy_kwh=energy_kwh,
            inverter_status=status
        )
