import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import ElementUI from 'element-ui'
// import 'element-ui/lib/theme-chalk/index.css' // 注释掉默认主题
// import '@/assets/themes/theme-ochre.css' // 注释掉之前的尝试
import '@/assets/themes/custom-theme.css'      // 引入我们编译的自定义主题
import axios from 'axios'
import './permission' // 权限控制

// 导入指令
import directive from './directive'

Vue.config.productionTip = false

// 使用ElementUI
Vue.use(ElementUI)

// 注册指令
Vue.use(directive)

// 配置axios
axios.defaults.baseURL = process.env.VUE_APP_BASE_API || ''
Vue.prototype.$http = axios

// 添加请求拦截器
axios.interceptors.request.use(
  config => {
    const token = store.getters.token
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 添加响应拦截器
axios.interceptors.response.use(
  response => {
    return response
  },
  error => {
    if (error.response) {
      if (error.response.status === 401) {
        // 未授权，清除token并跳转到登录页
        store.dispatch('user/resetToken')
        router.push('/login')
      }
    }
    return Promise.reject(error)
  }
)

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app') 