<script setup lang="ts">
import { useSolarTelemetry } from './composables/useSolarTelemetry';
import KpiCards from './components/KpiCards.vue';
import EnergyFlowDiagram from './components/EnergyFlowDiagram.vue';
import PowerChart from './components/PowerChart.vue';
import ModbusStatusPanel from './components/ModbusStatusPanel.vue';

const { connectionState, powerState, linkStatuses } = useSolarTelemetry();
</script>

<template>
  <main class="min-h-screen bg-zinc-950 text-zinc-100 p-3 md:p-6 font-sans touch-action-manipulation">
    <!-- Topbar SCADA Industrial -->
    <header class="flex justify-between items-center mb-4 pb-3 border-b border-zinc-800/80">
      <div class="flex items-center gap-3">
        <div class="w-3.5 h-3.5 bg-amber-400 rounded-sm shadow-[0_0_12px_#f59e0b]"></div>
        <div>
          <h1 class="text-sm md:text-base font-bold tracking-wide uppercase">SolarHub EMS | Multi-Inverter Gateway</h1>
          <p class="text-[10px] font-mono text-zinc-500">SMA • Fronius • Huawei • SolarEdge • Victron</p>
        </div>
      </div>

      <!-- Estado de conexión del Gateway -->
      <div class="flex items-center gap-2">
        <span class="text-[11px] font-mono uppercase tracking-wider hidden sm:inline"
              :class="{
                'text-emerald-400': connectionState === 'CONNECTED',
                'text-amber-400': connectionState === 'POLLING_FALLBACK',
                'text-rose-500': connectionState === 'DISCONNECTED' || connectionState === 'CONNECTING'
              }">
          {{ connectionState }}
        </span>
        <span class="w-3 h-3 rounded-full flex items-center justify-center border"
              :class="{
                'border-emerald-500 bg-emerald-500/30': connectionState === 'CONNECTED',
                'border-amber-500 bg-amber-500/30 animate-pulse': connectionState === 'POLLING_FALLBACK',
                'border-rose-500 bg-rose-500/30': connectionState === 'DISCONNECTED' || connectionState === 'CONNECTING'
              }">
          <span class="w-1.5 h-1.5 rounded-full"
                :class="{
                  'bg-emerald-400': connectionState === 'CONNECTED',
                  'bg-amber-400': connectionState === 'POLLING_FALLBACK',
                  'bg-rose-400': connectionState === 'DISCONNECTED' || connectionState === 'CONNECTING'
                }"></span>
        </span>
      </div>
    </header>

    <!-- 1. KPIs Superiores -->
    <section class="mb-4">
      <KpiCards :power="powerState" />
    </section>

    <!-- 2. Grid Central: Diagrama de Flujo + Curva ECharts -->
    <section class="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
      <EnergyFlowDiagram :power="powerState" />
      <PowerChart :power="powerState" />
    </section>

    <!-- 3. Panel Inferior: Telemetría de Buses Modbus -->
    <section>
      <ModbusStatusPanel :links="linkStatuses" />
    </section>
  </main>
</template>
