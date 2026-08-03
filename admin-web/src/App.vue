<template>
  <router-view />
</template>

<style>
/* ══════════════════════════════════════
   macOS 液态玻璃 UI 全局样式
   ══════════════════════════════════════ */
:root {
  --glass-bg: rgba(255,255,255,0.65);
  --glass-border: rgba(255,255,255,0.5);
  --glass-shadow: 0 8px 32px rgba(0,0,0,0.04), 0 2px 8px rgba(0,0,0,0.03);
  --glass-blur: 20px;
  --radius-sm: 8px;
  --radius: 12px;
  --radius-lg: 16px;
  --text-primary: #1D1D1F;
  --text-secondary: #6E6E73;
  --text-tertiary: #98989D;
  --bg-base: #F0F0F2;
  --color-primary: #007AFF;
  --color-success: #34C759;
  --color-warning: #FF9500;
  --color-danger: #FF3B30;
  --border-subtle: rgba(0,0,0,0.06);
  --font-system: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', 'Helvetica Neue', sans-serif;
}

* { box-sizing: border-box; }

body {
  margin: 0; padding: 0;
  font-family: var(--font-system);
  font-size: 14px; color: var(--text-primary);
  background: var(--bg-base);
  -webkit-font-smoothing: antialiased;
}

/* ── 玻璃卡片 ── */
.glass {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius);
  box-shadow: var(--glass-shadow);
  -webkit-backdrop-filter: blur(var(--glass-blur));
  backdrop-filter: blur(var(--glass-blur));
}

/* ── 表格 ── */
.el-table {
  --el-table-bg-color: transparent;
  --el-table-tr-bg-color: transparent;
  --el-table-header-bg-color: rgba(255,255,255,0.4);
  --el-table-border-color: var(--border-subtle);
  border-radius: var(--radius); overflow: hidden;
}
.el-table th.el-table__cell {
  background: rgba(255,255,255,0.4) !important;
  -webkit-backdrop-filter: blur(10px);
  backdrop-filter: blur(10px);
  font-weight: 600; font-size: 13px; color: var(--text-secondary);
}
.el-table tr { background: transparent !important; }
.el-table--striped .el-table__body tr.el-table__row--striped td.el-table__cell {
  background: rgba(0,0,0,0.02) !important;
}

/* ── 对话框 ── */
.el-dialog {
  --el-dialog-bg-color: rgba(255,255,255,0.85);
  border-radius: var(--radius-lg) !important;
  -webkit-backdrop-filter: blur(30px);
  backdrop-filter: blur(30px);
  border: 1px solid var(--glass-border);
  box-shadow: 0 25px 60px rgba(0,0,0,0.12);
}

/* ── 按钮 ── */
.el-button { border-radius: var(--radius-sm) !important; font-weight: 500; }
.el-button--primary { background: var(--color-primary) !important; border-color: var(--color-primary) !important; }

/* ── 标签 ── */
.el-tag { border-radius: 6px; font-weight: 500; }

/* ── 输入框 ── */
.el-input__wrapper {
  border-radius: var(--radius-sm) !important;
  background: rgba(255,255,255,0.5) !important;
  box-shadow: none !important;
}

/* ── 卡片 ── */
.el-card {
  border-radius: var(--radius) !important;
  border: 1px solid var(--border-subtle) !important;
  background: var(--glass-bg) !important;
  -webkit-backdrop-filter: blur(10px);
  backdrop-filter: blur(10px);
}

/* ── 弹窗内容淡入动画 ── */
.el-dialog__body { animation: fadeSlideIn 0.3s ease; }
.el-dialog { animation: dialogIn 0.25s ease; }
@keyframes fadeSlideIn {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes dialogIn {
  from { opacity: 0; transform: scale(0.96); }
  to { opacity: 1; transform: scale(1); }
}

/* ── 滚动条 ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.15); border-radius: 3px; }
</style>
