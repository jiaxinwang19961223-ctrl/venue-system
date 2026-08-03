<template>
  <div>
    <div class="page-header">
      <h3><i class="ri-file-list-3-line"></i> 我的订单</h3>
    </div>

    <el-table :data="orders" stripe size="small" v-loading="loading" empty-text="暂无订单">
      <el-table-column prop="order_no" label="订单号" width="180" />
      <el-table-column label="类型" width="90">
        <template #default="{ row }">
          <el-tag size="small" :type="orderTypeTag(row.order_type)">{{ orderTypeLabel(row.order_type) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="venue_name" label="球馆" width="120" />
      <el-table-column prop="field_name" label="场地" width="80" />
      <el-table-column label="日期" width="110">
        <template #default="{ row }">{{ row.book_date || '-' }}</template>
      </el-table-column>
      <el-table-column label="时段" width="120">
        <template #default="{ row }">
          {{ row.start_time && row.end_time ? row.start_time + ' - ' + row.end_time : '-' }}
        </template>
      </el-table-column>
      <el-table-column label="金额" width="90">
        <template #default="{ row }">¥{{ (row.paid_amount || row.original_amount || 0).toFixed(2) }}</template>
      </el-table-column>
      <el-table-column label="支付方式" width="80">
        <template #default="{ row }">{{ row.payment_method === 'wechat' ? '微信' : (row.payment_method || '-') }}</template>
      </el-table-column>
      <el-table-column label="状态" width="80">
        <template #default="{ row }">
          <el-tag size="small" :type="statusType(row.status)">{{ statusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160">
        <template #default="{ row }">
          <div class="btn-row" v-if="row.order_type === 'field_book'">
            <el-button v-if="row.status === 'pending'" type="primary" size="small" @click="doPay(row)">支付</el-button>
            <el-button
              v-if="row.status === 'pending' || row.status === 'paid'"
              type="danger" size="small" @click="doCancel(row)">取消</el-button>
          </div>
          <span v-else style="color:#C0C4CC;font-size:12px">-</span>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getOrders, updateOrderStatus } from '../api'

const orders = ref([])
const loading = ref(false)
let timer = null

const orderTypeMap = { field_book: '订场', walk_in: '散客', card_recharge: '办卡', course_book: '课程' }
const statusMap = { pending: '待支付', paid: '已支付', confirmed: '已确认', checked_in: '已签到', cancelled: '已取消', refunded: '已退款' }
const statusTypeMap = { pending: 'warning', paid: 'success', confirmed: '', checked_in: 'success', cancelled: 'info', refunded: 'info' }

function orderTypeLabel(t) { return orderTypeMap[t] || t }
function orderTypeTag(t) { return t === 'field_book' ? 'success' : t === 'card_recharge' ? 'warning' : 'info' }
function statusLabel(s) { return statusMap[s] || s }
function statusType(s) { return statusTypeMap[s] || 'info' }

async function load() {
  try {
    const res = await getOrders()
    orders.value = res.orders || []
  } catch { /* */ }
}

async function doPay(row) {
  try {
    await updateOrderStatus(row.id, 'paid')
    ElMessage.success('支付成功')
    load()
  } catch { /* */ }
}

async function doCancel(row) {
  try {
    await ElMessageBox.confirm('确定取消该订单？', '提示', { type: 'warning' })
  } catch { return }
  try {
    await updateOrderStatus(row.id, 'cancelled')
    ElMessage.success('已取消')
    load()
  } catch { /* */ }
}

onMounted(() => {
  load()
  timer = setInterval(load, 5000)
})

onUnmounted(() => clearInterval(timer))
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.page-header h3 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}
.btn-row {
  display: flex;
  gap: 4px;
}
</style>
