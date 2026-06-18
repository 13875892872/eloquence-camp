import { createRouter, createWebHashHistory } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getAdminRole } from '@/store/app'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue'),
    meta: { title: '登录' },
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
        meta: { title: '数据看板', icon: 'Odometer' },
      },
      {
        path: 'training',
        name: 'TrainingList',
        component: () => import('@/views/training/index.vue'),
        meta: { title: '训练题库', icon: 'Memo' },
      },
      {
        path: 'training/recommend',
        name: 'RecommendConfig',
        component: () => import('@/views/training/recommend.vue'),
        meta: { title: '热门推荐', icon: 'Star', parent: '训练题库' },
      },
      {
        path: 'checkin/tasks',
        name: 'CheckinTasks',
        component: () => import('@/views/checkin/tasks.vue'),
        meta: { title: '每日任务', icon: 'Calendar', parent: '打卡配置' },
      },
      {
        path: 'checkin/growth',
        name: 'GrowthGoals',
        component: () => import('@/views/checkin/growth.vue'),
        meta: { title: '成长目标', icon: 'Trophy', parent: '打卡配置' },
      },
      {
        path: 'ai',
        name: 'AIConfig',
        component: () => import('@/views/ai/index.vue'),
        meta: { title: 'AI 配置', icon: 'Cpu' },
      },
      {
        path: 'users',
        name: 'UserList',
        component: () => import('@/views/user/index.vue'),
        meta: { title: '用户管理', icon: 'User' },
      },
      {
        path: 'users/:id',
        name: 'UserDetail',
        component: () => import('@/views/user/detail.vue'),
        meta: { title: '用户详情', parent: '用户管理' },
      },
      {
        path: 'push',
        name: 'PushCenter',
        component: () => import('@/views/push/index.vue'),
        meta: { title: '消息推送', icon: 'Message' },
      },
      {
        path: 'settings',
        component: () => import('@/components/SettingsLayout.vue'),
        redirect: '/settings/password',
        meta: { title: '系统设置' },
        children: [
          {
            path: 'password',
            name: 'SettingsPassword',
            component: () => import('@/views/settings/password.vue'),
            meta: { title: '修改密码' },
          },
          {
            path: 'storage',
            name: 'SettingsStorage',
            component: () => import('@/views/settings/storage.vue'),
            meta: { title: '存储管理', roles: ['super_admin'] },
          },
          {
            path: 'logs',
            name: 'SettingsLogs',
            component: () => import('@/views/settings/logs.vue'),
            meta: { title: '操作日志', roles: ['super_admin'] },
          },
        ],
      },
    ],
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - 口才训练营后台` : '口才训练营后台'
  const token = localStorage.getItem('admin_token')
  if (to.path !== '/login' && !token) {
    next('/login')
    return
  }
  if (to.path === '/login' && token) {
    next('/dashboard')
    return
  }
  const roles = to.matched.flatMap((r) => r.meta?.roles || []).filter(Boolean)
  if (roles.length) {
    const role = getAdminRole()
    if (!roles.includes(role)) {
      ElMessage.error('当前账号无权限访问该页面')
      next(from.path && from.path !== '/login' ? from.path : '/dashboard')
      return
    }
  }
  next()
})

export default router
