/** 业务字典 — 避免各页面重复定义 */

export const TRAINING_CATEGORY = {
  basic: '基础口才',
  speech: '演讲实战',
  livestream: '直播话术',
  improv: '即兴表达',
  interview: '面试模拟',
  short_video: '短视频口播',
  student: '学生场景',
}

export const GROWTH_LEVEL = {
  newbie: '新人',
  beginner: '入门',
  advanced: '进阶',
  expert: '达人',
  master: '大师',
}

export const GROWTH_LEVEL_TAG = {
  newbie: 'info',
  beginner: '',
  advanced: 'success',
  expert: 'warning',
  master: 'danger',
}

export const AI_SCENE = {
  speech: '演讲文案',
  short_video: '短视频',
  livestream: '直播话术',
  interview: '面试话术',
  opening: '开场白',
}

export const trainingCategoryLabel = (v) => TRAINING_CATEGORY[v] || v
export const growthLevelLabel = (v) => GROWTH_LEVEL[v] || v
export const growthLevelTag = (v) => GROWTH_LEVEL_TAG[v] || 'info'
export const aiSceneLabel = (v) => AI_SCENE[v] || v
