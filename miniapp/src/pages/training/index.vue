<template>
<view class="page page-flush training-page">
  <view class="top-bar" id="training-top">
    <view class="search-wrap">
      <AppIcon name="search" size="sm"/>
      <input
        class="search-input"
        v-model="keyword"
        placeholder="搜索训练内容..."
        placeholder-style="font-size:26rpx;color:#999"
        @confirm="search"
        maxlength="50"
      />
    </view>
    <view class="rank-btn" @click="goLeaderboard">
      <AppIcon name="trophy" size="md"/>
    </view>
  </view>

  <view class="menu-layout">
    <scroll-view scroll-y class="side-nav" :show-scrollbar="false" :style="scrollStyle">
      <view
        class="nav-item"
        v-for="t in tabs"
        :key="t.value"
        :class="{ active: cat === t.value }"
        @click="switchCat(t.value)"
      >
        <view class="nav-bar" v-if="cat === t.value"></view>
        <AppIcon :name="t.icon" size="md"/>
        <text class="nav-label">{{ t.label }}</text>
      </view>
    </scroll-view>

    <scroll-view scroll-y class="main-list" :show-scrollbar="false" :style="scrollStyle" @scrolltolower="loadMore">
      <view class="list-hdr" v-if="currentTab">
        <view class="list-title">{{ currentTab.label }}</view>
        <view class="list-desc">{{ currentTab.desc }}</view>
      </view>

      <view v-if="loading" class="state-tip">加载中...</view>
      <block v-else-if="list.length">
        <view class="product-card" v-for="it in list" :key="it.id" :class="{ locked: it.locked }" @click="goDetail(it)">
          <view class="prod-info">
            <view class="prod-title">{{ it.title }}<text v-if="it.locked" class="lock-tag"> 🔒</text></view>
            <view class="prod-tags">
              <text class="tag">{{ cl(it.category) }}</text>
              <text class="tag diff">{{ stars(it.difficulty) }}</text>
            </view>
            <view class="prod-foot">
              <text class="prod-count">{{ it.practice_count || 0 }}人练过</text>
            </view>
          </view>
        </view>
      </block>
      <view v-else class="state-tip">{{ loadError || '暂无训练内容' }}</view>

      <view class="load-tip" v-if="hasMore && list.length" @click="loadMore">加载更多</view>
      <view class="load-tip dim" v-if="list.length && !hasMore">— 已全部加载 —</view>
      <view class="list-bottom"></view>
    </scroll-view>
  </view>
</view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onLoad, onShow } from '@dcloudio/uni-app'
import api from '@/api/request'
import AppIcon from '@/components/AppIcon.vue'
import { getScrollHeight } from '@/utils/layout'
import { catLabel } from '@/utils/category'

const cat = ref('')
const keyword = ref('')
const list = ref([])
const page = ref(1)
const hasMore = ref(true)
const loading = ref(false)
const loadError = ref('')
const listHeight = ref(getScrollHeight(130))
const PAGE_SIZE = 10
let loadingLock = false

const tabs = [
  { label: '全部', value: '', icon: 'list', desc: '全部训练题目' },
  { label: '基础口才', value: 'basic', icon: 'mic', desc: '发音与基础表达' },
  { label: '演讲实战', value: 'speech', icon: 'target', desc: '场景演讲模拟' },
  { label: '直播话术', value: 'livestream', icon: 'video', desc: '直播带货话术' },
  { label: '即兴表达', value: 'improv', icon: 'bolt', desc: '快速即兴反应' },
  { label: '面试模拟', value: 'interview', icon: 'briefcase', desc: '求职面试实战' },
  { label: '短视频口播', value: 'short_video', icon: 'video', desc: '口播稿实战' },
  { label: '学生场景', value: 'student', icon: 'book', desc: '答辩竞选复试' },
]

const scrollStyle = computed(() => ({ height: listHeight.value + 'px' }))
const currentTab = computed(() => tabs.find(t => t.value === cat.value) || tabs[0])
const cl = catLabel
const stars = n => '★'.repeat(Math.min(n || 1, 5))

async function load(reset = true) {
  if (loadingLock) return
  loadingLock = true
  if (reset) { page.value = 1; list.value = []; hasMore.value = true; loadError.value = '' }
  loading.value = true
  try {
    const d = await api.get('/training/items', {
      category: cat.value || undefined,
      keyword: keyword.value || undefined,
      page: page.value,
      page_size: PAGE_SIZE
    })
    const items = d.items || []
    if (reset) list.value = items
    else list.value = [...list.value, ...items]
    hasMore.value = items.length >= PAGE_SIZE
  } catch (e) {
    if (reset) loadError.value = '加载失败，请检查网络与后端服务'
    console.error('[training] load failed', e)
  } finally {
    loading.value = false
    loadingLock = false
  }
}

function search() { load() }
function switchCat(v) { cat.value = v; load() }
function loadMore() { if (hasMore.value) { page.value++; load(false) } }
function goLeaderboard() { uni.navigateTo({ url: '/pages/training/leaderboard' }) }
function goDetail(it) {
  if (it.locked) return uni.showToast({ title: it.lock_reason || '升级后解锁', icon: 'none' })
  uni.navigateTo({ url: '/pages/training/detail?id=' + it.id })
}

onLoad(() => {
  const c = uni.getStorageSync('training_cat')
  if (c) { cat.value = c; uni.removeStorageSync('training_cat') }
})

onShow(() => { load() })
</script>

<style scoped>
.training-page {
  padding-bottom: 0;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}

.top-bar {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 12rpx 24rpx 16rpx;
  flex-shrink: 0;
}
.search-wrap {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12rpx;
  background: #fff;
  border-radius: 40rpx;
  padding: 0 24rpx;
  height: 72rpx;
  box-shadow: 0 4rpx 20rpx rgba(160, 216, 239, 0.35);
  min-width: 0;
}
.search-input { flex: 1; font-size: 26rpx; height: 72rpx; color: #1a1a1a; }
.rank-btn {
  width: 72rpx; height: 72rpx;
  background: #fff;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 4rpx 20rpx rgba(160, 216, 239, 0.35);
  flex-shrink: 0;
}

.menu-layout {
  flex: 1;
  display: flex;
  flex-direction: row;
  width: 100%;
  overflow: hidden;
}

.side-nav {
  width: 168rpx;
  flex-shrink: 0;
  background: #f7f7f7;
}

.nav-item {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6rpx;
  padding: 28rpx 8rpx;
}
.nav-item.active { background: #fff; }
.nav-bar {
  position: absolute;
  left: 0; top: 50%;
  transform: translateY(-50%);
  width: 6rpx; height: 40rpx;
  background: var(--brand-primary);
  border-radius: 0 4rpx 4rpx 0;
}
.nav-label { font-size: 22rpx; text-align: center; line-height: 1.3; color: #666; }
.nav-item.active .nav-label { color: var(--brand-primary); font-weight: 600; }

.main-list {
  flex: 1;
  width: 0;
  background: #fff;
  padding: 0 20rpx;
  box-sizing: border-box;
}

.list-hdr {
  padding: 20rpx 0 12rpx;
  border-bottom: 1rpx solid #f0f0f0;
  margin-bottom: 8rpx;
}
.list-title { font-size: 30rpx; font-weight: bold; color: #1a1a1a; line-height: 1.4; }
.list-desc { font-size: 22rpx; color: #999; margin-top: 4rpx; line-height: 1.4; }

.product-card {
  padding: 24rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
  width: 100%;
  box-sizing: border-box;
}
.product-card.locked { opacity: 0.65; }
.lock-tag { font-size: 22rpx; color: #D48806; }

.prod-info {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 10rpx;
}

.prod-title {
  font-size: 28rpx;
  font-weight: 600;
  color: #1a1a1a;
  line-height: 1.5;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.prod-tags { display: flex; flex-wrap: wrap; gap: 8rpx; margin-top: 10rpx; }
.tag {
  font-size: 20rpx;
  color: var(--brand-primary);
  background: #e8eef8;
  padding: 4rpx 12rpx;
  border-radius: 6rpx;
  line-height: 1.4;
}
.tag.diff { color: #E31837; background: #fff0f0; }

.prod-foot {
  margin-top: 12rpx;
}
.prod-count { font-size: 22rpx; color: #999; line-height: 1.4; }

.state-tip { text-align: center; color: #999; padding: 80rpx 0; font-size: 28rpx; }
.load-tip { text-align: center; padding: 24rpx 0; font-size: 26rpx; color: var(--brand-primary); }
.load-tip.dim { color: #999; }
.list-bottom { height: 40rpx; }
</style>
