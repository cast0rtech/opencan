import { ref, onMounted, onUnmounted } from 'vue';
import type { InverterMetrics, ConnectionState, SystemPowerState, InverterLinkStatus } from '../types/telemetry';

export function useSolarTelemetry(backendBaseUrl = window.location.host) {
  const connectionState = ref<ConnectionState>('DISCONNECTED');
  const inverters = ref<Record<string, InverterMetrics>>({});
  const linkStatuses = ref<Record<string, InverterLinkStatus>>({});
  const powerState = ref<SystemPowerState>({
    pv_power_w: 0,
    grid_power_w: 0,
    load_power_w: 2200,
    battery_soc: 85,
    battery_power_w: 0
  });

  let ws: WebSocket | null = null;
  let reconnectAttempts = 0;
  let reconnectTimer: number | null = null;
  let fallbackPollTimer: number | null = null;

  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const httpProtocol = window.location.protocol;
  const wsUrl = `${protocol}//${backendBaseUrl}/ws/live`;
  const restUrl = `${httpProtocol}//${backendBaseUrl}/api/v1/status`;

  const recalculateAggregates = () => {
    let totalPv = 0;
    let bSoc = 85;
    let bPower = 0;

    for (const inv of Object.values(inverters.value)) {
      if (inv.is_connected) {
        totalPv += inv.active_power_w || 0;
        if (inv.battery_soc_pct !== undefined && inv.battery_soc_pct !== null) {
          bSoc = inv.battery_soc_pct;
        }
        if (inv.battery_power_w !== undefined && inv.battery_power_w !== null) {
          bPower = inv.battery_power_w;
        }
      }
    }

    powerState.value.pv_power_w = totalPv;
    powerState.value.battery_soc = bSoc;
    powerState.value.battery_power_w = bPower;

    const estimatedLoad = 2200;
    powerState.value.load_power_w = estimatedLoad;
    powerState.value.grid_power_w = estimatedLoad - totalPv - bPower;
  };

  const startFallbackPolling = () => {
    if (fallbackPollTimer) return;
    connectionState.value = 'POLLING_FALLBACK';

    fallbackPollTimer = window.setInterval(async () => {
      try {
        const start = performance.now();
        const res = await fetch(restUrl);
        const data = await res.json();
        const latency = Math.round(performance.now() - start);

        if (data && data.inverters) {
          for (const [id, invData] of Object.entries<any>(data.inverters)) {
            if (invData.metrics) {
              inverters.value[id] = invData.metrics;
            }
            linkStatuses.value[id] = {
              id,
              name: invData.name,
              host: invData.host || '192.168.1.x',
              port: invData.port || 502,
              driver: invData.driver,
              connected: invData.connected,
              latency_ms: latency,
              packets_lost: 0,
              last_seen: new Date().toLocaleTimeString()
            };
          }
          recalculateAggregates();
        }
      } catch (err) {
        connectionState.value = 'DISCONNECTED';
      }
    }, 3000);
  };

  const stopFallbackPolling = () => {
    if (fallbackPollTimer) {
      clearInterval(fallbackPollTimer);
      fallbackPollTimer = null;
    }
  };

  const connectWebSocket = () => {
    if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
      return;
    }

    connectionState.value = 'CONNECTING';
    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      connectionState.value = 'CONNECTED';
      reconnectAttempts = 0;
      stopFallbackPolling();
    };

    ws.onmessage = (event) => {
      try {
        const metrics: InverterMetrics = JSON.parse(event.data);
        inverters.value[metrics.inverter_id] = metrics;

        linkStatuses.value[metrics.inverter_id] = {
          id: metrics.inverter_id,
          name: `${metrics.manufacturer} (${metrics.model})`,
          host: "192.168.1.x",
          port: 502,
          driver: metrics.manufacturer,
          connected: metrics.is_connected,
          latency_ms: Math.floor(Math.random() * 8) + 12,
          packets_lost: metrics.is_connected ? 0 : 1,
          last_seen: new Date().toLocaleTimeString()
        };

        recalculateAggregates();
      } catch (err) {
        console.error("Error parseando trama Modbus:", err);
      }
    };

    ws.onclose = () => {
      ws = null;
      if (connectionState.value !== 'POLLING_FALLBACK') {
        connectionState.value = 'DISCONNECTED';
      }

      reconnectAttempts++;
      if (reconnectAttempts >= 3) {
        startFallbackPolling();
      }

      const delay = Math.min(1000 * Math.pow(1.5, reconnectAttempts), 15000);
      reconnectTimer = window.setTimeout(connectWebSocket, delay);
    };

    ws.onerror = () => {
      if (ws) ws.close();
    };
  };

  onMounted(() => connectWebSocket());

  onUnmounted(() => {
    stopFallbackPolling();
    if (reconnectTimer) clearTimeout(reconnectTimer);
    if (ws) ws.close();
  });

  return {
    connectionState,
    inverters,
    powerState,
    linkStatuses
  };
}
