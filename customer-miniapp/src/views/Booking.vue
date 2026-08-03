<template>
  <div>
    <div class="page-header">
      <h3>
        <i class="ri-arrow-left-s-line" style="cursor:pointer" @click="$router.back()"></i>
        预订场地
      </h3>
    </div>

    <!-- 场地信息 -->
    <el-card class="info-card">
      <div class="field-summary">
        <span class="field-label">{{ fieldName }}</span>
        <span class="field-price">¥{{ fieldPrice }}/小时</span>
      </div>
    </el-card>

    <!-- 日期导航 -->
    <div class="date-nav">
      <el-button text @click="prevDay"><i class="ri-arrow-left-s-line"></i></el-button>
      <el-date-picker
        v-model="bookDate"
        type="date"
        value-format="YYYY-MM-DD"
        :disabled-date="disabledDate"
        @change="loadSlots"
        style="width:180px"
      />
      <el-button text @click="nextDay"><i class="ri-arrow-right-s-line"></i></el-button>
      <el-button size="small" @click="goToday">今天</el-button>
    </div>

    <!-- 时段选择 -->
    <div class="slots-section" v-loading="loadingSlots">
      <div v-if="slots.length === 0 && !loadingSlots" style="text-align:center;padding:40px;color:#909399">
        该日期无可选时段
      </div>
      <div class="slot-grid">
        <div
          v-for="s in slots"
          :key="s.time"
          class="slot-item"
          :class="{
            'slot-booked': s.booked,
            'slot-expired': s.expired,
            'slot-selected': selectedSlot?.time === s.time,
            'slot-peak': s.is_peak,
          }"
          @click="selectSlot(s)"
        >
          <div class="slot-time">{{ s.time }} - {{ s.end_time }}</div>
          <div class="slot-price">¥{{ s.price }}</div>
          <div class="slot-tag">
            <el-tag v-if="s.booked" type="danger" size="small">已订</el-tag>
            <el-tag v-else-if="s.expired" type="info" size="small">已过期</el-tag>
            <el-tag v-else-if="s.is_peak" type="warning" size="small">高峰</el-tag>
            <el-tag v-else type="success" size="small">可订</el-tag>
          </div>
        </div>
      </div>
    </div>

    <!-- 确认栏 -->
    <div class="confirm-bar" v-if="selectedSlot && !selectedSlot.booked && !selectedSlot.expired">
      <div class="confirm-info">
        <span>日期：<b>{{ bookDate }}</b></span>
        <span>时段：<b>{{ selectedSlot.time }} - {{ selectedSlot.end_time }}</b></span>
        <span>场地：<b>{{ fieldName }}</b></span>
        <span class="confirm-amount">¥{{ selectedSlot.price }}</span>
      </div>
      <el-button type="primary" size="large" :loading="submitting" @click="handleSubmit">
        提交订单
      </el-button>
    </div>

    <!-- 支付成功弹窗 -->
    <el-dialog v-model="showPayDialog" title="订单已创建" width="360px" :close-on-click-modal="false">
      <div class="pay-info">
        <p>订单号：<b>{{ createdOrderNo }}</b></p>
        <p>金额：<b>¥{{ selectedSlot?.price }}</b></p>
        <p>选择支付方式：</p>
      </div>
      <el-button type="success" size="large" style="width:100%" :loading="paying" @click="handlePay">
        <i class="ri-wechat-pay-fill"></i> 微信支付（模拟）
      </el-button>
      <div style="text-align:center;margin-top:8px">
        <el-button text size="small" @click="showPayDialog = false; $router.push('/orders')">稍后支付</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getVenue, getAvailability, createOrder, updateOrderStatus } from '../api'

const route = useRoute()
const router = useRouter()
const venueId = parseInt(route.params.venueId)
const fieldId = parseInt(route.params.fieldId)

const fieldName = ref('')
const fieldPrice = ref(0)
const bookDate = ref('')
const slots = ref([])
const selectedSlot = ref(null)
const loadingSlots = ref(false)
const submitting = ref(false)
const paying = ref(false)
const showPayDialog = ref(false)
const createdOrderNo = ref('')
const createdOrderId = ref(null)

onMounted(async () => {
  // 获取场地信息
  try {
    const venue = await getVenue(venueId)
    const field = venue.fields?.find(f => f.id === fieldId)
    if (field) {
      fieldName.value = field.name
      fieldPrice.value = field.price_per_hour
    }
  } catch { /* */ }
  // 默认今天
  bookDate.value = new Date().toISOString().slice(0, 10)
  loadSlots()
})

function disabledDate(time) {
  return time.getTime() < Date.now() - 86400000 // 不能选昨天及之前
}

function goToday() {
  bookDate.value = new Date().toISOString().slice(0, 10)
  loadSlots()
}

function prevDay() {
  const d = new Date(bookDate.value)
  d.setDate(d.getDate() - 1)
  bookDate.value = d.toISOString().slice(0, 10)
  loadSlots()
}

function nextDay() {
  const d = new Date(bookDate.value)
  d.setDate(d.getDate() + 1)
  bookDate.value = d.toISOString().slice(0, 10)
  loadSlots()
}

async function loadSlots() {
  selectedSlot.value = null
  loadingSlots.value = true
  try {
    const res = await getAvailability(fieldId, bookDate.value)
    slots.value = res.slots || []
  } catch { /* */ }
  finally { loadingSlots.value = false }
}

function selectSlot(slot) {
  if (slot.booked || slot.expired) return
  selectedSlot.value = slot
}

async function handleSubmit() {
  submitting.value = true
  try {
    const res = await createOrder({
      venue_id: venueId,
      field_id: fieldId,
      order_type: 'field_book',
      book_date: bookDate.value,
      start_time: selectedSlot.value.time,
      remark: '顾客自助订场',
    })
    createdOrderId.value = res.id
    createdOrderNo.value = res.order_no
    showPayDialog.value = true
  } catch { /* */ }
  finally { submitting.value = false }
}

async function handlePay() {
  paying.value = true
  try {
    await new Promise(r => setTimeout(r, 800)) // 模拟支付中
    await updateOrderStatus(createdOrderId.value, 'paid')
    ElMessage.success('支付成功')
    showPayDialog.value = false
    router.push('/orders')
  } catch { /* */ }
  finally { paying.value = false }
}
</script>

<style scoped>
.page-header h3 {
  margin: 0 0 16px;
  font-size: 20px;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 4px;
}

.info-card {
  margin-bottom: 16px;
}
.field-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.field-label {
  font-size: 16px;
  font-weight: 600;
}
.field-price {
  font-size: 20px;
  font-weight: 700;
  color: #E6A23C;
}

.date-nav {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 20px;
}

.slots-section {
  margin-bottom: 24px;
}
.slot-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
}
.slot-item {
  background: #fff;
  border: 2px solid #DCDFE6;
  border-radius: 8px;
  padding: 12px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
}
.slot-item:hover:not(.slot-booked):not(.slot-expired) {
  border-color: #409EFF;
}
.slot-selected {
  border-color: #409EFF !important;
  background: #ECF5FF;
}
.slot-booked {
  background: #FEF0F0;
  border-color: #FBC4C4;
  cursor: not-allowed;
}
.slot-expired {
  background: #F5F7FA;
  border-color: #E4E7ED;
  cursor: not-allowed;
  opacity: 0.6;
}
.slot-peak:not(.slot-booked):not(.slot-expired) {
  border-color: #F5DAB1;
}
.slot-time {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}
.slot-price {
  font-size: 13px;
  color: #E6A23C;
  margin-bottom: 6px;
}

.confirm-bar {
  position: sticky;
  bottom: 16px;
  background: #fff;
  border: 1px solid #E4E7ED;
  border-radius: 8px;
  padding: 16px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 -2px 12px rgba(0,0,0,0.08);
}
.confirm-info {
  display: flex;
  gap: 20px;
  font-size: 14px;
  color: #606266;
}
.confirm-amount {
  font-size: 22px;
  font-weight: 700;
  color: #E6A23C;
}

.pay-info p {
  margin: 8px 0;
  font-size: 15px;
}
</style>
