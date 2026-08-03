<template>
  <el-container>
    <el-header class="customer-header">
      <div class="header-left">
        <h2 class="logo" @click="$router.push('/home')">
          <i class="ri-store-2-fill"></i> 场馆订场
        </h2>
        <el-menu
          mode="horizontal"
          router
          :default-active="route.path"
          class="header-menu"
          background-color="transparent"
        >
          <el-menu-item index="/home">首页</el-menu-item>
          <el-menu-item index="/orders">我的订单</el-menu-item>
          <el-menu-item index="/member">会员中心</el-menu-item>
        </el-menu>
      </div>
      <div class="header-right">
        <template v-if="store.user">
          <span class="user-name">{{ store.user.name }}</span>
          <el-tag size="small" type="info">顾客</el-tag>
          <el-button text size="small" @click="handleLogout">退出</el-button>
        </template>
      </div>
    </el-header>
    <el-main class="customer-main">
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { useVenueStore } from '../stores/venue'
import { onMounted } from 'vue'

const route = useRoute()
const router = useRouter()
const store = useUserStore()
const venueStore = useVenueStore()

onMounted(() => {
  venueStore.load()
})

function handleLogout() {
  store.logout()
  router.push('/login')
}
</script>

<style scoped>
.customer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid #e6e6e6;
  padding: 0 24px;
  height: 56px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 32px;
}

.logo {
  margin: 0;
  font-size: 18px;
  color: #409EFF;
  cursor: pointer;
  white-space: nowrap;
}

.header-menu {
  border-bottom: none !important;
}

.header-menu .el-menu-item {
  height: 56px;
  line-height: 56px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-name {
  font-size: 14px;
  color: #303133;
}

.customer-main {
  max-width: 1100px;
  margin: 0 auto;
  padding: 24px 16px;
  min-height: calc(100vh - 56px);
  background: #f5f7fa;
}
</style>
