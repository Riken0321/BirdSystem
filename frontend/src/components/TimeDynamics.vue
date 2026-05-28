<template>
  <div>
      <div class="flex items-center mb-2 space-x-2">
          <h2 class="text-xl font-semibold">时间动态与行为规律</h2>
      </div>
    <div ref="target" class="w-full h-full -mt-2"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from "vue";
import * as echarts from "echarts";
// 定义接收父组件传来的值
const props = defineProps({
  data: {
    type: Object,
    required: true,
  }
});

// 1.初始化
let myChart = null;
const target = ref(null);
onMounted(() => {
  myChart = echarts.init(target.value);
  renderChart();
});

// 2.构建 option 配置对象
const renderChart = () => {
  const options = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' }
    },
    xAxis: {
      type: 'category',
      data: props.data.regionData.map(item => item.mdate),
      axisLine: { lineStyle: { color: '#9eb1c8' } }
    },
    yAxis: [
      {
        type: 'value',
        name: '观测数量',
        axisLabel: { color: '#5D98CE' },
        splitLine: { lineStyle: { color: '#2d3a4b' } }
      },
      {
        type: 'value',
        name: '温度(℃)',
        axisLabel: { color: '#FFA940' },
        splitLine: { show: false }
      }
    ],
    series: [
      {
        name: '观测数量',
        type: 'bar',
        data: props.data.regionData.map(item => item.value),
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#5D98CE' },
            { offset: 1, color: '#2E5C8A' }
          ]),
          borderRadius: [4, 4, 0, 0]
        },
        barWidth: 20
      },
      {
        name: '温度趋势',
        type: 'line',
        yAxisIndex: 1,
        data: props.data.regionData.map(item => item.temperature),
        symbol: 'circle',
        symbolSize: 8,
        smooth: true,  // 新增平滑曲线配置
        itemStyle: {
          color: '#FFA940',
          borderWidth: 2
        },
        lineStyle: {
          width: 2,
          type: 'solid'  // 修改为实线
        }
      }
    ],
    grid: {
      top: 50,
      right: 30,
      bottom: 30,
      left: 60,
      containLabel: true
    } 
  };
  // 3.通过实例.setOptions(option)
  myChart.setOption(options);
};
watch(
  () => props.data,
  () => renderChart()
);
</script>