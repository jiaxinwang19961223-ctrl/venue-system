<template>
  <view class="page">
    <view class="venue-header">
      <text class="venue-name">{{ venue?.name || '加载中...' }}</text>
      <text class="tag" :class="venue?.status === 'open' ? 'tag-green' : 'tag-gray'">
        {{ venue?.status === 'open' ? '营业中' : '休息中' }}
      </text>
    </view>
    <view class="venue-meta" v-if="venue">
      <text class="meta-item">📍 {{ venue.address || '地址待完善' }}</text>
      <text class="meta-item">🕐 {{ venue.business_hours || '09:00-22:00' }}</text>
    </view>
    <view class="venue-meta" v-if="venue">
      <text class="meta-item" v-if="venue.phone">📞 {{ venue.phone }}</text>
    </view>
    <view class="venue-desc" v-if="venue?.description">
      <text>{{ venue.description }}</text>
    </view>

    <text class="section-title">可用场地</text>
    <view class="glass field-card" v-for="f in fields" :key="f.id" :data-id="f.id" :data-name="f.name" :data-price="f.price_per_hour" @tap="goBook">
      <text class="field-type-tag" :class="'ft-' + f.field_type">{{ typeLabel(f.field_type) }}</text>
      <text class="field-name">{{ f.name }}</text>
      <view class="field-price">
        <text class="price-num">¥{{ f.price_per_hour }}</text>
        <text class="price-unit">/小时</text>
      </view>
      <text class="field-capacity" v-if="f.capacity">可容纳 {{ f.capacity }} 人</text>
      <view class="btn btn-primary field-btn">立即预订</view>
    </view>
    <view class="empty-state" v-if="!loading && fields.length === 0">
      <text class="empty-text">该球馆暂无可用场地</text>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { getVenue } from '../../api'

let venueId = null
const venue = ref(null)
const fields = ref([])
const loading = ref(true)

const fieldTypeMap = {
  badminton: '羽毛球', basketball: '篮球', pingpong: '乒乓球',
  tennis: '网球', football: '足球', swimming: '游泳', fitness: '健身', other: '其他',
}
function typeLabel(t) { return fieldTypeMap[t] || t }
function goBook(e) {
  const { id, name, price } = e.currentTarget.dataset
  if (!id) return
  uni.navigateTo({
    url: `/pages/booking/booking?venueId=${venueId}&fieldId=${id}&fieldName=${encodeURIComponent(name || '')}&price=${price || 0}`
  })
}

async function loadData() {
  const pages = getCurrentPages()
  const page = pages[pages.length - 1]
  const options = page.$page?.options || page.options || {}
  venueId = parseInt(options.id)
  if (!venueId) { uni.showToast({ title: '参数错误', icon: 'none' }); uni.navigateBack(); return }
  loading.value = true
  try {
    const res = await getVenue(venueId)
    venue.value = res
    fields.value = res.fields || []
  } catch { /* */ }
  finally { loading.value = false }
}
loadData()
</script>

<style scoped>
.venue-header { display: flex; align-items: center; gap: 16rpx; margin-bottom: 12rpx; }
.venue-name { font-size: 44rpx; font-weight: 800; color: #1D1D1F; letter-spacing: -0.5px; }
.venue-meta { display: flex; gap: 32rpx; margin-bottom: 12rpx; flex-wrap: wrap; }
.meta-item { font-size: 24rpx; color: #86868B; }
.venue-desc {
  padding: 20rpx 24rpx; margin-bottom: 24rpx;
  background: rgba(64,158,255,0.04); border-radius: 16rpx;
  font-size: 24rpx; color: #606266; line-height: 1.6;
}

.field-card { padding: 32rpx 28rpx; margin-bottom: 20rpx; text-align: center; }
.field-type-tag {
  font-size: 20rpx; padding: 4rpx 14rpx; border-radius: 8rpx;
  display: inline-block; margin-bottom: 14rpx; font-weight: 500;
}
.ft-badminton { background: rgba(103,194,58,0.12); color: #4A9E2F; }
.ft-basketball { background: rgba(230,162,60,0.12); color: #C7851F; }
.ft-pingpong { background: rgba(245,108,108,0.12); color: #D94848; }
.ft-tennis { background: rgba(0,0,0,0.06); color: #86868B; }
.ft-football { background: rgba(64,158,255,0.12); color: #2B7DE9; }
.ft-swimming { background: rgba(64,158,255,0.1); color: #2B7DE9; }
.ft-fitness { background: rgba(124,92,252,0.1); color: #6B4FE0; }

.field-name { display: block; font-size: 36rpx; font-weight: 700; color: #1D1D1F; margin-bottom: 8rpx; }
.field-price { margin-bottom: 4rpx; }
.price-num { font-size: 52rpx; font-weight: 800; color: #E6A23C; }
.price-unit { font-size: 24rpx; color: #86868B; }
.field-capacity { display: block; font-size: 22rpx; color: #A1A1A6; margin-bottom: 20rpx; }
.field-btn { margin-top: 8rpx; }
</style>
