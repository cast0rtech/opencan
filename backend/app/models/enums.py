from enum import Enum


class DriverType(str, Enum):
    FRONIUS = "fronius"
    HUAWEI = "huawei"
    SMA = "sma"
    SOLAREDGE = "solaredge"
    VICTRON = "victron"


class InverterStatus(str, Enum):
    STANDBY = "Standby"
    RUNNING = "Running"
    FAULT = "Fault"
    SLEEPING = "Sleeping"
    OFFLINE = "Offline"
