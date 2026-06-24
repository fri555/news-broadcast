import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import './style.css'

// 在 Vue 挂载前应用主题——防止刷新闪烁和重置
const savedTheme = localStorage.getItem('theme') || 'theme-warm'
document.documentElement.classList.add(savedTheme)

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
