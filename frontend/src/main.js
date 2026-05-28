import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import axios from 'axios'
import '@fortawesome/fontawesome-free/css/all.min.css'


// 配置axios基础路径
axios.defaults.baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const app = createApp(App)
app.mount('#app')