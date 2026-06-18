<template>
<view class="page profile-page">
  <!-- 用户信息卡片 -->
  <view class="profile-header">
    <view class="profile-bg"></view>
    <view class="profile-body">
      <image class="av" :src="user.avatar_url || ''" mode="aspectFill"/>
      <view class="profile-info">
        <text class="un ellipsis">{{ user.nickname || '微信用户' }}</text>
        <text class="ul">{{ lv(user.growth_level) }}</text>
      </view>
    </view>
    <view class="us">
      <view class="usi">
        <text class="usn">{{ user.total_days || 0 }}</text>
        <text class="usl">累计打卡</text>
      </view>
      <view class="usi-divider"></view>
      <view class="usi">
        <text class="usn">{{ user.continuous_days || 0 }}</text>
        <text class="usl">连续打卡</text>
      </view>
      <view class="usi-divider"></view>
      <view class="usi">
        <text class="usn">{{ user.total_practice_minutes || 0 }}</text>
        <text class="usl">练习分钟</text>
      </view>
    </view>
  </view>

  <!-- 功能菜单 -->
  <view class="menu-group">
    <view class="menu-item" @click="nav('records')">
      <view class="mi-left"><AppIcon name="mic" size="sm"/><text>录音记录</text></view>
      <text class="mi-arrow">›</text>
    </view>
    <view class="menu-item" @click="nav('favorites')">
      <view class="mi-left"><AppIcon name="star" size="sm"/><text>我的收藏</text></view>
      <text class="mi-arrow">›</text>
    </view>
    <view class="menu-item" @click="nav('quota')">
      <view class="mi-left"><AppIcon name="gift" size="sm"/><text>权益中心</text></view>
      <text class="mi-arrow">›</text>
    </view>
  </view>

  <view class="menu-group">
    <view class="menu-item">
      <view class="mi-left"><AppIcon name="moon" size="sm"/><text>深色模式</text></view>
      <switch :checked="isDark" @change="onDarkChange" color="var(--brand-primary)" style="flex-shrink:0"/>
    </view>
    <view class="menu-item">
      <view class="mi-left"><AppIcon name="bell" size="sm"/><text>消息提醒</text></view>
      <switch :checked="remind" @change="onRemindChange" color="var(--brand-primary)" style="flex-shrink:0"/>
    </view>
    <view class="menu-item" @click="cc">
      <view class="mi-left"><AppIcon name="list" size="sm"/><text>清除缓存</text></view>
      <text class="mi-arrow">›</text>
    </view>
    <view class="menu-item">
      <view class="mi-left"><AppIcon name="info" size="sm"/><text>关于我们</text></view>
      <text class="mi-arrow">›</text>
    </view>
  </view>
</view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import api from '@/api/request'
import AppIcon from '@/components/AppIcon.vue'
import { safeRequestSubscribe } from '@/utils/subscribe'

const user = ref({})
const remind = ref(true)
const isDark = ref(false)
const lv = v => ({ newbie: 'Lv1 新人', beginner: 'Lv2 入门', advanced: 'Lv3 进阶', expert: 'Lv4 达人', master: 'Lv5 大师' }[v] || 'Lv1 新人')
const nav = p => uni.navigateTo({ url: '/pages/profile/' + p })

async function load() {
  try { const d = await api.get('/user/profile'); user.value = d; remind.value = !!d.subscribe_status } catch (e) {}
}

async function onRemindChange(e) {
  const val = e.detail.value
  if (val) {
    try {
      const tplData = await api.get('/checkin/push-template-ids')
      const tmplIds = tplData.tmpl_ids || []
      if (tmplIds.length > 0) await safeRequestSubscribe(tmplIds)
    } catch (e) {}
  }
  remind.value = val
  try { await api.put('/user/profile/subscribe', { subscribe_status: val }) } catch (e) {
    remind.value = !val; uni.showToast({ title: '设置失败', icon: 'none' })
  }
}

async function onDarkChange(e) {
  const val = e.detail.value
  isDark.value = val
  uni.setStorageSync('dark_mode', val)
  uni.showToast({ title: val ? '深色模式已开启' : '深色模式已关闭', icon: 'none' })
}
function cc() { uni.showToast({ title: '缓存已清除', icon: 'success' }) }
onShow(() => { load(); isDark.value = !!uni.getStorageSync('dark_mode') })
</script>

<style scoped>
.profile-page { padding-top: 8rpx; }

.profile-header {
  position: relative;
  border-radius: 24rpx;
  overflow: hidden;
  margin-bottom: 24rpx;
  box-shadow: 0 8rpx 24rpx rgba(160, 216, 239, 0.35);
}
.profile-bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, var(--hero-from) 0%, var(--hero-to) 100%);
}
.profile-body {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 20rpx;
  padding: 36rpx 28rpx 24rpx;
}
.av {
  width: 96rpx; height: 96rpx;
  border-radius: 50%;
  border: 4rpx solid rgba(160, 216, 239, 0.45);
  background: rgba(255, 255, 255, 0.6);
  flex-shrink: 0;
}
.profile-info { flex: 1; min-width: 0; }
.un { font-size: 34rpx; font-weight: bold; color: var(--text-primary); display: block; }
.ul { font-size: 24rpx; color: #D4A853; display: block; margin-top: 6rpx; font-weight: 500; }

.us {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  background: rgba(160, 216, 239, 0.22);
  padding: 20rpx 0;
}
.usi { flex: 1; text-align: center; min-width: 0; }
.usi-divider { width: 1rpx; height: 48rpx; background: rgba(255,255,255,0.2); flex-shrink: 0; }
.usn { font-size: 36rpx; font-weight: bold; color: #fff; display: block; }
.usl { font-size: 20rpx; color: rgba(255,255,255,0.7); display: block; margin-top: 4rpx; }

.menu-group {
  background: var(--bg-card);
  border-radius: 20rpx;
  overflow: hidden;
  margin-bottom: 20rpx;
  box-shadow: var(--card-shadow);
}
.menu-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 28rpx 28rpx;
  border-bottom: 1rpx solid var(--border-light);
  font-size: 28rpx;
  color: var(--text-primary);
}
.menu-item:last-child { border-bottom: none; }
.mi-left { display: flex; align-items: center; gap: 16rpx; }
.mi-arrow { color: var(--text-hint); font-size: 32rpx; }
</style>
