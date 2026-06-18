/** 训练分类中文名 */
const CATEGORY_LABELS = {
  basic: '基础口才',
  speech: '演讲实战',
  livestream: '直播话术',
  improv: '即兴表达',
  interview: '面试模拟',
  short_video: '短视频口播',
  student: '学生场景',
}

export function catLabel(category) {
  return CATEGORY_LABELS[category] || category || '训练'
}

export function showGoalAchieved(data) {
  const goals = data?.goals_achieved || (data?.goal_achieved ? [data.goal_achieved] : [])
  if (!goals.length) return
  const g = goals[0]
  const badge = g.badge?.icon || '🏅'
  const name = g.badge?.name || g.name || '新成就'
  uni.showModal({
    title: '恭喜达成成长目标',
    content: `${badge} ${name}\n${g.reward_level ? '解锁：' + g.reward_level + '素材\n' : ''}${g.reward_extra_ai > 0 ? 'AI 次数 +' + g.reward_extra_ai : ''}`,
    showCancel: false,
  })
}
