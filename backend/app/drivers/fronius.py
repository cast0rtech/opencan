from app.drivers.base import BaseInverterDriver
from app.drivers.codec import ModbusCodec
from app.models.metrics import InverterMetrics, InverterStatus, GridVoltage


class FroniusDriver(BaseInverterDriver):
    """Fronius Primo / Symo / GEN24 bajo SunSpec Model 101/103."""

    async def read_telemetry(self) -> InverterMetrics:
        base = self.config.base_address
        rr = await self.client.read_holding_registers(
            address=base,
            count=38,
            slave=self.config.unit_id
        )
        if rr.isError():
            raise IOError(f"Error Fronius SunSpec: {rr}")

        r = rr.registers

        # Offsets SunSpec: 13=W, 14=W_SF, 15=Hz, 16=Hz_SF, 7=V_L1, 10=V_SF, 23=WH, 25=WH_SF
        w = ModbusCodec.apply_sunspec_scale(
            ModbusCodec.decode_int16(r[13]),
            ModbusCodec.decode_int16(r[14])
        )
        freq = ModbusCodec.apply_sunspec_scale(
            r[15],
            ModbusCodec.decode_int16(r[16])
        )
        sf_v = ModbusCodec.decode_int16(r[10])
        v1 = ModbusCodec.apply_sunspec_scale(r[7], sf_v)
        v2 = ModbusCodec.apply_sunspec_scale(r[8], sf_v)
        v3 = ModbusCodec.apply_sunspec_scale(r[9], sf_v)
        wh = ModbusCodec.apply_sunspec_scale(
            (r[23] << 16) | r[24],
            ModbusCodec.decode_int16(r[25])
        )

        return InverterMetrics(
            inverter_id=self.config.id,
            manufacturer="Fronius",
            model="Symo/GEN24",
            active_power_w=max(0.0, w),
            grid_voltage_v=GridVoltage(l1=v1, l2=v2, l3=v3),
            grid_frequency_hz=freq,
            total_energy_kwh=wh / 1000.0,
            inverter_status=InverterStatus.RUNNING if w > 10 else InverterStatus.STANDBY
        )
