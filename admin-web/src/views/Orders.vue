<template>
  <div>
    <div class="page-header">
      <h3>订单管理</h3>
      <div class="actions">
        <el-button type="primary" @click="showCreate">快速开单</el-button>
        <el-select v-model="filterStatus" placeholder="状态筛选" clearable style="width:130px" @change="load">
          <el-option label="待支付" value="pending" />
          <el-option label="已支付" value="paid" />
          <el-option label="已确认" value="confirmed" />
          <el-option label="已签到" value="checked_in" />
          <el-option label="已取消" value="cancelled" />
        </el-select>
      </div>
    </div>

    <el-table :data="orders" stripe>
      <el-table-column prop="order_no" label="订单号" width="170" />
      <el-table-column label="会员" width="100">
        <template #default="{ row }">{{ row.name || '散客' }}</template>
      </el-table-column>
      <el-table-column label="手机号" width="120">
        <template #default="{ row }">{{ row.phone || '—' }}</template>
      </el-table-column>
      <el-table-column prop="order_type" label="类型" width="70">
        <template #default="{ row }">{{ { field_book: '场地', walk_in: '散客', card_recharge: '办卡', course_book: '课程' }[row.order_type] }}</template>
      </el-table-column>
      <el-table-column label="消费时间" width="155">
        <template #default="{ row }">{{ row.created_at?.slice(0,16)?.replace('T',' ') }}</template>
      </el-table-column>
      <el-table-column label="时段" width="110">
        <template #default="{ row }">{{ row.start_time ? row.start_time + '-' + row.end_time : '—' }}</template>
      </el-table-column>
      <el-table-column prop="paid_amount" label="金额" width="80">
        <template #default="{ row }">¥{{ row.paid_amount?.toFixed(2) }}</template>
      </el-table-column>
      <el-table-column label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150">
        <template #default="{ row }">
          <el-button v-if="row.status === 'pending'" size="small" type="success" @click="changeStatus(row.id, 'confirmed')">确认</el-button>
          <el-button v-if="row.status === 'confirmed'" size="small" type="warning" @click="changeStatus(row.id, 'checked_in')">签到</el-button>
          <el-button v-if="['pending','paid','confirmed'].includes(row.status)" size="small" type="danger" @click="changeStatus(row.id, 'cancelled')">取消</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 快速开单 -->
    <el-dialog title="快速开单" v-model="showCreateDialog" width="500px">
      <el-form :model="orderForm" label-width="80px">
        <el-form-item label="订单类型">
          <el-select v-model="orderForm.order_type">
            <el-option label="场地预订" value="field_book" />
            <el-option label="散客消费" value="walk_in" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期"><el-date-picker v-model="orderForm.book_date" type="date" value-format="YYYY-MM-DD" /></el-form-item>
        <el-form-item label="开始时间"><el-time-picker v-model="orderForm.start_time" format="HH:mm" value-format="HH:mm" /></el-form-item>
        <el-form-item label="结束时间"><el-time-picker v-model="orderForm.end_time" format="HH:mm" value-format="HH:mm" /></el-form-item>
        <el-form-item label="金额"><el-input-number v-model="orderForm.paid_amount" :min="0" :precision="2" /></el-form-item>
        <el-form-item label="支付方式">
          <el-select v-model="orderForm.payment_method">
            <el-option label="微信" value="wechat" /><el-option label="现金" value="cash" /><el-option label="会员卡" value="card" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注"><el-input v-model="orderForm.remark" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreate">确认开单</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { getOrders, createOrder, updateOrderStatus } from '../api'
import { useVenueStore } from '../stores/venue'
import { ElMessage, ElMessageBox } from 'element-plus'

const venueStore = useVenueStore()
const orders = ref([])
const filterStatus = ref('')
const showCreateDialog = ref(false)

const orderForm = ref({
  venue_id: venueStore.currentId, order_type: 'field_book', book_date: '',
  start_time: '', end_time: '', paid_amount: 0, payment_method: 'wechat', remark: ''
})

async function load() {
  try {
    orders.value = (await getOrders({ status: filterStatus.value || undefined, venue_id: venueStore.currentId })).orders || []
  } catch { /* */ }
}

async function changeStatus(id, status) {
  try {
    await updateOrderStatus(id, status)
    await load()
    ElMessage.success(`已${statusLabel(status)}`)
  } catch { /* */ }
}

function showCreate() { orderForm.value = { venue_id: venueStore.currentId, order_type: 'field_book', book_date: '', start_time: '', end_time: '', paid_amount: 0, payment_method: 'wechat', remark: '' }; showCreateDialog.value = true }

async function handleCreate() {
  try {
    await createOrder(orderForm.value)
    showCreateDialog.value = false
    await load()
    ElMessage.success('开单成功')
  } catch { /* */ }
}

function statusType(s) { return { pending: 'info', paid: 'warning', confirmed: 'success', checked_in: '', cancelled: 'danger', refunded: 'danger' }[s] || '' }
function statusLabel(s) { return { pending: '待支付', paid: '已支付', confirmed: '已确认', checked_in: '已签到', cancelled: '已取消', refunded: '已退款' }[s] || s }

onMounted(load)
watch(() => venueStore.currentId, () => { load() })
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.actions { display: flex; gap: 10px; }
</style>
