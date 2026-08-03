import api from './request'

export const login = (data) => api.post('/auth/login', data)
export const registerUser = (data) => api.post('/auth/register', data)
export const getMe = () => api.get('/auth/me')

export const getVenues = () => api.get('/venues')
export const getVenue = (id) => api.get(`/venues/${id}`)
export const getAvailability = (fieldId, date) =>
  api.get(`/venues/fields/${fieldId}/availability`, { date })

export const getOrders = (params) => api.get('/orders', params)
export const createOrder = (data) => api.post('/orders', data)
export const updateOrderStatus = (id, status) =>
  api.put(`/orders/${id}/status?status=${status}`)

export const getMyMember = (venueId) =>
  api.get('/members/me', venueId ? { venue_id: venueId } : {})
export const registerMember = (data) => api.post('/members/me', data)
export const buyCard = (data) => api.post('/members/me/cards', data)

export const getCardTypes = () => api.get('/card-types')

export default api
