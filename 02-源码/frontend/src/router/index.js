import { createRouter, createWebHistory } from 'vue-router'

/** 路由表：后台管理端 + 种植户门户，登录态由守卫统一校验 */
const routes = [
  { path: '/login', component: () => import('@/views/Login.vue'), meta: { public: true } },
  {
    path: '/',
    component: () => import('@/layout/MainLayout.vue'),
    redirect: '/dashboard',
    children: [
      { path: 'dashboard', component: () => import('@/views/Dashboard.vue'), meta: { title: '农业用水分析' } },
      { path: 'farmland', component: () => import('@/views/Farmland.vue'), meta: { title: '地块用水地图' } },
      { path: 'application', component: () => import('@/views/Application.vue'), meta: { title: '用水申请' } },
      { path: 'plan', component: () => import('@/views/Plan.vue'), meta: { title: '灌溉计划' } },
      { path: 'task', component: () => import('@/views/Task.vue'), meta: { title: '执行任务' } },
      { path: 'fee', component: () => import('@/views/Fee.vue'), meta: { title: '费用台账' } },
      { path: 'quota', component: () => import('@/views/Quota.vue'), meta: { title: '水权定额' } },
      { path: 'source', component: () => import('@/views/Source.vue'), meta: { title: '水源与渠道' } },
      { path: 'advice', component: () => import('@/views/Advice.vue'), meta: { title: '用水建议' } },
      { path: 'analysis', component: () => import('@/views/Analyze.vue'), meta: { title: '用水统计' } },
      { path: 'system', component: () => import('@/views/System.vue'), meta: { title: '系统管理' } },
      { path: 'profile', component: () => import('@/views/Profile.vue'), meta: { title: '个人中心' } }
    ]
  },
  { path: '/portal', component: () => import('@/views/Portal.vue'), meta: { title: '种植户门户' } },
  { path: '/:pathMatch(.*)*', redirect: '/dashboard' }
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.meta.public) {
    return next()
  }
  if (!token) {
    return next('/login')
  }
  if (to.meta.title) {
    document.title = to.meta.title + ' · 农田灌溉计划与用水统计系统'
  }
  next()
})

export default router
