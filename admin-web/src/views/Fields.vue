<template>
  <div>
    <el-button @click="$router.back()">← 返回场馆</el-button>
    <div class="page-header"><h3>{{ venueName }} — 场地管理</h3></div>
    <el-table :data="fields" stripe>
      <el-table-column prop="name" label="场地名称" />
      <el-table-column prop="field_type" label="类型" width="100" />
      <el-table-column prop="price_per_hour" label="价格/小时" width="100">
        <template #default="{ row }">¥{{ row.price_per_hour }}</template>
      </el-table-column>
      <el-table-column prop="peak_price_per_hour" label="高峰价" width="100">
        <template #default="{ row }">¥{{ row.peak_price_per_hour || '-' }}</template>
      </el-table-column>
      <el-table-column prop="capacity" label="人数" width="80" />
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getFields, getVenue } from '../api'

const route = useRoute()
const fields = ref([])
const venueName = ref('')

onMounted(async () => {
  try {
    const venue = await getVenue(route.params.venueId)
    venueName.value = venue.name
    const res = await getFields(route.params.venueId)
    fields.value = res.fields || []
  } catch { /* */ }
})
</script>

<style scoped>
.page-header { margin: 16px 0; }
</style>
