<template>
  <div class="login-page">
    <el-card class="login-card">
      <div class="login-logo">
        <i class="ri-store-2-fill"></i>
        <h2>创运维</h2>
      </div>
      <el-form :model="form" label-width="0" @submit.prevent="handleLogin">
        <el-form-item>
          <el-input v-model="form.username" placeholder="用户名">
            <template #prefix><i class="ri-user-line"></i></template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.password" type="password" placeholder="密码" show-password @keyup.enter="handleLogin">
            <template #prefix><i class="ri-lock-line"></i></template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleLogin" style="width:100%">
            <i class="ri-login-box-line"></i> 登 录
          </el-button>
        </el-form-item>
      </el-form>
      <p class="hint">测试账号: admin / admin123</p>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { ElMessage } from 'element-plus'

const router = useRouter()
const store = useUserStore()
const loading = ref(false)
const form = reactive({ username: '', password: '' })

async function handleLogin() {
  if (!form.username || !form.password) return ElMessage.warning('请输入用户名和密码')
  loading.value = true
  try {
    await store.login(form.username, form.password)
    router.push('/dashboard')
  } catch { /* 拦截器已提示 */ }
  finally { loading.value = false }
}
</script>

<style scoped>
.login-page { height: 100vh; display: flex; align-items: center; justify-content: center; background: #f0f2f5; }
.login-card { width: 400px; }
.login-logo { text-align: center; margin-bottom: 24px; }
.login-logo i { font-size: 48px; color: #409EFF; display: block; margin-bottom: 8px; }
.login-logo h2 { margin: 0; }
.hint { text-align: center; color: #999; font-size: 13px; }
</style>
