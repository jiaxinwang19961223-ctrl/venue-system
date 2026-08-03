<template>
  <view class="page">
    <view class="quick-row">
      <view class="glass quick-card" @tap="goFirstVenue">
        <image class="quick-icon" src="/static/icon-booking.png" mode="aspectFit" />
        <view class="quick-text">
          <text class="quick-title">立即订场</text>
          <text class="quick-desc">选择场馆和时段</text>
        </view>
        <text class="quick-arrow">›</text>
      </view>
      <view class="glass quick-card" @tap="goMember">
        <image class="quick-icon" src="/static/icon-member.png" mode="aspectFit" />
        <view class="quick-text">
          <text class="quick-title">会员中心</text>
          <text class="quick-desc">办理会员，享优惠</text>
        </view>
        <text class="quick-arrow">›</text>
      </view>
    </view>

    <text class="section-title">全部球馆</text>
    <view class="glass venue-card" v-for="venue in venues" :key="venue.id" :data-id="venue.id" @tap="goVenue">
      <view class="venue-top">
        <view class="venue-info">
          <view class="venue-name-row">
            <text class="venue-name">{{ venue.name }}</text>
            <text class="district-tag" v-if="venue.district">{{ venue.district }}</text>
          </view>
          <view class="venue-addr">
            <image class="addr-pin" src="/static/icons/pin-blue.svg" mode="aspectFit" />
            <text>{{ venue.address || '地址待完善' }}</text>
          </view>
        </view>
        <text class="tag" :class="venue.status === 'open' ? 'tag-green' : 'tag-gray'">
          {{ venue.status === 'open' ? '营业中' : '休息中' }}
        </text>
      </view>
      <view class="venue-bottom">
        <text class="venue-hours">🕐 {{ venue.business_hours || '09:00-22:00' }}</text>
        <text class="action-link">去订场 →</text>
      </view>
    </view>
    <view class="empty-state" v-if="!loading && venues.length === 0">
      <text class="empty-icon">🏟</text>
      <text class="empty-text">{{ error || '暂无可订球馆' }}</text>
      <text class="empty-sub" v-if="error" style="color:#409EFF;margin-top:16rpx" @tap="loadVenues">点击重试</text>
    </view>

    <!-- 加载中 -->
    <view class="loading-state" v-if="loading">
      <text class="loading-text">加载中...</text>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { getVenues } from '../../api'

const venues = ref([])
const loading = ref(true)
const error = ref('')

async function loadVenues() {
  loading.value = true
  error.value = ''
  try {
    console.log('[首页] 开始加载球馆列表...')
    const res = await getVenues()
    console.log('[首页] 球馆数据:', JSON.stringify(res))
    venues.value = res.venues || []
  } catch (e) {
    console.error('[首页] 加载失败:', e)
    error.value = '加载失败，下拉刷新重试'
  } finally {
    loading.value = false
  }
}

function goFirstVenue() {
  if (venues.value.length) {
    uni.navigateTo({ url: `/pages/venue/venue?id=${venues.value[0].id}` })
  } else {
    uni.showToast({ title: '暂无可用球馆', icon: 'none' })
  }
}
function goVenue(e) {
  const id = e.currentTarget.dataset.id
  if (id) uni.navigateTo({ url: `/pages/venue/venue?id=${id}` })
}
function goMember() { uni.switchTab({ url: '/pages/member/member' }) }

onShow(() => {
  console.log('[首页] onShow 触发')
  const token = uni.getStorageSync('token')
  console.log('[首页] token存在:', !!token)
  if (!token) {
    console.log('[首页] 无token，跳转登录')
    uni.reLaunch({ url: '/pages/login/login' })
    return
  }
  loadVenues()
})
</script>

<style scoped>
.quick-row { display: flex; gap: 16rpx; margin-bottom: 36rpx; }
.quick-card {
  flex: 1; display: flex; align-items: center; gap: 16rpx;
  padding: 28rpx 24rpx;
}
.quick-icon { width: 52rpx; height: 52rpx; flex-shrink: 0; }
.quick-text { flex: 1; }
.quick-title { font-size: 30rpx; font-weight: 700; color: #1D1D1F; display: block; }
.quick-desc { font-size: 22rpx; color: #86868B; margin-top: 4rpx; display: block; }
.quick-arrow { font-size: 32rpx; color: #C7C7CC; }

.venue-card { padding: 28rpx; margin-bottom: 20rpx; }
.venue-top { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16rpx; }
.venue-name-row { display: flex; align-items: center; gap: 12rpx; }
.venue-name { font-size: 34rpx; font-weight: 700; color: #1D1D1F; }
.district-tag {
  font-size: 20rpx; padding: 2rpx 12rpx; border-radius: 8rpx;
  background: rgba(64,158,255,0.08); color: #409EFF; font-weight: 500;
  flex-shrink: 0;
}
.venue-addr { font-size: 24rpx; color: #86868B; display: flex; align-items: center; gap: 6rpx; margin-top: 6rpx; }
.addr-pin { width: 28rpx; height: 28rpx; flex-shrink: 0; }
.venue-bottom { display: flex; justify-content: space-between; align-items: center; }
.venue-hours { font-size: 24rpx; color: #86868B; }
.action-link { font-size: 26rpx; color: #409EFF; font-weight: 600; }
.loading-state { padding: 80rpx 0; text-align: center; }
.loading-text { font-size: 28rpx; color: #A1A1A6; }
</style>
