<template>
  <div>
    <div class="page-header">
      <h3><i class="ri-grid-line"></i> 包场看板</h3>
      <div class="actions">
        <div class="date-nav">
          <el-button circle size="small" @click="prevDay"><i class="ri-arrow-left-s-line"></i></el-button>
          <el-date-picker v-model="pickerDate" type="date" value-format="YYYY-MM-DD" style="width:155px" @change="onDatePicked" :clearable="false" />
          <el-button circle size="small" @click="nextDay"><i class="ri-arrow-right-s-line"></i></el-button>
          <el-button size="small" @click="goToday">今天</el-button>
        </div>
      </div>
    </div>

    <!-- 看板主体 -->
    <div class="board-wrap" v-loading="loading">
      <div class="board-scroll" ref="scrollRef" @wheel.prevent="onWheel">
        <div class="board-table">

          <!-- 表头行 -->
          <div class="board-row header-row">
            <div class="field-col fixed-col header-col">场地</div>
            <div
              v-for="slot in timeSlots"
              :key="slot"
              class="time-col"
              :class="{ peak: isPeak(slot) }"
            >
              {{ slot }}
            </div>
          </div>

          <!-- 场地行 -->
          <div
            v-for="field in fields"
            :key="field.id"
            class="board-row"
          >
            <div class="field-col fixed-col">
              <span class="field-name">{{ field.name }}</span>
              <span class="field-type">{{ typeLabel(field.field_type) }}</span>
            </div>
            <div
              v-for="slot in timeSlots"
              :key="`${field.id}-${slot}`"
              class="time-col slot-cell"
              :class="cellClass(field.id, slot)"
              @click="handleCellClick(field, slot)"
            >
              <span v-if="getBooking(field.id, slot)" :class="getBooking(field.id,slot).status === 'pending' ? 'cell-locked' : 'cell-booked'">
                {{ getBooking(field.id, slot)?.status === 'pending' ? '锁定' : getBooking(field.id, slot)?.name || '已订' }}
              </span>
              <span v-else-if="isSlotPast(slot)" class="cell-past"></span>
              <span v-else class="cell-free">空闲</span>
            </div>
          </div>

        </div>
      </div>
    </div>

    <!-- 图例 -->
    <div class="legend">
      <span><span class="dot free"></span> 可预约</span>
      <span><span class="dot locked-dot"></span> 已锁定</span>
      <span><span class="dot booked"></span> 已预订</span>
      <span><span class="dot past"></span> 已过期</span>
      <span><span class="dot peak-dot"></span> 高峰</span>
    </div>

    <!-- 场地预订 — 完整整合表单 -->
    <el-dialog title="场地预订" v-model="showQuickOrder" width="520px">
      <!-- 场地信息 -->
      <el-descriptions :column="3" border size="small">
        <el-descriptions-item label="场地">{{ selectedField?.name }}</el-descriptions-item>
        <el-descriptions-item label="日期">{{ date }}</el-descriptions-item>
        <el-descriptions-item label="价格">¥{{ selectedField?.price_per_hour || 0 }}/时</el-descriptions-item>
        <el-descriptions-item label="时段">{{ selectedSlot }} - {{ endSlot }}</el-descriptions-item>
        <el-descriptions-item label="类型">{{ typeLabel(selectedField?.field_type) }}</el-descriptions-item>
        <el-descriptions-item label="状态"><el-tag type="success" size="small">可预订</el-tag></el-descriptions-item>
      </el-descriptions>

      <el-divider />

      <!-- 顾客信息 -->
      <el-form :model="orderForm" label-width="80px">
        <el-form-item label="顾客类型">
          <el-radio-group v-model="customerType" @change="onCustomerTypeChange">
            <el-radio label="member">会员</el-radio>
            <el-radio label="walkin">散客</el-radio>
          </el-radio-group>
        </el-form-item>

        <template v-if="customerType === 'member'">
          <el-form-item label="手机号">
            <el-input v-model="orderForm.phone" placeholder="输入会员手机号" @input="onPhoneInput">
              <template #append><el-button @click="searchMember" :loading="searching">搜索</el-button></template>
            </el-input>
          </el-form-item>
          <!-- 搜索结果 -->
          <div v-if="foundMember" class="member-card">
            <div class="member-card-header">
              <el-avatar :src="foundMember.face_image" :size="40" />
              <div style="flex:1">
                <strong>{{ foundMember.name }}</strong>
                <p style="margin:2px 0 0;font-size:12px;color:#909399">{{ foundMember.phone }}</p>
              </div>
              <el-tag type="success">余额 ¥{{ foundMember.balance?.toFixed(2) }}</el-tag>
            </div>
          </div>
          <p v-else-if="orderForm.phone && searched" style="color:#909399;font-size:13px">未找到会员，自动切换为散客</p>
        </template>

        <template v-else>
          <el-form-item label="顾客姓名">
            <el-input v-model="orderForm.customer_name" placeholder="散客姓名" />
          </el-form-item>
          <el-form-item label="手机号">
            <el-input v-model="orderForm.phone" placeholder="散客手机号（选填）" />
          </el-form-item>
        </template>

        <el-divider />

        <!-- 支付 -->
        <el-form-item label="支付方式">
          <el-radio-group v-model="orderForm.payment_method" @change="onPaymentChange">
            <el-radio label="wechat">微信</el-radio>
            <el-radio label="cash">现金</el-radio>
            <el-radio label="balance" :disabled="!foundMember">会员余额</el-radio>
            <el-radio label="card_times" :disabled="!foundMember || !memberCards.length">次卡扣次</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item v-if="orderForm.payment_method === 'card_times'" label="选择次卡">
          <el-select v-model="orderForm.card_id" style="width:100%" placeholder="选择要扣次的卡">
            <el-option v-for="c in memberCards" :key="c.id" :label="`${c.card_type} 剩余${c.total_times - c.used_times}次`" :value="c.id" />
          </el-select>
        </el-form-item>

        <el-form-item label="实收金额" v-if="orderForm.payment_method !== 'card_times'">
          <el-input-number v-model="orderForm.paid_amount" :min="0" :precision="2" style="width:100%" />
          <span v-if="orderForm.payment_method === 'balance' && foundMember" style="margin-left:8px;color:#909399;font-size:12px;white-space:nowrap">
            扣后余额 ¥{{ Math.max(0, (foundMember.balance || 0) - orderForm.paid_amount).toFixed(2) }}
          </span>
        </el-form-item>

        <el-form-item label="备注">
          <el-input v-model="orderForm.remark" placeholder="备注信息（选填）" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showQuickOrder = false">取消</el-button>
        <el-button type="warning" @click="submitQuickOrder('pending')" :loading="submitting">
          <i class="ri-lock-line"></i> 锁场
        </el-button>
        <el-button type="primary" @click="submitQuickOrder('confirmed')" :loading="submitting">
          <i class="ri-check-double-line"></i> 确认订场
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { getVenues, getFields, getOrders, getMembers, createOrder } from '../api'
import api from '../api'
import { useVenueStore } from '../stores/venue'
import { ElMessage, ElMessageBox } from 'element-plus'

const venueStore = useVenueStore()
const venues = ref([])
const fields = ref([])
const bookings = ref([])
const venueId = computed(() => venueStore.currentId)
const date = ref(new Date().toISOString().slice(0, 10))
const loading = ref(false)
const pickerDate = ref(new Date().toISOString().slice(0, 10))
const scrollRef = ref(null)

const timeSlots = Array.from({ length: 15 }, (_, i) => `${String(8 + i).padStart(2, '0')}:00`)


const showQuickOrder = ref(false)
const selectedField = ref(null)
const selectedSlot = ref('')
const foundMember = ref(null)
const memberCards = ref([])
const searched = ref(false)
const searching = ref(false)
const submitting = ref(false)
const customerType = ref('member')
const orderForm = ref({ phone: '', customer_name: '', paid_amount: 0, payment_method: 'wechat', venue_id: venueStore.currentId, order_type: 'field_book', remark: '', card_id: null })

const endSlot = computed(() => {
  if (!selectedSlot.value) return ''
  const h = parseInt(selectedSlot.value)
  return `${String(h + 1).padStart(2, '0')}:00`
})

// ──── 日期导航 ────
function setDate(d) { date.value = d; pickerDate.value = d; load() }
function prevDay() { const d = new Date(date.value); d.setDate(d.getDate() - 1); setDate(d.toISOString().slice(0, 10)) }
function nextDay() { const d = new Date(date.value); d.setDate(d.getDate() + 1); setDate(d.toISOString().slice(0, 10)) }
function goToday() { setDate(new Date().toISOString().slice(0, 10)) }
function onDatePicked(v) { if (v) setDate(v) }

// ──── 滚轮横向滚动 ────
function onWheel(e) {
  if (!scrollRef.value) return
  scrollRef.value.scrollLeft += e.deltaY
}

// ──── 数据加载 ────
async function load() {
  loading.value = true
  try {
    const [fRes, oRes] = await Promise.all([
      getFields(venueId.value),
      getOrders({ date: date.value }),
    ])
    fields.value = fRes.fields || []
    bookings.value = (oRes.orders || []).filter(o =>
      !['cancelled', 'refunded'].includes(o.status) && o.order_type === 'field_book'
    )
  } catch { /* */ }
  loading.value = false
  // 滚动到当前时间
  nextTick(() => {
    if (!scrollRef.value) return
    const now = new Date()
    if (date.value === now.toISOString().slice(0, 10)) {
      const hour = now.getHours()
      scrollRef.value.scrollLeft = Math.max(0, (hour - 8) * 80 - 200)
    }
  })
}

// ──── 单元格逻辑 ────
function getBooking(fieldId, slot) {
  return bookings.value.find(b => b.field_id === fieldId && b.start_time === slot)
}
function isSlotPast(slot) {
  const now = new Date()
  const slotDate = new Date(date.value + 'T' + slot)
  return slotDate < now
}
function isPeak(slot) {
  return ['18:00', '19:00', '20:00'].includes(slot)
}
function cellClass(fieldId, slot) {
  const b = getBooking(fieldId, slot)
  if (b) {
    if (b.status === 'pending') return 'locked'
    return 'booked'
  }
  if (isSlotPast(slot)) return 'past'
  return 'free'
}
function typeLabel(t) {
  const map = { badminton: '🏸', basketball: '🏀', pingpong: '🏓', tennis: '🎾', football: '⚽', swimming: '🏊', fitness: '🏋️' }
  return map[t] || ''
}

// ──── 快速开单 ────
function handleCellClick(field, slot) {
  const booking = getBooking(field.id, slot)
  if (isSlotPast(slot)) return

  if (booking?.status === 'pending') {
    ElMessageBox.confirm(
      `${field.name} ${slot} 已锁定${booking.name ? ' · ' + booking.name : ''}`,
      '锁定场地',
      { confirmButtonText: '确认订场', cancelButtonText: '取消锁场', distinguishCancelAndClose: true, type: 'info' }
    ).then(async () => {
      try { await api.put(`/orders/${booking.id}/status?status=confirmed`); ElMessage.success('已确认订场'); await load() } catch { /* */ }
    }).catch(async (action) => {
      if (action === 'cancel') {
        try { await api.put(`/orders/${booking.id}/status?status=cancelled`); ElMessage.success('已取消锁场'); await load() } catch { /* */ }
      }
    })
    return
  }

  if (booking) {
    ElMessageBox.confirm(
      `${field.name} ${slot} 已预订${booking.name ? ' · ' + booking.name : ''}，要取消吗？`,
      '取消预订',
      { confirmButtonText: '取消预订', cancelButtonText: '保留', type: 'warning', confirmButtonClass: 'el-button--danger' }
    ).then(async () => {
      try { await api.put(`/orders/${booking.id}/status?status=cancelled`); ElMessage.success('已取消预订'); await load() } catch { /* */ }
    }).catch(() => {})
    return
  }

  // 新预订
  selectedField.value = field
  selectedSlot.value = slot
  orderForm.value = { phone: '', customer_name: '', paid_amount: field.price_per_hour || 0, payment_method: 'wechat', venue_id: venueId.value, order_type: 'field_book', remark: '', card_id: null }
  foundMember.value = null
  memberCards.value = []
  searched.value = false
  customerType.value = 'member'
  showQuickOrder.value = true
}

function onCustomerTypeChange() {
  foundMember.value = null
  searched.value = false
  orderForm.value.phone = ''
  orderForm.value.customer_name = ''
  orderForm.value.payment_method = 'wechat'
  memberCards.value = []
}

function onPaymentChange(method) {
  if (method === 'card_times') orderForm.value.paid_amount = 0
}

function onPhoneInput() {
  foundMember.value = null
  searched.value = false
  memberCards.value = []
}

async function searchMember() {
  if (!orderForm.value.phone || orderForm.value.phone.length < 4) { ElMessage.warning('请输入至少4位手机号'); return }
  searching.value = true; searched.value = true
  try {
    const r = await getMembers({ keyword: orderForm.value.phone })
    foundMember.value = (r.members || [])[0] || null
    if (foundMember.value) {
      try {
        const cr = await api.get(`/members/${foundMember.value.id}/cards`)
        memberCards.value = (cr.cards || []).filter(c => c.is_active && c.total_times > c.used_times)
      } catch { memberCards.value = [] }
    } else {
      // 没找到会员 → 自动切散客
      customerType.value = 'walkin'
    }
  } catch { foundMember.value = null }
  searching.value = false
}

async function submitQuickOrder(status) {
  submitting.value = true
  try {
    let paymentMethod = orderForm.value.payment_method
    let memberId = null

    if (customerType.value === 'member' && foundMember.value) {
      memberId = foundMember.value.id
      // 会员余额支付 → 扣余额
      if (paymentMethod === 'balance') {
        paymentMethod = 'card'
        try {
          await api.post(`/members/${memberId}/consume`, {
            amount: orderForm.value.paid_amount,
            remark: `场租 ${selectedField.value?.name} ${date.value} ${selectedSlot.value}`,
          })
        } catch { /* */ }
      }
      // 次卡扣次
      if (paymentMethod === 'card_times') {
        try {
          await api.post(`/members/${memberId}/consume`, {
            use_card: true,
            card_id: orderForm.value.card_id,
            remark: `场租 ${selectedField.value?.name} ${date.value} ${selectedSlot.value}`,
          })
        } catch { /* */ }
        orderForm.value.paid_amount = 0
        paymentMethod = 'card'
      }
    }

    const remark = [
      customerType.value === 'walkin' ? `散客:${orderForm.value.customer_name || orderForm.value.phone}` : '',
      orderForm.value.payment_method === 'card_times' ? '次卡扣次' : '',
      orderForm.value.remark,
    ].filter(Boolean).join(' | ')

    const created = await createOrder({
      venue_id: venueId.value, field_id: selectedField.value.id,
      member_id: memberId, order_type: 'field_book',
      book_date: date.value, start_time: selectedSlot.value,
      end_time: endSlot.value,
      paid_amount: orderForm.value.paid_amount, payment_method: paymentMethod,
      remark,
    })
    if (created?.id) {
      try { await api.put(`/orders/${created.id}/status?status=${status}`) } catch { /* */ }
    }
    showQuickOrder.value = false
    ElMessage.success(status === 'pending' ? '锁场成功' : '订场成功')
    await load()
  } catch { /* */ }
  submitting.value = false
}

onMounted(async () => {
  await venueStore.load()
  await load()
})

watch(() => venueStore.currentId, () => { load() })
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 10px; }
.actions { display: flex; gap: 10px; align-items: center; }
.date-nav { display: flex; align-items: center; gap: 4px; }
.date-display { font-size: 14px; font-weight: 600; padding: 4px 8px; cursor: pointer; border-radius: 4px; user-select: none; }
.date-display:hover { background: #ECF5FF; }

/* ──── 看板主体 ──── */
.board-wrap { border: 1px solid #EBEEF5; border-radius: 6px; background: #fff; overflow: hidden; }
.board-scroll { overflow-x: auto; overflow-y: hidden; }
.board-scroll::-webkit-scrollbar { height: 6px; }
.board-scroll::-webkit-scrollbar-thumb { background: #C0C4CC; border-radius: 3px; }

.board-table { display: inline-block; min-width: 100%; }

.board-row { display: flex; }
.board-row:not(.header-row):hover { background: #F5F7FA; }

/* 固定列 */
.fixed-col { position: sticky; left: 0; z-index: 2; background: inherit; }
.header-col { background: #FAFAFA; font-weight: 600; }

.field-col {
  width: 120px; min-width: 120px;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 10px 6px; border-bottom: 1px solid #EBEEF5; border-right: 2px solid #DCDFE6;
  font-size: 13px;
}
.header-row .field-col { font-size: 14px; border-bottom: 2px solid #DCDFE6; }
.field-name { font-weight: 600; }
.field-type { font-size: 11px; color: #909399; margin-top: 2px; }

/* 时间列 */
.time-col {
  width: 76px; min-width: 76px;
  display: flex; align-items: center; justify-content: center;
  padding: 10px 2px; font-size: 12px;
  border-bottom: 1px solid #EBEEF5; border-right: 1px solid #F2F6FC;
}

.header-row .time-col {
  font-weight: 600; font-size: 13px; padding: 12px 2px;
  background: #FAFAFA; border-bottom: 2px solid #DCDFE6;
}
.time-col.peak { background: #FFF7E6; border-bottom-color: #E6A23C; }

/* 单元格 */
.slot-cell { cursor: default; height: 56px; transition: all 0.15s; }
.slot-cell.free { background: #F0F9EB; cursor: pointer; }
.slot-cell.free:hover { background: #C8E6C9; transform: scale(1.05); z-index: 1; box-shadow: 0 2px 8px rgba(103,194,58,0.3); border-radius: 4px; }
.slot-cell.booked { background: #FFECEC; cursor: not-allowed; }
.slot-cell.past { background: #F5F5F5; cursor: not-allowed; }

.cell-booked { color: #F56C6C; font-weight: 500; font-size: 11px; }
.cell-locked { color: #909399; font-weight: 500; font-size: 11px; }
.cell-free { color: #67C23A; }
.cell-past { color: #DDD; }

.slot-cell.locked { background: #F0F0F0; cursor: pointer; }
.slot-cell.locked:hover { background: #E0E0E0; }

/* ──── 图例 ──── */
.legend { display: flex; gap: 24px; padding: 12px 16px; margin-top: 12px; background: #FAFAFA; border-radius: 6px; }
.legend span { display: flex; align-items: center; gap: 6px; font-size: 13px; color: #606266; }
.legend .dot { width: 14px; height: 14px; border-radius: 3px; }
.dot.free { background: #F0F9EB; border: 1px solid #C8E6C9; }
.dot.locked-dot { background: #F0F0F0; border: 1px solid #C0C4CC; }
.dot.booked { background: #FFECEC; border: 1px solid #FFA8A8; }
.dot.past { background: #F5F5F5; border: 1px solid #DDD; }
.dot.peak-dot { background: #FFF7E6; border: 1px solid #F5DAB1; }

.order-preview { background: #F5F7FA; padding: 12px; border-radius: 4px; margin-bottom: 16px; }
.order-preview p { margin: 4px 0; }

.member-card { background: #ECF5FF; border: 1px solid #D9ECFF; border-radius: 8px; padding: 12px; }
.member-card-header { display: flex; align-items: center; gap: 12px; }
.member-card-header p { margin: 2px 0 0; font-size: 12px; color: #909399; }
.info-label { font-size: 11px; color: #909399; }
</style>
