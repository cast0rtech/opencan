<script setup lang="ts">
import type { InverterLinkStatus } from '../types/telemetry';

defineProps<{
  links: Record<string, InverterLinkStatus>;
}>();
</script>

<template>
  <div class="bg-zinc-900/90 border border-zinc-800 rounded-xl p-4 shadow-xl">
    <div class="flex justify-between items-center mb-3">
      <span class="text-xs font-semibold tracking-wider uppercase text-zinc-400">Buses de Comunicación Modbus TCP / RTU</span>
      <span class="text-[10px] font-mono text-zinc-500">Timeout límite: 3000ms</span>
    </div>

    <div class="overflow-x-auto">
      <table class="w-full text-left text-xs font-mono">
        <thead>
          <tr class="text-zinc-500 border-b border-zinc-800/80 pb-2">
            <th class="pb-2 font-medium">DISPOSITIVO</th>
            <th class="pb-2 font-medium">FABRICANTE</th>
            <th class="pb-2 font-medium">DIRECCIÓN IP</th>
            <th class="pb-2 font-medium">ENLACE</th>
            <th class="pb-2 font-medium">RTT</th>
            <th class="pb-2 font-medium text-right">ÚLTIMO FRAME</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-zinc-800/50">
          <tr v-for="link in links" :key="link.id" class="text-zinc-300 hover:bg-zinc-800/30">
            <td class="py-2.5 font-sans font-medium text-zinc-200 flex items-center gap-1.5">
              <span class="w-2 h-2 rounded-full" :class="link.connected ? 'bg-emerald-400 shadow-[0_0_8px_#34d399]' : 'bg-rose-500'"></span>
              {{ link.name }}
            </td>
            <td class="py-2.5 text-zinc-400">{{ link.driver }}</td>
            <td class="py-2.5 text-zinc-400">{{ link.host }}:{{ link.port }}</td>
            <td class="py-2.5">
              <span class="px-1.5 py-0.5 rounded text-[10px]" 
                    :class="link.connected ? 'bg-emerald-950/70 text-emerald-400 border border-emerald-800/40' : 'bg-rose-950/70 text-rose-400 border border-rose-800/40'">
                {{ link.connected ? 'ONLINE' : 'OFFLINE' }}
              </span>
            </td>
            <td class="py-2.5 text-zinc-400">{{ link.latency_ms }} ms</td>
            <td class="py-2.5 text-right text-zinc-500">{{ link.last_seen }}</td>
          </tr>
          <tr v-if="Object.keys(links).length === 0">
            <td colspan="6" class="py-4 text-center text-zinc-500">
              Esperando frames de telemetría Modbus...
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
