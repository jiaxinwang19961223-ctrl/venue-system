<template>
  <view class="login-page">
    <view class="glass login-card">
      <view class="login-logo">
        <image class="logo-icon" src="/static/icons/venue.svg" mode="aspectFit" />
        <text class="logo-title">万创体育</text>
        <text class="logo-sub">羽毛球 · 篮球 · 乒乓球 · 更多</text>
      </view>

      <view class="tabs">
        <view class="tab-item" :class="{ active: activeTab === 'login' }" @tap="activeTab = 'login'">登录</view>
        <view class="tab-item" :class="{ active: activeTab === 'register' }" @tap="activeTab = 'register'">注册</view>
      </view>

      <view class="form" v-if="activeTab === 'login'">
        <input class="input-glass" v-model="loginForm.username" placeholder="用户名 / 手机号" />
        <input class="input-glass" v-model="loginForm.password" type="password" placeholder="密码" />
        <view class="btn btn-primary" @tap="handleLogin">登 录</view>
        <text class="hint">测试账号：testcust / test123</text>
      </view>

      <view class="form" v-if="activeTab === 'register'">
        <input class="input-glass" v-model="regForm.username" placeholder="用户名" />
        <input class="input-glass" v-model="regForm.name" placeholder="姓名" />
        <input class="input-glass" v-model="regForm.phone" type="number" maxlength="11" placeholder="手机号" />
        <input class="input-glass" v-model="regForm.password" type="password" placeholder="密码" />
        <view class="btn btn-primary" @tap="handleRegister">注 册</view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { useUserStore } from '../../store/user'

const store = useUserStore()
const activeTab = ref('login')
const loading = ref(false)

const loginForm = ref({ username: '', password: '' })
const regForm = ref({ username: '', name: '', phone: '', password: '' })

async function handleLogin() {
  if (!loginForm.value.username || !loginForm.value.password) {
    return uni.showToast({ title: '请输入用户名和密码', icon: 'none' })
  }
  loading.value = true
  try {
    await store.login(loginForm.value.username, loginForm.value.password)
    uni.showToast({ title: '登录成功', icon: 'success' })
    uni.switchTab({ url: '/pages/index/index' })
  } catch { /* */ }
  finally { loading.value = false }
}

async function handleRegister() {
  const f = regForm.value
  if (!f.username || !f.name || !f.phone || !f.password) {
    return uni.showToast({ title: '请填写完整信息', icon: 'none' })
  }
  if (!/^1\d{10}$/.test(f.phone)) {
    return uni.showToast({ title: '手机号格式不正确', icon: 'none' })
  }
  loading.value = true
  try {
    await store.register({ username: f.username, name: f.name, phone: f.phone, password: f.password })
    uni.showToast({ title: '注册成功', icon: 'success' })
    uni.switchTab({ url: '/pages/index/index' })
  } catch { /* */ }
  finally { loading.value = false }
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
.tabs { display: flex; border-bottom: 1rpx solid rgba(0,0,0,0.06); margin-bottom: 32rpx; }
.tab-item {
  flex: 1; text-align: center; padding: 20rpx 0; font-size: 30rpx;
  color: #86868B; border-bottom: 4rpx solid transparent;
}
.tab-item.active { color: #409EFF; border-bottom-color: #409EFF; font-weight: 600; }
.form { padding: 0; }
.input-glass { margin-bottom: 20rpx; }
.hint { display: block; text-align: center; font-size: 22rpx; color: #C7C7CC; margin-top: 24rpx; }
</style>
