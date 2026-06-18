<template>
  <view class="page">
    <!-- 配额提示 -->
    <view class="quota-bar">
      <text>今日剩余 </text>
      <text class="quota-num">{{ quota }}</text>
      <text> 次 · {{ cfg.title }}</text>
    </view>

    <!-- 场景选择 -->
    <scroll-view scroll-x class="scene-scroll" :show-scrollbar="false">
      <view
        class="scene-chip"
        v-for="s in scenes"
        :key="s.value"
        :class="{ on: form.scene_type === s.value }"
        @tap="selectScene(s.value)"
      >
        <AppIcon :name="s.icon" size="md"/>
        <text class="scene-label">{{ s.label }}</text>
      </view>
    </scroll-view>

    <view class="card form-card">
      <view class="fi">
        <text class="fl">{{ cfg.topicLabel }} *</text>
        <input class="finp" v-model="form.topic" :placeholder="cfg.topicPlaceholder" placeholder-style="font-size:26rpx;color:#999" maxlength="50"/>
      </view>

      <view class="fi">
        <text class="fl">{{ cfg.descLabel }}</text>
        <input class="finp" v-model="form.scene_desc" :placeholder="cfg.descPlaceholder" placeholder-style="font-size:26rpx;color:#999" maxlength="50"/>
      </view>

      <view class="fr" v-if="cfg.showDuration">
        <view class="fi h">
          <text class="fl">时长</text>
          <picker :range="cfg.durations" @change="onPickDuration">
            <view class="fp">{{ form.duration || '选择' }}</view>
          </picker>
        </view>
        <view class="fi h">
          <text class="fl">风格</text>
          <picker :range="cfg.styles" @change="onPickStyle">
            <view class="fp">{{ form.style || '选择' }}</view>
          </picker>
        </view>
      </view>

      <view v-if="form.scene_type === 'opening'" class="tip">
        💡 一次生成 <text class="tb">3种风格</text> 开场白：专业正式 · 轻松幽默 · 情感共鸣
      </view>

      <button class="gen-btn" @click="generate" :loading="gen">{{ cfg.btnText }}</button>
    </view>

    <view v-if="result" class="card result-card">
      <text class="rtit ellipsis">{{ result.title }}</text>
      <view class="rct"><text>{{ result.content }}</text></view>
      <view v-if="result.tips" class="tips-box">💡 {{ result.tips }}</view>
      <view class="rbtns">
        <button size="mini" class="rbtn" @click="cp">📋 复制文案</button>
        <button size="mini" class="rbtn primary" @click="im">🔊 导入练习</button>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import api from '@/api/request'
import AppIcon from '@/components/AppIcon.vue'

const quota = ref(3)
const gen = ref(false)
const result = ref(null)

const scenes = [
  { icon: 'mic', label: '演讲文案', value: 'speech' },
  { icon: 'video', label: '短视频', value: 'short_video' },
  { icon: 'robot', label: '直播话术', value: 'livestream' },
  { icon: 'briefcase', label: '面试话术', value: 'interview' },
  { icon: 'star', label: '开场白', value: 'opening' }
]

const SCENE_CONFIG = {
  speech: {
    title: '演讲稿撰写',
    topicLabel: '演讲主题',
    topicPlaceholder: '例：如何做好时间管理',
    descLabel: '演讲场景',
    descPlaceholder: '例：部门周会3分钟分享',
    durations: ['1min', '3min', '5min', '10min'],
    styles: ['专业正式', '轻松幽默', '情感共鸣', '数据驱动'],
    showDuration: true,
    btnText: 'AI 生成演讲稿'
  },
  short_video: {
    title: '短视频口播',
    topicLabel: '视频主题',
    topicPlaceholder: '例：3个高效学习小技巧',
    descLabel: '发布平台',
    descPlaceholder: '例：抖音、小红书、视频号',
    durations: ['30s', '1min', '2min', '3min'],
    styles: ['轻松口语化', '幽默搞笑', '情感共鸣', '干货分享', '悬念反转'],
    showDuration: true,
    btnText: 'AI 生成口播稿'
  },
  livestream: {
    title: '直播带货话术',
    topicLabel: '产品/主题',
    topicPlaceholder: '例：某品牌蓝牙耳机',
    descLabel: '直播场景',
    descPlaceholder: '例：抖音带货、视频号直播',
    durations: ['1min', '3min', '5min'],
    styles: ['热情有感染力', '专业可信赖', '幽默风趣', '快节奏促单'],
    showDuration: true,
    btnText: 'AI 生成直播话术'
  },
  interview: {
    title: '面试话术',
    topicLabel: '面试问题',
    topicPlaceholder: '例：请做一个自我介绍',
    descLabel: '岗位/场景',
    descPlaceholder: '例：互联网产品经理校招',
    durations: ['1min', '2min', '3min'],
    styles: ['专业稳重', '真诚自信', '逻辑清晰', 'STAR结构化'],
    showDuration: true,
    btnText: 'AI 生成面试话术'
  },
  opening: {
    title: '万能开场白',
    topicLabel: '开场主题',
    topicPlaceholder: '例：公司年会致辞',
    descLabel: '使用场合',
    descPlaceholder: '例：正式晚宴、朋友聚会',
    durations: [],
    styles: [],
    showDuration: false,
    btnText: 'AI 生成3种开场白'
  }
}

const form = reactive({
  scene_type: 'speech',
  topic: '',
  scene_desc: '',
  duration: '3min',
  style: '专业正式'
})

const cfg = computed(() => SCENE_CONFIG[form.scene_type] || SCENE_CONFIG.speech)

function selectScene(v) {
  form.scene_type = v
  const c = SCENE_CONFIG[v]
  if (c.durations.length) form.duration = c.durations[0]
  if (c.styles.length) form.style = c.styles[0]
}

function onPickDuration(e) { form.duration = cfg.value.durations[e.detail.value] }
function onPickStyle(e) { form.style = cfg.value.styles[e.detail.value] }

async function lq() {
  try { const d = await api.get('/ai-text/quota'); quota.value = d.remaining || 3 } catch (e) {}
}

async function generate() {
  if (!form.topic) return uni.showToast({ title: '请输入主题', icon: 'none' })
  if (quota.value <= 0) return uni.showToast({ title: '今日次数已用完', icon: 'none' })
  gen.value = true
  try {
    const payload = { ...form }
    if (form.scene_type === 'opening') { delete payload.duration; delete payload.style }
    result.value = await api.post('/ai-text/generate', payload)
    quota.value = result.value.remaining_quota || quota.value - 1
  } catch (e) {} finally { gen.value = false }
}

function cp() { uni.setClipboardData({ data: result.value?.content || '', success: () => uni.showToast({ title: '已复制' }) }) }
function im() {
  if (!result.value?.content) return
  api.post('/ai-text/import-practice', {
    title: result.value.title,
    content: result.value.content,
    scene_type: form.scene_type,
  }).then(d => {
    uni.showToast({ title: '已导入练习库', icon: 'success' })
    if (d.training_item_id) {
      setTimeout(() => uni.navigateTo({ url: '/pages/training/detail?id=' + d.training_item_id }), 500)
    }
  }).catch(() => uni.showToast({ title: '导入失败', icon: 'none' }))
}
onShow(lq)
</script>

<style scoped>
.quota-bar {
  text-align: center;
  font-size: 24rpx;
  color: var(--text-secondary);
  background: var(--bg-card);
  border-radius: 40rpx;
  padding: 14rpx 24rpx;
  margin-bottom: 20rpx;
  box-shadow: var(--card-shadow);
}
.quota-num { color: #E31837; font-weight: bold; font-size: 28rpx; }

.scene-scroll { white-space: nowrap; margin-bottom: 20rpx; width: 100%; }
.scene-chip {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
  background: var(--bg-card);
  border-radius: 16rpx;
  padding: 20rpx 28rpx;
  margin-right: 12rpx;
  box-shadow: var(--card-shadow);
  border: 2rpx solid transparent;
}
.scene-chip.on {
  background: var(--bg-brand-light);
  border-color: var(--brand-primary);
}
.scene-chip.on .scene-label { color: var(--brand-primary); font-weight: 600; }
.scene-label { font-size: 22rpx; color: var(--text-secondary); }

.form-card { padding: 28rpx; }
.fi { margin-bottom: 16rpx; }
.fl { font-size: 24rpx; color: var(--text-primary); font-weight: 500; display: block; margin-bottom: 8rpx; }
.finp {
  background: var(--bg-secondary);
  border-radius: 12rpx;
  padding: 18rpx 20rpx;
  font-size: 26rpx;
  height: 72rpx;
  line-height: 36rpx;
  width: 100%;
}
.fr { display: flex; gap: 16rpx; }
.h { flex: 1; min-width: 0; }
.fp {
  background: var(--bg-secondary);
  border-radius: 12rpx;
  padding: 18rpx 20rpx;
  font-size: 26rpx;
  height: 72rpx;
  line-height: 36rpx;
  color: var(--text-primary);
  display: flex;
  align-items: center;
}

.tip {
  background: #FFF8E8;
  border-radius: 12rpx;
  padding: 16rpx 20rpx;
  font-size: 24rpx;
  color: #B8860B;
  margin-bottom: 16rpx;
  text-align: center;
}
.tb { font-weight: bold; color: #E31837; }

.gen-btn {
  width: 100%;
  height: 88rpx;
  background: linear-gradient(135deg, var(--brand-primary), var(--brand-light));
  color: #fff;
  border-radius: 44rpx;
  border: none;
  font-size: 30rpx;
  font-weight: 600;
  margin-top: 8rpx;
}

.result-card { margin-top: 8rpx; }
.rtit { font-size: 30rpx; font-weight: bold; display: block; margin-bottom: 8rpx; }
.rct {
  background: var(--bg-secondary);
  border-radius: 16rpx;
  padding: 24rpx;
  margin: 16rpx 0;
  font-size: 26rpx;
  line-height: 1.8;
  max-height: 500rpx;
  overflow-y: auto;
}
.tips-box {
  background: #FFF8E8;
  border-radius: 12rpx;
  padding: 16rpx 20rpx;
  font-size: 24rpx;
  color: #B8860B;
  margin-bottom: 16rpx;
  line-height: 1.5;
}
.rbtns { display: flex; gap: 16rpx; }
.rbtn {
  flex: 1;
  background: var(--bg-card);
  border: 1rpx solid var(--border-color);
  border-radius: 12rpx;
  font-size: 24rpx;
  color: var(--text-primary);
}
.rbtn.primary {
  background: var(--bg-brand-light);
  border-color: var(--brand-primary);
  color: var(--brand-primary);
}
</style>
