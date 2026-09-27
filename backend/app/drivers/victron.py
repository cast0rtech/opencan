from app.drivers.base import BaseInverterDriver
from app.drivers.codec import ModbusCodec
from app.models.metrics import InverterMetrics, InverterStatus, GridVoltage


class VictronDriver(BaseInverterDriver):
    """
    Driver para Victron Cerbo GX / Venus OS (MultiPlus, Quattro, MPPTs).
    Lee simultáneamente el bus general del sistema (Unit ID 100) y VE.Bus.
    """

    VICTRON_VEBUS_STATES = {
        0: InverterStatus.OFFLINE,
        1: InverterStatus.STANDBY,
        2: InverterStatus.FAULT,
        3: InverterStatus.RUNNING,
        4: InverterStatus.RUNNING,
        5: InverterStatus.RUNNING,
        9: InverterStatus.RUNNING,
    }

    async def read_telemetry(self) -> InverterMetrics:
        # Unit 100: com.victronenergy.system
        # Reg 820: Total PV Power (uint16, 1W)
        # Reg 840: Battery SOC (uint16, factor 0.1%)
        # Reg 842: Battery Power (int16, 1W)
        rr_sys = await self.client.read_holding_registers(
            address=self.config.base_address,  # default 820
            count=35,
            slave=100
        )
        if rr_sys.isError():
            raise IOError(f"Error Modbus Victron Systemcalc (Unit 100): {rr_sys}")

        regs_sys = rr_sys.registers
        pv_power_w = float(regs_sys[0])                  # Reg 820
        battery_soc = regs_sys[20] * 0.1                 # Reg 840
        battery_power = ModbusCodec.decode_int16(regs_sys[22])  # Reg 842

        # Lectura de VE.Bus (Unit 228 por defecto para Multiplus/Quattro)
        vebus_unit = self.config.unit_id if self.config.unit_id != 100 else 228
        rr_vebus = await self.client.read_holding_registers(address=3, count=15, slave=vebus_unit)

        voltage_l1 = 230.0
        freq = 50.0
        status = InverterStatus.RUNNING

        if not rr_vebus.isError():
            state_code = rr_vebus.registers[0]           # Reg 3
            status = self.VICTRON_VEBUS_STATES.get(state_code, InverterStatus.RUNNING)
            voltage_l1 = rr_vebus.registers[9] * 0.1     # Reg 12 (12-3 = offset 9)
            freq = rr_vebus.registers[11] * 0.01         # Reg 14 (14-3 = offset 11)

        return InverterMetrics(
            inverter_id=self.config.id,
            manufacturer="Victron Energy",
            model="Cerbo GX / VE.Bus",
            active_power_w=pv_power_w,
            grid_voltage_v=GridVoltage(l1=voltage_l1, l2=0.0, l3=0.0),
            grid_frequency_hz=freq,
            inverter_status=status,
            battery_soc_pct=battery_soc,
            battery_power_w=float(battery_power)
        )
