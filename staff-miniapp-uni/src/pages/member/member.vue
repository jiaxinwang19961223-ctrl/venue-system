<template>
  <view class="page">
    <!-- 搜索栏 -->
    <view class="glass search-bar">
      <view class="search-input-row">
        <image class="search-icon" src="/static/icons/search.svg" mode="aspectFit" />
        <input class="search-input" v-model="keyword" placeholder="搜索会员姓名或手机号"
          @confirm="doSearch" confirm-type="search" />
      </view>
    </view>

    <!-- 会员列表 -->
    <view class="glass member-card" v-for="m in members" :key="m.id"
      @tap="goDetail(m.id)">
      <view class="flex-between">
        <view>
          <text class="member-name">{{ m.name }}</text>
          <text class="member-phone" style="margin-left:16rpx">{{ m.phone }}</text>
        </view>
        <text class="tag" :class="m.is_active ? 'tag-green' : 'tag-gray'">
          {{ m.is_active ? '活跃' : '停用' }}
        </text>
      </view>
      <view class="flex-between" style="margin-top:16rpx">
        <view>
          <text class="text-muted" style="font-size:24rpx">余额 <text style="color:#1D1D1F;font-weight:600">¥{{ m.balance }}</text></text>
          <text class="text-muted" style="font-size:24rpx;margin-left:20rpx"
            v-if="m.card_types">卡: {{ m.card_types }}</text>
        </view>
        <text class="tag tag-blue" v-if="m.card_remaining && m.card_remaining > 0">
          剩{{ m.card_remaining }}次
        </text>
      </view>
      <text class="text-muted" style="font-size:22rpx;margin-top:8rpx;display:block"
        v-if="m.last_consume_time">
        最近消费: {{ formatDate(m.last_consume_time) }}
      </text>
    </view>

    <view class="empty-state" v-if="!loading && members.length === 0 && searched">
      <image class="empty-icon" src="/static/icons/user.svg" mode="aspectFit" />
      <text class="empty-text">未找到会员</text>
      <text class="empty-sub">尝试其他关键词或确认会员已录入</text>
    </view>
    <view class="empty-state" v-if="!loading && !searched && members.length === 0">
      <image class="empty-icon" src="/static/icons/search.svg" mode="aspectFit" />
      <text class="empty-text">搜索会员</text>
      <text class="empty-sub">输入姓名或手机号搜索</text>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { getMembers } from '../../api'
import { useUserStore } from '../../store/user'

const store = useUserStore()
const keyword = ref('')
const members = ref([])
const loading = ref(false)
const searched = ref(false)

async function doSearch() {
  if (!keyword.value.trim()) return
  loading.value = true
  searched.value = true
  try {
    const res = await getMembers({ keyword: keyword.value.trim() })
    members.value = res.members || []
  } catch { /* */ }
  finally { loading.value = false }
}

function goDetail(id) {
  uni.navigateTo({ url: `/pages/member-detail/member-detail?id=${id}` })
}

function formatDate(t) {
  if (!t) return ''
  return t.slice(0, 16).replace('T', ' ')
}
</script>

<style scoped>
.search-bar { padding: 16rpx 24rpx; margin-bottom: 24rpx; }
.search-input-row { display: flex; align-items: center; gap: 12rpx; }
.search-icon { width: 40rpx; height: 40rpx; flex-shrink: 0; }
.search-input { flex: 1; font-size: 28rpx; height: 64rpx; }
.member-card { padding: 24rpx; margin-bottom: 16rpx; }
.member-name { font-size: 32rpx; font-weight: 600; color: #1D1D1F; }
.member-phone { font-size: 26rpx; color: #86868B; }
</style>
