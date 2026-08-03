<template>
  <view class="page">
    <!-- 订单信息 -->
    <view class="glass info-card">
      <view class="flex-between">
        <text style="font-size:24rpx;color:#86868B">订单号</text>
        <text style="font-size:28rpx;font-weight:600">{{ order.order_no }}</text>
      </view>
      <view class="flex-between" style="margin-top:16rpx">
        <text class="text-muted" style="font-size:24rpx">状态</text>
        <text class="tag" :class="statusTag(order.status)">{{ statusLabel(order.status) }}</text>
      </view>
      <view class="flex-between" style="margin-top:16rpx">
        <text class="text-muted" style="font-size:24rpx">类型</text>
        <text>{{ orderTypeLabel(order.order_type) }}</text>
      </view>
      <view v-if="order.field_name" class="flex-between" style="margin-top:12rpx">
        <text class="text-muted" style="font-size:24rpx">场地</text>
        <text>{{ order.field_name }}</text>
      </view>
      <view v-if="order.book_date" class="flex-between" style="margin-top:12rpx">
        <text class="text-muted" style="font-size:24rpx">日期</text>
        <text>{{ order.book_date }}</text>
      </view>
      <view v-if="order.start_time" class="flex-between" style="margin-top:12rpx">
        <text class="text-muted" style="font-size:24rpx">时段</text>
        <text>{{ order.start_time }} - {{ order.end_time }}</text>
      </view>
      <view class="flex-between" style="margin-top:12rpx">
        <text class="text-muted" style="font-size:24rpx">球馆</text>
        <text>{{ order.venue_name || '—' }}</text>
      </view>
      <view class="flex-between" style="margin-top:12rpx">
        <text class="text-muted" style="font-size:24rpx">会员</text>
        <text>{{ order.name || '散客' }}</text>
      </view>
      <view class="flex-between" style="margin-top:12rpx">
        <text class="text-muted" style="font-size:24rpx">手机号</text>
        <text>{{ order.phone || '—' }}</text>
      </view>
    </view>

    <!-- 金额 -->
    <view class="glass amount-card">
      <view class="flex-between">
        <text class="text-muted" style="font-size:24rpx">支付方式</text>
        <text>{{ order.payment_method || '—' }}</text>
      </view>
      <view class="flex-between" style="margin-top:12rpx">
        <text class="text-muted" style="font-size:24rpx">原价</text>
        <text>¥{{ order.original_amount }}</text>
      </view>
      <view class="flex-between" style="margin-top:12rpx">
        <text class="text-muted" style="font-size:24rpx">实付</text>
        <text style="font-size:36rpx;font-weight:700;color:#1D1D1F">¥{{ order.paid_amount }}</text>
      </view>
    </view>

    <!-- 操作按钮 -->
    <view class="action-btns" v-if="canOperate">
      <view class="btn btn-primary" v-if="order.status === 'pending'" @tap="changeStatus('paid')">
        确认收款
      </view>
      <view class="btn btn-success" v-if="order.status === 'paid' || order.status === 'pending'" @tap="changeStatus('confirmed')">
        确认到店
      </view>
      <view class="btn btn-primary" v-if="canCheckIn && order.status === 'confirmed'" @tap="changeStatus('checked_in')">
        签到 / 消课
      </view>
      <view class="btn btn-danger" v-if="canRefund && ['pending','paid','confirmed'].includes(order.status)" @tap="changeStatus('cancelled')">
        取消订单
      </view>
    </view>

    <text class="text-muted" style="text-align:center;display:block;margin-top:24rpx;font-size:22rpx">
      {{ order.remark ? '备注: ' + order.remark : '' }}
    </text>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { getOrder, updateOrderStatus } from '../../api'
import { useUserStore } from '../../store/user'

const store = useUserStore()
const order = ref({})

const canOperate = computed(() =>
  ['core_management', 'manager', 'reception'].includes(store.userRole)
)
const canCheckIn = computed(() => store.canCheckIn)
const canRefund = computed(() =>
  ['core_management', 'manager'].includes(store.userRole)
)

onLoad(async (opts) => {
  if (!opts.id) return
  try {
    order.value = await getOrder(opts.id)
  } catch { /* */ }
})

async function changeStatus(status) {
  const labels = {
    paid: '确认收款',
    confirmed: '确认到店',
    checked_in: '签到',
    cancelled: '取消订单',
    refunded: '退款',
  }
  const r = await uni.showModal({
    title: `${labels[status] || '操作'}`,
    content: `确定要${labels[status] || '执行'}吗？`,
  })
  if (!r.confirm) return

  try {
    await updateOrderStatus(order.value.id, status)
    uni.showToast({ title: '操作成功', icon: 'success' })
    // 刷新
    order.value = await getOrder(order.value.id)
  } catch { /* */ }
}

function orderTypeLabel(t) {
  const m = { field_book: '场地预订', walk_in: '散客消费', card_recharge: '办卡/充值', course_book: '课程报名' }
  return m[t] || t
}
function statusLabel(s) {
  const m = { pending: '待支付', paid: '已支付', confirmed: '已确认', checked_in: '已签到', cancelled: '已取消', refunded: '已退款' }
  return m[s] || s
}
function statusTag(s) {
  const m = { pending: 'tag-orange', paid: 'tag-blue', confirmed: 'tag-green', checked_in: 'tag-green', cancelled: 'tag-gray', refunded: 'tag-red' }
  return m[s] || 'tag-gray'
}
</script>

<style scoped>
.info-card { padding: 28rpx; margin-bottom: 20rpx; }
.amount-card { padding: 24rpx 28rpx; margin-bottom: 24rpx; }
.action-btns { display: flex; flex-direction: column; gap: 16rpx; }
</style>
