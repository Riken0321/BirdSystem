<template>
  <div class="p-6">
    <div class="text-slate-300 text-center">
      数据总量：
      <span ref="totalCountTarget" class="font-[Electronic] text-Electronic text-7xl ml-2 mr-2 font-bold">
      </span>
      条记录
    </div>
    <div class="mt-3 flex flex-wrap">
      <div class="w-1/4 text-center text-slate-400 text-sm">
        一级保护：
        <span ref="city1" class="text-[#5DC5EF] text-3xl font-[Electronic]"></span>
      </div>
      <div class="w-1/4 text-center text-slate-400 text-sm">
        二级保护：<span ref="city2" class="text-[#5DC5EF] text-3xl font-[Electronic]"></span>
      </div>
      <div class="w-1/4 text-center text-slate-400 text-sm">
        三级保护：<span ref="city3" class="text-[#5DC5EF] text-3xl font-[Electronic]"></span>
      </div>
      <div class="w-1/4 text-center text-slate-400 text-sm">
        普通鸟类：<span ref="city4" class="text-[#5DC5EF] text-3xl font-[Electronic]"></span>
      </div>

    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import { CountUp } from 'countup.js';

const props = defineProps({
  data: {
    type: Object,
    required: true,

  }
});

const totalCountTarget = ref(null);
const city1 = ref(null);
const city2 = ref(null);
const city3 = ref(null);
const city4 = ref(null);

onMounted(() => {
  new CountUp(totalCountTarget.value, props.data.total).start();
  new CountUp(city1.value, props.data.hb).start();
  new CountUp(city2.value, props.data.db).start();
  new CountUp(city3.value, props.data.hd).start();
  new CountUp(city4.value, props.data.zn).start();
});

</script>