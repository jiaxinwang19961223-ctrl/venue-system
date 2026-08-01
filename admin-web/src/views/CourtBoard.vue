<template>
  <div>
    <div class="page-header">
      <h3><i class="ri-grid-line"></i> 包场看板</h3>
      <div class="actions">
        <el-date-picker v-model="date" type="date" value-format="YYYY-MM-DD" @change="load" />
        <el-select v-model="venueId" @change="loadVenue" style="width:160px">
          <el-option v-for="v in venues" :key="v.id" :label="v.name" :value="v.id" />
        </el-select>
        <el-tag>{{ date }} {{ weekday }}</el-tag>
      </div>
    </div>

    <!-- 场地时间格子看板 -->
    <div class="board" v-loading="loading">
      <!-- 表头 -->
      <div class="board-header">
        <div class="field-label">场地</div>
        <div v-for="slot in timeSlots" :key="slot" class="time-header" :class="{ peak: slot.includes('18') || slot.includes('19') || slot.includes('20') }">
          {{ slot }}
        </div>
      </div>

      <!-- 场地行 -->
      <div v-for="field in fields" :key="field.id" class="board-row">
        <div class="field-label">
          <strong>{{ field.name }}</strong>
          <span class="field-type">{{ typeLabel(field.field_type) }}</span>
        </div>
        <div
          v-for="slot in timeSlots"
          :key="slot"
          class="time-cell"
          :class="cellClass(field.id, slot)"
          @click="handleCellClick(field, slot)"
        >
          <template v-if="getBooking(field.id, slot)">
            <span class="booking-name">{{ getBooking(field.id, slot)?.name || '已订' }}</span>
          </template>
          <template v-else-if="isSlotPast(slot)">
            <span class="past-text">—</span>
          </template>
          <template v-else>
            <span class="avail-text">空闲</span>
          </template>
        </div>
      </div>

      <!-- 图例 -->
      <div class="legend">
        <span class="legend-item"><span class="dot avail"></span> 可预约</span>
        <span class="legend-item"><span class="dot booked"></span> 已预订</span>
        <span class="legend-item"><span class="dot past"></span> 已过期</span>
        <span class="legend-item"><span class="dot peak-dot"></span> 高峰时段</span>
      </div>
    </div>

    <!-- 快速开单弹窗 -->
    <el-dialog title="快速开单" v-model="showQuickOrder" width="420px">
      <div class="order-preview">
        <p><strong>场地：</strong>{{ selectedField?.name }}</p>
        <p><strong>时间：</strong>{{ date }} {{ selectedSlot }}</p>
      </div>
      <el-form :model="orderForm" label-width="80px">
        <el-form-item label="会员手机">
          <el-input v-model="orderForm.phone" placeholder="输入手机号搜索会员" @blur="searchMember">
            <template #prefix><i class="ri-phone-line"></i></template>
          </el-input>
        </el-form-item>
        <el-form-item v-if="foundMember" label="会员">
          <el-tag type="success">{{ foundMember.name }} | 余额: ¥{{ foundMember.balance?.toFixed(2) }}</el-tag>
        </el-form-item>
        <el-form-item label="金额">
          <el-input-number v-model="orderForm.paid_amount" :min="0" :precision="2" style="width:100%" />
        </el-form-item>
        <el-form-item label="支付">
          <el-radio-group v-model="orderForm.payment_method">
            <el-radio label="wechat">微信</el-radio>
            <el-radio label="cash">现金</el-radio>
            <el-radio label="card">会员卡</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showQuickOrder = false">取消</el-button>
        <el-button type="primary" @click="submitQuickOrder">确认开单</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getVenues, getFields, getOrders, createOrder } from '../api'
import { getMembers } from '../api'
import { ElMessage } from 'element-plus'

const venues = ref([])
const fields = ref([])
const bookings = ref([])
const venueId = ref(1)
const date = ref(new Date().toISOString().slice(0, 10))
const loading = ref(false)

// 时段：8:00-22:00 每小时一个
const timeSlots = Array.from({ length: 14 }, (_, i) => `${String(8 + i).padStart(2, '0')}:00`)

const weekday = computed(() => {
  const d = new Date(date.value)
  return ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][d.getDay()]
})

// 快速开单
const showQuickOrder = ref(false)
const selectedField = ref(null)
const selectedSlot = ref('')
const foundMember = ref(null)
const orderForm = ref({ phone: '', paid_amount: 0, payment_method: 'wechat', venue_id: 1, order_type: 'field_book' })

async function load() {
  loading.value = true
  try {
    const [fRes, oRes] = await Promise.all([
      getFields(venueId.value),
      getOrders({ date: date.value }),
    ])
    fields.value = fRes.fields || []
    bookings.value = (oRes.orders || []).filter(o => ['paid', 'confirmed', 'checked_in'].includes(o.status) && o.order_type === 'field_book')
  } catch { /* */ }
  loading.value = false
}

async function loadVenue() {
  orderForm.value.venue_id = venueId.value
  await load()
}

function getBooking(fieldId, slot) {
  return bookings.value.find(b => b.field_id === fieldId && b.start_time === slot)
}

function isSlotPast(slot) {
  const now = new Date()
  const slotDate = new Date(date.value + 'T' + slot)
  return slotDate < now
}

function cellClass(fieldId, slot) {
  if (getBooking(fieldId, slot)) return 'booked'
  if (isSlotPast(slot)) return 'past'
  return 'available'
}

function typeLabel(t) {
  const map = { badminton: '🏸', basketball: '🏀', pingpong: '🏓', tennis: '🎾', football: '⚽', swimming: '🏊', fitness: '🏋️' }
  return map[t] || t || ''
}

// 快速开单
function handleCellClick(field, slot) {
  if (getBooking(field.id, slot) || isSlotPast(slot)) return
  selectedField.value = field
  selectedSlot.value = slot
  orderForm.value = { phone: '', paid_amount: field.price_per_hour || 0, payment_method: 'wechat', venue_id: venueId.value, order_type: 'field_book' }
  foundMember.value = null
  showQuickOrder.value = true
}

async function searchMember() {
  if (!orderForm.value.phone) { foundMember.value = null; return }
  try {
    const res = await getMembers({ keyword: orderForm.value.phone })
    foundMember.value = (res.members || [])[0] || null
  } catch { foundMember.value = null }
}

async function submitQuickOrder() {
  try {
    await createOrder({
      venue_id: venueId.value,
      field_id: selectedField.value.id,
      member_id: foundMember.value?.id || null,
      order_type: 'field_book',
      book_date: date.value,
      start_time: selectedSlot.value,
      end_time: String(parseInt(selectedSlot.value) + 1).padStart(2, '0') + ':00',
      paid_amount: orderForm.value.paid_amount,
      payment_method: orderForm.value.payment_method,
    })
    showQuickOrder.value = false
    ElMessage.success('开单成功')
    await load()
  } catch { /* */ }
}

onMounted(async () => {
  try {
    const v = await getVenues()
    venues.value = v.venues || []
    if (venues.value.length > 0) venueId.value = venues.value[0].id
  } catch { /* */ }
  await load()
})
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 10px; }
.actions { display: flex; gap: 10px; align-items: center; }

.board { overflow-x: auto; background: #fff; border-radius: 4px; border: 1px solid #EBEEF5; }
.board-header, .board-row { display: flex; min-width: 1200px; }
.field-label { width: 130px; min-width: 130px; padding: 12px 10px; border-bottom: 1px solid #EBEEF5; border-right: 1px solid #EBEEF5; display: flex; flex-direction: column; justify-content: center; }
.field-type { font-size: 12px; color: #909399; }

.time-header { width: 80px; min-width: 80px; padding: 10px 4px; text-align: center; font-size: 13px; font-weight: 500; border-bottom: 2px solid #DCDFE6; border-right: 1px solid #EBEEF5; background: #FAFAFA; }
.time-header.peak { background: #FFF7E6; border-bottom-color: #E6A23C; }

.time-cell {
  width: 80px; min-width: 80px; height: 52px; border-bottom: 1px solid #EBEEF5; border-right: 1px solid #EBEEF5;
  display: flex; align-items: center; justify-content: center; font-size: 12px; cursor: default; transition: all 0.2s;
}
.time-cell.available { background: #F0F9EB; cursor: pointer; }
.time-cell.available:hover { background: #C8E6C9; }
.time-cell.booked { background: #FFECEC; cursor: not-allowed; }
.time-cell.past { background: #F5F5F5; cursor: not-allowed; }

.booking-name { color: #F56C6C; font-weight: 500; font-size: 11px; }
.avail-text { color: #67C23A; }
.past-text { color: #CCC; }

.legend { display: flex; gap: 20px; padding: 12px 16px; border-top: 1px solid #EBEEF5; }
.legend-item { display: flex; align-items: center; gap: 6px; font-size: 13px; color: #606266; }
.dot { width: 14px; height: 14px; border-radius: 3px; border: 1px solid #DCDFE6; }
.dot.avail { background: #F0F9EB; }
.dot.booked { background: #FFECEC; }
.dot.past { background: #F5F5F5; }
.dot.peak-dot { background: #FFF7E6; }

.order-preview { background: #F5F7FA; padding: 12px; border-radius: 4px; margin-bottom: 16px; }
.order-preview p { margin: 4px 0; }
</style>
