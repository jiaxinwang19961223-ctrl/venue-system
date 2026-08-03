<template>
  <view class="page">
    <!-- 日期选择 -->
    <view class="glass date-bar flex-between">
      <view class="btn btn-glass btn-sm" @tap="changeDate(-1)">‹ 前一天</view>
      <picker mode="date" :value="displayDate" @change="onPickDate">
        <view class="flex-center">
          <text style="font-size:30rpx;font-weight:600">{{ displayDate }}</text>
          <text style="font-size:20rpx;color:#86868B;margin-left:4rpx">📅</text>
        </view>
      </picker>
      <view class="btn btn-glass btn-sm" @tap="changeDate(1)">后一天 ›</view>
    </view>

    <!-- 图例 -->
    <view class="legend">
      <text class="legend-item"><view class="dot dot-free"></view>空闲</text>
      <text class="legend-item"><view class="dot dot-booked"></view>已订</text>
      <text class="legend-item"><view class="dot dot-playing"></view>进行中</text>
    </view>

    <!-- 场地 × 时段 网格 -->
    <view v-if="!loading" style="margin-top:16rpx">
      <view v-for="venue in venueBoards" :key="venue.id" style="margin-bottom:32rpx">
        <view class="venue-title-row">
          <image class="pin-icon" src="/static/icons/pin-blue.svg" mode="aspectFit" />
          <text class="section-title" style="margin:0">{{ venue.name }}</text>
        </view>
        <view class="glass board-card" v-for="field in venue.fields" :key="field.id" style="margin-bottom:16rpx">
          <view class="flex-between" style="margin-bottom:12rpx">
            <text style="font-size:28rpx;font-weight:600">{{ field.name }}</text>
            <text class="text-muted" style="font-size:22rpx">¥{{ field.price_per_hour }}/h</text>
          </view>
          <view class="timeline-row">
            <view class="timeline-slot" v-for="s in field.slots" :key="s.time"
              :class="{
                'slot-free': !s.booked,
                'slot-booked': s.booked && !s.playing,
                'slot-playing': s.booked && s.playing,
                'slot-past': s.past,
              }"
              @tap="s.booked ? goOrder(s.orderId) : quickBook(field, s)">
              <text class="slot-hour">{{ s.time }}</text>
              <text class="slot-status" v-if="s.booked && s.memberName" style="font-size:16rpx">{{ s.memberName.slice(0,2) }}</text>
              <text class="slot-status" v-else-if="s.booked">已订</text>
              <text class="slot-status" v-else-if="s.past">—</text>
            </view>
          </view>
        </view>
      </view>
    </view>

    <view class="empty-state" v-if="!loading && venueBoards.length === 0">
      <image class="empty-icon" src="/static/icons/clipboard.svg" mode="aspectFit" />
      <text class="empty-text">暂无场地数据</text>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { getVenues, getFields, getOrders } from '../../api'
import { useUserStore } from '../../store/user'

const store = useUserStore()
const currentDate = ref(new Date())
const loading = ref(true)
const venueBoards = ref([])

const displayDate = ref('')

function formatDate(d) {
  const y = d.getFullYear()
  const m = (d.getMonth() + 1).toString().padStart(2, '0')
  const day = d.getDate().toString().padStart(2, '0')
  return `${y}-${m}-${day}`
}

function changeDate(delta) {
  const d = new Date(currentDate.value)
  d.setDate(d.getDate() + delta)
  currentDate.value = d
  loadBoard()
}

function onPickDate(e) {
  const d = new Date(e.detail.value)
  currentDate.value = d
  loadBoard()
}

async function loadBoard() {
  loading.value = true
  displayDate.value = formatDate(currentDate.value)

  try {
    const vRes = await getVenues()
    const venues = vRes.venues || []
    const dateStr = displayDate.value
    const now = new Date()
    const currentHour = now.getHours()
    const isToday = dateStr === formatDate(now)

    // 获取今日所有订单
    const oRes = await getOrders({ date: dateStr })
    const orders = oRes.orders || []

    const boards = []
    for (const v of venues) {
      const fRes = await getFields(v.id)
      const fields = fRes.fields || []

      const fieldData = []
      for (const f of fields) {
        // 优先用 API 获取时段，失败则用默认生成
        let slots = []
        try {
          const aRes = await getAvailability(f.id, dateStr)
          if (aRes.slots && aRes.slots.length) {
            slots = aRes.slots.map(s => ({
              ...s,
              playing: false,
              past: s.expired,
              orderId: null,
              memberName: null,
            }))
            // 补充订单信息
            for (const s of slots) {
              if (s.booked) {
                const order = orders.find(o =>
                  o.field_id === f.id &&
                  o.start_time && o.end_time &&
                  o.start_time <= s.time && o.end_time > s.time
                )
                if (order) {
                  s.playing = order.status === 'checked_in' || order.status === 'confirmed'
                  s.orderId = order.id
                  s.memberName = order.name
                }
              }
            }
          } else {
            slots = generateSlots(orders, f, dateStr, isToday, currentHour)
          }
        } catch {
          slots = generateSlots(orders, f, dateStr, isToday, currentHour)
        }
        fieldData.push({ ...f, slots })
      }
      boards.push({ ...v, fields: fieldData })
    }
    venueBoards.value = boards
  } catch { /* */ }
  finally { loading.value = false }
}

function generateSlots(orders, field, dateStr, isToday, currentHour) {
  const slots = []
  for (let h = 9; h < 22; h++) {
    const time = `${h.toString().padStart(2, '0')}:00`
    const endTime = `${(h + 1).toString().padStart(2, '0')}:00`

    // 找该时段是否有订单
    const order = orders.find(o =>
      o.field_id === field.id &&
      o.start_time && o.end_time &&
      o.start_time <= time && o.end_time > time
    )

    const isPast = isToday && h <= currentHour

    slots.push({
      time,
      booked: !!order,
      playing: order && (order.status === 'checked_in' || order.status === 'confirmed'),
      past: isPast,
      orderId: order?.id,
      memberName: order?.name,
      status: order?.status,
    })
  }
  return slots
}

function goOrder(id) {
  if (id) uni.navigateTo({ url: `/pages/order-detail/order-detail?id=${id}` })
}

function quickBook(field, slot) {
  uni.navigateTo({ url: `/pages/order/order?field=${field.id}&date=${displayDate.value}&time=${slot.time}` })
}

onShow(() => {
  if (!store.isLoggedIn) { uni.reLaunch({ url: '/pages/login/login' }); return }
  loadBoard()
})
</script>

<style scoped>
.venue-title-row { display: flex; align-items: center; gap: 8rpx; margin-bottom: 16rpx; }
.pin-icon { width: 36rpx; height: 36rpx; }
.date-bar { padding: 16rpx 24rpx; margin-bottom: 20rpx; }

.legend { display: flex; gap: 24rpx; padding: 0 8rpx; margin-bottom: 4rpx; }
.legend-item { display: flex; align-items: center; font-size: 22rpx; color: #86868B; gap: 6rpx; }
.dot { width: 16rpx; height: 16rpx; border-radius: 4rpx; }
.dot-free { background: #E8F5E9; border: 1rpx solid #A5D6A7; }
.dot-booked { background: #E3F2FD; border: 1rpx solid #90CAF9; }
.dot-playing { background: #FFF3E0; border: 1rpx solid #FFCC80; }

.board-card { padding: 20rpx; }

.timeline-row { display: flex; gap: 4rpx; overflow-x: auto; }
.timeline-slot {
  flex-shrink: 0; width: 62rpx; padding: 8rpx 0;
  text-align: center; border-radius: 8rpx;
  transition: all 0.2s;
}
.slot-free { background: rgba(103,194,58,0.08); }
.slot-booked { background: rgba(64,158,255,0.1); }
.slot-playing { background: rgba(230,162,60,0.12); }
.slot-past { background: rgba(0,0,0,0.02); opacity: 0.5; }
.slot-hour { font-size: 20rpx; color: #86868B; display: block; }
.slot-status { font-size: 18rpx; color: #A1A1A6; display: block; }
</style>
