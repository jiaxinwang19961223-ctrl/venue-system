<template>
  <div>
    <div class="page-header">
      <h3><i class="ri-vip-crown-line"></i> 会员管理</h3>
      <div class="actions">
        <el-input v-model="keyword" placeholder="搜索姓名/手机号" style="width:200px" clearable @clear="load" @keyup.enter="load" />
        <el-button type="primary" @click="search">搜索</el-button>
        <el-button type="success" @click="showAdd"><i class="ri-user-add-line"></i> 新增会员</el-button>
      </div>
    </div>

    <el-table :data="members" stripe>
      <el-table-column label="人脸" width="70">
        <template #default="{ row }">
          <el-avatar v-if="row.face_image" :src="row.face_image" size="small" />
          <el-tag v-else size="small" type="info">—</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="name" label="姓名" width="100" />
      <el-table-column prop="phone" label="手机号" width="130" />
      <el-table-column prop="gender" label="性别" width="60" />
      <el-table-column prop="balance" label="余额" width="100" sortable>
        <template #default="{ row }"><strong>¥{{ row.balance?.toFixed(2) }}</strong></template>
      </el-table-column>
      <el-table-column prop="total_recharge" label="累计充值" width="100">
        <template #default="{ row }">¥{{ (row.total_recharge || 0).toFixed(2) }}</template>
      </el-table-column>
      <el-table-column prop="total_consumption" label="累计消费" width="100">
        <template #default="{ row }">¥{{ (row.total_consumption || 0).toFixed(2) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="280" fixed="right">
        <template #default="{ row }">
          <div class="btn-row">
            <el-button size="small" type="warning" @click="showRecharge(row)">充值</el-button>
            <el-button size="small" type="success" @click="showIssueCard(row)">办卡</el-button>
            <el-button size="small" @click="showOrders(row)">记录</el-button>
            <el-button size="small" type="primary" @click="editMember(row)">编辑</el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <!-- ──── 新增/编辑（含人脸拍照）──── -->
    <el-dialog :title="editingId ? '编辑会员' : '新增会员'" v-model="showDialog" width="560px" @closed="stopCamera">
      <el-row :gutter="20">
        <!-- 左侧：基本信息 -->
        <el-col :span="14">
          <el-form :model="form" label-width="80px">
            <el-form-item label="姓名"><el-input v-model="form.name" /></el-form-item>
            <el-form-item label="手机号"><el-input v-model="form.phone" /></el-form-item>
            <el-form-item label="性别">
              <el-select v-model="form.gender"><el-option label="男" value="男" /><el-option label="女" value="女" /></el-select>
            </el-form-item>
            <el-form-item label="生日"><el-date-picker v-model="form.birthday" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item>
            <el-form-item label="备注"><el-input v-model="form.remark" type="textarea" rows="2" /></el-form-item>
          </el-form>
        </el-col>
        <!-- 右侧：人脸拍照 -->
        <el-col :span="10">
          <div class="face-section">
            <p class="face-title"><i class="ri-camera-line"></i> 人脸录入</p>
            <div class="face-camera-mini">
              <video ref="videoRef" autoplay playsinline width="180" height="135"></video>
              <canvas ref="canvasRef" width="180" height="135" style="display:none"></canvas>
              <img v-if="facePreview" :src="facePreview" class="face-preview-mini" />
            </div>
            <div class="face-btns">
              <el-button size="small" @click="startCamera" :disabled="cameraActive"><i class="ri-camera-line"></i> 打开</el-button>
              <el-button size="small" type="success" @click="captureFace" :disabled="!cameraActive">拍照</el-button>
              <el-button size="small" v-if="facePreview" @click="retakeFace">重拍</el-button>
            </div>
            <p v-if="faceStatus" class="face-status" :style="{color: faceOk ? '#67C23A' : '#E6A23C'}">{{ faceStatus }}</p>
          </div>
        </el-col>
      </el-row>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>

    <!-- ──── 人脸补拍 ──── -->
    <el-dialog title="人脸补拍" v-model="showRetakeDialog" width="420px" @closed="stopCamera">
      <p><strong>会员：</strong>{{ retakeMember?.name }}</p>
      <div class="face-camera-mini" style="width:200px;height:150px;margin:10px auto">
        <video ref="retakeVideoRef" autoplay playsinline width="200" height="150"></video>
        <canvas ref="retakeCanvasRef" width="200" height="150" style="display:none"></canvas>
        <img v-if="retakePreview" :src="retakePreview" class="face-preview-mini" style="width:200px;height:150px" />
      </div>
      <div style="text-align:center;margin-top:10px">
        <el-button size="small" @click="startRetakeCamera" :disabled="retakeCameraActive">打开摄像头</el-button>
        <el-button size="small" type="success" @click="captureRetake" :disabled="!retakeCameraActive">拍照</el-button>
      </div>
      <p v-if="retakeStatus" style="text-align:center" :style="{color: retakeOk ? '#67C23A' : '#E6A23C'}">{{ retakeStatus }}</p>
      <template #footer>
        <el-button @click="showRetakeDialog = false">取消</el-button>
        <el-button type="primary" @click="saveRetake" :disabled="!retakeDescriptor">保存人脸</el-button>
      </template>
    </el-dialog>

    <!-- ──── 签到扣费 ──── -->
    <el-dialog title="签到扣费" v-model="showConsumeDialog" width="400px">
      <div class="info-box"><p><strong>会员：</strong>{{ consumeMember?.name }}</p><p><strong>余额：</strong>¥{{ consumeMember?.balance?.toFixed(2) }}</p></div>
      <el-form :model="consumeForm" label-width="80px">
        <el-form-item label="扣费方式">
          <el-radio-group v-model="consumeForm.use_card">
            <el-radio :value="false">余额扣费</el-radio>
            <el-radio :value="true">次卡扣次</el-radio>
          </el-radio-group>
        </el-form-item>
        <template v-if="consumeForm.use_card">
          <el-form-item label="选择卡"><el-select v-model="consumeForm.card_id" style="width:100%"><el-option v-for="c in consumeCards" :key="c.id" :label="`${c.card_type} 剩${c.total_times - c.used_times}次`" :value="c.id" /></el-select></el-form-item>
        </template>
        <template v-else>
          <el-form-item label="金额"><el-input-number v-model="consumeForm.amount" :min="0" :precision="2" style="width:100%" /></el-form-item>
        </template>
        <el-form-item label="备注"><el-input v-model="consumeForm.remark" placeholder="消费项目" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="showConsumeDialog = false">取消</el-button><el-button type="danger" @click="handleConsume">确认扣费</el-button></template>
    </el-dialog>

    <!-- ──── 充值 ──── -->
    <el-dialog title="余额充值" v-model="showRechargeDialog" width="400px">
      <div class="info-box"><p><strong>会员：</strong>{{ rechargeMember?.name }}</p><p><strong>余额：</strong>¥{{ rechargeMember?.balance?.toFixed(2) }}</p></div>
      <el-form :model="rechargeForm" label-width="80px">
        <el-form-item label="金额"><el-input-number v-model="rechargeForm.amount" :min="1" :step="100" style="width:100%" /></el-form-item>
        <el-form-item label="支付"><el-radio-group v-model="rechargeForm.payment_method"><el-radio label="wechat">微信</el-radio><el-radio label="cash">现金</el-radio></el-radio-group></el-form-item>
      </el-form>
      <template #footer><el-button @click="showRechargeDialog = false">取消</el-button><el-button type="primary" @click="handleRecharge">确认</el-button></template>
    </el-dialog>

    <!-- ──── 办卡 ──── -->
    <el-dialog title="办理会员卡" v-model="showIssueCardDialog" width="450px">
      <p><strong>会员：</strong>{{ rechargeMember?.name }}</p>
      <el-form :model="cardForm" label-width="80px">
        <el-form-item label="卡种"><el-select v-model="cardForm.card_type_id" style="width:100%" @change="onCardTypeChange"><el-option v-for="ct in cardTypes" :key="ct.id" :label="`${ct.name} (¥${ct.price})`" :value="ct.id" /></el-select></el-form-item>
        <el-form-item label="售价"><el-input-number v-model="cardForm.price" :min="0" :precision="2" style="width:100%" /></el-form-item>
        <el-form-item label="生效"><el-date-picker v-model="cardForm.start_date" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="showIssueCardDialog = false">取消</el-button><el-button type="primary" @click="handleIssueCard">确认办卡</el-button></template>
    </el-dialog>

    <!-- ──── 消费记录 ──── -->
    <el-dialog title="消费记录" v-model="showOrdersDialog" width="700px">
      <p><strong>{{ consumeMember?.name }}</strong> | 累计消费：¥{{ (consumeMember?.total_consumption || 0).toFixed(2) }}</p>
      <el-table :data="memberOrders" stripe max-height="400">
        <el-table-column prop="order_no" label="订单号" width="170" />
        <el-table-column label="类型" width="80"><template #default="{ row }">{{ { field_book:'场地', walk_in:'散客', card_recharge:'充值', course_book:'课程' }[row.order_type] }}</template></el-table-column>
        <el-table-column prop="created_at" label="时间" width="160" />
        <el-table-column prop="paid_amount" label="金额" width="80"><template #default="{ row }">¥{{ row.paid_amount?.toFixed(2) }}</template></el-table-column>
        <el-table-column prop="payment_method" label="支付" width="70"><template #default="{ row }">{{ { wechat:'微信', cash:'现金', card:'会员卡' }[row.payment_method]||row.payment_method }}</template></el-table-column>
        <el-table-column prop="remark" label="备注" min-width="100" />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getMembers, getMember, createMember, updateMember, getMemberCards, createCard } from '../api'
import api from '../api'
import * as faceapi from 'face-api.js'
import { ElMessage } from 'element-plus'

const members = ref([])
const cardTypes = ref([])
const cards = ref([])
const consumeCards = ref([])
const memberOrders = ref([])
const keyword = ref('')

// 弹窗状态
const showDialog = ref(false)
const showRetakeDialog = ref(false)
const showConsumeDialog = ref(false)
const showRechargeDialog = ref(false)
const showIssueCardDialog = ref(false)
const showOrdersDialog = ref(false)

const editingId = ref(null)
const rechargeMember = ref(null)
const consumeMember = ref(null)
const retakeMember = ref(null)

// 表单
const form = ref({ name: '', phone: '', gender: '', birthday: '', remark: '', venue_id: 1 })
const rechargeForm = ref({ amount: 0, payment_method: 'wechat' })
const consumeForm = ref({ amount: 0, use_card: false, card_id: null, remark: '' })
const cardForm = ref({ card_type_id: null, total_times: 0, price: 0, start_date: '', end_date: '', member_id: 0, card_type: '' })

// ──── 新增/编辑人脸 ────
const videoRef = ref(null)
const canvasRef = ref(null)
const cameraActive = ref(false)
const facePreview = ref(null)
const faceDescriptor = ref(null)
const faceStatus = ref('')
const faceOk = ref(false)
let stream = null

// ──── 补拍人脸 ────
const retakeVideoRef = ref(null)
const retakeCanvasRef = ref(null)
const retakeCameraActive = ref(false)
const retakePreview = ref(null)
const retakeDescriptor = ref(null)
const retakeStatus = ref('')
const retakeOk = ref(false)
let retakeStream = null

// ──── 摄像头 ────
async function doStartCamera(videoEl, setActive) {
  try {
    const s = await navigator.mediaDevices.getUserMedia({ video: { width: 200, height: 150, facingMode: 'user' } })
    if (videoEl) videoEl.srcObject = s
    setActive(true)
    return s
  } catch { ElMessage.error('无法访问摄像头'); return null }
}

async function startCamera() { stream = await doStartCamera(videoRef.value, (v) => cameraActive.value = v) }
async function startRetakeCamera() { retakeStream = await doStartCamera(retakeVideoRef.value, (v) => retakeCameraActive.value = v) }

function stopStream(s, setActive) { if (s) { s.getTracks().forEach(t => t.stop()) }; setActive(false) }

async function doCapture(videoEl, canvasEl, setPreview, setDescriptor, setStatus, setOk, s) {
  const video = videoEl
  const canvas = canvasEl
  if (!canvas || !video) return
  canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height)
  const img = canvas.toDataURL('image/jpeg', 0.8)
  setPreview(img)
  if (s) { s.getTracks().forEach(t => t.stop()) }

  // 提取特征
  try {
    const d = await faceapi.detectSingleFace(canvas, new faceapi.TinyFaceDetectorOptions({ inputSize: 160, scoreThreshold: 0.5 }))
      .withFaceLandmarks(true).withFaceDescriptor()
    if (d) {
      setDescriptor(JSON.stringify(Array.from(d.descriptor)))
      setStatus('✅ 人脸特征已提取')
      setOk(true)
    } else {
      setDescriptor(null)
      setStatus('⚠ 未检测到清晰人脸')
      setOk(false)
    }
  } catch {
    setDescriptor(null)
    setStatus('⚠ 特征提取失败')
    setOk(false)
  }
}

async function captureFace() { await doCapture(videoRef.value, canvasRef.value, (v) => facePreview.value = v, (v) => faceDescriptor.value = v, (v) => faceStatus.value = v, (v) => faceOk.value = v, stream); cameraActive.value = false }
async function captureRetake() { await doCapture(retakeVideoRef.value, retakeCanvasRef.value, (v) => retakePreview.value = v, (v) => retakeDescriptor.value = v, (v) => retakeStatus.value = v, (v) => retakeOk.value = v, retakeStream); retakeCameraActive.value = false }

function retakeFace() { facePreview.value = null; faceDescriptor.value = null; faceStatus.value = ''; faceOk.value = false; startCamera() }

function stopCamera() { stopStream(stream, (v) => cameraActive.value = v); stopStream(retakeStream, (v) => retakeCameraActive.value = v) }

// ──── 补拍 ────
function editMember(m) {
  editingId.value = m.id
  form.value = { name: m.name, phone: m.phone, gender: m.gender || '', birthday: '', remark: '', venue_id: m.venue_id }
  facePreview.value = m.face_image || null
  faceDescriptor.value = null
  faceStatus.value = m.face_image ? '(已有照片，可重拍)' : ''
  faceOk.value = false
  showDialog.value = true
}

function showRetake(m) {
  retakeMember.value = m
  retakePreview.value = m.face_image || null
  retakeDescriptor.value = null
  retakeStatus.value = ''
  retakeOk.value = false
  showRetakeDialog.value = true
}

async function saveRetake() {
  try {
    await updateMember(retakeMember.value.id, { face_image: retakePreview.value, face_descriptor: retakeDescriptor.value })
    showRetakeDialog.value = false
    await load()
    ElMessage.success('人脸已更新')
  } catch { /* */ }
}

// ──── CRUD ────
function showAdd() { editingId.value = null; form.value = { name: '', phone: '', gender: '', birthday: '', remark: '', venue_id: 1 }; facePreview.value = null; faceDescriptor.value = null; faceStatus.value = ''; faceOk.value = false; showDialog.value = true }
async function load() { try { members.value = (await getMembers({ keyword: keyword.value })).members || [] } catch { /* */ } }
async function search() { keyword.value = keyword.value.trim(); await load() }

async function handleSave() {
  const data = { ...form.value }
  if (facePreview.value) { data.face_image = facePreview.value; data.face_descriptor = faceDescriptor.value }
  try {
    if (editingId.value) { await updateMember(editingId.value, data) } else { await createMember(data) }
    showDialog.value = false; stopCamera(); await load(); ElMessage.success('保存成功')
  } catch { /* */ }
}

// ──── 充值/办卡/签到/记录 ────
function showRecharge(m) { rechargeMember.value = m; rechargeForm.value = { amount: 0, payment_method: 'wechat' }; showRechargeDialog.value = true }
async function handleRecharge() {
  try {
    await api.post('/orders', { venue_id: rechargeMember.value.venue_id||1, member_id: rechargeMember.value.id, order_type: 'card_recharge', paid_amount: rechargeForm.value.amount, payment_method: rechargeForm.value.payment_method })
    await updateMember(rechargeMember.value.id, { balance: (rechargeMember.value.balance||0) + rechargeForm.value.amount })
    showRechargeDialog.value = false; await load(); ElMessage.success('充值成功')
  } catch { /* */ }
}

function showIssueCard(m) { rechargeMember.value = m; cardForm.value = { card_type_id:null, total_times:0, price:0, start_date: new Date().toISOString().slice(0,10), end_date:'', member_id: m.id, card_type:'times' }; showIssueCardDialog.value = true }
function onCardTypeChange(id) { const ct = cardTypes.value.find(t=>t.id===id); if(ct){ cardForm.value.price=ct.price; cardForm.value.total_times=ct.total_times; cardForm.value.card_type=ct.category; const e=new Date(); e.setDate(e.getDate()+ct.valid_days); cardForm.value.end_date=e.toISOString().slice(0,10) } }
async function handleIssueCard() { try { await createCard({ member_id:rechargeMember.value.id, card_type: cardForm.value.card_type||'times', total_times:cardForm.value.total_times, price:cardForm.value.price, start_date:cardForm.value.start_date, end_date:cardForm.value.end_date }); showIssueCardDialog.value=false; ElMessage.success('办卡成功') } catch { /* */ } }

async function showConsume(m) { consumeMember.value=m; consumeForm.value={amount:0,use_card:false,card_id:null,remark:''}; try{consumeCards.value=(await getMemberCards(m.id)).cards?.filter(c=>c.is_active&&c.total_times>c.used_times)||[]}catch{consumeCards.value=[]}; showConsumeDialog.value=true }
async function handleConsume() { try { await api.post(`/members/${consumeMember.value.id}/consume`, consumeForm.value); showConsumeDialog.value=false; await load(); ElMessage.success('扣费成功') } catch { /* */ } }

async function showOrders(m) { consumeMember.value=m; try{memberOrders.value=(await api.get(`/members/${m.id}/orders`)).orders||[]}catch{memberOrders.value=[]}; showOrdersDialog.value=true }

onMounted(async () => {
  try { cardTypes.value = (await api.get('/card-types')).card_types || [] } catch { /* */ }
  const M = 'https://justadudewhohacks.github.io/face-api.js/models'
  try { await Promise.all([faceapi.nets.tinyFaceDetector.loadFromUri(M), faceapi.nets.faceLandmark68TinyNet.loadFromUri(M), faceapi.nets.faceRecognitionNet.loadFromUri(M)]) } catch { /* */ }
  await load()
})
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 10px; }
.actions { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
.btn-row { display: flex; gap: 4px; flex-wrap: nowrap; white-space: nowrap; }
.info-box { background: #F5F7FA; padding: 12px; border-radius: 4px; margin-bottom: 16px; }
.info-box p { margin: 4px 0; }
.face-section { border: 1px dashed #DCDFE6; border-radius: 8px; padding: 10px; text-align: center; }
.face-title { margin: 0 0 8px; font-size: 13px; color: #606266; }
.face-camera-mini { position: relative; width: 180px; height: 135px; margin: 0 auto; background: #000; border-radius: 4px; overflow: hidden; }
.face-camera-mini video, .face-preview-mini { width: 100%; height: 100%; object-fit: cover; }
.face-btns { margin-top: 8px; display: flex; gap: 5px; justify-content: center; }
.face-status { font-size: 12px; margin: 6px 0 0; }
</style>
