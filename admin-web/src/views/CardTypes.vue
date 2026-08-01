<template>
  <div>
    <div class="page-header">
      <h3><i class="ri-bank-card-line"></i> 卡种管理</h3>
      <el-button type="primary" @click="showAdd"><i class="ri-add-line"></i> 新增卡种</el-button>
    </div>

    <!-- 卡片展示 -->
    <el-row :gutter="16">
      <el-col v-for="ct in cardTypes" :key="ct.id" :span="8" style="margin-bottom:16px">
        <el-card shadow="hover" class="card-item">
          <div class="card-header">
            <span class="card-name">{{ ct.name || categoryLabel(ct.category) }}</span>
            <el-tag :type="tagType(ct.category)" size="small">{{ categoryLabel(ct.category) }}</el-tag>
          </div>
          <div class="card-price">¥{{ ct.price }}</div>
          <div class="card-meta">
            <span v-if="ct.category === 'stored' && ct.total_times"><i class="ri-money-dollar-circle-line"></i> 储值¥{{ ct.total_times }}</span>
            <span v-else-if="ct.total_times"><i class="ri-repeat-line"></i> {{ ct.total_times }}次</span>
            <span v-else><i class="ri-infinity-line"></i> 不限次</span>
            <span><i class="ri-time-line"></i> {{ formatValidDays(ct.valid_days) }}</span>
          </div>
          <div class="card-desc" v-if="ct.description">{{ ct.description }}</div>
          <div class="card-actions">
            <el-button size="small" type="primary" @click="editType(ct)">编辑</el-button>
            <el-popconfirm title="停用此卡种？" @confirm="deleteType(ct.id)">
              <template #reference><el-button size="small" type="danger" text>停用</el-button></template>
            </el-popconfirm>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-empty v-if="!cardTypes.length" description="暂无卡种，点击上方按钮创建" />

    <!-- 新增/编辑弹窗 -->
    <el-dialog :title="editingId ? '编辑卡种' : '新增卡种'" v-model="showDialog" width="500px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="卡类型">
          <el-radio-group v-model="form.category">
            <el-radio-button label="stored">储值卡</el-radio-button>
            <el-radio-button label="month">月卡</el-radio-button>
            <el-radio-button label="season">季卡</el-radio-button>
            <el-radio-button label="year">年卡</el-radio-button>
            <el-radio-button label="custom">定制</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="form.category === 'stored' || form.category === 'custom'" label="储值金额">
          <el-input-number v-model="form.total_times" :min="1" :step="100" style="width:100%" controls-position="right" />
        </el-form-item>
        <el-form-item v-else label="售价(元)">
          <el-input-number v-model="form.price" :min="0" :precision="2" style="width:100%" controls-position="right" />
        </el-form-item>
        <el-form-item label="有效期">
          <span v-if="form.category === 'stored'" style="color:#909399">固定3年（1095天）</span>
          <el-select v-else v-model="form.valid_days" style="width:100%">
            <el-option v-for="d in validOptions" :key="d.value" :label="d.label" :value="d.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="2" placeholder="如：限本人使用、周末不可用等" />
        </el-form-item>
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
const form = ref({ category: 'stored', total_times: 500, price: 0, valid_days: 1095, description: '' })

const validOptions = [
  { label: '1个月', value: 30 },
  { label: '3个月', value: 90 },
  { label: '半年', value: 180 },
  { label: '1年', value: 365 },
  { label: '2年', value: 730 },
]

function categoryLabel(c) { return { stored: '储值卡', month: '月卡', season: '季卡', year: '年卡', custom: '定制' }[c] || c }
function tagType(c) { return { stored: 'success', month: '', season: 'warning', year: 'danger', custom: 'info' }[c] || '' }
function formatValidDays(d) {
  if (d >= 365) return `${Math.floor(d/365)}年`
  if (d >= 30) return `${Math.floor(d/30)}个月`
  return `${d}天`
}

async function load() {
  try { cardTypes.value = (await api.get('/card-types')).card_types || [] } catch { /* */ }
}

function showAdd() {
  editingId.value = null
  form.value = { category: 'stored', total_times: 500, price: 0, valid_days: 1095, description: '' }
  showDialog.value = true
}

async function handleSave() {
  const data = { ...form.value }
  // 储值卡/定制：售价 = 储值金额
  if (data.category === 'stored' || data.category === 'custom') {
    data.price = data.total_times
  }
  try {
    if (editingId.value) { await api.put(`/card-types/${editingId.value}`, data) }
    else { await api.post('/card-types', data) }
    showDialog.value = false
    await load()
    ElMessage.success('保存成功')
  } catch { /* */ }
}

function editType(row) {
  editingId.value = row.id
  form.value = { ...row }
  showDialog.value = true
}

async function deleteType(id) {
  try { await api.delete(`/card-types/${id}`); await load(); ElMessage.success('已停用') } catch { /* */ }
}

onMounted(load)
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }

.card-item { cursor: default; }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.card-name { font-weight: 600; font-size: 15px; }
.card-price { font-size: 28px; font-weight: 700; color: #F56C6C; margin: 8px 0; }
.card-price::before { content: '¥'; font-size: 16px; }
.card-meta { display: flex; gap: 16px; font-size: 13px; color: #606266; margin-bottom: 8px; }
.card-meta i { margin-right: 4px; }
.card-desc { font-size: 12px; color: #909399; margin-bottom: 12px; border-top: 1px solid #EBEEF5; padding-top: 8px; }
.card-actions { display: flex; justify-content: flex-end; gap: 8px; border-top: 1px solid #EBEEF5; padding-top: 10px; }
</style>
