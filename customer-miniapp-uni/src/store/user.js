import { defineStore } from 'pinia'
import { login as apiLogin, registerUser } from '../api'

export const useUserStore = defineStore('user', {
  state: () => ({
    user: uni.getStorageSync('user') ? JSON.parse(uni.getStorageSync('user')) : null,
    token: uni.getStorageSync('token') || '',
  }),
  getters: {
    isLoggedIn: (state) => !!state.token,
    userName: (state) => state.user?.name || '',
    userPhone: (state) => state.user?.phone || '',
  },
  actions: {
    async login(username, password) {
      const res = await apiLogin({ username, password })
      this.token = res.access_token
      this.user = res.user
      uni.setStorageSync('token', res.access_token)
      uni.setStorageSync('user', JSON.stringify(res.user))
    },
    async register(form) {
      await registerUser({
        username: form.username,
        password: form.password,
        name: form.name,
        phone: form.phone,
        role: 'customer',
      })
      await this.login(form.username, form.password)
    },
    logout() {
      this.token = ''
      this.user = null
      uni.removeStorageSync('token')
      uni.removeStorageSync('user')
    },
  },
})
