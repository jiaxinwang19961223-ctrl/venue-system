# 场馆运营系统 — 竞品分析报告

> 2026-08-01 | 来源：球之道线上分析 🔍 + SmartSportV API分析 🔍

---

## 一、球之道（arena.balledu.com）

### 技术栈
- **前端**: Vue.js + Element UI + ECharts + webpack
- **风格**: 传统后台管理 SPA，Element UI 组件体系
- **认证**: phone + password，JWT token (access_token + refresh_token)

### 完整导航结构（6+ 一级模块）

```
🏠 首页
  └── 前台首页 (home_frontDesk)

👤 会员管理
  ├── 办卡管理 (handleCard_management)
  ├── 会员列表
  ├── 会员等级 / 创建会员等级
  ├── 会员资料配置
  ├── 会员订单
  ├── 通卡会员列表
  └── 视频会员卡设置

🚶 客流管理
  ├── 客流详情 (ke_keliu)
  └── 客流统计 (ketong_liutong)

📋 订单管理
  ├── 场地订单 (order_site)
  └── 散客消费 (order_traveler)

📊 市场管理（CRM）
  ├── 渠道管理 / 渠道明细
  ├── 市场计划 / 市场看板
  ├── 线索管理 / 资源池
  ├── 市场KPI明细
  ├── 销售计划 / 销售明细 / 销售跟进
  ├── 成单明细 / 周看板 / 销售总控
  └── 销售KPI明细

🎓 教务管理（培训）
  ├── 套餐管理
  ├── 课程管理 / 班级管理 / 分班管理
  ├── 学员管理 / 教务管理
  ├── 销课明细
  └── 班级人数统计

🏟️ 场地管理
  ├── 场地看板 (changdi)
  ├── 场地配置 / 场地关联配置
  └── 场地视频配置

⚽ 联赛管理
  ├── 联赛管理 / 参赛球队
  ├── 赛程管理 / 比赛管理
  └── 比赛统计 / 队员统计 / 球队统计

💰 财务 (finance)
  └── 财务报表

📈 报表中心
  ├── 经营报表 (home_boss)
  ├── 办卡报表 / 客流报表
  ├── 订场报表 / 销售报表
  ├── 市场报表 / 教务报表
  └── 教练报表

⚙️ 系统设置
  ├── 队魂上架 / 规则配置
  ├── 角色权限 (jiaoquan_sequan)
  └── 操作日志 (caozuo_rizi)
```

### 球之道核心亮点（可借鉴）

| 模块 | 亮点 | 实现方式 |
|------|------|----------|
| **会员体系** | 多层会员等级 + 通卡 + 视频会员卡 | 会员资料配置独立页面 |
| **包场逻辑** | 场地看板直观展示占用状态 | changdi 组件 + ECharts |
| **销课系统** | 签到消课 + 教务管理 | 教务独立模块 |
| **销售漏斗** | 线索→跟进→成单 完整 CRM | 市场管理整套 |
| **多维度报表** | 按模块独立报表（8类） | 每个业务线一个报表 |
| **客流统计** | 入场/离场时间线追踪 | ECharts 可视化 |

### 球之道不足
- 细节对齐不严谨（用户反馈）
- 传统 SPA 架构，非微服务，耦合度高
- 没有小程序端，只有 Web 后台
- UI 偏老旧（Element UI 经典风格）

---

## 二、SmartSportV（3075426724/SmartSportV）

### 技术栈
- **前端**: 微信小程序原生 + WeUI
- **后端**: 微信云开发 Cloud Base（云函数 + 云数据库）
- **架构**: `miniprogram/` + `cloudfunctions/mcloud/`
- **场景前缀**: `projects/placeone/`（单场馆版）

### 页面结构（51页）

#### 用户端（C端）
```
首页 default_index        → 场地列表/推荐
场地浏览 about_list/about_index → 场地详情
搜索 search               → 场地搜索
预约 enroll_all           → 选择场地/时段
预约确认 enroll_join      → 填写信息/提交
我的预约 enroll_my_join_list → 预约历史
预约详情 enroll_my_join_detail
修改预约 enroll_join_edit
我的 my_index             → 个人信息
注册 my_reg / 编辑 my_edit
足迹 my_foot / 收藏 my_fav
资讯 news_index/detail/cate1/cate2
```

#### 后台管理端（B端）
```
管理员登录 admin_login
管理首页 admin_home        → 数据概览
场地管理 admin_enroll_list/add/edit  → 场地CRUD
预约管理 admin_enroll_join_list      → 预约审核
预约核销 admin_enroll_scan           → 扫码核销
预约导出 admin_enroll_export         → Excel导出
预约模板 admin_enroll_temp           → 时段模板
日视图 admin_enroll_day              → 当日场地占用
预约记录 admin_enroll_record         → 历史记录
人流分析 admin_enroll_flow           → 客流统计 ⭐
通知管理 admin_enroll_notice         → 推送消息
数据统计 admin_enroll_data           → 可视化数据 ⭐
预约详情 admin_enroll_join_detail
用户管理 admin_user_list/detail/export → 用户CRUD
管理员管理 admin_mgr_list/add/edit/pwd/log
资讯管理 admin_news_list/add/edit
系统设置 admin_setup_about/about_list/qr
内容管理 admin_content
```

### 云函数结构
```
cloudfunctions/mcloud/
  ├── config/      → 配置（数据库连接、常量）
  ├── framework/   → 框架层（路由、中间件、权限）
  └── project/     → 业务云函数
      ├── admin/   → 管理端逻辑
      ├── user/    → 用户端逻辑
      └── public/  → 公共逻辑
```

### SmartSportV 优势
- ✅ 小程序原生，零框架依赖
- ✅ 云开发免服务器运维
- ✅ 完整的前后台 + 核销流程
- ✅ 人流分析 + 数据统计（竞品中独有）
- ✅ 扫码核销功能完整

### SmartSportV 不足
- ❌ 单场馆设计，无多馆切换
- ❌ 没有独立的会员体系（只有用户管理）
- ❌ 没有课程/教练/教务模块
- ❌ 没有财务模块
- ❌ 云开发数据库不可迁移

---

## 三、差距分析：我们要做的 vs 现有方案

| 需求 | 球之道 | SmartSportV | 我们做 |
|------|:--:|:--:|:--:|
| 场地管理 | ✅ 完整 | ✅ 完整 | ✅ |
| 会员体系 | ✅ 多等级+通卡 | ❌ 只有用户 | ✅ 参考球之道 |
| 订单/预约 | ✅ | ✅ | ✅ |
| 包场管理 | ✅ 场地看板 | ❌ | ✅ 参考球之道 |
| 课程/消课 | ✅ 教务体系 | ❌ | ✅ |
| 客流统计 | ✅ | ✅ 人流分析 | ✅ |
| 销售CRM | ✅ 完整漏斗 | ❌ | Phase 2 |
| 多馆切换 | ❌ | ❌ 单馆 | ✅ 核心需求 |
| 小程序端 | ❌ | ✅ | ✅ 员工+顾客双端 |
| 角色权限 | ✅ 单系统 | ❌ | ✅ 四角色 |
| AI Agent | ❌ | ❌ | ✅ |
| 数据库可控 | ❌ | ❌ 云开发 | ✅ 自建DB |
| 报表中心 | ✅ 8类报表 | ❌ | Phase 2 |

---

## 四、结论：技术方案建议

### 技术栈
| 层 | 选择 | 理由 |
|----|------|------|
| **管理后台(Web)** | Vue 3 + Element Plus | 参考球之道但升级到Vue3 |
| **小程序(双端)** | 原生 + WeUI | 参考SmartSportV，不绑云开发 |
| **后端API** | Node.js/Python + REST | 自建，不依赖微信云开发 |
| **数据库** | MySQL/PostgreSQL | 可控、可迁移、支持多馆 |
| **部署** | 阿里云 ECS (199/年) | Docker Compose 一键部署 |

### 分阶段策略
```
Phase 1（现在）: 基础CRUD + 三端框架
  → 场地管理 + 订单管理 + 会员基础 + 登录权限 + 多馆切换

Phase 2: 业务深化
  → 课程/消课 + 报表 + 包场看板 + 客流统计

Phase 3: 智能化
  → AI Agent + 销售CRM + 营销工具
```
