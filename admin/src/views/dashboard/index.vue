<template>
<div class="page-wrap db">
  <el-alert
    v-if="loadError"
    type="error"
    title="看板数据加载失败"
    description="请确认后端服务已启动（端口 5000），然后点击重新加载。"
    show-icon
    :closable="false"
    class="mb16"
  >
    <el-button size="small" type="primary" @click="load" style="margin-top:8px">重新加载</el-button>
  </el-alert>

  <el-row :gutter="16" class="stat-row">
    <el-col :xs="12" :sm="12" :md="6" v-for="c in cards" :key="c.label">
      <el-card shadow="never" class="stat-card" :body-style="{ padding: '20px 24px' }">
        <div class="stat-v" :style="{ color: c.color }">{{ c.value }}</div>
        <div class="stat-l">{{ c.label }}</div>
      </el-card>
    </el-col>
  </el-row>

  <el-row :gutter="12" class="quick-row">
    <el-col :xs="12" :sm="12" :md="6" v-for="q in quicks" :key="q.path">
      <div class="quick-card" @click="$router.push(q.path)">
        <el-icon class="quick-icon-el" :size="22"><component :is="q.icon" /></el-icon>
        <div class="quick-info">
          <span class="quick-label">{{ q.label }}</span>
          <span class="quick-desc">{{ q.desc }}</span>
        </div>
      </div>
    </el-col>
  </el-row>

  <ChartCard title="数据趋势" :height="300" :loading="loading">
    <template #extra>
      <el-radio-group v-model="period" size="small" @change="load" :disabled="loadError">
        <el-radio-button :value="7">7天</el-radio-button>
        <el-radio-button :value="30">30天</el-radio-button>
      </el-radio-group>
    </template>
    <div ref="trendRef" class="chart-inner" />
  </ChartCard>

  <el-row :gutter="16" class="mt16">
    <el-col :xs="24" :md="12">
      <ChartCard title="训练热度 Top10" :loading="loading" :no-margin="true">
        <div ref="rankRef" class="chart-inner" />
      </ChartCard>
    </el-col>
    <el-col :xs="24" :md="12">
      <el-card shadow="never" class="ai-card">
        <template #header><span class="card-title">AI 今日用量</span></template>
        <div class="ai-row">
          <div class="ai-item"><span class="ai-n">{{ ai.today_text }}</span><span class="ai-l">文案生成</span></div>
          <div class="ai-item"><span class="ai-n">{{ ai.today_speech }}</span><span class="ai-l">语音评测</span></div>
          <div class="ai-item"><span class="ai-n">{{ ai.today_users }}</span><span class="ai-l">活跃用户</span></div>
        </div>
      </el-card>
    </el-col>
  </el-row>

  <el-row :gutter="16" class="mt16">
    <el-col :xs="24" :md="12">
      <ChartCard title="用户留存漏斗（近30天新用户）" :loading="loading" :no-margin="true">
        <div ref="funnelRef" class="chart-inner" />
      </ChartCard>
    </el-col>
    <el-col :xs="24" :md="12">
      <ChartCard title="近7日练习热力图" :loading="loading" :no-margin="true">
        <div ref="heatRef" class="chart-inner" />
      </ChartCard>
    </el-col>
  </el-row>
</div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/api/request'
import ChartCard from '@/components/ChartCard.vue'
import { useChart } from '@/composables/useChart'

const period = ref(30)
const loading = ref(false)
const loadError = ref(false)
const cards = ref([
  { label: '总用户数', value: '--', color: 'var(--brand-primary)' },
  { label: '昨日新增', value: '--', color: 'var(--brand-secondary)' },
  { label: '昨日DAU', value: '--', color: '#52C41A' },
  { label: '昨日打卡率', value: '--', color: '#722ED1' },
])
const ai = reactive({ today_text: '--', today_speech: '--', today_users: '--' })

const trendRef = ref(null)
const rankRef = ref(null)
const funnelRef = ref(null)
const heatRef = ref(null)
const trendChart = useChart(trendRef)
const rankChart = useChart(rankRef)
const funnelChart = useChart(funnelRef)
const heatChart = useChart(heatRef)

const quicks = [
  { icon: 'Memo', label: '训练题库', desc: '管理训练素材', path: '/training' },
  { icon: 'User', label: '用户管理', desc: '查看用户数据', path: '/users' },
  { icon: 'Star', label: '推荐配置', desc: '设置首页推荐', path: '/training/recommend' },
  { icon: 'Cpu', label: 'AI 配置', desc: '调整模型参数', path: '/ai' },
]

async function load() {
  loading.value = true
  loadError.value = false
  try {
    const d = await request.get('/admin/dashboard', { period: period.value })
    const s = d.stats || {}
    cards.value = [
      { label: '总用户数', value: s.total_users ?? 0, color: 'var(--brand-primary)' },
      { label: '昨日新增', value: s.yesterday_new_users ?? 0, color: 'var(--brand-secondary)' },
      { label: '昨日DAU', value: s.yesterday_dau ?? 0, color: '#52C41A' },
      { label: '昨日打卡率', value: `${s.yesterday_checkin_rate ?? 0}%`, color: '#722ED1' },
    ]
    ai.today_text = d.ai_usage?.today_text_generations ?? 0
    ai.today_speech = d.ai_usage?.today_speech_evaluations ?? 0
    ai.today_users = d.ai_usage?.today_active_users ?? s.yesterday_dau ?? 0
    await nextTick()
    await Promise.all([
      renderTrends(d.trends || []),
      renderRanks(d.top_trainings || []),
      renderFunnel(d.retention),
      renderHeatmap(d.checkin_heatmap),
    ])
  } catch (e) {
    loadError.value = true
    ElMessage.error('看板数据加载失败，请检查后端连接')
    cards.value = cards.value.map(c => ({ ...c, value: '--' }))
    ai.today_text = '--'
    ai.today_speech = '--'
    ai.today_users = '--'
    await nextTick()
    await Promise.all([
      trendChart.showEmpty(),
      rankChart.showEmpty(),
      funnelChart.showEmpty(),
      heatChart.showEmpty(),
    ])
  } finally {
    loading.value = false
  }
}

async function renderTrends(d) {
  if (!d.length) { await trendChart.showEmpty(); return }
  await trendChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['新增', 'DAU', '打卡率'] },
    grid: { left: 40, right: 40, top: 20, bottom: 20 },
    xAxis: { type: 'category', data: d.map(t => t.date.slice(5)) },
    yAxis: [{ type: 'value' }, { type: 'value', max: 100 }],
    series: [
      { name: '新增', type: 'line', data: d.map(t => t.new_users), smooth: true, itemStyle: { color: 'var(--brand-secondary)' } },
      { name: 'DAU', type: 'line', data: d.map(t => t.dau), smooth: true, itemStyle: { color: '#52C41A' } },
      { name: '打卡率', type: 'line', yAxisIndex: 1, data: d.map(t => t.checkin_rate), smooth: true, itemStyle: { color: 'var(--brand-primary)' } },
    ],
  }, true)
}

async function renderRanks(d) {
  if (!d.length) { await rankChart.showEmpty(); return }
  const items = [...d].reverse()
  await rankChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: 110, right: 20, top: 0, bottom: 0 },
    yAxis: { type: 'category', data: items.map(i => i.title), axisLabel: { width: 100, overflow: 'truncate' } },
    xAxis: { type: 'value' },
    series: [{ type: 'bar', data: items.map(i => i.practice_count), itemStyle: { color: 'var(--brand-secondary)' }, barMaxWidth: 20 }],
  }, true)
}

async function renderFunnel(ret) {
  if (!ret?.new_users) { await funnelChart.showEmpty(); return }
  const total = ret.new_users
  await funnelChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    series: [{
      type: 'funnel', left: '10%', width: '80%', label: { formatter: '{b}\n{c}人 ({d}%)' },
      data: [
        { value: total, name: '新增用户' },
        { value: ret.d1_count ?? Math.round(total * ret.d1_retention / 100), name: '次日留存' },
        { value: ret.d7_count ?? Math.round(total * ret.d7_retention / 100), name: '7日留存' },
        { value: ret.d30_count ?? Math.round(total * ret.d30_retention / 100), name: '30日留存' },
      ],
    }],
  }, true)
}

async function renderHeatmap(hm) {
  if (!hm?.data?.length) { await heatChart.showEmpty(); return }
  await heatChart.setOption({
    tooltip: { position: 'top' },
    grid: { height: '70%', top: '10%' },
    xAxis: { type: 'category', data: Array.from({ length: 24 }, (_, i) => i + '时'), splitArea: { show: true } },
    yAxis: { type: 'category', data: hm.weekdays || ['周一', '周二', '周三', '周四', '周五', '周六', '周日'], splitArea: { show: true } },
    visualMap: { min: 0, max: hm.max || 10, calculable: true, orient: 'horizontal', left: 'center', bottom: '0%' },
    series: [{ type: 'heatmap', data: hm.data, label: { show: false }, emphasis: { itemStyle: { shadowBlur: 10 } } }],
  }, true)
}

onMounted(load)
</script>

<style scoped lang="scss">
.stat-row { margin-bottom: 16px; }
.stat-card {
  text-align: center;
  border-radius: var(--card-radius);
}
.stat-v { font-size: 32px; font-weight: 600; margin-bottom: 4px; }
.stat-l { font-size: 13px; color: var(--text-muted); }

.quick-row { margin-bottom: 16px; }
.quick-card {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #fff;
  border: 1px solid var(--border-color);
  border-radius: var(--card-radius);
  padding: 14px 16px;
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
  margin-bottom: 12px;
  &:hover {
    border-color: var(--el-color-primary-light-5);
    background: var(--el-color-primary-light-9);
  }
}
.quick-icon-el { color: var(--el-color-primary); flex-shrink: 0; }
.quick-info { display: flex; flex-direction: column; }
.quick-label { font-size: 14px; font-weight: 600; color: var(--text-primary); }
.quick-desc { font-size: 12px; color: var(--text-muted); margin-top: 2px; }

.chart-inner { width: 100%; height: 100%; min-height: inherit; }
.ai-card { border-radius: var(--card-radius); height: calc(100% - 0px); }
.card-title { font-weight: 600; }
.ai-row { display: flex; justify-content: space-around; padding: 30px 0; }
.ai-item { text-align: center; }
.ai-n { font-size: 40px; font-weight: bold; color: var(--brand-primary); display: block; }
.ai-l { font-size: 13px; color: var(--text-muted); margin-top: 6px; display: block; }
</style>
