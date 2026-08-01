import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { noAuth: true },
  },
  {
    path: '/',
    component: () => import('../layouts/MainLayout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue'),
        meta: { title: '首页' },
      },
      {
        path: 'venues',
        name: 'Venues',
        component: () => import('../views/Venues.vue'),
        meta: { title: '场馆管理' },
      },
      {
        path: 'fields/:venueId',
        name: 'Fields',
        component: () => import('../views/Fields.vue'),
        meta: { title: '场地管理' },
      },
      {
        path: 'members',
        name: 'Members',
        component: () => import('../views/Members.vue'),
        meta: { title: '会员管理' },
      },
      {
        path: 'orders',
        name: 'Orders',
        component: () => import('../views/Orders.vue'),
        meta: { title: '订单管理' },
      },
      {
        path: 'court-board',
        name: 'CourtBoard',
        component: () => import('../views/CourtBoard.vue'),
        meta: { title: '包场看板' },
      },
      {
        path: 'card-types',
        name: 'CardTypes',
        component: () => import('../views/CardTypes.vue'),
        meta: { title: '卡种管理' },
      },
      {
        path: 'face-checkin',
        name: 'FaceCheckin',
        component: () => import('../views/FaceCheckin.vue'),
        meta: { title: '人脸签到' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫 — 未登录跳转登录页
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (!to.meta.noAuth && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router
