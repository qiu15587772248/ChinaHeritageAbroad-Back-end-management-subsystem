import axios from 'axios'
import { MessageBox, Message } from 'element-ui'
import store from '@/store'
import { getToken } from '@/utils/auth'

// 创建axios实例
const service = axios.create({
  baseURL: process.env.VUE_APP_BASE_API || '', // url = base url + request url
  timeout: 5000 // 请求超时时间
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    // 发送请求前做一些处理
    if (store.getters.token) {
      // 让每个请求携带token
      config.headers['Authorization'] = `Bearer ${getToken()}`
    }
    return config
  },
  error => {
    // 请求错误处理
    console.log(error) // for debug
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  /**
   * 如果您想获得http信息，如头信息或状态信息
   * 请返回 response => response
  */

  /**
   * 通过自定义代码确定请求状态
   * 这里只是一个例子
   * 您也可以通过HTTP状态码判断状态
   */
  response => {
    const res = response.data

    // 如果响应不是200或201，则判定为错误
    if (response.status !== 200 && response.status !== 201) {
      Message({
        message: res.message || '请求错误',
        type: 'error',
        duration: 5 * 1000
      })

      // 401: 未登录/Token过期
      if (response.status === 401) {
        // 重新登录
        MessageBox.confirm('您已登出，可以取消以停留在此页面，或者重新登录', '确认登出', {
          confirmButtonText: '重新登录',
          cancelButtonText: '取消',
          type: 'warning'
        }).then(() => {
          store.dispatch('user/resetToken').then(() => {
            location.reload()
          })
        })
      }
      return Promise.reject(new Error(res.message || '请求错误'))
    } else {
      return response
    }
  },
  error => {
    console.log('err' + error) // for debug
    let message = error.message
    if (error.response) {
      if (error.response.status === 401) {
        // 401: 未登录/Token过期
        store.dispatch('user/resetToken').then(() => {
          location.reload()
        })
        message = '未经授权，请重新登录'
      } else {
        message = error.response.data.message || '请求错误'
      }
    }
    Message({
      message: message,
      type: 'error',
      duration: 5 * 1000
    })
    return Promise.reject(error)
  }
)

export default service