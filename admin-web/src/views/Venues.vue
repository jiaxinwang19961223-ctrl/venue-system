<template>
  <div>
    <div class="page-header">
      <h3>场馆管理</h3>
      <el-button type="primary" @click="showDialog = true" v-if="canManage">新增球馆</el-button>
    </div>
    <el-table :data="venues" stripe>
      <el-table-column prop="name" label="球馆名称" />
      <el-table-column prop="address" label="地址" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }"><el-tag :type="row.status === 'open' ? 'success' : 'danger'">{{ row.status === 'open' ? '营业中' : '歇业' }}</el-tag></template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button size="small" @click="$router.push(`/fields/${row.id}`)">场地</el-button>
          <el-button size="small" type="primary" @click="editVenue(row)">编辑</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 新增/编辑对话框 -->
    <el-dialog :title="editingId ? '编辑球馆' : '新增球馆'" v-model="showDialog" width="500px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="地址"><el-input v-model="form.address" /></el-form-item>
        <el-form-item label="电话"><el-input v-model="form.phone" /></el-form-item>
        <el-form-item label="所在区"><el-input v-model="form.district" placeholder="一照多址合规：同区" /></el-form-item>
        <el-form-item label="营业时间"><el-input v-model="form.business_hours" placeholder="09:00-22:00" /></el-form-item>
        <el-form-item label="简介"><el-input v-model="form.description" type="textarea" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getVenues, getVenue, createVenue, updateVenue } from '../api'
import { useUserStore } from '../stores/user'
import { ElMessage } from 'element-plus'

const store = useUserStore()
const canManage = store.hasRole('core_management', 'manager')
const venues = ref([])
const showDialog = ref(false)
const editingId = ref(null)
const form = ref({ name: '', address: '', phone: '', district: '', business_hours: '09:00-22:00', description: '' })

async function load() {
  try { venues.value = (await getVenues()).venues || [] } catch { /* */ }
}

onMounted(load)

async function editVenue(venue) {
  editingId.value = venue.id
  // 先用表格数据填充，立即弹窗
  form.value = {
    name: venue.name || '',
    address: venue.address || '',
    phone: '',
    district: '',
    business_hours: '09:00-22:00',
    description: '',
  }
  showDialog.value = true
  // 再异步加载完整详情
  try {
    const detail = await getVenue(venue.id)
    if (editingId.value === venue.id) {
      form.value = {
        name: detail.name || venue.name || '',
        address: detail.address || venue.address || '',
        phone: detail.phone || '',
        district: detail.district || '',
        business_hours: detail.business_hours || '09:00-22:00',
        description: detail.description || '',
      }
    }
  } catch { /* 表格数据已可用 */ }
}

async function handleSave() {
  if (!form.value.name) { ElMessage.warning('请输入球馆名称'); return }
  try {
    if (editingId.value) {
      await updateVenue(editingId.value, form.value)
    } else {
      await createVenue(form.value)
    }
    showDialog.value = false
    editingId.value = null
    form.value = { name: '', address: '', phone: '', district: '', business_hours: '09:00-22:00', description: '' }
    await load()
    ElMessage.success('保存成功')
  } catch { /* */ }
}
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
</style>
