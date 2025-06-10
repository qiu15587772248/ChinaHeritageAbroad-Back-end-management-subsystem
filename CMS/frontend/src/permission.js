import router from './router'
import store from './store'
import { Message } from 'element-ui'
import NProgress from 'nprogress' // 进度条
import 'nprogress/nprogress.css' // 进度条样式
import { getToken } from '@/utils/auth' // 从cookie获取token

NProgress.configure({ showSpinner: false }) // 进度条配置

const whiteList = ['/login'] // 免登录白名单

router.beforeEach(async(to, from, next) => {
  // 开始进度条
  NProgress.start()

  // 设置页面标题
  document.title = to.meta.title || '文化遗产后台管理系统'

  // 确定用户是否已登录
  const hasToken = getToken()

  console.log(`[Nav Guard] From: ${from.path}, To: ${to.path}`);

  if (hasToken) {
    if (to.path === '/login') {
      console.log('[Nav Guard] User has token, to /login. Redirecting to /.');
      next({ path: '/' })
      NProgress.done()
    } else {
      console.log('[Nav Guard] User has token, to non-login page.');
      console.log('[Nav Guard] store.getters.name:', store.getters.name);
      const hasGetUserInfo = store.getters.name
      
      if (hasGetUserInfo) {
        console.log('[Nav Guard] User info already in store. Calling next().');
        next();
        console.log('[Nav Guard] Called next() for existing user info.');
      } else {
        console.log('[Nav Guard] User info not in store. Fetching...');
        try {
          await store.dispatch('user/getInfo')
          console.log('[Nav Guard] Fetched user info. Calling next().');
          next()
          console.log('[Nav Guard] Called next() after fetching user info.');
        } catch (error) {
          console.error('[Nav Guard] Error fetching user info:', error);
          await store.dispatch('user/resetToken')
          Message.error(error || '认证失败，请重新登录')
          next(`/login?redirect=${to.path}`)
          NProgress.done()
        }
      }
    }
  } else {
    console.log('[Nav Guard] No token.');
    if (whiteList.indexOf(to.path) !== -1) {
      console.log('[Nav Guard] Path in whitelist. Calling next().');
      next()
      console.log('[Nav Guard] Called next() for whitelist.');
    } else {
      console.log('[Nav Guard] Path not in whitelist. Redirecting to login.');
      next(`/login?redirect=${to.path}`)
      NProgress.done()
    }
  }
})

router.afterEach(() => {
  // 结束进度条
  NProgress.done()
}) 