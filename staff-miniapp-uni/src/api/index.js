import api from './request'

// Auth
export const login = (data) => api.post('/auth/login', data)
export const getMe = () => api.get('/auth/me')

// Dashboard
export const getTodayDashboard = (venueId) =>
  api.get('/dashboard/today', { venue_id: venueId })

// Venues & Fields
export const getVenues = () => api.get('/venues')
export const getVenue = (id) => api.get(`/venues/${id}`)
export const getFields = (venueId) => api.get(`/venues/${venueId}/fields`)
export const getAvailability = (fieldId, date) =>
  api.get(`/venues/fields/${fieldId}/availability`, { date })

// Orders
export const getOrders = (params) => api.get('/orders', params)
export const createOrder = (data) => api.post('/orders', data)
export const updateOrderStatus = (id, status) =>
  api.put(`/orders/${id}/status?status=${status}`)
export const getOrder = (id) => api.get(`/orders/${id}`)

// Members
export const getMembers = (params) => api.get('/members', params)
export const getMember = (id) => api.get(`/members/${id}`)
export const getMemberCards = (id) => api.get(`/members/${id}/cards`)
export const getMemberOrders = (id, limit = 50) =>
  api.get(`/members/${id}/orders`, { limit })
export const memberConsume = (id, data) =>
  api.post(`/members/${id}/consume`, data)
export const getCardLogs = (params) => api.get('/members/card-logs', params)
export const updateCardValidity = (memberId, cardId, data) =>
  api.put(`/members/${memberId}/cards/${cardId}/validity`, data)

// Card Types
export const getCardTypes = () => api.get('/card-types')

export default api
