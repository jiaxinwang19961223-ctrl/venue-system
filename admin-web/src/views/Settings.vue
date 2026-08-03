<template>
  <div class="settings-page">
    <el-tabs v-model="activeTab" type="border-card">
      <!-- ──── Tab 1: 球馆信息 ──── -->
      <el-tab-pane label="球馆信息" name="venues">
        <div class="tab-header">
          <el-button type="primary" @click="showVenueDialog = true" v-if="canManage">新增球馆</el-button>
        </div>
        <el-table :data="venues" stripe style="font-size:14px">
          <el-table-column prop="name" label="球馆名称" min-width="140" />
          <el-table-column label="所在区" min-width="200">
            <template #default="{ row }">
              <span v-if="row.district" style="font-size:13px;color:#606266">{{ row.district }}</span>
              <span v-else style="color:#C0C4CC">—</span>
            </template>
          </el-table-column>
          <el-table-column prop="address" label="地址" min-width="200" show-overflow-tooltip />
          <el-table-column prop="phone" label="电话" width="140" />
          <el-table-column prop="business_hours" label="营业时间" width="110" align="center" />
          <el-table-column label="状态" width="90" align="center">
            <template #default="{ row }">
              <el-switch :model-value="row.status === 'open'" size="small" @change="(val) => toggleVenueStatus(row, val)" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" align="center">
            <template #default="{ row }">
              <el-button size="small" type="primary" @click="editVenue(row)">编辑</el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 球馆编辑弹窗 -->
        <el-dialog :title="editingVenueId ? '编辑场馆' : '新增场馆'" v-model="showVenueDialog" width="560px" @closed="resetVenueForm">
          <el-form :model="venueForm" label-width="90px">
            <el-row :gutter="16">
              <el-col :span="14"><el-form-item label="场馆名称"><el-input v-model="venueForm.name" /></el-form-item></el-col>
              <el-col :span="10"><el-form-item label="所在地区">
                <el-cascader v-model="venueForm.region" :options="regionData" placeholder="省/市/区" style="width:100%" clearable filterable />
              </el-form-item></el-col>
            </el-row>
            <el-form-item label="详细地址"><el-input v-model="venueForm.address" /></el-form-item>
            <el-row :gutter="16">
              <el-col :span="12"><el-form-item label="电话"><el-input v-model="venueForm.phone" /></el-form-item></el-col>
              <el-col :span="12"><el-form-item label="状态">
                <el-radio-group v-model="venueForm.status"><el-radio value="open">营业中</el-radio><el-radio value="closed">歇业</el-radio></el-radio-group>
              </el-form-item></el-col>
            </el-row>
            <el-form-item label="营业时间">
              <el-row :gutter="8" style="width:100%">
                <el-col :span="10"><el-time-select v-model="venueForm.open_time" start="06:00" step="01:00" end="23:00" style="width:100%" /></el-col>
                <el-col :span="4" style="text-align:center;line-height:32px;color:#909399">至</el-col>
                <el-col :span="10"><el-time-select v-model="venueForm.close_time" start="06:00" step="01:00" end="23:00" style="width:100%" /></el-col>
              </el-row>
            </el-form-item>
            <el-form-item label="简介"><el-input v-model="venueForm.description" type="textarea" rows="2" /></el-form-item>
          </el-form>
          <template #footer><el-button @click="showVenueDialog = false">取消</el-button><el-button type="primary" @click="saveVenue">保存</el-button></template>
        </el-dialog>
      </el-tab-pane>

      <!-- ──── Tab 2: 场地设置 ──── -->
      <el-tab-pane label="场地设置" name="fields">
        <div class="tab-header">
          <span style="color:#909399;font-size:13px">当前场馆：<strong style="color:#303133">{{ venueStore.currentName || '未选择' }}</strong></span>
          <el-button type="primary" @click="showAddField" :disabled="!fieldVenueId">新增场地</el-button>
        </div>

        <el-row :gutter="16" v-if="fieldVenueId">
          <el-col :span="17">
            <el-table :data="displayFields" stripe size="small">
              <el-table-column label="场地名称" min-width="130">
                <template #default="{ row }">
                  <span :style="{ paddingLeft: row._indent ? '20px' : '0' }">{{ row._indent ? '└ ' : '' }}{{ row.name }}</span>
                  <el-tag v-if="row._isParent" size="small" type="warning" effect="plain" style="margin-left:6px">可拆分</el-tag>
                  <el-tag v-if="row._isChild" size="small" type="info" effect="plain" style="margin-left:6px">半场</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="类型" width="80"><template #default="{ row }">{{ fieldTypeLabel(row.field_type) }}</template></el-table-column>
              <el-table-column label="价格/h" width="80"><template #default="{ row }">￥{{ row.price_per_hour }}</template></el-table-column>
              <el-table-column label="时长" width="60"><template #default="{ row }">{{ row.duration || 1 }}h</template></el-table-column>
              <el-table-column label="排序" width="60">
                <template #default="{ row, $index }">
                  <el-button size="small" text :disabled="$index === 0" @click="moveField(row, -1)"><i class="ri-arrow-up-s-line"></i></el-button>
                  <el-button size="small" text :disabled="$index === displayFields.length - 1" @click="moveField(row, 1)"><i class="ri-arrow-down-s-line"></i></el-button>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="120">
                <template #default="{ row }">
                  <el-button size="small" type="primary" @click="editField(row)">编辑</el-button>
                  <el-popconfirm title="删除？" @confirm="doDeleteField(row.id)"><template #reference><el-button size="small" type="danger" text>删除</el-button></template></el-popconfirm>
                </template>
              </el-table-column>
            </el-table>
          </el-col>
          <el-col :span="7">
            <div class="form-panel" v-if="editingFieldId || showFieldForm">
              <el-form :model="fieldForm" label-width="70px" size="small">
                <el-form-item label="名称"><el-input v-model="fieldForm.name" /></el-form-item>
                <el-form-item label="类型">
                  <el-select v-model="fieldForm.field_type" style="width:100%" @change="onFieldTypeChange">
                    <el-option v-for="t in fieldTypes" :key="t.value" :label="t.icon + ' ' + t.label" :value="t.value" />
                  </el-select>
                </el-form-item>
                <el-form-item label="价格/h"><el-input-number v-model="fieldForm.price_per_hour" :min="0" controls-position="right" style="width:100%" /></el-form-item>
                <el-form-item label="高峰价"><el-input-number v-model="fieldForm.peak_price_per_hour" :min="0" controls-position="right" style="width:100%" /></el-form-item>
                <el-form-item label="时长">
                  <el-select v-model="fieldForm.duration" style="width:100%">
                    <el-option v-for="h in [1,2,3]" :key="h" :label="h + ' 小时'" :value="h" />
                  </el-select>
                </el-form-item>
                <el-form-item label="容纳"><el-input-number v-model="fieldForm.capacity" :min="0" controls-position="right" style="width:100%" /></el-form-item>
                <el-form-item label="关系">
                  <el-radio-group v-model="fieldRelation" @change="onFieldRelationChange">
                    <el-radio label="independent">独立</el-radio>
                    <el-radio label="parent">全场(可拆分)</el-radio>
                    <el-radio label="child">半场</el-radio>
                  </el-radio-group>
                </el-form-item>
                <el-form-item v-if="fieldRelation === 'child'" label="所属全场">
                  <el-select v-model="fieldForm.parent_field_id" style="width:100%">
                    <el-option v-for="p in parentCandidates" :key="p.id" :label="p.name" :value="p.id" />
                  </el-select>
                </el-form-item>
                <el-form-item label="排序"><el-input-number v-model="fieldForm.sort_order" :min="0" controls-position="right" style="width:100%" /></el-form-item>
              </el-form>
              <div class="form-actions"><el-button @click="cancelFieldEdit">取消</el-button><el-button type="primary" @click="saveField">保存</el-button></div>
            </div>
            <el-empty v-else description="点击编辑或新增" :image-size="60" />
          </el-col>
        </el-row>
        <el-empty v-if="!fieldVenueId" description="请先选择一个球馆" :image-size="60" />
      </el-tab-pane>

      <!-- ──── Tab 3: 卡种管理 ──── -->
      <el-tab-pane label="卡种管理" name="cards">
        <div class="tab-header">
          <span style="color:#909399;font-size:13px">当前场馆：<strong style="color:#303133">{{ venueStore.currentName || '请先在顶部选择' }}</strong></span>
          <el-button type="primary" @click="showAddCard" :disabled="!venueStore.currentId">新增卡种</el-button>
        </div>
        <el-row :gutter="16">
          <el-col v-for="ct in sortedCardTypes" :key="ct.id" :span="8" style="margin-bottom:16px">
            <el-card shadow="hover">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
                <strong>{{ ct.name || cardCategoryLabel(ct.category) }}</strong>
                <el-tag :type="cardTagType(ct.category)" size="small">{{ cardCategoryLabel(ct.category) }}</el-tag>
              </div>
              <div style="font-size:13px;color:#606266;margin:6px 0">
                <span v-if="ct.category==='stored'">储值卡</span>
                <span v-else>{{ ct.valid_days }}天有效</span>
              </div>
              <div v-if="ct.bonus_amount" style="font-size:12px;color:#E6A23C;margin:4px 0">🎁 赠￥{{ ct.bonus_amount }}</div>
              <div v-if="ct.description" style="font-size:12px;color:#909399;margin:8px 0;padding-top:8px;border-top:1px solid #EBEEF5">{{ ct.description }}</div>
              <div style="display:flex;justify-content:flex-end;gap:8px;margin-top:10px;padding-top:10px;border-top:1px solid #EBEEF5">
                <el-button size="small" type="primary" @click="editCard(ct)">编辑</el-button>
                <el-popconfirm title="停用？" @confirm="deleteCard(ct.id)"><template #reference><el-button size="small" type="danger" text>停用</el-button></template></el-popconfirm>
              </div>
            </el-card>
          </el-col>
        </el-row>
        <el-empty v-if="!sortedCardTypes.length" description="暂无卡种" />

        <el-dialog :title="editingCardId?'编辑卡种':'新增卡种'" v-model="showCardDialog" width="480px">
          <el-form :model="cardForm" label-width="80px">
            <el-form-item label="卡类型">
              <el-radio-group v-model="cardForm.category" @change="onCardCategoryChange">
                <el-radio-button label="stored">储值卡</el-radio-button>
                <el-radio-button label="month">月卡</el-radio-button>
                <el-radio-button label="season">季卡</el-radio-button>
                <el-radio-button label="year">年卡</el-radio-button>
                <el-radio-button label="custom">定制</el-radio-button>
              </el-radio-group>
            </el-form-item>
            <el-form-item v-if="cardForm.category==='stored'||cardForm.category==='custom'" label="储值金额">
              <el-input-number v-model="cardForm.total_times" :min="1" :step="100" style="width:100%" />
            </el-form-item>
            <el-form-item v-if="cardForm.category==='stored'||cardForm.category==='custom'" label="赠送金额">
              <el-input-number v-model="cardForm.bonus_amount" :min="0" :step="10" style="width:100%" />
              <div style="font-size:11px;color:#909399">充值{{ cardForm.total_times }}元赠{{ cardForm.bonus_amount || 0 }}元，到账{{ cardForm.total_times + (cardForm.bonus_amount||0) }}元</div>
            </el-form-item>
            <el-form-item :label="cardForm.category==='stored'?'储值金额':'名称'">
              <el-input v-model="cardForm.name" :placeholder="cardForm.category==='stored'?'如：500元储值卡':'如：月度畅打卡'" />
            </el-form-item>
            <el-form-item label="描述"><el-input v-model="cardForm.description" type="textarea" rows="2" /></el-form-item>
          </el-form>
          <template #footer><el-button @click="showCardDialog=false">取消</el-button><el-button type="primary" @click="saveCard">保存</el-button></template>
        </el-dialog>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { getVenues, getVenue, createVenue, updateVenue, getFields, createField, updateField, deleteField as apiDeleteField } from '../api'
import api from '../api'
import { useUserStore } from '../stores/user'
import { useVenueStore } from '../stores/venue'
import { ElMessage } from 'element-plus'

const store = useUserStore()
const venueStore = useVenueStore()
const canManage = store.hasRole('core_management', 'manager')
const activeTab = ref('venues')

// ═══════ 球馆数据 ═══════
const venues = ref([])

// ═══════ 地区数据 ═══════
const regionData = [
  { value:'北京市',label:'北京市',children:[{ value:'北京市',label:'北京市',children:[{value:'东城区',label:'东城区'},{value:'朝阳区',label:'朝阳区'},{value:'海淀区',label:'海淀区'}]}] },
  { value:'上海市',label:'上海市',children:[{ value:'上海市',label:'上海市',children:[{value:'浦东新区',label:'浦东新区'},{value:'黄浦区',label:'黄浦区'},{value:'徐汇区',label:'徐汇区'}]}] },
  { value:'江苏省',label:'江苏省',children:[
    { value:'南京市',label:'南京市',children:[{value:'鼓楼区',label:'鼓楼区'},{value:'玄武区',label:'玄武区'},{value:'建邺区',label:'建邺区'},{value:'江宁区',label:'江宁区'}] },
    { value:'苏州市',label:'苏州市',children:[{value:'姑苏区',label:'姑苏区'},{value:'工业园区',label:'工业园区'},{value:'昆山市',label:'昆山市'}] },
    { value:'镇江市',label:'镇江市',children:[
      { value:'京口区',label:'京口区' },{ value:'润州区',label:'润州区' },
      { value:'丹徒区',label:'丹徒区' },
      { value:'丹阳市',label:'丹阳市',children:[
        {value:'高新区',label:'高新区'},{value:'开发区',label:'开发区'},{value:'云阳街道',label:'云阳街道'},{value:'曲阿街道',label:'曲阿街道'},
        {value:'司徒镇',label:'司徒镇'},{value:'延陵镇',label:'延陵镇'},{value:'珥陵镇',label:'珥陵镇'},{value:'导墅镇',label:'导墅镇'},
        {value:'皇塘镇',label:'皇塘镇'},{value:'吕城镇',label:'吕城镇'},{value:'陵口镇',label:'陵口镇'},{value:'访仙镇',label:'访仙镇'},{value:'界牌镇',label:'界牌镇'},
      ]},
    ]},
    { value:'无锡市',label:'无锡市',children:[{value:'梁溪区',label:'梁溪区'},{value:'新吴区',label:'新吴区'},{value:'江阴市',label:'江阴市'}] },
    { value:'常州市',label:'常州市',children:[{value:'天宁区',label:'天宁区'},{value:'武进区',label:'武进区'},{value:'溧阳市',label:'溧阳市'}] },
    { value:'南通市',label:'南通市',children:[{value:'崇川区',label:'崇川区'},{value:'如皋市',label:'如皋市'}] },
    { value:'扬州市',label:'扬州市',children:[{value:'广陵区',label:'广陵区'},{value:'邗江区',label:'邗江区'}] },
    { value:'徐州市',label:'徐州市',children:[{value:'云龙区',label:'云龙区'},{value:'泉山区',label:'泉山区'}] },
  ]},
  { value:'浙江省',label:'浙江省',children:[
    { value:'杭州市',label:'杭州市',children:[{value:'西湖区',label:'西湖区'},{value:'滨江区',label:'滨江区'},{value:'余杭区',label:'余杭区'}] },
    { value:'宁波市',label:'宁波市',children:[{value:'海曙区',label:'海曙区'},{value:'鄞州区',label:'鄞州区'}] },
  ]},
  { value:'安徽省',label:'安徽省',children:[
    { value:'合肥市',label:'合肥市',children:[{value:'蜀山区',label:'蜀山区'},{value:'包河区',label:'包河区'},{value:'高新区',label:'高新区'},{value:'经开区',label:'经开区'}] },
  ]},
  { value:'广东省',label:'广东省',children:[
    { value:'广州市',label:'广州市',children:[{value:'天河区',label:'天河区'},{value:'越秀区',label:'越秀区'}] },
    { value:'深圳市',label:'深圳市',children:[{value:'南山区',label:'南山区'},{value:'福田区',label:'福田区'},{value:'宝安区',label:'宝安区'}] },
  ]},
]

function parseRegion(text) {
  if (!text) return []
  const result = []
  let remaining = text
  for (const prov of regionData) {
    if (remaining.startsWith(prov.value)) { result.push(prov.value); remaining = remaining.slice(prov.value.length)
      if (prov.children) for (const city of prov.children) {
        if (remaining.startsWith(city.value)) { result.push(city.value); remaining = remaining.slice(city.value.length)
          if (city.children) for (const dist of city.children) {
            if (remaining.startsWith(dist.value)) { result.push(dist.value); remaining = remaining.slice(dist.value.length)
              if (dist.children) for (const sub of dist.children) {
                if (remaining.startsWith(sub.value)) { result.push(sub.value); break }
              }
              break }
          }
          break }
      }
      break }
  }
  return result.length ? result : []
}

// ═══════ Tab 1: 球馆管理 ═══════
const showVenueDialog = ref(false)
const editingVenueId = ref(null)
const venueForm = ref({ name:'',address:'',phone:'',district:'',status:'open',open_time:'09:00',close_time:'22:00',description:'',region:[] })
const regionText = computed(() => venueForm.value.region?.join('') || '')

function resetVenueForm() { editingVenueId.value = null; venueForm.value = { name:'',address:'',phone:'',district:'',status:'open',open_time:'09:00',close_time:'22:00',description:'',region:[] } }

async function loadVenues() { try { venues.value = (await getVenues()).venues || [] } catch { /* */ } }

async function editVenue(v) {
  editingVenueId.value = v.id
  try { const d = await getVenue(v.id); const h = (d.business_hours||'09:00-22:00').split('-')
    venueForm.value = { name:d.name||'',address:d.address||'',phone:d.phone||'',district:d.district||'',status:d.status||'open',open_time:h[0]||'09:00',close_time:h[1]||'22:00',description:d.description||'',region:parseRegion(d.district||'') }
  } catch { venueForm.value = { ...venueForm.value, name:v.name||'' } }
  showVenueDialog.value = true
}

async function saveVenue() {
  if (!venueForm.value.name) { ElMessage.warning('请输入名称'); return }
  const data = { ...venueForm.value, district: regionText.value || venueForm.value.district, business_hours: `${venueForm.value.open_time}-${venueForm.value.close_time}` }
  try {
    editingVenueId.value ? await updateVenue(editingVenueId.value, data) : await createVenue(data)
    showVenueDialog.value = false; await loadVenues(); ElMessage.success('保存成功')
  } catch { /* */ }
}

async function toggleVenueStatus(v, val) {
  try { await updateVenue(v.id, { status: val ? 'open' : 'closed' }); v.status = val ? 'open' : 'closed'; ElMessage.success(val?'营业中':'已歇业') } catch { /* */ }
}

// ═══════ Tab 2: 场地设置 ═══════
const fieldTypes = [
  { value:'badminton',label:'羽毛球',icon:'🏸' },{ value:'basketball',label:'篮球',icon:'🏀' },
  { value:'pingpong',label:'乒乓球',icon:'🏓' },{ value:'tennis',label:'网球',icon:'🎾' },
  { value:'football',label:'足球',icon:'⚽' },{ value:'swimming',label:'游泳',icon:'🏊' },
  { value:'fitness',label:'健身',icon:'🏋️' },{ value:'other',label:'其他',icon:'📌' },
]
const ftMap = Object.fromEntries(fieldTypes.map(t=>[t.value,t.label]))
function fieldTypeLabel(t) { return ftMap[t] || t }

const fieldVenueId = computed(() => venueStore.currentId)
const fields = ref([])
const editingFieldId = ref(null)
const showFieldForm = ref(false)
const fieldRelation = ref('independent')
const fieldForm = ref({ name:'',field_type:'basketball',price_per_hour:0,peak_price_per_hour:0,duration:2,capacity:0,parent_field_id:null,sort_order:0 })

const parentFields = computed(() => fields.value.filter(f=>!f.parent_field_id))
const hasChildren = (id) => fields.value.some(f=>f.parent_field_id===id)
const getChildren = (id) => fields.value.filter(f=>f.parent_field_id===id)
const parentCandidates = computed(() => fields.value.filter(f=>!f.parent_field_id && f.id!==editingFieldId.value))
const displayFields = computed(() => {
  const r = []
  for (const pf of parentFields.value) { r.push({...pf,_isParent:hasChildren(pf.id),_indent:false,_isChild:false}); for (const c of getChildren(pf.id)) r.push({...c,_isParent:false,_indent:true,_isChild:true}) }
  return r
})

async function loadFields() { if (!fieldVenueId.value) return; try { const r = await getFields(fieldVenueId.value); fields.value = (r.fields||[]).map(f=>({...f,parent_field_id:f.parent_field_id||null})) } catch { /* */ } }
// 跟随顶部场馆切换
watch(() => venueStore.currentId, () => { if (venueStore.currentId) loadFields() }, { immediate: true })

function editField(row) { editingFieldId.value = row.id; showFieldForm.value = true; fieldForm.value = { name:row.name,field_type:row.field_type,price_per_hour:row.price_per_hour||0,peak_price_per_hour:row.peak_price_per_hour||0,duration:row.duration||(row.field_type==='basketball'?2:1),capacity:row.capacity||0,parent_field_id:row.parent_field_id||null,sort_order:row.sort_order||0 }; fieldRelation.value = row._isChild?'child':(row._isParent?'parent':'independent') }
function showAddField() { editingFieldId.value = null; showFieldForm.value = true; fieldForm.value = { name:'',field_type:'basketball',price_per_hour:100,peak_price_per_hour:0,duration:2,capacity:0,parent_field_id:null,sort_order:fields.value.length+1 }; fieldRelation.value = 'independent' }
function cancelFieldEdit() { editingFieldId.value = null; showFieldForm.value = false }
function onFieldTypeChange(v) { fieldForm.value.duration = (v==='basketball'||v==='football')?2:1 }
function onFieldRelationChange(v) { if (v!=='child') fieldForm.value.parent_field_id = null }

// 实时同步到列表
// 编辑时每 300ms 同步到列表（防抖减少卡顿）
let syncTimer = null
watch(fieldForm, (val) => {
  if (!editingFieldId.value) return
  clearTimeout(syncTimer)
  syncTimer = setTimeout(() => {
    const idx = fields.value.findIndex(f=>f.id===editingFieldId.value)
    if (idx===-1) return
    fields.value[idx] = {...fields.value[idx], name:val.name,field_type:val.field_type,price_per_hour:val.price_per_hour,peak_price_per_hour:val.peak_price_per_hour,duration:val.duration,capacity:val.capacity,parent_field_id:fieldRelation.value==='child'?val.parent_field_id:null,sort_order:val.sort_order}
  }, 300)
}, { deep:true })

async function saveField() {
  if (!fieldForm.value.name) { ElMessage.warning('请输入名称'); return }
  const data = {...fieldForm.value, venue_id:fieldVenueId.value, parent_field_id:fieldRelation.value==='child'?fieldForm.value.parent_field_id:null}
  try { editingFieldId.value ? await updateField(editingFieldId.value, data) : await createField(data); cancelFieldEdit(); await loadFields(); ElMessage.success('保存成功') } catch { /* */ }
}
async function doDeleteField(id) { try { await apiDeleteField(id); await loadFields(); ElMessage.success('已删除') } catch { /* */ } }
async function moveField(row, dir) {
  const idx = displayFields.value.findIndex(f=>f.id===row.id); if (idx===-1) return
  const t = idx+dir; if (t<0||t>=displayFields.value.length) return
  const target = displayFields.value[t]
  try { await updateField(row.id,{...row,sort_order:target.sort_order,venue_id:fieldVenueId.value}); await updateField(target.id,{...target,sort_order:row.sort_order,venue_id:fieldVenueId.value}); await loadFields() } catch { /* */ }
}

// ═══════ Tab 3: 卡种管理 ═══════
const cardTypes = ref([])
const sortedCardTypes = computed(() => {
  const order = { stored: 0, times: 1, month: 2, season: 3, year: 4, custom: 5 }
  return [...cardTypes.value].sort((a, b) => {
    const catA = order[a.category] ?? 9
    const catB = order[b.category] ?? 9
    if (catA !== catB) return catA - catB
    // 同类型按金额少→多
    if (a.price !== b.price) return a.price - b.price
    // 同金额按时长短→长
    return (a.valid_days || 0) - (b.valid_days || 0)
  })
})
const showCardDialog = ref(false)
const editingCardId = ref(null)
const cardForm = ref({ category:'stored', total_times:500, valid_days:1095, name:'', description:'', price:0 })
const cardValidMap = { stored:1095, month:30, season:90, year:365, custom:365 }
function cardCategoryLabel(c) { return {stored:'储值卡',month:'月卡',season:'季卡',year:'年卡',custom:'定制'}[c]||c }
function cardTagType(c) { return {stored:'success',month:'',season:'warning',year:'danger',custom:'info'}[c]||'' }
function onCardCategoryChange(c) { cardForm.value.valid_days = cardValidMap[c]||30 }

async function loadCards() {
  if (!venueStore.currentId) { cardTypes.value = []; return }
  try { cardTypes.value = (await api.get('/card-types', { params: { venue_id: venueStore.currentId } })).card_types || [] } catch { /* */ }
}
// 监听球馆切换
watch(() => venueStore.currentId, () => { loadCards() })

function showAddCard() { editingCardId.value = null; cardForm.value = { category:'stored',total_times:500,bonus_amount:0,price:0,valid_days:1095,name:'',description:'' }; showCardDialog.value = true }
function editCard(row) { editingCardId.value = row.id; cardForm.value = {...row}; showCardDialog.value = true }
async function saveCard() {
  const d = {...cardForm.value, venue_id: venueStore.currentId}
  d.price = (d.category==='stored'||d.category==='custom') ? d.total_times : 0
  try { editingCardId.value ? await api.put(`/card-types/${editingCardId.value}`,d) : await api.post('/card-types',d); showCardDialog.value = false; await loadCards(); ElMessage.success('保存成功') } catch { /* */ }
}
async function deleteCard(id) { try { await api.delete(`/card-types/${id}`); await loadCards(); ElMessage.success('已停用') } catch { /* */ } }

onMounted(async () => { await venueStore.load(); await loadVenues(); await loadCards() })
</script>

<style scoped>
.settings-page { max-width: 1300px; }
.tab-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; gap:12px; }
.form-panel { background:#FAFAFA; border:1px solid #EBEEF5; border-radius:8px; padding:16px; }
.form-actions { display:flex; gap:10px; justify-content:flex-end; margin-top:16px; padding-top:12px; border-top:1px solid #EBEEF5; }
:deep(.el-tabs__content) { padding: 20px; }
</style>
