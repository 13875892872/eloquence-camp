<template>
<view class="page">
  <!-- 数据概览 -->
  <view class="stats-card">
    <view class="si" v-for="s in statsArr" :key="s.l">
      <text class="sn">{{ s.v }}</text>
      <text class="sl">{{ s.l }}</text>
    </view>
    <view v-if="allDone" class="share-pill" @click="openCheckinPoster">分享打卡 🎉</view>
  </view>

  <view class="link-row" @click="goCalendar">
    <view class="link-left"><AppIcon name="calendar" size="sm"/><text>打卡日历</text></view>
    <text class="arrow">›</text>
  </view>

  <view class="action-row" v-if="!allDone">
    <text class="action-link" @click="doMakeup">补签昨日</text>
    <text class="action-link dim" @click="doRest">今日休息</text>
  </view>

  <!-- 能力评分 -->
  <view class="card" v-if="ability">
    <text class="section-h">口才能力雷达</text>
    <ScoreRadar :scores="ability" :size="260" />
  </view>

  <!-- 今日任务 -->
  <view class="section-hdr">
    <text class="section-h">今日任务</text>
    <text class="section-sub">{{ doneCount }}/{{ tasks.length }} 已完成</text>
  </view>
  <view
    class="task-card"
    v-for="t in tasks"
    :key="t.task_index"
    :class="{ locked: t.status === 'locked', done: t.status === 'completed' }"
    @click="startTask(t)"
  >
    <view class="task-left">
      <view class="task-icon" :class="t.status">{{ taskIcon(t.status) }}</view>
    </view>
    <view class="task-body">
      <text class="tt ellipsis">{{ t.title }}</text>
      <text class="tsb ellipsis">{{ t.subtitle }} · 最低{{ t.min_duration }}s</text>
      <text v-if="t.my_record" class="tsc">评分 {{ t.my_record.score }} 分</text>
    </view>
    <text class="task-arrow">›</text>
  </view>

  <!-- 成长目标 -->
  <view class="section-hdr">
    <text class="section-h">成长目标</text>
  </view>
  <view class="goal-card" v-for="g in goals" :key="g.level">
    <view class="gh">
      <text class="goal-name ellipsis">{{ g.badge }} {{ g.name }}</text>
      <text class="gp">{{ g.my_days }}/{{ g.required_days }}天</text>
    </view>
    <view class="gb"><view class="gf" :style="{ width: g.progress + '%' }"></view></view>
    <text v-if="g.achieved" class="gd">✅ 已达成</text>
  </view>

  <Poster :visible="showPoster" type="checkin" :data="posterData" @close="showPoster=false"/>
</view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import api from '@/api/request'
import AppIcon from '@/components/AppIcon.vue'
import Poster from '@/components/poster.vue'
import ScoreRadar from '@/components/ScoreRadar.vue'
import { showGoalAchieved } from '@/utils/category'
import { safeRequestSubscribe } from '@/utils/subscribe'

const stats = ref({ continuous_days: 0, total_days: 0, total_minutes: 0 })
const tasks = ref([])
const ability = ref(null)
const goals = ref([])
const allDone = ref(false)
const showPoster = ref(false)
const posterData = ref({})

const dl = k => ({ pronunciation: '发音', fluency: '流利度', completeness: '完整度', content: '内容', expressiveness: '表现力' }[k] || k)
const statsArr = computed(() => [
  { l: '连续打卡', v: stats.value.continuous_days },
  { l: '累计天数', v: stats.value.total_days },
  { l: '总时长(min)', v: stats.value.total_minutes }
])
const doneCount = computed(() => tasks.value.filter(t => t.status === 'completed').length)
function taskIcon(s) { return s === 'completed' ? '✓' : s === 'locked' ? '🔒' : '○' }

async function load() {
  try {
    const d = await api.get('/checkin/today')
    tasks.value = d.tasks || []
    allDone.value = !!d.all_completed
    Object.assign(stats.value, d.stats || {})
  } catch (e) {}
  try {
    const p = await api.get('/user/profile')
    ability.value = p.ability_score
    Object.assign(stats.value, { continuous_days: p.continuous_days, total_days: p.total_days, total_minutes: p.total_practice_minutes })
  } catch (e) {}
  try {
    const g = await api.get('/checkin/growth-progress')
    goals.value = (g.goals || []).map(g => ({ ...g, badge: g.badge?.icon || '🎯', progress: g.achieved ? 100 : g.progress || 0 }))
  } catch (e) {}
}

function startTask(t) {
  if (t.status === 'locked') return uni.showToast({ title: '请先完成前一个任务', icon: 'none' })
  if (t.status === 'completed') return uni.showToast({ title: '已完成', icon: 'none' })
  if (t.training_item?.id) {
    uni.navigateTo({ url: '/pages/training/detail?id=' + t.training_item.id + '&tk=' + t.task_index + '&min=' + (t.min_duration || 30) })
  } else {
    uni.showToast({ title: '请在训练题库中选择题目练习', icon: 'none' })
  }
}

async function doMakeup() {
  try {
    const res = await api.post('/checkin/makeup', {})
    uni.showToast({ title: '补签成功', icon: 'success' })
    showGoalAchieved(res)
    load()
  } catch (e) {
    uni.showModal({
      title: '补签说明',
      content: '需先完成至少60秒练习。请完成一次训练后，在录音记录页选择「用此记录补签」。',
      showCancel: false,
    })
  }
}

async function doRest() {
  uni.showModal({
    title: '今日休息',
    content: '设置后今日不计漏打卡，确定休息吗？',
    success: async (r) => {
      if (!r.confirm) return
      try {
        await api.post('/checkin/rest', {})
        uni.showToast({ title: '已设置休息', icon: 'none' })
        load()
      } catch (e) {}
    },
  })
}

function openCheckinPoster() {
  posterData.value = {
    days: stats.value.continuous_days || 0,
    totalMinutes: stats.value.total_minutes || 0,
    nickname: '我',
  }
  showPoster.value = true
}
function goCalendar() { uni.navigateTo({ url: '/pages/checkin/calendar' }) }

onShow(() => { load(); requestSubscribe() })

async function requestSubscribe() {
  try {
    const u = await api.get('/user/profile')
    if (!u.subscribe_status) {
      const tplData = await api.get('/checkin/push-template-ids')
      const tmplIds = tplData.tmpl_ids || []
      if (tmplIds.length > 0) await safeRequestSubscribe(tmplIds)
      await api.put('/user/profile/subscribe', { subscribe_status: true })
    }
  } catch (e) {}
}
</script>

<style scoped>
.stats-card {
  display: flex;
  background: linear-gradient(135deg, var(--brand-primary), var(--brand-light));
  border-radius: 24rpx;
  padding: 36rpx 0;
  margin-bottom: 20rpx;
  box-shadow: 0 8rpx 24rpx rgba(160, 216, 239, 0.4);
}
.si { flex: 1; text-align: center; color: #fff; min-width: 0; position: relative; }
.si + .si::before {
  content: '';
  position: absolute;
  left: 0; top: 50%;
  transform: translateY(-50%);
  width: 1rpx; height: 48rpx;
  background: rgba(255,255,255,0.2);
}
.sn { font-size: 44rpx; font-weight: bold; display: block; }
.sl { font-size: 22rpx; opacity: 0.8; display: block; margin-top: 4rpx; }
.share-pill {
  margin: 16rpx 24rpx 0; text-align: center; font-size: 24rpx;
  background: rgba(255,255,255,.2); border-radius: 32rpx; padding: 12rpx;
}
.action-row { display: flex; justify-content: space-around; margin-bottom: 16rpx; }
.action-link { font-size: 24rpx; color: var(--brand-primary); padding: 8rpx 16rpx; }
.action-link.dim { color: #999; }

.arrow { color: var(--text-hint); font-size: 32rpx; }
.link-left { display: flex; align-items: center; gap: 12rpx; }

.section-h { font-size: 30rpx; font-weight: bold; display: block; margin-bottom: 16rpx; color: var(--text-primary); }
.section-hdr { display: flex; justify-content: space-between; align-items: center; margin: 28rpx 0 16rpx; }
.section-sub { font-size: 24rpx; color: var(--text-hint); }

.radar-row { display: flex; align-items: center; margin: 10rpx 0; }
.rl { width: 110rpx; font-size: 22rpx; color: var(--text-secondary); flex-shrink: 0; }
.rb { flex: 1; height: 12rpx; background: var(--border-light); border-radius: 6rpx; overflow: hidden; margin: 0 12rpx; min-width: 0; }
.rf { height: 100%; background: linear-gradient(90deg, var(--brand-primary), var(--brand-light)); border-radius: 6rpx; transition: width 0.5s; }
.rv { width: 50rpx; text-align: right; font-size: 22rpx; color: var(--brand-primary); font-weight: bold; flex-shrink: 0; }

.task-card {
  display: flex;
  align-items: center;
  background: var(--bg-card);
  border-radius: 20rpx;
  padding: 24rpx;
  margin-bottom: 14rpx;
  box-shadow: var(--card-shadow);
}
.task-card.locked { opacity: 0.55; }
.task-card.done { border-left: 6rpx solid #52C41A; }
.task-left { flex-shrink: 0; margin-right: 16rpx; }
.task-icon {
  width: 56rpx; height: 56rpx;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 24rpx;
  background: var(--bg-brand-light);
  color: var(--brand-primary);
}
.task-icon.completed { background: #E8F8EE; color: #52C41A; }
.task-icon.locked { background: #F5F5F5; color: #999; }
.task-body { flex: 1; min-width: 0; }
.tt { font-size: 28rpx; font-weight: 600; display: block; color: var(--text-primary); }
.tsb { font-size: 22rpx; color: var(--text-hint); display: block; margin-top: 4rpx; }
.tsc { font-size: 22rpx; color: #E31837; margin-top: 6rpx; display: block; font-weight: 500; }
.task-arrow { color: var(--text-hint); font-size: 32rpx; flex-shrink: 0; margin-left: 8rpx; }

.goal-card {
  background: var(--bg-card);
  border-radius: 20rpx;
  padding: 24rpx;
  margin-bottom: 14rpx;
  box-shadow: var(--card-shadow);
}
.gh { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10rpx; }
.goal-name { font-size: 28rpx; font-weight: 500; flex: 1; min-width: 0; }
.gp { font-size: 24rpx; color: var(--brand-primary); font-weight: 600; flex-shrink: 0; margin-left: 16rpx; }
.gb { height: 10rpx; background: var(--border-light); border-radius: 5rpx; overflow: hidden; }
.gf { height: 100%; background: linear-gradient(90deg, #52C41A, #73D13D); border-radius: 5rpx; }
.gd { font-size: 22rpx; color: #52C41A; display: block; margin-top: 8rpx; }
</style>
