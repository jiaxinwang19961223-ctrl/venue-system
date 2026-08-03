<template>
  <div class="orders-page">
    <div class="page-header">
      <h3><i class="ri-bill-line"></i> 订单管理</h3>
      <div class="actions" v-if="activeTab === 'orders'">
        <el-select v-model="filterStatus" placeholder="全部状态" clearable size="small" style="width:110px" @change="load">
          <el-option label="待支付" value="pending" /><el-option label="已确认" value="confirmed" />
          <el-option label="已签到" value="checked_in" /><el-option label="已取消" value="cancelled" />
        </el-select>
      </div>
    </div>

    <el-tabs v-model="activeTab" @tab-change="onTabChange">
      <!-- ──── 订单列表 ──── -->
      <el-tab-pane label="订单" name="orders">
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
            <template #default="{ row }"><span :style="{ color: row.status === 'refunded' ? '#67C23A' : '#F56C6C' }">
  {{ row.status === 'refunded' ? '+' : '-' }}¥{{ Math.abs(row.paid_amount || 0).toFixed(2) }}
</span></template>
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
        <div style="display:flex;justify-content:center;margin-top:16px" v-if="total > pageSize">
          <el-pagination v-model:current-page="page" :page-size="pageSize" :total="total" layout="prev, pager, next" background small @current-change="load" />
        </div>
      </el-tab-pane>

      <!-- ──── 修改记录 ──── -->
      <el-tab-pane label="修改记录" name="logs">
        <el-table :data="logs" stripe size="small" style="width:100%">
          <el-table-column label="时间" width="170">
            <template #default="{ row }">{{ row.created_at?.slice(0,16)?.replace('T',' ') }}</template>
          </el-table-column>
          <el-table-column prop="member_name" label="会员" width="100" />
          <el-table-column label="操作类型" width="100">
            <template #default="{ row }">
              <el-tag size="small" :type="row.field==='删除'?'danger':''">{{ { end_date:'有效期修改', 删除:'删除会员', 报名:'报名' }[row.field] || row.field }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="旧值 → 新值" width="240">
            <template #default="{ row }">
              <span style="color:#909399">{{ row.old_value }}</span>
              <span style="margin:0 6px">→</span>
              <span style="color:#409EFF;font-weight:500">{{ row.new_value }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="user_name" label="操作人" width="100" />
          <el-table-column prop="remark" label="备注" min-width="150" />
        </el-table>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { getOrders } from '../api'
import api from '../api'
import { useVenueStore } from '../stores/venue'

const venueStore = useVenueStore()
const orders = ref([])
const logs = ref([])
const filterStatus = ref('')
const activeTab = ref('orders')
const page = ref(1)
const pageSize = ref(15)
const total = ref(0)
let timer = null

async function load() {
  try {
    const res = await getOrders({
      status: filterStatus.value || undefined,
      venue_id: venueStore.currentId,
      page: page.value,
      page_size: pageSize.value,
    })
    orders.value = res.orders || []
    total.value = res.total || 0
  } catch { /* */ }
}

async function loadLogs() {
  try {
    const [cardRes, memberRes] = await Promise.all([
      api.get('/members/card-logs', { params: { limit: 200 } }),
      api.get('/members/logs', { params: { limit: 200 } }),
    ])
    const cardLogs = (cardRes.logs || []).map(l => ({ ...l, _type: 'card' }))
    const memberLogs = (memberRes.logs || []).map(l => ({ ...l, _type: 'member' }))
    logs.value = [...cardLogs, ...memberLogs].sort((a, b) => (b.created_at || '').localeCompare(a.created_at || ''))
  } catch { /* */ }
}

function onTabChange(tab) {
  if (tab === 'logs') loadLogs()
}

function statusType(s) { return { pending: 'info', paid: 'warning', confirmed: 'success', checked_in: '', cancelled: 'danger', refunded: 'success' }[s] || '' }
function statusLabel(s) { return { pending: '待支付', paid: '已支付', confirmed: '已确认', checked_in: '已签到', cancelled: '已取消', refunded: '已退款' }[s] || s }

onMounted(() => { load(); timer = setInterval(load, 10000) })
onUnmounted(() => { clearInterval(timer) })
watch(() => venueStore.currentId, () => { load() })
</script>

<style scoped>
.orders-page { width: 100%; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.actions { display: flex; gap: 10px; }
:deep(.order-row) { border-bottom: 1px solid #EBEEF5; }
:deep(.el-tabs__header) { margin-bottom: 12px; }
</style>
