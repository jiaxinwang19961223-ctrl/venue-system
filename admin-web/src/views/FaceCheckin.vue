<template>
  <div>
    <div class="page-header">
      <h3><i class="ri-camera-line"></i> 人脸签到</h3>
      <el-tag :type="modelReady ? 'success' : modelError ? 'danger' : 'warning'">{{ modelReady ? '模型就绪' : modelError ? '模型加载失败' : '加载模型中...' }}</el-tag>
    </div>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header>摄像头 <span v-if="detecting" style="color:#67C23A">● 检测中</span></template>
          <div class="camera-wrap">
            <video ref="videoRef" autoplay playsinline width="400" height="300"></video>
            <canvas ref="overlayRef" width="400" height="300" class="overlay-canvas"></canvas>
          </div>
          <div style="margin-top:12px;text-align:center">
            <el-button type="primary" @click="startDetection" :disabled="detecting || !modelReady">
              <i class="ri-camera-line"></i> {{ detecting ? '检测中...' : '开始检测' }}
            </el-button>
            <el-button @click="stopDetection" :disabled="!detecting">停止</el-button>
          </div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card>
          <template #header>识别结果</template>
          <div v-if="!detectedMember && !noMatch" class="no-result">
            <i class="ri-user-search-line" style="font-size:48px;color:#DCDFE6"></i>
            <p>将人脸对准摄像头，自动匹配</p>
            <p style="font-size:12px;color:#999">已录入 {{ labeledDescriptors.length }} 人</p>
          </div>
          <div v-else-if="noMatch" class="no-result">
            <i class="ri-user-unfollow-line" style="font-size:48px;color:#E6A23C"></i>
            <p style="color:#E6A23C">未识别到已录入会员</p>
            <p style="font-size:12px;color:#999">请确认该会员已录入人脸</p>
          </div>
          <div v-else class="detected">
            <el-avatar :src="detectedMember.face_image" :size="80" />
            <h2>{{ detectedMember.name }}</h2>
            <p>{{ detectedMember.phone }}</p>
            <el-tag type="success" size="large">✅ 匹配成功</el-tag>
            <p class="match-score">吻合度 {{ matchDistance }}</p>
            <div class="member-info">
              <p>余额：<strong>¥{{ detectedMember.balance?.toFixed(2) }}</strong></p>
              <p v-if="checkinForm.amount > 0" style="color:#E6A23C">扣费后：<strong>¥{{ Math.max(0, (detectedMember.balance || 0) - checkinForm.amount).toFixed(2) }}</strong></p>
            </div>
            <el-divider />
            <el-form :model="checkinForm" label-width="80px" size="default">
              <el-form-item label="消费金额">
                <el-input-number v-model="checkinForm.amount" :min="0" :step="10" :precision="2" style="width:100%" controls-position="right" />
              </el-form-item>
              <el-form-item label="消费项目">
                <el-input v-model="checkinForm.remark" placeholder="如：买水、租拍、打球场租…" />
              </el-form-item>
            </el-form>
            <el-button type="primary" size="large" @click="doCheckin" style="margin-top:8px;width:100%" :disabled="checkinForm.amount > (detectedMember.balance || 0)">
              <i class="ri-check-double-line"></i> 确认扣费签到
            </el-button>
            <p v-if="checkinForm.amount > (detectedMember.balance || 0)" style="color:#F56C6C;font-size:12px;margin-top:4px">⚠ 余额不足</p>
          </div>
        </el-card>

        <el-card style="margin-top:16px">
          <template #header>今日签到记录 ({{ checkins.length }})</template>
          <el-timeline v-if="checkins.length">
            <el-timeline-item v-for="c in checkins" :key="c.id" :timestamp="c.time" placement="top">
              {{ c.name }} — {{ c.type_label }}
            </el-timeline-item>
          </el-timeline>
          <p v-else style="color:#999;text-align:center">暂无</p>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { getMembers } from '../api'
import api from '../api'
import * as faceapi from 'face-api.js'
import { useVenueStore } from '../stores/venue'
import { ElMessage } from 'element-plus'

const venueStore = useVenueStore()
const videoRef = ref(null)
const overlayRef = ref(null)
const detecting = ref(false)
const detectedMember = ref(null)
const noMatch = ref(false)
const members = ref([])
const checkins = ref([])
const modelReady = ref(false)
const modelError = ref(false)
const matchDistance = ref('')
const labeledDescriptors = ref([])

const checkinForm = reactive({ amount: 0, remark: '' })
let stream = null
let detectionInterval = null
let faceMatcher = null

const MODEL_URL = '/models'

async function loadModels() {
  try {
    console.log('开始加载人脸模型...', MODEL_URL)
    await faceapi.nets.tinyFaceDetector.loadFromUri(MODEL_URL)
    console.log('tinyFaceDetector 加载完成')
    await faceapi.nets.faceLandmark68TinyNet.loadFromUri(MODEL_URL)
    console.log('faceLandmark68TinyNet 加载完成')
    await faceapi.nets.faceRecognitionNet.loadFromUri(MODEL_URL)
    console.log('faceRecognitionNet 加载完成')
    modelReady.value = true
    ElMessage.success('人脸模型就绪')
  } catch (e) {
    console.error('模型加载失败', e)
    modelError.value = true
    ElMessage.error('人脸模型加载失败: ' + (e.message || '未知错误'))
  }
}

async function buildFaceMatcher() {
  // 加载所有有描述符的会员
  try {
    const res = await getMembers({ venue_id: venueStore.currentId })
    members.value = (res.members || []).filter(m => m.face_descriptor && m.face_image)
  } catch { return }

  if (!members.value.length) {
    ElMessage.warning('没有已录入人脸的会员')
    return
  }

  // 构建 LabeledFaceDescriptors
  const descriptors = members.value.map(m => {
    try {
      const descriptor = JSON.parse(m.face_descriptor)
      return new faceapi.LabeledFaceDescriptors(
        `${m.id}_${m.name}`,
        [new Float32Array(descriptor)]
      )
    } catch {
      return null
    }
  }).filter(Boolean)

  labeledDescriptors.value = descriptors
  faceMatcher = new faceapi.FaceMatcher(descriptors, 0.45)
}

async function startCamera() {
  try {
    stream = await navigator.mediaDevices.getUserMedia({
      video: { width: 400, height: 300, facingMode: 'user' }
    })
    if (videoRef.value) videoRef.value.srcObject = stream
    return true
  } catch {
    ElMessage.error('无法访问摄像头')
    return false
  }
}

async function startDetection() {
  await buildFaceMatcher()
  if (!faceMatcher || !labeledDescriptors.value.length) return

  const ok = await startCamera()
  if (!ok) return

  detecting.value = true
  noMatch.value = false
  detectedMember.value = null

  let detectTimer = null

  async function detectOnce() {
    if (!videoRef.value || !detecting.value) return
    try {
      const result = await faceapi
        .detectSingleFace(videoRef.value, new faceapi.TinyFaceDetectorOptions({ inputSize: 160, scoreThreshold: 0.4 }))
        .withFaceLandmarks(true)
        .withFaceDescriptor()

      const canvas = overlayRef.value
      const ctx = canvas?.getContext('2d')
      ctx?.clearRect(0, 0, 400, 300)

      if (!result) {
        if (!detectedMember.value) noMatch.value = false
        detectTimer = setTimeout(detectOnce, 800) // 没人 → 快扫
        return
      }

      const box = result.detection.box
      ctx.strokeStyle = '#409EFF'
      ctx.lineWidth = 2
      ctx.strokeRect(box.x, box.y, box.width, box.height)

      const match = faceMatcher.findBestMatch(result.descriptor)

      if (match.label === 'unknown' || match.distance > 0.45) {
        detectedMember.value = null
        noMatch.value = true
        ctx.strokeStyle = '#E6A23C'
        ctx.strokeRect(box.x, box.y, box.width, box.height)
        if (match.label !== 'unknown') {
          matchDistance.value = `最近: ${match.label.split('_')[1]} 距离${match.distance.toFixed(2)}`
        } else {
          matchDistance.value = ''
        }
        detectTimer = setTimeout(detectOnce, 800) // 未识别 → 快扫
        return
      }

      // 匹配成功 → 锁定，不再检测
      noMatch.value = false
      const memberId = parseInt(match.label.split('_')[0])
      const prevId = detectedMember.value?.id
      detectedMember.value = members.value.find(m => m.id === memberId)
      const similarity = ((1 - match.distance) * 100).toFixed(1)
      matchDistance.value = `${similarity}%`
      if (prevId !== memberId) {
        Object.assign(checkinForm, { amount: 0, remark: '' })
      }

      ctx.strokeStyle = '#67C23A'
      ctx.lineWidth = 3
      ctx.strokeRect(box.x, box.y, box.width, box.height)
      ctx.fillStyle = '#67C23A'
      ctx.font = '14px sans-serif'
      ctx.fillText(match.label.split('_')[1], box.x, box.y - 8)
      // 识别成功后不再继续检测，保持稳定

    } catch { detectTimer = setTimeout(detectOnce, 2000) }
  }

  detectTimer = setTimeout(detectOnce, 500)
}

function stopDetection() {
  clearTimeout(detectionInterval)
  detecting.value = false
  detectedMember.value = null
  noMatch.value = false
  matchDistance.value = ''
  if (stream) { stream.getTracks().forEach(t => t.stop()); stream = null }
  const canvas = overlayRef.value
  if (canvas) canvas.getContext('2d').clearRect(0, 0, 400, 300)
}

async function doCheckin() {
  if (!detectedMember.value) return
  const m = detectedMember.value
  try {
    const res = await api.post(`/members/${m.id}/consume`, {
      venue_id: venueStore.currentId,
      amount: checkinForm.amount || 0,
      use_card: false,
      remark: checkinForm.remark || '人脸签到',
    })
    checkins.value.unshift({
      id: Date.now(),
      name: m.name,
      time: new Date().toLocaleTimeString(),
      type_label: `¥${(checkinForm.amount || 0).toFixed(2)} ${checkinForm.remark || '签到'}`,
    })
    if (res.balance !== undefined) {
      m.balance = res.balance
      m.total_consumption = res.total_consumption
    }
    ElMessage.success(`${m.name} 扣费 ¥${(checkinForm.amount || 0).toFixed(2)}`)
    // 扣费后清零，防多扣
    Object.assign(checkinForm, { amount: 0, remark: '' })
  } catch { /* */ }
}

onMounted(() => { loadModels() })
onUnmounted(() => { stopDetection() })
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.camera-wrap { position: relative; width: 400px; height: 300px; margin: 0 auto; background: #000; border-radius: 8px; overflow: hidden; }
.camera-wrap video, .overlay-canvas { position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; }
.overlay-canvas { z-index: 2; }
.no-result { text-align: center; padding: 40px 0; color: #909399; }
.detected { text-align: center; padding: 10px 0; }
.detected h2 { margin: 10px 0 4px; }
.match-score { font-size: 12px; color: #909399; margin: 4px 0 0; }
.member-info { background: #F5F7FA; padding: 10px; border-radius: 8px; margin-top: 12px; text-align: left; }
.member-info p { margin: 4px 0; }
</style>
