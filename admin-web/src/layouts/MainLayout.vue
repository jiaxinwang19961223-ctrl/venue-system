<template>
  <el-container class="layout">
    <el-aside width="220px" class="aside">
      <div class="logo"><i class="ri-store-2-fill"></i> 万创运维</div>
      <el-menu
        :default-active="route.path"
        router
        background-color="transparent"
        text-color="rgba(255,255,255,0.7)"
        active-text-color="#fff"
      >
        <el-menu-item index="/dashboard"><i class="ri-dashboard-line ri-lg"></i><span>首页</span></el-menu-item>
        <el-menu-item index="/settings"><i class="ri-building-2-line ri-lg"></i><span>场馆设置</span></el-menu-item>
        <el-menu-item index="/training"><i class="ri-team-line ri-lg"></i><span>训练营</span></el-menu-item>
        <el-menu-item index="/face-checkin"><i class="ri-camera-line ri-lg"></i><span>人脸签到</span></el-menu-item>
        <el-menu-item index="/court-board"><i class="ri-grid-line ri-lg"></i><span>包场看板</span></el-menu-item>
        <el-menu-item index="/orders"><i class="ri-bill-line ri-lg"></i><span>订单管理</span></el-menu-item>
        <el-menu-item index="/members"><i class="ri-vip-crown-line ri-lg"></i><span>会员管理</span></el-menu-item>
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
          <el-button size="small" @click="handleLogout">退出</el-button>
        </div>
      </el-header>
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, onMounted } from 'vue'
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
  router.replace({ path: route.path, query: { ...route.query, _t: Date.now() } })
}

function handleLogout() { store.logout(); router.push('/login') }

onMounted(() => { venueStore.load() })
</script>

<style scoped>
.layout { height: 100vh; }

/* ── 侧边栏：深色玻璃 ── */
.aside {
  background: rgba(30,30,32,0.85) !important;
  -webkit-backdrop-filter: blur(40px) saturate(180%);
  backdrop-filter: blur(40px) saturate(180%);
  border-right: 1px solid rgba(255,255,255,0.08);
}
.logo { color: #fff; text-align: center; padding: 20px 16px; font-size: 23px; font-weight: 900; font-style: italic; letter-spacing: 1.5px; }
.logo i { margin-right: 6px; color: var(--color-primary, #007AFF); }

:deep(.el-menu) { border-right: none !important; }
:deep(.el-menu-item) { margin: 2px 8px; border-radius: 8px; height: 46px; line-height: 46px; font-size: 17px; font-weight: 700; letter-spacing: 2px; }
:deep(.el-menu-item:hover) { background: rgba(255,255,255,0.08) !important; }
:deep(.el-menu-item.is-active) { background: rgba(255,255,255,0.12) !important; color: #fff !important; }

/* ── 顶栏：透明玻璃 ── */
.header {
  background: rgba(255,255,255,0.6);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  backdrop-filter: blur(20px) saturate(180%);
  border-bottom: 1px solid rgba(0,0,0,0.06);
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 24px; height: 52px;
}
.header-left { display: flex; align-items: center; }
.page-title { font-weight: 700; font-size: 16px; color: var(--text-primary, #1D1D1F); }
.header-right { display: flex; align-items: center; gap: 10px; }
.user-name { font-size: 13px; color: var(--text-secondary, #6E6E73); }

/* ── 内容区 ── */
.main-content { background: #F0F0F2; padding: 24px; }
</style>
