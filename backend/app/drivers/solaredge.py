from app.drivers.base import BaseInverterDriver
from app.drivers.codec import ModbusCodec
from app.models.metrics import InverterMetrics, InverterStatus, GridVoltage


class SolarEdgeDriver(BaseInverterDriver):
    """
    Driver para SolarEdge HD-Wave y Trifásicos bajo SunSpec Model 101/103.
    Manejo de factores de escala SunSpec para potencia, tensión y contadores acumulados.
    """

    SUNSPEC_STATUS = {
        1: InverterStatus.OFFLINE,
        2: InverterStatus.SLEEPING,  # Noche / Standby
        3: InverterStatus.STANDBY,   # Arrancando
        4: InverterStatus.RUNNING,   # Produciendo MPPT
        5: InverterStatus.RUNNING,   # Throttled / Limitado
        6: InverterStatus.STANDBY,   # Parando
        7: InverterStatus.FAULT,     # Error
    }

    async def read_telemetry(self) -> InverterMetrics:
        base = self.config.base_address  # Generalmente 40069
        rr = await self.client.read_holding_registers(
            address=base,
            count=40,
            slave=self.config.unit_id
        )
        if rr.isError():
            raise IOError(f"Error SunSpec SolarEdge en base {base}: {rr}")

        regs = rr.registers

        # +13: Watts (int16), +14: W_SF (int16)
        raw_w = ModbusCodec.decode_int16(regs[13])
        sf_w = ModbusCodec.decode_int16(regs[14])
        power_w = ModbusCodec.apply_sunspec_scale(raw_w, sf_w)

        # +15: Hz (uint16), +16: Hz_SF (int16)
        raw_hz = regs[15]
        sf_hz = ModbusCodec.decode_int16(regs[16])
        freq = ModbusCodec.apply_sunspec_scale(raw_hz, sf_hz)

        # +7: Tensión PhVphA (L1), +8: L2, +9: L3, +10: V_SF
        sf_v = ModbusCodec.decode_int16(regs[10])
        v_l1 = ModbusCodec.apply_sunspec_scale(regs[7], sf_v)
        v_l2 = ModbusCodec.apply_sunspec_scale(regs[8], sf_v)
        v_l3 = ModbusCodec.apply_sunspec_scale(regs[9], sf_v)

        # +23: Total Energy (uint32 acc32), +25: WH_SF
        raw_wh = (regs[23] << 16) | regs[24]
        sf_wh = ModbusCodec.decode_int16(regs[25])
        total_kwh = ModbusCodec.apply_sunspec_scale(raw_wh, sf_wh) / 1000.0

        # +31: Operating State (I_STATUS)
        state_code = regs[31]
        status = self.SUNSPEC_STATUS.get(state_code, InverterStatus.STANDBY)

        return InverterMetrics(
            inverter_id=self.config.id,
            manufacturer="SolarEdge",
            model="SE-Inverter-SunSpec",
            active_power_w=max(0.0, power_w),
            grid_voltage_v=GridVoltage(l1=v_l1, l2=v_l2, l3=v_l3),
            grid_frequency_hz=freq,
            total_energy_kwh=total_kwh,
            inverter_status=status
        )
