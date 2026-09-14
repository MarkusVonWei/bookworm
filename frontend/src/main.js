import { createApp } from 'vue'
import './styles/variables.css'
import './styles/components.css'
import App from './App.vue'
import router from './router'
import { useUser } from './composables/useUser'

const app = createApp(App)

app.use(router)

// 应用启动时初始化匿名用户
const { initUser } = useUser()
initUser().then(() => {
  app.mount('#app')
}).catch((err) => {
  console.error('用户初始化失败, 应用仍会启动:', err)
  // 即使初始化失败也挂载应用, 降级为无用户状态
  app.mount('#app')
})
