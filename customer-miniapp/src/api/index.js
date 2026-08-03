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
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

// ──── Auth ────
export const login = (data) => api.post('/auth/login', data)
export const registerUser = (data) => api.post('/auth/register', data)
export const getMe = () => api.get('/auth/me')

// ──── Venues ────
export const getVenues = () => api.get('/venues')
export const getVenue = (id) => api.get(`/venues/${id}`)
export const getFields = (venueId) => api.get(`/venues/${venueId}/fields`)
export const getAvailability = (fieldId, date) =>
  api.get(`/venues/fields/${fieldId}/availability`, { params: { date } })

// ──── Orders ────
export const getOrders = (params) => api.get('/orders', { params })
export const createOrder = (data) => api.post('/orders', data)
export const updateOrderStatus = (id, status) =>
  api.put(`/orders/${id}/status?status=${status}`)

// ──── Members (顾客自助) ────
export const getMyMember = (venueId) =>
  api.get('/members/me', { params: venueId ? { venue_id: venueId } : {} })
export const registerMember = (data) => api.post('/members/me', data)
export const buyCard = (data) => api.post('/members/me/cards', data)

// ──── Card Types ────
export const getCardTypes = () => api.get('/card-types')

export default api
