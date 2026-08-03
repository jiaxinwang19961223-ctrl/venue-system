<template>
  <div>
    <div class="page-header">
      <h3>
        <i class="ri-arrow-left-s-line" style="cursor:pointer" @click="$router.back()"></i>
        {{ venue?.name || '场地列表' }}
      </h3>
      <el-tag v-if="venue" :type="venue.status === 'open' ? 'success' : 'info'">
        {{ venue.status === 'open' ? '营业中' : '休息中' }}
      </el-tag>
    </div>

    <div class="venue-meta" v-if="venue">
      <span><i class="ri-map-pin-line"></i> {{ venue.address || '地址待完善' }}</span>
      <span><i class="ri-time-line"></i> {{ venue.business_hours || '09:00-22:00' }}</span>
    </div>

    <el-row :gutter="16">
      <el-col :span="8" v-for="f in fields" :key="f.id">
        <el-card shadow="hover" class="field-card">
          <el-tag size="small" :type="typeColor(f.field_type)">{{ typeLabel(f.field_type) }}</el-tag>
          <div class="field-name">{{ f.name }}</div>
          <div class="field-price">
            <span class="price-num">¥{{ f.price_per_hour }}</span>
            <span class="price-unit">/小时</span>
          </div>
          <div class="field-meta" v-if="f.capacity">可容纳 {{ f.capacity }} 人</div>
          <el-button type="primary" style="width:100%;margin-top:12px"
            @click="$router.push(`/book/${venueId}/${f.id}`)">
            立即预订
          </el-button>
        </el-card>
      </el-col>
    </el-row>

    <el-empty v-if="!loading && fields.length === 0" description="该球馆暂无可用场地" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getVenue } from '../api'

const route = useRoute()
const venueId = route.params.venueId
const venue = ref(null)
const fields = ref([])
const loading = ref(true)

const fieldTypeMap = {
  badminton: '羽毛球', basketball: '篮球', pingpong: '乒乓球',
  tennis: '网球', football: '足球', swimming: '游泳', fitness: '健身', other: '其他',
}

function typeLabel(t) { return fieldTypeMap[t] || t }
function typeColor(t) {
  const m = { badminton: 'success', basketball: 'warning', pingpong: 'danger', tennis: 'info' }
  return m[t] || ''
}

onMounted(async () => {
  loading.value = true
  try {
    const res = await getVenue(venueId)
    venue.value = res
    fields.value = res.fields || []
  } catch { /* */ }
  finally { loading.value = false }
})
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.page-header h3 {
  margin: 0;
  font-size: 20px;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 4px;
}

.venue-meta {
  display: flex;
  gap: 20px;
  font-size: 13px;
  color: #909399;
  margin-bottom: 20px;
}

.field-card {
  text-align: center;
  margin-bottom: 16px;
}
.field-name {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 12px 0 8px;
}
.field-price {
  margin-bottom: 4px;
}
.price-num {
  font-size: 24px;
  font-weight: 700;
  color: #E6A23C;
}
.price-unit {
  font-size: 13px;
  color: #909399;
}
.field-meta {
  font-size: 12px;
  color: #C0C4CC;
}
</style>
