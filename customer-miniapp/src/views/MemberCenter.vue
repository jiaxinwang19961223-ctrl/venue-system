<template>
  <div>
    <div class="page-header">
      <h3><i class="ri-vip-crown-fill"></i> 会员中心</h3>
    </div>

    <!-- 未办理会员 -->
    <el-card v-if="!loading && !member" class="register-card">
      <el-empty description="您还未办理会员" :image-size="80" />
      <el-form :model="form" label-width="80px" style="max-width:400px;margin:0 auto">
        <el-form-item label="选择球馆">
          <el-select v-model="form.venue_id" placeholder="请选择球馆" style="width:100%">
            <el-option v-for="v in venueStore.venues" :key="v.id" :label="v.name" :value="v.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="form.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="性别">
          <el-radio-group v-model="form.gender">
            <el-radio value="男">男</el-radio>
            <el-radio value="女">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="生日">
          <el-date-picker v-model="form.birthday" type="date" value-format="YYYY-MM-DD" placeholder="选填" style="width:100%" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="registering" @click="doRegister" style="width:100%">
            立即办理
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 已办理会员 -->
    <template v-if="member">
      <!-- 会员信息卡 -->
      <el-card class="member-card">
        <div class="member-header">
          <div class="member-avatar">
            <i class="ri-user-3-fill"></i>
          </div>
          <div class="member-info">
            <div class="member-name">{{ member.name }}
              <el-tag size="small" v-if="member.level_name">{{ member.level_name }}</el-tag>
            </div>
            <div class="member-meta">
              {{ member.phone }} · {{ member.gender || '未设置' }}
              · {{ member.venue_name }}
            </div>
          </div>
        </div>
        <el-divider />
        <el-row :gutter="16">
          <el-col :span="6">
            <div class="stat-item">
              <div class="stat-val">¥{{ (member.balance || 0).toFixed(2) }}</div>
              <div class="stat-label">余额</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-item">
              <div class="stat-val">¥{{ (member.total_recharge || 0).toFixed(2) }}</div>
              <div class="stat-label">累计充值</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-item">
              <div class="stat-val">¥{{ (member.total_consumption || 0).toFixed(2) }}</div>
              <div class="stat-label">累计消费</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-item">
              <div class="stat-val">{{ member.points || 0 }}</div>
              <div class="stat-label">积分</div>
            </div>
          </el-col>
        </el-row>
      </el-card>

      <!-- 我的会员卡 -->
      <div class="section-title">
        <span>我的会员卡</span>
      </div>
      <el-row :gutter="16">
        <el-col :span="8" v-for="c in member.cards" :key="c.id">
          <el-card shadow="hover" class="card-card" :class="{ 'card-expired': !c.is_active || isExpired(c) }">
            <div class="card-type-tag">
              <el-tag size="small" :type="cardTypeColor(c.card_type)">{{ cardTypeLabel(c.card_type) }}</el-tag>
            </div>
            <div class="card-title">{{ cardTypeLabel(c.card_type) }}卡</div>
            <div class="card-detail" v-if="c.card_type === 'stored'">
              储值 ¥{{ (c.stored_value || 0).toFixed(0) }} · 已用 ¥{{ (c.used_value || 0).toFixed(0) }}
            </div>
            <div class="card-detail" v-else>
              {{ c.used_times || 0 }} / {{ c.total_times || 0 }} 次
            </div>
            <div class="card-expiry">
              有效期至 {{ c.end_date || '永久' }}
              <el-tag v-if="!c.is_active" type="danger" size="small">已失效</el-tag>
            </div>
          </el-card>
        </el-col>
        <el-col :span="8" v-if="member.cards.length === 0">
          <el-empty description="暂无会员卡" :image-size="60" />
        </el-col>
      </el-row>

      <!-- 选购卡种 -->
      <div class="section-title">
        <span>选购卡种</span>
      </div>
      <el-row :gutter="16">
        <el-col :span="8" v-for="ct in cardTypes" :key="ct.id">
          <el-card shadow="hover" class="ct-card">
            <div class="ct-name">{{ ct.name }}</div>
            <div class="ct-price">¥{{ ct.price }}</div>
            <div class="ct-meta">
              <span v-if="ct.category === 'stored'">储值 {{ ct.total_times }} 元</span>
              <span v-else>{{ ct.total_times }} 次</span>
              <span v-if="ct.valid_days"> · {{ ct.valid_days }}天有效</span>
            </div>
            <div class="ct-desc" v-if="ct.description">{{ ct.description }}</div>
            <el-button type="primary" size="small" style="width:100%;margin-top:8px"
              :loading="buyingId === ct.id" @click="doBuy(ct)">
              立即购买
            </el-button>
          </el-card>
        </el-col>
      </el-row>
      <el-empty v-if="cardTypes.length === 0" description="暂无可购卡种" :image-size="60" />
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getMyMember, registerMember, buyCard, getCardTypes } from '../api'
import { useUserStore } from '../stores/user'
import { useVenueStore } from '../stores/venue'

const userStore = useUserStore()
const venueStore = useVenueStore()

const member = ref(null)
const cardTypes = ref([])
const loading = ref(true)
const registering = ref(false)
const buyingId = ref(null)

const form = ref({
  venue_id: venueStore.currentId || '',
  name: userStore.user?.name || '',
  gender: '男',
  birthday: '',
})

const cardTypeLabelMap = { stored: '储值', month: '月卡', season: '季卡', year: '年卡', times: '次卡', custom: '自定义' }
function cardTypeLabel(t) { return cardTypeLabelMap[t] || t }
function cardTypeColor(t) {
  return t === 'stored' ? 'warning' : t === 'year' ? 'success' : t === 'season' ? '' : 'info'
}
function isExpired(c) {
  if (!c.end_date) return false
  return new Date(c.end_date) < new Date()
}

async function loadMember() {
  loading.value = true
  try {
    const res = await getMyMember()
    member.value = res
  } catch (e) {
    member.value = null
  }
  try {
    const res = await getCardTypes()
    cardTypes.value = res.card_types || []
  } catch { /* */ }
  finally { loading.value = false }
}

async function doRegister() {
  if (!form.value.venue_id) return ElMessage.warning('请选择球馆')
  if (!form.value.name) return ElMessage.warning('请输入姓名')
  registering.value = true
  try {
    await registerMember({ ...form.value })
    ElMessage.success('会员办理成功')
    loadMember()
  } catch { /* */ }
  finally { registering.value = false }
}

async function doBuy(ct) {
  try {
    await ElMessageBox.confirm(`确认购买「${ct.name}」？金额：¥${ct.price}`, '购买会员卡', { type: 'info' })
  } catch { return }
  buyingId.value = ct.id
  try {
    const res = await buyCard({ card_type_id: ct.id })
    ElMessage.success(`购卡成功！订单号：${res.order_no}`)
    loadMember()
  } catch { /* */ }
  finally { buyingId.value = null }
}

onMounted(() => {
  venueStore.load()
  loadMember()
})
</script>

<style scoped>
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

.register-card {
  margin-bottom: 24px;
}

.member-card {
  margin-bottom: 24px;
}
.member-header {
  display: flex;
  align-items: center;
  gap: 16px;
}
.member-avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: #ECF5FF;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: #409EFF;
}
.member-name {
  font-size: 18px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}
.member-meta {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

.stat-item { text-align: center; }
.stat-val { font-size: 20px; font-weight: 700; color: #303133; }
.stat-label { font-size: 12px; color: #909399; margin-top: 4px; }

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 24px 0 12px;
}

.card-card { margin-bottom: 16px; }
.card-expired { opacity: 0.5; }
.card-type-tag { margin-bottom: 8px; }
.card-title { font-size: 16px; font-weight: 600; margin-bottom: 4px; }
.card-detail { font-size: 13px; color: #606266; margin-bottom: 4px; }
.card-expiry { font-size: 12px; color: #909399; display: flex; align-items: center; gap: 8px; }

.ct-card { margin-bottom: 16px; text-align: center; }
.ct-name { font-size: 18px; font-weight: 600; color: #303133; }
.ct-price { font-size: 28px; font-weight: 700; color: #E6A23C; margin: 4px 0; }
.ct-meta { font-size: 12px; color: #909399; }
.ct-desc { font-size: 12px; color: #C0C4CC; margin-top: 4px; }
</style>
