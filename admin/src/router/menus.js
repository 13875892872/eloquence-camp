/** 侧边栏菜单配置 — 单一数据源 */
export const sideMenus = [
  { type: 'item', path: '/dashboard', title: '数据看板', icon: 'DataAnalysis' },
  {
    type: 'sub',
    index: 'content-group',
    title: '内容管理',
    icon: 'Document',
    children: [
      { path: '/training', title: '训练题库' },
      { path: '/training/recommend', title: '推荐配置' },
    ],
  },
  {
    type: 'sub',
    index: 'checkin-group',
    title: '打卡配置',
    icon: 'Calendar',
    children: [
      { path: '/checkin/tasks', title: '每日任务' },
      { path: '/checkin/growth', title: '成长目标' },
    ],
  },
  { type: 'item', path: '/ai', title: 'AI 配置', icon: 'Cpu' },
  { type: 'item', path: '/users', title: '用户管理', icon: 'User' },
  { type: 'item', path: '/push', title: '消息推送', icon: 'ChatDotRound' },
  { type: 'item', path: '/settings', title: '系统设置', icon: 'Setting' },
]
