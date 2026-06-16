import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/',
    component: () => import('@/components/AppLayout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: { title: '数据看板', icon: 'Odometer' }
      },
      {
        path: 'training',
        name: 'TrainingList',
        component: () => import('@/views/training/index.vue'),
        meta: { title: '训练题库', icon: 'Memo' }
      },
      {
        path: 'training/recommend',
        name: 'RecommendConfig',
        component: () => import('@/views/training/recommend.vue'),
        meta: { title: '热门推荐', icon: 'Star' }
      },
      {
        path: 'checkin/tasks',
        name: 'CheckinTasks',
        component: () => import('@/views/checkin/tasks.vue'),
        meta: { title: '每日任务', icon: 'Calendar' }
      },
      {
        path: 'checkin/growth',
        name: 'GrowthGoals',
        component: () => import('@/views/checkin/growth.vue'),
        meta: { title: '成长目标', icon: 'Trophy' }
      },
      {
        path: 'ai',
        name: 'AIConfig',
        component: () => import('@/views/ai/index.vue'),
        meta: { title: 'AI配置', icon: 'Cpu' }
      },
      {
        path: 'users',
        name: 'UserList',
        component: () => import('@/views/user/index.vue'),
        meta: { title: '用户管理', icon: 'User' }
      },
      {
        path: 'users/:id',
        name: 'UserDetail',
        component: () => import('@/views/user/detail.vue'),
        meta: { title: '用户详情', hidden: true }
      },
      {
        path: 'push',
        name: 'PushCenter',
        component: () => import('@/views/push/index.vue'),
        meta: { title: '消息推送', icon: 'Message' }
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/views/settings/index.vue'),
        meta: { title: '系统设置', icon: 'Setting' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

// 导航守卫
router.beforeEach((to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - 口才训练营后台` : '口才训练营后台'
  const token = localStorage.getItem('admin_token')
  if (to.path !== '/login' && !token) {
    next('/login')
  } else if (to.path === '/login' && token) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
