<template>
  <view v-if="visible" class="ob-mask" @tap.stop>
    <view class="ob-card">
      <swiper class="ob-swiper" :current="step" @change="onSwipe">
        <swiper-item v-for="(s, i) in slides" :key="i">
          <view class="ob-slide">
            <text class="ob-icon">{{ s.icon }}</text>
            <text class="ob-title">{{ s.title }}</text>
            <text class="ob-desc">{{ s.desc }}</text>
          </view>
        </swiper-item>
      </swiper>
      <view class="ob-dots">
        <view v-for="(_, i) in slides" :key="i" class="ob-dot" :class="{ on: step === i }"></view>
      </view>
      <view class="ob-actions">
        <text class="ob-skip" @tap="finish">跳过</text>
        <button class="ob-btn" @tap="next">{{ step >= slides.length - 1 ? '开始练习' : '下一步' }}</button>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({ visible: { type: Boolean, default: false } })
const emit = defineEmits(['finish'])

const step = ref(0)
const slides = [
  { icon: '🎤', title: '每日打卡练口才', desc: '3 个短任务，跟读、表达、即兴，每天 10 分钟养成习惯' },
  { icon: '📚', title: '场景化训练题库', desc: '演讲、面试、直播、即兴等多场景素材，AI 语音评分反馈' },
  { icon: '🤖', title: 'AI 文案助手', desc: '一键生成演讲稿/口播稿，可导入练习库直接开练' },
]

function onSwipe(e) { step.value = e.detail.current || 0 }
function next() {
  if (step.value >= slides.length - 1) finish()
  else step.value += 1
}
function finish() {
  uni.setStorageSync('onboarding_done', true)
  emit('finish')
}
</script>

<style scoped>
.ob-mask {
  position: fixed; inset: 0; background: rgba(0,0,0,.55); z-index: 9998;
  display: flex; align-items: center; justify-content: center; padding: 40rpx;
}
.ob-card {
  width: 100%; max-width: 640rpx; background: #fff; border-radius: 24rpx;
  padding: 40rpx 32rpx 32rpx; box-sizing: border-box;
}
.ob-swiper { height: 320rpx; }
.ob-slide { display: flex; flex-direction: column; align-items: center; text-align: center; padding: 20rpx; }
.ob-icon { font-size: 72rpx; margin-bottom: 24rpx; }
.ob-title { font-size: 34rpx; font-weight: 700; color: #1a1a1a; margin-bottom: 16rpx; }
.ob-desc { font-size: 26rpx; color: #666; line-height: 1.6; }
.ob-dots { display: flex; justify-content: center; gap: 12rpx; margin: 16rpx 0 24rpx; }
.ob-dot { width: 12rpx; height: 12rpx; border-radius: 50%; background: #ddd; }
.ob-dot.on { background: var(--brand-primary); width: 28rpx; border-radius: 6rpx; }
.ob-actions { display: flex; align-items: center; justify-content: space-between; }
.ob-skip { font-size: 26rpx; color: #999; padding: 16rpx; }
.ob-btn {
  flex: 1; margin-left: 24rpx; background: var(--brand-primary); color: #fff; border-radius: 40rpx;
  font-size: 28rpx; border: none;
}
</style>
