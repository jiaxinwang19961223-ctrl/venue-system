<template>
  <view class="page">
    <!-- 会员基本信息 -->
    <view class="glass info-card">
      <view class="flex-between">
        <text class="member-name">{{ member.name }}</text>
        <text class="tag" :class="member.is_active ? 'tag-green' : 'tag-gray'">
          {{ member.is_active ? '活跃' : '停用' }}
        </text>
      </view>
      <view class="info-row">
        <text class="text-muted">{{ member.phone }}</text>
        <text class="text-muted" v-if="member.gender">{{ member.gender === 'male' ? '男' : member.gender === 'female' ? '女' : member.gender }}</text>
      </view>
      <view class="flex-between" style="margin-top:20rpx">
        <view>
          <text style="font-size:22rpx;color:#86868B">余额</text>
          <text style="font-size:40rpx;font-weight:700;display:block">¥{{ member.balance }}</text>
        </view>
        <view>
          <text style="font-size:22rpx;color:#86868B">累计消费</text>
          <text style="font-size:28rpx;font-weight:600;display:block">¥{{ member.total_consumption || 0 }}</text>
        </view>
        <view>
          <text style="font-size:22rpx;color:#86868B">积分</text>
          <text style="font-size:28rpx;font-weight:600;display:block">{{ member.points || 0 }}</text>
        </view>
      </view>
    </view>

    <!-- 会员卡 -->
    <text class="section-title" v-if="cards.length">会员卡</text>
    <view class="glass card-item" v-for="c in cards" :key="c.id">
      <view class="flex-between">
        <view>
          <text style="font-size:28rpx;font-weight:600">{{ c.card_type === 'times' ? '次卡' : c.card_type === 'stored' ? '储值卡' : c.card_type }}</text>
          <text class="tag tag-blue" style="margin-left:12rpx" v-if="c.is_active">有效</text>
          <text class="tag tag-gray" style="margin-left:12rpx" v-else>失效</text>
        </view>
        <text class="text-muted" style="font-size:24rpx">
          {{ c.start_date ? c.start_date.slice(0,10) : '' }} ~ {{ c.end_date ? c.end_date.slice(0,10) : '长期' }}
        </text>
      </view>
      <view class="flex-between" style="margin-top:12rpx">
        <text v-if="c.card_type === 'times'" style="font-size:24rpx;color:#86868B">
          已用 {{ c.used_times }} / 共计 {{ c.total_times }} 次
        </text>
        <text v-else style="font-size:24rpx;color:#86868B">
          已用 ¥{{ c.used_value || 0 }} / 储值 ¥{{ c.stored_value || 0 }}
        </text>
        <text style="font-size:22rpx;color:var(--color-primary)" @tap="changeValidity(c)">改有效期</text>
      </view>
    </view>
    <view v-if="!cards.length && !loading" class="text-muted" style="text-align:center;padding:24rpx">暂无会员卡</view>

    <!-- 签到扣费 -->
    <text class="section-title" v-if="store.canCheckIn">签到 / 扣费</text>
    <view class="glass form-card" v-if="store.canCheckIn">
      <view class="flex-between" style="margin-bottom:16rpx">
        <text class="form-label" style="margin:0">扣费方式</text>
        <view style="display:flex;gap:12rpx">
          <text class="method-tab" :class="{ active: consumeMethod === 'balance' }" @tap="consumeMethod = 'balance'">余额</text>
          <text class="method-tab" :class="{ active: consumeMethod === 'card' && selectedCard }" @tap="consumeMethod = 'card'" v-if="cards.length">刷卡</text>
        </view>
      </view>

      <picker v-if="consumeMethod === 'card'" mode="selector" :range="cardOptions" @change="onCardChange">
        <view class="picker-input">{{ cardOptions[cardOptionIndex] || '选择会员卡' }}</view>
      </picker>

      <view class="flex-between" style="margin-top:16rpx">
        <input class="input-glass" style="flex:1;margin:0" v-model="consumeAmount" type="digit" placeholder="消费金额" />
        <view class="btn btn-primary btn-sm" style="margin-left:16rpx" @tap="doConsume">确认扣费</view>
      </view>
      <input class="input-glass" style="margin-top:12rpx" v-model="consumeRemark" placeholder="备注（可选）" />
    </view>

    <!-- 消费记录 -->
    <text class="section-title">消费记录</text>
    <view class="glass order-card" v-for="o in orders" :key="o.id">
      <view class="flex-between">
        <view>
          <text class="tag" :class="orderTypeTag(o.order_type)">{{ orderTypeLabel(o.order_type) }}</text>
          <text class="tag" :class="orderStatusTag(o.status)" style="margin-left:8rpx">{{ orderStatusLabel(o.status) }}</text>
        </view>
        <text style="font-size:28rpx;font-weight:700">¥{{ o.paid_amount }}</text>
      </view>
      <text class="text-muted" style="font-size:22rpx;display:block;margin-top:8rpx">
        {{ o.book_date || '' }}  {{ o.start_time || '' }}  ·  {{ o.remark || '' }}
      </text>
    </view>
    <view class="empty-state" v-if="!loading && orders.length === 0">
      <text class="empty-text">暂无消费记录</text>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { getMember, getMemberCards, getMemberOrders, memberConsume, updateCardValidity } from '../../api'
import { useUserStore } from '../../store/user'

const store = useUserStore()
const member = ref({})
const cards = ref([])
const orders = ref([])
const loading = ref(true)

const consumeMethod = ref('balance')
const consumeAmount = ref('')
const consumeRemark = ref('')
const selectedCard = ref(null)
const cardOptions = ref([])
const cardOptionIndex = ref(-1)

onLoad(async (opts) => {
  if (!opts.id) return
  loading.value = true
  try {
    const [mRes, cRes, oRes] = await Promise.all([
      getMember(opts.id),
      getMemberCards(opts.id),
      getMemberOrders(opts.id),
    ])
    member.value = mRes
    cards.value = (cRes.cards || []).filter(c => c.is_active)
    orders.value = oRes.orders || []

    // 过滤可用的卡
    cardOptions.value = cards.value.map(c => {
      if (c.card_type === 'times') {
        return `次卡 剩${c.total_times - c.used_times}次 (至${c.end_date ? c.end_date.slice(0,10) : '长期'})`
      }
      return `储值卡 ¥${(c.stored_value || 0) - (c.used_value || 0)} (至${c.end_date ? c.end_date.slice(0,10) : '长期'})`
    })
  } catch { /* */ }
  finally { loading.value = false }
})

async function doConsume() {
  const amount = parseFloat(consumeAmount.value)
  if (!amount || amount <= 0) {
    return uni.showToast({ title: '请输入消费金额', icon: 'none' })
  }
  const data = {
    amount,
    use_card: false,
    card_id: null,
    remark: consumeRemark.value,
  }
  if (consumeMethod.value === 'card' && selectedCard.value) {
    data.use_card = true
    data.card_id = selectedCard.value.id
  }
  try {
    const res = await memberConsume(member.value.id, data)
    uni.showToast({ title: res.message || '签到扣费成功', icon: 'success' })
    consumeAmount.value = ''
    consumeRemark.value = ''
    // 刷新
    const [mRes, oRes] = await Promise.all([
      getMember(member.value.id),
      getMemberOrders(member.value.id),
    ])
    member.value = mRes
    orders.value = oRes.orders || []
  } catch { /* */ }
}

function onCardChange(e) {
  cardOptionIndex.value = e.detail.value
  selectedCard.value = cards.value[cardOptionIndex.value]
}

function changeValidity(card) {
  uni.showModal({
    title: '修改有效期',
    content: `当前截止: ${card.end_date ? card.end_date.slice(0, 10) : '长期有效'}\n\n手动修改请前往管理后台操作`,
    showCancel: false,
  })
}

function orderTypeLabel(t) {
  const m = { field_book: '订场', walk_in: '散客', card_recharge: '办卡', course_book: '课程' }
  return m[t] || t
}
function orderTypeTag(t) {
  const m = { field_book: 'tag-blue', walk_in: 'tag-orange', card_recharge: 'tag-green' }
  return m[t] || 'tag-gray'
}
function orderStatusLabel(s) {
  const m = { pending: '待付', paid: '已付', confirmed: '确认', checked_in: '签到' }
  return m[s] || s
}
function orderStatusTag(s) {
  const m = { pending: 'tag-orange', paid: 'tag-blue', confirmed: 'tag-green', checked_in: 'tag-green' }
  return m[s] || 'tag-gray'
}
</script>

<style scoped>
.info-card { padding: 28rpx; margin-bottom: 24rpx; }
.member-name { font-size: 38rpx; font-weight: 700; color: #1D1D1F; }
.info-row { display: flex; gap: 20rpx; margin-top: 8rpx; font-size: 26rpx; }

.card-item { padding: 24rpx; margin-bottom: 16rpx; }

.form-card { padding: 24rpx; margin-bottom: 24rpx; }
.method-tab {
  font-size: 24rpx; padding: 8rpx 16rpx; border-radius: 12rpx;
  background: rgba(0,0,0,0.04); color: #86868B;
}
.method-tab.active { background: rgba(64,158,255,0.12); color: var(--color-primary); font-weight: 600; }

.order-card { padding: 20rpx 24rpx; margin-bottom: 12rpx; }
</style>
