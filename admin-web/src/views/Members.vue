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

    <el-table :data="members" stripe style="max-width:1100px">
      <el-table-column label="照片" width="70" align="center">
        <template #default="{ row }">
          <el-avatar v-if="row.face_image" :src="row.face_image" :size="40" shape="square" style="cursor:pointer" @click="previewPhoto(row)" />
          <el-avatar v-else :size="40" shape="square" style="background:#C0C4CC"><i class="ri-user-line"></i></el-avatar>
        </template>
      </el-table-column>
      <el-table-column prop="name" label="姓名" width="100" />
      <el-table-column prop="phone" label="联系电话" width="140" />
      <el-table-column label="卡片类型" min-width="110">
        <template #default="{ row }">
          <el-tag v-if="row.card_types" size="small" type="success">{{ cardTypeLabel(row.card_types) }}</el-tag>
          <span v-else style="color:#C0C4CC">—</span>
        </template>
      </el-table-column>
      <el-table-column label="有效期" width="100" align="center">
        <template #default="{ row }">
          <span v-if="row.card_end_date" class="expire-tag" :class="expireClass(row.card_end_date)">
            {{ countdownDays(row.card_end_date) }}
          </span>
          <span v-else style="color:#C0C4CC;font-size:12px">—</span>
        </template>
      </el-table-column>
      <el-table-column label="储值/余额" width="120" sortable align="right">
        <template #default="{ row }"><strong style="font-size:15px">¥{{ (row.balance || 0).toFixed(2) }}</strong></template>
      </el-table-column>
      <el-table-column label="操作" width="330" fixed="right">
        <template #default="{ row }">
          <div class="btn-row">
            <el-button size="small" type="warning" @click="showRecharge(row)">充值</el-button>
            <el-button size="small" type="success" @click="showIssueCard(row)">办卡</el-button>
            <el-button size="small" @click="showOrders(row)">记录</el-button>
            <el-button size="small" type="primary" @click="editMember(row)">编辑</el-button>
            <el-popconfirm title="删除会员？" @confirm="doDeleteMember(row.id)"><template #reference><el-button size="small" type="danger" text>删除</el-button></template></el-popconfirm>
          </div>
        </template>
      </el-table-column>
    </el-table>
    <div style="display:flex;justify-content:center;margin-top:16px" v-if="total > pageSize">
      <el-pagination v-model:current-page="page" :page-size="pageSize" :total="total" layout="prev, pager, next" background small @current-change="load" />
    </div>

    <!-- ──── 新增/编辑（含人脸拍照）──── -->
    <el-dialog :title="editingId ? '编辑会员' : '新增会员'" v-model="showDialog" width="820px" @closed="stopCamera">
      <el-row :gutter="20">
        <!-- 左侧：基本信息 -->
        <el-col :span="13">
          <el-form :model="form" label-width="80px">
            <el-form-item label="姓名"><el-input v-model="form.name" /></el-form-item>
            <el-form-item label="手机号"><el-input v-model="form.phone" /></el-form-item>
            <el-form-item label="性别">
              <el-select v-model="form.gender"><el-option label="男" value="男" /><el-option label="女" value="女" /></el-select>
            </el-form-item>
            <el-form-item label="生日"><el-date-picker v-model="form.birthday" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item>
            <el-form-item label="备注"><el-input v-model="form.remark" type="textarea" rows="2" /></el-form-item>
            <el-form-item label="办卡" v-if="!editingId">
              <el-select v-model="form.card_type_id" clearable placeholder="选卡种（可选）" style="width:100%">
                <el-option v-for="ct in venueCardTypes" :key="ct.id" :label="ctLabel(ct)" :value="ct.id" />
              </el-select>
            </el-form-item>
          </el-form>
        </el-col>
        <!-- 右侧：人脸拍照 -->
        <el-col :span="6">
          <div class="face-section">
            <p class="face-title"><i class="ri-camera-line"></i> 人脸录入</p>
            <div class="face-camera-mini">
              <video ref="videoRef" autoplay playsinline width="180" height="135"></video>
              <canvas ref="canvasRef" width="180" height="135" style="position:absolute;top:-9999px;left:-9999px"></canvas>
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
      <!-- 编辑模式下：卡有效期调整（全宽） -->
      <el-row v-if="editingId && editingCards.length > 0">
        <el-col :span="24">
          <el-divider content-position="left" style="margin:8px 0">卡有效期调整</el-divider>
          <el-form :model="form" label-width="100px" inline>
            <el-form-item label="当前卡">
              <el-tag size="small" type="success">{{ cardTypeLabel(editingCards[0]?.card_type) }}</el-tag>
              <span style="margin-left:8px;font-size:12px;color:#909399">到期: {{ editingCards[0]?.end_date || '—' }}</span>
            </el-form-item>
            <el-form-item label="修改到期日">
              <el-date-picker v-model="editCardEndDate" type="date" value-format="YYYY-MM-DD" placeholder="选择新的到期日期" style="width:220px" />
            </el-form-item>
          </el-form>
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
      <div class="face-camera-mini" style="width:320px;height:240px;margin:10px auto">
        <video ref="retakeVideoRef" autoplay playsinline width="320" height="240"></video>
        <canvas ref="retakeCanvasRef" width="320" height="240" style="position:absolute;top:-9999px;left:-9999px"></canvas>
        <img v-if="retakePreview" :src="retakePreview" class="face-preview-mini" style="width:320px;height:240px" />
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
            <el-radio :value="true">储值卡扣费</el-radio>
          </el-radio-group>
        </el-form-item>
        <template v-if="consumeForm.use_card">
          <el-form-item label="选择卡">
            <el-select v-model="consumeForm.card_id" style="width:100%">
              <el-option v-for="c in consumeCards" :key="c.id" :label="cardLabel(c)" :value="c.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="扣费金额" v-if="selectedCardType === 'stored'">
            <el-input-number v-model="consumeForm.amount" :min="1" :max="selectedCardRemaining" :precision="2" style="width:100%" />
            <span style="margin-left:8px;font-size:12px;color:#909399">余额 ¥{{ selectedCardRemaining }}</span>
          </el-form-item>
        </template>
        <template v-else>
          <el-form-item label="金额"><el-input-number v-model="consumeForm.amount" :min="0" :precision="2" style="width:100%" /></el-form-item>
        </template>
        <el-form-item label="备注"><el-input v-model="consumeForm.remark" placeholder="消费项目" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="showConsumeDialog = false">取消</el-button><el-button type="danger" @click="handleConsume">确认扣费</el-button></template>
    </el-dialog>

    <!-- ──── 充值 ──── -->
    <el-dialog title="余额充值" v-model="showRechargeDialog" width="460px">
      <div class="info-box"><p><strong>会员：</strong>{{ rechargeMember?.name }}</p><p><strong>余额：</strong>¥{{ rechargeMember?.balance?.toFixed(2) }}</p></div>
      <el-form :model="rechargeForm" label-width="80px">
        <el-form-item label="快捷卡种">
          <el-select v-model="rechargeForm.card_type_id" style="width:100%" placeholder="选择卡种（可选）" clearable @change="onRechargeCardChange">
            <el-option v-for="ct in rechargeCardTypes" :key="ct.id" :label="ctLabel(ct)" :value="ct.id" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="rechargeCardType==='stored'" label="充值金额">
          <el-input-number v-model="rechargeForm.amount" :min="1" :step="100" style="width:100%" controls-position="right" />
          <div v-if="rechargeForm.bonus" style="font-size:12px;color:#E6A23C;margin-top:4px">🎁 赠送 {{ rechargeForm.bonus }} 元，到账 {{ rechargeForm.amount + rechargeForm.bonus }} 元</div>
        </el-form-item>
        <el-form-item v-else-if="rechargeCardType" label="卡类型">
          <el-tag type="warning" size="large">{{ {month:'月卡',season:'季卡',year:'年卡',custom:'定制'}[rechargeCardType] || rechargeCardType }}</el-tag>
          <span style="margin-left:8px;color:#909399">{{ rechargeCardName }}</span>
        </el-form-item>
        <el-form-item label="支付"><el-radio-group v-model="rechargeForm.payment_method"><el-radio label="wechat">扫码</el-radio><el-radio label="cash">现金</el-radio></el-radio-group></el-form-item>
      </el-form>
      <template #footer><el-button @click="showRechargeDialog = false">取消</el-button><el-button type="primary" @click="handleRecharge">确认</el-button></template>
    </el-dialog>

    <!-- ──── 办卡 ──── -->
    <el-dialog title="办理会员卡" v-model="showIssueCardDialog" width="450px">
      <p><strong>会员：</strong>{{ rechargeMember?.name }}</p>
      <el-form :model="cardForm" label-width="80px">
        <el-form-item label="卡种"><el-select v-model="cardForm.card_type_id" style="width:100%" @change="onCardTypeChange"><el-option v-for="ct in venueCardTypes" :key="ct.id" :label="ctLabel(ct)" :value="ct.id" /></el-select></el-form-item>
        <el-form-item label="售价"><el-input-number v-model="cardForm.price" :min="0" :precision="2" style="width:100%" /></el-form-item>
        <el-form-item label="生效"><el-date-picker v-model="cardForm.start_date" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="showIssueCardDialog = false">取消</el-button><el-button type="primary" @click="handleIssueCard">确认办卡</el-button></template>
    </el-dialog>

    <!-- ──── 消费记录 ──── -->
    <el-dialog title="消费记录" v-model="showOrdersDialog" width="820px">
      <transition name="el-fade-in-linear" mode="out-in">
        <div v-if="ordersLoading" key="loading" class="orders-loading">
          <i class="el-icon-loading" style="font-size:32px;color:#409EFF"></i>
          <p style="color:#909399;margin-top:12px">加载中...</p>
        </div>
        <div v-else key="content" class="orders-content fade-in">
      <div class="orders-summary">
        <span><strong>{{ consumeMember?.name }}</strong></span>
        <el-tag type="danger" effect="plain">累计消费 ¥{{ (consumeMember?.total_consumption || 0).toFixed(2) }}</el-tag>
      </div>
      <el-table :data="memberOrders" stripe max-height="400" size="small">
        <el-table-column prop="order_no" label="订单号" width="180" />
        <el-table-column label="类型" width="80" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.status==='refunded'" size="small" type="success">退费</el-tag>
            <el-tag v-else-if="row.order_type==='card_recharge'" size="small" type="warning">充值</el-tag>
            <el-tag v-else size="small" type="danger">{{ { field_book:'订场', walk_in:'消费', course_book:'课程' }[row.order_type] || '消费' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="时间" width="155" />
        <el-table-column label="金额" width="100" align="right">
          <template #default="{ row }">
            <span :style="{ color: row.status==='refunded'?'#67C23A':(row.order_type==='card_recharge'?'#409EFF':'#F56C6C'), fontWeight:'600' }">
              {{ (row.status==='refunded'||row.order_type==='card_recharge')?'+':'−' }}¥{{ Math.abs(row.paid_amount||0).toFixed(2) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="备注" min-width="120" show-overflow-tooltip>
          <template #default="{ row }">
            <span v-if="row.status==='refunded'" style="color:#67C23A">[退费]</span>
            <span v-else-if="row.remark" style="color:#909399">{{ row.remark }}</span>
            <span v-else style="color:#C0C4CC">—</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" align="center" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="warning" @click="showAdjust(row)">金额调整</el-button>
          </template>
        </el-table-column>
      </el-table>
      </div>
      </transition>
    </el-dialog>

    <!-- ──── 金额调整 ──── -->
    <el-dialog title="金额调整" v-model="showAdjustDialog" width="400px">
      <p><strong>会员：</strong>{{ consumeMember?.name }}</p>
      <p v-if="adjustOrder">订单：{{ adjustOrder.order_no }} · 原金额 ¥{{ (adjustOrder.paid_amount || 0).toFixed(2) }}</p>
      <el-form :model="adjustForm" label-width="80px" style="margin-top:16px">
        <el-form-item label="调整类型">
          <el-radio-group v-model="adjustForm.type">
            <el-radio label="refund">退费 (+)</el-radio>
            <el-radio label="charge">补扣 (-)</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="调整金额">
          <el-input-number v-model="adjustForm.amount" :min="0" :precision="2" style="width:100%" controls-position="right" />
        </el-form-item>
        <el-form-item label="原因">
          <el-input v-model="adjustForm.remark" placeholder="调整原因" />
        </el-form-item>
      </el-form>
      <div v-if="adjustForm.amount > 0" style="background:#F5F7FA;padding:10px;border-radius:8px;margin-top:8px">
        <span v-if="adjustForm.type === 'refund'" style="color:#67C23A">将退回 ¥{{ adjustForm.amount }}，余额 +{{ adjustForm.amount }}</span>
        <span v-else style="color:#F56C6C">将扣除 ¥{{ adjustForm.amount }}，余额 -{{ adjustForm.amount }}</span>
      </div>
      <template #footer>
        <el-button @click="showAdjustDialog = false">取消</el-button>
        <el-button type="primary" @click="handleAdjust">确认调整</el-button>
      </template>
    </el-dialog>

    <!-- 照片预览 -->
    <el-dialog :title="photoPreview?.name||'照片'" v-model="showPhotoPreview" width="360px" @closed="photoPreview=null">
      <img v-if="photoPreview" :src="photoPreview.src" style="width:100%;border-radius:8px" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { getMembers, getMember, createMember, updateMember, deleteMember, getMemberCards, createCard } from '../api'
import api from '../api'
import * as faceapi from 'face-api.js'
import { useVenueStore } from '../stores/venue'
import { ElMessage } from 'element-plus'

const venueStore = useVenueStore()
const members = ref([])
const photoPreview = ref(null)
const showPhotoPreview = ref(false)
function previewPhoto(row) {
  if (row.face_image) { photoPreview.value = { name: row.name, src: row.face_image }; showPhotoPreview.value = true }
}
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const cardTypes = ref([])
const venueCardTypes = computed(() => cardTypes.value.filter(ct => !ct.venue_id || ct.venue_id === venueStore.currentId))
const cards = ref([])
const consumeCards = ref([])
const memberOrders = ref([])
const ordersLoading = ref(false)
const showAdjustDialog = ref(false)
const adjustOrder = ref(null)
const adjustForm = ref({ type: 'refund', amount: 0, remark: '' })
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
const form = ref({ name: '', phone: '', gender: '', birthday: '', remark: '', venue_id: 0 })
const rechargeForm = ref({ amount: 0, payment_method: 'wechat', card_type_id: null, bonus: 0 })
const rechargeCardTypes = computed(() =>
  cardTypes.value.filter(ct => !ct.venue_id || ct.venue_id === venueStore.currentId)
)
const rechargeCardType = computed(() => {
  const ct = cardTypes.value.find(t => t.id === rechargeForm.value.card_type_id)
  return ct ? ct.category : null
})
const rechargeCardName = computed(() => {
  const ct = cardTypes.value.find(t => t.id === rechargeForm.value.card_type_id)
  return ct ? `${ctLabel(ct)} · ${ct.valid_days}天` : ''
})
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
    const s = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480, facingMode: 'user' } })
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
  if (!canvas || !video) { setStatus('摄像头未就绪'); return }
  if (video.readyState < 2) { setStatus('摄像头未就绪，请稍等'); return }

  const ctx = canvas.getContext('2d')
  canvas.width = video.videoWidth || 640; canvas.height = video.videoHeight || 480
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
  const img = canvas.toDataURL('image/jpeg', 1.0)
  setPreview(img)
  if (s) { s.getTracks().forEach(t => t.stop()) }

  setStatus('正在提取人脸特征...')
  try {
    const d = await faceapi.detectSingleFace(canvas, new faceapi.TinyFaceDetectorOptions({ inputSize: 320, scoreThreshold: 0.4 }))
      .withFaceLandmarks(true).withFaceDescriptor()
    if (d) {
      setDescriptor(JSON.stringify(Array.from(d.descriptor)))
      setStatus('✅ 已提取')
      setOk(true)
    } else {
      setDescriptor(null)
      setStatus('⚠ 未检测到人脸，仅保存照片')
      setOk(false)
    }
  } catch (e) {
    setDescriptor(null)
    setStatus('⚠ 仅保存照片（特征提取失败）')
    setOk(false)
  }
}

async function captureFace() { await doCapture(videoRef.value, canvasRef.value, (v) => facePreview.value = v, (v) => faceDescriptor.value = v, (v) => faceStatus.value = v, (v) => faceOk.value = v, stream); cameraActive.value = false }
async function captureRetake() { await doCapture(retakeVideoRef.value, retakeCanvasRef.value, (v) => retakePreview.value = v, (v) => retakeDescriptor.value = v, (v) => retakeStatus.value = v, (v) => retakeOk.value = v, retakeStream); retakeCameraActive.value = false }

function retakeFace() { facePreview.value = null; faceDescriptor.value = null; faceStatus.value = ''; faceOk.value = false; startCamera() }

function stopCamera() { stopStream(stream, (v) => cameraActive.value = v); stopStream(retakeStream, (v) => retakeCameraActive.value = v) }

// ──── 补拍 ────
const editingCards = ref([])   // 编辑时加载的会员卡列表
const editingCardId = ref(null)
const editCardEndDate = ref('')

async function editMember(m) {
  editingId.value = m.id
  form.value = { name: m.name, phone: m.phone, gender: m.gender || '', birthday: '', remark: '', venue_id: m.venue_id }
  facePreview.value = m.face_image || null
  faceDescriptor.value = null
  faceStatus.value = m.face_image ? '(已有照片，可重拍)' : ''
  faceOk.value = false
  // 加载会员卡
  try {
    const res = await getMemberCards(m.id)
    editingCards.value = (res.cards || []).filter(c => c.is_active || c.stored_value > 0 || c.total_times > 0)
    if (editingCards.value.length > 0) {
      const c = editingCards.value[0]
      editingCardId.value = c.id
      editCardEndDate.value = c.end_date || ''
    }
  } catch { editingCards.value = [] }
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
function showAdd() {
  editingId.value = null
  form.value = { name: '', phone: '', gender: '', birthday: '', remark: '', venue_id: venueStore.currentId || 1, card_type_id: null }
  facePreview.value = null; faceDescriptor.value = null; faceStatus.value = ''; faceOk.value = false
  showDialog.value = true
}
async function doDeleteMember(id) {
  try {
    await deleteMember(id)
    await load()
    ElMessage.success('已删除')
  } catch (e) {
    console.error('删除失败', e)
    ElMessage.error('删除失败')
  }
}
async function load() {
  try {
    const res = await getMembers({ keyword: keyword.value, venue_id: venueStore.currentId, page: page.value, page_size: pageSize.value })
    members.value = res.members || []
    total.value = res.total || 0
  } catch { /* */ }
}
async function search() { keyword.value = keyword.value.trim(); page.value = 1; await load() }

async function handleSave() {
  if (!form.value.name) { ElMessage.warning('请输入姓名'); return }
  if (!form.value.phone) { ElMessage.warning('请输入手机号'); return }
  if (!form.value.venue_id) { ElMessage.warning('请先在顶部选择场馆'); return }

  const data = {
    venue_id: form.value.venue_id,
    name: form.value.name,
    phone: form.value.phone,
    gender: form.value.gender || '',
    birthday: form.value.birthday || null,
    balance: form.value.balance || 0,
    remark: form.value.remark || '',
  }
  if (facePreview.value) {
    data.face_image = facePreview.value
    data.face_descriptor = faceDescriptor.value || null
  }
  const cardTypeId = form.value.card_type_id

  try {
    let memberId = editingId.value
    if (editingId.value) {
      await updateMember(editingId.value, data)
      // 如果修改了卡有效期
      if (editingCardId.value && editCardEndDate.value) {
        try {
          await api.put(`/members/${editingId.value}/cards/${editingCardId.value}/validity`, {
            end_date: editCardEndDate.value,
            remark: '手动调整有效期',
          })
          ElMessage.success('卡有效期已更新')
        } catch (e) { console.error('有效期更新失败', e) }
      }
    } else {
      const res = await createMember(data)
      memberId = res.id
    }

    if (!editingId.value && cardTypeId && memberId) {
      const ct = cardTypes.value.find(t => t.id === cardTypeId)
      if (ct) {
        const end = new Date(); end.setDate(end.getDate() + ct.valid_days)
        try {
          await createCard({
            member_id: memberId, card_type: ct.category,
            total_times: ct.total_times, stored_value: ct.total_times, price: ct.price,
            start_date: new Date().toISOString().slice(0, 10),
            end_date: end.toISOString().slice(0, 10),
          })
          if (ct.category === 'stored') {
            await updateMember(memberId, { balance: (data.balance||0) + ct.price + (ct.bonus_amount||0) })
          }
        } catch (e) { console.error('办卡失败', e) }
      }
    }
    showDialog.value = false; stopCamera(); await load(); ElMessage.success('保存成功')
  } catch (e) {
    console.error('保存失败', e)
    ElMessage.error('保存失败，请检查网络或联系管理员')
  }
}

// ──── 充值/办卡/签到/记录 ────
function ctLabel(ct) { return ct.name + (ct.bonus_amount ? ` (赠${ct.bonus_amount})` : '') }
async function onRechargeCardChange(id) {
  const ct = cardTypes.value.find(t => t.id === id)
  if (!ct) { rechargeForm.value.bonus = 0; return }
  if (ct.category === 'stored') {
    rechargeForm.value.amount = ct.price
    rechargeForm.value.bonus = ct.bonus_amount || 0
  } else {
    // 期卡：停用旧卡 + 直接办新卡
    showRechargeDialog.value = false
    try {
      const existingCards = await getMemberCards(rechargeMember.value.id)
      for (const c of (existingCards.cards || [])) {
        if (c.is_active) await api.put(`/members/${rechargeMember.value.id}/cards/${c.id}/validity`, { end_date: new Date().toISOString().slice(0,10), remark: '更换卡种' })
      }
    } catch { /* */ }
    const end = new Date(); end.setDate(end.getDate() + ct.valid_days)
    createCard({
      member_id: rechargeMember.value.id,
      card_type: ct.category, total_times: ct.total_times,
      price: ct.price, start_date: new Date().toISOString().slice(0,10),
      end_date: end.toISOString().slice(0,10),
    }).then(() => {
      load()
      ElMessage.success(`已办理${ctLabel(ct)}`)
    }).catch(() => {})
  }
}
function showRecharge(m) {
  rechargeMember.value = m
  rechargeForm.value = { amount: 0, payment_method: 'wechat', card_type_id: null, bonus: 0 }
  showRechargeDialog.value = true
}
async function handleRecharge() {
  if (rechargeCardType.value && rechargeCardType.value !== 'stored') {
    // 期卡已在 onRechargeCardChange 中处理
    return
  }
  if (!rechargeForm.value.amount) { ElMessage.warning('请输入金额'); return }
  try {
    const totalAmount = rechargeForm.value.amount + (rechargeForm.value.bonus || 0)
    await api.post('/orders', {
      venue_id: rechargeMember.value.venue_id||1,
      member_id: rechargeMember.value.id,
      order_type: 'card_recharge',
      paid_amount: rechargeForm.value.amount,
      payment_method: rechargeForm.value.payment_method,
      remark: rechargeForm.value.bonus ? `充值${rechargeForm.value.amount}赠${rechargeForm.value.bonus}` : '',
    })
    await updateMember(rechargeMember.value.id, { balance: (rechargeMember.value.balance||0) + totalAmount })
    showRechargeDialog.value = false; await load(); ElMessage.success(`充值成功，到账￥${totalAmount}`)
  } catch { /* */ }
}

function showIssueCard(m) { rechargeMember.value = m; cardForm.value = { card_type_id:null, total_times:0, price:0, start_date: new Date().toISOString().slice(0,10), end_date:'', member_id: m.id, card_type:'times' }; showIssueCardDialog.value = true }
function onCardTypeChange(id) { const ct = cardTypes.value.find(t=>t.id===id); if(ct){ cardForm.value.price=ct.price; cardForm.value.total_times=ct.total_times; cardForm.value.card_type=ct.category; const e=new Date(); e.setDate(e.getDate()+ct.valid_days); cardForm.value.end_date=e.toISOString().slice(0,10) } }
async function handleIssueCard() {
  try {
    // 停用该会员所有旧卡
    const existingCards = await getMemberCards(rechargeMember.value.id)
    for (const c of (existingCards.cards || [])) {
      if (c.is_active) await api.put(`/members/${rechargeMember.value.id}/cards/${c.id}/validity`, { end_date: new Date().toISOString().slice(0,10), remark: '更换卡种' })
    }
    await createCard({ member_id:rechargeMember.value.id, card_type: cardForm.value.card_type||'times', total_times:cardForm.value.total_times, price:cardForm.value.price, start_date:cardForm.value.start_date, end_date:cardForm.value.end_date })
    if (cardForm.value.card_type === 'stored') {
      const bonus = cardTypes.value.find(t=>t.id===cardForm.value.card_type_id)?.bonus_amount || 0
      await updateMember(rechargeMember.value.id, { balance: (rechargeMember.value.balance||0) + cardForm.value.price + bonus })
      rechargeMember.value.balance = (rechargeMember.value.balance||0) + cardForm.value.price + bonus
    }
    showIssueCardDialog.value=false; await load(); ElMessage.success('办卡成功')
  } catch { /* */ }
}

async function showConsume(m) { consumeMember.value=m; consumeForm.value={amount:0,use_card:false,card_id:null,remark:''}; try{consumeCards.value=(await getMemberCards(m.id)).cards?.filter(c=>c.is_active&&((c.stored_value||0)>(c.used_value||0)||c.total_times>c.used_times))||[]}catch{consumeCards.value=[]}; showConsumeDialog.value=true }
async function handleConsume() { try { await api.post(`/members/${consumeMember.value.id}/consume`, consumeForm.value); showConsumeDialog.value=false; await load(); ElMessage.success('扣费成功') } catch { /* */ } }

async function showOrders(m) {
  consumeMember.value = m
  memberOrders.value = []
  showOrdersDialog.value = true
  ordersLoading.value = true
  try {
    memberOrders.value = (await api.get(`/members/${m.id}/orders`, { params: { limit: 100 } })).orders || []
    // 从实际订单计算累计消费
    const total = memberOrders.value.reduce((sum, o) => {
      return sum + (o.status === 'refunded' ? -(o.paid_amount || 0) : (o.paid_amount || 0))
    }, 0)
    consumeMember.value.total_consumption = total
  } catch { memberOrders.value = [] }
  ordersLoading.value = false
}
function showAdjust(row) {
  adjustOrder.value = row
  adjustForm.value = { type: 'refund', amount: 0, remark: '' }
  showAdjustDialog.value = true
}
async function handleAdjust() {
  if (!adjustForm.value.amount) { ElMessage.warning('请输入金额'); return }
  const isRefund = adjustForm.value.type === 'refund'
  const amount = adjustForm.value.amount
  try {
    // 退费：恢复余额，创建退款记录
    if (isRefund) {
      const res = await api.post('/orders', {
        venue_id: consumeMember.value.venue_id || 1,
        member_id: consumeMember.value.id,
        order_type: 'walk_in',
        paid_amount: amount, original_amount: amount,
        payment_method: 'card',
        remark: adjustForm.value.remark || '手动退费调整',
      })
      if (res?.id) await api.put(`/orders/${res.id}/status?status=refunded`)
      await api.put(`/members/${consumeMember.value.id}`, {
        balance: (consumeMember.value.balance || 0) + amount,
      })
    } else {
      if ((consumeMember.value.balance || 0) < amount) { ElMessage.warning('余额不足'); return }
      const res = await api.post('/orders', {
        venue_id: consumeMember.value.venue_id || 1,
        member_id: consumeMember.value.id,
        order_type: 'walk_in',
        paid_amount: amount, original_amount: amount,
        payment_method: 'card',
        remark: adjustForm.value.remark || '手动补扣调整',
      })
      if (res?.id) await api.put(`/orders/${res.id}/status?status=checked_in`)
      const newTotal = (consumeMember.value.total_consumption || 0) + amount
      await api.put(`/members/${consumeMember.value.id}`, {
        balance: Math.max(0, (consumeMember.value.balance || 0) - amount),
        total_consumption: newTotal,
      })
    }
    showAdjustDialog.value = false
    consumeMember.value.balance = (consumeMember.value.balance || 0) + (isRefund ? amount : -amount)
    // 退费=减少累计消费，补扣=增加累计消费
    const totalChange = isRefund ? -amount : amount
    await api.put(`/members/${consumeMember.value.id}`, {
      total_consumption: Math.max(0, (consumeMember.value.total_consumption || 0) + totalChange),
    })
    memberOrders.value = (await api.get(`/members/${consumeMember.value.id}/orders`)).orders || []
    await load()
    ElMessage.success(isRefund ? '退费成功' : '补扣成功')
  } catch { /* */ }
}

function cardTypeLabel(types) {
  if (!types) return ''
  return types.split(',').map(t => ({ stored: '储值卡', times: '次卡', month: '月卡', year: '年卡' }[t.trim()] || t)).join('/')
}

function cardLabel(c) {
  if (c.card_type === 'stored') return `储值卡 余额¥${((c.stored_value||0) - (c.used_value||0)).toFixed(2)}`
  return `${c.card_type} 剩${c.total_times - c.used_times}次`
}

// ──── 有效期倒计时（天为单位）────
const now = ref(Date.now())
let countdownTimer = null

function countdownDays(endDateStr) {
  if (!endDateStr) return ''
  const end = new Date(endDateStr).getTime()
  const diff = end - now.value
  if (diff <= 0) return '已过期'
  const days = Math.ceil(diff / 86400000)
  return `${days}天`
}

function expireClass(endDateStr) {
  if (!endDateStr) return ''
  const end = new Date(endDateStr).getTime()
  const diff = end - now.value
  if (diff <= 0) return 'expired'
  if (diff < 3 * 86400000) return 'urgent'
  if (diff < 7 * 86400000) return 'soon'
  return 'ok'
}

const selectedCardType = computed(() => {
  const c = consumeCards.value.find(c => c.id === consumeForm.value.card_id)
  return c?.card_type || ''
})
const selectedCardRemaining = computed(() => {
  const c = consumeCards.value.find(c => c.id === consumeForm.value.card_id)
  if (!c) return 0
  return (c.stored_value || 0) - (c.used_value || 0)
})

onMounted(async () => {
  try { cardTypes.value = (await api.get('/card-types')).card_types || [] } catch { /* */ }
  const M = '/models'
  try { await Promise.all([faceapi.nets.tinyFaceDetector.loadFromUri(M), faceapi.nets.faceLandmark68TinyNet.loadFromUri(M), faceapi.nets.faceRecognitionNet.loadFromUri(M)]) } catch { /* */ }
  await load()
  // 有效期每天刷新（每小时检查一次）
  countdownTimer = setInterval(() => { now.value = Date.now() }, 3600000)
})

watch(() => venueStore.currentId, () => { load() })

onBeforeUnmount(() => { if (countdownTimer) clearInterval(countdownTimer) })
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 10px; }
.actions { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
.btn-row { display: flex; gap: 6px; flex-wrap: nowrap; white-space: nowrap; padding: 4px 0; }
.info-box { background: #F5F7FA; padding: 12px; border-radius: 4px; margin-bottom: 16px; }
.info-box p { margin: 4px 0; }
.face-section { border: 1px dashed #DCDFE6; border-radius: 8px; padding: 10px; text-align: center; }
.face-title { margin: 0 0 8px; font-size: 13px; color: #606266; }
.face-camera-mini { position: relative; width: 320px; height: 240px; margin: 0 auto; background: #000; border-radius: 4px; overflow: hidden; }
.face-camera-mini video, .face-preview-mini { width: 100%; height: 100%; object-fit: cover; }
.face-btns { margin-top: 8px; display: flex; gap: 5px; justify-content: center; }
.face-status { font-size: 12px; margin: 6px 0 0; }

/* 有效期标签 */
.expire-tag {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  border: 1px solid;
}
.expire-tag.ok     { color: #67C23A; border-color: #67C23A; background: #f0f9eb; }
.expire-tag.soon   { color: #409EFF; border-color: #409EFF; background: #ecf5ff; }
.expire-tag.urgent { color: #E6A23C; border-color: #E6A23C; background: #fdf6ec; font-weight: 700; }
.expire-tag.expired{ color: #F56C6C; border-color: #F56C6C; background: #fef0f0; font-weight: 700; }
.orders-summary { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.orders-content { animation: fadeSlideIn 0.35s ease; }
.orders-loading { text-align: center; padding: 60px 0; }
@keyframes fadeSlideIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
