<template>
  <div>
    <div class="page-header">
      <h3><i class="ri-bank-card-line"></i> 卡种管理</h3>
      <el-button type="primary" @click="showAdd"><i class="ri-add-line"></i> 新增卡种</el-button>
    </div>

    <el-table :data="cardTypes" stripe>
      <el-table-column prop="name" label="卡种名称" width="200" />
      <el-table-column prop="category" label="类型" width="90">
        <template #default="{ row }">{{ { times: '次卡', month: '月卡', year: '年卡', custom: '自定义' }[row.category] }}</template>
      </el-table-column>
      <el-table-column prop="total_times" label="次数" width="80">
        <template #default="{ row }">{{ row.total_times || '—' }}</template>
      </el-table-column>
      <el-table-column prop="price" label="售价" width="100">
        <template #default="{ row }">¥{{ row.price }}</template>
      </el-table-column>
      <el-table-column prop="valid_days" label="有效天数" width="90" />
      <el-table-column prop="description" label="描述" />
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button size="small" type="primary" @click="editType(row)">编辑</el-button>
          <el-popconfirm title="确定停用此卡种？" @confirm="deleteType(row.id)">
            <template #reference><el-button size="small" type="danger">停用</el-button></template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog :title="editingId ? '编辑卡种' : '新增卡种'" v-model="showDialog" width="480px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="卡种名称"><el-input v-model="form.name" placeholder="如：羽毛球10次卡" /></el-form-item>
        <el-form-item label="类型">
          <el-select v-model="form.category" style="width:100%">
            <el-option label="次卡" value="times" />
            <el-option label="月卡" value="month" />
            <el-option label="年卡" value="year" />
            <el-option label="自定义" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="form.category === 'times' || form.category === 'custom'" label="总次数">
          <el-input-number v-model="form.total_times" :min="0" style="width:100%" />
        </el-form-item>
        <el-form-item label="售价(元)"><el-input-number v-model="form.price" :min="0" :precision="2" style="width:100%" /></el-form-item>
        <el-form-item label="有效天数"><el-input-number v-model="form.valid_days" :min="1" :max="3650" style="width:100%" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" type="textarea" /></el-form-item>
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
import api from '../api'
import { ElMessage } from 'element-plus'

const cardTypes = ref([])
const showDialog = ref(false)
const editingId = ref(null)
const form = ref({ name: '', category: 'times', total_times: 10, price: 0, valid_days: 30, description: '' })

async function load() {
  try { cardTypes.value = (await api.get('/card-types')).card_types || [] } catch { /* */ }
}

function showAdd() {
  editingId.value = null
  form.value = { name: '', category: 'times', total_times: 10, price: 0, valid_days: 30, description: '' }
  showDialog.value = true
}

function editType(row) {
  editingId.value = row.id
  form.value = { ...row }
  showDialog.value = true
}

async function handleSave() {
  try {
    if (editingId.value) { await api.put(`/card-types/${editingId.value}`, form.value) }
    else { await api.post('/card-types', form.value) }
    showDialog.value = false
    await load()
    ElMessage.success('保存成功')
  } catch { /* */ }
}

async function deleteType(id) {
  try { await api.delete(`/card-types/${id}`); await load(); ElMessage.success('已停用') } catch { /* */ }
}

onMounted(load)
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
</style>
