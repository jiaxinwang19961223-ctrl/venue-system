# 🏟️ 场馆运营系统

> Phase 1: 基础 CRUD 完成 | 2026-08-01

## 技术栈

| 层 | 技术 |
|---|------|
| 管理后台 | Vue 3 + Element Plus + Vite |
| 后端 API | Python 3 + FastAPI + SQLAlchemy |
| 数据库 | SQLite（开发）/ MySQL（生产） |
| 认证 | JWT + bcrypt |

## 项目结构

```
venue-system/
├── backend/                    # Python FastAPI 后端
│   ├── app/
│   │   ├── api/               # API 路由
│   │   │   ├── auth.py        # 认证（登录/注册/JWT）
│   │   │   ├── venues.py      # 场馆 & 场地管理
│   │   │   ├── members.py     # 会员 & 等级 & 办卡
│   │   │   └── orders.py      # 订单 & 状态流转
│   │   ├── core/              # 核心配置
│   │   │   ├── config.py      # 应用配置
│   │   │   ├── security.py    # JWT + 密码加密
│   │   │   └── database.py    # 数据库连接
│   │   ├── models/            # 数据模型
│   │   │   ├── venue.py       # 场馆/场地/时段模板
│   │   │   ├── member.py      # 会员/等级/会员卡
│   │   │   ├── order.py       # 订单
│   │   │   ├── user.py        # 用户/角色权限
│   │   │   └── course.py      # 课程/套餐/消课
│   │   └── main.py            # FastAPI 入口
│   ├── init_db.py             # 数据库初始化
│   └── venue.db               # SQLite 数据库
├── admin-web/                  # Vue 3 管理后台
│   └── src/
│       ├── views/
│       │   ├── Login.vue      # 登录页
│       │   ├── Dashboard.vue  # 数据概览
│       │   ├── Venues.vue     # 场馆管理
│       │   ├── Fields.vue     # 场地管理
│       │   ├── Members.vue    # 会员管理
│       │   └── Orders.vue     # 订单管理（含快速开单）
│       ├── api/index.js       # API 请求封装
│       ├── stores/user.js     # 用户状态管理
│       └── layouts/MainLayout.vue
├── ANALYSIS.md                 # 竞品分析报告
└── README.md
```

## 启动方式

```bash
# 1. 后端
cd backend
python3 init_db.py       # 初始化数据库（仅首次）
python3 -m uvicorn app.main:app --port 8000 --reload

# 2. 前端
cd admin-web
npm run dev
```

## 测试账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 核心管理层 | admin | admin123 |
| 前台 | staff | staff123 |

## API 文档

启动后端后访问: http://localhost:8000/docs

## 数据模型

- **Venues** — 球馆（支持多馆 + 一照多址）
- **Fields** — 场地（类型/价格/容量/时段模板）
- **Members** — 会员（等级/余额/积分/通卡）
- **MemberLevels** — 会员等级（折扣/门槛）
- **MemberCards** — 会员卡（次卡/月卡/年卡）
- **Orders** — 订单（场地/散客/办卡/课程）
- **Users** — 用户（四角色权限体系）
- **Courses** — 课程/套餐/消课记录

## 角色权限

| 功能 | 核心管理层 | 馆长 | 前台 | 教练 |
|------|:--:|:--:|:--:|:--:|
| 全部门店 | ✅ | — | — | — |
| 营收数据 | ✅ | ✅ | — | — |
| 场地管理 | ✅ | ✅ | — | — |
| 快速开单 | ✅ | ✅ | ✅ | — |
| 会员编辑 | ✅ | ✅ | — | — |
| 消课签到 | ✅ | ✅ | — | ✅ |
| 退款 | ✅ | ✅ | — | — |

## 参考来源

- 球之道（arena.balledu.com）— 会员体系、包场逻辑、教务结构
- SmartSportV — 微信小程序架构、云开发模式
- 全项目记忆: [[project-system-planning]]
