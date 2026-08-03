<script>
export default {
  onLaunch() {
    console.log('Staff App Launch')
  },
}
</script>

<style lang="scss">
/* ═══════════════════════════════════
   iOS 毛玻璃设计系统 — 员工端
   （与顾客端保持一致）
   ═══════════════════════════════════ */

page {
  --glass-bg: rgba(255, 255, 255, 0.72);
  --glass-border: rgba(255, 255, 255, 0.6);
  --glass-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.04), 0 2rpx 8rpx rgba(0, 0, 0, 0.02);
  --glass-radius: 24rpx;
  --glass-blur: 20px;

  --card-bg: rgba(255, 255, 255, 0.85);
  --card-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.03);

  --color-primary: #409EFF;
  --color-success: #67C23A;
  --color-warning: #E6A23C;
  --color-danger: #F56C6C;

  background: linear-gradient(180deg, #F0F4F8 0%, #F5F7FA 30%, #EDF1F5 100%);
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Helvetica Neue', sans-serif;
  font-size: 14px;
  color: #1D1D1F;
  -webkit-font-smoothing: antialiased;
}

/* ── 毛玻璃卡片基类 ── */
.glass {
  background: var(--glass-bg);
  border: 1rpx solid var(--glass-border);
  border-radius: var(--glass-radius);
  box-shadow: var(--glass-shadow);
  -webkit-backdrop-filter: blur(var(--glass-blur));
  backdrop-filter: blur(var(--glass-blur));
}

.card {
  background: var(--card-bg);
  border-radius: 20rpx;
  box-shadow: var(--card-shadow);
}

/* ── 工具类 ── */
.flex { display: flex; }
.flex-center { display: flex; align-items: center; justify-content: center; }
.flex-between { display: flex; align-items: center; justify-content: space-between; }
.text-center { text-align: center; }
.text-muted { color: #86868B; }
.text-primary { color: var(--color-primary); }

/* ── 通用按钮 ── */
.btn {
  display: flex; align-items: center; justify-content: center;
  padding: 20rpx 40rpx; border-radius: 16rpx;
  font-size: 28rpx; font-weight: 600;
  transition: all 0.2s;
}
.btn-primary {
  background: var(--color-primary);
  color: #fff;
  box-shadow: 0 4rpx 16rpx rgba(64, 158, 255, 0.3);
}
.btn-primary:active { transform: scale(0.97); opacity: 0.9; }

.btn-glass {
  background: rgba(255,255,255,0.6);
  color: var(--color-primary);
  border: 1rpx solid rgba(64,158,255,0.2);
  -webkit-backdrop-filter: blur(10px);
  backdrop-filter: blur(10px);
}

.btn-sm {
  padding: 12rpx 24rpx;
  font-size: 24rpx;
}

.btn-danger {
  background: var(--color-danger);
  color: #fff;
}
.btn-danger:active { transform: scale(0.97); opacity: 0.9; }

.btn-success {
  background: var(--color-success);
  color: #fff;
}

/* ── 通用输入框 ── */
.input-glass {
  width: 100%; height: 88rpx;
  background: rgba(255,255,255,0.6);
  border: 1rpx solid rgba(0,0,0,0.06);
  border-radius: 16rpx;
  padding: 0 24rpx; font-size: 28rpx; color: #1D1D1F;
  box-sizing: border-box;
}
.input-glass:focus { border-color: var(--color-primary); background: rgba(255,255,255,0.9); }

/* ── 标签 ── */
.tag {
  display: inline-block;
  font-size: 20rpx; padding: 4rpx 12rpx; border-radius: 8rpx;
  font-weight: 500;
}
.tag-green { background: rgba(103,194,58,0.12); color: #4A9E2F; }
.tag-blue { background: rgba(64,158,255,0.12); color: #2B7DE9; }
.tag-orange { background: rgba(230,162,60,0.12); color: #C7851F; }
.tag-red { background: rgba(245,108,108,0.12); color: #D94848; }
.tag-gray { background: rgba(0,0,0,0.06); color: #86868B; }

/* ── 页面容器 ── */
.page {
  padding: 24rpx;
  padding-bottom: 120rpx;
  min-height: 100vh;
}

/* ── 区块标题 ── */
.section-title {
  font-size: 34rpx; font-weight: 700; color: #1D1D1F;
  margin-bottom: 20rpx; margin-top: 8rpx;
  letter-spacing: -0.3px;
}

/* ── 空状态 ── */
.empty-state { padding: 120rpx 0; text-align: center; }
.empty-icon { width: 100rpx; height: 100rpx; margin: 0 auto 16rpx; display: block; opacity: 0.6; }
.empty-text { font-size: 30rpx; color: #86868B; display: block; }
.empty-sub { font-size: 24rpx; color: #A1A1A6; display: block; margin-top: 8rpx; }
</style>
