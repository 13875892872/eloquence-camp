<template>
<view class="page">
  <view class="month-switcher">
    <text class="ms-arrow" @tap="prevMonth">←</text>
    <text class="ms-label">{{currentYear}}年{{currentMonth}}月</text>
    <text class="ms-arrow" @tap="nextMonth">→</text>
  </view>

  <view class="weekday-row">
    <text class="wd" v-for="d in weekdays" :key="d">{{d}}</text>
  </view>

  <view class="calendar-grid">
    <view class="day" v-for="(d,i) in daysList" :key="i"
      :class="[d.status, { today: d.isToday, empty: !d.day }]">
      <text v-if="d.day" class="day-num">{{d.day}}</text>
      <text v-if="d.status" class="day-dot">{{ statusIcon(d.status) }}</text>
    </view>
  </view>

  <view class="legend">
    <text class="lg-item"><text class="dot completed">✓</text> 正常打卡</text>
    <text class="lg-item"><text class="dot makeup">补</text> 补签</text>
    <text class="lg-item"><text class="dot rest">休</text> 休息</text>
  </view>

  <view class="card stats-card" v-if="summary">
    <text class="st">本月打卡 <text class="highlight">{{summary.total}}</text> 天</text>
    <text class="sd">正常 {{summary.completed||0}} · 补签 {{summary.makeup||0}} · 休息 {{summary.rest||0}}</text>
  </view>
</view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import api from '@/api/request'

const currentYear = ref(new Date().getFullYear())
const currentMonth = ref(new Date().getMonth() + 1)
const dayMap = ref({})
const summary = ref(null)
const weekdays = ['日','一','二','三','四','五','六']

function statusIcon(s) {
  return { completed: '✓', makeup: '补', rest: '休' }[s] || ''
}

const daysList = computed(() => {
  const year = currentYear.value
  const month = currentMonth.value
  const firstDay = new Date(year, month - 1, 1).getDay()
  const daysInMonth = new Date(year, month, 0).getDate()
  const today = new Date()
  const todayStr = `${today.getFullYear()}-${String(today.getMonth()+1).padStart(2,'0')}-${String(today.getDate()).padStart(2,'0')}`

  const list = []
  for (let i = 0; i < firstDay; i++) list.push({ day: null, status: '', isToday: false })
  for (let d = 1; d <= daysInMonth; d++) {
    const dateStr = `${year}-${String(month).padStart(2,'0')}-${String(d).padStart(2,'0')}`
    list.push({
      day: d,
      status: dayMap.value[dateStr] || '',
      isToday: dateStr === todayStr,
    })
  }
  return list
})

async function load() {
  try {
    const d = await api.get('/checkin/calendar', { year: currentYear.value, month: currentMonth.value })
    const map = {}
    for (const entry of (d.days || [])) {
      if (typeof entry === 'string') map[entry] = 'completed'
      else if (entry?.date) map[entry.date] = entry.status || 'completed'
    }
    dayMap.value = map
    summary.value = d.summary || null
  } catch (e) {}
}

function prevMonth() {
  if (currentMonth.value === 1) { currentMonth.value = 12; currentYear.value-- }
  else currentMonth.value--
  load()
}

function nextMonth() {
  if (currentMonth.value === 12) { currentMonth.value = 1; currentYear.value++ }
  else currentMonth.value++
  load()
}

onLoad(load)
</script>

<style scoped>
.month-switcher{display:flex;justify-content:space-between;align-items:center;padding:24rpx 0;width:100%}
.ms-arrow{font-size:36rpx;color:var(--brand-primary);padding:8rpx 24rpx}
.ms-label{font-size:34rpx;font-weight:bold}
.weekday-row{display:flex;background:var(--bg-warm);border-radius:16rpx;padding:14rpx 0;margin-bottom:10rpx;width:100%}
.wd{flex:1;text-align:center;font-size:24rpx;color:#666;font-weight:500}
.calendar-grid{display:flex;flex-wrap:wrap;width:100%}
.day{width:calc(100%/7);aspect-ratio:1;display:flex;flex-direction:column;align-items:center;justify-content:center;position:relative;border-radius:16rpx}
.day.empty{background:transparent}
.day.completed{background:#E8F4E8}
.day.makeup{background:#FFF7E6}
.day.rest{background:#F5F5F5}
.day.today{border:2rpx solid var(--brand-primary)}
.day-num{font-size:28rpx;color:#1A1A1A}
.day-dot{font-size:18rpx;margin-top:2rpx}
.day.completed .day-dot{color:#52C41A}
.day.makeup .day-dot{color:#FAAD14}
.day.rest .day-dot{color:#999}
.legend{display:flex;flex-wrap:wrap;gap:20rpx;margin-top:16rpx;font-size:22rpx;color:#666}
.lg-item{display:flex;align-items:center;gap:6rpx}
.dot{font-size:20rpx;padding:2rpx 8rpx;border-radius:6rpx}
.dot.completed{background:#E8F4E8;color:#52C41A}
.dot.makeup{background:#FFF7E6;color:#FAAD14}
.dot.rest{background:#F5F5F5;color:#999}
.card{background:var(--bg-card);border-radius:24rpx;padding:28rpx;margin-top:24rpx;width:100%;box-sizing:border-box}
.st{font-size:32rpx;font-weight:bold;display:block;margin-bottom:8rpx}
.highlight{color:var(--brand-primary)}
.sd{font-size:24rpx;color:#999;display:block}
</style>
