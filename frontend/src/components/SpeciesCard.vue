<template>
  <div class="mb-6 pl-2 pt-4">
    <h2 class="text-3xl text-[#5DC5EF] font-bold text-left pl-3 mt-2">
      湖南农业大学鸟类监测平台
    </h2>
  </div>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 bg-transparent">
    <!-- 累计观测物种卡片 -->
    <div class="bg-transparent p-6 rounded-lg flex flex-col items-center justify-center">
      <div class="p-3 bg-green-trans rounded-full mb-4">
        <i class="fas fa-dove text-blue-500 text-4xl"></i>
      </div>
      <p class="text-[#5DC5EF] text-3xl font-[Electronic]">{{ data.totalSpecies }}</p>
      <h3 class="text-sm font-medium text-blue-200 dark:text-gray-400 whitespace-nowrap">累计物种</h3>
    </div>

    <!-- 其他三个卡片结构相同，仅修改图标和颜色 -->
    <!-- 今日活跃物种 -->
    <div class="bg-transparent p-6 rounded-lg flex flex-col items-center justify-center">
      <div class="p-3 bg-blue-trans rounded-full mb-4">
        <i class="fas fa-feather text-blue-500 text-4xl"></i>
      </div>
      <p class="text-[#5DC5EF] text-3xl font-[Electronic]">{{ data.todayActive }}</p>
      <h3 class="text-sm font-medium text-blue-200 dark:text-gray-400 whitespace-nowrap">活跃物种</h3>
    </div>

    <!-- 在线观测设备 -->
    <div class="bg-transparent p-6 rounded-lg flex flex-col items-center justify-center">
      <div class="p-3 bg-purple-trans rounded-full mb-4">
        <i class="fas fa-video text-blue-500 text-4xl"></i>
      </div>
      <p class="text-[#5DC5EF] text-3xl font-[Electronic]">{{ data.onlineDevices }}</p>
      <h3 class="text-sm font-medium text-blue-200 dark:text-gray-400 whitespace-nowrap">投喂设备</h3>
    </div>

    <!-- 天气 -->
    <div class="bg-transparent p-6 rounded-lg flex flex-col items-center justify-center">
      <div class="p-3 bg-yellow-trans  rounded-full mb-4">
        <i class="fas fa-sun text-yellow-500 text-4xl"></i>
      </div>
      <p class="text-[#5DC5EF] text-3xl font-[Electronic]">{{ data.weather }}</p>
      <h3 class="text-sm font-medium text-blue-200 dark:text-gray-400 whitespace-nowrap">实时天气</h3>
    </div>
  </div>
</template>


// 使用defineProps声明接收父组件传递的props，defineProps具备数据验证功能
<script setup>
const props = defineProps({
  data: {
    type: Object,
    required: true,
  }
});
</script>