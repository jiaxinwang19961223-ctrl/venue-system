import { defineStore } from 'pinia'
import { login as apiLogin } from '../api'

export const useUserStore = defineStore('user', {
  state: () => ({
    user: uni.getStorageSync('user') ? JSON.parse(uni.getStorageSync('user')) : null,
    token: uni.getStorageSync('token') || '',
  }),
  getters: {
    isLoggedIn: (state) => !!state.token,
    userName: (state) => state.user?.name || '',
    userRole: (state) => state.user?.role || '',
    userRoleLabel: (state) => {
      const map = {
        core_management: '核心管理',
        manager: '馆长',
        reception: '前台',
        coach: '教练',
      }
      return map[state.user?.role] || state.user?.role || ''
    },
    venueId: (state) => state.user?.venue_id || null,
    canManage: (state) =>
      ['core_management', 'manager'].includes(state.user?.role),
    canOrder: (state) =>
      ['core_management', 'manager', 'reception'].includes(state.user?.role),
    canCheckIn: (state) =>
      ['core_management', 'manager', 'coach'].includes(state.user?.role),
  },
  actions: {
    async login(username, password) {
      const res = await apiLogin({ username, password })
      // 员工端：拒绝顾客登录
      if (res.user.role === 'customer') {
        throw new Error('顾客请使用顾客小程序')
      }
      this.token = res.access_token
      this.user = res.user
      uni.setStorageSync('token', res.access_token)
      uni.setStorageSync('user', JSON.stringify(res.user))
    },
    logout() {
      this.token = ''
      this.user = null
      uni.removeStorageSync('token')
      uni.removeStorageSync('user')
    },
  },
})
