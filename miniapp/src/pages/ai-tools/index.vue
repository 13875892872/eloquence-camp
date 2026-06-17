<template>
  <view class="page">
    <view class="qb">今日剩余 <text class="qn">{{quota}}</text> 次 · {{cfg.title}}</view>

    <view class="sg">
      <view class="sc" v-for="s in scenes" :key="s.value" :class="{on:form.scene_type===s.value}" @tap="selectScene(s.value)">
        <text class="sci">{{s.icon}}</text><text class="scl">{{s.label}}</text>
      </view>
    </view>

    <view class="card">
      <!-- 主题 -->
      <view class="fi">
        <text class="fl">{{cfg.topicLabel}} *</text>
        <input class="finp" v-model="form.topic" :placeholder="cfg.topicPlaceholder" placeholder-style="font-size:26rpx;color:#999" maxlength="50"/>
      </view>

      <!-- 场景描述 -->
      <view class="fi">
        <text class="fl">{{cfg.descLabel}}</text>
        <input class="finp" v-model="form.scene_desc" :placeholder="cfg.descPlaceholder" placeholder-style="font-size:26rpx;color:#999" maxlength="50"/>
      </view>

      <!-- 时长 + 风格（开场白不显示） -->
      <view class="fr" v-if="cfg.showDuration">
        <view class="fi h"><text class="fl">时长</text>
          <picker :range="cfg.durations" @change="onPickDuration">
            <text class="fp">{{form.duration||'选择'}}</text>
          </picker>
        </view>
        <view class="fi h"><text class="fl">风格</text>
          <picker :range="cfg.styles" @change="onPickStyle">
            <text class="fp">{{form.style||'选择'}}</text>
          </picker>
        </view>
      </view>

      <!-- 开场白提示 -->
      <view v-if="form.scene_type==='opening'" class="tip">
        💡 一次生成 <text class="tb">3种风格</text> 开场白：专业正式 · 轻松幽默 · 情感共鸣
      </view>

      <button class="gbn" @click="generate" :loading="gen">{{cfg.btnText}}</button>
    </view>

    <!-- 生成结果 -->
    <view v-if="result" class="card rc">
      <text class="rtit ellipsis">{{result.title}}</text>
      <view class="rct"><text>{{result.content}}</text></view>
      <view v-if="result.tips" class="tips-box">💡 {{result.tips}}</view>
      <view class="rbtns">
        <button size="mini" class="rbtn" @click="cp">📋 复制文案</button>
        <button size="mini" class="rbtn rbtn2" @click="im">🔊 导入练习</button>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import api from '@/api/request'

const quota = ref(3)
const gen = ref(false)
const result = ref(null)

const scenes = [
  { icon: '🎤', label: '演讲文案', value: 'speech' },
  { icon: '📱', label: '短视频',   value: 'short_video' },
  { icon: '🛒', label: '直播话术', value: 'livestream' },
  { icon: '🌟', label: '开场白',   value: 'opening' }
]

// ── 每种场景的配置 ──
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
    btnText: '🎤 AI生成演讲稿'
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
    btnText: '📱 AI生成口播稿'
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
    btnText: '🛒 AI生成直播话术'
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
    btnText: '🌟 AI生成3种开场白'
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
  // 自动填充默认值
  if (c.durations.length) form.duration = c.durations[0]
  if (c.styles.length) form.style = c.styles[0]
}

function onPickDuration(e) {
  form.duration = cfg.value.durations[e.detail.value]
}
function onPickStyle(e) {
  form.style = cfg.value.styles[e.detail.value]
}

async function lq() {
  try { const d = await api.get('/ai-text/quota'); quota.value = d.remaining || 3 } catch (e) { }
}

async function generate() {
  if (!form.topic) return uni.showToast({ title: '请输入主题', icon: 'none' })
  if (quota.value <= 0) return uni.showToast({ title: '今日次数已用完', icon: 'none' })
  gen.value = true
  try {
    // 开场白不传 duration 和 style
    const payload = { ...form }
    if (form.scene_type === 'opening') {
      delete payload.duration
      delete payload.style
    }
    result.value = await api.post('/ai-text/generate', payload)
    quota.value = result.value.remaining_quota || quota.value - 1
  } catch (e) { } finally { gen.value = false }
}

function cp() {
  uni.setClipboardData({ data: result.value?.content || '', success: () => uni.showToast({ title: '已复制' }) })
}
function im() {
  uni.showToast({ title: '已导入练习库', icon: 'none' })
}
onShow(lq)
</script>

<style scoped>
.qb{text-align:center;font-size:24rpx;color:#666;margin-bottom:16rpx;width:100%}.qn{color:#FF6B35;font-weight:bold}
.sg{display:flex;gap:10rpx;margin-bottom:20rpx;width:100%}
.sc{flex:1;min-width:0;text-align:center;background:var(--bg-card);border-radius:16rpx;padding:18rpx 4rpx;box-shadow:0 2rpx 8rpx rgba(0,0,0,.06);box-sizing:border-box;overflow:hidden}
.sc.on{background:#FFF0E8;border:2rpx solid #FF6B35}
.sci{font-size:32rpx;display:block;margin-bottom:4rpx}.scl{font-size:18rpx;color:#666;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;display:block}
.card{background:var(--bg-card);border-radius:20rpx;padding:24rpx;margin-bottom:20rpx;width:100%;box-sizing:border-box;overflow:hidden}
.fi{margin-bottom:14rpx;width:100%}.fl{font-size:24rpx;color:#333;display:block;margin-bottom:6rpx}
.finp{background:var(--bg-secondary);border-radius:10rpx;padding:16rpx 18rpx;font-size:26rpx;height:68rpx;line-height:36rpx;width:100%;box-sizing:border-box}
.fr{display:flex;gap:14rpx;width:100%}.h{flex:1;min-width:0}.fp{background:var(--bg-secondary);border-radius:10rpx;padding:16rpx 18rpx;font-size:26rpx;height:68rpx;line-height:36rpx;color:#999;width:100%;box-sizing:border-box;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;display:flex;align-items:center}
.gbn{width:100%;height:80rpx;background:linear-gradient(135deg,#FF6B35,#FF8C5A);color:#fff;border-radius:40rpx;border:none;font-size:30rpx;font-weight:bold;margin-top:4rpx;box-sizing:border-box}
.tip{background:#FFF8E1;border-radius:12rpx;padding:14rpx 18rpx;font-size:24rpx;color:#F57F17;margin-bottom:14rpx;text-align:center;width:100%;box-sizing:border-box}.tb{font-weight:bold;color:#E65100}
.rc{margin-top:20rpx}.rtit{font-size:30rpx;font-weight:bold;display:block;margin-bottom:4rpx}
.rct{background:var(--bg-secondary);border-radius:14rpx;padding:20rpx;margin:14rpx 0;font-size:26rpx;line-height:1.7;word-break:break-all;max-height:500rpx;overflow-y:auto;width:100%;box-sizing:border-box}
.tips-box{background:#FFF8E1;border-radius:12rpx;padding:14rpx 18rpx;font-size:24rpx;color:#F57F17;margin-bottom:14rpx;width:100%;box-sizing:border-box;line-height:1.5}
.rbtns{display:flex;gap:12rpx}
.rbtn{flex:1;background:var(--bg-card);border:1rpx solid #ddd;border-radius:10rpx;font-size:24rpx;color:#333}
.rbtn2{background:#FFF0E8;border-color:#FF6B35;color:#FF6B35}
</style>
