<template>
  <view class="page">
    <view class="glass info-card">
      <view class="info-row">
        <text class="info-label">{{ fieldName }}</text>
        <text class="info-price">¥{{ fieldPrice }}<text class="info-unit">/小时</text></text>
      </view>
    </view>

    <view class="date-section">
      <view class="glass date-nav">
        <view class="date-arrow" @tap="prevDay"><text>‹</text></view>
        <picker mode="date" :value="bookDate" :start="todayStr" @change="onDateChange">
          <text class="date-text">{{ bookDate }}</text>
        </picker>
        <view class="date-arrow" @tap="nextDay"><text>›</text></view>
      </view>
      <view class="glass date-today" @tap="goToday"><text>今天</text></view>
    </view>

    <view class="slots-section">
      <view class="slot-grid">
        <view
          v-for="s in slots" :key="s.time"
          class="glass slot-item"
          :class="{
            'slot-booked': s.booked,
            'slot-expired': s.expired,
            'slot-selected': selectedSlot?.time === s.time && !s.booked && !s.expired,
            'slot-peak': s.is_peak && !s.booked && !s.expired,
          }"
          :data-time="s.time"
          @tap="selectSlot"
        >
          <text class="slot-time">{{ s.time }}</text>
          <text class="slot-price">¥{{ s.price }}</text>
          <text class="tag slot-status" :class="slotTagClass(s)">{{ slotLabel(s) }}</text>
        </view>
      </view>
      <view class="empty-state" v-if="slots.length === 0 && !loadingSlots">
        <text class="empty-text">该日期无可选时段</text>
      </view>
    </view>

    <view class="glass confirm-bar" v-if="selectedSlot && !selectedSlot.booked && !selectedSlot.expired">
      <view class="confirm-left">
        <text class="confirm-date">{{ bookDate }}</text>
        <text class="confirm-time">{{ selectedSlot.time }} - {{ selectedSlot.end_time }}</text>
      </view>
      <view class="confirm-right">
        <text class="confirm-price">¥{{ selectedSlot.price }}</text>
        <view class="btn btn-primary" @tap="handleSubmit">提交订单</view>
      </view>
    </view>

    <view class="modal-mask" v-if="showPayDialog" @tap="showPayDialog = false">
      <view class="glass modal-card" @tap.stop>
        <text class="modal-title">订单已创建</text>
        <view class="modal-body">
          <text class="modal-text">订单号：{{ createdOrderNo }}</text>
          <text class="modal-text modal-amount">¥{{ selectedSlot?.price }}</text>
        </view>
        <view class="btn btn-primary" style="margin-bottom:16rpx" @tap="handlePay">微信支付（模拟）</view>
        <text class="modal-link" @tap="showPayDialog = false; goOrders()">稍后支付</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { getAvailability, createOrder, updateOrderStatus } from '../../api'

let venueId = null, fieldId = null
const fieldName = ref(''), fieldPrice = ref(0), bookDate = ref('')
const slots = ref([]), selectedSlot = ref(null), loadingSlots = ref(false)
const showPayDialog = ref(false), createdOrderNo = ref(''), createdOrderId = ref(null)
const todayStr = new Date().toISOString().slice(0, 10)

function getToday() { return new Date().toISOString().slice(0, 10) }
function goToday() { bookDate.value = getToday(); loadSlots() }
function prevDay() {
  const d = new Date(bookDate.value); d.setDate(d.getDate() - 1)
  const ds = d.toISOString().slice(0, 10)
  if (ds < getToday()) return
  bookDate.value = ds; loadSlots()
}
function nextDay() {
  const d = new Date(bookDate.value); d.setDate(d.getDate() + 1)
  bookDate.value = d.toISOString().slice(0, 10); loadSlots()
}
function onDateChange(e) { bookDate.value = e.detail.value; loadSlots() }

async function loadSlots() { selectedSlot.value = null; loadingSlots.value = true
  try { const res = await getAvailability(fieldId, bookDate.value); slots.value = res.slots || [] } catch { /* */ }
  finally { loadingSlots.value = false }
}
function selectSlot(e) {
  const time = e.currentTarget.dataset.time
  const s = slots.value.find(s => s.time === time)
  if (!s || s.booked || s.expired) return
  selectedSlot.value = s
}

function slotLabel(s) { if (s.booked) return '已订'; if (s.expired) return '过期'; if (s.is_peak) return '高峰'; return '可订' }
function slotTagClass(s) { if (s.booked) return 'tag-red'; if (s.expired) return 'tag-gray'; if (s.is_peak) return 'tag-orange'; return 'tag-green' }

async function handleSubmit() {
  try {
    const res = await createOrder({ venue_id: venueId, field_id: fieldId, order_type: 'field_book', book_date: bookDate.value, start_time: selectedSlot.value.time, remark: '顾客自助订场' })
    createdOrderId.value = res.id; createdOrderNo.value = res.order_no; showPayDialog.value = true
  } catch { /* */ }
}
async function handlePay() {
  try { await new Promise(r => setTimeout(r, 800)); await updateOrderStatus(createdOrderId.value, 'paid')
    uni.showToast({ title: '支付成功', icon: 'success' }); showPayDialog.value = false; goOrders() } catch { /* */ }
}
function goOrders() { uni.switchTab({ url: '/pages/orders/orders' }) }

const pages = getCurrentPages(); const page = pages[pages.length - 1]
const options = page.$page?.options || page.options || {}
venueId = parseInt(options.venueId); fieldId = parseInt(options.fieldId)
fieldName.value = decodeURIComponent(options.fieldName || ''); fieldPrice.value = parseFloat(options.price || 0)
bookDate.value = getToday(); loadSlots()
</script>

<style scoped>
.info-card { padding: 28rpx; margin-bottom: 24rpx; }
.info-row { display: flex; justify-content: space-between; align-items: baseline; }
.info-label { font-size: 34rpx; font-weight: 700; color: #1D1D1F; }
.info-price { font-size: 40rpx; font-weight: 800; color: #E6A23C; }
.info-unit { font-size: 24rpx; font-weight: 400; }

.date-section { display: flex; align-items: center; justify-content: center; gap: 16rpx; margin-bottom: 28rpx; }
.date-nav { display: flex; align-items: center; gap: 8rpx; padding: 8rpx 12rpx; }
.date-arrow { width: 56rpx; height: 56rpx; display: flex; align-items: center; justify-content: center; font-size: 40rpx; color: #1D1D1F; font-weight: 300; }
.date-text { font-size: 30rpx; font-weight: 700; color: #1D1D1F; padding: 0 16rpx; }
.date-today { padding: 14rpx 28rpx; font-size: 26rpx; color: #409EFF; font-weight: 600; }

.slot-grid { display: flex; flex-wrap: wrap; gap: 12rpx; }
.slot-item { width: calc(25% - 9rpx); padding: 18rpx 8rpx; text-align: center; box-sizing: border-box; }
.slot-selected { border-color: #409EFF !important; background: rgba(64,158,255,0.08) !important; }
.slot-booked { opacity: 0.45; background: rgba(0,0,0,0.02) !important; }
.slot-expired { opacity: 0.35; }
.slot-peak { border-color: rgba(230,162,60,0.25) !important; }
.slot-time { display: block; font-size: 24rpx; font-weight: 700; color: #1D1D1F; margin-bottom: 4rpx; }
.slot-price { display: block; font-size: 22rpx; color: #E6A23C; margin-bottom: 8rpx; }
.slot-status { font-size: 18rpx !important; }

.confirm-bar { position: fixed; bottom: 0; left: 0; right: 0; display: flex; align-items: center; justify-content: space-between; padding: 24rpx 32rpx; padding-bottom: calc(24rpx + env(safe-area-inset-bottom)); z-index: 100; border-radius: 32rpx 32rpx 0 0; }
.confirm-left { display: flex; flex-direction: column; }
.confirm-date { font-size: 24rpx; color: #86868B; }
.confirm-time { font-size: 28rpx; font-weight: 600; color: #1D1D1F; }
.confirm-right { display: flex; align-items: center; gap: 16rpx; }
.confirm-price { font-size: 36rpx; font-weight: 800; color: #E6A23C; }

.modal-mask { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.35); display: flex; align-items: center; justify-content: center; z-index: 200; -webkit-backdrop-filter: blur(4px); backdrop-filter: blur(4px); }
.modal-card { width: 600rpx; padding: 44rpx 36rpx; text-align: center; }
.modal-title { font-size: 34rpx; font-weight: 700; color: #1D1D1F; display: block; margin-bottom: 24rpx; }
.modal-body { margin-bottom: 32rpx; }
.modal-text { display: block; font-size: 28rpx; color: #86868B; margin-bottom: 8rpx; }
.modal-amount { font-size: 48rpx; font-weight: 800; color: #E6A23C; margin-top: 8rpx; }
.modal-link { font-size: 26rpx; color: #86868B; }
</style>
