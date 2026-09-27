export interface GridVoltage {
  l1: number;
  l2: number;
  l3: number;
}

export interface InverterMetrics {
  inverter_id: string;
  manufacturer: string;
  model: string;
  timestamp: string;
  is_connected: boolean;
  active_power_w: number;
  reactive_power_var?: number;
  daily_yield_wh?: number;
  total_energy_kwh: number;
  grid_voltage_v: GridVoltage;
  grid_frequency_hz: number;
  inverter_status: string;
  internal_temperature_c?: number;
  battery_soc_pct?: number;
  battery_power_w?: number;
  error_message?: string;
}

export interface SystemPowerState {
  pv_power_w: number;
  grid_power_w: number;
  load_power_w: number;
  battery_soc: number;
  battery_power_w: number;
}

export type ConnectionState = 'CONNECTING' | 'CONNECTED' | 'DISCONNECTED' | 'POLLING_FALLBACK';

export interface InverterLinkStatus {
  id: string;
  name: string;
  host: string;
  port: number;
  driver: string;
  connected: boolean;
  latency_ms: number;
  packets_lost: number;
  last_seen: string;
}
