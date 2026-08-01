<template>
  <el-container class="layout">
    <el-aside width="220px" class="aside">
      <div class="logo"><i class="ri-store-2-fill"></i> 场馆运营</div>
      <el-menu
        :default-active="route.path"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <el-menu-item index="/dashboard">
          <i class="ri-dashboard-line ri-lg"></i>
          <span>首页</span>
        </el-menu-item>
        <el-menu-item index="/venues">
          <i class="ri-building-2-line ri-lg"></i>
          <span>场馆管理</span>
        </el-menu-item>
        <el-menu-item index="/members">
          <i class="ri-vip-crown-line ri-lg"></i>
          <span>会员管理</span>
        </el-menu-item>
        <el-menu-item index="/court-board">
          <i class="ri-grid-line ri-lg"></i>
          <span>包场看板</span>
        </el-menu-item>
        <el-menu-item index="/orders">
          <i class="ri-bill-line ri-lg"></i>
          <span>订单管理</span>
        </el-menu-item>
        <el-menu-item index="/members">
          <i class="ri-vip-crown-line ri-lg"></i>
          <span>会员管理</span>
        </el-menu-item>
        <el-menu-item index="/card-types">
          <i class="ri-bank-card-line ri-lg"></i>
          <span>卡种管理</span>
        </el-menu-item>
        <el-menu-item index="/face-checkin">
          <i class="ri-camera-line ri-lg"></i>
          <span>人脸签到</span>
        </el-menu-item>
        <el-menu-item index="/courses" disabled>
          <i class="ri-calendar-check-line ri-lg"></i>
          <span>课程管理</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <span>{{ route.meta.title || '' }}</span>
        <div class="header-right">
          <span class="user-name">{{ store.user?.name }}</span>
          <el-tag size="small">{{ roleLabel }}</el-tag>
          <el-button type="danger" size="small" @click="handleLogout">退出</el-button>
        </div>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'

const route = useRoute()
const router = useRouter()
const store = useUserStore()

const roleLabel = computed(() => {
  const map = {
    core_management: '核心管理层',
    manager: '馆长',
    reception: '前台',
    coach: '教练',
    customer: '顾客',
  }
  return map[store.user?.role] || store.user?.role || ''
})

function handleLogout() {
  store.logout()
  router.push('/login')
}
</script>

<style scoped>
.layout { height: 100vh; }
.aside { background: #304156; overflow-y: auto; }
.logo { color: #fff; text-align: center; padding: 16px; font-size: 18px; font-weight: bold; border-bottom: 1px solid #4a5e77; }
.logo i { margin-right: 6px; }
.header { background: #fff; border-bottom: 1px solid #e6e6e6; display: flex; align-items: center; justify-content: space-between; padding: 0 20px; height: 50px; }
.header-right { display: flex; align-items: center; gap: 10px; }
:deep(.el-menu-item i) { margin-right: 8px; vertical-align: middle; }
</style>
