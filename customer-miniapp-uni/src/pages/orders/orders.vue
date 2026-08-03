<template>
  <view class="page">
    <view class="order-list" v-if="orders.length > 0">
      <view class="glass order-card" v-for="o in orders" :key="o.id">
        <view class="order-hd">
          <text class="order-no">{{ o.order_no }}</text>
          <text class="tag" :class="statusTag(o.status)">{{ statusLabel(o.status) }}</text>
        </view>
        <view class="order-bd">
          <view class="or">
            <text class="ol">类型</text>
            <text class="ov tag-sm" :class="'ot-' + o.order_type">{{ typeLabel(o.order_type) }}</text>
          </view>
          <view class="or"><text class="ol">球馆</text><text class="ov">{{ o.venue_name || '-' }}</text></view>
          <view class="or"><text class="ol">场地</text><text class="ov">{{ o.field_name || '-' }}</text></view>
          <view class="or" v-if="o.book_date"><text class="ol">日期</text><text class="ov">{{ o.book_date }}</text></view>
          <view class="or" v-if="o.start_time"><text class="ol">时段</text><text class="ov">{{ o.start_time }} - {{ o.end_time }}</text></view>
          <view class="or"><text class="ol">金额</text><text class="ov oa">¥{{ (o.paid_amount || o.original_amount || 0).toFixed(2) }}</text></view>
        </view>
        <view class="order-ft" v-if="o.order_type === 'field_book' && (o.status === 'pending' || o.status === 'paid')">
          <view class="btn btn-glass" v-if="o.status === 'pending'" @tap="doPay(o)">支付</view>
          <view class="btn btn-glass" style="color:#F56C6C;border-color:rgba(245,108,108,0.2)" @tap="doCancel(o)">取消</view>
        </view>
      </view>
    </view>
    <view class="empty-state" v-if="!loading && orders.length === 0">
      <text class="empty-icon">📋</text>
      <text class="empty-text">暂无订单</text>
      <text class="empty-sub">去首页预订场地吧</text>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow, onHide } from '@dcloudio/uni-app'
import { getOrders, updateOrderStatus } from '../../api'

const orders = ref([]), loading = ref(false)
let timer = null

const typeMap = { field_book: '订场', walk_in: '散客', card_recharge: '办卡', course_book: '课程' }
const statusMap = { pending: '待支付', paid: '已支付', confirmed: '已确认', checked_in: '已签到', cancelled: '已取消', refunded: '已退款' }
function typeLabel(t) { return typeMap[t] || t }
function statusLabel(s) { return statusMap[s] || s }
function statusTag(s) { const m = { pending: 'tag-orange', paid: 'tag-green', confirmed: 'tag-blue', checked_in: 'tag-green', cancelled: 'tag-gray', refunded: 'tag-gray' }; return m[s] || 'tag-gray' }

async function loadOrders() { try { const res = await getOrders(); orders.value = res.orders || [] } catch { /* */ } }
async function doPay(row) { try { await updateOrderStatus(row.id, 'paid'); uni.showToast({ title: '支付成功', icon: 'success' }); loadOrders() } catch { /* */ } }
async function doCancel(row) {
  const res = await new Promise(r => { uni.showModal({ title: '提示', content: '确定取消该订单？', success: r }) })
  if (!res.confirm) return
  try { await updateOrderStatus(row.id, 'cancelled'); uni.showToast({ title: '已取消', icon: 'success' }); loadOrders() } catch { /* */ }
}

onShow(() => {
  const token = uni.getStorageSync('token')
  if (!token) { uni.reLaunch({ url: '/pages/login/login' }); return }
  loading.value = true; loadOrders().finally(() => { loading.value = false })
  timer = setInterval(loadOrders, 5000)
})
onHide(() => { if (timer) clearInterval(timer) })
</script>

<style scoped>
.order-card { padding: 28rpx; margin-bottom: 20rpx; }
.order-hd { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20rpx; padding-bottom: 16rpx; border-bottom: 1rpx solid rgba(0,0,0,0.04); }
.order-no { font-size: 22rpx; color: #A1A1A6; font-family: 'SF Mono', monospace; }
.order-bd { margin-bottom: 4rpx; }
.or { display: flex; align-items: center; margin-bottom: 10rpx; }
.ol { width: 80rpx; font-size: 24rpx; color: #86868B; }
.ov { font-size: 26rpx; color: #1D1D1F; }
.oa { font-size: 28rpx; font-weight: 700; color: #E6A23C; }
.tag-sm { font-size: 18rpx; padding: 2rpx 10rpx; border-radius: 6rpx; display: inline-block; }
.ot-field_book { background: rgba(64,158,255,0.1); color: #2B7DE9; }
.ot-card_recharge { background: rgba(230,162,60,0.1); color: #C7851F; }
.ot-walk_in { background: rgba(0,0,0,0.05); color: #86868B; }
.order-ft { display: flex; gap: 16rpx; justify-content: flex-end; margin-top: 16rpx; padding-top: 16rpx; border-top: 1rpx solid rgba(0,0,0,0.04); }
</style>
