<template>
  <view class="page">
    <!-- 订单类型 Tab -->
    <view class="type-tabs">
      <view class="type-tab" :class="{ active: orderType === 'field' }" @tap="orderType = 'field'">场地预订</view>
      <view class="type-tab" :class="{ active: orderType === 'walk' }" @tap="orderType = 'walk'">散客消费</view>
    </view>

    <!-- 场地预订表单 -->
    <view v-if="orderType === 'field'" class="form-section">
      <view class="glass form-card">
        <text class="form-label">选择球馆</text>
        <picker mode="selector" :range="venueNames" @change="onVenueChange">
          <view class="picker-input">{{ venueNames[venueIndex] || '请选择球馆' }}</view>
        </picker>
      </view>

      <view class="glass form-card" v-if="venueIndex >= 0">
        <text class="form-label">选择场地</text>
        <picker mode="selector" :range="fieldNames" @change="onFieldChange">
          <view class="picker-input">{{ fieldNames[fieldIndex] || '请选择场地' }}</view>
        </picker>
      </view>

      <view class="glass form-card" v-if="fieldIndex >= 0">
        <text class="form-label">预订日期</text>
        <picker mode="date" :value="bookDate" :start="today" @change="onDateChange">
          <view class="picker-input">{{ bookDate || '选择日期' }}</view>
        </picker>
      </view>

      <view class="glass form-card" v-if="bookDate">
        <text class="form-label">选择时段</text>
        <view class="slot-grid" v-if="slots.length">
          <view class="slot-item" v-for="s in slots" :key="s.time"
            :class="{ 'slot-booked': s.booked, 'slot-expired': s.expired, 'slot-selected': s.time === selectedSlot }"
            @tap="selectSlot(s)">
            <text class="slot-time">{{ s.time }}</text>
            <text class="slot-price">¥{{ s.price }}</text>
            <text class="slot-badge" v-if="s.booked">已订</text>
            <text class="slot-badge" v-else-if="s.expired">过期</text>
          </view>
        </view>
        <view v-else-if="loadingSlots" class="text-center" style="padding:40rpx">
          <text class="text-muted">加载时段中...</text>
        </view>
        <view v-else class="text-center" style="padding:40rpx">
          <text class="text-muted">请先选择场地和日期</text>
        </view>
      </view>

      <!-- 会员（可选） -->
      <view class="glass form-card">
        <text class="form-label">关联会员（可选）</text>
        <input class="input-glass" v-model="memberSearch" placeholder="输入会员姓名/手机号搜索" @confirm="searchMember" />
        <view class="member-result" v-if="foundMember" style="margin-top:16rpx">
          <text>{{ foundMember.name }} · {{ foundMember.phone }}</text>
          <text class="tag tag-blue" style="margin-left:12rpx">余额 ¥{{ foundMember.balance }}</text>
          <text style="color:var(--color-danger);margin-left:12rpx;font-size:22rpx" @tap="foundMember = null">清除</text>
        </view>
      </view>

      <!-- 金额 -->
      <view class="glass form-card">
        <text class="form-label">金额</text>
        <view class="flex-between">
          <text style="font-size:40rpx;font-weight:700">¥{{ orderAmount }}</text>
          <view class="btn btn-primary btn-sm" @tap="submitOrder">确认开单</view>
        </view>
      </view>
    </view>

    <!-- 散客消费表单 -->
    <view v-if="orderType === 'walk'" class="form-section">
      <view class="glass form-card">
        <text class="form-label">选择球馆</text>
        <picker mode="selector" :range="venueNames" @change="onVenueChange">
          <view class="picker-input">{{ venueNames[venueIndex] || '请选择球馆' }}</view>
        </picker>
      </view>

      <view class="glass form-card">
        <text class="form-label">消费金额</text>
        <input class="input-glass" v-model="walkAmount" type="digit" placeholder="输入消费金额" />
      </view>

      <view class="glass form-card">
        <text class="form-label">关联会员（可选）</text>
        <input class="input-glass" v-model="memberSearch" placeholder="输入会员姓名/手机号搜索" @confirm="searchMember" />
        <view class="member-result" v-if="foundMember" style="margin-top:16rpx">
          <text>{{ foundMember.name }} · {{ foundMember.phone }}</text>
          <text class="tag tag-blue" style="margin-left:12rpx">余额 ¥{{ foundMember.balance }}</text>
          <text style="color:var(--color-danger);margin-left:12rpx;font-size:22rpx" @tap="foundMember = null">清除</text>
        </view>
      </view>

      <view class="glass form-card">
        <text class="form-label">备注</text>
        <input class="input-glass" v-model="walkRemark" placeholder="如：买水、租拍等" />
      </view>

      <view class="btn btn-primary" style="margin-top:24rpx" @tap="submitWalkOrder">确认开单 · ¥{{ walkAmount || '0' }}</view>
    </view>

    <!-- 快速入口：场地看板 -->
    <view class="quick-link" @tap="goFieldBoard">
      <image src="/static/icons/clipboard.svg" mode="aspectFit" style="width:36rpx;height:36rpx" />
      <text>查看场地状态看板</text>
      <text style="color:#C7C7CC">›</text>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { getVenues, getFields, getAvailability, getMembers, createOrder } from '../../api'
import { useUserStore } from '../../store/user'

const store = useUserStore()
const orderType = ref('field')
const venues = ref([])
const venueIndex = ref(-1)
const fields = ref([])
const fieldIndex = ref(-1)
const bookDate = ref('')
const slots = ref([])
const loadingSlots = ref(false)
const selectedSlot = ref('')
const selectedPrice = ref(0)
const memberSearch = ref('')
const foundMember = ref(null)
const walkAmount = ref('')
const walkRemark = ref('')

const today = new Date().toISOString().slice(0, 10)

const venueNames = ref([])
const fieldNames = ref([])

const orderAmount = ref(0)

async function loadVenues() {
  try {
    const res = await getVenues()
    venues.value = res.venues || []
    venueNames.value = venues.value.map(v => v.name)
  } catch { /* */ }
}

async function onVenueChange(e) {
  venueIndex.value = e.detail.value
  fieldIndex.value = -1
  fields.value = []
  fieldNames.value = []
  bookDate.value = ''
  slots.value = []
  const v = venues.value[venueIndex.value]
  if (!v) return
  try {
    const res = await getFields(v.id)
    fields.value = res.fields || []
    fieldNames.value = fields.value.map(f => `${f.name} (¥${f.price_per_hour}/h)`)
  } catch { /* */ }
}

async function onFieldChange(e) {
  fieldIndex.value = e.detail.value
  bookDate.value = ''
  slots.value = []
}

async function onDateChange(e) {
  bookDate.value = e.detail.value
  selectedSlot.value = ''
  orderAmount.value = 0
  const f = fields.value[fieldIndex.value]
  if (!f || !bookDate.value) return
  loadingSlots.value = true
  try {
    const res = await getAvailability(f.id, bookDate.value)
    slots.value = res.slots || []
  } catch { /* */ }
  finally { loadingSlots.value = false }
}

function selectSlot(s) {
  if (s.booked || s.expired) return
  if (selectedSlot.value === s.time) {
    selectedSlot.value = ''
    orderAmount.value = 0
    selectedPrice.value = 0
    return
  }
  selectedSlot.value = s.time
  selectedPrice.value = s.price
  orderAmount.value = s.price
}

async function searchMember() {
  if (!memberSearch.value) return
  try {
    const res = await getMembers({ keyword: memberSearch.value })
    if (res.members && res.members.length > 0) {
      foundMember.value = res.members[0]
    } else {
      uni.showToast({ title: '未找到会员', icon: 'none' })
    }
  } catch { /* */ }
}

async function submitOrder() {
  if (!selectedSlot.value) {
    return uni.showToast({ title: '请选择时段', icon: 'none' })
  }
  const v = venues.value[venueIndex.value]
  const f = fields.value[fieldIndex.value]
  if (!v || !f) return
  const endH = parseInt(selectedSlot.value.split(':')[0]) + 1
  const endTime = `${endH.toString().padStart(2, '0')}:00`

  try {
    const res = await createOrder({
      venue_id: v.id,
      field_id: f.id,
      member_id: foundMember.value?.id || null,
      order_type: 'field_book',
      book_date: bookDate.value,
      start_time: selectedSlot.value,
      end_time: endTime,
      original_amount: selectedPrice.value,
      paid_amount: 0,
      payment_method: '',
    })
    uni.showToast({ title: `开单成功 #${res.order_no}`, icon: 'success' })
    resetForm()
  } catch { /* */ }
}

async function submitWalkOrder() {
  const amount = parseFloat(walkAmount.value)
  if (!amount || amount <= 0) {
    return uni.showToast({ title: '请输入有效金额', icon: 'none' })
  }
  const v = venues.value[venueIndex.value >= 0 ? venueIndex.value : 0]
  if (!v) return
  try {
    await createOrder({
      venue_id: v.id,
      member_id: foundMember.value?.id || null,
      order_type: 'walk_in',
      original_amount: amount,
      paid_amount: amount,
      payment_method: 'cash',
      remark: walkRemark.value,
    })
    uni.showToast({ title: '散客开单成功', icon: 'success' })
    walkAmount.value = ''
    walkRemark.value = ''
    foundMember.value = null
  } catch { /* */ }
}

function resetForm() {
  bookDate.value = ''
  selectedSlot.value = ''
  selectedPrice.value = 0
  orderAmount.value = 0
  slots.value = []
  foundMember.value = null
  memberSearch.value = ''
}

function goFieldBoard() {
  uni.navigateTo({ url: '/pages/field-board/field-board' })
}

onShow(() => {
  if (!store.isLoggedIn) { uni.reLaunch({ url: '/pages/login/login' }); return }
  if (!store.canOrder) {
    uni.showToast({ title: '无开单权限', icon: 'none' })
    uni.switchTab({ url: '/pages/index/index' })
    return
  }
  loadVenues()
})
</script>

<style scoped>
.type-tabs { display: flex; margin-bottom: 24rpx; gap: 16rpx; }
.type-tab {
  flex: 1; text-align: center; padding: 20rpx 0;
  font-size: 28rpx; color: #86868B; background: rgba(255,255,255,0.5);
  border-radius: 16rpx; font-weight: 500;
}
.type-tab.active { background: var(--color-primary); color: #fff; font-weight: 600; }

.form-card { padding: 24rpx; margin-bottom: 20rpx; }
.form-label { font-size: 26rpx; color: #86868B; display: block; margin-bottom: 12rpx; }
.picker-input {
  padding: 16rpx 0; font-size: 30rpx; color: #1D1D1F;
  border-bottom: 1rpx solid rgba(0,0,0,0.06);
}

.slot-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12rpx; }
.slot-item {
  padding: 16rpx 12rpx; text-align: center;
  background: rgba(255,255,255,0.6); border-radius: 12rpx;
  border: 1rpx solid rgba(0,0,0,0.06); position: relative;
}
.slot-booked { background: rgba(0,0,0,0.04); opacity: 0.6; }
.slot-expired { background: rgba(0,0,0,0.02); opacity: 0.4; }
.slot-selected { border-color: var(--color-primary); background: rgba(64,158,255,0.08); }
.slot-time { font-size: 28rpx; font-weight: 600; color: #1D1D1F; display: block; }
.slot-price { font-size: 22rpx; color: #86868B; display: block; margin-top: 4rpx; }
.slot-badge { font-size: 18rpx; color: #C7C7CC; position: absolute; top: 4rpx; right: 6rpx; }

.member-result { display: flex; align-items: center; font-size: 26rpx; }

.quick-link {
  display: flex; justify-content: space-between; align-items: center;
  padding: 24rpx; margin-top: 24rpx; font-size: 28rpx; color: var(--color-primary);
}
</style>
