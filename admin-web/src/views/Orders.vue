<template>
  <div class="orders-page">
    <div class="page-header">
      <h3><i class="ri-bill-line"></i> 订单管理</h3>
      <div class="actions">
        <el-select v-model="filterStatus" placeholder="全部状态" clearable size="small" style="width:110px" @change="load">
          <el-option label="待支付" value="pending" /><el-option label="已确认" value="confirmed" />
          <el-option label="已签到" value="checked_in" /><el-option label="已取消" value="cancelled" />
        </el-select>
      </div>
    </div>

    <el-table :data="orders" stripe size="small" style="width:100%" row-class-name="order-row">
      <el-table-column prop="order_no" label="订单号" min-width="170" resizable />
      <el-table-column label="会员" min-width="90" resizable>
        <template #default="{ row }">{{ row.name || '散客' }}</template>
      </el-table-column>
      <el-table-column label="手机号" min-width="120" resizable>
        <template #default="{ row }">{{ row.phone || '—' }}</template>
      </el-table-column>
      <el-table-column label="类型" min-width="60" resizable>
        <template #default="{ row }">{{ { field_book: '场地', walk_in: '散客', card_recharge: '办卡' }[row.order_type] }}</template>
      </el-table-column>
      <el-table-column label="消费时间" min-width="155" resizable>
        <template #default="{ row }">{{ row.created_at?.slice(0,16)?.replace('T',' ') }}</template>
      </el-table-column>
      <el-table-column label="金额" min-width="80" resizable>
        <template #default="{ row }"><strong>¥{{ row.paid_amount?.toFixed(2) }}</strong></template>
      </el-table-column>
      <el-table-column label="支付" min-width="70" resizable>
        <template #default="{ row }">{{ { wechat:'微信',cash:'现金',card:'会员卡' }[row.payment_method] || row.payment_method }}</template>
      </el-table-column>
      <el-table-column label="状态" min-width="80" resizable>
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { getOrders } from '../api'
import { useVenueStore } from '../stores/venue'

const venueStore = useVenueStore()
const orders = ref([])
const filterStatus = ref('')
let timer = null

async function load() {
  try {
    orders.value = (await getOrders({ status: filterStatus.value || undefined, venue_id: venueStore.currentId })).orders || []
  } catch { /* */ }
}

function statusType(s) { return { pending: 'info', paid: 'warning', confirmed: 'success', checked_in: '', cancelled: 'danger' }[s] || '' }
function statusLabel(s) { return { pending: '待支付', paid: '已支付', confirmed: '已确认', checked_in: '已签到', cancelled: '已取消' }[s] || s }

onMounted(() => { load(); timer = setInterval(load, 5000) })
onUnmounted(() => { clearInterval(timer) })
watch(() => venueStore.currentId, () => { load() })
</script>

<style scoped>
.orders-page { width: 100%; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.actions { display: flex; gap: 10px; }
:deep(.order-row) { border-bottom: 1px solid #EBEEF5; }
</style>
