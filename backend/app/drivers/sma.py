from app.drivers.base import BaseInverterDriver
from app.drivers.codec import ModbusCodec
from app.models.metrics import InverterMetrics, InverterStatus, GridVoltage


class SmaDriver(BaseInverterDriver):
    """
    Driver para inversores SMA Sunny Boy / Tripower vía SMA Modbus TCP.
    Usa registros de 32 bits Big-Endian típicos de SMA Speedwire.
    """

    SMA_STATUS_MAP = {
        35: InverterStatus.FAULT,
        303: InverterStatus.OFFLINE,
        307: InverterStatus.RUNNING,
        455: InverterStatus.STANDBY,
    }

    async def read_telemetry(self) -> InverterMetrics:
        # 30775: Potencia Activa Total (GridMs.W.Pac - int32)
        rr = await self.client.read_holding_registers(
            address=self.config.base_address,  # default 30775
            count=36,
            slave=self.config.unit_id
        )
        if rr.isError():
            raise IOError(f"Error Modbus SMA: {rr}")

        regs = rr.registers
        active_power = ModbusCodec.decode_int32(regs[0:2])
        freq = ModbusCodec.decode_uint32(regs[26:28]) * 0.01
        v_l1 = ModbusCodec.decode_uint32(regs[28:30]) * 0.01
        v_l2 = ModbusCodec.decode_uint32(regs[30:32]) * 0.01
        v_l3 = ModbusCodec.decode_uint32(regs[32:34]) * 0.01

        # Estado operativo (30201)
        rr_status = await self.client.read_holding_registers(address=30201, count=2, slave=self.config.unit_id)
        raw_status = ModbusCodec.decode_uint32(rr_status.registers) if not rr_status.isError() else 307
        status = self.SMA_STATUS_MAP.get(raw_status, InverterStatus.RUNNING)

        # Energía (30513)
        rr_energy = await self.client.read_holding_registers(address=30513, count=20, slave=self.config.unit_id)
        daily_wh = 0.0
        total_kwh = 0.0
        if not rr_energy.isError():
            daily_wh = float(ModbusCodec.decode_uint32(rr_energy.registers[0:2]))
            total_kwh = ModbusCodec.decode_uint32(rr_energy.registers[16:18]) / 1000.0

        return InverterMetrics(
            inverter_id=self.config.id,
            manufacturer="SMA",
            model="Sunny Tripower/Boy",
            active_power_w=max(0.0, float(active_power)),
            grid_voltage_v=GridVoltage(l1=v_l1, l2=v_l2, l3=v_l3),
            grid_frequency_hz=freq,
            daily_yield_wh=daily_wh,
            total_energy_kwh=total_kwh,
            inverter_status=status
        )
