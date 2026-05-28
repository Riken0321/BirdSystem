<template>
  <div>
      <div class="flex items-center mb-2 space-x-2">
          <h2 class="text-xl font-semibold">种群趋势分析与预警</h2>
      </div>
      <div ref="chartRef" class="w-full h-[400px]"></div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount, computed } from 'vue';
import * as echarts from 'echarts';

const props = defineProps({
  data: {
    type: Object,
    required: true
  }
});

// 数据格式转换
const chartData = computed(() => {
  const header = [props.data.dimensions[0], ...props.data.dimensions.slice(1)];
  const rows = props.data.data.map(item => [
    item.species, 
    ...item.values
  ]);
  return [header, ...rows];
});

const dimensions = computed(() => props.data.dimensions);

const chartRef = ref(null);
let myChart = null;

// 初始化图表配置
const initChart = () => {
  const option = {
    legend: {
      show:false
    },
    tooltip: {
      trigger: 'axis',
      showContent: false
    },
    dataset: {
      source: chartData.value
    },
    xAxis: { type: 'category' },
    yAxis: { gridIndex: 0 },
    grid: { top: '55%' },
    series: [
      ...dimensions.value.slice(1).map(() => ({
        type: 'line',
        smooth: true,
        seriesLayoutBy: 'row',
        emphasis: { focus: 'series' }
      })),
      {
        type: 'pie',
        id: 'pie',
        selectedMode: 'single',
        selected: { disabled: false, label: { show: true } }, // 启用默认选中状态
        radius: '30%',
        center: ['50%', '25%'],
        emphasis: { focus: 'self' },
        label: {
          formatter: '{b}: {@[' + dimensions.value[0] + ']} ({d}%)',
          textStyle: {
            color: '#fff',
            fontSize: 12,
            fontWeight: 'bold',
            textShadowColor: 'rgba(0, 0, 0, 0.5)',
            textShadowBlur: 2,
            textShadowOffsetX: 1,
            textShadowOffsetY: 1
          },
          rich: {
            b: {
              color: '#ffd700',
              fontSize: 14
            }
          }
        },
        encode: {
          itemName: dimensions.value[0],
          value: dimensions.value[0],
          tooltip: dimensions.value[0]
        }
      }
    ]
  };

  // 事件监听实现联动
  myChart.on('updateAxisPointer', (event) => {
    const xAxisInfo = event.axesInfo[0];
    if (xAxisInfo) {
      const dimension = dimensions.value[xAxisInfo.value + 1];
      myChart.setOption({
        series: {
          id: 'pie',
          label: {
            formatter: `{b}: {@[${dimension}]} ({d}%)`
          },
          encode: {
            value: dimension,
            tooltip: dimension
          }
        }
      });
    }
  });

  myChart.setOption(option);
  myChart.dispatchAction({
    type: 'highlight',
    seriesIndex: 1, // 饼图系列索引
    dataIndex: 0    // 默认选中第一个数据项
  });

  // 添加默认数据更新逻辑
  if (chartData.value.length > 1) {
    myChart.dispatchAction({
      type: 'showTip',
      seriesIndex: 1,
      dataIndex: 0
    });
  }
};

// 生命周期管理
onMounted(() => {
  myChart = echarts.init(chartRef.value);
  initChart();
  window.addEventListener('resize', () => myChart.resize());
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', () => myChart.resize());
  myChart?.dispose();
});

// 监听数据变化
watch(
  chartData,
  (newVal) => {
    myChart.setOption({
      dataset: { source: newVal }
    });
    // 数据更新后重新触发高亮
    myChart.dispatchAction({
      type: 'highlight',
      seriesIndex: 1,
      dataIndex: 0
    });
  },
  { deep: true }
);
</script>