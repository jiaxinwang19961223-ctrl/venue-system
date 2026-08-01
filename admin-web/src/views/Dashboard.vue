<template>
  <div>
    <h3><i class="ri-dashboard-line"></i> 数据概览</h3>
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover" @click="$router.push('/venues')" class="clickable">
          <div class="stat">
            <i class="ri-building-2-line stat-icon" style="color:#409EFF"></i>
            <span class="num">{{ venues.length }}</span>
            <span class="label">球馆 · 管理</span>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" @click="$router.push('/face-checkin')" class="clickable">
          <div class="stat">
            <i class="ri-camera-line stat-icon" style="color:#409EFF"></i>
            <span class="num">{{ members.length }}</span>
            <span class="label">会员 · 签到</span>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" @click="$router.push('/court-board')" class="clickable">
          <div class="stat">
            <i class="ri-grid-line stat-icon" style="color:#E6A23C"></i>
            <span class="num">{{ orders.length }}</span>
            <span class="label">订单 · 看板</span>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" @click="$router.push('/members')" class="clickable">
          <div class="stat">
            <i class="ri-vip-crown-line stat-icon" style="color:#67C23A"></i>
            <span class="num">{{ fields }}</span>
            <span class="label">场地 · 会员</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 当前场馆信息 -->
    <el-card style="margin-top:20px">
      <template #header>
        <span><i class="ri-building-2-line"></i> 当前场馆：{{ venueStore.currentName || '未选择' }}</span>
        <el-button size="small" type="primary" style="float:right" @click="$router.push('/venues')">管理场馆</el-button>
      </template>
      <el-descriptions :column="3" size="small">
        <el-descriptions-item label="场地数">{{ fields }}</el-descriptions-item>
        <el-descriptions-item label="会员数">{{ members.length }}</el-descriptions-item>
        <el-descriptions-item label="今日订单">{{ orders.length }}</el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getVenues, getMembers, getOrders, getFields } from '../api'
import { useVenueStore } from '../stores/venue'

const venueStore = useVenueStore()
const venues = ref([])
const members = ref([])
const orders = ref([])
const fields = ref(0)

onMounted(async () => {
  try {
    const [v, m, o] = await Promise.all([
      getVenues(),
      getMembers({ venue_id: venueStore.currentId }),
      getOrders({ venue_id: venueStore.currentId }),
    ])
    venues.value = v.venues || []
    members.value = m.members || []
    orders.value = o.orders || []
    if (venueStore.currentId) {
      try { const f = await getFields(venueStore.currentId); fields.value = (f.fields || []).length } catch { /* */ }
    }
  } catch { /* */ }
})
</script>

<style scoped>
.stat { text-align: center; padding: 16px 0; }
.stat-icon { font-size: 28px; display: block; margin-bottom: 8px; }
.stat .num { font-size: 32px; font-weight: bold; color: #303133; display: block; }
.stat .label { color: #909399; font-size: 14px; }
.clickable { cursor: pointer; transition: transform 0.2s; }
.clickable:hover { transform: translateY(-2px); }
</style>
