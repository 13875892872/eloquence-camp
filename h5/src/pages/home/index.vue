<template>
<view class="page home-page">
  <!-- 顶部打卡入口 -->
  <view class="hero" @click="goCheckin">
    <view class="hero-bg"></view>
    <view class="hero-pattern"></view>
    <view class="hero-waves">
      <view class="wave-bar" v-for="i in 5" :key="i" :style="{ animationDelay: (i * 0.15) + 's' }"></view>
    </view>
    <view class="hero-body">
      <text class="hero-tag">口才训练营</text>
      <text class="hero-title">{{ isChecked ? '今日打卡已完成' : '开始今日口才练习' }}</text>
      <text class="hero-sub">{{ isChecked ? '坚持让表达更有力量' : '待练 ' + pendingCount + ' 个任务，完成即可打卡' }}</text>
      <view class="hero-stats" v-if="user.continuous_days || pendingCount">
        <text class="hero-stat" v-if="user.continuous_days">连续 {{ user.continuous_days }} 天</text>
        <text class="hero-stat" v-if="!isChecked && pendingCount">剩余 {{ pendingCount }} 项</text>
      </view>
      <view class="hero-btn"><text>{{ isChecked ? '查看打卡' : '立即打卡' }}</text></view>
    </view>
  </view>

  <!-- 用户状态条 -->
  <view class="user-bar">
    <view class="user-left">
      <image v-if="userAvatar" class="avatar-img" :src="userAvatar" mode="aspectFill"/>
      <view v-else class="avatar-fallback"><AppIcon name="profile" size="md"/></view>
      <view class="user-meta">
        <text class="user-greet">{{ greeting }}，来练口才吧</text>
        <text class="user-level">{{ levelLabel }}</text>
      </view>
    </view>
    <view class="streak-pill" v-if="user.continuous_days">
      <AppIcon name="fire" size="sm"/>
      <text>连续{{ user.continuous_days }}天</text>
    </view>
  </view>

  <!-- 核心服务入口 -->
  <view class="svc-primary">
    <view class="svc-big" v-for="s in primaryServices" :key="s.cat" @click="goCat(s.cat)">
      <view class="svc-icon-wrap" :style="{ background: s.bg }">
        <AppIcon :name="s.icon" size="lg"/>
      </view>
      <text class="svc-name">{{ s.label }}</text>
      <text class="svc-desc">{{ s.desc }}</text>
    </view>
  </view>

  <!-- 次要服务入口 -->
  <view class="svc-secondary">
    <view class="svc-sm" v-for="s in secondaryServices" :key="s.action" @click="goAction(s.action)">
      <AppIcon :name="s.icon" size="md"/>
      <text class="svc-sm-label">{{ s.label }}</text>
    </view>
  </view>

  <!-- 双栏推广区 -->
  <view class="promo-grid">
    <view class="promo-main" @click="scrollToCourse">
      <view class="promo-main-body">
        <text class="promo-tag">新人专享</text>
        <text class="promo-title">7天口才入门</text>
        <text class="promo-desc">每天10分钟 · 告别紧张</text>
        <view class="promo-btn">开始入门</view>
      </view>
    </view>
    <view class="promo-side">
      <view class="promo-mini quote-mini" v-if="dailyQuote">
        <text class="pm-tag">每日一句</text>
        <text class="pm-text ellipsis-2">{{ dailyQuote.content }}</text>
      </view>
      <view class="promo-mini ai-mini" @click="goAi">
        <AppIcon name="robot" size="md"/>
        <text class="pm-tag hot">AI 文案</text>
        <text class="pm-text">智能生成演讲稿</text>
        <text class="pm-price">免费体验</text>
      </view>
    </view>
  </view>

  <!-- 7天入门（新用户） -->
  <view class="course-section" v-if="showBeginner">
    <view class="hot-hdr">
      <text class="hot-title">7天口才入门</text>
      <text class="hot-more">Day {{ courseDay }}/7</text>
    </view>
    <scroll-view scroll-x class="course-scroll" :show-scrollbar="false">
      <view
        class="course-card"
        v-for="d in beginnerDays"
        :key="d.day"
        :class="d.status"
        @click="goCourseDay(d)"
      >
        <text class="cc-day">Day {{ d.day }}</text>
        <text class="cc-title ellipsis">{{ d.title }}</text>
        <text class="cc-status">{{ d.status === 'completed' ? '已完成' : d.status === 'active' ? '今日' : '待解锁' }}</text>
      </view>
    </scroll-view>
  </view>

  <view class="hot-section">
    <view class="hot-hdr">
      <text class="hot-title">热门推荐</text>
      <text class="hot-more" @click="goTraining">查看全部 ›</text>
    </view>
    <view class="hot-list">
      <view class="hot-row" v-for="it in hots" :key="it.id" @click="goDetail(it)">
        <view class="hot-row-main">
          <text class="hot-name ellipsis">{{ it.title }}</text>
          <text class="hot-meta">{{ cl(it.category) }} · {{ it.practice_count || 0 }}人练过</text>
        </view>
        <text class="hot-arrow">›</text>
      </view>
    </view>
  </view>

  <OnboardingGuide :visible="showOnboarding" @finish="showOnboarding = false" />
</view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import api from '@/api/request'
import AppIcon from '@/components/AppIcon.vue'
import OnboardingGuide from '@/components/OnboardingGuide.vue'
import { catLabel } from '@/utils/category'

const cl = catLabel

const user = ref({ continuous_days: 0, growth_level: 'newbie', avatar_url: '' })
const pendingCount = ref(3)
const isChecked = ref(false)
const hots = ref([])
const dailyQuote = ref(null)
const showOnboarding = ref(false)
const showBeginner = ref(false)
const beginnerDays = ref([])
const courseDay = ref(1)

const greeting = computed(() => {
  const h = new Date().getHours()
  return h < 12 ? '早上好' : h < 18 ? '下午好' : '晚上好'
})

const userAvatar = computed(() => user.value.avatar_url || '')

const levelLabel = computed(() => {
  const map = { newbie: 'Lv1 新人', beginner: 'Lv2 入门', advanced: 'Lv3 进阶', expert: 'Lv4 达人', master: 'Lv5 大师' }
  return map[user.value.growth_level] || 'Lv1 新人'
})

const primaryServices = [
  { icon: 'mic', label: '基础口才', desc: '发音与表达', cat: 'basic', bg: 'linear-gradient(135deg,var(--bg-brand-light),var(--hero-to))' },
  { icon: 'target', label: '演讲实战', desc: '场景模拟', cat: 'speech', bg: 'linear-gradient(135deg,#FFF0E8,#FFE0CC)' },
  { icon: 'bolt', label: '即兴表达', desc: '快速反应', cat: 'improv', bg: 'linear-gradient(135deg,#E8F8F0,#C8EDD8)' }
]

const secondaryServices = [
  { icon: 'video', label: '直播话术', action: 'livestream' },
  { icon: 'briefcase', label: '面试模拟', action: 'interview' },
  { icon: 'robot', label: 'AI文案', action: 'ai' },
  { icon: 'calendar', label: '打卡日历', action: 'calendar' },
  { icon: 'trophy', label: '排行榜', action: 'leaderboard' }
]

async function load() {
  try {
    const d = await api.get('/checkin/today')
    pendingCount.value = d.tasks?.filter(t => t.status !== 'completed').length || 3
    isChecked.value = d.all_completed
    Object.assign(user.value, d.stats || {})
    dailyQuote.value = d.daily_quote || null
  } catch (e) {}
  try {
    const p = await api.get('/user/profile')
    if (p.avatar_url) user.value.avatar_url = p.avatar_url
    if (p.growth_level) user.value.growth_level = p.growth_level
  } catch (e) {}
  try {
    const r = await api.get('/training/items', { page_size: 6 })
    hots.value = r.items || []
  } catch (e) {}
  try {
    const bc = await api.get('/checkin/beginner-course')
    showBeginner.value = bc.is_new_user || bc.days_since_register <= 14
    beginnerDays.value = bc.days || []
    courseDay.value = bc.current_day || 1
  } catch (e) {}
  if (!uni.getStorageSync('onboarding_done')) {
    showOnboarding.value = true
  }
}

function scrollToCourse() {
  if (beginnerDays.value.length) {
    const active = beginnerDays.value.find(d => d.status === 'active') || beginnerDays.value[0]
    goCourseDay(active)
  } else goCat('basic')
}

function goCourseDay(d) {
  if (d.status === 'locked') return uni.showToast({ title: '按顺序完成入门课程', icon: 'none' })
  if (d.training_item?.id) {
    uni.navigateTo({ url: '/pages/training/detail?id=' + d.training_item.id })
  } else {
    goCat(d.category || 'basic')
  }
}

function goCheckin() { uni.switchTab({ url: '/pages/checkin/index' }) }
function goCat(cat) { uni.setStorageSync('training_cat', cat); uni.switchTab({ url: '/pages/training/index' }) }
function goTraining() { uni.switchTab({ url: '/pages/training/index' }) }
function goAi() { uni.switchTab({ url: '/pages/ai-tools/index' }) }
function goDetail(it) { uni.navigateTo({ url: '/pages/training/detail?id=' + it.id }) }
function goAction(action) {
  if (action === 'ai') return goAi()
  if (action === 'calendar') return uni.navigateTo({ url: '/pages/checkin/calendar' })
  if (action === 'leaderboard') return uni.navigateTo({ url: '/pages/training/leaderboard' })
  if (action === 'livestream') return goCat('livestream')
  if (action === 'interview') return goCat('interview')
}

onShow(load)
</script>

<style scoped>
.home-page { padding-top: 8rpx; }

.hero {
  position: relative;
  border-radius: 24rpx;
  overflow: hidden;
  margin-bottom: 20rpx;
  min-height: 240rpx;
}
.hero-bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, var(--hero-from) 0%, var(--hero-to) 100%);
  z-index: 1;
}
.hero-pattern {
  position: absolute;
  inset: 0;
  z-index: 2;
  opacity: 0.08;
  background-image: radial-gradient(circle at 20% 30%, #fff 1px, transparent 1px),
    radial-gradient(circle at 70% 60%, #fff 1px, transparent 1px);
  background-size: 48rpx 48rpx;
}
.hero-waves {
  position: absolute;
  right: 28rpx;
  bottom: 32rpx;
  z-index: 3;
  display: flex;
  align-items: flex-end;
  gap: 8rpx;
  height: 72rpx;
  opacity: 0.55;
}
.wave-bar {
  width: 8rpx;
  height: 24rpx;
  background: var(--brand-light);
  border-radius: 4rpx;
  animation: wavePulse 1.2s ease-in-out infinite;
}
.wave-bar:nth-child(2) { height: 40rpx; }
.wave-bar:nth-child(3) { height: 56rpx; }
.wave-bar:nth-child(4) { height: 36rpx; }
.wave-bar:nth-child(5) { height: 48rpx; }
@keyframes wavePulse {
  0%, 100% { transform: scaleY(0.6); opacity: 0.6; }
  50% { transform: scaleY(1); opacity: 1; }
}

.hero-body {
  position: relative;
  z-index: 4;
  padding: 32rpx 28rpx;
  color: var(--text-primary);
}
.hero-tag {
  display: inline-block;
  font-size: 20rpx;
  background: rgba(160, 216, 239, 0.35);
  color: var(--brand-primary);
  border-radius: 20rpx;
  padding: 4rpx 16rpx;
  margin-bottom: 12rpx;
  letter-spacing: 1rpx;
}
.hero-title {
  font-size: 36rpx;
  font-weight: bold;
  display: block;
  margin-bottom: 8rpx;
  line-height: 1.35;
}
.hero-sub {
  font-size: 24rpx;
  color: var(--text-secondary);
  display: block;
  margin-bottom: 16rpx;
  line-height: 1.5;
}
.hero-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
  margin-bottom: 20rpx;
}
.hero-stat {
  font-size: 22rpx;
  background: rgba(160, 216, 239, 0.28);
  color: var(--brand-primary);
  border-radius: 20rpx;
  padding: 6rpx 16rpx;
}
.hero-btn {
  display: inline-flex;
  background: var(--brand-primary);
  color: #fff;
  font-size: 26rpx;
  font-weight: 600;
  border-radius: 32rpx;
  padding: 12rpx 36rpx;
}

.user-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #2C2C2C;
  border-radius: 16rpx;
  padding: 20rpx 24rpx;
  margin-bottom: 24rpx;
}
.user-left { display: flex; align-items: center; gap: 16rpx; flex: 1; min-width: 0; }
.avatar-img, .avatar-fallback {
  width: 64rpx; height: 64rpx;
  border-radius: 50%;
  flex-shrink: 0;
}
.avatar-fallback {
  background: #444;
  display: flex; align-items: center; justify-content: center;
}
.user-meta { flex: 1; min-width: 0; }
.user-greet { font-size: 26rpx; color: #fff; display: block; }
.user-level { font-size: 22rpx; color: #D4A853; display: block; margin-top: 4rpx; }
.streak-pill {
  display: flex;
  align-items: center;
  gap: 6rpx;
  background: rgba(227,24,55,0.15);
  border: 1rpx solid rgba(227,24,55,0.4);
  border-radius: 24rpx;
  padding: 8rpx 16rpx;
  font-size: 22rpx;
  color: #FF6B6B;
  flex-shrink: 0;
}

.svc-primary { display: flex; gap: 16rpx; margin-bottom: 20rpx; }
.svc-big {
  flex: 1;
  background: var(--bg-card);
  border-radius: 20rpx;
  padding: 24rpx 12rpx;
  text-align: center;
  box-shadow: var(--card-shadow);
  min-width: 0;
}
.svc-icon-wrap {
  width: 80rpx; height: 80rpx;
  border-radius: 20rpx;
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto 12rpx;
}
.svc-name { font-size: 26rpx; font-weight: 600; display: block; color: var(--text-primary); }
.svc-desc { font-size: 20rpx; color: var(--text-hint); display: block; margin-top: 4rpx; }

.svc-secondary {
  display: flex;
  background: var(--bg-card);
  border-radius: 20rpx;
  padding: 24rpx 8rpx;
  margin-bottom: 24rpx;
  box-shadow: var(--card-shadow);
}
.svc-sm {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
  min-width: 0;
}
.svc-sm-label { font-size: 22rpx; color: var(--text-secondary); display: block; }

.promo-grid {
  display: flex;
  gap: 16rpx;
  margin-bottom: 24rpx;
  height: 320rpx;
}
.promo-main {
  flex: 1;
  border-radius: 20rpx;
  position: relative;
  overflow: hidden;
  color: #fff;
  min-width: 0;
  background: linear-gradient(160deg, var(--hero-from), var(--hero-to));
}
.promo-main-body { padding: 24rpx; height: 100%; display: flex; flex-direction: column; justify-content: center; }
.promo-tag {
  font-size: 20rpx;
  background: rgba(255,255,255,0.2);
  border-radius: 8rpx;
  padding: 4rpx 12rpx;
  display: inline-block;
  margin-bottom: 12rpx;
  align-self: flex-start;
}
.promo-title { font-size: 32rpx; font-weight: bold; display: block; margin-bottom: 8rpx; }
.promo-desc { font-size: 22rpx; opacity: 0.8; display: block; margin-bottom: 20rpx; }
.promo-btn {
  display: inline-block;
  background: #fff;
  color: var(--brand-primary);
  font-size: 22rpx;
  font-weight: 600;
  border-radius: 24rpx;
  padding: 8rpx 24rpx;
  align-self: flex-start;
}

.promo-side {
  width: 240rpx;
  display: flex;
  flex-direction: column;
  gap: 12rpx;
  flex-shrink: 0;
}
.promo-mini {
  flex: 1;
  background: var(--bg-card);
  border-radius: 16rpx;
  padding: 16rpx;
  box-shadow: var(--card-shadow);
  overflow: hidden;
  min-height: 0;
}
.pm-tag {
  font-size: 18rpx;
  color: var(--brand-primary);
  background: var(--bg-brand-light);
  border-radius: 6rpx;
  padding: 2rpx 10rpx;
  display: inline-block;
  margin-bottom: 8rpx;
}
.pm-tag.hot { color: #E31837; background: #FFF0F0; }
.pm-text { font-size: 22rpx; color: var(--text-secondary); display: block; line-height: 1.5; }
.pm-price { font-size: 24rpx; color: #E31837; font-weight: bold; display: block; margin-top: 8rpx; }
.ai-mini { display: flex; flex-direction: column; justify-content: center; gap: 4rpx; }

.course-section { margin-bottom: 24rpx; }
.course-scroll { white-space: nowrap; width: 100%; }
.course-card {
  display: inline-block; width: 220rpx; margin-right: 16rpx; padding: 20rpx;
  background: #fff; border-radius: 16rpx; vertical-align: top;
  box-shadow: 0 4rpx 20rpx rgba(0,45,114,.06); border: 2rpx solid transparent;
}
.course-card.active { border-color: var(--brand-primary); background: var(--bg-warm); }
.course-card.completed { opacity: 0.75; }
.course-card.locked { opacity: 0.5; }
.cc-day { font-size: 22rpx; color: var(--brand-primary); font-weight: 600; display: block; }
.cc-title { font-size: 24rpx; color: #1a1a1a; margin: 8rpx 0; display: block; }
.cc-status { font-size: 20rpx; color: #999; display: block; }

.hot-section { margin-bottom: 24rpx; }
.hot-hdr { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16rpx; }
.hot-title { font-size: 32rpx; font-weight: bold; color: var(--text-primary); }
.hot-more { font-size: 24rpx; color: var(--text-hint); }
.hot-list {
  background: #fff;
  border-radius: 20rpx;
  padding: 0 24rpx;
  box-shadow: var(--card-shadow);
}
.hot-row {
  display: flex;
  align-items: center;
  padding: 24rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}
.hot-row:last-child { border-bottom: none; }
.hot-row-main { flex: 1; min-width: 0; }
.hot-name { font-size: 28rpx; font-weight: 500; color: #1a1a1a; display: block; }
.hot-meta { font-size: 22rpx; color: #999; display: block; margin-top: 6rpx; }
.hot-arrow { color: #ccc; font-size: 32rpx; flex-shrink: 0; margin-left: 12rpx; }
</style>
