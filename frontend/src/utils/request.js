import axios from 'axios'

const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器 — 提取后端错误信息并写入 error.message，由调用方决定如何提示
service.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    const data = error.response?.data
    const msg = data?.message || data?.detail || '服务器错误'
    error.message = msg
    return Promise.reject(error)
  }
)

export default service
