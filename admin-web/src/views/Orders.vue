<template>
  <div>
    <div class="page-header">
      <h3><i class="ri-bill-line"></i> 订单管理</h3>
      <div class="actions">
        <el-select v-model="filterStatus" placeholder="状态筛选" clearable size="small" style="width:110px" @change="load">
          <el-option label="待支付" value="pending" /><el-option label="已确认" value="confirmed" />
          <el-option label="已签到" value="checked_in" /><el-option label="已取消" value="cancelled" />
        </el-select>
      </div>
    </div>

    <el-table :data="orders" stripe size="small">
      <el-table-column prop="order_no" label="订单号" width="175" />
      <el-table-column label="会员" width="90">
        <template #default="{ row }">{{ row.name || '散客' }}</template>
      </el-table-column>
      <el-table-column label="手机号" width="120">
        <template #default="{ row }">{{ row.phone || '—' }}</template>
      </el-table-column>
      <el-table-column label="类型" width="60">
        <template #default="{ row }">{{ { field_book: '场地', walk_in: '散客', card_recharge: '办卡' }[row.order_type] }}</template>
      </el-table-column>
      <el-table-column label="消费时间" width="155">
        <template #default="{ row }">{{ row.created_at?.slice(0,16)?.replace('T',' ') }}</template>
      </el-table-column>
      <el-table-column prop="paid_amount" label="金额" width="80">
        <template #default="{ row }">¥{{ row.paid_amount?.toFixed(2) }}</template>
      </el-table-column>
      <el-table-column label="状态" width="80">
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

onMounted(() => {
  load()
  timer = setInterval(load, 5000)
})
onUnmounted(() => { clearInterval(timer) })
watch(() => venueStore.currentId, () => { load() })
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.actions { display: flex; gap: 10px; }
</style>
