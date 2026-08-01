<template>
  <div>
    <h3><i class="ri-dashboard-line"></i> 数据概览</h3>
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat">
            <i class="ri-building-2-line stat-icon" style="color:#409EFF"></i>
            <span class="num">{{ venues.length }}</span>
            <span class="label">球馆</span>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat">
            <i class="ri-vip-crown-line stat-icon" style="color:#67C23A"></i>
            <span class="num">{{ members.length }}</span>
            <span class="label">会员</span>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat">
            <i class="ri-bill-line stat-icon" style="color:#E6A23C"></i>
            <span class="num">{{ orders.length }}</span>
            <span class="label">今日订单</span>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat">
            <i class="ri-football-line stat-icon" style="color:#F56C6C"></i>
            <span class="num">{{ fields }}</span>
            <span class="label">场地</span>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getVenues, getMembers, getOrders } from '../api'

const venues = ref([])
const members = ref([])
const orders = ref([])
const fields = ref(0)

onMounted(async () => {
  try {
    const [v, m, o] = await Promise.all([
      getVenues(),
      getMembers(),
      getOrders(),
    ])
    venues.value = v.venues || []
    members.value = m.members || []
    orders.value = o.orders || []
    fields.value = venues.value.reduce((sum, v) => sum + (v.fields?.length || 0), 0)
  } catch { /* */ }
})
</script>

<style scoped>
.stat { text-align: center; padding: 16px 0; }
.stat-icon { font-size: 28px; display: block; margin-bottom: 8px; }
.stat .num { font-size: 32px; font-weight: bold; color: #303133; display: block; }
.stat .label { color: #909399; font-size: 14px; }
</style>
