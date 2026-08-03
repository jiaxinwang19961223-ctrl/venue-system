<template>
  <view class="login-page">
    <view class="glass login-card">
      <view class="login-logo">
        <image class="logo-icon" src="/static/icons/venue.svg" mode="aspectFit" />
        <text class="logo-title">场馆运营</text>
        <text class="logo-sub">员工端 · 快速开单管理</text>
      </view>

      <view class="form">
        <input class="input-glass" v-model="form.username" placeholder="用户名 / 手机号" />
        <input class="input-glass" v-model="form.password" type="password" placeholder="密码" />
        <view class="btn btn-primary" @tap="handleLogin" :class="{ 'btn-disabled': loading }">
          {{ loading ? '登录中...' : '登 录' }}
        </view>
        <text class="hint">仅限员工登录 · 顾客请使用顾客小程序</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { useUserStore } from '../../store/user'

const store = useUserStore()
const loading = ref(false)
const form = ref({ username: '', password: '' })

async function handleLogin() {
  if (!form.value.username || !form.value.password) {
    return uni.showToast({ title: '请输入用户名和密码', icon: 'none' })
  }
  loading.value = true
  try {
    await store.login(form.value.username, form.value.password)
    uni.showToast({ title: '登录成功', icon: 'success' })
    setTimeout(() => uni.switchTab({ url: '/pages/index/index' }), 800)
  } catch (e) {
    uni.showToast({ title: e.message || '登录失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  display: flex; justify-content: center; align-items: center;
  min-height: 100vh; padding: 32rpx;
}
.login-card {
  width: 100%; max-width: 640rpx;
  padding: 48rpx 40rpx;
}
.login-logo { text-align: center; margin-bottom: 40rpx; }
.logo-icon { width: 100rpx; height: 100rpx; margin: 0 auto; display: block; }
.logo-title { display: block; font-size: 44rpx; font-weight: 700; color: #1D1D1F; margin-top: 12rpx; }
.logo-sub { display: block; font-size: 24rpx; color: #86868B; margin-top: 8rpx; }
.form { padding: 0; }
.input-glass { margin-bottom: 20rpx; }
.hint { display: block; text-align: center; font-size: 22rpx; color: #C7C7CC; margin-top: 24rpx; }
.btn-disabled { opacity: 0.6; pointer-events: none; }
</style>
