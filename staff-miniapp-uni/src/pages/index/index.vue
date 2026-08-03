<template>
  <view class="page">
    <!-- 统计卡片 -->
    <view class="stats-row">
      <view class="glass stat-card" v-for="item in statCards" :key="item.key">
        <text class="stat-value">{{ item.value }}</text>
        <text class="stat-label">{{ item.label }}</text>
      </view>
    </view>

    <!-- 场地占用率 -->
    <view class="glass section-card">
      <view class="flex-between">
        <text class="section-title" style="margin:0">场地占用</text>
        <text class="text-muted" style="font-size:24rpx">{{ stats.total_fields }}片场地</text>
      </view>
      <view class="progress-bar">
        <view class="progress-fill" :style="{ width: stats.occupancy + '%' }"></view>
      </view>
      <text class="text-muted" style="font-size:24rpx">{{ stats.occupancy }}% 已预订</text>
    </view>

    <!-- 今日营收明细 -->
    <view class="glass section-card" v-if="stats.paid_total > 0 || stats.walk_in_total > 0">
      <view class="flex-between" style="margin-bottom:16rpx">
        <text class="revenue-item">场地预订 <text class="revenue-amount">¥{{ stats.paid_total.toFixed(2) }}</text></text>
        <text class="revenue-item">散客消费 <text class="revenue-amount">¥{{ stats.walk_in_total.toFixed(2) }}</text></text>
      </view>
    </view>

    <!-- 最近订单 -->
    <text class="section-title">最近订单</text>
    <view class="glass order-card" v-for="o in recentOrders" :key="o.id"
      @tap="goOrder(o.id)">
      <view class="flex-between">
        <view>
          <text class="order-no">#{{ o.order_no.slice(-8) }}</text>
          <text class="order-type tag" :class="orderTypeTag(o.order_type)">{{ orderTypeLabel(o.order_type) }}</text>
        </view>
        <text class="tag" :class="statusTag(o.status)">{{ statusLabel(o.status) }}</text>
      </view>
      <view class="flex-between" style="margin-top:12rpx">
        <text class="text-muted" style="font-size:24rpx">
          {{ o.field_name || '无场地' }}  {{ o.member_name || '散客' }}
        </text>
        <text style="font-size:28rpx;font-weight:600;color:#1D1D1F">¥{{ o.paid_amount }}</text>
      </view>
      <text class="text-muted" style="font-size:22rpx;margin-top:4rpx;display:block">
        {{ o.start_time }} - {{ o.end_time }}  ·  {{ formatTime(o.created_at) }}
      </text>
    </view>
    <view class="empty-state" v-if="!loading && recentOrders.length === 0">
      <image class="empty-icon" src="/static/icons/clipboard.svg" mode="aspectFit" />
      <text class="empty-text">今日暂无订单</text>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { getTodayDashboard, getOrders } from '../../api'
import { useUserStore } from '../../store/user'

const store = useUserStore()
const loading = ref(true)
const stats = ref({ order_count: 0, paid_total: 0, field_book_count: 0, walk_in_total: 0, occupancy: 0, active_members: 0, total_fields: 0 })
const recentOrders = ref([])

const statCards = computed(() => [
  { key: 'orders', value: stats.value.order_count, label: '今日订单' },
  { key: 'revenue', value: '¥' + stats.value.paid_total.toFixed(0), label: '营收' },
  { key: 'fields', value: stats.value.field_book_count, label: '场地预订' },
  { key: 'members', value: stats.value.active_members, label: '活跃会员' },
])

async function load() {
  loading.value = true
  try {
    const res = await getTodayDashboard(store.venueId)
    stats.value = res.stats
    recentOrders.value = res.recent_orders || []
  } catch {
    // fallback: 用订单列表
    try {
      const r = await getOrders({})
      recentOrders.value = (r.orders || []).slice(0, 10)
    } catch { /* */ }
  } finally {
    loading.value = false
  }
}

function goOrder(id) { uni.navigateTo({ url: `/pages/order-detail/order-detail?id=${id}` }) }

function orderTypeLabel(t) {
  const m = { field_book: '订场', walk_in: '散客', card_recharge: '办卡', course_book: '课程' }
  return m[t] || t
}
function orderTypeTag(t) {
  const m = { field_book: 'tag-blue', walk_in: 'tag-orange', card_recharge: 'tag-green', course_book: 'tag-blue' }
  return m[t] || 'tag-gray'
}
function statusLabel(s) {
  const m = { pending: '待付', paid: '已付', confirmed: '已确认', checked_in: '已签到', cancelled: '取消', refunded: '退款' }
  return m[s] || s
}
function statusTag(s) {
  const m = { pending: 'tag-orange', paid: 'tag-blue', confirmed: 'tag-green', checked_in: 'tag-green', cancelled: 'tag-gray', refunded: 'tag-red' }
  return m[s] || 'tag-gray'
}
function formatTime(t) {
  if (!t) return ''
  const d = new Date(t.replace(' ', 'T'))
  const h = d.getHours().toString().padStart(2, '0')
  const m = d.getMinutes().toString().padStart(2, '0')
  return `${h}:${m}`
}

onShow(() => {
  if (!store.isLoggedIn) { uni.reLaunch({ url: '/pages/login/login' }); return }
  load()
})
</script>

<style scoped>
.stats-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16rpx; margin-bottom: 24rpx; }
.stat-card { padding: 28rpx 24rpx; text-align: center; }
.stat-value { display: block; font-size: 48rpx; font-weight: 700; color: #1D1D1F; }
.stat-label { display: block; font-size: 24rpx; color: #86868B; margin-top: 8rpx; }
.section-card { padding: 24rpx; margin-bottom: 24rpx; }
.progress-bar {
  height: 12rpx; background: rgba(0,0,0,0.06); border-radius: 6rpx;
  margin: 16rpx 0 8rpx; overflow: hidden;
}
.progress-fill {
  height: 100%; background: var(--color-primary);
  border-radius: 6rpx; transition: width 0.6s;
}
.revenue-item { font-size: 24rpx; color: #86868B; }
.revenue-amount { font-weight: 700; color: #1D1D1F; font-size: 28rpx; }
.order-card { padding: 24rpx; margin-bottom: 16rpx; }
.order-no { font-size: 24rpx; color: #86868B; margin-right: 12rpx; }
.order-type { margin-right: 8rpx; }
</style>
