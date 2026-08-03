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
              :key="slot.time"
              class="time-col"
              :class="{ peak: isPeak(slot.time) }"
            >
              {{ slot.label }}
            </div>
          </div>

          <!-- 场地行 -->
          <template v-for="pf in parentFields" :key="pf.id">
            <div class="board-row" :class="{ 'parent-row': hasChildren(pf.id) }">
              <div class="field-col fixed-col">
                <span class="field-name">{{ pf.name }}</span>
                <span class="field-type">{{ typeIcon(pf.field_type) }} {{ typeLabel(pf.field_type) }}</span>
                <span class="field-price">¥{{ pf.price_per_hour }}/{{ pf.duration || 1 }}h</span>
              </div>
              <div
                v-for="slot in timeSlots"
                :key="`${pf.id}-${slot.time}`"
                class="time-col slot-cell"
                :class="cellClass(pf.id, slot.time)"
                @click="handleCellClick(pf, slot.time)"
              >
                <span v-if="getBooking(pf.id, slot.time) && !getBooking(pf.id, slot.time)._viaChild" :class="getBooking(pf.id,slot.time).status === 'pending' ? 'cell-locked' : 'cell-booked'">
                  {{ getBooking(pf.id, slot.time)?.status === 'pending' ? '锁定' : getBooking(pf.id, slot.time)?.name || '已订' }}
                </span>
                <span v-else-if="getBooking(pf.id, slot.time)?._viaChild" class="cell-child-booked">
                  {{ getBooking(pf.id, slot.time)?._childName }}
                </span>
                <span v-else-if="isSlotPast(slot.time)" class="cell-past"></span>
                <span v-else class="cell-free">空闲</span>
              </div>
            </div>

            <!-- 子场地行（全场拆分的半场） -->
            <div v-if="getChildren(pf.id).length" class="child-rows">
              <div
                v-for="child in getChildren(pf.id)"
                :key="child.id"
                class="board-row child-row"
              >
                <div class="field-col fixed-col">
                  <span class="field-name">{{ child.name }}</span>
                  <span class="field-type">¥{{ child.price_per_hour }}/{{ child.duration || 1 }}h</span>
                </div>
                <div
                  v-for="slot in timeSlots"
                  :key="`${child.id}-${slot.time}`"
                  class="time-col slot-cell"
                  :class="cellClass(child.id, slot.time)"
                  @click="handleCellClick(child, slot.time)"
                >
                  <span v-if="getBooking(child.id, slot.time)" :class="getBooking(child.id,slot.time).status === 'pending' ? 'cell-locked' : 'cell-booked'">
                    {{ getBooking(child.id, slot.time)?.status === 'pending' ? '锁定' : getBooking(child.id, slot.time)?.name || '已订' }}
                  </span>
                  <span v-else-if="getBooking(child.id, slot.time)?._viaChild" class="cell-child-booked">
                    {{ getBooking(child.id, slot.time)?._childName }}
                  </span>
                  <span v-else-if="isSlotPast(slot.time)" class="cell-past"></span>
                  <span v-else class="cell-free">空闲</span>
                </div>
              </div>
            </div>
          </template>

        </div>
      </div>
      <!-- 图例 -->
      <div class="legend">
        <span><span class="dot free"></span> 空闲</span>
        <span><span class="dot locked-dot"></span> 锁定</span>
        <span><span class="dot booked"></span> 已订</span>
        <span><span class="dot past"></span> 过期</span>
      </div>
    </div>

    <!-- 场地预订 — 完整整合表单 -->
    <el-dialog title="场地预订" v-model="showQuickOrder" width="520px">
      <!-- 场地信息 -->
      <el-descriptions :column="3" border size="small">
        <el-descriptions-item label="场地">{{ selectedField?.name }}</el-descriptions-item>
        <el-descriptions-item label="日期">{{ date }}</el-descriptions-item>
        <el-descriptions-item label="价格">¥{{ selectedField?.price_per_hour || 0 }}</el-descriptions-item>
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
          <el-radio-group v-model="orderForm.payment_method">
            <el-radio label="wechat">微信</el-radio>
            <el-radio label="cash">现金</el-radio>
            <el-radio label="balance" :disabled="!foundMember">会员余额</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="实收金额">
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
import { getVenues, getVenue, getFields, getOrders, getMembers, createOrder } from '../api'
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

const venueHours = ref('09:00-22:00')
const timeSlots = computed(() => {
  const parts = (venueHours.value || '09:00-22:00').split('-')
  const start = parseInt(parts[0]) || 9
  const end = parseInt(parts[1]) || 22
  const count = Math.max(1, end - start)
  return Array.from({ length: count }, (_, i) => {
    const h = start + i
    return { time: `${String(h).padStart(2,'0')}:00`, label: `${String(h).padStart(2,'0')}-${String(h+1).padStart(2,'0')}` }
  })
})


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
  if (!selectedSlot.value || !selectedField.value) return ''
  const h = parseInt(selectedSlot.value)
  const dur = selectedField.value.duration || 1
  return `${String(h + dur).padStart(2, '0')}:00`
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

// ──── 场地分组（父场地+子场地）────
// 按类型+名称排序
const typeOrder = { badminton: 1, pingpong: 2, tennis: 3, football: 4, basketball: 5, swimming: 6, fitness: 7, other: 8 }
function fieldSortKey(f) {
  // 提取楼层：匹配 XF/X楼/X号 或首个数字
  const floorMatch = f.name.match(/(\d+)[F楼号]/) || f.name.match(/(\d+)/)
  const floor = floorMatch ? parseInt(floorMatch[1]) : 99
  const type = typeOrder[f.field_type] || 9
  const num = parseInt(f.name.match(/\d+/)?.[0]) || 99
  const hasChild = fields.value.some(c => c.parent_field_id === f.id)
  const parentPri = hasChild ? 0 : (f.parent_field_id ? 2 : 1)
  // 球类优先 → 父子（全场>半场）→ 楼层 → 场地号
  return `${type}-${parentPri}-${String(floor).padStart(2,'0')}-${String(num).padStart(3,'0')}-${f.name}`
}

const parentFields = computed(() =>
  fields.value.filter(f => !f.parent_field_id).sort((a, b) => fieldSortKey(a).localeCompare(fieldSortKey(b)))
)
const getChildren = (parentId) =>
  fields.value.filter(f => f.parent_field_id === parentId).sort((a, b) => a.name.localeCompare(b.name))
const hasChildren = (id) => fields.value.some(f => f.parent_field_id === id)

function typeIcon(t) {
  const map = { badminton: '🏸', basketball: '🏀', pingpong: '🏓', tennis: '🎾', football: '⚽', swimming: '🏊', fitness: '🏋️' }
  return map[t] || ''
}

// ──── 数据加载 ────
let _loading = false
async function load() {
  if (_loading) return  // 防止重复加载覆盖数据
  if (!venueId.value) return
  _loading = true
  loading.value = true
  try {
    const [fRes, oRes, vRes] = await Promise.all([
      getFields(venueId.value),
      getOrders({ date: date.value }),
      getVenue(venueId.value),
    ])
    venueHours.value = (vRes?.business_hours) || '09:00-22:00'
    fields.value = (fRes.fields || []).map(f => ({
      ...f,
      parent_field_id: f.parent_field_id || null,
    }))
    bookings.value = (oRes.orders || []).filter(o =>
      !['cancelled', 'refunded'].includes(o.status) && o.order_type === 'field_book'
    )
  } catch { /* */ }
  loading.value = false
  _loading = false
  nextTick(() => {
    if (!scrollRef.value) return
    const now = new Date()
    if (date.value === now.toISOString().slice(0, 10)) {
      scrollRef.value.scrollLeft = Math.max(0, (now.getHours() - 8) * 80 - 200)
    }
  })
}

// ──── 订场冲突检测（含父子场地互斥）────
function getBooking(fieldId, slot) {
  const field = fields.value.find(f => f.id === fieldId)
  if (!field) return null

  // 直接查该场地的订单
  const direct = bookings.value.find(b => b.field_id === fieldId && b.start_time === slot)
  if (direct) return direct

  // 如果是子场地 → 检查父场地是否被订
  if (field.parent_field_id) {
    return bookings.value.find(b => b.field_id === field.parent_field_id && b.start_time === slot) || null
  }

  // 如果是父场地 → 检查任一子场地是否被订
  const children = getChildren(fieldId)
  if (children.length) {
    for (const child of children) {
      const b = bookings.value.find(b => b.field_id === child.id && b.start_time === slot)
      if (b) return { ...b, _viaChild: true, _childName: child.name }
    }
  }

  return null
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
  // 子场地隐藏，不单独显示行（在父场地行中展示）
  const field = fields.value.find(f => f.id === fieldId)
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
    const hasPaid = booking.status === 'paid' || booking.status === 'confirmed' || booking.status === 'checked_in'
    const paidInfo = hasPaid ? `\n金额：¥${(booking.paid_amount || 0).toFixed(2)}` : ''
    ElMessageBox.confirm(
      `${field.name} ${slot} 已预订${booking.name ? ' · ' + booking.name : ''}${paidInfo}`,
      '取消预订',
      {
        confirmButtonText: hasPaid ? '退费取消' : '取消预订',
        cancelButtonText: '保留',
        distinguishCancelAndClose: hasPaid,
        type: 'warning',
        confirmButtonClass: 'el-button--danger',
      }
    ).then(async () => {
      // 退费：后端自动恢复会员余额
      if (hasPaid) {
        try {
          await api.put(`/orders/${booking.id}/status?status=refunded`)
          ElMessage.success('已退款，余额已自动恢复')
        } catch { /* */ }
      } else {
        try { await api.put(`/orders/${booking.id}/status?status=cancelled`); ElMessage.success('已取消') } catch { /* */ }
      }
      await load()
    }).catch(async (action) => {
      // 仅取消不退费
      if (action === 'cancel') {
        try { await api.put(`/orders/${booking.id}/status?status=cancelled`); ElMessage.success('已取消（不退费）'); await load() } catch { /* */ }
      }
    })
    return
  }

  // 新预订 — 篮球场自动占2小时
  const dur = field.duration || 1
  if (dur > 1) {
    // 检查后续时段是否都空闲
    const nextH = parseInt(slot.split(':')[0])
    let conflict = false
    for (let i = 1; i < dur; i++) {
      const nextSlot = `${String(nextH + i).padStart(2, '0')}:00`
      if (getBooking(field.id, nextSlot) || isSlotPast(nextSlot)) { conflict = true; break }
    }
    if (conflict) {
      ElMessage.warning(`篮球场需连续${dur}小时，后续时段不可用`)
      return
    }
  }

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
      orderForm.value.payment_method = 'balance'
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
      // 会员余额支付 → 校验并扣余额
      if (paymentMethod === 'balance') {
        if ((foundMember.value.balance || 0) < orderForm.value.paid_amount) {
          ElMessage.warning('会员余额不足')
          submitting.value = false
          return
        }
        paymentMethod = 'card'
      }
    }

    const remark = [
      customerType.value === 'walkin' ? `散客:${orderForm.value.customer_name || orderForm.value.phone}` : '',
      orderForm.value.remark,
    ].filter(Boolean).join(' | ')

    const created = await createOrder({
      venue_id: venueId.value, field_id: selectedField.value.id,
      member_id: memberId, order_type: 'field_book',
      book_date: date.value, start_time: selectedSlot.value,
      end_time: endSlot.value,
      duration: selectedField.value?.duration || 1,
      original_amount: orderForm.value.paid_amount,
      paid_amount: orderForm.value.paid_amount, payment_method: paymentMethod,
      remark,
    })
    if (created?.id) {
      try { await api.put(`/orders/${created.id}/status?status=${status}`) } catch { /* */ }
      // 会员余额支付：扣余额
      if (memberId && orderForm.value.payment_method === 'balance') {
        const newBalance = (foundMember.value.balance || 0) - orderForm.value.paid_amount
        try {
          await api.put(`/members/${memberId}`, { balance: Math.max(0, newBalance), total_consumption: (foundMember.value.total_consumption || 0) + orderForm.value.paid_amount })
          foundMember.value.balance = Math.max(0, newBalance)
        } catch { /* */ }
      }
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
.board-wrap {
  border: 1px solid rgba(0,0,0,0.06);
  border-radius: 12px; background: rgba(255,255,255,0.7);
  height: calc(100vh - 180px);
  display: flex; flex-direction: column; overflow: hidden;
}
.board-scroll {
  overflow-x: scroll; overflow-y: auto; flex: 1; min-height: 0;
}
.board-scroll::-webkit-scrollbar { width: 6px; height: 8px; }
.board-scroll::-webkit-scrollbar-track { background: rgba(0,0,0,0.04); border-radius: 4px; }
.board-scroll::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.2); border-radius: 4px; }
.board-scroll::-webkit-scrollbar-thumb:hover { background: rgba(0,0,0,0.35); }

.board-table { min-width: 1100px; }

.board-row {
  display: flex; height: 58px; flex-shrink: 0;
  background: #fff;
}
.board-row:hover { background: #F5F7FA; }
.header-row:hover { background: #FAFAFA; }

/* 固定表头 */
.header-row { position: sticky; top: 0; z-index: 3; }

/* 固定列 */
.fixed-col {
  position: sticky; left: 0; z-index: 2;
  background: #fff !important;
  box-shadow: 2px 0 4px rgba(0,0,0,0.04);
}
.header-row .fixed-col { z-index: 4; background: #FAFAFA; }
.header-col { background: #FAFAFA; font-weight: 600; }

/* 子场地行 */
.child-row .fixed-col { background: #FAFBFC; }

.field-col {
  width: 130px; min-width: 130px; max-width: 130px;
  display: flex; flex-direction: column; align-items: flex-start; justify-content: center;
  padding: 10px 14px; border-bottom: 1px solid #EBEEF5; border-right: 2px solid #DCDFE6;
  font-size: 13px; flex-shrink: 0; box-sizing: border-box;
}
.header-row .field-col { font-size: 14px; border-bottom: 2px solid #DCDFE6; }
.field-name { font-weight: 600; font-size: 14px; }
.field-type { font-size: 11px; color: #909399; margin-top: 2px; }

/* 时间列 */
.time-col {
  flex: 1 0 56px;
  display: flex; align-items: center; justify-content: center;
  padding: 10px 2px; font-size: 12px; box-sizing: border-box;
  border-bottom: 1px solid #EBEEF5; border-right: 1px solid #F2F6FC;
}
.time-col:last-child { border-right: none; }
.header-row .time-col {
  font-weight: 600; font-size: 13px; padding: 12px 2px;
  background: #FAFAFA; border-bottom: 2px solid #DCDFE6;
}
.time-col.peak { background: #FFF7E6; border-bottom-color: #E6A23C; }

/* 单元格 */
.slot-cell {
  cursor: default; height: 100%; transition: background 0.15s;
  box-sizing: border-box;
}
.slot-cell.booked { background: #FFECEC; }
.slot-cell.free { background: #E8F5E9; cursor: pointer; }
.slot-cell.free:hover { background: #C8E6C9; }
.slot-cell.booked { }
.slot-cell.past { opacity: 0.4; }

.cell-booked { color: #F56C6C; font-weight: 500; font-size: 11px; }
.cell-locked { color: #909399; font-weight: 500; font-size: 11px; }
.cell-child-booked { color: #E6A23C; font-weight: 500; font-size: 10px; }
.cell-free { color: #67C23A; }
.cell-past { color: #DDD; }

/* ──── 子场地行 ──── */
.child-rows { display: block; }
.child-row {
  height: 58px;
  background: #fff;
}
.child-row .field-col { background: #fff; }
.child-row:hover { background: #F5F7FA; }

/* 父场行（有子场地的全场）：浅灰底色 */
.parent-row { background: #F5F6F8; }
.parent-row .fixed-col { background: #F5F6F8; }
.parent-row:hover { background: #EDEFF2; }
.parent-row:hover .fixed-col { background: #EDEFF2; }
.field-price { font-size: 11px; color: #909399; margin-top: 2px; }

.slot-cell.locked { background: #F0F0F0; cursor: pointer; }
.slot-cell.locked:hover { background: #E0E0E0; }

/* ──── 图例 ──── */
.legend {
  display: flex; gap: 20px; padding: 8px 16px; flex-shrink: 0;
  background: rgba(255,255,255,0.5); border-top: 1px solid rgba(0,0,0,0.06);
  font-size: 12px; color: #86868B;
}
.legend span { display: flex; align-items: center; gap: 4px; white-space: nowrap; }
.legend .dot { width: 12px; height: 12px; border-radius: 3px; flex-shrink: 0; }
.dot.free { background: #E8F5E9; border: 1px solid #A5D6A7; }
.dot.locked-dot { background: #F0F0F0; border: 1px solid #C0C4CC; }
.dot.booked { background: #FFECEC; border: 1px solid #FFA8A8; }
.dot.past { background: #F5F5F5; border: 1px solid #DDD; }

.order-preview { background: #F5F7FA; padding: 12px; border-radius: 4px; margin-bottom: 16px; }
.order-preview p { margin: 4px 0; }

.member-card { background: #ECF5FF; border: 1px solid #D9ECFF; border-radius: 8px; padding: 12px; }
.member-card-header { display: flex; align-items: center; gap: 12px; }
.member-card-header p { margin: 2px 0 0; font-size: 12px; color: #909399; }
.info-label { font-size: 11px; color: #909399; }
</style>
