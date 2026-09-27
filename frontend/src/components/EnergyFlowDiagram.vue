<script setup lang="ts">
import { computed } from 'vue';
import { Sun, Zap, Home, BatteryCharging, ArrowRightLeft } from 'lucide-vue-next';
import type { SystemPowerState } from '../types/telemetry';

const props = defineProps<{
  power: SystemPowerState;
}>();

const formatKw = (watts: number) => (Math.abs(watts) / 1000).toFixed(2) + ' kW';

const isGridExporting = computed(() => props.power.grid_power_w < 0);
const isPvActive = computed(() => props.power.pv_power_w > 50);
const isBatteryCharging = computed(() => props.power.battery_power_w > 0);
</script>

<template>
  <div class="relative bg-zinc-900/90 border border-zinc-800 rounded-xl p-4 flex flex-col justify-between shadow-2xl backdrop-blur-md overflow-hidden">
    <div class="flex justify-between items-center mb-2">
      <span class="text-xs font-semibold tracking-wider uppercase text-zinc-400">Flujo Energético Activo</span>
      <span class="text-xs font-mono px-2 py-0.5 rounded bg-zinc-800 text-emerald-400 flex items-center gap-1">
        <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span> SCADA Live
      </span>
    </div>

    <!-- SVG Canvas de conexiones energéticas -->
    <div class="relative w-full aspect-[16/9] max-h-[320px] flex items-center justify-center">
      <svg class="absolute inset-0 w-full h-full" viewBox="0 0 600 340" fill="none" xmlns="http://www.w3.org/2000/svg">
        <!-- PV -> Inversor -->
        <path d="M 120 70 L 300 170" 
              :class="isPvActive ? 'stroke-amber-400 energy-line-forward' : 'stroke-zinc-700'" 
              stroke-width="3" stroke-linecap="round" />

        <!-- Inversor -> Hogar/Carga -->
        <path d="M 300 170 L 480 70" 
              class="stroke-sky-400 energy-line-forward" 
              stroke-width="3" stroke-linecap="round" />

        <!-- Inversor <-> Red Eléctrica -->
        <path d="M 300 170 L 480 270" 
              :class="[
                Math.abs(props.power.grid_power_w) > 50 
                  ? (isGridExporting ? 'stroke-emerald-400 energy-line-forward' : 'stroke-rose-400 energy-line-backward') 
                  : 'stroke-zinc-700'
              ]" 
              stroke-width="3" stroke-linecap="round" />

        <!-- Inversor <-> Batería -->
        <path d="M 300 170 L 120 270" 
              :class="[
                Math.abs(props.power.battery_power_w) > 30 
                  ? (isBatteryCharging ? 'stroke-emerald-400 energy-line-backward' : 'stroke-purple-400 energy-line-forward') 
                  : 'stroke-zinc-700'
              ]" 
              stroke-width="3" stroke-linecap="round" />
      </svg>

      <!-- Nodos Interactivos -->
      
      <!-- 1. Nodo Solar -->
      <div class="absolute left-[8%] top-[8%] flex flex-col items-center">
        <div class="w-16 h-16 rounded-2xl bg-zinc-800/90 border-2 flex items-center justify-center transition-all duration-300 shadow-lg"
             :class="isPvActive ? 'border-amber-400 text-amber-400 shadow-amber-950/40' : 'border-zinc-700 text-zinc-500'">
          <Sun class="w-8 h-8" />
        </div>
        <span class="text-xs text-zinc-400 mt-1 font-medium">Solar FV</span>
        <span class="text-sm font-bold font-mono text-amber-400">{{ formatKw(power.pv_power_w) }}</span>
      </div>

      <!-- 2. Nodo Inversor Central -->
      <div class="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 flex flex-col items-center z-10">
        <div class="w-20 h-20 rounded-2xl bg-zinc-950 border-2 border-emerald-500/80 text-emerald-400 flex flex-col items-center justify-center shadow-xl shadow-emerald-950/50">
          <Zap class="w-9 h-9 animate-pulse" />
          <span class="text-[10px] font-mono tracking-tighter text-zinc-400">EMS HUB</span>
        </div>
      </div>

      <!-- 3. Nodo Consumo Cargas -->
      <div class="absolute right-[8%] top-[8%] flex flex-col items-center">
        <div class="w-16 h-16 rounded-2xl bg-zinc-800/90 border-2 border-sky-400 text-sky-400 flex items-center justify-center shadow-lg shadow-sky-950/40">
          <Home class="w-8 h-8" />
        </div>
        <span class="text-xs text-zinc-400 mt-1 font-medium">Consumo Cargas</span>
        <span class="text-sm font-bold font-mono text-sky-400">{{ formatKw(power.load_power_w) }}</span>
      </div>

      <!-- 4. Nodo Red Eléctrica -->
      <div class="absolute right-[8%] bottom-[8%] flex flex-col items-center">
        <div class="w-16 h-16 rounded-2xl bg-zinc-800/90 border-2 flex items-center justify-center shadow-lg transition-colors"
             :class="isGridExporting ? 'border-emerald-400 text-emerald-400 shadow-emerald-950/30' : 'border-rose-400 text-rose-400 shadow-rose-950/30'">
          <ArrowRightLeft class="w-8 h-8" />
        </div>
        <span class="text-xs text-zinc-400 mt-1 font-medium">{{ isGridExporting ? 'Inyectando a Red' : 'Importando Red' }}</span>
        <span class="text-sm font-bold font-mono" :class="isGridExporting ? 'text-emerald-400' : 'text-rose-400'">
          {{ formatKw(power.grid_power_w) }}
        </span>
      </div>

      <!-- 5. Nodo Batería -->
      <div class="absolute left-[8%] bottom-[8%] flex flex-col items-center">
        <div class="w-16 h-16 rounded-2xl bg-zinc-800/90 border-2 border-purple-400 text-purple-400 flex items-center justify-center shadow-lg shadow-purple-950/30">
          <BatteryCharging class="w-8 h-8" />
        </div>
        <span class="text-xs text-zinc-400 mt-1 font-medium">Batería ({{ power.battery_soc }}%)</span>
        <div class="w-14 bg-zinc-700 h-1.5 rounded-full mt-1 overflow-hidden">
          <div class="bg-purple-500 h-full transition-all duration-500" :style="{ width: `${power.battery_soc}%` }"></div>
        </div>
      </div>
    </div>
  </div>
</template>
