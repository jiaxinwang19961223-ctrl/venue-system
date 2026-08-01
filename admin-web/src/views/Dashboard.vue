<template>
  <div class="dashboard">
    <!-- 场馆卡片——每家独立显示 -->
    <div v-for="v in venueStats" :key="v.id" class="venue-section">
      <div class="venue-header">
        <h3><i class="ri-building-2-line"></i> {{ v.name }}</h3>
        <el-tag :type="v.status === 'open' ? 'success' : 'danger'" size="small">{{ v.status === 'open' ? '营业中' : '歇业' }}</el-tag>
      </div>

      <!-- 仪表盘数据 -->
      <el-row :gutter="16">
        <el-col :span="6">
          <div class="metric-card">
            <div class="metric-icon" style="background:#ECF5FF"><i class="ri-football-line" style="color:#409EFF"></i></div>
            <div class="metric-body">
              <span class="metric-val">{{ v.field_count }}</span>
              <span class="metric-label">场地</span>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="metric-card">
            <div class="metric-icon" style="background:#F0F9EB"><i class="ri-vip-crown-line" style="color:#67C23A"></i></div>
            <div class="metric-body">
              <span class="metric-val">{{ v.member_count }}</span>
              <span class="metric-label">会员</span>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="metric-card">
            <div class="metric-icon" style="background:#FFF7E6"><i class="ri-bill-line" style="color:#E6A23C"></i></div>
            <div class="metric-body">
              <span class="metric-val">{{ v.order_today }}</span>
              <span class="metric-label">今日订单</span>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="metric-card">
            <div class="metric-icon" style="background:#FEF0F0"><i class="ri-money-dollar-circle-line" style="color:#F56C6C"></i></div>
            <div class="metric-body">
              <span class="metric-val">¥{{ v.revenue_today }}</span>
              <span class="metric-label">今日营收</span>
            </div>
          </div>
        </el-col>
      </el-row>

      <!-- 场地占用条 -->
      <div class="usage-bar" v-if="v.field_count > 0">
        <div class="usage-title">
          <span>场地占用</span>
          <span>{{ v.booked_fields }}/{{ v.field_count }} 已订</span>
        </div>
        <el-progress
          :percentage="v.field_count ? Math.round(v.booked_fields / v.field_count * 100) : 0"
          :color="v.booked_fields === v.field_count ? '#F56C6C' : '#409EFF'"
          :stroke-width="14"
        />
      </div>

      <!-- 今日时段一览 -->
      <div class="today-slots" v-if="v.today_bookings.length">
        <div class="usage-title"><span>今日预订</span></div>
        <div class="slot-tags">
          <el-tag
            v-for="b in v.today_bookings.slice(0, 8)"
            :key="b.id"
            :type="b.status === 'pending' ? 'info' : ''"
            size="small"
            style="margin:2px"
          >
            {{ b.field_name || '场地' }} {{ b.start_time }}
          </el-tag>
          <el-tag v-if="v.today_bookings.length > 8" size="small" type="info" style="margin:2px">
            +{{ v.today_bookings.length - 8 }} 条
          </el-tag>
        </div>
      </div>
    </div>

    <!-- 无场馆 -->
    <el-empty v-if="!venueStats.length" description="暂无场馆数据">
      <el-button type="primary" @click="$router.push('/venues')">去创建场馆</el-button>
    </el-empty>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { getVenues, getFields, getMembers, getOrders } from '../api'
import { useVenueStore } from '../stores/venue'

const venueStore = useVenueStore()
const venueStats = ref([])

async function load() {
  try {
    const vRes = await getVenues()
    const allVenues = vRes.venues || []

    // 如果选了单店，只显示该店
    const venues = venueStore.currentId
      ? allVenues.filter(v => v.id === venueStore.currentId)
      : allVenues

    const stats = await Promise.all(venues.map(async (v) => {
      let field_count = 0, member_count = 0, order_today = 0, revenue_today = 0
      let booked_fields = 0
      let today_bookings = []

      try {
        const fRes = await getFields(v.id)
        const fields = fRes.fields || []
        field_count = fields.length

        // 今日订单
        const today = new Date().toISOString().slice(0, 10)
        const oRes = await getOrders({ venue_id: v.id, date: today })
        const orders = oRes.orders || []
        order_today = orders.length
        revenue_today = orders.reduce((sum, o) => sum + (o.paid_amount || 0), 0).toFixed(2)
        booked_fields = new Set(orders.filter(o => !['cancelled', 'refunded'].includes(o.status)).map(o => o.field_id)).size

        // 预订标签
        today_bookings = orders.filter(o => o.order_type === 'field_book' && !['cancelled', 'refunded'].includes(o.status)).map(o => ({
          id: o.id, field_name: fields.find(f => f.id === o.field_id)?.name || '', start_time: o.start_time, status: o.status
        }))
      } catch { /* */ }

      try {
        const mRes = await getMembers({ venue_id: v.id })
        member_count = (mRes.members || []).length
      } catch { /* */ }

      return {
        id: v.id, name: v.name, status: v.status || 'open',
        field_count, member_count, order_today, revenue_today,
        booked_fields, today_bookings,
      }
    }))

    venueStats.value = stats
  } catch { /* */ }
}

onMounted(load)
watch(() => venueStore.currentId, load)
</script>

<style scoped>
.dashboard { max-width: 1200px; }
.venue-section {
  background: #fff; border: 1px solid #EBEEF5; border-radius: 8px; padding: 20px; margin-bottom: 20px;
}
.venue-header { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
.venue-header h3 { margin: 0; font-size: 16px; }

.metric-card { display: flex; align-items: center; gap: 12px; padding: 12px; background: #FAFAFA; border-radius: 8px; }
.metric-icon { width: 44px; height: 44px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; }
.metric-body { display: flex; flex-direction: column; }
.metric-val { font-size: 22px; font-weight: 700; color: #303133; }
.metric-label { font-size: 12px; color: #909399; margin-top: 2px; }

.usage-bar { margin-top: 16px; }
.usage-title { display: flex; justify-content: space-between; font-size: 13px; color: #606266; margin-bottom: 8px; }

.today-slots { margin-top: 12px; }
.slot-tags { margin-top: 6px; }
</style>
