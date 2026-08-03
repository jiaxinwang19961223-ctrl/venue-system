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
    component: () => import('../layouts/CustomerLayout.vue'),
    redirect: '/home',
    children: [
      {
        path: 'home',
        name: 'Home',
        component: () => import('../views/Home.vue'),
        meta: { title: '首页' },
      },
      {
        path: 'venues/:venueId',
        name: 'VenueDetail',
        component: () => import('../views/VenueDetail.vue'),
        meta: { title: '场地列表' },
      },
      {
        path: 'book/:venueId/:fieldId',
        name: 'Booking',
        component: () => import('../views/Booking.vue'),
        meta: { title: '预订场地' },
      },
      {
        path: 'orders',
        name: 'MyOrders',
        component: () => import('../views/MyOrders.vue'),
        meta: { title: '我的订单' },
      },
      {
        path: 'member',
        name: 'MemberCenter',
        component: () => import('../views/MemberCenter.vue'),
        meta: { title: '会员中心' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (!to.meta.noAuth && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router
