<template>
  <view class="page">
    <!-- 未办理会员 -->
    <view class="glass card-pad" v-if="!loading && !member">
      <text class="empty-icon" style="font-size:72rpx">👤</text>
      <text class="empty-text">您还未办理会员</text>
      <view class="form" style="margin-top:36rpx;text-align:left">
        <view class="fi">
          <text class="fl">选择球馆</text>
          <picker :range="venueNames" @change="onVenueChange">
            <view class="input-glass picker-like">
              <text :class="{ ph: !form.venue_name }">{{ form.venue_name || '请选择球馆' }}</text>
            </view>
          </picker>
        </view>
        <view class="fi">
          <text class="fl">姓名</text>
          <input class="input-glass" v-model="form.name" placeholder="请输入姓名" />
        </view>
        <view class="fi">
          <text class="fl">性别</text>
          <view class="radio-row">
            <view class="glass radio-btn" :class="{ on: form.gender === '男' }" @tap="form.gender = '男'">男</view>
            <view class="glass radio-btn" :class="{ on: form.gender === '女' }" @tap="form.gender = '女'">女</view>
          </view>
        </view>
        <view class="fi">
          <text class="fl">生日</text>
          <picker mode="date" :end="today" @change="onBirthdayChange">
            <view class="input-glass picker-like">
              <text :class="{ ph: !form.birthday }">{{ form.birthday || '选填' }}</text>
            </view>
          </picker>
        </view>
        <view class="btn btn-primary" style="margin-top:8rpx" @tap="doRegister">立即办理</view>
      </view>
    </view>

    <!-- 已办理 -->
    <template v-if="member">
      <view class="member-card">
        <view class="mc-inner">
          <view class="mh">
            <view class="mav">👤</view>
            <view class="mi">
              <view class="mnr">
                <text class="mn">{{ member.name }}</text>
                <text class="mlt" v-if="member.level_name">{{ member.level_name }}</text>
              </view>
              <text class="mm">{{ member.phone }} · {{ member.gender || '未设置' }} · {{ member.venue_name }}</text>
            </view>
          </view>
          <view class="sr">
            <view class="si"><text class="sv">¥{{ (member.balance||0).toFixed(2) }}</text><text class="sl">余额</text></view>
            <view class="si"><text class="sv">¥{{ (member.total_recharge||0).toFixed(2) }}</text><text class="sl">累计充值</text></view>
            <view class="si"><text class="sv">¥{{ (member.total_consumption||0).toFixed(2) }}</text><text class="sl">累计消费</text></view>
            <view class="si"><text class="sv">{{ member.points||0 }}</text><text class="sl">积分</text></view>
          </view>
        </view>
      </view>

      <text class="section-title">我的会员卡</text>
      <view v-if="member.cards && member.cards.length">
        <view class="glass card-item" v-for="c in member.cards" :key="c.id" :class="{ dim: !c.is_active || isExpired(c) }">
          <text class="ctag" :class="'ct-' + c.card_type">{{ cardTypeLabel(c.card_type) }}</text>
          <text class="ctitle">{{ cardTypeLabel(c.card_type) }}卡</text>
          <text class="cdetail" v-if="c.card_type === 'stored'">储值 ¥{{ (c.stored_value||0).toFixed(0) }} · 已用 ¥{{ (c.used_value||0).toFixed(0) }}</text>
          <text class="cdetail" v-else>{{ c.used_times||0 }} / {{ c.total_times||0 }} 次</text>
          <view class="cex"><text>有效期至 {{ c.end_date || '永久' }}</text><text class="etag" v-if="!c.is_active">已失效</text></view>
        </view>
      </view>
      <view class="empty-state" style="padding:40rpx 0" v-else><text class="empty-text">暂无会员卡</text></view>

      <text class="section-title">选购卡种</text>
      <view v-if="cardTypes.length">
        <view class="glass ct-card" v-for="ct in cardTypes" :key="ct.id">
          <text class="ctn">{{ ct.name }}</text>
          <text class="ctp">¥{{ ct.price }}</text>
          <text class="ctm">
            <text v-if="ct.category==='stored'">储值 {{ ct.total_times }} 元</text>
            <text v-else>{{ ct.total_times }} 次</text>
            <text v-if="ct.valid_days"> · {{ ct.valid_days }}天有效</text>
          </text>
          <view class="btn btn-primary" style="margin-top:20rpx" @tap="doBuy(ct)">立即购买</view>
        </view>
      </view>
      <view class="empty-state" style="padding:40rpx 0" v-else><text class="empty-text">暂无可购卡种</text></view>
    </template>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { getMyMember, registerMember, buyCard, getCardTypes } from '../../api'
import { useVenueStore } from '../../store/venue'
import { useUserStore } from '../../store/user'

const venueStore = useVenueStore(), userStore = useUserStore()
const member = ref(null), cardTypes = ref([]), loading = ref(true)
const today = new Date().toISOString().slice(0, 10)
const form = ref({ venue_id: null, venue_name: '', name: '', gender: '男', birthday: '' })
const venueNames = computed(() => venueStore.venues.map(v => v.name))

const clMap = { stored: '储值', month: '月卡', season: '季卡', year: '年卡', times: '次卡', custom: '自定义' }
function cardTypeLabel(t) { return clMap[t] || t }
function isExpired(c) { return c.end_date && new Date(c.end_date) < new Date() }
function onVenueChange(e) { const v = venueStore.venues[e.detail.value]; if (v) { form.value.venue_id = v.id; form.value.venue_name = v.name } }
function onBirthdayChange(e) { form.value.birthday = e.detail.value }

async function loadData() {
  loading.value = true
  try {
    await venueStore.load()
    if (venueStore.currentId && !form.value.venue_id) { form.value.venue_id = venueStore.currentId; form.value.venue_name = venueStore.currentName }
    if (!form.value.name) form.value.name = userStore.userName || ''
    try { member.value = await getMyMember() } catch (e) { member.value = null }
    try { const res = await getCardTypes(); cardTypes.value = res.card_types || [] } catch { /* */ }
  } finally { loading.value = false }
}
async function doRegister() {
  if (!form.value.venue_id) return uni.showToast({ title: '请选择球馆', icon: 'none' })
  if (!form.value.name) return uni.showToast({ title: '请输入姓名', icon: 'none' })
  try { await registerMember({ venue_id: form.value.venue_id, name: form.value.name, gender: form.value.gender, birthday: form.value.birthday || undefined }); uni.showToast({ title: '会员办理成功', icon: 'success' }); loadData() } catch { /* */ }
}
async function doBuy(ct) {
  const res = await new Promise(r => { uni.showModal({ title: '购买会员卡', content: `确认购买「${ct.name}」？金额：¥${ct.price}`, success: r }) })
  if (!res.confirm) return
  try { await buyCard({ card_type_id: ct.id }); uni.showToast({ title: '购卡成功！', icon: 'success' }); loadData() } catch { /* */ }
}

onShow(() => { const token = uni.getStorageSync('token'); if (!token) { uni.reLaunch({ url: '/pages/login/login' }); return }; loadData() })
</script>

<style scoped>
.card-pad { padding: 48rpx 32rpx; text-align: center; }
.fi { margin-bottom: 24rpx; text-align: left; }
.fl { font-size: 26rpx; color: #86868B; margin-bottom: 10rpx; display: block; font-weight: 500; }
.picker-like { display: flex; align-items: center; }
.ph { color: #C7C7CC; }
.radio-row { display: flex; gap: 20rpx; }
.radio-btn { padding: 16rpx 44rpx; font-size: 28rpx; color: #86868B; text-align: center; }
.radio-btn.on { border-color: #409EFF; color: #409EFF; background: rgba(64,158,255,0.06); }

.member-card { background: linear-gradient(145deg, #409EFF 0%, #2B7DE9 100%); border-radius: 28rpx; padding: 36rpx; margin-bottom: 36rpx; color: #fff; }
.mh { display: flex; align-items: center; gap: 20rpx; margin-bottom: 32rpx; }
.mav { width: 88rpx; height: 88rpx; border-radius: 50%; background: rgba(255,255,255,0.18); display: flex; align-items: center; justify-content: center; font-size: 44rpx; }
.mnr { display: flex; align-items: center; gap: 10rpx; margin-bottom: 4rpx; }
.mn { font-size: 34rpx; font-weight: 700; }
.mlt { font-size: 20rpx; background: rgba(255,255,255,0.2); padding: 2rpx 12rpx; border-radius: 6rpx; }
.mm { font-size: 24rpx; opacity: 0.75; }
.sr { display: flex; background: rgba(255,255,255,0.12); border-radius: 16rpx; padding: 22rpx 0; }
.si { flex: 1; text-align: center; }
.sv { font-size: 32rpx; font-weight: 700; display: block; }
.sl { font-size: 20rpx; opacity: 0.65; display: block; margin-top: 4rpx; }

.card-item { padding: 24rpx; margin-bottom: 16rpx; }
.dim { opacity: 0.45; }
.ctag { font-size: 20rpx; padding: 2rpx 10rpx; border-radius: 6rpx; display: inline-block; margin-bottom: 8rpx; font-weight: 500; }
.ct-stored { background: rgba(230,162,60,0.12); color: #C7851F; }
.ct-month { background: rgba(64,158,255,0.12); color: #2B7DE9; }
.ct-season { background: rgba(0,0,0,0.06); color: #86868B; }
.ct-year { background: rgba(103,194,58,0.12); color: #4A9E2F; }
.ctitle { font-size: 30rpx; font-weight: 700; color: #1D1D1F; display: block; margin-bottom: 4rpx; }
.cdetail { font-size: 24rpx; color: #86868B; display: block; margin-bottom: 4rpx; }
.cex { display: flex; align-items: center; gap: 12rpx; font-size: 22rpx; color: #A1A1A6; }
.etag { background: rgba(245,108,108,0.12); color: #D94848; padding: 2rpx 8rpx; border-radius: 4rpx; font-size: 18rpx; }

.ct-card { padding: 32rpx 28rpx; margin-bottom: 16rpx; text-align: center; }
.ctn { font-size: 36rpx; font-weight: 700; color: #1D1D1F; display: block; }
.ctp { font-size: 56rpx; font-weight: 800; color: #E6A23C; display: block; margin: 8rpx 0; }
.ctm { font-size: 22rpx; color: #86868B; display: block; }
</style>
