import struct
from typing import List


class ModbusCodec:
    """Utilidades puras de conversión binaria de registros Modbus sin dependencias C."""

    @staticmethod
    def decode_int16(reg: int) -> int:
        """Convierte uint16 de Modbus en signed int16."""
        return struct.unpack(">h", struct.pack(">H", reg & 0xFFFF))[0]

    @staticmethod
    def decode_int32(regs: List[int], word_order: str = "big") -> int:
        """Decodifica un int32 a partir de 2 registros de 16 bits."""
        if len(regs) < 2:
            return 0
        r1, r2 = (regs[0], regs[1]) if word_order == "big" else (regs[1], regs[0])
        return struct.unpack(">i", struct.pack(">HH", r1, r2))[0]

    @staticmethod
    def decode_uint32(regs: List[int], word_order: str = "big") -> int:
        """Decodifica un uint32 a partir de 2 registros de 16 bits."""
        if len(regs) < 2:
            return 0
        r1, r2 = (regs[0], regs[1]) if word_order == "big" else (regs[1], regs[0])
        return struct.unpack(">I", struct.pack(">HH", r1, r2))[0]

    @staticmethod
    def decode_float32(regs: List[int], word_order: str = "big") -> float:
        """Decodifica un float32 IEEE 754 a partir de 2 registros."""
        if len(regs) < 2:
            return 0.0
        r1, r2 = (regs[0], regs[1]) if word_order == "big" else (regs[1], regs[0])
        return struct.unpack(">f", struct.pack(">HH", r1, r2))[0]

    @staticmethod
    def apply_sunspec_scale(value: int, scale_factor: int) -> float:
        """
        Aplica factor de escala SunSpec: valor * 10^SF.
        Filtra los centinelas estándar que indican campo no implementado.
        """
        if value in (0x8000, 0x7FFF, 0xFFFF, 0x80000000, 0xFFFFFFFF):
            return 0.0
        if scale_factor in (0x8000, 0x7FFF, -32768):
            return float(value)
        return float(value) * (10 ** scale_factor)
