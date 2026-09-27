<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue';
import * as echarts from 'echarts';
import type { SystemPowerState } from '../types/telemetry';

const props = defineProps<{
  power: SystemPowerState;
}>();

const chartContainer = ref<HTMLDivElement | null>(null);
let chartInstance: echarts.ECharts | null = null;

const timeData: string[] = [];
const solarSeries: number[] = [];
const loadSeries: number[] = [];
const gridSeries: number[] = [];
const maxDataPoints = 30;

const initChart = () => {
  if (!chartContainer.value) return;

  chartInstance = echarts.init(chartContainer.value, 'dark', {
    renderer: 'canvas'
  });

  const option: echarts.EChartsOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(24, 24, 27, 0.95)',
      borderColor: '#3f3f46',
      textStyle: { color: '#f4f4f5', fontFamily: 'monospace' }
    },
    legend: {
      data: ['Generación FV', 'Consumo Cargas', 'Balance Red'],
      textStyle: { color: '#a1a1aa' },
      top: 5
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '5%',
      top: '18%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: timeData,
      axisLine: { lineStyle: { color: '#3f3f46' } },
      axisLabel: { color: '#71717a', fontSize: 10 }
    },
    yAxis: {
      type: 'value',
      name: 'kW',
      splitLine: { lineStyle: { color: '#27272a' } },
      axisLabel: { color: '#71717a' }
    },
    series: [
      {
        name: 'Generación FV',
        type: 'line',
        smooth: true,
        showSymbol: false,
        lineStyle: { width: 2.5, color: '#f59e0b' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(245, 158, 11, 0.35)' },
            { offset: 1, color: 'rgba(245, 158, 11, 0.0)' }
          ])
        },
        data: solarSeries
      },
      {
        name: 'Consumo Cargas',
        type: 'line',
        smooth: true,
        showSymbol: false,
        lineStyle: { width: 2, color: '#38bdf8' },
        data: loadSeries
      },
      {
        name: 'Balance Red',
        type: 'line',
        smooth: true,
        showSymbol: false,
        lineStyle: { width: 1.8, color: '#f43f5e', type: 'dashed' },
        data: gridSeries
      }
    ]
  };

  chartInstance.setOption(option);
};

watch(() => props.power, (newVal) => {
  if (!chartInstance) return;

  const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });

  if (timeData.length >= maxDataPoints) {
    timeData.shift();
    solarSeries.shift();
    loadSeries.shift();
    gridSeries.shift();
  }

  timeData.push(now);
  solarSeries.push(Number((newVal.pv_power_w / 1000).toFixed(2)));
  loadSeries.push(Number((newVal.load_power_w / 1000).toFixed(2)));
  gridSeries.push(Number((newVal.grid_power_w / 1000).toFixed(2)));

  chartInstance.setOption({
    xAxis: { data: timeData },
    series: [
      { data: solarSeries },
      { data: loadSeries },
      { data: gridSeries }
    ]
  }, { notMerge: false, lazyUpdate: true });
}, { deep: true });

const handleResize = () => chartInstance?.resize();

onMounted(() => {
  initChart();
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  chartInstance?.dispose();
});
</script>

<template>
  <div class="bg-zinc-900/90 border border-zinc-800 rounded-xl p-4 shadow-xl flex flex-col">
    <div class="flex justify-between items-center mb-1">
      <span class="text-xs font-semibold tracking-wider uppercase text-zinc-400">Curva de Balance Energético (kW)</span>
      <span class="text-[11px] font-mono text-zinc-500">Muestreo en tiempo real</span>
    </div>
    <div ref="chartContainer" class="w-full h-[260px] md:h-[300px]"></div>
  </div>
</template>
