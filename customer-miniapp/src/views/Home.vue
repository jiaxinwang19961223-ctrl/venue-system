<template>
  <div>
    <div class="page-header">
      <h3><i class="ri-home-4-fill"></i> 首页</h3>
    </div>

    <!-- 快捷入口 -->
    <el-row :gutter="16" style="margin-bottom:24px">
      <el-col :span="12">
        <div class="quick-card" @click="goFirstVenue">
          <i class="ri-calendar-check-fill" style="color:#409EFF"></i>
          <div>
            <div class="quick-title">立即订场</div>
            <div class="quick-desc">选择场馆和时段，快速预订</div>
          </div>
          <i class="ri-arrow-right-s-line"></i>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="quick-card" @click="$router.push('/member')">
          <i class="ri-vip-crown-fill" style="color:#E6A23C"></i>
          <div>
            <div class="quick-title">会员中心</div>
            <div class="quick-desc">办理会员，享受优惠</div>
          </div>
          <i class="ri-arrow-right-s-line"></i>
        </div>
      </el-col>
    </el-row>

    <!-- 球馆列表 -->
    <div class="section-title">全部球馆</div>
    <el-row :gutter="16">
      <el-col :span="8" v-for="v in venues" :key="v.id">
        <el-card shadow="hover" class="venue-card" @click="$router.push(`/venues/${v.id}`)">
          <div class="venue-name">{{ v.name }}</div>
          <div class="venue-addr">
            <i class="ri-map-pin-line"></i> {{ v.address || '地址待完善' }}
          </div>
          <div class="venue-info">
            <el-tag :type="v.status === 'open' ? 'success' : 'info'" size="small">
              {{ v.status === 'open' ? '营业中' : '休息中' }}
            </el-tag>
            <span class="venue-hours">{{ v.business_hours || '09:00-22:00' }}</span>
          </div>
          <div class="venue-action">
            <el-button type="primary" size="small">去订场 →</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-empty v-if="!loading && venues.length === 0" description="暂无可订球馆" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getVenues } from '../api'

const router = useRouter()
const venues = ref([])
const loading = ref(true)

onMounted(async () => {
  loading.value = true
  try {
    const res = await getVenues()
    venues.value = res.venues || []
  } catch { /* */ }
  finally { loading.value = false }
})

function goFirstVenue() {
  if (venues.value.length) {
    router.push(`/venues/${venues.value[0].id}`)
  }
}
</script>

<style scoped>
.quick-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  cursor: pointer;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  transition: box-shadow 0.2s;
}
.quick-card:hover {
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
}
.quick-card > i:first-child {
  font-size: 36px;
}
.quick-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}
.quick-desc {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}

.venue-card {
  cursor: pointer;
  margin-bottom: 16px;
}
.venue-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}
.venue-addr {
  font-size: 13px;
  color: #909399;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 4px;
}
.venue-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}
.venue-hours {
  font-size: 12px;
  color: #909399;
}
.venue-action {
  text-align: right;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.page-header h3 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}
</style>
