import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login as loginApi, registerUser as registerApi } from '../api'

export const useUserStore = defineStore('user', () => {
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const token = ref(localStorage.getItem('token') || '')

  async function login(username, password) {
    const res = await loginApi({ username, password })
    token.value = res.access_token
    user.value = res.user
    localStorage.setItem('token', res.access_token)
    localStorage.setItem('user', JSON.stringify(res.user))
    return res
  }

  async function register(form) {
    await registerApi(form)
    // 注册成功后自动登录
    return await login(form.username, form.password)
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  function hasRole(...roles) {
    return user.value && roles.includes(user.value.role)
  }

  return { user, token, login, register, logout, hasRole }
})
