<template>
  <div>
    <div class="flex items-center mb-2 space-x-2">
      <h2 class="text-xl font-semibold">物种组成与多样性分析</h2>
    </div>
    <div ref="target" class="w-full h-full"></div>      
  </div>
</template>
/////在ref等于target的div中绘制
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
    // X轴展示数据
    xAxis: {
      show: false, //不显示X
      type: "value", //表示X轴作为数据展示
      max: function (value) {
        return parseInt(value.max * 1.2);
      },
    },
    // Y轴展示数据
    yAxis: {
      type: "category",
      data: props.data.regionData.map((item) => item.name), // 统一字段名
      inverse: true,
      axisLine: { show: false }, //不展示线
      axisTick: { show: false }, //不展示刻度
      axisLabel: { color: "#9eb1c8" },
    },
    // 图标绘制的位置 对应上下左右
    grid: {
      top: 0,
      right: 0,
      bottom: 0,
      left: 0,
      containLabel: true, //计算时包含标签
    },
    // 核心配置
    series: [
      {
        type: "bar",
        data: props.data.regionData.map((item) => ({ // 统一字段名
          name: item.name || '未知物种',
          value: item.value || 0
        })),
        showBackground: true,
        backgroundStyle: {
          color: "rgba(180, 180, 180, 0.2)",
        },
        itemStyle: {
          color: "#5D98CE",
          borderRadius: 5,  // 替换已弃用的barBorderRadius
          shadowColor: "rgba(0,0,0,0.3)",
          shadowBlur: 5,
        },
        barWidth: 12,
        label: {
          show: true,
          position: "right",
          color: "#fff",  // 直接设置颜色属性
          // 移除textStyle层级
        },
      },
    ],
  };
  // 3.通过实例.setOptions(option)
  myChart.setOption(options);
};

watch(
  () => props.data,
  () => renderChart()
);
</script>