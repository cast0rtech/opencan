<script setup lang="ts">
import { Sun, Home, ArrowUpRight, ArrowDownRight, Activity } from 'lucide-vue-next';
import type { SystemPowerState } from '../types/telemetry';

defineProps<{
  power: SystemPowerState;
}>();
</script>

<template>
  <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
    <!-- KPI 1: Producción FV -->
    <div class="bg-zinc-900 border border-zinc-800 rounded-xl p-3.5 flex flex-col justify-between">
      <div class="flex justify-between items-start text-zinc-400">
        <span class="text-xs font-medium uppercase">Potencia FV</span>
        <Sun class="w-4 h-4 text-amber-400" />
      </div>
      <div class="mt-2 flex items-baseline gap-1">
        <span class="text-2xl lg:text-3xl font-bold font-mono text-amber-400">
          {{ (power.pv_power_w / 1000).toFixed(2) }}
        </span>
        <span class="text-xs text-zinc-500 font-mono">kW</span>
      </div>
      <span class="text-[10px] text-zinc-500 mt-1">Generación total activa</span>
    </div>

    <!-- KPI 2: Consumo Instalación -->
    <div class="bg-zinc-900 border border-zinc-800 rounded-xl p-3.5 flex flex-col justify-between">
      <div class="flex justify-between items-start text-zinc-400">
        <span class="text-xs font-medium uppercase">Consumo Actual</span>
        <Home class="w-4 h-4 text-sky-400" />
      </div>
      <div class="mt-2 flex items-baseline gap-1">
        <span class="text-2xl lg:text-3xl font-bold font-mono text-sky-400">
          {{ (power.load_power_w / 1000).toFixed(2) }}
        </span>
        <span class="text-xs text-zinc-500 font-mono">kW</span>
      </div>
      <span class="text-[10px] text-zinc-500 mt-1">Demanda de cargas</span>
    </div>

    <!-- KPI 3: Balance Red -->
    <div class="bg-zinc-900 border border-zinc-800 rounded-xl p-3.5 flex flex-col justify-between">
      <div class="flex justify-between items-start text-zinc-400">
        <span class="text-xs font-medium uppercase">Balance Red</span>
        <component :is="power.grid_power_w < 0 ? ArrowUpRight : ArrowDownRight" 
                   :class="power.grid_power_w < 0 ? 'text-emerald-400' : 'text-rose-400'" class="w-4 h-4" />
      </div>
      <div class="mt-2 flex items-baseline gap-1">
        <span class="text-2xl lg:text-3xl font-bold font-mono" :class="power.grid_power_w < 0 ? 'text-emerald-400' : 'text-rose-400'">
          {{ (Math.abs(power.grid_power_w) / 1000).toFixed(2) }}
        </span>
        <span class="text-xs text-zinc-500 font-mono">kW</span>
      </div>
      <span class="text-[10px] text-zinc-500 mt-1">
        {{ power.grid_power_w < 0 ? 'Inyección excedentes' : 'Importación de red' }}
      </span>
    </div>

    <!-- KPI 4: Autoconsumo / Batería -->
    <div class="bg-zinc-900 border border-zinc-800 rounded-xl p-3.5 flex flex-col justify-between">
      <div class="flex justify-between items-start text-zinc-400">
        <span class="text-xs font-medium uppercase">Batería (SOC)</span>
        <Activity class="w-4 h-4 text-purple-400" />
      </div>
      <div class="mt-2 flex items-baseline gap-1">
        <span class="text-2xl lg:text-3xl font-bold font-mono text-purple-400">
          {{ power.battery_soc }}
        </span>
        <span class="text-xs text-zinc-500 font-mono">%</span>
      </div>
      <span class="text-[10px] text-zinc-500 mt-1">Almacenamiento ESS</span>
    </div>
  </div>
</template>
