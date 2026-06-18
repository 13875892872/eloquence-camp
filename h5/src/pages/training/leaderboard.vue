<template>
<view class="page">
  <!-- 维度切换 -->
  <view class="tabs">
    <view
      class="tab"
      v-for="t in tabList"
      :key="t.value"
      :class="{ active: type === t.value }"
      @click="switchType(t.value)"
    >{{ t.label }}</view>
  </view>

  <!-- 我的排名 -->
  <view class="my-rank-card" v-if="myRank">
    <text class="mr-label">我的排名</text>
    <text class="mr-rank">#{{ myRank }}</text>
    <text class="mr-value">{{ formatMyValue() }}</text>
  </view>
  <view class="my-rank-card dim" v-else-if="loaded">
    <text class="mr-label">我的排名</text>
    <text class="mr-tip">暂无排名，快去训练吧</text>
  </view>

  <!-- 前三名 -->
  <view class="podium" v-if="list.length >= 3">
    <view
      class="podium-item"
      v-for="item in podiumOrder"
      :key="item.rank"
      :class="'rank-' + item.rank"
    >
      <text class="p-medal">{{ medals[item.rank] }}</text>
      <text class="p-name ellipsis">{{ item.nickname }}</text>
      <text class="p-value">{{ formatValue(item) }}</text>
    </view>
  </view>

  <!-- 4~10 名 -->
  <view class="rank-list card" v-if="list.length > 3">
    <view
      class="rank-item"
      v-for="item in list.slice(3)"
      :key="item.rank"
      :class="{ me: myRank === item.rank }"
    >
      <text class="ri-rank">{{ item.rank }}</text>
      <text class="ri-name ellipsis">{{ item.nickname }}</text>
      <text class="ri-score">{{ formatValue(item) }}</text>
    </view>
  </view>

  <!-- 不足 3 人时的完整列表 -->
  <view class="rank-list card" v-else-if="list.length && list.length <= 3">
    <view
      class="rank-item"
      v-for="item in list"
      :key="item.rank"
      :class="{ me: myRank === item.rank }"
    >
      <text class="ri-rank">{{ item.rank }}</text>
      <text class="ri-name ellipsis">{{ item.nickname }}</text>
      <text class="ri-score">{{ formatValue(item) }}</text>
    </view>
  </view>

  <view v-if="loaded && !list.length" class="empty">暂无排名数据</view>
</view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import api from '@/api/request'

const tabList = [
  { label: '本周时长', value: 'week_duration' },
  { label: '本月时长', value: 'month_duration' },
  { label: '连续天数', value: 'continuous_days' }
]

const type = ref('week_duration')
const list = ref([])
const myRank = ref(null)
const myData = ref(null)
const unit = ref('分钟')
const loaded = ref(false)
const medals = ['', '🥇', '🥈', '🥉']

const podiumOrder = computed(() => {
  const top3 = list.value.slice(0, 3)
  if (top3.length < 3) return top3
  return [top3[1], top3[0], top3[2]]
})

function formatValue(item) {
  const v = item.value ?? 0
  if (type.value === 'continuous_days') return `${v} 天`
  return `${v} 分钟`
}

function formatMyValue() {
  if (!myData.value) return ''
  return formatValue(myData.value)
}

async function load() {
  loaded.value = false
  try {
    const d = await api.get('/user/leaderboard', { type: type.value })
    list.value = d.items || []
    myRank.value = d.my_rank || null
    myData.value = d.my_data || null
    unit.value = d.unit || '分钟'
  } catch (e) {
    list.value = []
    myRank.value = null
    myData.value = null
  } finally {
    loaded.value = true
  }
}

function switchType(v) {
  if (type.value === v) return
  type.value = v
  load()
}

onLoad(load)
</script>

<style scoped>
.tabs {
  display: flex;
  background: #fff;
  border-radius: 40rpx;
  padding: 6rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 4rpx 20rpx rgba(160, 216, 239, 0.35);
}
.tab {
  flex: 1;
  text-align: center;
  font-size: 24rpx;
  color: #666;
  padding: 16rpx 8rpx;
  border-radius: 32rpx;
}
.tab.active {
  background: var(--brand-primary);
  color: #fff;
  font-weight: 600;
}

.my-rank-card {
  background: linear-gradient(135deg, var(--brand-primary), var(--brand-light));
  border-radius: 24rpx;
  padding: 32rpx;
  text-align: center;
  color: #fff;
  margin-bottom: 24rpx;
}
.my-rank-card.dim { opacity: 0.92; }
.mr-label { font-size: 24rpx; opacity: 0.85; display: block; }
.mr-rank { font-size: 64rpx; font-weight: bold; display: block; margin: 8rpx 0; }
.mr-value { font-size: 26rpx; opacity: 0.9; display: block; }
.mr-tip { font-size: 26rpx; opacity: 0.85; display: block; margin-top: 12rpx; }

.podium {
  display: flex;
  align-items: flex-end;
  justify-content: center;
  gap: 16rpx;
  margin-bottom: 24rpx;
  padding: 20rpx 0;
}
.podium-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  background: #fff;
  border-radius: 20rpx;
  padding: 24rpx 16rpx;
  box-shadow: 0 4rpx 20rpx rgba(160, 216, 239, 0.35);
  flex: 1;
  max-width: 200rpx;
  min-width: 0;
}
.podium-item.rank-1 { order: 2; transform: scale(1.08); border-top: 6rpx solid #FFD700; }
.podium-item.rank-2 { order: 1; border-top: 6rpx solid #C0C0C0; }
.podium-item.rank-3 { order: 3; border-top: 6rpx solid #CD7F32; }
.p-medal { font-size: 40rpx; display: block; }
.p-name { font-size: 24rpx; margin: 8rpx 0; max-width: 100%; color: #1a1a1a; }
.p-value { font-size: 22rpx; color: var(--brand-primary); font-weight: bold; }

.card {
  background: #fff;
  border-radius: 24rpx;
  padding: 8rpx 24rpx;
  box-shadow: 0 4rpx 20rpx rgba(160, 216, 239, 0.35);
}
.rank-item {
  display: flex;
  align-items: center;
  padding: 20rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}
.rank-item:last-child { border-bottom: none; }
.rank-item.me { background: var(--bg-warm); margin: 0 -24rpx; padding: 20rpx 24rpx; }
.ri-rank { width: 56rpx; font-size: 28rpx; font-weight: bold; color: #999; flex-shrink: 0; }
.ri-name { font-size: 28rpx; flex: 1; min-width: 0; margin: 0 16rpx; color: #1a1a1a; }
.ri-score { font-size: 24rpx; color: var(--brand-primary); font-weight: 500; flex-shrink: 0; }

.empty { padding: 120rpx 0; text-align: center; font-size: 28rpx; color: #999; }
</style>
