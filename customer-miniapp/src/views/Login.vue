<template>
  <div class="login-page">
    <el-card class="login-card">
      <div class="login-logo">
        <i class="ri-store-2-fill"></i>
        <h2>场馆订场</h2>
        <p>羽毛球 · 篮球 · 乒乓球 · 更多</p>
      </div>

      <el-tabs v-model="activeTab" class="login-tabs">
        <el-tab-pane label="登录" name="login">
          <el-form :model="loginForm" @keyup.enter="handleLogin">
            <el-form-item>
              <el-input v-model="loginForm.username" placeholder="用户名 / 手机号" prefix-icon="User" size="large" />
            </el-form-item>
            <el-form-item>
              <el-input v-model="loginForm.password" type="password" placeholder="密码" prefix-icon="Lock" size="large" show-password />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" size="large" :loading="loading" @click="handleLogin" style="width:100%">
                登 录
              </el-button>
            </el-form-item>
          </el-form>
          <div class="test-hint">测试账号：testcust / test123</div>
        </el-tab-pane>

        <el-tab-pane label="注册" name="register">
          <el-form :model="regForm">
            <el-form-item>
              <el-input v-model="regForm.username" placeholder="用户名" size="large" />
            </el-form-item>
            <el-form-item>
              <el-input v-model="regForm.name" placeholder="姓名" size="large" />
            </el-form-item>
            <el-form-item>
              <el-input v-model="regForm.phone" placeholder="手机号" size="large" maxlength="11" />
            </el-form-item>
            <el-form-item>
              <el-input v-model="regForm.password" type="password" placeholder="密码" size="large" show-password />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" size="large" :loading="loading" @click="handleRegister" style="width:100%">
                注 册
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../stores/user'

const router = useRouter()
const store = useUserStore()
const activeTab = ref('login')
const loading = ref(false)

const loginForm = ref({ username: '', password: '' })
const regForm = ref({ username: '', name: '', phone: '', password: '' })

async function handleLogin() {
  if (!loginForm.value.username || !loginForm.value.password) {
    return ElMessage.warning('请输入用户名和密码')
  }
  loading.value = true
  try {
    await store.login(loginForm.value.username, loginForm.value.password)
    ElMessage.success('登录成功')
    router.push('/home')
  } catch { /* 拦截器已提示 */ }
  finally { loading.value = false }
}

async function handleRegister() {
  const f = regForm.value
  if (!f.username || !f.name || !f.phone || !f.password) {
    return ElMessage.warning('请填写完整信息')
  }
  if (!/^1\d{10}$/.test(f.phone)) {
    return ElMessage.warning('手机号格式不正确')
  }
  loading.value = true
  try {
    await store.register({
      username: f.username,
      name: f.name,
      phone: f.phone,
      password: f.password,
      role: 'customer',
    })
    ElMessage.success('注册成功')
    router.push('/home')
  } catch { /* 拦截器已提示 */ }
  finally { loading.value = false }
}
</script>

<style scoped>
.login-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f0f2f5;
}

.login-card {
  width: 420px;
  padding: 8px 0;
}

.login-logo {
  text-align: center;
  margin-bottom: 16px;
}

.login-logo i {
  font-size: 48px;
  color: #409EFF;
}

.login-logo h2 {
  margin: 8px 0 4px;
  font-size: 22px;
  color: #303133;
}

.login-logo p {
  margin: 0;
  font-size: 13px;
  color: #909399;
}

.login-tabs {
  padding: 0 8px;
}

.test-hint {
  text-align: center;
  font-size: 12px;
  color: #C0C4CC;
  margin-top: -8px;
}
</style>
