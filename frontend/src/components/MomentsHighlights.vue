<template>
  <div class="video-grid p-4">
    <div 
      v-for="item in data" 
      :key="item.id"
      class="video-item bg-white rounded-lg shadow-md overflow-hidden relative"
    >
      <div class="relative">
        <video
          :src="item.videoUrl"
          class="w-full h-48 object-cover"
          controls
          muted
        ></video>

        <!-- 右上角标题容器 -->
        <div class="absolute top-2 right-2 bg-black/50 rounded-lg p-2 backdrop-blur-sm">
          <h3 class="text-white font-semibold text-sm truncate shadow-title">
            {{ item.title || `监测片段 #${item.id}` }}
          </h3>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.shadow-title {
  text-shadow: 0 2px 4px rgba(0,0,0,0.5);
}

/* 新增标题动画效果 */
.video-item:hover h3 {
  transform: translateY(0);
  opacity: 1;
}

.video-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}

@media (max-width: 1024px) {
  .video-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .video-grid {
    grid-template-columns: 1fr;
  }
}
</style>

<script setup>
defineProps({
  data: {
    type: Array,
    required: true,
    validator: value => value.every(v => (
      'id' in v && 
      'videoUrl' in v 
    ))
  }
})
</script>