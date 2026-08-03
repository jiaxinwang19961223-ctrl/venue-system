<template>
  <view class="page">
    <!-- 员工信息卡片 -->
    <view class="glass profile-card">
      <image class="avatar" src="/static/icons/user.svg" mode="aspectFit" />
      <text class="profile-name">{{ store.userName }}</text>
      <view class="profile-meta">
        <text class="tag tag-blue">{{ store.userRoleLabel }}</text>
        <text class="text-muted" style="font-size:24rpx;margin-left:12rpx">{{ user.phone || '' }}</text>
      </view>
      <text class="text-muted" style="font-size:24rpx;display:block;margin-top:8rpx">
        所属球馆: {{ venueName || '总部' }}
      </text>
    </view>

    <!-- 角色权限说明 -->
    <text class="section-title">功能权限</text>
    <view class="glass permission-list">
      <view class="perm-item" v-for="p in permissions" :key="p.key">
        <text class="perm-label">{{ p.label }}</text>
        <text :style="{ color: p.has ? 'var(--color-success)' : '#C7C7CC', fontSize: '28rpx' }">
          {{ p.has ? '✅' : '—' }}
        </text>
      </view>
    </view>

    <!-- 快捷入口 -->
    <text class="section-title">快捷入口</text>
    <view class="quick-row">
      <view class="glass quick-btn" @tap="goFieldBoard">
        <text class="quick-icon-text">📋</text>
        <text>场地看板</text>
      </view>
      <view class="glass quick-btn" v-if="canCheckIn" @tap="goCheckIn">
        <text class="quick-icon-text">✅</text>
        <text>课程签到</text>
      </view>
    </view>

    <!-- 退出 -->
    <view class="btn btn-danger" style="margin-top:40rpx" @tap="handleLogout">退出登录</view>
    <text class="version-text">场馆运营系统 v0.1.0 · 员工端</text>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useUserStore } from '../../store/user'
import { getVenues } from '../../api'

const store = useUserStore()
const user = computed(() => store.user || {})
const venueName = ref('')

const canCheckIn = computed(() => store.canCheckIn)

const permissions = computed(() => [
  { key: 'all_venues', label: '全部球馆数据', has: user.value.role === 'core_management' },
  { key: 'view_revenue', label: '查看营收', has: ['core_management', 'manager'].includes(user.value.role) },
  { key: 'manage_fields', label: '场地管理', has: ['core_management', 'manager'].includes(user.value.role) },
  { key: 'quick_order', label: '快速开单', has: store.canOrder },
  { key: 'check_in', label: '课程签到', has: canCheckIn.value },
  { key: 'member_query', label: '会员查询', has: ['core_management', 'manager', 'reception'].includes(user.value.role) },
  { key: 'member_edit', label: '会员编辑', has: ['core_management', 'manager'].includes(user.value.role) },
  { key: 'refund', label: '订单退款', has: ['core_management', 'manager'].includes(user.value.role) },
])

async function loadVenueName() {
  if (!store.venueId) return
  try {
    const res = await getVenues()
    const v = (res.venues || []).find(v => v.id === store.venueId)
    if (v) venueName.value = v.name
  } catch { /* */ }
}

function goFieldBoard() { uni.navigateTo({ url: '/pages/field-board/field-board' }) }
function goCheckIn() {
  uni.showToast({ title: '请前往会员详情页签到', icon: 'none' })
}

function handleLogout() {
  uni.showModal({
    title: '退出登录',
    content: '确定退出当前账号？',
    success(res) {
      if (res.confirm) {
        store.logout()
        uni.reLaunch({ url: '/pages/login/login' })
      }
    },
  })
}

onShow(() => {
  if (!store.isLoggedIn) { uni.reLaunch({ url: '/pages/login/login' }); return }
  loadVenueName()
})
</script>

<style scoped>
.profile-card { padding: 36rpx; text-align: center; margin-bottom: 24rpx; }
.avatar { width: 88rpx; height: 88rpx; margin: 0 auto 12rpx; display: block; opacity: 0.4; }
.profile-name { font-size: 38rpx; font-weight: 700; color: #1D1D1F; display: block; }
.profile-meta { display: flex; align-items: center; justify-content: center; margin-top: 12rpx; }

.permission-list { padding: 24rpx; margin-bottom: 24rpx; }
.perm-item { display: flex; justify-content: space-between; align-items: center; padding: 16rpx 0; }
.perm-item + .perm-item { border-top: 1rpx solid rgba(0,0,0,0.04); }
.perm-label { font-size: 28rpx; color: #1D1D1F; }

.quick-row { display: flex; gap: 16rpx; }
.quick-btn {
  flex: 1; padding: 28rpx; text-align: center;
  font-size: 26rpx; color: #1D1D1F;
}
.quick-icon-text { font-size: 40rpx; display: block; margin-bottom: 8rpx; }

.version-text { display: block; text-align: center; font-size: 22rpx; color: #C7C7CC; margin-top: 24rpx; }
</style>
