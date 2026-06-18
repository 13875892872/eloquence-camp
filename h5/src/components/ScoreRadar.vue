<template>
  <view class="radar-wrap">
    <canvas
      :canvas-id="canvasId"
      class="radar-canvas"
      :style="{ width: size + 'px', height: size + 'px' }"
    />
    <view class="radar-labels">
      <text v-for="l in labels" :key="l.key" class="rl-item">{{ l.name }} {{ l.value }}</text>
    </view>
  </view>
</template>

<script setup>
import { watch, nextTick, getCurrentInstance, computed } from 'vue'

const props = defineProps({
  scores: { type: Object, default: () => ({}) },
  size: { type: Number, default: 260 }
})

const canvasId = `scoreRadar_${Math.random().toString(36).slice(2, 9)}`
const instance = getCurrentInstance()

const DIMS = [
  { key: 'pronunciation', name: '发音' },
  { key: 'fluency', name: '流利' },
  { key: 'completeness', name: '完整' },
  { key: 'content', name: '内容' },
  { key: 'expressiveness', name: '表现' },
]

const labels = computed(() => DIMS.map(d => ({
  ...d,
  value: props.scores?.[d.key] ?? 0
})))

watch(() => props.scores, async () => {
  await nextTick()
  draw()
}, { deep: true, immediate: true })

function draw() {
  const ctx = uni.createCanvasContext(canvasId, instance)
  const S = props.size
  const cx = S / 2
  const cy = S / 2
  const R = S * 0.34
  const n = DIMS.length
  const vals = DIMS.map(d => Math.min(100, Math.max(0, props.scores?.[d.key] ?? 0)) / 100)

  ctx.clearRect(0, 0, S, S)

  for (let ring = 1; ring <= 4; ring++) {
    ctx.beginPath()
    const r = (R * ring) / 4
    for (let i = 0; i < n; i++) {
      const ang = -Math.PI / 2 + (2 * Math.PI * i) / n
      const x = cx + r * Math.cos(ang)
      const y = cy + r * Math.sin(ang)
      if (i === 0) ctx.moveTo(x, y)
      else ctx.lineTo(x, y)
    }
    ctx.closePath()
    ctx.setStrokeStyle('#e8f6fc')
    ctx.setLineWidth(1)
    ctx.stroke()
  }

  for (let i = 0; i < n; i++) {
    const ang = -Math.PI / 2 + (2 * Math.PI * i) / n
    ctx.beginPath()
    ctx.moveTo(cx, cy)
    ctx.lineTo(cx + R * Math.cos(ang), cy + R * Math.sin(ang))
    ctx.setStrokeStyle('#e8f6fc')
    ctx.stroke()
  }

  ctx.beginPath()
  vals.forEach((v, i) => {
    const ang = -Math.PI / 2 + (2 * Math.PI * i) / n
    const x = cx + R * v * Math.cos(ang)
    const y = cy + R * v * Math.sin(ang)
    if (i === 0) ctx.moveTo(x, y)
    else ctx.lineTo(x, y)
  })
  ctx.closePath()
  ctx.setFillStyle('rgba(160, 216, 239, 0.45)')
  ctx.fill()
  ctx.setStrokeStyle('#5BA8CF')
  ctx.setLineWidth(2)
  ctx.stroke()

  vals.forEach((v, i) => {
    const ang = -Math.PI / 2 + (2 * Math.PI * i) / n
    const x = cx + R * v * Math.cos(ang)
    const y = cy + R * v * Math.sin(ang)
    ctx.beginPath()
    ctx.arc(x, y, 4, 0, 2 * Math.PI)
    ctx.setFillStyle('#5BA8CF')
    ctx.fill()
  })

  ctx.draw()
}
</script>

<style scoped>
.radar-wrap { display: flex; flex-direction: column; align-items: center; }
.radar-canvas { display: block; }
.radar-labels {
  display: flex; flex-wrap: wrap; justify-content: center; gap: 12rpx 20rpx;
  margin-top: 12rpx; width: 100%;
}
.rl-item { font-size: 22rpx; color: #666; }
</style>
