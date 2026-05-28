<template>
    <div class="upload-container">
      <div class="upload-box">
        <label class="file-input">
          <input type="file" @change="handleFileSelect" hidden />
          <span>选择文件</span>
        </label>
        <button 
          class="upload-button" 
          @click="startUpload" 
          :disabled="!file || isUploading"
        >
          {{ isUploading ? `上传中 ${Math.round(progress)}%` : '开始上传' }}
        </button>
      </div>
      <div class="progress-wrapper">
        <progress 
          class="upload-progress" 
          :value="progress" 
          max="100"
        ></progress>
        <div class="upload-status">
          {{ uploadedSize }} / {{ totalSize }} ({{ Math.round(progress) }}%)
        </div>
      </div>
      <div v-if="errorMessage" class="error-message">
        {{ errorMessage }}
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed } from 'vue'
  import axios from 'axios'
  import SparkMD5 from 'spark-md5'
  
  // 配置常量
  const CHUNK_SIZE = 5 * 1024 * 1024  // 5MB分块
  const MAX_RETRY = 3                 // 最大重试次数
  const CONCURRENT_UPLOADS = 4        // 并发上传数
  
  // 响应式状态
  const file = ref(null)
  const uploadId = ref('')
  const progress = ref(0)
  const isUploading = ref(false)
  const errorMessage = ref('')
  
  // 计算文件大小显示格式
  const totalSize = computed(() => {
    return formatSize(file.value?.size || 0)
  })
  
  // 计算已上传大小
  const uploadedSize = computed(() => {
    return formatSize((progress.value / 100) * (file.value?.size || 0))
  })
  
  // 处理文件选择
  const handleFileSelect = (e) => {
    resetState()
    file.value = e.target.files[0]
  }
  
  // MD5哈希计算
  const calculateMD5 = async (file) => {
    const spark = new SparkMD5.ArrayBuffer()
    const chunkSize = 2 * 1024 * 1024  // 2MB分块计算
    let cursor = 0
    
    while (cursor < file.size) {
      const chunk = file.slice(cursor, cursor + chunkSize)
      const buffer = await chunk.arrayBuffer()
      spark.append(buffer)
      cursor += chunkSize
    }
    return spark.end()
  }
  
  // 开始上传流程
  const startUpload = async () => {
    if (!validateFile()) return
    
    try {
      isUploading.value = true
      errorMessage.value = ''
      
      // 初始化上传任务
      const { data } = await axios.post('/api/upload/init', {
        filename: file.value.name,
        total_size: file.value.size
      })
      uploadId.value = data.upload_id
      
      // 分块上传
      const totalChunks = Math.ceil(file.value.size / CHUNK_SIZE)
      const uploadedChunks = new Set()
      
      // 创建上传队列
      const uploadQueue = Array.from({length: totalChunks}, (_, i) => i)
      
      while (uploadQueue.length > 0) {
        const currentChunks = uploadQueue.splice(0, CONCURRENT_UPLOADS)
        await Promise.all(currentChunks.map(i => 
          uploadChunkWithRetry(i, uploadedChunks)
        ))
      }
      
      // 完成上传
      await axios.post(`/api/upload/complete/${uploadId.value}`)
    } catch (error) {
      handleUploadError(error)
    } finally {
      isUploading.value = false
    }
  }
  
  // 分块上传重试机制
  const uploadChunkWithRetry = async (chunkIndex, uploadedChunks) => {
    let retryCount = 0
    while (retryCount <= MAX_RETRY) {
      try {
        await uploadChunk(chunkIndex, uploadedChunks)
        return
      } catch (error) {
        if (retryCount === MAX_RETRY) throw error
        retryCount++
        await new Promise(resolve => setTimeout(resolve, 1000 * retryCount))
      }
    }
  }
  
  // 执行分块上传
  const uploadChunk = async (chunkIndex, uploadedChunks) => {
    const start = chunkIndex * CHUNK_SIZE
    const end = Math.min(start + CHUNK_SIZE, file.value.size)
    const chunk = file.value.slice(start, end)
    
    const formData = new FormData()
    formData.append('file', chunk)
    
    await axios.post(
      `/api/upload/chunk/${uploadId.value}/${chunkIndex + 1}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        onUploadProgress: () => updateProgress(chunkIndex, uploadedChunks)
      }
    )
  }
  
  // 更新上传进度
  const updateProgress = (chunkIndex, uploadedChunks) => {
    uploadedChunks.add(chunkIndex)
    const loaded = Array.from(uploadedChunks).reduce((sum, index) => {
      const chunkSize = index === Math.floor(file.value.size / CHUNK_SIZE) 
        ? file.value.size % CHUNK_SIZE 
        : CHUNK_SIZE
      return sum + chunkSize
    }, 0)
    progress.value = (loaded / file.value.size) * 100
  }
  
  // 文件验证
  const validateFile = () => {
    if (!file.value) {
      errorMessage.value = '请先选择要上传的文件'
      return false
    }
    if (file.value.size > 2 * 1024 * 1024 * 1024) {  // 2GB限制
      errorMessage.value = '文件大小超过2GB限制'
      return false
    }
    return true
  }
  
  // 错误处理
  const handleUploadError = (error) => {
    console.error('上传失败:', error)
    errorMessage.value = error.response?.data?.message || '文件上传失败，请重试'
    progress.value = 0
  }
  
  // 状态重置
  const resetState = () => {
    progress.value = 0
    errorMessage.value = ''
  }
  
  // 文件大小格式化
  const formatSize = (bytes) => {
    if (bytes === 0) return '0B'
    const units = ['B', 'KB', 'MB', 'GB']
    const exp = Math.floor(Math.log(bytes) / Math.log(1024))
    return `${(bytes / Math.pow(1024, exp)).toFixed(1)}${units[exp]}`
  }
  </script>
  
  <style scoped>
  .upload-container {
    margin: 2rem;
    padding: 2rem;
    border: 1px solid #e5e7eb;
    border-radius: 0.5rem;
    max-width: 600px;
  }
  
  .upload-box {
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
  }
  
  .file-input span {
    padding: 0.5rem 1rem;
    background: #f3f4f6;
    border-radius: 0.375rem;
    cursor: pointer;
    transition: background 0.2s;
  }
  
  .file-input:hover span {
    background: #e5e7eb;
  }
  
  .upload-button {
    padding: 0.5rem 1rem;
    background: #3b82f6;
    color: white;
    border: none;
    border-radius: 0.375rem;
    cursor: pointer;
    transition: background 0.2s;
  }
  
  .upload-button:disabled {
    background: #9ca3af;
    cursor: not-allowed;
  }
  
  .progress-wrapper {
    width: 100%;
    margin-top: 1rem;
  }
  
  .upload-progress {
    width: 100%;
    height: 8px;
    border-radius: 4px;
  }
  
  .upload-status {
    margin-top: 0.5rem;
    font-size: 0.875rem;
    color: #64748b;
    text-align: center;
  }
  
  .error-message {
    color: #ef4444;
    margin-top: 1rem;
    font-size: 0.875rem;
  }
  </style>