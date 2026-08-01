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
        <el-menu-item index="/face-checkin">
          <i class="ri-camera-line ri-lg"></i>
          <span>人脸签到</span>
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
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <span class="page-title">{{ route.meta.title || '' }}</span>
          <el-select
            v-if="venueStore.venues.length > 1"
            :model-value="venueStore.currentId"
            @change="onVenueChange"
            size="small"
            style="width:180px;margin-left:16px"
          >
            <el-option v-for="v in venueStore.venues" :key="v.id" :label="v.name" :value="v.id" />
          </el-select>
        </div>
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
import { computed, onMounted, provide } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { useVenueStore } from '../stores/venue'

const route = useRoute()
const router = useRouter()
const store = useUserStore()
const venueStore = useVenueStore()

const roleLabel = computed(() => {
  const map = { core_management: '核心管理层', manager: '馆长', reception: '前台', coach: '教练', customer: '顾客' }
  return map[store.user?.role] || store.user?.role || ''
})

function onVenueChange(id) {
  const v = venueStore.venues.find(v => v.id === id)
  venueStore.setCurrent(id, v?.name || '')
  // 刷新当前页面
  router.replace({ path: route.path, query: { ...route.query, _t: Date.now() } })
}

function handleLogout() {
  store.logout()
  router.push('/login')
}

onMounted(() => { venueStore.load() })
</script>

<style scoped>
.layout { height: 100vh; }
.aside { background: #304156; overflow-y: auto; }
.logo { color: #fff; text-align: center; padding: 16px; font-size: 18px; font-weight: bold; border-bottom: 1px solid #4a5e77; }
.logo i { margin-right: 6px; }
.header { background: #fff; border-bottom: 1px solid #e6e6e6; display: flex; align-items: center; justify-content: space-between; padding: 0 20px; height: 50px; }
.header-left { display: flex; align-items: center; }
.page-title { font-weight: 600; }
.header-right { display: flex; align-items: center; gap: 10px; }
:deep(.el-menu-item i) { margin-right: 8px; vertical-align: middle; }
</style>
