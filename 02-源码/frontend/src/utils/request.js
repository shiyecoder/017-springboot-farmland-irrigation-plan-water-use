import axios from 'axios'
import { ElMessage } from 'element-plus'

const service = axios.create({ baseURL: '/api', timeout: 20000 })

service.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = 'Bearer ' + token
  }
  return config
})

// 统一解包：code=200 直接返回 data；401 清登录态回登录页；其余弹业务提示
service.interceptors.response.use(
  resp => {
    const body = resp.data
    if (body && body.code === 200) {
      return body.data
    }
    if (body && body.code === 401) {
      localStorage.removeItem('token')
      if (location.hash.indexOf('/login') < 0) {
        location.href = '/login'
      }
    }
    ElMessage.error((body && body.message) || '请求失败')
    return Promise.reject(new Error((body && body.message) || '请求失败'))
  },
  err => {
    const msg = err.response && err.response.data && err.response.data.message
    ElMessage.error(msg || '网络异常，请稍后重试')
    return Promise.reject(err)
  }
)

export default service
