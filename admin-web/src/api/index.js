import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  timeout: 10000,
})

// 请求拦截器 — 自动附带 Token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器 — 统一错误处理
api.interceptors.response.use(
  res => res.data,
  err => {
    const msg = err.response?.data?.detail || '请求失败'
    ElMessage.error(msg)
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

// ──── Auth ────
export const login = (data) => api.post('/auth/login', data)

// ──── Venues ────
export const getVenues = () => api.get('/venues')
export const getVenue = (id) => api.get(`/venues/${id}`)
export const createVenue = (data) => api.post('/venues', data)
export const updateVenue = (id, data) => api.put(`/venues/${id}`, data)
export const getFields = (venueId) => api.get(`/venues/${venueId}/fields`)

// ──── Orders ────
export const getOrders = (params) => api.get('/orders', { params })
export const getOrder = (id) => api.get(`/orders/${id}`)
export const createOrder = (data) => api.post('/orders', data)
export const updateOrderStatus = (id, status) => api.put(`/orders/${id}/status?status=${status}`)

// ──── Members ────
export const getMembers = (params) => api.get('/members', { params })
export const getMember = (id) => api.get(`/members/${id}`)
export const createMember = (data) => api.post('/members', data)
export const updateMember = (id, data) => api.put(`/members/${id}`, data)
export const getMemberLevels = () => api.get('/members/levels/list')
export const getMemberCards = (memberId) => api.get(`/members/${memberId}/cards`)
export const createCard = (data) => api.post('/members/cards', data)

export default api
